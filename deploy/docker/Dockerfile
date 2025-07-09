# CellFrame Python SDK - Production Docker Image
FROM debian:bookworm-slim

LABEL maintainer="CellFrame Team <team@cellframe.net>"
LABEL description="CellFrame Python SDK Production Container"
LABEL version="1.0.0"

# Build arguments
ARG PYTHON_VERSION=3.9
ARG CELLFRAME_VERSION=latest
ARG BUILD_DATE
ARG VCS_REF

# Metadata
LABEL org.opencontainers.image.title="CellFrame Python SDK"
LABEL org.opencontainers.image.description="Production-ready CellFrame Python SDK container"
LABEL org.opencontainers.image.url="https://cellframe.net"
LABEL org.opencontainers.image.source="https://github.com/cellframe-network/cellframe-node"
LABEL org.opencontainers.image.version="${CELLFRAME_VERSION}"
LABEL org.opencontainers.image.created="${BUILD_DATE}"
LABEL org.opencontainers.image.revision="${VCS_REF}"
LABEL org.opencontainers.image.vendor="CellFrame Network"

# Environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV CELLFRAME_PYTHON_SDK_CONFIG=/opt/cellframe/etc/python-sdk.conf
ENV CELLFRAME_PYTHON_SDK_LOG_LEVEL=info
ENV CELLFRAME_PYTHON_SDK_PLUGINS_DIR=/opt/cellframe/lib/python-sdk/plugins
ENV PYTHONPATH=/opt/cellframe/lib/python-sdk

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3=${PYTHON_VERSION}* \
    python3-dev \
    python3-pip \
    python3-venv \
    build-essential \
    cmake \
    make \
    gcc \
    g++ \
    libc6-dev \
    libssl-dev \
    libffi-dev \
    libsqlite3-dev \
    libreadline-dev \
    zlib1g-dev \
    libbz2-dev \
    libncurses5-dev \
    libgdbm-dev \
    libnss3-dev \
    liblzma-dev \
    curl \
    wget \
    git \
    ca-certificates \
    sudo \
    && rm -rf /var/lib/apt/lists/*

# Create cellframe user and group
RUN groupadd --system cellframe && \
    useradd --system --no-create-home --shell /bin/false --gid cellframe cellframe

# Create directory structure
RUN mkdir -p /opt/cellframe/{bin,lib,etc,var/{log,run,lib},share/{doc,man}} && \
    mkdir -p /opt/cellframe/lib/python-sdk/{plugins,config,cache} && \
    mkdir -p /opt/cellframe/var/{log,run,lib}/python-sdk && \
    mkdir -p /opt/cellframe/etc/{python-sdk,monitoring,security} && \
    chown -R cellframe:cellframe /opt/cellframe/var && \
    chmod -R 755 /opt/cellframe/{bin,lib,etc,share} && \
    chmod -R 750 /opt/cellframe/var

# Install Python dependencies
COPY requirements.txt /tmp/requirements.txt
RUN pip3 install --no-cache-dir --upgrade pip setuptools wheel && \
    pip3 install --no-cache-dir -r /tmp/requirements.txt && \
    rm /tmp/requirements.txt

# Copy source code
COPY . /usr/src/cellframe-python-sdk/
WORKDIR /usr/src/cellframe-python-sdk

# Build and install Python SDK
RUN mkdir -p build && \
    cd build && \
    cmake .. \
        -DCMAKE_INSTALL_PREFIX=/opt/cellframe \
        -DCMAKE_BUILD_TYPE=Release \
        -DPYTHON_VERSION=${PYTHON_VERSION} \
        -DENABLE_TESTING=OFF && \
    make -j$(nproc) && \
    make install && \
    cd .. && \
    rm -rf build

# Copy configuration files
COPY deploy/config/ /opt/cellframe/etc/
COPY deploy/monitoring/ /opt/cellframe/etc/monitoring/
COPY deploy/security/ /opt/cellframe/etc/security/

# Set proper permissions
RUN find /opt/cellframe/etc -type f -exec chmod 640 {} \; && \
    find /opt/cellframe/etc -type d -exec chmod 750 {} \; && \
    find /opt/cellframe/etc/security -type f -exec chmod 600 {} \; && \
    find /opt/cellframe/etc/security -type d -exec chmod 700 {} \; && \
    chown -R root:cellframe /opt/cellframe/etc && \
    chown -R cellframe:cellframe /opt/cellframe/var

# Create startup script
RUN cat > /opt/cellframe/bin/start-python-sdk.sh << 'EOF'
#!/bin/bash
set -e

# Initialize environment
export CELLFRAME_PYTHON_SDK_CONFIG=${CELLFRAME_PYTHON_SDK_CONFIG:-/opt/cellframe/etc/python-sdk.conf}
export CELLFRAME_PYTHON_SDK_LOG_LEVEL=${CELLFRAME_PYTHON_SDK_LOG_LEVEL:-info}
export CELLFRAME_PYTHON_SDK_PLUGINS_DIR=${CELLFRAME_PYTHON_SDK_PLUGINS_DIR:-/opt/cellframe/lib/python-sdk/plugins}
export PYTHONPATH=${PYTHONPATH:-/opt/cellframe/lib/python-sdk}

# Create log directory if it doesn't exist
mkdir -p /opt/cellframe/var/log/python-sdk

# Log startup
echo "$(date): Starting CellFrame Python SDK" >> /opt/cellframe/var/log/python-sdk/startup.log

# Start the service
exec python3 -m cellframe_python_sdk.main "$@"
EOF

RUN chmod +x /opt/cellframe/bin/start-python-sdk.sh

# Create health check script
RUN cat > /opt/cellframe/bin/health-check.sh << 'EOF'
#!/bin/bash
set -e

# Check if the service is responding
if python3 -c "import sys; sys.path.append('/opt/cellframe/lib/python-sdk'); import cellframe; print('OK')" > /dev/null 2>&1; then
    echo "Health check passed"
    exit 0
else
    echo "Health check failed"
    exit 1
fi
EOF

RUN chmod +x /opt/cellframe/bin/health-check.sh

# Expose ports
EXPOSE 8080/tcp 8443/tcp

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD /opt/cellframe/bin/health-check.sh

# Volume for persistent data
VOLUME ["/opt/cellframe/var", "/opt/cellframe/etc"]

# Switch to cellframe user
USER cellframe

# Set working directory
WORKDIR /opt/cellframe

# Default command
CMD ["/opt/cellframe/bin/start-python-sdk.sh"] 