"""
📝 DAP Logging Management

Direct Python wrapper over DAP logging functions.
Handles log level management and logging configuration.
"""

import logging
import sys
from typing import Union
from enum import Enum

from .exceptions import DapCoreError


class DapLoggingMissingError(DapCoreError):
    """DAP Logging functions missing in C extension."""
    
    def __init__(self, missing_functions: list = None, **kwargs):
        missing_functions = missing_functions or []
        message = f"Logging functions missing in python_dap C extension. Using Python logging fallback."
        super().__init__(
            message=message,
            error_code="DAP_LOGGING_MISSING",
            **kwargs
        )
        self.add_context("missing_function_count", len(missing_functions))
        self.add_context("missing_functions", missing_functions)
        self.add_suggestion("Using Python logging as fallback")
        self.add_suggestion("Check if DAP SDK logging module is properly linked")


# Import existing DAP functions - FAIL FAST, NO FALLBACKS
try:
    from ..python_dap import (
        dap_common_init, dap_common_deinit  # These are available
    )
    
    # Try to import additional logging functions - fail if missing
    from ..python_dap import dap_set_log_level, dap_log_level_set, dap_get_log_level
    
except ImportError as e:
    print(f"🚨 CRITICAL ERROR: python_dap missing - C bindings failed to load!")
    print(f"Cannot continue without native DAP SDK bindings.")
    print(f"Import error: {e}")
    print(f"Please check:")
    print(f"  1. DAP SDK compilation successful")
    print(f"  2. python_dap.so file exists and accessible")
    print(f"  3. Library paths configured correctly")
    print(f"TERMINATING - All functions must be implemented in C extension.")
    sys.exit(1)


class DapLogLevel(Enum):
    """DAP supported log levels"""
    CRITICAL = "CRITICAL"
    ERROR = "ERROR"
    WARNING = "WARNING"
    NOTICE = "NOTICE"
    INFO = "INFO"
    DEBUG = "DEBUG"

# Mapping from string names to C constants
_LOG_LEVEL_TO_INT = {
    "DEBUG": 0,     # L_DEBUG
    "INFO": 1,      # L_INFO
    "NOTICE": 1,    # Map to L_INFO (NOTICE not in C)
    "WARNING": 5,   # L_WARNING
    "ERROR": 7,     # L_ERROR
    "CRITICAL": 8,  # L_CRITICAL
}


class DapLoggingError(DapCoreError):
    """DAP Logging specific errors"""
    pass


class DapLogging:
    """
    📝 DAP Logging wrapper
    
    Direct wrapper over dap_set_log_level/get_log_level functions.
    Provides centralized logging configuration for DAP systems.
    
    Example:
        # Basic usage
        logger = DapLogging()
        logger.set_level(DapLogLevel.DEBUG)
        
        # Static usage
        DapLogging.set_log_level(DapLogLevel.INFO)
        current_level = DapLogging.get_log_level()
    """
    
    def __init__(self):
        """Initialize logging manager"""
        self._logger = logging.getLogger(__name__)
    
    @staticmethod
    def set_log_level(level: Union[DapLogLevel, str]) -> None:
        """
        Set DAP logging level
        
        Args:
            level: Log level to set (enum or string)
            
        Raises:
            DapLoggingError: If setting log level fails
        """
        try:
            if isinstance(level, DapLogLevel):
                level_str = level.value
            else:
                level_str = str(level).upper()
                # Validate level
                if level_str not in [lvl.value for lvl in DapLogLevel]:
                    raise DapLoggingError(f"Invalid log level: {level_str}")
            
            # Convert string level to integer for C function
            level_int = _LOG_LEVEL_TO_INT.get(level_str)
            if level_int is None:
                raise DapLoggingError(f"Unknown log level: {level_str}")
            
            # Call C functions: dap_set_log_level() (int) and dap_log_level_set() (str)
            dap_set_log_level(level_int)
            dap_log_level_set(level_str)
            
            logging.getLogger(__name__).info(f"Set DAP log level to {level_str}")
            
        except Exception as e:
            raise DapLoggingError(f"Failed to set log level: {e}")
    
    @staticmethod
    def get_log_level() -> str:
        """
        Get current DAP logging level
        
        Returns:
            Current log level string
            
        Raises:
            DapLoggingError: If getting log level fails
        """
        try:
            # Call C function: dap_get_log_level()
            level = dap_get_log_level()
            return level if level else "INFO"
            
        except Exception as e:
            logging.getLogger(__name__).error(f"Failed to get log level: {e}")
            raise DapLoggingError(f"Failed to get log level: {e}")
    
    def set_level(self, level: Union[DapLogLevel, str]) -> None:
        """
        Set log level using instance method
        
        Args:
            level: Log level to set
        """
        self.set_log_level(level)
    
    def get_level(self) -> str:
        """
        Get log level using instance method
        
        Returns:
            Current log level string
        """
        return self.get_log_level()
    
    @staticmethod
    def is_level_enabled(level: Union[DapLogLevel, str]) -> bool:
        """
        Check if specific log level is enabled
        
        Args:
            level: Log level to check
            
        Returns:
            True if level is enabled
        """
        try:
            current_level = DapLogging.get_log_level()
            
            if isinstance(level, DapLogLevel):
                check_level = level.value
            else:
                check_level = str(level).upper()
            
            # Define level hierarchy
            level_hierarchy = {
                "CRITICAL": 50,
                "ERROR": 40,
                "WARNING": 30,
                "NOTICE": 25,
                "INFO": 20,
                "DEBUG": 10
            }
            
            current_priority = level_hierarchy.get(current_level, 20)
            check_priority = level_hierarchy.get(check_level, 20)
            
            return check_priority >= current_priority
            
        except Exception as e:
            logging.getLogger(__name__).error(f"Failed to check log level: {e}")
            return True  # Default to enabled
    
    @staticmethod
    def list_levels() -> list:
        """
        Get list of all available log levels
        
        Returns:
            List of log level strings
        """
        return [level.value for level in DapLogLevel]
    
    def debug(self, message: str) -> None:
        """
        Log debug message via DAP logging system
        
        Args:
            message: Debug message to log
        """
        try:
            # Try to use DAP logging
            from ..python_dap import py_dap_log_it_debug
            py_dap_log_it_debug(message)
        except (ImportError, AttributeError):
            # Fallback to Python logging
            if self.is_level_enabled(DapLogLevel.DEBUG):
                self._logger.debug(f"[DAP] {message}")
    
    def info(self, message: str) -> None:
        """
        Log info message via DAP logging system
        
        Args:
            message: Info message to log
        """
        try:
            # Try to use DAP logging
            from ..python_dap import py_dap_log_it_info
            py_dap_log_it_info(message)
        except (ImportError, AttributeError):
            # Fallback to Python logging
            if self.is_level_enabled(DapLogLevel.INFO):
                self._logger.info(f"[DAP] {message}")
    
    def error(self, message: str) -> None:
        """
        Log error message via DAP logging system
        
        Args:
            message: Error message to log
        """
        try:
            # Try to use DAP logging
            from ..python_dap import py_dap_log_it_error
            py_dap_log_it_error(message)
        except (ImportError, AttributeError):
            # Fallback to Python logging
            if self.is_level_enabled(DapLogLevel.ERROR):
                self._logger.error(f"[DAP] {message}")
    
    def warning(self, message: str) -> None:
        """
        Log warning message via DAP logging system
        
        Args:
            message: Warning message to log
        """
        try:
            # Try to use DAP logging
            from ..python_dap import py_dap_log_it_warning
            py_dap_log_it_warning(message)
        except (ImportError, AttributeError):
            # Fallback to Python logging
            if self.is_level_enabled(DapLogLevel.WARNING):
                self._logger.warning(f"[DAP] {message}")
    
    def critical(self, message: str) -> None:
        """
        Log critical message via DAP logging system
        
        Args:
            message: Critical message to log
        """
        try:
            # Try to use DAP logging for critical messages
            from ..python_dap import py_dap_log_it_error
            py_dap_log_it_error(f"CRITICAL: {message}")
        except (ImportError, AttributeError):
            # Fallback to Python logging
            if self.is_level_enabled(DapLogLevel.CRITICAL):
                self._logger.critical(f"[DAP] {message}")
    
    def __repr__(self) -> str:
        try:
            current_level = self.get_level()
            return f"DapLogging(level={current_level})"
        except:
            return "DapLogging(level=unknown)"


# Convenience functions
def set_debug_logging():
    """Enable debug logging"""
    DapLogging.set_log_level(DapLogLevel.DEBUG)


def set_info_logging():
    """Enable info logging"""
    DapLogging.set_log_level(DapLogLevel.INFO)


def set_error_logging():
    """Enable error logging only"""
    DapLogging.set_log_level(DapLogLevel.ERROR)


__all__ = [
    'DapLogging',
    'DapLogLevel', 
    'DapLoggingError',
    'set_debug_logging',
    'set_info_logging',
    'set_error_logging'
] 