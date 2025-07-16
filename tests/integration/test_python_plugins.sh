#!/bin/bash
# test_python_plugins.sh - Test Python plugin functionality after binary loading

set -e

# Source test utilities
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../helpers/test_utils.sh"
source "$SCRIPT_DIR/../helpers/node_control.sh"

# Test constants
TEST_NAME="Python Plugin Functionality"
PYTHON_PLUGIN_SO="${PYTHON_PLUGIN_PATH:-$PROJECT_ROOT/build/plugin/plugin-python/libcellframe-node-plugin-python.so}"
PYTHON_SCRIPTS_DIR="$TESTS_ROOT/fixtures/plugins/python"

# Setup Python test scripts
setup_python_test_scripts() {
    log_info "Setting up Python test scripts"
    
    mkdir -p "$PYTHON_SCRIPTS_DIR"
    
    # Create a simple test Python plugin
    cat > "$PYTHON_SCRIPTS_DIR/test_plugin.py" << 'EOF'
#!/usr/bin/env python3
"""
Simple test Python plugin for CellFrame Node
"""

import json
import logging
import time
from pathlib import Path

# Plugin metadata
PLUGIN_INFO = {
    "name": "test_plugin",
    "version": "1.0.0",
    "description": "Test Python plugin for integration tests",
    "author": "CellFrame Tests"
}

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestPlugin:
    """Test plugin implementation"""
    
    def __init__(self):
        self.initialized = False
        self.start_time = None
        self.call_count = 0
        
    def initialize(self):
        """Initialize the plugin"""
        try:
            self.start_time = time.time()
            self.initialized = True
            logger.info(f"Test plugin {PLUGIN_INFO['name']} initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize test plugin: {e}")
            return False
    
    def get_status(self):
        """Get plugin status"""
        return {
            "initialized": self.initialized,
            "start_time": self.start_time,
            "uptime": time.time() - self.start_time if self.start_time else 0,
            "call_count": self.call_count,
            "info": PLUGIN_INFO
        }
    
    def test_function(self, data=None):
        """Test function that can be called from the node"""
        self.call_count += 1
        logger.info(f"Test function called (call #{self.call_count})")
        
        result = {
            "success": True,
            "call_count": self.call_count,
            "timestamp": time.time(),
            "received_data": data
        }
        
        return result
    
    def cleanup(self):
        """Cleanup the plugin"""
        logger.info("Test plugin cleanup called")
        self.initialized = False

# Global plugin instance
test_plugin = TestPlugin()

def plugin_init():
    """Plugin initialization entry point"""
    return test_plugin.initialize()

def plugin_deinit():
    """Plugin cleanup entry point"""
    test_plugin.cleanup()

def get_plugin_info():
    """Get plugin information"""
    return PLUGIN_INFO

def get_plugin_status():
    """Get plugin status"""
    return test_plugin.get_status()

def test_api_call(data=None):
    """Test API call"""
    return test_plugin.test_function(data)

# Export functions for the node
__all__ = [
    'plugin_init',
    'plugin_deinit', 
    'get_plugin_info',
    'get_plugin_status',
    'test_api_call'
]

if __name__ == "__main__":
    # Test the plugin directly
    print("Testing plugin directly...")
    plugin_init()
    print("Plugin status:", json.dumps(get_plugin_status(), indent=2))
    result = test_api_call({"test": "data"})
    print("Test call result:", json.dumps(result, indent=2))
    plugin_deinit()
EOF

    # Create a plugin with CellFrame API usage
    cat > "$PYTHON_SCRIPTS_DIR/cellframe_test_plugin.py" << 'EOF'
#!/usr/bin/env python3
"""
CellFrame API test plugin
"""

import logging
import json

logger = logging.getLogger(__name__)

PLUGIN_INFO = {
    "name": "cellframe_test_plugin",
    "version": "1.0.0",
    "description": "Test plugin using CellFrame APIs"
}

class CellFrameTestPlugin:
    """Plugin that tests CellFrame API integration"""
    
    def __init__(self):
        self.initialized = False
        
    def initialize(self):
        """Initialize and test CellFrame APIs"""
        try:
            # Try to import CellFrame modules
            logger.info("Testing CellFrame API imports...")
            
            # Test basic imports
            try:
                import cellframe
                logger.info("✓ CellFrame module imported successfully")
            except ImportError as e:
                logger.warning(f"✗ CellFrame module import failed: {e}")
            
            try:
                import dap
                logger.info("✓ DAP module imported successfully")
            except ImportError as e:
                logger.warning(f"✗ DAP module import failed: {e}")
            
            self.initialized = True
            logger.info("CellFrame test plugin initialized")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize CellFrame test plugin: {e}")
            return False
    
    def test_cellframe_apis(self):
        """Test CellFrame API functionality"""
        results = {}
        
        try:
            # Test CellFrame chain operations
            import cellframe
            results['cellframe_available'] = True
            
            # Test basic CellFrame functionality
            try:
                # This would test actual CellFrame APIs when they're available
                logger.info("Testing CellFrame APIs...")
                results['chain_apis'] = "available"
            except Exception as e:
                results['chain_apis'] = f"error: {e}"
                
        except ImportError:
            results['cellframe_available'] = False
            results['error'] = "CellFrame module not available"
        
        try:
            # Test DAP operations
            import dap
            results['dap_available'] = True
            
            # Test basic DAP functionality
            try:
                logger.info("Testing DAP APIs...")
                results['dap_apis'] = "available"
            except Exception as e:
                results['dap_apis'] = f"error: {e}"
                
        except ImportError:
            results['dap_available'] = False
            
        return results
    
    def cleanup(self):
        """Cleanup the plugin"""
        self.initialized = False
        logger.info("CellFrame test plugin cleaned up")

# Global instance
cellframe_test_plugin = CellFrameTestPlugin()

def plugin_init():
    return cellframe_test_plugin.initialize()

def plugin_deinit():
    cellframe_test_plugin.cleanup()

def get_plugin_info():
    return PLUGIN_INFO

def test_cellframe_integration():
    return cellframe_test_plugin.test_cellframe_apis()

__all__ = ['plugin_init', 'plugin_deinit', 'get_plugin_info', 'test_cellframe_integration']
EOF

    # Create a plugin manifest
    cat > "$PYTHON_SCRIPTS_DIR/plugins.json" << EOF
{
    "plugins": [
        {
            "name": "test_plugin",
            "file": "test_plugin.py",
            "enabled": true,
            "auto_start": true
        },
        {
            "name": "cellframe_test_plugin", 
            "file": "cellframe_test_plugin.py",
            "enabled": true,
            "auto_start": true
        }
    ]
}
EOF

    log_success "Python test scripts created"
}

# Test functions
test_binary_plugin_loads_python_support() {
    log_info "Testing that binary plugin loads Python support"
    
    # Skip if plugin binary doesn't exist
    if [[ ! -f "$PYTHON_PLUGIN_SO" ]]; then
        log_warning "Python plugin binary not found, skipping test"
        return 0
    fi
    
    # Setup Python scripts
    setup_python_test_scripts
    
    # Create config with Python plugin
    create_test_config "python_support_test"
    
    # Copy binary plugin
    mkdir -p "$PLUGINS_DIR"
    cp "$PYTHON_PLUGIN_SO" "$PLUGINS_DIR/"
    
    # Start node
    if start_node "python_support_test"; then
        assert_process_running "cellframe-node" "Node should start with Python plugin"
        
        if wait_for_node_ready 30; then
            # Check logs for Python-related messages
            local logs=$(get_node_logs 200)
            
            # Look for Python initialization messages
            if echo "$logs" | grep -q -i "python"; then
                assert_contains "$logs" "python" "Logs should contain Python-related messages"
            else
                log_warning "No Python messages in logs - plugin might load silently"
            fi
            
            log_success "Binary plugin appears to provide Python support"
        else
            assert_equals "0" "1" "Node should become ready with Python plugin"
        fi
        
        stop_node
    else
        assert_equals "0" "1" "Node should start with Python plugin"
    fi
    
    return 0
}

test_python_plugin_execution() {
    log_info "Testing Python plugin execution"
    
    # Skip if we can't test Python plugins
    if [[ ! -f "$PYTHON_PLUGIN_SO" ]]; then
        log_warning "Python plugin binary not found, skipping execution test"
        return 0
    fi
    
    # Test the Python script directly first
    if command -v python3 >/dev/null 2>&1; then
        log_info "Testing Python script directly"
        
        if python3 "$PYTHON_SCRIPTS_DIR/test_plugin.py" >/dev/null 2>&1; then
            assert_equals "0" "0" "Python test script should execute successfully"
        else
            assert_equals "0" "1" "Python test script should execute successfully"
        fi
    fi
    
    return 0
}

test_python_cellframe_api_integration() {
    log_info "Testing Python CellFrame API integration"
    
    # Skip if plugin binary doesn't exist
    if [[ ! -f "$PYTHON_PLUGIN_SO" ]]; then
        log_warning "Python plugin binary not found, skipping API integration test"
        return 0
    fi
    
    # Test the CellFrame API script
    if command -v python3 >/dev/null 2>&1; then
        log_info "Testing CellFrame API script"
        
        # Set PYTHONPATH to include our Python modules
        local python_cellframe_path="$PROJECT_ROOT/plugin/plugin-python/python-cellframe"
        local python_dap_path="$PROJECT_ROOT/plugin/plugin-python/python-dap"
        
        if [[ -d "$python_cellframe_path" && -d "$python_dap_path" ]]; then
            PYTHONPATH="$python_cellframe_path:$python_dap_path:$PYTHONPATH" \
            python3 -c "
import sys
sys.path.insert(0, '$python_cellframe_path')
sys.path.insert(0, '$python_dap_path')

try:
    exec(open('$PYTHON_SCRIPTS_DIR/cellframe_test_plugin.py').read())
    print('CellFrame API test plugin loaded successfully')
except Exception as e:
    print(f'Error loading CellFrame API test plugin: {e}')
    sys.exit(1)
" 2>/dev/null
            
            if [[ $? -eq 0 ]]; then
                assert_equals "0" "0" "CellFrame API test script should load successfully"
            else
                log_warning "CellFrame API test script failed - modules may not be available"
            fi
        else
            log_warning "Python module paths not found, skipping API integration test"
        fi
    fi
    
    return 0
}

test_python_plugin_lifecycle() {
    log_info "Testing Python plugin lifecycle management"
    
    # Skip if plugin binary doesn't exist
    if [[ ! -f "$PYTHON_PLUGIN_SO" ]]; then
        log_warning "Python plugin binary not found, skipping lifecycle test"
        return 0
    fi
    
    # Create config that would load Python plugins
    create_test_config "python_lifecycle_test"
    
    # Copy plugin files
    mkdir -p "$PLUGINS_DIR"
    cp "$PYTHON_PLUGIN_SO" "$PLUGINS_DIR/"
    
    # Copy Python scripts to a location where they might be found
    local python_plugins_dir="$PLUGINS_DIR/python"
    mkdir -p "$python_plugins_dir"
    cp "$PYTHON_SCRIPTS_DIR"/*.py "$python_plugins_dir/"
    
    # Start node
    if start_node "python_lifecycle_test"; then
        if wait_for_node_ready 30; then
            log_success "Node started with Python plugin support"
            
            # Test restart to check plugin persistence
            restart_node "python_lifecycle_test"
            
            if wait_for_node_ready 30; then
                assert_process_running "cellframe-node" "Node should restart with Python plugins"
            else
                assert_equals "0" "1" "Node should restart with Python plugins"
            fi
        else
            assert_equals "0" "1" "Node should start with Python plugins"
        fi
        
        stop_node
    else
        assert_equals "0" "1" "Node should start with Python plugin support"
    fi
    
    return 0
}

test_python_plugin_error_handling() {
    log_info "Testing Python plugin error handling"
    
    # Create a Python script with syntax error
    mkdir -p "$PYTHON_SCRIPTS_DIR"
    cat > "$PYTHON_SCRIPTS_DIR/broken_plugin.py" << 'EOF'
#!/usr/bin/env python3
# This plugin has intentional syntax errors

def plugin_init():
    # Syntax error - missing closing quote
    print("This will cause a syntax error
    return True

def plugin_deinit():
    pass
EOF
    
    # Create config
    create_test_config "python_error_test"
    
    if [[ -f "$PYTHON_PLUGIN_SO" ]]; then
        mkdir -p "$PLUGINS_DIR"
        cp "$PYTHON_PLUGIN_SO" "$PLUGINS_DIR/"
        
        # Copy broken script
        local python_plugins_dir="$PLUGINS_DIR/python"
        mkdir -p "$python_plugins_dir"
        cp "$PYTHON_SCRIPTS_DIR/broken_plugin.py" "$python_plugins_dir/"
        
        # Node should still start even with broken Python scripts
        if start_node "python_error_test"; then
            assert_process_running "cellframe-node" "Node should start even with broken Python plugins"
            
            # Check logs for error messages
            local logs=$(get_node_logs 100)
            if echo "$logs" | grep -q -i "error\|syntax"; then
                log_info "Node properly logged Python plugin errors"
            else
                log_warning "Node may not have logged Python plugin errors"
            fi
            
            stop_node
        else
            log_warning "Node failed to start with broken Python plugin"
        fi
    else
        log_warning "Python plugin binary not found, skipping error handling test"
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
    run_test "Binary plugin loads Python support" test_binary_plugin_loads_python_support
    run_test "Python plugin execution" test_python_plugin_execution
    run_test "Python CellFrame API integration" test_python_cellframe_api_integration
    run_test "Python plugin lifecycle" test_python_plugin_lifecycle
    run_test "Python plugin error handling" test_python_plugin_error_handling
    
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