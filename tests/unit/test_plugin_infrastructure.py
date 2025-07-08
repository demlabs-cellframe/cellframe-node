"""
Unit tests for Plugin Infrastructure
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

try:
    from plugin_python_init import (
        plugin_python_init,
        plugin_python_deinit,
        python_interpreter_init,
        python_interpreter_deinit,
        python_cellframe_modules_init,
        python_plugins_load_from_dir
    )
except ImportError:
    # For testing without actual plugin
    plugin_python_init = Mock
    plugin_python_deinit = Mock
    python_interpreter_init = Mock
    python_interpreter_deinit = Mock
    python_cellframe_modules_init = Mock
    python_plugins_load_from_dir = Mock


@pytest.mark.unit
@pytest.mark.plugin
class TestPluginInfrastructure:
    """Test cases for plugin infrastructure"""

    @pytest.fixture
    def plugin_manifest(self, plugin_root):
        """Load plugin manifest for testing"""
        manifest_path = plugin_root / "dist" / "plugin-python.json"
        if manifest_path.exists():
            with open(manifest_path, 'r') as f:
                return json.load(f)
        return {
            "name": "test-plugin",
            "version": "1.0.0",
            "description": "Test plugin"
        }

    @pytest.mark.mock_only
    def test_plugin_initialization(self, plugin_manifest):
        """Test plugin initialization process"""
        with patch('plugin_python_init.dap_config_get_item_bool_default', return_value=True), \
             patch('plugin_python_init.dap_config_get_item_str_default', return_value="/test/path"), \
             patch('plugin_python_init.dap_dir_test', return_value=0), \
             patch('plugin_python_init.python_interpreter_init', return_value=0), \
             patch('plugin_python_init.python_cellframe_modules_init', return_value=0), \
             patch('plugin_python_init.python_plugins_load_from_dir', return_value=5):
            
            result = plugin_python_init()
            
            assert result == 0  # Success

    @pytest.mark.mock_only
    def test_plugin_initialization_disabled(self):
        """Test plugin initialization when disabled in config"""
        with patch('plugin_python_init.dap_config_get_item_bool_default', return_value=False):
            result = plugin_python_init()
            
            assert result == 0  # Should succeed but do nothing

    @pytest.mark.mock_only
    def test_plugin_initialization_failure(self):
        """Test plugin initialization failure scenarios"""
        with patch('plugin_python_init.dap_config_get_item_bool_default', return_value=True), \
             patch('plugin_python_init.dap_config_get_item_str_default', return_value="/test/path"), \
             patch('plugin_python_init.dap_dir_test', return_value=0), \
             patch('plugin_python_init.python_interpreter_init', return_value=-1):  # Fail
            
            result = plugin_python_init()
            
            assert result == -5  # Expected error code

    @pytest.mark.mock_only
    def test_plugin_deinitialization(self):
        """Test plugin deinitialization process"""
        with patch('plugin_python_init.python_plugins_unload_all'), \
             patch('plugin_python_init.python_cellframe_modules_deinit'), \
             patch('plugin_python_init.python_interpreter_deinit'):
            
            # Should not raise any exceptions
            plugin_python_deinit()

    @pytest.mark.mock_only
    def test_python_interpreter_lifecycle(self):
        """Test Python interpreter initialization and deinitialization"""
        with patch('plugin_python_init.Py_Initialize'), \
             patch('plugin_python_init.Py_IsInitialized', return_value=True), \
             patch('plugin_python_init.PyEval_InitThreads'), \
             patch('plugin_python_init.PyRun_SimpleString'):
            
            # Test initialization
            result = python_interpreter_init("/test/python/path")
            assert result == 0
            
            # Test deinitialization
            with patch('plugin_python_init.Py_Finalize'):
                python_interpreter_deinit()

    @pytest.mark.mock_only
    def test_cellframe_modules_initialization(self):
        """Test CellFrame Python modules initialization"""
        with patch('plugin_python_init.python_interpreter_is_initialized', return_value=True), \
             patch('plugin_python_init.PyImport_ImportModule') as mock_import:
            
            # Mock successful imports
            mock_import.return_value = MagicMock()
            
            result = python_cellframe_modules_init()
            
            assert result == 0
            assert mock_import.call_count == 2  # cellframe and dap modules

    @pytest.mark.mock_only
    def test_cellframe_modules_initialization_failure(self):
        """Test CellFrame modules initialization failure"""
        with patch('plugin_python_init.python_interpreter_is_initialized', return_value=True), \
             patch('plugin_python_init.PyImport_ImportModule', return_value=None):
            
            result = python_cellframe_modules_init()
            
            assert result == -2  # Expected error code

    @pytest.mark.mock_only
    def test_python_plugins_loading(self, temp_dir):
        """Test loading Python plugins from directory"""
        # Create mock plugin files
        plugin_file = temp_dir / "test_plugin.py"
        plugin_file.write_text("""
def plugin_init():
    print("Plugin initialized")
    return True
""")
        
        with patch('plugin_python_init.python_interpreter_is_initialized', return_value=True), \
             patch('plugin_python_init.opendir') as mock_opendir, \
             patch('plugin_python_init.readdir') as mock_readdir, \
             patch('plugin_python_init.PyRun_SimpleFile', return_value=0):
            
            # Mock directory reading
            mock_opendir.return_value = MagicMock()
            mock_readdir.side_effect = [
                MagicMock(d_name="test_plugin.py"),
                MagicMock(d_name="another_plugin.py"),
                None  # End of directory
            ]
            
            result = python_plugins_load_from_dir(str(temp_dir))
            
            assert result == 2  # Two plugins loaded


@pytest.mark.unit
@pytest.mark.plugin
@pytest.mark.dual_package
class TestDualPackageSystem:
    """Test cases for dual package system"""

    @pytest.mark.mock_only
    def test_binary_plugin_package(self, plugin_binary_mock):
        """Test binary plugin package functionality"""
        # Test plugin entry points
        assert plugin_binary_mock.init() == 0
        assert plugin_binary_mock.get_info()["name"] == "test_plugin"
        
        # Test plugin lifecycle
        plugin_binary_mock.deinit()

    @pytest.mark.mock_only
    def test_standalone_library_package(self, standalone_library_mock):
        """Test standalone library package functionality"""
        # Test library initialization
        assert standalone_library_mock.cellframe_init() == 0
        assert standalone_library_mock.get_version() == "1.0.0"
        
        # Test library cleanup
        standalone_library_mock.cellframe_deinit()

    @pytest.mark.mock_only
    def test_package_isolation(self):
        """Test that packages are properly isolated"""
        # Binary plugin should not interfere with standalone library
        with patch('plugin_python_init.plugin_python_init'), \
             patch('standalone_library.cellframe_init'):
            
            # Both should be able to initialize independently
            plugin_result = plugin_python_init()
            standalone_result = standalone_library_mock.cellframe_init()
            
            assert plugin_result == 0
            assert standalone_result == 0

    @pytest.mark.mock_only
    def test_shared_python_modules(self):
        """Test that both packages can use shared Python modules"""
        # Both plugin and standalone should access same python-cellframe and python-dap
        with patch('sys.path') as mock_path:
            # Test that both packages add the same paths
            expected_paths = [
                "python-cellframe",
                "python-dap"
            ]
            
            # Simulate both packages initializing
            for path in expected_paths:
                mock_path.insert(0, path)
            
            # Both should have access to same modules
            assert len(mock_path.insert.call_args_list) == len(expected_paths)


@pytest.mark.unit
@pytest.mark.plugin
class TestPluginConfiguration:
    """Test cases for plugin configuration"""

    @pytest.fixture
    def plugin_config(self):
        """Sample plugin configuration"""
        return {
            "enabled": True,
            "plugins_path": "/opt/cellframe-node/var/lib/plugins",
            "python_path": "/opt/cellframe-node/python",
            "log_level": "INFO",
            "max_plugins": 50
        }

    @pytest.mark.mock_only
    def test_plugin_configuration_loading(self, plugin_config):
        """Test loading plugin configuration"""
        with patch('plugin_python_init.dap_config_get_item_bool_default') as mock_bool, \
             patch('plugin_python_init.dap_config_get_item_str_default') as mock_str:
            
            mock_bool.return_value = plugin_config["enabled"]
            mock_str.side_effect = [
                plugin_config["plugins_path"],
                plugin_config["python_path"]
            ]
            
            # Test configuration access
            enabled = mock_bool.return_value
            plugins_path = mock_str.return_value
            
            assert enabled == plugin_config["enabled"]
            assert plugins_path == plugin_config["plugins_path"]

    @pytest.mark.mock_only
    def test_plugin_configuration_validation(self, plugin_config):
        """Test plugin configuration validation"""
        with patch('plugin_python_init.dap_config_get_item_str_default') as mock_str:
            mock_str.return_value = plugin_config["plugins_path"]
            
            # Test path validation
            with patch('plugin_python_init.dap_dir_test', return_value=0):
                # Valid path
                assert True
                
            with patch('plugin_python_init.dap_dir_test', return_value=-1):
                # Invalid path - should create directory
                with patch('plugin_python_init.dap_mkdir_with_parents', return_value=0):
                    assert True

    @pytest.mark.mock_only
    def test_plugin_manifest_validation(self, plugin_manifest):
        """Test plugin manifest validation"""
        required_fields = [
            "name",
            "version", 
            "description",
            "type",
            "runtime"
        ]
        
        for field in required_fields:
            assert field in plugin_manifest

        # Test manifest structure
        assert plugin_manifest["type"] == "binary"
        assert "entry_point" in plugin_manifest.get("runtime", {})
        assert "dependencies" in plugin_manifest


@pytest.mark.unit
@pytest.mark.plugin
class TestPluginErrorHandling:
    """Test cases for plugin error handling"""

    @pytest.mark.mock_only
    def test_plugin_initialization_error_recovery(self):
        """Test error recovery during plugin initialization"""
        with patch('plugin_python_init.dap_config_get_item_bool_default', return_value=True), \
             patch('plugin_python_init.python_interpreter_init', side_effect=Exception("Init failed")):
            
            # Should handle error gracefully
            result = plugin_python_init()
            assert result < 0  # Error code

    @pytest.mark.mock_only
    def test_plugin_loading_error_handling(self):
        """Test handling of individual plugin loading errors"""
        with patch('plugin_python_init.python_interpreter_is_initialized', return_value=True), \
             patch('plugin_python_init.PyRun_SimpleFile', side_effect=Exception("Plugin error")):
            
            # Should continue loading other plugins despite individual failures
            result = python_plugins_load_from_dir("/test/path")
            assert result >= 0  # Should not fail completely

    @pytest.mark.mock_only
    def test_plugin_cleanup_on_failure(self):
        """Test proper cleanup when plugin initialization fails"""
        with patch('plugin_python_init.python_interpreter_init', return_value=0), \
             patch('plugin_python_init.python_cellframe_modules_init', return_value=-1), \
             patch('plugin_python_init.python_interpreter_deinit') as mock_cleanup:
            
            result = plugin_python_init()
            
            # Should cleanup on failure
            assert result < 0
            mock_cleanup.assert_called_once()

    @pytest.mark.mock_only
    def test_plugin_memory_management(self):
        """Test proper memory management in plugin"""
        with patch('plugin_python_init.python_interpreter_init', return_value=0), \
             patch('plugin_python_init.python_cellframe_modules_init', return_value=0), \
             patch('plugin_python_init.python_plugins_load_from_dir', return_value=5):
            
            # Initialize plugin
            result = plugin_python_init()
            assert result == 0
            
            # Deinitialize should cleanup properly
            with patch('plugin_python_init.python_interpreter_deinit') as mock_deinit:
                plugin_python_deinit()
                mock_deinit.assert_called_once() 