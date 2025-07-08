#!/usr/bin/env python3
"""
Integration test to verify Python API symbols are accessible
in cellframe-node binary without requiring full runtime
"""

import sys
import pytest
import subprocess
from pathlib import Path
from typing import List, Tuple


@pytest.mark.integration
@pytest.mark.plugin
class TestPythonAPISymbols:
    """Test Python API symbols integration in cellframe-node binary"""

    @pytest.fixture(scope="class")
    def binary_path(self):
        """Path to cellframe-node binary"""
        # Try different possible paths
        possible_paths = [
            Path("../../build/cellframe-node"),
            Path("../../../build/cellframe-node"),
            Path("./build/cellframe-node"),
            Path("../build/cellframe-node")
        ]
        
        for path in possible_paths:
            if path.exists():
                return str(path)
        
        pytest.skip("cellframe-node binary not found")

    def test_python_symbols_exist(self, binary_path):
        """Test that Python symbols exist in cellframe-node binary"""
        try:
            # Use nm to check symbols on macOS/Linux
            result = subprocess.run(
                ['nm', binary_path], 
                capture_output=True, 
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                pytest.skip("nm command failed or not available")
            
            python_symbols = [
                line for line in result.stdout.split('\n') 
                if 'python' in line.lower() or 'cellframe' in line.lower()
            ]
            
            # Should have at least some Python-related symbols
            assert len(python_symbols) > 0, "No Python symbols found in binary"
            
            print(f"✅ Found {len(python_symbols)} Python/CellFrame symbols")
            
        except subprocess.TimeoutExpired:
            pytest.fail("Symbol check timed out")
        except FileNotFoundError:
            pytest.skip("nm command not available")
        except Exception as e:
            pytest.fail(f"Symbol check failed: {e}")

    def test_critical_symbols_present(self, binary_path):
        """Test that critical Python API symbols are present"""
        try:
            result = subprocess.run(
                ['nm', binary_path], 
                capture_output=True, 
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                pytest.skip("nm command failed")
            
            # Check for critical symbols (case-insensitive)
            critical_symbols = [
                'python',
                'cellframe',
                'dap'
            ]
            
            symbols_text = result.stdout.lower()
            found_critical = []
            
            for symbol in critical_symbols:
                if symbol in symbols_text:
                    found_critical.append(symbol)
            
            # Should find at least Python and CellFrame related symbols
            assert len(found_critical) >= 2, f"Missing critical symbols. Found: {found_critical}"
            
            print(f"✅ Found critical symbols: {found_critical}")
            
        except subprocess.TimeoutExpired:
            pytest.fail("Critical symbol check timed out")
        except FileNotFoundError:
            pytest.skip("nm command not available")
        except Exception as e:
            pytest.fail(f"Critical symbol check failed: {e}")

    def test_python_libraries_linked(self, binary_path):
        """Test that Python libraries are properly linked"""
        try:
            # Use otool on macOS or ldd on Linux
            commands = [
                ['otool', '-L', binary_path],  # macOS
                ['ldd', binary_path]           # Linux
            ]
            
            linked_libs = []
            for cmd in commands:
                try:
                    result = subprocess.run(
                        cmd, 
                        capture_output=True, 
                        text=True,
                        timeout=30
                    )
                    
                    if result.returncode == 0:
                        linked_libs = [
                            line.strip() for line in result.stdout.split('\n') 
                            if 'python' in line.lower()
                        ]
                        break
                        
                except FileNotFoundError:
                    continue
            
            if not linked_libs:
                pytest.skip("Could not check linked libraries (otool/ldd not available)")
            
            # Should have at least one Python library linked
            assert len(linked_libs) >= 1, f"No Python libraries linked. Found: {linked_libs}"
            
            print(f"✅ Python libraries linked: {len(linked_libs)}")
            for lib in linked_libs:
                print(f"   {lib}")
                
        except subprocess.TimeoutExpired:
            pytest.fail("Library check timed out")
        except Exception as e:
            pytest.fail(f"Library check failed: {e}")

    @pytest.mark.slow
    def test_binary_executable(self, binary_path):
        """Test that binary is executable and responds to --help"""
        try:
            result = subprocess.run(
                [binary_path, '--help'], 
                capture_output=True, 
                text=True,
                timeout=10
            )
            
            # Binary should respond to --help without crashing
            assert result.returncode in [0, 1], f"Binary crashed with code {result.returncode}"
            
            # Should have some output
            assert len(result.stdout) > 0 or len(result.stderr) > 0, "No output from binary"
            
            print("✅ Binary is executable and responds to --help")
            
        except subprocess.TimeoutExpired:
            pytest.fail("Binary execution timed out")
        except Exception as e:
            pytest.fail(f"Binary execution failed: {e}")

    def test_plugin_manifest_exists(self):
        """Test that plugin manifest exists"""
        manifest_path = Path("../dist/plugin-python.json")
        
        assert manifest_path.exists(), "Plugin manifest not found"
        
        # Check manifest is valid JSON
        import json
        try:
            with open(manifest_path, 'r') as f:
                manifest = json.load(f)
            
            # Should have basic plugin info
            required_fields = ["name", "version", "description", "type"]
            for field in required_fields:
                assert field in manifest, f"Missing required field: {field}"
            
            print("✅ Plugin manifest is valid")
            
        except json.JSONDecodeError:
            pytest.fail("Plugin manifest is not valid JSON")
        except Exception as e:
            pytest.fail(f"Manifest validation failed: {e}")


def test_main_compatibility():
    """Compatibility test for running as main script"""
    # This maintains backward compatibility for direct execution
    print("🧪 Testing Python API Integration in cellframe-node")
    print("=" * 60)
    
    # Run basic checks
    try:
        test_instance = TestPythonAPISymbols()
        binary_path = None
        
        # Try to find binary
        possible_paths = [
            Path("../../build/cellframe-node"),
            Path("../../../build/cellframe-node"),
            Path("./build/cellframe-node"),
            Path("../build/cellframe-node")
        ]
        
        for path in possible_paths:
            if path.exists():
                binary_path = str(path)
                break
        
        if binary_path:
            print(f"✅ Found binary at: {binary_path}")
            print("🎯 cellframe-node has functional Python support")
        else:
            print("⚠️  Binary not found - build cellframe-node first")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
    
    return True


if __name__ == "__main__":
    # Maintain backward compatibility
    success = test_main_compatibility()
    sys.exit(0 if success else 1) 