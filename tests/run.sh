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

set -euo pipefail

# Colors (optional; keep output ASCII-safe)
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

success() {
    echo -e "${GREEN}[ OK ]${NC} $1"
}

error() {
    echo -e "${RED}[ERR ]${NC} $1" >&2
}

warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

# Directories
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
STAGE_ENV_WRAPPER="$SCRIPT_DIR/stage-env/stage-env"
STAGE_ENV_CONFIG="$SCRIPT_DIR/stage-env.cfg"
TESTNET_DOCKER_DIR="$PROJECT_ROOT/../../tests-in-docker"
TESTNET_DOCKER_SCRIPT="$TESTNET_DOCKER_DIR/testnet.sh"

# Test directories
E2E_TESTS="$SCRIPT_DIR/e2e"
STAGE_ENV_INTEGRATION_BASE_TESTS="$SCRIPT_DIR/stage-env/tests/integration/scenarios/base"
FUNCTIONAL_TESTS="$SCRIPT_DIR/functional"

# Build directories
TEST_BUILD_DIR="$PROJECT_ROOT/test_build"

# Parse arguments
RUN_E2E=false
RUN_FUNCTIONAL=false
CLEAN_BEFORE=false
KEEP_RUNNING=false
REBUILD_IMAGES=false
SKIP_BUILD=false
BACKEND="stage-env" # stage-env | docker
PACKAGE_ARG=""

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
        --backend)
            BACKEND="${2:-}"
            shift 2
            ;;
        --package)
            PACKAGE_ARG="${2:-}"
            shift 2
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --e2e           Run only E2E tests"
            echo "  --functional    Run only functional tests"
            echo "  --clean         Clean before running (includes Docker cleanup)"
            echo "  --keep-running  Do not stop the network after tests"
            echo "  --rebuild       Force rebuild Docker images"
            echo "  --skip-build    Skip building cellframe-node (use existing)"
            echo "  --backend ARG   stage-env (default) or docker"
            echo "  --package ARG   Node package URL or path (docker backend)"
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

# Validate backend
case "$BACKEND" in
    stage-env|docker) ;;
    *)
        error "Unsupported backend: $BACKEND (expected: stage-env or docker)"
        exit 1
        ;;
esac

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

# Detect if running in cellframe-node repository and build local package
DEB_PACKAGE=""
if [ -f "$PROJECT_ROOT/CMakeLists.txt" ] && grep -q "cellframe-node" "$PROJECT_ROOT/CMakeLists.txt"; then
    if $SKIP_BUILD; then
        info "Skipping build (--skip-build specified)"
        # Try to find existing .deb package
        DEB_PACKAGE=$(find "$TEST_BUILD_DIR" -maxdepth 1 -name "cellframe-node*.deb" -type f 2>/dev/null | head -n 1)
        if [ -n "$DEB_PACKAGE" ]; then
            success "Using existing package: $(basename "$DEB_PACKAGE")"
        else
            warning "No existing package found in $TEST_BUILD_DIR"
        fi
    else
        info "Detected cellframe-node repository - building local package..."
        
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
        
        # Find the generated .deb package
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
    elif [ -z "$DEB_PACKAGE" ]; then
        warning "No .deb package to configure"
    else
        warning "stage-env.cfg not found at $STAGE_ENV_CONFIG"
    fi
else
    info "Not in cellframe-node repository - using configured node source"
fi

# If docker backend is used and no explicit package is provided,
# prefer the locally built package when available.
if [[ "$BACKEND" == "docker" ]]; then
    if [[ -z "$PACKAGE_ARG" && -n "${DEB_PACKAGE:-}" ]]; then
        PACKAGE_ARG="$DEB_PACKAGE"
    fi
fi

# Clean if requested
if $CLEAN_BEFORE; then
    warning "Cleaning test environment..."
    
    if [[ "$BACKEND" == "stage-env" ]]; then
        # Clean Docker containers, images, and volumes first
        COMPOSE_FILE="$SCRIPT_DIR/stage-env/docker-compose.generated.yml"
        if [ -f "$COMPOSE_FILE" ]; then
            info "Stopping and removing Docker containers/images..."
            docker compose -f "$COMPOSE_FILE" -p cellframe-stage stop 2>/dev/null || true
            docker compose -f "$COMPOSE_FILE" -p cellframe-stage down --rmi local --volumes 2>/dev/null || true
        fi
        
        # Also clean the cf-node images directly
        info "Removing cf-node images..."
        docker images --filter "reference=cf-node:*" -q | xargs -r docker rmi -f 2>/dev/null || true
        
        if [ -x "$STAGE_ENV_WRAPPER" ]; then
            "$STAGE_ENV_WRAPPER" clean --all --yes || true
        fi
    else
        if [ -x "$TESTNET_DOCKER_DIR/clean.sh" ]; then
            "$TESTNET_DOCKER_DIR/clean.sh" || true
        fi
    fi
    
    success "Environment cleaned"
fi

# Track results
E2E_EXIT=0
FUNCTIONAL_EXIT=0

# Docker backend: delegate to the known-good integration script.
# It starts the network and performs its own checks.
if [[ "$BACKEND" == "docker" ]]; then
    echo ""
    info "═══════════════════════════════════"
    info "Docker backend (tests-in-docker/testnet.sh)"
    info "═══════════════════════════════════"
    echo ""
    
    if [ ! -x "$TESTNET_DOCKER_SCRIPT" ]; then
        error "testnet.sh not found or not executable at: $TESTNET_DOCKER_SCRIPT"
        exit 1
    fi
    
    if [[ -n "$PACKAGE_ARG" ]]; then
        if [[ -f "$PACKAGE_ARG" ]]; then
            # testnet.sh accepts only files from its local debs/ directory.
            mkdir -p "$TESTNET_DOCKER_DIR/debs"
            cp -f "$PACKAGE_ARG" "$TESTNET_DOCKER_DIR/debs/"
            PACKAGE_ARG="$(basename "$PACKAGE_ARG")"
        fi
        info "Starting docker testnet with package: $PACKAGE_ARG"
        (cd "$TESTNET_DOCKER_DIR" && bash "./testnet.sh" "$PACKAGE_ARG")
    else
        info "Starting docker testnet with default package (master/latest)"
        (cd "$TESTNET_DOCKER_DIR" && bash "./testnet.sh")
    fi
    
    success "Docker testnet script finished successfully"
    exit 0
fi

# stage-env backend: start network once, run selected suites, then stop (unless --keep-running).
if [ ! -x "$STAGE_ENV_WRAPPER" ]; then
    error "stage-env wrapper not found or not executable at: $STAGE_ENV_WRAPPER"
    exit 1
fi

echo ""
info "═══════════════════════════════════"
info "stage-env backend"
info "═══════════════════════════════════"
echo ""

# Pre-cleanup: Stop any running containers and clean up before starting fresh
# This prevents BuildKit "image already exists" errors
COMPOSE_FILE="$SCRIPT_DIR/stage-env/docker-compose.generated.yml"
if [ -f "$COMPOSE_FILE" ]; then
    info "Cleaning up previous Docker resources..."
    docker compose -f "$COMPOSE_FILE" -p cellframe-stage stop 2>/dev/null || true
    
    if $REBUILD_IMAGES || $CLEAN_BEFORE; then
        # Full cleanup with image removal
        docker compose -f "$COMPOSE_FILE" -p cellframe-stage down --rmi local --volumes 2>/dev/null || true
        # Also remove cf-node images directly
        docker images --filter "reference=cf-node:*" -q | xargs -r docker rmi -f 2>/dev/null || true
        success "Docker cleanup completed (with image removal)"
    else
        # Quick cleanup without image removal
        docker compose -f "$COMPOSE_FILE" -p cellframe-stage down --volumes 2>/dev/null || true
        success "Docker cleanup completed"
    fi
fi

# Build stage-env start command
STAGE_ENV_START_ARGS="--wait"
if $REBUILD_IMAGES; then
    STAGE_ENV_START_ARGS="$STAGE_ENV_START_ARGS --rebuild"
fi

info "Starting stage environment..."
if "$STAGE_ENV_WRAPPER" --config="$STAGE_ENV_CONFIG" start $STAGE_ENV_START_ARGS; then
    success "Stage environment started"
else
    error "Failed to start stage environment"
    exit 1
fi

# Run E2E tests
if $RUN_E2E; then
    echo ""
    info "Running E2E Tests..."
    
    TEST_DIRS=()
    if [ -d "$E2E_TESTS" ]; then
        TEST_DIRS+=("$E2E_TESTS")
    fi
    if [ -d "$STAGE_ENV_INTEGRATION_BASE_TESTS" ]; then
        TEST_DIRS+=("$STAGE_ENV_INTEGRATION_BASE_TESTS")
    fi
    
    if [ ${#TEST_DIRS[@]} -gt 0 ]; then
        KEEP_ARG=""
        $KEEP_RUNNING && KEEP_ARG="--keep-running"
        "$STAGE_ENV_WRAPPER" --config="$STAGE_ENV_CONFIG" run-tests --no-start-network "${TEST_DIRS[@]}" $KEEP_ARG || E2E_EXIT=$?
    else
        warning "No E2E test directories found"
        E2E_EXIT=1
    fi
fi

# Run functional tests
if $RUN_FUNCTIONAL; then
    echo ""
    info "Running Functional Tests..."
    
    TEST_DIRS=()
    if [ -d "$FUNCTIONAL_TESTS" ]; then
        TEST_DIRS+=("$FUNCTIONAL_TESTS")
    fi
    
    if [ ${#TEST_DIRS[@]} -gt 0 ]; then
        KEEP_ARG=""
        $KEEP_RUNNING && KEEP_ARG="--keep-running"
        "$STAGE_ENV_WRAPPER" --config="$STAGE_ENV_CONFIG" run-tests --no-start-network "${TEST_DIRS[@]}" $KEEP_ARG || FUNCTIONAL_EXIT=$?
    else
        warning "Functional tests directory not found: $FUNCTIONAL_TESTS"
        FUNCTIONAL_EXIT=1
    fi
fi

# Stop environment (unless --keep-running)
if $KEEP_RUNNING; then
    warning "Keeping stage environment running (--keep-running)"
else
    info "Stopping stage environment..."
    "$STAGE_ENV_WRAPPER" --config="$STAGE_ENV_CONFIG" stop || true
    success "Stage environment stopped"
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

