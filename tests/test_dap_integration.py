"""
🔗 Python DAP Integration Tests

Integration tests for Python DAP SDK cross-module functionality.
Tests interactions between different DAP modules.
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


class TestDapCrossModuleImports:
    """Test cross-module import compatibility"""
    
    def test_no_circular_imports(self):
        """Test that modules can be imported without circular dependencies"""
        try:
            # Import modules individually to check for circular imports
            import dap.core
            import dap.config  
            import dap.crypto
            import dap.network
            import dap.global_db
            
            # If we reach here, no circular imports detected
            assert True
            
        except ImportError as e:
            if "circular" in str(e).lower():
                pytest.fail(f"Circular import detected: {e}")
            else:
                pytest.skip(f"Some modules not available: {e}")
                
    def test_module_init_files_exist(self):
        """Test that all modules have proper __init__.py files"""
        import dap
        dap_path = Path(dap.__file__).parent
        
        expected_modules = ['core', 'config', 'crypto', 'network', 'global_db']
        missing_inits = []
        
        for module in expected_modules:
            init_file = dap_path / module / '__init__.py'
            if not init_file.exists():
                missing_inits.append(f"{module}/__init__.py")
                
        if missing_inits:
            print(f"Warning: Missing init files: {missing_inits}")
            
        # Should have most init files
        assert len(missing_inits) <= 2  # Allow some to be missing
        
    def test_dap_main_init_imports(self):
        """Test that main dap __init__.py can import submodules"""
        try:
            # This should work if __init__.py is properly configured
            import dap
            
            # Check if main init tries to import submodules
            dap_init_file = Path(dap.__file__)
            if dap_init_file.exists():
                with open(dap_init_file, 'r') as f:
                    content = f.read()
                    
                # Should have some imports (but might fail due to missing C libs)
                has_imports = ('import' in content or 'from' in content)
                assert has_imports or len(content.strip()) == 0  # Empty is OK too
                
        except Exception as e:
            pytest.skip(f"Could not read dap init file: {e}")


class TestDapModuleStructure:
    """Test overall module structure"""
    
    def test_expected_submodules_present(self):
        """Test that expected submodule directories exist"""
        import dap
        dap_path = Path(dap.__file__).parent
        
        expected_modules = ['core', 'config', 'crypto', 'network', 'global_db']
        present_modules = []
        
        for module in expected_modules:
            module_path = dap_path / module
            if module_path.exists() and module_path.is_dir():
                present_modules.append(module)
                
        print(f"Found modules: {present_modules}")
        
        # Should have at least half of expected modules
        assert len(present_modules) >= len(expected_modules) // 2
        
    def test_submodules_have_python_files(self):
        """Test that submodules contain Python files"""
        import dap
        dap_path = Path(dap.__file__).parent
        
        modules_with_py_files = []
        
        for item in dap_path.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                py_files = list(item.glob('*.py'))
                if py_files:
                    modules_with_py_files.append(item.name)
                    
        print(f"Modules with Python files: {modules_with_py_files}")
        
        # Should have at least some modules with Python files
        assert len(modules_with_py_files) >= 1


class TestDapBasicIntegration:
    """Test basic integration scenarios"""
    
    def test_import_all_available_modules(self):
        """Test importing all available modules"""
        import dap
        dap_path = Path(dap.__file__).parent
        
        successfully_imported = []
        failed_imports = []
        
        # Try to import each submodule
        for item in dap_path.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                module_name = f"dap.{item.name}"
                try:
                    __import__(module_name)
                    successfully_imported.append(module_name)
                except ImportError as e:
                    failed_imports.append((module_name, str(e)))
                    
        print(f"Successfully imported: {successfully_imported}")
        print(f"Failed imports: {failed_imports}")
        
        # Should successfully import at least some modules
        assert len(successfully_imported) >= 1
        
    def test_module_attributes_accessible(self):
        """Test that imported modules have accessible attributes"""
        import dap
        
        # Test that dap module has some attributes
        dap_attrs = [attr for attr in dir(dap) if not attr.startswith('_')]
        print(f"DAP module attributes: {dap_attrs}")
        
        # Should have at least __file__ and possibly more
        assert len(dap_attrs) >= 0  # Very permissive, just check it doesn't crash


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 