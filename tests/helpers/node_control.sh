#!/bin/bash
# node_control.sh - Node management functions for tests

# Source test utilities
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/test_utils.sh"

# Node management
NODE_PID=""
NODE_CONFIG_FILE=""
NODE_LOG_FILE=""

# Create test configuration
create_test_config() {
    local config_name="${1:-test_node}"
    local config_file="$CELLFRAME_CONFIG_PATH/${config_name}.cfg"
    
    log_info "Creating test configuration: $config_file"
    
    mkdir -p "$(dirname "$config_file")"
    
    cat > "$config_file" << EOF
[general]
node_role=full
auto_online=false
debug_mode=true
server_enabled=true
server_addr=0.0.0.0
server_port=$TEST_PORT
accept_ca_list=auto
enabled_chains=$TEST_NETWORK

[plugins]
enabled=true
path=$PLUGINS_DIR
python_plugins_enabled=false

[resources]
pid_path=$LOG_DIR/${config_name}.pid
log_file=$LOG_DIR/${config_name}.log
db_path=$LOG_DIR/${config_name}_db/

[network-$TEST_NETWORK]
enabled=true
role=full
node_type=full

[chain-$TEST_NETWORK]
enabled=true
node_role=full
ledger_cache_enabled=true
EOF

    NODE_CONFIG_FILE="$config_file"
    NODE_LOG_FILE="$LOG_DIR/${config_name}.log"
    
    log_success "Test configuration created: $config_file"
    return 0
}

# Start CellFrame Node
start_node() {
    local config_name="${1:-test_node}"
    local timeout="${2:-$TEST_TIMEOUT}"
    
    # Create config if it doesn't exist
    if [[ -z "$NODE_CONFIG_FILE" ]]; then
        create_test_config "$config_name"
    fi
    
    log_info "Starting CellFrame Node with config: $NODE_CONFIG_FILE"
    
    # Check if node is already running
    if [[ -n "$NODE_PID" ]] && kill -0 "$NODE_PID" 2>/dev/null; then
        log_warning "Node is already running with PID: $NODE_PID"
        return 0
    fi
    
    # Clean up any existing process
    stop_node_force
    
    # Start the node in background
    "$CELLFRAME_NODE_PATH" -c "$NODE_CONFIG_FILE" > "$NODE_LOG_FILE" 2>&1 &
    NODE_PID=$!
    
    log_info "Started CellFrame Node with PID: $NODE_PID"
    
    # Wait for node to start
    if wait_for_process "cellframe-node" "$timeout"; then
        if wait_for_port "$TEST_PORT" "$timeout"; then
            log_success "CellFrame Node started successfully"
            return 0
        else
            log_error "Node started but port $TEST_PORT is not accessible"
            stop_node
            return 1
        fi
    else
        log_error "Failed to start CellFrame Node"
        stop_node
        return 1
    fi
}

# Stop CellFrame Node gracefully
stop_node() {
    if [[ -n "$NODE_PID" ]]; then
        log_info "Stopping CellFrame Node (PID: $NODE_PID)"
        
        # Send SIGTERM
        if kill "$NODE_PID" 2>/dev/null; then
            # Wait for graceful shutdown
            for i in {1..10}; do
                if ! kill -0 "$NODE_PID" 2>/dev/null; then
                    log_success "Node stopped gracefully"
                    NODE_PID=""
                    return 0
                fi
                sleep 1
            done
            
            # Force kill if still running
            log_warning "Node didn't stop gracefully, forcing..."
            kill -9 "$NODE_PID" 2>/dev/null
            NODE_PID=""
        else
            log_warning "Node PID $NODE_PID not found"
            NODE_PID=""
        fi
    fi
    
    # Make sure no node processes are running
    stop_node_force
    return 0
}

# Force stop all node processes
stop_node_force() {
    log_debug "Force stopping all CellFrame Node processes"
    
    # Kill any running cellframe-node processes
    pkill -f "cellframe-node" 2>/dev/null || true
    sleep 1
    pkill -9 -f "cellframe-node" 2>/dev/null || true
    
    NODE_PID=""
}

# Restart node
restart_node() {
    local config_name="${1:-test_node}"
    local timeout="${2:-$TEST_TIMEOUT}"
    
    log_info "Restarting CellFrame Node"
    stop_node
    sleep 2
    start_node "$config_name" "$timeout"
}

# Check if node is running
is_node_running() {
    if [[ -n "$NODE_PID" ]] && kill -0 "$NODE_PID" 2>/dev/null; then
        return 0
    else
        return 1
    fi
}

# Wait for node to be ready
wait_for_node_ready() {
    local timeout="${1:-$TEST_TIMEOUT}"
    
    log_info "Waiting for node to be ready (timeout: ${timeout}s)"
    
    for ((i=0; i<timeout; i++)); do
        if is_node_running && nc -z localhost "$TEST_PORT" 2>/dev/null; then
            # Try to get node status via CLI
            if "$CELLFRAME_NODE_PATH-cli" version >/dev/null 2>&1; then
                log_success "Node is ready"
                return 0
            fi
        fi
        sleep 1
    done
    
    log_error "Timeout waiting for node to be ready"
    return 1
}

# Get node logs
get_node_logs() {
    local lines="${1:-50}"
    
    if [[ -f "$NODE_LOG_FILE" ]]; then
        tail -n "$lines" "$NODE_LOG_FILE"
    else
        log_warning "Node log file not found: $NODE_LOG_FILE"
        return 1
    fi
}

# Check node status via CLI
get_node_status() {
    if [[ -x "$CELLFRAME_NODE_PATH-cli" ]]; then
        "$CELLFRAME_NODE_PATH-cli" version 2>/dev/null
    else
        log_warning "Node CLI not found: $CELLFRAME_NODE_PATH-cli"
        return 1
    fi
}

# Load plugin
load_plugin() {
    local plugin_path="$1"
    local plugin_name="$(basename "$plugin_path")"
    
    log_info "Loading plugin: $plugin_name"
    
    if [[ ! -f "$plugin_path" ]]; then
        log_error "Plugin file not found: $plugin_path"
        return 1
    fi
    
    # Copy plugin to plugins directory
    mkdir -p "$PLUGINS_DIR"
    cp "$plugin_path" "$PLUGINS_DIR/"
    
    # Restart node to load plugin
    restart_node
    
    # Check if plugin is loaded (this would depend on specific CLI commands)
    if "$CELLFRAME_NODE_PATH-cli" plugins list 2>/dev/null | grep -q "$plugin_name"; then
        log_success "Plugin loaded successfully: $plugin_name"
        return 0
    else
        log_error "Failed to load plugin: $plugin_name"
        return 1
    fi
}

# Unload plugin
unload_plugin() {
    local plugin_name="$1"
    
    log_info "Unloading plugin: $plugin_name"
    
    # Remove plugin file
    rm -f "$PLUGINS_DIR/$plugin_name"*
    
    # Restart node
    restart_node
    
    log_success "Plugin unloaded: $plugin_name"
}

# Send HTTP request to node
send_http_request() {
    local endpoint="$1"
    local method="${2:-GET}"
    local data="${3:-}"
    local expected_status="${4:-200}"
    
    local url="http://localhost:$TEST_PORT$endpoint"
    local curl_args=("-s" "-w" "%{http_code}" "-X" "$method")
    
    if [[ -n "$data" ]]; then
        curl_args+=("-H" "Content-Type: application/json" "-d" "$data")
    fi
    
    log_debug "Sending $method request to $url"
    
    local response=$(curl "${curl_args[@]}" "$url" 2>/dev/null)
    local status_code="${response: -3}"
    local body="${response%???}"
    
    if [[ "$status_code" == "$expected_status" ]]; then
        echo "$body"
        return 0
    else
        log_error "HTTP request failed. Expected: $expected_status, Got: $status_code"
        log_error "Response: $body"
        return 1
    fi
}

# Cleanup function for node tests
cleanup_node_test() {
    log_info "Cleaning up node test environment"
    
    # Stop node
    stop_node
    
    # Clean up files
    if [[ -n "$NODE_LOG_FILE" ]] && [[ -f "$NODE_LOG_FILE" ]]; then
        rm -f "$NODE_LOG_FILE"
    fi
    
    if [[ -n "$NODE_CONFIG_FILE" ]] && [[ -f "$NODE_CONFIG_FILE" ]]; then
        rm -f "$NODE_CONFIG_FILE"
    fi
    
    # Clean up test database
    rm -rf "$LOG_DIR/test_node_db" 2>/dev/null || true
    
    # Reset variables
    NODE_PID=""
    NODE_CONFIG_FILE=""
    NODE_LOG_FILE=""
    
    log_success "Node test environment cleaned up"
}

# Trap to ensure cleanup on exit
trap cleanup_node_test EXIT

# Export functions
export -f create_test_config start_node stop_node stop_node_force restart_node
export -f is_node_running wait_for_node_ready get_node_logs get_node_status
export -f load_plugin unload_plugin send_http_request cleanup_node_test 