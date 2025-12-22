#!/usr/bin/env bash
#
# Unified test runner for Cellframe Node
#
# Usage:
#   ./tests/run.sh                     # Run all tests
#   ./tests/run.sh --e2e               # Run only E2E tests
#   ./tests/run.sh --functional        # Run only functional tests
#   ./tests/run.sh --clean             # Clean cache before running (does NOT rebuild node)
#   ./tests/run.sh --rebuild           # Rebuild Docker images before starting network
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

success() {
    echo -e "${GREEN}✓${NC} $1"
}

error() {
    echo -e "${RED}✗${NC} $1" >&2
}

warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Directories
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

STAGE_ENV_WRAPPER="$SCRIPT_DIR/stage-env/stage-env"
STAGE_ENV_CONFIG="$SCRIPT_DIR/stage-env.cfg"

# Test directories
STAGE_ENV_BASE_TESTS="$SCRIPT_DIR/stage-env/tests/base"
FUNCTIONAL_TESTS="$SCRIPT_DIR/functional"
SCENARIOS_TESTS="$SCRIPT_DIR/e2e"  # E2E tests directory
REGRESSION_TESTS="$SCRIPT_DIR/regression"  # Regression tests directory

# Build directories
TEST_BUILD_DIR="$PROJECT_ROOT/build"

# Parse arguments
RUN_E2E=false
RUN_FUNCTIONAL=false
RUN_REGRESSION=false
CLEAN_BEFORE=false
REBUILD_IMAGES=false
PKGS_UPDATE=false
STOP_ENV=false
SPECIFIC_TESTS=()

while [[ $# -gt 0 ]]; do
    case $1 in
        --e2e)
            RUN_E2E=true
            shift
            ;;
        --functional)
            RUN_FUNCTIONAL=true
            shift
            ;;
        --regression)
            RUN_REGRESSION=true
            shift
            ;;
        --clean)
            CLEAN_BEFORE=true
            shift
            ;;
        --rebuild)
            REBUILD_IMAGES=true
            shift
            ;;
        --pkgs-update)
            PKGS_UPDATE=true
            shift
            ;;
        --stop)
            STOP_ENV=true
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS] [TEST_PATH...]"
            echo ""
            echo "Options:"
            echo "  --e2e           Run only E2E tests"
            echo "  --functional    Run only functional tests"
            echo "  --regression    Run only regression tests (bug reproduction scenarios)"
            echo "  --clean         Clean cache before running (does NOT rebuild node)"
            echo "  --rebuild       Rebuild Docker images before starting network"
            echo "  --pkgs-update   Update packages in running containers (binary + apt update/upgrade)"
            echo "  --stop          Stop stage environment"
            echo "  -h, --help      Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                                    # Run all tests"
            echo "  $0 --e2e                              # Run all E2E tests"
            echo "  $0 --clean --e2e                      # Clean cache and run E2E tests"
            echo "  $0 --rebuild --e2e                    # Rebuild images and run E2E tests"
            echo "  $0 --stop                             # Stop stage environment"
            echo "  $0 tests/e2e/token                    # Run specific test suite"
            echo "  $0 tests/e2e/token/001_token_decl.yml # Run specific test"
            echo "  $0 tests/functional/wallet tests/e2e/token # Run multiple suites"
            echo ""
            echo "If no test type or path specified, all tests will run."
            exit 0
            ;;
        -*)
            error "Unknown option: $1"
            exit 1
            ;;
        *)
            # It's a test path
            SPECIFIC_TESTS+=("$1")
            shift
            ;;
    esac
done

# Handle --stop first
if [ "$STOP_ENV" = true ]; then
    info "Stopping stage environment..."
    
    if [ -x "$STAGE_ENV_WRAPPER" ]; then
        pushd "$SCRIPT_DIR/stage-env" > /dev/null
        STAGE_ENV_CONFIG_ABS="$(cd "$(dirname "$STAGE_ENV_CONFIG")" && pwd)/$(basename "$STAGE_ENV_CONFIG")"
        ./stage-env --config="$STAGE_ENV_CONFIG_ABS" stop || true
        popd > /dev/null
    else
        error "stage-env wrapper not found or not executable"
        exit 1
    fi
    
    success "Stage environment stopped"
    exit 0
fi

# If specific tests provided, use them directly
if [ ${#SPECIFIC_TESTS[@]} -gt 0 ]; then
    info "Specific tests requested: ${SPECIFIC_TESTS[*]}"
    # Don't set RUN_E2E or RUN_FUNCTIONAL - we'll use SPECIFIC_TESTS directly
elif ! $RUN_E2E && ! $RUN_FUNCTIONAL && ! $RUN_REGRESSION; then
    # If nothing specified and no specific tests, run all
    RUN_E2E=true
    RUN_FUNCTIONAL=true
    RUN_REGRESSION=true
fi

info "Cellframe Node Test Runner"
echo "────────────────────────────────────"

# Check prerequisites
info "Checking prerequisites..."

if ! command -v python3 &> /dev/null; then
    error "Python 3 is required but not installed"
    exit 1
fi

if ! command -v docker &> /dev/null; then
    error "Docker is required but not installed"
    exit 1
fi

success "Prerequisites OK"

# Package building is now handled by stage-env automatically
# run.sh only passes config path to stage-env
info "Using node source configuration from $STAGE_ENV_CONFIG"
info "Stage-env will handle package building automatically if needed"

# Clean if requested
if $CLEAN_BEFORE; then
    warning "Cleaning test environment..."
    
    if [ -x "$STAGE_ENV_WRAPPER" ]; then
        pushd "$SCRIPT_DIR/stage-env" > /dev/null
        STAGE_ENV_CONFIG_ABS="$(cd "$(dirname "$STAGE_ENV_CONFIG")" && pwd)/$(basename "$STAGE_ENV_CONFIG")"
        ./stage-env --config="$STAGE_ENV_CONFIG_ABS" clean --all || true
        popd > /dev/null
    fi
    
    # Additional cleanup: snapshot, cache/data, cache/code, config
    # This ensures complete cleanup even if snapshot deletion fails
    # NOTE: cache/data cleanup is handled by stage-env clean --all via Docker
    # This section only handles directories that stage-env doesn't clean
    info "Cleaning additional directories..."
    
    STAGE_ENV_DIR="$SCRIPT_DIR/stage-env"
    TESTING_DIR="$SCRIPT_DIR/testing"
    
    # Clean snapshots (if stage-env clean didn't handle them)
    if [ -d "$TESTING_DIR/snapshots" ] && [ "$(ls -A "$TESTING_DIR/snapshots" 2>/dev/null)" ]; then
        info "Removing remaining snapshots..."
        # Use Docker for cleanup if available (handles root-owned files)
        if command -v docker &> /dev/null; then
            docker run --rm -v "$TESTING_DIR:/cleanup" alpine:latest sh -c "rm -rf /cleanup/snapshots/* && echo 'Snapshots cleaned'" || true
        else
            rm -rf "$TESTING_DIR/snapshots"/* || true
        fi
        success "Snapshots cleaned"
    fi
    
    # Clean cache/data using Docker (handles root-owned files from containers)
    if [ -d "$TESTING_DIR/cache/data" ] && [ "$(ls -A "$TESTING_DIR/cache/data" 2>/dev/null)" ]; then
        info "Removing cache/data via Docker..."
        if command -v docker &> /dev/null; then
            docker run --rm -v "$TESTING_DIR/cache:/cleanup" alpine:latest sh -c "rm -rf /cleanup/data/* && echo 'Cache/data cleaned'" || true
        else
            warning "Docker not available, falling back to sudo (may fail)"
            sudo rm -rf "$TESTING_DIR/cache/data"/* || true
        fi
        success "Cache/data cleaned"
    fi
    
    # Clean cache/code using Docker (handles root-owned files from containers)
    if [ -d "$TESTING_DIR/cache/code" ] && [ "$(ls -A "$TESTING_DIR/cache/code" 2>/dev/null)" ]; then
        info "Removing cache/code via Docker..."
        if command -v docker &> /dev/null; then
            docker run --rm -v "$TESTING_DIR/cache:/cleanup" alpine:latest sh -c "rm -rf /cleanup/code/* && echo 'Cache/code cleaned'" || true
        else
            warning "Docker not available, falling back to sudo (may fail)"
            sudo rm -rf "$TESTING_DIR/cache/code"/* || true
        fi
        success "Cache/code cleaned"
    fi
    
    # Clean config cache (if exists) - this is safe to remove with rm
    if [ -d "$STAGE_ENV_DIR/.cache" ]; then
        info "Removing config cache..."
        rm -rf "$STAGE_ENV_DIR/.cache" || true
        success "Config cache cleaned"
    fi
    
    success "Environment cleaned"
fi

# Track results
E2E_EXIT=0
FUNCTIONAL_EXIT=0
REGRESSION_EXIT=0

# Handle pkgs-update flag
if [ "$PKGS_UPDATE" = true ]; then
    echo ""
    info "═══════════════════════════════════"
    info "Updating Packages"
    info "═══════════════════════════════════"
    echo ""
    
    if [ ! -x "$STAGE_ENV_WRAPPER" ]; then
        error "stage-env wrapper not found or not executable"
        exit 1
    fi
    
    pushd "$SCRIPT_DIR/stage-env" > /dev/null
    STAGE_ENV_CONFIG_ABS="$(cd "$(dirname "$STAGE_ENV_CONFIG")" && pwd)/$(basename "$STAGE_ENV_CONFIG")"
    
    info "Updating packages in running containers..."
    ./stage-env --config="$STAGE_ENV_CONFIG_ABS" pkgs-update || exit $?
    
    popd > /dev/null
    
    success "Package update completed"
    exit 0
fi

# Run all tests (E2E + Functional + Regression) in a single run
# Also run if specific tests are provided
if $RUN_E2E || $RUN_FUNCTIONAL || $RUN_REGRESSION || [ ${#SPECIFIC_TESTS[@]} -gt 0 ]; then
    echo ""
    info "═══════════════════════════════════"
    info "Running Tests"
    info "═══════════════════════════════════"
    echo ""
    
    if [ ! -x "$STAGE_ENV_WRAPPER" ]; then
        error "stage-env wrapper not found or not executable"
        E2E_EXIT=1
        FUNCTIONAL_EXIT=1
    else
        # Start stage environment with config
        info "Starting stage environment..."
        
        # CRITICAL: Change to stage-env directory before running wrapper
        # This ensures relative paths in config (like cache_dir, local_path) work correctly
        pushd "$SCRIPT_DIR/stage-env" > /dev/null
        
        # Convert config path to absolute for safety
        STAGE_ENV_CONFIG_ABS="$(cd "$(dirname "$STAGE_ENV_CONFIG")" && pwd)/$(basename "$STAGE_ENV_CONFIG")"
        
        # Build rebuild flag for stage-env start
        if [ "$REBUILD_IMAGES" = true ]; then
            info "Will rebuild Docker images before starting"
            ./stage-env --config="$STAGE_ENV_CONFIG_ABS" start --rebuild --wait || E2E_EXIT=$?
        else
            ./stage-env --config="$STAGE_ENV_CONFIG_ABS" start --wait || E2E_EXIT=$?
        fi
        
        popd > /dev/null
        
        if [ $E2E_EXIT -eq 0 ]; then
            success "Stage environment started"
            
            # Collect ALL test directories for single run
            TEST_DIRS=()
            
            # If specific tests provided, use them
            if [ ${#SPECIFIC_TESTS[@]} -gt 0 ]; then
                for test_path in "${SPECIFIC_TESTS[@]}"; do
                    # Convert relative path to absolute (relative to PROJECT_ROOT)
                    if [[ "$test_path" == /* ]]; then
                        abs_path="$test_path"
                    else
                        # Path is relative to PROJECT_ROOT (cellframe-node/)
                        abs_path="$PROJECT_ROOT/$test_path"
                    fi
                    
                    # For stage-env, paths need to be relative to stage-env directory
                    # Convert absolute to relative from stage-env/
                    stage_env_dir="$SCRIPT_DIR/stage-env"
                    rel_from_stage_env=$(realpath --relative-to="$stage_env_dir" "$abs_path" 2>/dev/null || echo "$abs_path")
                    
                    if [ -e "$abs_path" ]; then
                        info "Adding specific test: $test_path (stage-env: $rel_from_stage_env)"
                        TEST_DIRS+=("$rel_from_stage_env")
                    else
                        warning "Test path not found: $test_path (resolved to $abs_path)"
                    fi
                done
            else
                # Add stage-env base tests (if E2E enabled)
                if $RUN_E2E && [ -d "$STAGE_ENV_BASE_TESTS" ]; then
                    # Convert to relative path from stage-env/
                    stage_env_dir="$SCRIPT_DIR/stage-env"
                    rel_path=$(realpath --relative-to="$stage_env_dir" "$STAGE_ENV_BASE_TESTS")
                    info "Adding base tests: $rel_path"
                    TEST_DIRS+=("$rel_path")
                fi
                
                # Add E2E scenarios tests (if E2E enabled)
                if $RUN_E2E && [ -d "$SCENARIOS_TESTS" ]; then
                    stage_env_dir="$SCRIPT_DIR/stage-env"
                    rel_path=$(realpath --relative-to="$stage_env_dir" "$SCENARIOS_TESTS")
                    info "Adding E2E tests: $rel_path"
                    TEST_DIRS+=("$rel_path")
                fi
                
                # Add functional tests (if functional enabled)
                if $RUN_FUNCTIONAL && [ -d "$FUNCTIONAL_TESTS" ]; then
                    stage_env_dir="$SCRIPT_DIR/stage-env"
                    rel_path=$(realpath --relative-to="$stage_env_dir" "$FUNCTIONAL_TESTS")
                    info "Adding functional tests: $rel_path"
                    TEST_DIRS+=("$rel_path")
                fi
                
                # Add regression tests (if regression enabled)
                if $RUN_REGRESSION && [ -d "$REGRESSION_TESTS" ]; then
                    stage_env_dir="$SCRIPT_DIR/stage-env"
                    rel_path=$(realpath --relative-to="$stage_env_dir" "$REGRESSION_TESTS")
                    info "Adding regression tests: $rel_path"
                    TEST_DIRS+=("$rel_path")
                fi
            fi
            
            # Run ALL tests in one go (single run_id, single artifacts folder)
            if [ ${#TEST_DIRS[@]} -gt 0 ]; then
                info "Running ${#TEST_DIRS[@]} test suite(s) in unified run..."
                
                # CRITICAL: Run from stage-env directory for relative paths
                pushd "$SCRIPT_DIR/stage-env" > /dev/null
                
                # Use --no-start-network since we already started it above
                ./stage-env --config="$STAGE_ENV_CONFIG_ABS" run-tests --no-start-network "${TEST_DIRS[@]}" || TEST_EXIT=$?
                
                popd > /dev/null
                
                # Set individual exit codes based on result
                if [ $TEST_EXIT -ne 0 ]; then
                    if $RUN_E2E; then
                        E2E_EXIT=$TEST_EXIT
                    fi
                    if $RUN_FUNCTIONAL; then
                        FUNCTIONAL_EXIT=$TEST_EXIT
                    fi
                    if $RUN_REGRESSION; then
                        REGRESSION_EXIT=$TEST_EXIT
                    fi
                fi
            else
                warning "No test directories found"
            fi
            
            # Stop environment
            info "Stopping stage environment..."
            
            pushd "$SCRIPT_DIR/stage-env" > /dev/null
            ./stage-env --config="$STAGE_ENV_CONFIG_ABS" stop || true
            popd > /dev/null
            
            success "Stage environment stopped"
        else
            error "Failed to start stage environment"
            FUNCTIONAL_EXIT=$E2E_EXIT
        fi
    fi
fi

# Summary
echo ""
echo "════════════════════════════════════"
echo " Test Results Summary"
echo "════════════════════════════════════"

if $RUN_E2E; then
    if [ $E2E_EXIT -eq 0 ]; then
        success "E2E Tests: PASSED"
    else
        error "E2E Tests: FAILED (exit code: $E2E_EXIT)"
    fi
fi

if $RUN_FUNCTIONAL; then
    if [ $FUNCTIONAL_EXIT -eq 0 ]; then
        success "Functional Tests: PASSED"
    else
        error "Functional Tests: FAILED (exit code: $FUNCTIONAL_EXIT)"
    fi
fi

if $RUN_REGRESSION; then
    if [ $REGRESSION_EXIT -eq 0 ]; then
        success "Regression Tests: PASSED"
    else
        error "Regression Tests: FAILED (exit code: $REGRESSION_EXIT)"
    fi
fi

echo "════════════════════════════════════"

# Exit with error if any tests failed
TOTAL_EXIT=0
if [ $E2E_EXIT -ne 0 ] || [ $FUNCTIONAL_EXIT -ne 0 ] || [ $REGRESSION_EXIT -ne 0 ]; then
    TOTAL_EXIT=1
fi

exit $TOTAL_EXIT
