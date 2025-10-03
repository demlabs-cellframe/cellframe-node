#!/bin/bash
# Startup script for cellframe-node in Docker (without systemd)
# This simulates how a user would start the node manually

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting cellframe-node..."

# Check if already running
if pgrep -x "cellframe-node" > /dev/null; then
    echo "[INFO] cellframe-node is already running"
    exit 0
fi

# Start node in background
cd /opt/cellframe-node
/opt/cellframe-node/bin/cellframe-node > /opt/cellframe-node/var/log/cellframe-node.log 2>&1 &
NODE_PID=$!

# Wait for node to start
echo "[INFO] Waiting for node to initialize..."
sleep 3

# Check if process is still running
if ps -p $NODE_PID > /dev/null 2>&1; then
    echo "[OK] Node started successfully (PID: $NODE_PID)"
    echo $NODE_PID > /opt/cellframe-node/var/run/cellframe-node.pid
    
    # Wait for CLI socket to be ready
    echo "[INFO] Waiting for CLI server socket..."
    for i in {1..30}; do
        if [ -S "/opt/cellframe-node/var/run/node_cli" ]; then
            echo "[OK] CLI server is ready"
            exit 0
        fi
        sleep 1
    done
    
    echo "[WARN] CLI socket not ready after 30 seconds, but node is running"
    exit 0
else
    echo "[ERROR] Node failed to start"
    cat /opt/cellframe-node/var/log/cellframe-node.log 2>/dev/null || echo "[ERROR] No log file found"
    exit 1
fi

