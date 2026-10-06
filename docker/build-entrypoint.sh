#!/bin/bash
# Builder-container entrypoint: modes build (default) / test / debug node run.
# Sources are read from the /src mount, everything produced goes to /out.
set -e

SRC="${SRC:-/src}"
OUT="${OUT:-/out}"
BUILD_DIR="$OUT/build"
BUILD_TYPE="${BUILD_TYPE:-RelWithDebInfo}"

echo "[builder] src=$SRC out=$OUT type=$BUILD_TYPE tests=${BUILD_TESTS:-0} node=${RUN_NODE:-0}"

# First-time configure. Tests mode enables the sdk test targets so ctest can
# find them in the same build tree.
if [ ! -f "$BUILD_DIR/CMakeCache.txt" ]; then
    cmake -S "$SRC" -B "$BUILD_DIR" \
        -DCMAKE_POLICY_VERSION_MINIMUM=3.5 \
        -DCMAKE_BUILD_TYPE="$BUILD_TYPE" \
        -DCREATE_DEFAULT_CONFIG=OFF \
        -DSUPPORT_PYTHON_PLUGINS=OFF \
        -DBUILD_WITH_PYTHON_ENV=OFF \
        -DBUILD_WITH_GDB_DRIVER_MDBX=ON \
        -DBUILD_CELLFRAME_SDK_TESTS=$([ "${BUILD_TESTS:-0}" = "1" ] && echo ON || echo OFF)
fi

if [ "${RUN_NODE:-0}" != "1" ]; then
    cmake --build "$BUILD_DIR" -j"$(nproc)" \
        --target cellframe-node cellframe-node-cli cellframe-node-tool cellframe-node-config
fi

if [ "${BUILD_TESTS:-0}" = "1" ]; then
    cmake --build "$BUILD_DIR" -j"$(nproc)"
    ( cd "$BUILD_DIR" && ctest --output-on-failure )
fi

if [ "${RUN_NODE:-0}" = "1" ]; then
    [ -x "$BUILD_DIR/cellframe-node" ] || cmake --build "$BUILD_DIR" -j"$(nproc)" --target cellframe-node
    # Debug node run reuses the deploy entrypoint logic with an out-of-tree
    # BASE; templates come straight from the source tree, the python runtime
    # from the cpython fetched by configure.
    export BASE="$OUT/node-base"
    export TPL_SHARE="$SRC/dist/share"
    export TPL_ETC="$SRC/dist/etc"
    mkdir -p "$BASE/bin" "$BASE/python"
    ln -sf "$BUILD_DIR/cellframe-node"      "$BASE/bin/cellframe-node"
    ln -sf "$BUILD_DIR/cellframe-node-cli"  "$BASE/bin/cellframe-node-cli"
    ln -sf "$BUILD_DIR/cellframe-node-tool" "$BASE/bin/cellframe-node-tool"
    ln -sfn "$BUILD_DIR/_deps/cpythonstatic-src/lib" "$BASE/python/lib"
    [ -n "${BUILDER_UID:-}" ] && [ -n "${BUILDER_GID:-}" ] && chown -R "$BUILDER_UID:$BUILDER_GID" "$OUT/node-base" || true
    cd "$BASE"
    exec /usr/local/bin/entrypoint.sh "$BASE/bin/cellframe-node"
fi

# Assemble the deploy-image payload (see Dockerfile): prebuilt binaries plus
# the python runtime, laid out exactly as the deploy Dockerfile COPYs them.
mkdir -p "$OUT/artifacts/bin" "$OUT/artifacts/python-lib"
cp -f "$BUILD_DIR/cellframe-node" "$BUILD_DIR/cellframe-node-cli" \
      "$BUILD_DIR/cellframe-node-tool" "$BUILD_DIR/conftool/cellframe-node-config" \
      "$OUT/artifacts/bin/" 2>/dev/null || true
cp -a "$BUILD_DIR/_deps/cpythonstatic-src/lib/." "$OUT/artifacts/python-lib/" 2>/dev/null || true

# Hand the artifacts back to the host user.
if [ -n "${BUILDER_UID:-}" ] && [ -n "${BUILDER_GID:-}" ]; then
    chown -R "$BUILDER_UID:$BUILDER_GID" "$OUT" || true
fi
echo "[builder] done: $BUILD_DIR"
