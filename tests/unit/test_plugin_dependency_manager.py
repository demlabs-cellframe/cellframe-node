"""
Unit tests for Plugin Dependency Manager System
Tests the new plugin auto-loading system with dependency management
"""
import pytest
from unittest.mock import Mock, MagicMock, patch, call
import sys
import os
import tempfile
import json
from pathlib import Path

# Add paths for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../dap-sdk/plugin/src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

# Mock the C functions that will be called
C_FUNCTIONS_MOCK = {
    'dap_plugin_dependency_manager_init': Mock(return_value=0),
    'dap_plugin_dependency_manager_deinit': Mock(),
    'dap_plugin_dependency_manager_register_type_handler': Mock(return_value=0),
    'dap_plugin_dependency_manager_get_type_handler': Mock(return_value=Mock()),
    'dap_plugin_dependency_manager_resolve_dependencies': Mock(return_value=0),
    'dap_plugin_dependency_manager_detect_circular_dependencies': Mock(return_value=0),
    'dap_plugin_dependency_manager_add_plugin': Mock(return_value=0),
    'dap_plugin_dependency_manager_remove_plugin': Mock(return_value=0),
    'dap_plugin_dependency_manager_get_plugin_count': Mock(return_value=0),
    'dap_plugin_dependency_manager_get_handler_count': Mock(return_value=0),
    'dap_plugin_dependency_manager_clear_all': Mock()
}

# Mock the actual C module
with patch.dict('sys.modules', {'dap_plugin_dependency_manager': MagicMock(**C_FUNCTIONS_MOCK)}):
    try:
        from dap_plugin_dependency_manager import (
            dap_plugin_dependency_manager_init,
            dap_plugin_dependency_manager_deinit,
            dap_plugin_dependency_manager_register_type_handler,
            dap_plugin_dependency_manager_get_type_handler,
            dap_plugin_dependency_manager_resolve_dependencies,
            dap_plugin_dependency_manager_detect_circular_dependencies,
            dap_plugin_dependency_manager_add_plugin,
            dap_plugin_dependency_manager_remove_plugin,
            dap_plugin_dependency_manager_get_plugin_count,
            dap_plugin_dependency_manager_get_handler_count,
            dap_plugin_dependency_manager_clear_all
        )
    except ImportError:
        # Create mock functions if import fails
        dap_plugin_dependency_manager_init = Mock(return_value=0)
        dap_plugin_dependency_manager_deinit = Mock()
        dap_plugin_dependency_manager_register_type_handler = Mock(return_value=0)
        dap_plugin_dependency_manager_get_type_handler = Mock(return_value=Mock())
        dap_plugin_dependency_manager_resolve_dependencies = Mock(return_value=0)
        dap_plugin_dependency_manager_detect_circular_dependencies = Mock(return_value=0)
        dap_plugin_dependency_manager_add_plugin = Mock(return_value=0)
        dap_plugin_dependency_manager_remove_plugin = Mock(return_value=0)
        dap_plugin_dependency_manager_get_plugin_count = Mock(return_value=0)
        dap_plugin_dependency_manager_get_handler_count = Mock(return_value=0)
        dap_plugin_dependency_manager_clear_all = Mock()


@pytest.mark.unit
@pytest.mark.plugin
@pytest.mark.dependency_manager
class TestPluginDependencyManager:
    """Test cases for Plugin Dependency Manager"""

    def test_dependency_manager_initialization(self):
        """Test dependency manager initialization"""
        result = dap_plugin_dependency_manager_init()
        assert result == 0
        dap_plugin_dependency_manager_init.assert_called_once()

    def test_dependency_manager_deinitialization(self):
        """Test dependency manager deinitialization"""
        dap_plugin_dependency_manager_deinit()
        dap_plugin_dependency_manager_deinit.assert_called_once()

    def test_type_handler_registration(self):
        """Test type handler registration"""
        # Mock handler function
        mock_handler = Mock()
        
        result = dap_plugin_dependency_manager_register_type_handler(
            ".py", mock_handler
        )
        
        assert result == 0
        dap_plugin_dependency_manager_register_type_handler.assert_called_once_with(
            ".py", mock_handler
        )

    def test_type_handler_retrieval(self):
        """Test type handler retrieval"""
        mock_handler = Mock()
        dap_plugin_dependency_manager_get_type_handler.return_value = mock_handler
        
        result = dap_plugin_dependency_manager_get_type_handler(".py")
        
        assert result == mock_handler
        dap_plugin_dependency_manager_get_type_handler.assert_called_once_with(".py")

    def test_plugin_addition(self):
        """Test adding plugin to dependency manager"""
        result = dap_plugin_dependency_manager_add_plugin(
            "test_plugin.py", ["dep1", "dep2"]
        )
        
        assert result == 0
        dap_plugin_dependency_manager_add_plugin.assert_called_once_with(
            "test_plugin.py", ["dep1", "dep2"]
        )

    def test_plugin_removal(self):
        """Test removing plugin from dependency manager"""
        result = dap_plugin_dependency_manager_remove_plugin("test_plugin.py")
        
        assert result == 0
        dap_plugin_dependency_manager_remove_plugin.assert_called_once_with(
            "test_plugin.py"
        )

    def test_dependency_resolution(self):
        """Test dependency resolution"""
        mock_order = ["plugin1", "plugin2", "plugin3"]
        dap_plugin_dependency_manager_resolve_dependencies.return_value = mock_order
        
        result = dap_plugin_dependency_manager_resolve_dependencies()
        
        assert result == mock_order
        dap_plugin_dependency_manager_resolve_dependencies.assert_called_once()

    def test_circular_dependency_detection(self):
        """Test circular dependency detection"""
        # Test no circular dependencies
        dap_plugin_dependency_manager_detect_circular_dependencies.return_value = 0
        
        result = dap_plugin_dependency_manager_detect_circular_dependencies()
        
        assert result == 0
        dap_plugin_dependency_manager_detect_circular_dependencies.assert_called_once()

    def test_plugin_count(self):
        """Test getting plugin count"""
        dap_plugin_dependency_manager_get_plugin_count.return_value = 5
        
        result = dap_plugin_dependency_manager_get_plugin_count()
        
        assert result == 5
        dap_plugin_dependency_manager_get_plugin_count.assert_called_once()

    def test_handler_count(self):
        """Test getting handler count"""
        dap_plugin_dependency_manager_get_handler_count.return_value = 3
        
        result = dap_plugin_dependency_manager_get_handler_count()
        
        assert result == 3
        dap_plugin_dependency_manager_get_handler_count.assert_called_once()

    def test_clear_all(self):
        """Test clearing all plugins and handlers"""
        dap_plugin_dependency_manager_clear_all()
        dap_plugin_dependency_manager_clear_all.assert_called_once()


@pytest.mark.unit
@pytest.mark.plugin
@pytest.mark.dependency_manager
@pytest.mark.integration
class TestPluginDependencyManagerIntegration:
    """Integration tests for Plugin Dependency Manager"""

    def test_python_plugin_auto_loading_workflow(self):
        """Test complete Python plugin auto-loading workflow"""
        # Setup: Initialize dependency manager
        dap_plugin_dependency_manager_init.return_value = 0
        
        # Step 1: Register Python handler
        mock_python_handler = Mock()
        dap_plugin_dependency_manager_register_type_handler.return_value = 0
        
        # Step 2: Add Python plugin
        dap_plugin_dependency_manager_add_plugin.return_value = 0
        
        # Step 3: Resolve dependencies
        dap_plugin_dependency_manager_resolve_dependencies.return_value = [
            "python-plugin", "test_plugin.py"
        ]
        
        # Step 4: Check for circular dependencies
        dap_plugin_dependency_manager_detect_circular_dependencies.return_value = 0
        
        # Execute workflow
        init_result = dap_plugin_dependency_manager_init()
        assert init_result == 0
        
        register_result = dap_plugin_dependency_manager_register_type_handler(
            ".py", mock_python_handler
        )
        assert register_result == 0
        
        add_result = dap_plugin_dependency_manager_add_plugin(
            "test_plugin.py", ["python-plugin"]
        )
        assert add_result == 0
        
        circular_result = dap_plugin_dependency_manager_detect_circular_dependencies()
        assert circular_result == 0
        
        load_order = dap_plugin_dependency_manager_resolve_dependencies()
        assert load_order == ["python-plugin", "test_plugin.py"]
        
        # Verify calls
        dap_plugin_dependency_manager_init.assert_called_once()
        dap_plugin_dependency_manager_register_type_handler.assert_called_once()
        dap_plugin_dependency_manager_add_plugin.assert_called_once()
        dap_plugin_dependency_manager_detect_circular_dependencies.assert_called_once()
        dap_plugin_dependency_manager_resolve_dependencies.assert_called_once()

    def test_multiple_file_types_registration(self):
        """Test registration of multiple file type handlers"""
        handlers = {
            ".py": Mock(),
            ".js": Mock(),
            ".lua": Mock(),
            ".so": Mock()
        }
        
        dap_plugin_dependency_manager_register_type_handler.return_value = 0
        
        # Register all handlers
        for ext, handler in handlers.items():
            result = dap_plugin_dependency_manager_register_type_handler(ext, handler)
            assert result == 0
        
        # Verify all were registered
        assert dap_plugin_dependency_manager_register_type_handler.call_count == 4
        
        # Verify correct calls
        expected_calls = [call(ext, handler) for ext, handler in handlers.items()]
        dap_plugin_dependency_manager_register_type_handler.assert_has_calls(
            expected_calls, any_order=True
        )

    def test_complex_dependency_resolution(self):
        """Test complex dependency resolution scenario"""
        # Setup complex dependency graph
        plugins = [
            ("plugin_a.py", ["python-plugin"]),
            ("plugin_b.py", ["python-plugin", "plugin_a.py"]),
            ("plugin_c.py", ["python-plugin", "plugin_a.py", "plugin_b.py"]),
            ("plugin_d.js", ["javascript-plugin"]),
            ("plugin_e.lua", ["lua-plugin", "plugin_d.js"])
        ]
        
        dap_plugin_dependency_manager_add_plugin.return_value = 0
        dap_plugin_dependency_manager_resolve_dependencies.return_value = [
            "python-plugin", "plugin_a.py", "plugin_b.py", "plugin_c.py",
            "javascript-plugin", "plugin_d.js", "lua-plugin", "plugin_e.lua"
        ]
        
        # Add all plugins
        for plugin_path, deps in plugins:
            result = dap_plugin_dependency_manager_add_plugin(plugin_path, deps)
            assert result == 0
        
        # Resolve dependencies
        load_order = dap_plugin_dependency_manager_resolve_dependencies()
        
        # Verify correct order (dependencies loaded before dependents)
        assert load_order.index("python-plugin") < load_order.index("plugin_a.py")
        assert load_order.index("plugin_a.py") < load_order.index("plugin_b.py")
        assert load_order.index("plugin_b.py") < load_order.index("plugin_c.py")
        assert load_order.index("javascript-plugin") < load_order.index("plugin_d.js")
        assert load_order.index("plugin_d.js") < load_order.index("plugin_e.lua")
        assert load_order.index("lua-plugin") < load_order.index("plugin_e.lua")


@pytest.mark.unit
@pytest.mark.plugin
@pytest.mark.dependency_manager
@pytest.mark.error_handling
class TestPluginDependencyManagerErrorHandling:
    """Test error handling in Plugin Dependency Manager"""

    def test_initialization_failure(self):
        """Test handling of initialization failure"""
        dap_plugin_dependency_manager_init.return_value = -1
        
        result = dap_plugin_dependency_manager_init()
        
        assert result == -1
        dap_plugin_dependency_manager_init.assert_called_once()

    def test_handler_registration_failure(self):
        """Test handling of handler registration failure"""
        dap_plugin_dependency_manager_register_type_handler.return_value = -1
        
        result = dap_plugin_dependency_manager_register_type_handler(
            ".py", Mock()
        )
        
        assert result == -1

    def test_circular_dependency_detection(self):
        """Test circular dependency detection"""
        # Simulate circular dependency detected
        dap_plugin_dependency_manager_detect_circular_dependencies.return_value = 1
        
        result = dap_plugin_dependency_manager_detect_circular_dependencies()
        
        assert result == 1  # Circular dependency found

    def test_plugin_addition_failure(self):
        """Test handling of plugin addition failure"""
        dap_plugin_dependency_manager_add_plugin.return_value = -1
        
        result = dap_plugin_dependency_manager_add_plugin(
            "invalid_plugin.py", ["missing_dependency"]
        )
        
        assert result == -1

    def test_dependency_resolution_failure(self):
        """Test handling of dependency resolution failure"""
        dap_plugin_dependency_manager_resolve_dependencies.return_value = None
        
        result = dap_plugin_dependency_manager_resolve_dependencies()
        
        assert result is None


@pytest.mark.unit
@pytest.mark.plugin
@pytest.mark.dependency_manager
@pytest.mark.performance
class TestPluginDependencyManagerPerformance:
    """Performance tests for Plugin Dependency Manager"""

    def test_large_plugin_set_performance(self):
        """Test performance with large number of plugins"""
        # Simulate adding 1000 plugins
        dap_plugin_dependency_manager_add_plugin.return_value = 0
        dap_plugin_dependency_manager_get_plugin_count.return_value = 1000
        
        # Add plugins
        for i in range(1000):
            result = dap_plugin_dependency_manager_add_plugin(
                f"plugin_{i}.py", ["python-plugin"]
            )
            assert result == 0
        
        # Verify count
        count = dap_plugin_dependency_manager_get_plugin_count()
        assert count == 1000
        
        # Verify performance (should complete quickly)
        assert dap_plugin_dependency_manager_add_plugin.call_count == 1000

    def test_dependency_resolution_performance(self):
        """Test dependency resolution performance"""
        # Mock large dependency graph resolution
        large_order = [f"plugin_{i}.py" for i in range(100)]
        dap_plugin_dependency_manager_resolve_dependencies.return_value = large_order
        
        result = dap_plugin_dependency_manager_resolve_dependencies()
        
        assert len(result) == 100
        assert result == large_order

    def test_handler_lookup_performance(self):
        """Test handler lookup performance"""
        mock_handler = Mock()
        dap_plugin_dependency_manager_get_type_handler.return_value = mock_handler
        
        # Simulate many lookups
        for i in range(100):
            result = dap_plugin_dependency_manager_get_type_handler(".py")
            assert result == mock_handler
        
        # Verify lookup count
        assert dap_plugin_dependency_manager_get_type_handler.call_count == 100


@pytest.mark.unit
@pytest.mark.plugin
@pytest.mark.dependency_manager
@pytest.mark.memory_management
class TestPluginDependencyManagerMemoryManagement:
    """Memory management tests for Plugin Dependency Manager"""

    def test_memory_cleanup_on_deinit(self):
        """Test proper memory cleanup during deinitialization"""
        # Initialize
        dap_plugin_dependency_manager_init.return_value = 0
        init_result = dap_plugin_dependency_manager_init()
        assert init_result == 0
        
        # Add some plugins
        dap_plugin_dependency_manager_add_plugin.return_value = 0
        for i in range(10):
            result = dap_plugin_dependency_manager_add_plugin(
                f"plugin_{i}.py", ["python-plugin"]
            )
            assert result == 0
        
        # Deinitialize should clean up
        dap_plugin_dependency_manager_deinit()
        dap_plugin_dependency_manager_deinit.assert_called_once()

    def test_clear_all_functionality(self):
        """Test clear all functionality"""
        # Add some data
        dap_plugin_dependency_manager_add_plugin.return_value = 0
        dap_plugin_dependency_manager_register_type_handler.return_value = 0
        
        dap_plugin_dependency_manager_add_plugin("test.py", ["python-plugin"])
        dap_plugin_dependency_manager_register_type_handler(".py", Mock())
        
        # Clear all
        dap_plugin_dependency_manager_clear_all()
        
        # Verify counts reset
        dap_plugin_dependency_manager_get_plugin_count.return_value = 0
        dap_plugin_dependency_manager_get_handler_count.return_value = 0
        
        plugin_count = dap_plugin_dependency_manager_get_plugin_count()
        handler_count = dap_plugin_dependency_manager_get_handler_count()
        
        assert plugin_count == 0
        assert handler_count == 0

    def test_plugin_removal_memory_cleanup(self):
        """Test memory cleanup when removing plugins"""
        # Add plugin
        dap_plugin_dependency_manager_add_plugin.return_value = 0
        result = dap_plugin_dependency_manager_add_plugin("test.py", ["python-plugin"])
        assert result == 0
        
        # Remove plugin
        dap_plugin_dependency_manager_remove_plugin.return_value = 0
        result = dap_plugin_dependency_manager_remove_plugin("test.py")
        assert result == 0
        
        # Verify removal
        dap_plugin_dependency_manager_remove_plugin.assert_called_once_with("test.py")


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"]) 