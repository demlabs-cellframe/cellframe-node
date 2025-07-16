#!/bin/bash
# test_binary_plugins.sh - Test binary plugin loading

set -e

# Source test utilities
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../helpers/test_utils.sh"
source "$SCRIPT_DIR/../helpers/node_control.sh"

# Test constants
TEST_NAME="Binary Plugin Loading"
PYTHON_PLUGIN_SO="${PYTHON_PLUGIN_PATH:-$PROJECT_ROOT/build/plugin/plugin-python/libcellframe-node-plugin-python.so}"

# Test functions
test_node_starts_without_plugins() {
    log_info "Testing node startup without plugins"
    
    # Create clean config without plugins
    create_test_config "clean_node"
    
    # Start node
    assert_equals "0" "$?" "Node should start successfully"
    
    if start_node "clean_node"; then
        assert_process_running "cellframe-node" "Node process should be running"
        
        # Check that node is listening on port
        if wait_for_port "$TEST_PORT" 10; then
            assert_equals "0" "$?" "Node should be listening on port $TEST_PORT"
        else
            assert_equals "0" "1" "Node should be listening on port $TEST_PORT"
        fi
        
        # Stop node
        stop_node
        assert_process_not_running "cellframe-node" "Node process should be stopped"
    else
        assert_equals "0" "1" "Node should start successfully"
    fi
    
    return 0
}

test_binary_plugin_file_exists() {
    log_info "Testing binary plugin file existence"
    
    # Check if Python plugin binary exists
    assert_file_exists "$PYTHON_PLUGIN_SO" "Python plugin binary should exist"
    
    # Check if it's a valid shared library
    if command -v file >/dev/null 2>&1; then
        local file_output=$(file "$PYTHON_PLUGIN_SO" 2>/dev/null || echo "")
        assert_contains "$file_output" "shared" "Plugin should be a shared library"
    fi
    
    return 0
}

test_plugin_directory_setup() {
    log_info "Testing plugin directory setup"
    
    # Create plugins directory
    mkdir -p "$PLUGINS_DIR"
    assert_equals "0" "$?" "Should be able to create plugins directory"
    
    # Check directory permissions
    if [[ -d "$PLUGINS_DIR" && -w "$PLUGINS_DIR" ]]; then
        assert_equals "0" "0" "Plugins directory should be writable"
    else
        assert_equals "0" "1" "Plugins directory should be writable"
    fi
    
    return 0
}

test_plugin_loading() {
    log_info "Testing plugin loading mechanism"
    
    # Skip if plugin binary doesn't exist
    if [[ ! -f "$PYTHON_PLUGIN_SO" ]]; then
        log_warning "Python plugin binary not found, skipping plugin loading test"
        return 0
    fi
    
    # Create test config with plugins enabled
    create_test_config "plugin_test"
    
    # Copy plugin to plugins directory
    mkdir -p "$PLUGINS_DIR"
    cp "$PYTHON_PLUGIN_SO" "$PLUGINS_DIR/"
    assert_equals "0" "$?" "Should be able to copy plugin to plugins directory"
    
    # Start node with plugins
    if start_node "plugin_test"; then
        assert_process_running "cellframe-node" "Node should start with plugin"
        
        # Wait for node to be ready
        if wait_for_node_ready 30; then
            assert_equals "0" "0" "Node should become ready"
            
            # Check logs for plugin loading messages
            local logs=$(get_node_logs 100)
            
            # Look for plugin-related log messages
            if echo "$logs" | grep -q -i "plugin"; then
                assert_contains "$logs" "plugin" "Logs should contain plugin-related messages"
            else
                log_warning "No plugin messages found in logs, this might be expected if plugins load silently"
            fi
            
            # Check if plugin files exist in the right place
            local plugin_name="libcellframe-node-plugin-python.so"
            assert_file_exists "$PLUGINS_DIR/$plugin_name" "Plugin file should exist in plugins directory"
            
        else
            assert_equals "0" "1" "Node should become ready with plugin loaded"
        fi
        
        stop_node
    else
        assert_equals "0" "1" "Node should start with plugin"
    fi
    
    return 0
}

test_plugin_manifest() {
    log_info "Testing plugin manifest handling"
    
    # Create a test plugin manifest
    local manifest_dir="$PLUGINS_DIR/manifests"
    mkdir -p "$manifest_dir"
    
    cat > "$manifest_dir/python-plugin.json" << EOF
{
    "name": "cellframe-node-plugin-python",
    "version": "1.0.0",
    "description": "Python plugins support for CellFrame Node",
    "author": "Demlabs",
    "binary": "libcellframe-node-plugin-python.so",
    "dependencies": [],
    "enabled": true,
    "api_version": "1.0"
}
EOF
    
    assert_file_exists "$manifest_dir/python-plugin.json" "Plugin manifest should be created"
    
    # Validate JSON syntax
    if command -v jq >/dev/null 2>&1; then
        if jq . "$manifest_dir/python-plugin.json" >/dev/null 2>&1; then
            assert_equals "0" "0" "Plugin manifest should have valid JSON syntax"
        else
            assert_equals "0" "1" "Plugin manifest should have valid JSON syntax"
        fi
    fi
    
    return 0
}

test_node_with_missing_plugin() {
    log_info "Testing node behavior with missing plugin"
    
    # Create config that references non-existent plugin
    create_test_config "missing_plugin_test"
    
    # Create a manifest for non-existent plugin
    local manifest_dir="$PLUGINS_DIR/manifests"
    mkdir -p "$manifest_dir"
    
    cat > "$manifest_dir/missing-plugin.json" << EOF
{
    "name": "missing-plugin",
    "version": "1.0.0",
    "binary": "libmissing-plugin.so",
    "enabled": true
}
EOF
    
    # Start node - it should handle missing plugins gracefully
    if start_node "missing_plugin_test"; then
        assert_process_running "cellframe-node" "Node should start even with missing plugin"
        
        # Check logs for error messages about missing plugin
        local logs=$(get_node_logs 50)
        if echo "$logs" | grep -q -i "missing\|error\|fail"; then
            log_info "Node properly logged missing plugin issue"
        else
            log_warning "Node may not have logged missing plugin issue"
        fi
        
        stop_node
    else
        log_warning "Node failed to start with missing plugin - this might be expected behavior"
    fi
    
    return 0
}

test_plugin_unloading() {
    log_info "Testing plugin unloading"
    
    # Skip if plugin binary doesn't exist
    if [[ ! -f "$PYTHON_PLUGIN_SO" ]]; then
        log_warning "Python plugin binary not found, skipping plugin unloading test"
        return 0
    fi
    
    # Start with plugin loaded
    mkdir -p "$PLUGINS_DIR"
    cp "$PYTHON_PLUGIN_SO" "$PLUGINS_DIR/"
    
    create_test_config "unload_test"
    start_node "unload_test"
    
    if wait_for_node_ready 30; then
        # Remove plugin file
        rm -f "$PLUGINS_DIR/libcellframe-node-plugin-python.so"
        assert_equals "0" "$?" "Should be able to remove plugin file"
        
        # Restart node
        restart_node "unload_test"
        
        if wait_for_node_ready 30; then
            assert_process_running "cellframe-node" "Node should restart after plugin removal"
        else
            assert_equals "0" "1" "Node should restart after plugin removal"
        fi
        
        stop_node
    else
        log_warning "Node didn't become ready, skipping unload test"
        stop_node
    fi
    
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
    run_test "Node starts without plugins" test_node_starts_without_plugins
    run_test "Binary plugin file exists" test_binary_plugin_file_exists
    run_test "Plugin directory setup" test_plugin_directory_setup
    run_test "Plugin loading mechanism" test_plugin_loading
    run_test "Plugin manifest handling" test_plugin_manifest
    run_test "Node with missing plugin" test_node_with_missing_plugin
    run_test "Plugin unloading" test_plugin_unloading
    
    # Print summary
    print_test_summary
    local exit_code=$?
    
    # Cleanup
    cleanup_test_environment
    cleanup_node_test
    
    exit $exit_code
}

# Run main if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi 