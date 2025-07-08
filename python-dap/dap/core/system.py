"""
⚙️ DAP System Utilities

Minimal utilities for DAP system functions.
Python handles all system operations, we only provide DAP-specific system calls.
"""

import logging
import subprocess
from typing import Optional

# Import only DAP system functions we actually need for integration
try:
    from python_cellframe_common import (
        exec_with_ret_multistring
    )
except ImportError:
    logging.warning("python_cellframe_common not available - using fallback implementations")
    # Fallback implementations
    def exec_with_ret_multistring(cmd): return subprocess.run(cmd, shell=True, capture_output=True, text=True).stdout

from .exceptions import DapException


class DapSystemError(DapException):
    """DAP System integration specific errors"""
    pass


class DapSystem:
    """
    ⚙️ DAP System utilities
    
    Minimal DAP-specific system operations.
    Python handles regular system calls, this provides DAP SDK integration.
    
    Example:
        # Use DAP-specific command execution when needed
        dap_system = DapSystem()
        result = dap_system.execute_dap_command("dap_specific_command")
    """
    
    def __init__(self):
        """Initialize system helper"""
        self._logger = logging.getLogger(__name__)
    
    def execute_dap_command(self, command: str) -> str:
        """
        Execute command through DAP's exec_with_ret_multistring
        
        This is only for DAP-specific commands that need to go through
        the DAP execution environment. For regular system commands,
        use Python's subprocess module directly.
        
        Args:
            command: Command to execute through DAP
            
        Returns:
            Command output as string
            
        Raises:
            DapSystemError: If command execution fails
        """
        if not command or not command.strip():
            raise DapSystemError("Empty command provided")
        
        try:
            # Call C function: exec_with_ret_multistring()
            result = exec_with_ret_multistring(command)
            
            self._logger.debug(f"Executed DAP command: {command}")
            return result if result else ""
            
        except Exception as e:
            self._logger.error(f"Failed to execute DAP command '{command}': {e}")
            raise DapSystemError(f"DAP command execution failed: {e}")
    
    def validate_command(self, command: str) -> bool:
        """
        Basic command validation for safety
        
        Args:
            command: Command to validate
            
        Returns:
            True if command appears safe
        """
        if not command or not command.strip():
            return False
        
        # Basic validation - could be extended
        dangerous_patterns = [
            'rm -rf /', 'del /f /q', 'format ', 'mkfs.', 'dd if=', 'shutdown', 'reboot'
        ]
        
        command_lower = command.lower()
        for pattern in dangerous_patterns:
            if pattern in command_lower:
                return False
        
        return True
    
    def __repr__(self) -> str:
        return "DapSystem()"


# Convenience function for DAP commands
def execute_dap_command(command: str) -> str:
    """Execute command through DAP system (for DAP-specific commands only)"""
    dap_system = DapSystem()
    return dap_system.execute_dap_command(command)


def safe_execute_dap_command(command: str, default: str = "") -> str:
    """Execute DAP command safely with default fallback"""
    try:
        return execute_dap_command(command)
    except Exception as e:
        logging.getLogger(__name__).warning(f"Safe DAP command execution failed for '{command}': {e}")
        return default


__all__ = [
    'DapSystem',
    'DapSystemError',
    'execute_dap_command',
    'safe_execute_dap_command'
] 