#!/bin/bash
# Docker entrypoint for Cellframe Node
# Minimal wrapper that delegates to Python modules

set -e

NODE_ID=${NODE_ID:-1}
NODE_ROLE=${NODE_ROLE:-root}
NETWORK_NAME=${NETWORK_NAME:-stagenet}

echo "=== Cellframe Node Docker Entrypoint ==="
echo "Node ID: $NODE_ID"
echo "Node Role: $NODE_ROLE"
echo "Network: $NETWORK_NAME"

# Ensure all required directories exist
mkdir -p /opt/cellframe-node/var/log
mkdir -p /opt/cellframe-node/var/run
mkdir -p /opt/cellframe-node/var/lib
mkdir -p /opt/cellframe-node/var/lib/wallet
mkdir -p /opt/cellframe-node/var/lib/global_db
mkdir -p /opt/cellframe-node/var/lib/ca

# Fix permissions for mounted volumes
chmod -R 755 /opt/cellframe-node/var 2>/dev/null || true

# Start cellframe-node with maximum debug level
echo "Starting cellframe-node..."
exec /opt/cellframe-node/bin/cellframe-node -D 5

