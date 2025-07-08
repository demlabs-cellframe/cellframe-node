"""
⏰ DAP Time Utilities

Minimal utilities for DAP time types (dap_time_t).
Python handles all time operations, we only provide conversion to/from DAP native types.
"""

import logging
import time
from typing import Union

# Import only DAP time conversion functions we actually need
try:
    from python_cellframe_common import (
        dap_time_now, dap_time_to_str_rfc822
    )
except ImportError:
    logging.warning("python_cellframe_common not available - using fallback implementations")
    # Fallback implementations
    def dap_time_now(): return int(time.time())
    def dap_time_to_str_rfc822(timestamp): return time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime(timestamp))

from .exceptions import DapException


class DapTimeError(DapException):
    """DAP Time integration specific errors"""
    pass


class DapTime:
    """
    ⏰ DAP Time utilities
    
    Minimal DAP time operations for dap_time_t ↔ Python datetime conversion.
    All time operations handled by Python, only DAP type conversion.
    
    Example:
        # Get current time in DAP format
        dap_time = DapTime()
        dap_timestamp = dap_time.now_dap()
        
        # Convert to RFC822 for DAP protocols
        rfc822 = dap_time.to_rfc822(timestamp)
    """
    
    def __init__(self):
        """Initialize time helper"""
        self._logger = logging.getLogger(__name__)
    
    def now_dap(self) -> int:
        """
        Get current timestamp in DAP format (dap_time_t compatible)
        
        Returns:
            Current timestamp as DAP time integer
        """
        try:
            # Call C function: dap_time_now() - returns dap_time_t
            dap_timestamp = dap_time_now()
            self._logger.debug(f"Got DAP timestamp: {dap_timestamp}")
            return dap_timestamp
            
        except Exception as e:
            self._logger.warning(f"DAP time failed, using Python fallback: {e}")
            return int(time.time())
    
    def to_rfc822(self, timestamp: Union[int, float]) -> str:
        """
        Convert timestamp to RFC822 format for DAP protocols
        
        Args:
            timestamp: Unix timestamp (Python time or DAP time)
            
        Returns:
            RFC822 formatted time string
        """
        try:
            # Call C function: dap_time_to_str_rfc822()
            rfc822_str = dap_time_to_str_rfc822(int(timestamp))
            self._logger.debug(f"Converted {timestamp} to RFC822: {rfc822_str}")
            return rfc822_str
            
        except Exception as e:
            self._logger.warning(f"DAP RFC822 conversion failed, using Python fallback: {e}")
            return time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime(timestamp))
    
    def python_to_dap_time(self, python_timestamp: Union[int, float]) -> int:
        """
        Convert Python timestamp to DAP time format if needed
        
        Args:
            python_timestamp: Python time.time() result
            
        Returns:
            DAP-compatible timestamp
        """
        # For now, they're the same (Unix timestamp)
        # This function exists for future compatibility if DAP time format changes
        return int(python_timestamp)
    
    def dap_to_python_time(self, dap_timestamp: int) -> float:
        """
        Convert DAP time to Python timestamp if needed
        
        Args:
            dap_timestamp: DAP time value
            
        Returns:
            Python-compatible timestamp
        """
        # For now, they're the same (Unix timestamp)
        # This function exists for future compatibility if DAP time format changes
        return float(dap_timestamp)
    
    def __repr__(self) -> str:
        return "DapTime()"


# Convenience functions for quick operations
def now_dap() -> int:
    """Get current timestamp in DAP format"""
    dap_time = DapTime()
    return dap_time.now_dap()


def to_rfc822(timestamp: Union[int, float]) -> str:
    """Convert timestamp to RFC822 format for DAP protocols"""
    dap_time = DapTime()
    return dap_time.to_rfc822(timestamp)


def format_duration(seconds: Union[int, float]) -> str:
    """
    Format time duration in human readable format (pure Python)
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Human readable duration string
    """
    try:
        seconds = int(seconds)
        if seconds < 0:
            return "0s"
        
        if seconds < 60:
            return f"{seconds}s"
        elif seconds < 3600:
            minutes = seconds // 60
            remaining_seconds = seconds % 60
            if remaining_seconds == 0:
                return f"{minutes}m"
            else:
                return f"{minutes}m {remaining_seconds}s"
        elif seconds < 86400:
            hours = seconds // 3600
            remaining_minutes = (seconds % 3600) // 60
            if remaining_minutes == 0:
                return f"{hours}h"
            else:
                return f"{hours}h {remaining_minutes}m"
        else:
            days = seconds // 86400
            remaining_hours = (seconds % 86400) // 3600
            if remaining_hours == 0:
                return f"{days}d"
            else:
                return f"{days}d {remaining_hours}h"
                
    except Exception as e:
        logging.getLogger(__name__).error(f"Failed to format duration: {e}")
        return f"{seconds}s"


__all__ = [
    'DapTime',
    'DapTimeError',
    'now_dap',
    'to_rfc822',
    'format_duration'
] 