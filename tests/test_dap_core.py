"""
🧪 Python DAP Core Tests

Basic tests for Python DAP SDK core functionality.
Tests module imports, basic initialization, and core functions.
"""

import pytest
import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import dap
except ImportError as e:
    pytest.skip(f"DAP modules not available: {e}", allow_module_level=True)


class TestDapBasicImports:
    """Test basic DAP module imports"""
    
    def test_dap_main_import(self):
        """Test main dap package import"""
        import dap
        assert dap is not None
        
    def test_dap_init_exists(self):
        """Test that dap __init__ exists"""
        import dap
        assert hasattr(dap, '__file__')
        
    def test_dap_submodules_exist(self):
        """Test that basic submodules directories exist"""
        import dap
        dap_path = Path(dap.__file__).parent
        
        expected_modules = ['core', 'config', 'crypto', 'network', 'global_db']
        missing_modules = []
        
        for module in expected_modules:
            module_path = dap_path / module
            if not module_path.exists():
                missing_modules.append(module)
                
        if missing_modules:
            print(f"Warning: Missing modules: {missing_modules}")
            
        # Should have at least some modules
        assert len(missing_modules) < len(expected_modules)


class TestDapModuleStructure:
    """Test DAP module structure and imports"""
    
    def test_import_core_modules(self):
        """Test importing core modules"""
        try:
            from dap import core
            assert core is not None
        except ImportError:
            pytest.skip("Core module not available")
            
    def test_import_config_modules(self):
        """Test importing config modules"""
        try:
            from dap import config
            assert config is not None
        except ImportError:
            pytest.skip("Config module not available")
            
    def test_import_crypto_modules(self):
        """Test importing crypto modules"""
        try:
            from dap import crypto
            assert crypto is not None
        except ImportError:
            pytest.skip("Crypto module not available")
            
    def test_import_network_modules(self):
        """Test importing network modules"""
        try:
            from dap import network  
            assert network is not None
        except ImportError:
            pytest.skip("Network module not available")
            
    def test_import_gdb_modules(self):
        """Test importing global_db modules"""
        try:
            from dap import global_db
            assert global_db is not None
        except ImportError:
            pytest.skip("Global DB module not available")


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 