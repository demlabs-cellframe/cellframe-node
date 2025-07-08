#!/usr/bin/env python3
"""
Python DAP SDK Setup

Direct Python bindings and wrappers over DAP SDK (dap-sdk) functions.
This package provides low-level access to dap_* functions while maintaining
pythonic interfaces.
"""

from setuptools import setup, find_packages
import os

def read_file(filename):
    """Read file content."""
    try:
        with open(os.path.join(os.path.dirname(__file__), filename), 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return ""

def get_version():
    """Get version from __init__.py."""
    try:
        with open('dap/__init__.py', 'r') as f:
            for line in f:
                if line.startswith('__version__'):
                    return line.split('=')[1].strip().strip('"\'')
    except FileNotFoundError:
        pass
    return "1.0.0"

setup(
    name="python-dap",
    version=get_version(),
    description="Python bindings for DAP SDK",
    long_description=read_file("README.md"),
    long_description_content_type="text/markdown",
    author="Demlabs Team",
    author_email="support@demlabs.net",
    url="https://gitlab.demlabs.net/dap/python-dap",
    project_urls={
        "Bug Reports": "https://gitlab.demlabs.net/dap/python-dap/-/issues",
        "Source": "https://gitlab.demlabs.net/dap/python-dap",
        "Documentation": "https://docs.demlabs.net/python-dap/",
    },
    
    packages=find_packages(),
    package_data={
        'dap': ['py.typed'],
    },
    
    python_requires=">=3.8",
    install_requires=[
        # Core dependencies will be added when we know the actual requirements
    ],
    
    extras_require={
        'dev': [
            'pytest>=6.0',
            'pytest-cov',
            'black',
            'isort',
            'mypy',
            'flake8',
        ],
        'docs': [
            'sphinx>=4.0',
            'sphinx-rtd-theme',
            'myst-parser',
        ],
    },
    
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Distributed Computing",
        "Topic :: Security :: Cryptography",
    ],
    
    keywords="dap sdk blockchain demlabs crypto network",
    
    zip_safe=False,
    include_package_data=True,
) 