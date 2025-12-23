#!/bin/bash
#
# Clean all stage-env cache, snapshots, and Docker resources
# Run this script to start the network from scratch
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
STAGE_ENV_DIR="$SCRIPT_DIR/stage-env"
TESTING_DIR="$SCRIPT_DIR/testing"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

info() { echo -e "${BLUE}[INFO]${NC} $1"; }
success() { echo -e "${GREEN}[OK]${NC} $1"; }
warning() { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERR]${NC} $1"; }

echo ""
echo "========================================="
echo "  Stage-env Full Cleanup Script"
echo "========================================="
echo ""

# Parse arguments
REMOVE_IMAGES=false
FORCE=false

for arg in "$@"; do
    case $arg in
        --images)
            REMOVE_IMAGES=true
            shift
            ;;
        -f|--force)
            FORCE=true
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --images    Also remove Docker images (cf-node:*)"
            echo "  -f, --force Skip confirmation prompt"
            echo "  -h, --help  Show this help message"
            echo ""
            exit 0
            ;;
    esac
done

# Confirmation
if [ "$FORCE" = false ]; then
    echo "This will delete:"
    echo "  - stage-env/cache (configs, data, certs, crash-artifacts)"
    echo "  - testing/snapshots"
    echo "  - testing/artifacts"
    echo "  - All cellframe-stage Docker containers"
    if [ "$REMOVE_IMAGES" = true ]; then
        echo "  - All cf-node Docker images"
    fi
    echo ""
    read -p "Are you sure? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        info "Cancelled"
        exit 0
    fi
fi

echo ""

# Stop and remove Docker containers
info "Stopping Docker containers..."
cd "$STAGE_ENV_DIR"
if [ -f "docker-compose.generated.yml" ]; then
    docker compose -f docker-compose.generated.yml -p cellframe-stage down --volumes 2>/dev/null || true
fi
docker compose -f docker-compose.yml -p cellframe-stage down --volumes 2>/dev/null || true

# Remove any stray containers
CONTAINERS=$(docker ps -aq --filter "name=cellframe-stage" 2>/dev/null || true)
if [ -n "$CONTAINERS" ]; then
    info "Removing stray containers..."
    echo "$CONTAINERS" | xargs -r docker rm -f 2>/dev/null || true
fi
success "Docker containers stopped"

# Remove Docker images if requested
if [ "$REMOVE_IMAGES" = true ]; then
    info "Removing Docker images..."
    docker images --filter "reference=cf-node:*" -q 2>/dev/null | xargs -r docker rmi -f 2>/dev/null || true
    success "Docker images removed"
fi

# Clean stage-env cache
info "Cleaning stage-env cache..."
if [ -d "$STAGE_ENV_DIR/cache" ]; then
    # Some files may be owned by root (from Docker), use sudo if needed
    sudo rm -rf "$STAGE_ENV_DIR/cache/configs" 2>/dev/null || rm -rf "$STAGE_ENV_DIR/cache/configs" 2>/dev/null || true
    sudo rm -rf "$STAGE_ENV_DIR/cache/data" 2>/dev/null || rm -rf "$STAGE_ENV_DIR/cache/data" 2>/dev/null || true
    sudo rm -rf "$STAGE_ENV_DIR/cache/certs" 2>/dev/null || rm -rf "$STAGE_ENV_DIR/cache/certs" 2>/dev/null || true
    sudo rm -rf "$STAGE_ENV_DIR/cache/crash-artifacts" 2>/dev/null || rm -rf "$STAGE_ENV_DIR/cache/crash-artifacts" 2>/dev/null || true
    # Keep cellframe-packages (downloaded packages cache)
    success "stage-env/cache cleaned"
else
    warning "stage-env/cache not found"
fi

# Clean stage-env artifacts
info "Cleaning stage-env artifacts..."
if [ -d "$STAGE_ENV_DIR/artifacts" ]; then
    rm -rf "$STAGE_ENV_DIR/artifacts"/* 2>/dev/null || true
    success "stage-env/artifacts cleaned"
fi

# Clean testing snapshots
info "Cleaning testing snapshots..."
if [ -d "$TESTING_DIR/snapshots" ]; then
    sudo rm -rf "$TESTING_DIR/snapshots"/* 2>/dev/null || rm -rf "$TESTING_DIR/snapshots"/* 2>/dev/null || true
    success "testing/snapshots cleaned"
else
    warning "testing/snapshots not found"
fi

# Clean testing artifacts
info "Cleaning testing artifacts..."
if [ -d "$TESTING_DIR/artifacts" ]; then
    rm -rf "$TESTING_DIR/artifacts"/* 2>/dev/null || true
    success "testing/artifacts cleaned"
fi

# Clean generated compose file
info "Cleaning generated files..."
rm -f "$STAGE_ENV_DIR/docker-compose.generated.yml" 2>/dev/null || true
success "Generated files cleaned"

# Clean tmp logs
info "Cleaning tmp logs..."
rm -f /tmp/cellframe-stage-*.log 2>/dev/null || true
rm -f /tmp/final_test.log 2>/dev/null || true
success "Tmp logs cleaned"

echo ""
echo "========================================="
success "Cleanup complete! You can now run:"
echo ""
echo "  ./run.sh --keep-running"
echo ""
echo "========================================="

