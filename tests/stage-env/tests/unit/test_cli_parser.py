"""Unit tests for CLI parser."""

import pytest
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from utils.cli_parser import CLICommandParser


class TestCLICommandParser:
    """Test CLI command parser functionality."""
    
    def test_extract_commands_from_main_help(self, cli_help_main):
        """Test extracting command list from main help output."""
        parser = CLICommandParser()
        commands = parser._extract_commands(cli_help_main)
        
        assert len(commands) > 0, "Should extract commands"
        assert "token_decl" in commands
        assert "token_emit" in commands
        assert "wallet" in commands
        assert "tx_create" in commands
        
        # Filter out help keywords
        assert "help" not in commands
        assert "exit" not in commands
        assert "version" not in commands
    
    def test_extract_options_from_command_help(self, cli_help_token_decl):
        """Test extracting options from command-specific help."""
        parser = CLICommandParser()
        options = parser._extract_options(cli_help_token_decl)
        
        assert len(options) > 0, "Should extract options"
        assert "net" in options
        assert "chain" in options
        assert "token" in options
        assert "total_supply" in options
        assert "signs_total" in options
        assert "certs" in options
        assert "flags" in options
        assert "decimals" in options
    
    def test_apply_cli_defaults_adds_missing_option(self):
        """Test that defaults are added to commands missing options."""
        parser = CLICommandParser()
        
        # Manually set commands for testing
        parser.commands = {
            "token_decl": {"net", "token", "total_supply", "certs"}
        }
        parser._parsed = True
        
        cmd = "token_decl -token TEST -total_supply 1000000"
        defaults = {"net": "stagenet"}
        
        result = parser.apply_cli_defaults(cmd, defaults)
        
        assert "-net stagenet" in result
        assert result.startswith("token_decl")
    
    def test_apply_cli_defaults_doesnt_duplicate(self):
        """Test that existing options are not duplicated."""
        parser = CLICommandParser()
        
        parser.commands = {
            "token_decl": {"net", "token"}
        }
        parser._parsed = True
        
        cmd = "token_decl -net stagenet -token TEST"
        defaults = {"net": "mainnet"}  # Try to override
        
        result = parser.apply_cli_defaults(cmd, defaults)
        
        # Should NOT add -net again
        assert result == cmd
        assert result.count("-net") == 1
    
    def test_apply_cli_defaults_ignores_unsupported_options(self):
        """Test that unsupported options are ignored."""
        parser = CLICommandParser()
        
        parser.commands = {
            "token_decl": {"net", "token"}  # Only net and token supported
        }
        parser._parsed = True
        
        cmd = "token_decl -token TEST"
        defaults = {
            "net": "stagenet",
            "unsupported_option": "value"  # Not in command options
        }
        
        result = parser.apply_cli_defaults(cmd, defaults)
        
        assert "-net stagenet" in result
        assert "-unsupported_option" not in result
    
    def test_load_from_empty_cache_returns_false(self, tmp_path):
        """Test that empty cache is rejected."""
        import json
        
        cache_file = tmp_path / "empty_cache.json"
        cache_file.write_text("{}")
        
        parser = CLICommandParser(cache_file=cache_file)
        result = parser.load_from_cache()
        
        assert result is False, "Empty cache should be rejected"
        assert parser._parsed is False
    
    def test_load_from_valid_cache_returns_true(self, tmp_path):
        """Test that valid cache is loaded."""
        import json
        
        cache_file = tmp_path / "valid_cache.json"
        cache_data = {
            "token_decl": ["net", "token", "total_supply"],
            "wallet": ["net", "name"]
        }
        cache_file.write_text(json.dumps(cache_data))
        
        parser = CLICommandParser(cache_file=cache_file)
        result = parser.load_from_cache()
        
        assert result is True, "Valid cache should be loaded"
        assert parser._parsed is True
        assert len(parser.commands) == 2
        assert "token_decl" in parser.commands
        assert "net" in parser.commands["token_decl"]
    
    def test_save_to_cache(self, tmp_path):
        """Test saving parsed commands to cache."""
        import json
        
        cache_file = tmp_path / "test_cache.json"
        
        parser = CLICommandParser(cache_file=cache_file)
        parser.commands = {
            "token_decl": {"net", "token"},
            "wallet": {"net", "name"}
        }
        parser._parsed = True
        
        result = parser.save_to_cache()
        
        assert result is True
        assert cache_file.exists()
        
        # Verify cache content
        cached_data = json.loads(cache_file.read_text())
        assert "token_decl" in cached_data
        assert "net" in cached_data["token_decl"]

