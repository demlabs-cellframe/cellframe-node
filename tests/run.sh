#!/usr/bin/env bash
#
# Unified test runner for Cellframe Node
#
# Usage:
#   ./tests/run.sh                     # Run all tests
#   ./tests/run.sh --e2e               # Run only E2E tests
#   ./tests/run.sh --functional        # Run only functional tests
#   ./tests/run.sh --regression        # Run only regression tests
#   ./tests/run.sh --clean             # Clean cache before running
#   ./tests/run.sh --rebuild           # Rebuild Docker images
#   ./tests/run.sh --keep-running      # Don't stop network after tests
#   ./tests/run.sh --skip-build        # Skip building cellframe-node
#

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Helper functions
info() { echo -e "${BLUE}[INFO]${NC} $1"; }
success() { echo -e "${GREEN}[ OK ]${NC} $1"; }
error() { echo -e "${RED}[ERR ]${NC} $1" >&2; }
warning() { echo -e "${YELLOW}[WARN]${NC} $1"; }

# Directories
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
STAGE_ENV_WRAPPER="$SCRIPT_DIR/stage-env/stage-env"
STAGE_ENV_CONFIG="$SCRIPT_DIR/stage-env/config/stage-env.cfg"

# Test directories
E2E_TESTS="$SCRIPT_DIR/e2e"
SCENARIOS_TESTS="$SCRIPT_DIR/e2e"
FUNCTIONAL_TESTS="$SCRIPT_DIR/functional"
REGRESSION_TESTS="$SCRIPT_DIR/regression"
STAGE_ENV_INTEGRATION_BASE_TESTS="$SCRIPT_DIR/stage-env/tests/integration/scenarios/base"

# Build directories
TEST_BUILD_DIR="$PROJECT_ROOT/build"

# Parse arguments
RUN_E2E=false
RUN_FUNCTIONAL=false
RUN_REGRESSION=false
CLEAN_BEFORE=false
KEEP_RUNNING=false
REBUILD_IMAGES=false
SKIP_BUILD=false
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
        --keep-running)
            KEEP_RUNNING=true
            shift
            ;;
        --rebuild)
            REBUILD_IMAGES=true
            shift
            ;;
        --skip-build)
            SKIP_BUILD=true
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
            echo "  --regression    Run only regression tests"
            echo "  --clean         Clean cache before running"
            echo "  --keep-running  Don't stop the network after tests"
            echo "  --rebuild       Rebuild Docker images"
            echo "  --skip-build    Skip building cellframe-node (use existing)"
            echo "  --pkgs-update   Update packages in running containers"
            echo "  --stop          Stop stage environment"
            echo "  -h, --help      Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                                    # Run all tests"
            echo "  $0 --e2e                              # Run all E2E tests"
            echo "  $0 --clean --e2e                      # Clean cache and run E2E tests"
            echo "  $0 --rebuild --e2e                    # Rebuild images and run E2E tests"
            echo "  $0 --keep-running                     # Keep network running after tests"
            echo "  $0 --stop                             # Stop stage environment"
            echo "  $0 tests/e2e/token                    # Run specific test suite"
            echo ""
            exit 0
            ;;
        -*)
            error "Unknown option: $1"
            exit 1
            ;;
        *)
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

# Handle --pkgs-update
if [ "$PKGS_UPDATE" = true ]; then
    info "Updating packages in running containers..."
    if [ -x "$STAGE_ENV_WRAPPER" ]; then
        pushd "$SCRIPT_DIR/stage-env" > /dev/null
        STAGE_ENV_CONFIG_ABS="$(cd "$(dirname "$STAGE_ENV_CONFIG")" && pwd)/$(basename "$STAGE_ENV_CONFIG")"
        ./stage-env --config="$STAGE_ENV_CONFIG_ABS" pkgs-update || exit $?
        popd > /dev/null
    else
        error "stage-env wrapper not found or not executable"
        exit 1
    fi
    success "Package update completed"
    exit 0
fi

# If specific tests provided, use them directly
if [ ${#SPECIFIC_TESTS[@]} -gt 0 ]; then
    info "Specific tests requested: ${SPECIFIC_TESTS[*]}"
elif ! $RUN_E2E && ! $RUN_FUNCTIONAL && ! $RUN_REGRESSION; then
    # If nothing specified, run all
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

# Detect if running in cellframe-node repository and build local package
DEB_PACKAGE=""
if [ -f "$PROJECT_ROOT/CMakeLists.txt" ] && grep -q "cellframe-node" "$PROJECT_ROOT/CMakeLists.txt"; then
    if $SKIP_BUILD; then
        info "Skipping build (--skip-build specified)"
        DEB_PACKAGE=$(find "$TEST_BUILD_DIR" -maxdepth 1 -name "cellframe-node*.deb" -type f 2>/dev/null | head -n 1)
        if [ -n "$DEB_PACKAGE" ]; then
            success "Using existing package: $(basename "$DEB_PACKAGE")"
        else
            warning "No existing package found in $TEST_BUILD_DIR"
        fi
    else
        info "Detected cellframe-node repository - building local package..."
        mkdir -p "$TEST_BUILD_DIR"
        cd "$TEST_BUILD_DIR"
        
        info "Configuring with CMake (Debug mode)..."
        cmake -DCMAKE_BUILD_TYPE=Debug -DBUILD_TESTS=On .. || {
            error "CMake configuration failed"
            exit 1
        }
        
        info "Building cellframe-node..."
        make -j$(nproc) cellframe-node || {
            error "Build failed"
            exit 1
        }
        
        info "Creating .deb package..."
        cpack -G DEB || {
            error "Packaging failed"
            exit 1
        }
        
        DEB_PACKAGE=$(find "$TEST_BUILD_DIR" -maxdepth 1 -name "cellframe-node*.deb" -type f | head -n 1)
        
        if [ -z "$DEB_PACKAGE" ]; then
            error "No .deb package found after build"
            exit 1
        fi
        
        success "Package created: $(basename "$DEB_PACKAGE")"
        cd "$PROJECT_ROOT"
    fi
    
    # Update stage-env.cfg to use local package
    if [ -n "$DEB_PACKAGE" ] && [ -f "$STAGE_ENV_CONFIG" ]; then
        info "Updating stage-env.cfg with local package path..."
        python3 -c "
import configparser
config = configparser.ConfigParser()
config.read('$STAGE_ENV_CONFIG')

if not config.has_section('node_source'):
    config.add_section('node_source')

config.set('node_source', 'type', 'local')
config.set('node_source', 'local_path', '$DEB_PACKAGE')

with open('$STAGE_ENV_CONFIG', 'w') as f:
    config.write(f)
" || {
            warning "Failed to update stage-env.cfg automatically"
        }
        success "stage-env.cfg updated to use local package"
    fi
else
    info "Not in cellframe-node repository - using configured node source"
fi

# Clean if requested
if $CLEAN_BEFORE; then
    warning "Cleaning test environment..."
    
    if [ -x "$STAGE_ENV_WRAPPER" ]; then
        pushd "$SCRIPT_DIR/stage-env" > /dev/null
        STAGE_ENV_CONFIG_ABS="$(cd "$(dirname "$STAGE_ENV_CONFIG")" && pwd)/$(basename "$STAGE_ENV_CONFIG")"
        ./stage-env --config="$STAGE_ENV_CONFIG_ABS" clean --all || true
        popd > /dev/null
    fi
    
    # Additional cleanup
    STAGE_ENV_DIR="$SCRIPT_DIR/stage-env"
    TESTING_DIR="$SCRIPT_DIR/testing"
    
    if [ -d "$TESTING_DIR/snapshots" ] && [ "$(ls -A "$TESTING_DIR/snapshots" 2>/dev/null)" ]; then
        info "Removing remaining snapshots..."
        docker run --rm -v "$TESTING_DIR:/cleanup" alpine:latest sh -c "rm -rf /cleanup/snapshots/*" 2>/dev/null || true
    fi
    
    success "Environment cleaned"
fi

# Track results
E2E_EXIT=0
FUNCTIONAL_EXIT=0
REGRESSION_EXIT=0
TEST_EXIT=0

# Ensure stage-env is executable
if [ ! -x "$STAGE_ENV_WRAPPER" ]; then
    error "stage-env wrapper not found or not executable"
    exit 1
fi

echo ""
info "═══════════════════════════════════"
info "Running Tests"
info "═══════════════════════════════════"
echo ""

# Start stage environment
pushd "$SCRIPT_DIR/stage-env" > /dev/null
STAGE_ENV_CONFIG_ABS="$(cd "$(dirname "$STAGE_ENV_CONFIG")" && pwd)/$(basename "$STAGE_ENV_CONFIG")"

# Build start arguments
START_ARGS="--wait"
if $REBUILD_IMAGES; then
    START_ARGS="$START_ARGS --rebuild"
fi
if $KEEP_RUNNING; then
    START_ARGS="$START_ARGS --keep-running"
fi

info "Starting stage environment..."
./stage-env --config="$STAGE_ENV_CONFIG_ABS" start $START_ARGS || E2E_EXIT=$?
popd > /dev/null

if [ $E2E_EXIT -eq 0 ]; then
    success "Stage environment started"
    
    # Collect test directories
    TEST_DIRS=()
    
    if [ ${#SPECIFIC_TESTS[@]} -gt 0 ]; then
        for test_path in "${SPECIFIC_TESTS[@]}"; do
            if [[ "$test_path" == /* ]]; then
                abs_path="$test_path"
            else
                abs_path="$PROJECT_ROOT/$test_path"
            fi
            stage_env_dir="$SCRIPT_DIR/stage-env"
            rel_from_stage_env=$(realpath --relative-to="$stage_env_dir" "$abs_path" 2>/dev/null || echo "$abs_path")
            if [ -e "$abs_path" ]; then
                TEST_DIRS+=("$rel_from_stage_env")
            else
                warning "Test path not found: $test_path"
            fi
        done
    else
        if $RUN_E2E && [ -d "$E2E_TESTS" ]; then
            stage_env_dir="$SCRIPT_DIR/stage-env"
            rel_path=$(realpath --relative-to="$stage_env_dir" "$E2E_TESTS")
            TEST_DIRS+=("$rel_path")
        fi
        
        if $RUN_FUNCTIONAL && [ -d "$FUNCTIONAL_TESTS" ]; then
            stage_env_dir="$SCRIPT_DIR/stage-env"
            rel_path=$(realpath --relative-to="$stage_env_dir" "$FUNCTIONAL_TESTS")
            TEST_DIRS+=("$rel_path")
        fi
        
        if $RUN_REGRESSION && [ -d "$REGRESSION_TESTS" ]; then
            stage_env_dir="$SCRIPT_DIR/stage-env"
            rel_path=$(realpath --relative-to="$stage_env_dir" "$REGRESSION_TESTS")
            TEST_DIRS+=("$rel_path")
        fi
    fi
    
    # Run tests
    if [ ${#TEST_DIRS[@]} -gt 0 ]; then
        info "Running ${#TEST_DIRS[@]} test suite(s)..."
        
        pushd "$SCRIPT_DIR/stage-env" > /dev/null
        ./stage-env --config="$STAGE_ENV_CONFIG_ABS" run-tests --no-start-network "${TEST_DIRS[@]}" || TEST_EXIT=$?
        popd > /dev/null
        
        if [ $TEST_EXIT -ne 0 ]; then
            E2E_EXIT=$TEST_EXIT
            FUNCTIONAL_EXIT=$TEST_EXIT
            REGRESSION_EXIT=$TEST_EXIT
        fi
    else
        warning "No test directories found"
    fi
    
    # Stop environment (unless --keep-running)
    if $KEEP_RUNNING; then
        warning "Keeping stage environment running (--keep-running)"
    else
        info "Stopping stage environment..."
        pushd "$SCRIPT_DIR/stage-env" > /dev/null
        ./stage-env --config="$STAGE_ENV_CONFIG_ABS" stop || true
        popd > /dev/null
        success "Stage environment stopped"
    fi
else
    error "Failed to start stage environment"
    FUNCTIONAL_EXIT=$E2E_EXIT
    REGRESSION_EXIT=$E2E_EXIT
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
