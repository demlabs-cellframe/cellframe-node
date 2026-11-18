#!/usr/bin/env bash
# Build the amd64 DEB for cellframe-node inside the reproducible builder image.
#
# Usage:
#   tools/build-amd64-deb.sh [build-dir] [jobs]
#
#   build-dir  output directory under ../linux-build (default: build-amd64)
#   jobs       make parallelism (default: 8)
#
# Environment overrides:
#   BUILDER_IMAGE  docker image (default: cellframe-node-builder:trixie)
#   OUT_ROOT       host directory mounted as /out (default: <repo>/../linux-build)
#   BUILD_TYPE     CMAKE_BUILD_TYPE (default: RelWithDebInfo)
#   CONFIGURE=1    re-run cmake even when the cache exists (default: auto)
#
# The script mounts the repository at /src and the output root at /out, so the
# build never writes into the source tree. Incremental builds reuse the CMake
# cache; a version change in version.mk needs CONFIGURE=1 (CPack caches the
# package file name).
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BUILD_DIR_NAME="${1:-build-amd64}"
JOBS="${2:-8}"
BUILDER_IMAGE="${BUILDER_IMAGE:-cellframe-node-builder:trixie}"
OUT_ROOT="${OUT_ROOT:-$(cd "$REPO_DIR/.." && pwd)/linux-build}"
BUILD_TYPE="${BUILD_TYPE:-RelWithDebInfo}"
BUILD_PATH="$OUT_ROOT/$BUILD_DIR_NAME"

if ! command -v docker >/dev/null 2>&1; then
    echo "error: docker is not available" >&2
    exit 1
fi
mkdir -p "$BUILD_PATH"

# CPack caches the DEB file name (including the version) in CPackConfig.cmake;
# re-run cmake when version.mk changed since the last configure.
VERSION_NOW="$(grep -E '^VERSION_(MAJOR|MINOR|PATCH)=' "$REPO_DIR/version.mk" | tr '\n' ' ')"
VERSION_FILE="$BUILD_PATH/.configured-version"
NEED_CONFIGURE="${CONFIGURE:-0}"
if [ ! -f "$BUILD_PATH/CMakeCache.txt" ] || [ "$(cat "$VERSION_FILE" 2>/dev/null || true)" != "$VERSION_NOW" ]; then
    NEED_CONFIGURE=1
fi

echo "==> repo:    $REPO_DIR"
echo "==> out:     $BUILD_PATH"
echo "==> image:   $BUILDER_IMAGE (linux/amd64)"
echo "==> version: $VERSION_NOW"
echo "==> jobs:    $JOBS"

CMAKE_STEP=""
if [ "$NEED_CONFIGURE" = "1" ]; then
    CMAKE_STEP="cmake /src -DCMAKE_BUILD_TYPE=$BUILD_TYPE && "
fi

docker run --rm --platform linux/amd64 --entrypoint bash \
    -v "$REPO_DIR:/src" \
    -v "$OUT_ROOT:/out" \
    -w "/out/$BUILD_DIR_NAME" \
    "$BUILDER_IMAGE" \
    -c "set -e; ${CMAKE_STEP}make -j$JOBS && make package"

echo "$VERSION_NOW" > "$VERSION_FILE"

DEB="$(ls -t "$BUILD_PATH"/cellframe-node-*-amd64.deb 2>/dev/null | head -1 || true)"
if [ -z "$DEB" ]; then
    echo "error: no DEB produced in $BUILD_PATH" >&2
    exit 1
fi

echo "==> artifact: $DEB"
ls -la "$DEB"
if command -v md5sum >/dev/null 2>&1; then
    md5sum "$DEB"
elif command -v md5 >/dev/null 2>&1; then
    md5 "$DEB"
fi
