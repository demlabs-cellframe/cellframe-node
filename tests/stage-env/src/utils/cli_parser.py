"""
CLI command parser for extracting available options from help output.

Parses cellframe-node-cli help to build a map of commands and their options,
enabling automatic prefix injection in scenarios.
"""

import re
import json
from typing import Dict, List, Set
from pathlib import Path

from ..utils.logger import get_logger

logger = get_logger(__name__)


class CLICommandParser:
    """Parse CLI commands and extract available options."""
    
    def __init__(self, cache_file: Path = None):
        """
        Initialize CLI parser.
        
        Args:
            cache_file: Optional path to cache file for parsed commands
        """
        self.commands: Dict[str, Set[str]] = {}
        self._parsed = False
        self.cache_file = cache_file
    
    def load_from_cache(self) -> bool:
        """
        Load parsed commands from cache file.
        
        Returns:
            True if cache was loaded successfully
        """
        if not self.cache_file or not self.cache_file.exists():
            return False
        
        try:
            with open(self.cache_file, 'r') as f:
                data = json.load(f)
            
            # Convert lists back to sets
            self.commands = {
                cmd: set(opts) 
                for cmd, opts in data.items()
            }
            
            # Validate cache is not empty
            if not self.commands:
                logger.warning("Cache file exists but is empty - will reparse")
                return False
            
            self._parsed = True
            logger.info(f"Loaded CLI commands from cache: {len(self.commands)} commands")
            return True
            
        except Exception as e:
            logger.warning(f"Failed to load cache: {e}")
            return False
    
    def save_to_cache(self) -> bool:
        """
        Save parsed commands to cache file.
        
        Returns:
            True if cache was saved successfully
        """
        if not self.cache_file or not self._parsed:
            return False
        
        try:
            # Ensure cache directory exists
            self.cache_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Convert sets to lists for JSON serialization
            data = {
                cmd: list(opts) 
                for cmd, opts in self.commands.items()
            }
            
            with open(self.cache_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"Saved CLI commands to cache: {self.cache_file}")
            return True
            
        except Exception as e:
            logger.warning(f"Failed to save cache: {e}")
            return False
    
    async def parse_cli_help(self, node_container: str, use_cache: bool = True) -> bool:
        """
        Parse CLI help from a running node container.
        
        Args:
            node_container: Docker container name
            use_cache: If True, try to load from cache first
            
        Returns:
            True if parsing succeeded
        """
        import asyncio
        
        # Try cache first
        if use_cache and self.load_from_cache():
            return True
        
        try:
            logger.info("Parsing CLI help from container", container=node_container)
            
            # Get main help
            main_help = await self._exec_cli_help(node_container, [])
            if not main_help:
                logger.warning("Failed to get main CLI help")
                return False
            
            # Extract command list from main help
            commands = self._extract_commands(main_help)
            logger.info(f"Found {len(commands)} CLI commands")
            
            # Parse help for each command
            for cmd in commands:
                cmd_help = await self._exec_cli_help(node_container, [cmd, "-h"])
                if cmd_help:
                    options = self._extract_options(cmd_help)
                    self.commands[cmd] = options
                    logger.debug(f"Command '{cmd}': {len(options)} options")
            
            self._parsed = True
            logger.info(f"CLI parsing complete: {len(self.commands)} commands mapped")
            
            # Save to cache
            self.save_to_cache()
            
            return True
            
        except Exception as e:
            logger.error("Failed to parse CLI help", error=str(e))
            return False
    
    async def _exec_cli_help(self, container: str, args: List[str]) -> str:
        """Execute CLI help command in container."""
        import asyncio
        
        cmd = ["docker", "exec", container, "cellframe-node-cli"] + args
        
        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=10)
            
            if proc.returncode == 0:
                return stdout.decode('utf-8', errors='ignore')
            else:
                # Some commands return help on stderr with non-zero exit
                return stderr.decode('utf-8', errors='ignore')
                
        except asyncio.TimeoutError:
            logger.warning("CLI help command timeout", args=args)
            return ""
        except Exception as e:
            logger.debug("CLI help exec failed", args=args, error=str(e))
            return ""
    
    def _extract_commands(self, help_text: str) -> List[str]:
        """Extract command names from main help output."""
        commands = []
        
        # Look for lines that look like commands
        # Format: "  command_name         Description"
        pattern = r'^\s{2,}(\w+)\s+'
        
        for line in help_text.split('\n'):
            match = re.match(pattern, line)
            if match:
                cmd = match.group(1)
                # Filter out common help keywords
                if cmd not in ['help', 'version', 'exit', 'quit']:
                    commands.append(cmd)
        
        return commands
    
    def _extract_options(self, help_text: str) -> Set[str]:
        """Extract option names from command help output."""
        options = set()
        
        # Look for option patterns: -option, --option, -option <value>
        # Common formats in cellframe-node-cli:
        # -net <network>
        # -token <token_name>
        # -addr <address>
        
        patterns = [
            r'-(\w+)\s+<',      # -net <network>
            r'-(\w+)\s+\[',     # -net [network]
            r'-(\w+)(?:\s|$)',  # -flag or -flag\n
        ]
        
        for pattern in patterns:
            for match in re.finditer(pattern, help_text):
                option = match.group(1)
                # Skip common single-letter flags
                if len(option) > 1:
                    options.add(option)
        
        return options
    
    def get_command_options(self, command: str) -> Set[str]:
        """
        Get available options for a command.
        
        Args:
            command: Command name (e.g., 'token_decl')
            
        Returns:
            Set of option names (e.g., {'net', 'token', 'total_supply'})
        """
        return self.commands.get(command, set())
    
    def has_option(self, command: str, option: str) -> bool:
        """
        Check if command supports an option.
        
        Args:
            command: Command name
            option: Option name (without -)
            
        Returns:
            True if command has this option
        """
        return option in self.get_command_options(command)
    
    def apply_cli_defaults(self, cli_command: str, defaults: Dict[str, str]) -> str:
        """
        Apply default option values to CLI command.
        
        Args:
            cli_command: Original CLI command string
            defaults: Dict of option:value pairs (e.g., {'net': 'stagenet'})
            
        Returns:
            CLI command with defaults applied
        """
        if not defaults:
            return cli_command
        
        # Ensure cli_command is a string
        if not isinstance(cli_command, str):
            logger.warning(f"apply_cli_defaults received non-string command: {type(cli_command)}")
            return str(cli_command) if cli_command else ""
        
        # Extract command name (first word)
        parts = cli_command.split()
        if not parts:
            return cli_command
        
        command = parts[0]
        
        # Get available options for this command
        available_options = self.get_command_options(command)
        
        # Build list of options to add
        options_to_add = []
        for option, value in defaults.items():
            # Check if command supports this option
            if option in available_options:
                # Check if option is not already in command (word boundary aware)
                import re
                pattern = rf'(^|\s)-{re.escape(option)}(\s|$)'
                if not re.search(pattern, cli_command):
                    options_to_add.append(f"-{option} {value}")
        
        # Add options to command
        if options_to_add:
            return f"{cli_command} {' '.join(options_to_add)}"
        
        return cli_command
    
    def get_stats(self) -> Dict:
        """Get parsing statistics."""
        return {
            "parsed": self._parsed,
            "total_commands": len(self.commands),
            "commands": {
                cmd: len(opts) 
                for cmd, opts in self.commands.items()
            }
        }


# Global singleton instance
_cli_parser: CLICommandParser = None


def get_cli_parser(cache_file: Path = None) -> CLICommandParser:
    """
    Get global CLI parser instance.
    
    Args:
        cache_file: Optional cache file path (only used on first call)
    
    Returns:
        Global CLICommandParser instance
    """
    global _cli_parser
    if _cli_parser is None:
        _cli_parser = CLICommandParser(cache_file=cache_file)
    return _cli_parser

