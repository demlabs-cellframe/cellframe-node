#!/usr/bin/env python3
"""
🧬 Python DAP SDK Setup

Modern setup script for Python DAP SDK with pyproject.toml configuration.
Builds python_dap.so and includes it in the package.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
from setuptools import setup

def setup_native_library():
    """Set up the native library (.so file) for the package."""
    lib_dir = Path("lib")
    dap_dir = Path("dap")
        
    # Find the compiled library
    so_files = list(lib_dir.glob("python_dap*.so"))
    if not so_files:
        print("⚠️  No compiled .so file found in lib/")
        return
    
    source_so = so_files[0]
    target_so = dap_dir / "python_dap.so"
    
    # Copy to dap directory if needed
    if not target_so.exists() or source_so.stat().st_mtime > target_so.stat().st_mtime:
        print(f"📦 Copying {source_so} -> {target_so}")
        shutil.copy2(source_so, target_so)
        print("✅ Native library updated")
    else:
        print("✅ Using existing library")

if __name__ == "__main__":
    print("🧬 Setting up Python DAP SDK...")
    print("Setting up native library...")
    setup_native_library()
    
    # Use pyproject.toml configuration
    setup() 