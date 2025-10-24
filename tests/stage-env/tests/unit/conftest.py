"""Pytest configuration and fixtures for unit tests."""

import pytest
from pathlib import Path


@pytest.fixture
def fixtures_dir():
    """Path to fixtures directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def cli_help_main(fixtures_dir):
    """Main CLI help output."""
    return (fixtures_dir / "cli_help_main.txt").read_text()


@pytest.fixture
def cli_help_token_decl(fixtures_dir):
    """token_decl command help output."""
    return (fixtures_dir / "cli_help_token_decl.txt").read_text()


@pytest.fixture
def sample_yaml_error():
    """Sample YAML error response from CLI."""
    return """
        errors: 
            
                code: 102
                message: token_decl requires parameter '-net'
"""


@pytest.fixture
def sample_yaml_success():
    """Sample YAML success response with hash."""
    return """
        hash: 0x1234567890ABCDEF1234567890ABCDEF1234567890ABCDEF1234567890ABCDEF
        status: success
"""

