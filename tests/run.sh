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

# Test directories
STAGE_ENV_BASE_TESTS="$SCRIPT_DIR/stage-env/tests/base"
FUNCTIONAL_TESTS="$SCRIPT_DIR/functional"
SCENARIOS_TESTS="$SCRIPT_DIR/scenarios"

# Parse arguments
RUN_E2E=false
RUN_FUNCTIONAL=false
CLEAN_BEFORE=false

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
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --e2e           Run only E2E tests"
            echo "  --functional    Run only functional tests"
            echo "  --clean         Clean before running"
            echo "  -h, --help      Show this help message"
            echo ""
            echo "If no test type specified, all tests will run."
            exit 0
            ;;
        *)
            error "Unknown option: $1"
            exit 1
            ;;
    esac
done

# If neither specified, run both
if ! $RUN_E2E && ! $RUN_FUNCTIONAL; then
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

# Run E2E tests
if $RUN_E2E; then
    echo ""
    info "═══════════════════════════════════"
    info "Running E2E Tests"
    info "═══════════════════════════════════"
    echo ""
    
    if [ ! -x "$STAGE_ENV_WRAPPER" ]; then
        error "stage-env wrapper not found or not executable"
        E2E_EXIT=1
    else
        # Start stage environment
        info "Starting stage environment..."
        "$STAGE_ENV_WRAPPER" start --wait || E2E_EXIT=$?
        
        if [ $E2E_EXIT -eq 0 ]; then
            success "Stage environment started"
            
            # Collect E2E test directories
            TEST_DIRS=()
            
            # Add stage-env base tests
            if [ -d "$STAGE_ENV_BASE_TESTS" ]; then
                TEST_DIRS+=("$STAGE_ENV_BASE_TESTS")
            fi
            
            # Add scenarios tests if exist
            if [ -d "$SCENARIOS_TESTS" ]; then
                TEST_DIRS+=("$SCENARIOS_TESTS")
            fi
            
            # Run E2E tests through stage-env
            if [ ${#TEST_DIRS[@]} -gt 0 ]; then
                info "Running E2E test scenarios..."
                "$STAGE_ENV_WRAPPER" run-tests "${TEST_DIRS[@]}" || E2E_EXIT=$?
            else
                warning "No E2E test directories found"
                info "Expected: $SCENARIOS_TESTS (YAML scenarios - phase 14.5.8)"
            fi
            
            # Stop environment
            info "Stopping stage environment..."
            "$STAGE_ENV_WRAPPER" stop || true
            success "Stage environment stopped"
        else
            error "Failed to start stage environment"
        fi
    fi
fi

# Run functional tests
if $RUN_FUNCTIONAL; then
    echo ""
    info "═══════════════════════════════════"
    info "Running Functional Tests"
    info "═══════════════════════════════════"
    echo ""
    
    if [ ! -x "$STAGE_ENV_WRAPPER" ]; then
        error "stage-env wrapper not found or not executable"
        FUNCTIONAL_EXIT=1
    else
        # Collect functional test directories
        TEST_DIRS=()
        
        if [ -d "$FUNCTIONAL_TESTS" ]; then
            TEST_DIRS+=("$FUNCTIONAL_TESTS")
        fi
        
        # Run functional tests through stage-env
        if [ ${#TEST_DIRS[@]} -gt 0 ]; then
            info "Running functional test scenarios..."
            "$STAGE_ENV_WRAPPER" run-tests "${TEST_DIRS[@]}" || FUNCTIONAL_EXIT=$?
            
            if [ $FUNCTIONAL_EXIT -eq 0 ]; then
                success "Functional tests passed"
            else
                error "Functional tests failed"
            fi
        else
            warning "Functional tests directory not found: $FUNCTIONAL_TESTS"
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

