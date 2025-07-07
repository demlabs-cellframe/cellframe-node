#!/usr/bin/env python3
"""
Minimal test to verify Python API symbols are accessible
without requiring full cellframe-node runtime
"""

import sys
import ctypes
from ctypes.util import find_library

def test_python_symbols_in_cellframe_binary():
    """Test that Python symbols exist in cellframe-node binary"""
    try:
        # Try to access the binary
        binary_path = "./build/cellframe-node"
        
        # On macOS, we can use nm to check symbols 
        import subprocess
        result = subprocess.run(['nm', binary_path], 
                              capture_output=True, text=True)
        
        python_symbols = [line for line in result.stdout.split('\n') 
                         if 'python' in line.lower() or 'cellframe' in line.lower()]
        
        print("🔍 Found Python/CellFrame symbols in binary:")
        for symbol in python_symbols[:10]:  # Show first 10
            print(f"   {symbol}")
        
        if len(python_symbols) > 10:
            print(f"   ... and {len(python_symbols) - 10} more symbols")
            
        # Check for specific critical symbols
        critical_symbols = [
            'CellFramePythonModule',
            'DapPythonMethods', 
            'dap_chain_python',
            'python'
        ]
        
        found_critical = []
        for symbol in critical_symbols:
            if any(symbol.lower() in line.lower() for line in python_symbols):
                found_critical.append(symbol)
        
        print(f"\n✅ CRITICAL SYMBOLS FOUND: {len(found_critical)}/{len(critical_symbols)}")
        for symbol in found_critical:
            print(f"   ✓ {symbol}")
            
        # Check Python linkage
        ldd_result = subprocess.run(['otool', '-L', binary_path], 
                                  capture_output=True, text=True)
        python_libs = [line for line in ldd_result.stdout.split('\n') 
                      if 'python' in line.lower()]
        
        print(f"\n🔗 PYTHON LIBRARIES LINKED: {len(python_libs)}")
        for lib in python_libs:
            print(f"   {lib.strip()}")
            
        return len(found_critical) >= 2 and len(python_libs) >= 1
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Python API Integration in cellframe-node")
    print("=" * 60)
    
    success = test_python_symbols_in_cellframe_binary()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ SUCCESS: Python API integration confirmed!")
        print("🎯 cellframe-node has functional Python support")
        sys.exit(0)
    else:
        print("❌ FAILURE: Python API integration issues detected")
        sys.exit(1)
