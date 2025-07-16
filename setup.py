#!/usr/bin/env python3
"""
🧬 Python DAP SDK Setup

Setup script for Python DAP SDK with integrated C library.
Builds python_cellframe_common.so and includes it in the package.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
from setuptools import setup, find_packages, Extension
from setuptools.command.build_ext import build_ext

class CMakeBuild(build_ext):
    """Custom build command that uses CMake to build C library."""
    
    def run(self):
        try:
            subprocess.check_call(['cmake', '--version'])
        except OSError:
            raise RuntimeError("CMake must be installed to build python-dap")
        
        for ext in self.extensions:
            self.build_cmake(ext)
    
    def build_cmake(self, ext):
        """Build using CMake."""
        source_dir = Path(__file__).parent.absolute()
        build_temp = Path(self.build_temp).absolute()
        build_temp.mkdir(parents=True, exist_ok=True)
        
        # CMake configuration
        cmake_args = [
            f'-DCMAKE_LIBRARY_OUTPUT_DIRECTORY={build_temp}',
            f'-DCMAKE_BUILD_TYPE=Release',
            '-DBUILD_PYTHON_CELLFRAME_COMMON=ON',
            '-DBUILD_TESTS=OFF'
        ]
        
        # Build arguments
        build_args = ['--config', 'Release', '--', '-j4']
        
        # Configure
        subprocess.check_call(
            ['cmake', str(source_dir)] + cmake_args,
            cwd=build_temp
        )
        
        # Build
        subprocess.check_call(
            ['cmake', '--build', '.'] + build_args,
            cwd=build_temp
        )
        
        # Copy library to lib directory
        lib_dir = source_dir / 'lib'
        lib_dir.mkdir(exist_ok=True)
        
        # Find built library
        for lib_file in build_temp.glob('**/python_cellframe_common.*'):
            if lib_file.suffix in ['.so', '.dylib', '.dll']:
                dest = lib_dir / f'python_cellframe_common{lib_file.suffix}'
                print(f"Copying {lib_file} to {dest}")
                shutil.copy2(lib_file, dest)
                break

# Dummy extension to trigger CMake build
cmake_extension = Extension(
    'python_cellframe_common',
    sources=[],  # CMake handles the sources
)

# Package configuration
setup(
    name="python-dap",
    version="1.0.0",
    description="Python SDK for DAP (Distributed Applications Platform)",
    long_description="""
Python DAP SDK provides direct Python bindings for DAP SDK functions,
offering low-level access to the DAP ecosystem with compiled C performance.

Features:
- Direct DAP SDK integration
- No fallback implementations
- Production-ready C library
- Comprehensive test suite
- CI/CD ready
    """,
    author="DemLabs",
    author_email="support@demlabs.net",
    url="https://gitlab.demlabs.net/dap/python-dap",
    
    # Package structure
    packages=find_packages(),
    package_data={
        'dap': ['../lib/python_cellframe_common.*'],
    },
    include_package_data=True,
    
    # C extension
    ext_modules=[cmake_extension],
    cmdclass={'build_ext': CMakeBuild},
    
    # Requirements
    python_requires='>=3.8',
    install_requires=[
        # No dependencies - standalone package
    ],
    extras_require={
        'dev': [
            'pytest>=6.0',
            'pytest-cov>=2.0',
            'pytest-mock>=3.0',
        ],
        'test': [
            'pytest>=6.0',
            'pytest-mock>=3.0',
        ]
    },
    
    # Classifiers
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: C',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Distributed Computing',
    ],
    
    # Entry points
    entry_points={
        'console_scripts': [
            'python-dap-test=dap.testing:main',
        ],
    },
    
    # Zip safe
    zip_safe=False,
) 