# Dockerfile for Cellframe Node test build environment
# 
# This image contains only build tools and dependencies.
# Sources are mounted as volumes at runtime for fast incremental builds.
# 
# Usage:
#   Build image once:
#     docker build -f testing/e2e/Dockerfile.builder -t cellframe-builder-env .
#   
#   Run build with volume mounting:
#     docker run --rm \
#       -v $(pwd):/project:ro \
#       -v $(pwd)/build-docker:/project/build \
#       -e BUILD_TYPE=debug \
#       cellframe-builder-env
#
# =============================================================================
FROM debian:bookworm-slim

ARG BUILD_TYPE=debug

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    git \
    pkg-config \
    wget \
    ca-certificates \
    libssl-dev \
    libsqlite3-dev \
    python3 \
    python3-dev \
    libpq-dev \
    zlib1g-dev \
    libzip-dev \
    xsltproc \
    file \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /project

# Default build command (executed when container starts)
CMD ["bash", "-c", "\
    set -e && \
    mkdir -p build && \
    cd build && \
    cmake -DCMAKE_BUILD_TYPE=${BUILD_TYPE:-debug} .. && \
    make cellframe-node cert-generator -j$(nproc) && \
    echo '✅ Build complete!' && \
    ls -lh cellframe-node cert-generator \
"]
