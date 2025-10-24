#!/usr/bin/env bash
#
# Unified test runner for Cellframe Node
#
# Usage:
#   ./tests/run.sh                     # Run all tests
#   ./tests/run.sh --e2e               # Run only E2E tests
#   ./tests/run.sh --functional        # Run only functional tests
#   ./tests/run.sh --clean             # Clean before running
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

# Build directories
TEST_BUILD_DIR="$PROJECT_ROOT/build"

# Parse arguments
RUN_E2E=false
RUN_FUNCTIONAL=false
CLEAN_BEFORE=false
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
        --clean)
            CLEAN_BEFORE=true
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS] [TEST_PATH...]"
            echo ""
            echo "Options:"
            echo "  --e2e           Run only E2E tests"
            echo "  --functional    Run only functional tests"
            echo "  --clean         Clean before running"
            echo "  -h, --help      Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                                    # Run all tests"
            echo "  $0 --e2e                              # Run all E2E tests"
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

# If specific tests provided, use them directly
if [ ${#SPECIFIC_TESTS[@]} -gt 0 ]; then
    info "Specific tests requested: ${SPECIFIC_TESTS[*]}"
    # Don't set RUN_E2E or RUN_FUNCTIONAL - we'll use SPECIFIC_TESTS directly
elif ! $RUN_E2E && ! $RUN_FUNCTIONAL; then
    # If neither specified and no specific tests, run both
    RUN_E2E=true
    RUN_FUNCTIONAL=true
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
if [ -f "$PROJECT_ROOT/CMakeLists.txt" ] && grep -q "cellframe-node" "$PROJECT_ROOT/CMakeLists.txt"; then
    info "Detected cellframe-node repository"
    
    # Check if we need to build
    DEB_PACKAGE=$(find "$TEST_BUILD_DIR" -maxdepth 1 -name "cellframe-node*.deb" -type f 2>/dev/null | head -n 1)
    
    if [ -z "$DEB_PACKAGE" ] || [ "$CLEAN_BEFORE" = true ]; then
        if [ "$CLEAN_BEFORE" = true ]; then
            info "Cleaning previous build..."
            rm -rf "$TEST_BUILD_DIR"
        fi
        
        info "Building local package..."
        
        # Create test_build directory
        mkdir -p "$TEST_BUILD_DIR"
        cd "$TEST_BUILD_DIR"
        
        # Configure with CMake (Debug mode for testing)
        info "Configuring with CMake (Debug mode)..."
        cmake -DCMAKE_BUILD_TYPE=Debug -DBUILD_TESTS=On .. || {
            error "CMake configuration failed"
            exit 1
        }
        
        # Build
        info "Building cellframe-node..."
        make -j$(nproc) cellframe-node || {
            error "Build failed"
            exit 1
        }
        
        # Package with cpack
        info "Creating .deb package..."
        cpack -G DEB || {
            error "Packaging failed"
            exit 1
        }
        
        # Find the newly generated .deb package
        DEB_PACKAGE=$(find "$TEST_BUILD_DIR" -maxdepth 1 -name "cellframe-node*.deb" -type f | head -n 1)
    else
        info "Using existing package: $(basename "$DEB_PACKAGE")"
    fi
    
    if [ -z "$DEB_PACKAGE" ]; then
        error "No .deb package found after build"
        exit 1
    fi
    
    success "Package created: $(basename "$DEB_PACKAGE")"
    
    # Update stage-env.cfg to use local package
    if [ -f "$STAGE_ENV_CONFIG" ]; then
        info "Updating stage-env.cfg with local package path..."
        
        # Create temporary config with updated node_source
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
            info "Please update [node_source] section manually:"
            info "  type = local"
            info "  local_path = $DEB_PACKAGE"
        }
        
        success "stage-env.cfg updated to use local package"
    else
        warning "stage-env.cfg not found at $STAGE_ENV_CONFIG"
    fi
    
    cd "$PROJECT_ROOT"
else
    info "Not in cellframe-node repository - using configured node source"
fi

# Clean if requested
if $CLEAN_BEFORE; then
    warning "Cleaning test environment..."
    
    if [ -x "$STAGE_ENV_WRAPPER" ]; then
        "$STAGE_ENV_WRAPPER" clean --all || true
    fi
    
    success "Environment cleaned"
fi

# Track results
E2E_EXIT=0
FUNCTIONAL_EXIT=0

# Run all tests (E2E + Functional) in a single run
if $RUN_E2E || $RUN_FUNCTIONAL; then
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
        # Start stage environment with config (clean data for fresh state)
        info "Starting stage environment..."
        "$STAGE_ENV_WRAPPER" --config="$STAGE_ENV_CONFIG" start --wait --clean || E2E_EXIT=$?
        
        if [ $E2E_EXIT -eq 0 ]; then
            success "Stage environment started"
            
            # Collect ALL test directories for single run
            TEST_DIRS=()
            
            # If specific tests provided, use them
            if [ ${#SPECIFIC_TESTS[@]} -gt 0 ]; then
                for test_path in "${SPECIFIC_TESTS[@]}"; do
                    # Convert relative to absolute if needed
                    if [[ "$test_path" == /* ]]; then
                        abs_path="$test_path"
                    else
                        abs_path="$PROJECT_ROOT/$test_path"
                    fi
                    
                    if [ -e "$abs_path" ]; then
                        info "Adding specific test: $test_path"
                        TEST_DIRS+=("$abs_path")
                    else
                        warning "Test path not found: $test_path (resolved to $abs_path)"
                    fi
                done
            else
                # Add stage-env base tests (if E2E enabled)
                if $RUN_E2E && [ -d "$STAGE_ENV_BASE_TESTS" ]; then
                    info "Adding base tests: $STAGE_ENV_BASE_TESTS"
                    TEST_DIRS+=("$STAGE_ENV_BASE_TESTS")
                fi
                
                # Add E2E scenarios tests (if E2E enabled)
                if $RUN_E2E && [ -d "$SCENARIOS_TESTS" ]; then
                    info "Adding E2E tests: $SCENARIOS_TESTS"
                    TEST_DIRS+=("$SCENARIOS_TESTS")
                fi
                
                # Add functional tests (if functional enabled)
                if $RUN_FUNCTIONAL && [ -d "$FUNCTIONAL_TESTS" ]; then
                    info "Adding functional tests: $FUNCTIONAL_TESTS"
                    TEST_DIRS+=("$FUNCTIONAL_TESTS")
                fi
            fi
            
            # Run ALL tests in one go (single run_id, single artifacts folder)
            if [ ${#TEST_DIRS[@]} -gt 0 ]; then
                info "Running ${#TEST_DIRS[@]} test suite(s) in unified run..."
                "$STAGE_ENV_WRAPPER" --config="$STAGE_ENV_CONFIG" run-tests "${TEST_DIRS[@]}" || TEST_EXIT=$?
                
                # Set individual exit codes based on result
                if [ $TEST_EXIT -ne 0 ]; then
                    if $RUN_E2E; then
                        E2E_EXIT=$TEST_EXIT
                    fi
                    if $RUN_FUNCTIONAL; then
                        FUNCTIONAL_EXIT=$TEST_EXIT
                    fi
                fi
            else
                warning "No test directories found"
            fi
            
            # Stop environment and clean volumes
            info "Stopping stage environment..."
            "$STAGE_ENV_WRAPPER" --config="$STAGE_ENV_CONFIG" stop --volumes || true
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

echo "════════════════════════════════════"

# Exit with error if any tests failed
TOTAL_EXIT=0
if [ $E2E_EXIT -ne 0 ] || [ $FUNCTIONAL_EXIT -ne 0 ]; then
    TOTAL_EXIT=1
fi

exit $TOTAL_EXIT

