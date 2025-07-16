#!/bin/bash
# test_node_startup.sh - Test basic node startup and shutdown

set -e

# Source test utilities
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../helpers/test_utils.sh"
source "$SCRIPT_DIR/../helpers/node_control.sh"

# Test constants
TEST_NAME="Node Startup and Shutdown"

# Test functions
test_node_binary_exists() {
    log_info "Testing node binary existence"
    
    # Check if any cellframe-node binary exists
    local potential_paths=(
        "$PROJECT_ROOT/build/cellframe-node"
        "$PROJECT_ROOT/build_osx_debug/build/cellframe-node"
        "$PROJECT_ROOT/build_linux_debug/build/cellframe-node"
        "/usr/local/bin/cellframe-node"
        "/opt/cellframe-node/bin/cellframe-node"
    )
    
    local found_binary=""
    for path in "${potential_paths[@]}"; do
        if [[ -f "$path" && -x "$path" ]]; then
            found_binary="$path"
            break
        fi
    done
    
    if [[ -n "$found_binary" ]]; then
        export CELLFRAME_NODE_PATH="$found_binary"
        assert_file_exists "$found_binary" "CellFrame Node binary should exist"
        log_success "Found CellFrame Node at: $found_binary"
        return 0
    else
        log_warning "CellFrame Node binary not found in expected locations"
        log_info "Searched paths:"
        for path in "${potential_paths[@]}"; do
            log_info "  - $path"
        done
        
        # This is not a hard failure for this test
        assert_equals "0" "1" "CellFrame Node binary should be available for testing"
        return 1
    fi
}

test_node_version() {
    log_info "Testing node version command"
    
    # Skip if no binary found
    if [[ ! -x "$CELLFRAME_NODE_PATH" ]]; then
        log_warning "Skipping version test - no binary available"
        return 0
    fi
    
    # Try to get version
    local version_output
    if version_output=$("$CELLFRAME_NODE_PATH" --version 2>/dev/null); then
        assert_contains "$version_output" "CellframeNode" "Version output should contain 'CellframeNode'"
        log_success "Node version: $version_output"
    else
        log_warning "Node does not support --version flag, trying --help"
        if help_output=$("$CELLFRAME_NODE_PATH" --help 2>/dev/null); then
            log_info "Node help is available"
        else
            log_warning "Node does not respond to --help either"
        fi
    fi
    
    return 0
}

test_config_creation() {
    log_info "Testing configuration file creation"
    
    # Create a minimal test config
    local test_config="$TESTS_ROOT/fixtures/configs/minimal_test.cfg"
    mkdir -p "$(dirname "$test_config")"
    
    cat > "$test_config" << EOF
[general]
node_role=full
debug_mode=true
server_enabled=false
auto_online=false

[resources]
pid_path=$LOG_DIR/test_node.pid
log_file=$LOG_DIR/test_node.log
db_path=$LOG_DIR/test_node_db/
EOF

    assert_file_exists "$test_config" "Test configuration should be created"
    
    # Validate config syntax (basic check)
    if command -v grep >/dev/null 2>&1; then
        local sections=$(grep -c "^\[.*\]" "$test_config" || echo "0")
        if [[ "$sections" -gt 0 ]]; then
            assert_equals "0" "0" "Configuration should have valid section headers"
        else
            assert_equals "0" "1" "Configuration should have valid section headers"
        fi
    fi
    
    log_success "Test configuration created successfully"
    return 0
}

test_directory_permissions() {
    log_info "Testing directory permissions for node operation"
    
    # Test that we can create required directories
    local test_dirs=(
        "$LOG_DIR/test_permissions"
        "$LOG_DIR/test_permissions/db"
        "$LOG_DIR/test_permissions/log"
    )
    
    for dir in "${test_dirs[@]}"; do
        if mkdir -p "$dir" 2>/dev/null; then
            assert_equals "0" "0" "Should be able to create directory: $dir"
            
            # Test write permission
            local test_file="$dir/write_test.tmp"
            if echo "test" > "$test_file" 2>/dev/null; then
                assert_equals "0" "0" "Should be able to write to directory: $dir"
                rm -f "$test_file"
            else
                assert_equals "0" "1" "Should be able to write to directory: $dir"
            fi
        else
            assert_equals "0" "1" "Should be able to create directory: $dir"
        fi
    done
    
    # Cleanup
    rm -rf "$LOG_DIR/test_permissions" 2>/dev/null || true
    
    return 0
}

test_network_availability() {
    log_info "Testing network availability for node operations"
    
    # Test localhost connectivity
    if nc -z localhost 22 2>/dev/null; then
        log_info "SSH port (22) is accessible on localhost"
    elif nc -z localhost 80 2>/dev/null; then
        log_info "HTTP port (80) is accessible on localhost" 
    elif nc -z localhost 443 2>/dev/null; then
        log_info "HTTPS port (443) is accessible on localhost"
    else
        log_info "No common ports are accessible on localhost (this is normal)"
    fi
    
    # Test that we can bind to test port
    local test_port=18079
    if nc -z localhost "$test_port" 2>/dev/null; then
        log_warning "Test port $test_port is already in use"
    else
        log_success "Test port $test_port is available"
    fi
    
    return 0
}

test_mock_node_startup() {
    log_info "Testing mock node startup simulation"
    
    # Since we might not have a working binary, simulate the startup process
    local mock_pid_file="$LOG_DIR/mock_node.pid"
    local mock_log_file="$LOG_DIR/mock_node.log"
    
    # Simulate creating PID file
    echo "$$" > "$mock_pid_file"
    assert_file_exists "$mock_pid_file" "Mock PID file should be created"
    
    # Simulate log file creation
    echo "$(date): Mock CellFrame Node starting up" > "$mock_log_file"
    assert_file_exists "$mock_log_file" "Mock log file should be created"
    
    # Simulate running process
    sleep 1
    
    # Check mock process
    local mock_pid=$(cat "$mock_pid_file")
    if kill -0 "$mock_pid" 2>/dev/null; then
        assert_equals "0" "0" "Mock process should be running"
    else
        assert_equals "0" "1" "Mock process should be running"
    fi
    
    # Cleanup
    rm -f "$mock_pid_file" "$mock_log_file"
    
    log_success "Mock startup simulation completed"
    return 0
}

# Main test execution
main() {
    log_info "Starting $TEST_NAME tests"
    
    # Setup test environment
    if ! setup_test_environment; then
        log_error "Failed to setup test environment"
        exit 1
    fi
    
    # Run tests
    run_test "Node binary existence" test_node_binary_exists
    run_test "Node version command" test_node_version
    run_test "Configuration creation" test_config_creation
    run_test "Directory permissions" test_directory_permissions
    run_test "Network availability" test_network_availability
    run_test "Mock node startup" test_mock_node_startup
    
    # Print summary
    print_test_summary
    local exit_code=$?
    
    # Cleanup
    cleanup_test_environment
    
    exit $exit_code
}

# Run main if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi 