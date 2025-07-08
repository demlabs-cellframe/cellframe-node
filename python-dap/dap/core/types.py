"""
🔗 DAP Type Utilities

Minimal utilities for converting Python types to DAP native types.
Only includes functions needed for seamless Python ↔ DAP C interop.
Python handles all memory management automatically.
"""

import logging
from typing import Any

from .exceptions import DapException


class DapTypeError(DapException):
    """DAP Type conversion specific errors"""
    pass


class DapType:
    """
    🔗 DAP Type utilities
    
    Minimal helper for Python ↔ DAP type conversions.
    Python handles all memory management, we just provide conversion.
    
    Example:
        # Convert Python types to DAP types when needed
        dap_type = DapType()
        formatted = dap_type.format_bytes(1024)
    """
    
    def __init__(self):
        """Initialize type helper"""
        self._logger = logging.getLogger(__name__)
    
    def format_bytes(self, size: int) -> str:
        """
        Format byte size in human readable format (pure Python)
        
        Args:
            size: Size in bytes
            
        Returns:
            Formatted string (e.g., "1.5 MB")
        """
        try:
            units = ['B', 'KB', 'MB', 'GB', 'TB']
            unit_index = 0
            size_float = float(size)
            
            while size_float >= 1024.0 and unit_index < len(units) - 1:
                size_float /= 1024.0
                unit_index += 1
            
            if unit_index == 0:
                return f"{int(size_float)} {units[unit_index]}"
            else:
                return f"{size_float:.2f} {units[unit_index]}"
                
        except Exception as e:
            self._logger.error(f"Failed to format bytes: {e}")
            return f"{size} B"
    
    def __repr__(self) -> str:
        return "DapType()"


# Convenience function for byte formatting
def format_bytes(size: int) -> str:
    """Format byte size in human readable format"""
    dap_type = DapType()
    return dap_type.format_bytes(size)


__all__ = ['DapType', 'DapTypeError', 'format_bytes'] 