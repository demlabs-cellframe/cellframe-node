"""
Python Cellframe SDK - Modern Pythonic API for Cellframe Network
"""

from setuptools import setup, find_packages
import os

# Читаем README для long_description
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Читаем requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

# Версия SDK
VERSION = "2.0.0"

setup(
    name="cellframe",
    version=VERSION,
    
    # Metadata
    author="Demlabs",
    author_email="support@demlabs.net",
    description="Modern Pythonic API for Cellframe Network blockchain platform",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/demlabs-cellframe/cellframe-node",
    
    # Packages
    packages=find_packages(),
    include_package_data=True,
    
    # Requirements
    install_requires=read_requirements(),
    
    # Python version
    python_requires=">=3.8",
    
    # Classification
    classifiers=[
        "Development Status :: 5 - Production/Stable",
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
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Security :: Cryptography",
        "Topic :: Office/Business :: Financial",
    ],
    
    # Keywords
    keywords="cellframe blockchain cryptocurrency defi dap sdk python",
    
    # Project URLs
    project_urls={
        "Bug Reports": "https://github.com/demlabs-cellframe/cellframe-node/issues",
        "Source": "https://github.com/demlabs-cellframe/cellframe-node",
        "Documentation": "https://cellframe.net/docs",
        "Homepage": "https://cellframe.net",
        "Changelog": "https://github.com/demlabs-cellframe/cellframe-node/blob/master/CHANGELOG.md",
    },
    
    # Entry points
    entry_points={
        "console_scripts": [
            "cellframe=cellframe.cli:main",
            "cellframe-migrate=cellframe.migration:main",
        ],
    },
    
    # Package data
    package_data={
        "cellframe": [
            "py.typed",  # Type hints support
            "templates/*.json",
            "schemas/*.json",
        ],
    },
    
    # Extras
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=1.0.0",
            "pre-commit>=2.0.0",
        ],
        "async": [
            "aiohttp>=3.8.0",
            "asyncio>=3.4.0",
        ],
        "performance": [
            "psutil>=5.9.0",
            "memory-profiler>=0.60.0",
        ],
        "testing": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-mock>=3.10.0",
            "factory-boy>=3.2.0",
        ],
    },
    
    # Zip safe
    zip_safe=False,
    
    # Options
    options={
        "bdist_wheel": {
            "universal": False,
        },
    },
) 