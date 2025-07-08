"""
📁 DAP Configuration File Operations

Direct Python wrapper over DAP config file functions.
Handles opening, closing, reading and writing configuration files.
"""

import logging
from typing import Optional, Any, Union
from pathlib import Path

# Import existing DAP functions
try:
    from python_cellframe_common import (
        dap_config_open, dap_config_close,
        dap_config_get_item_str, dap_config_get_item_int, dap_config_get_item_bool,
        dap_config_set_item_str, dap_config_set_item_int, dap_config_set_item_bool,
        py_m_dap_config_get_item
    )
except ImportError:
    logging.warning("python_cellframe_common not available - using fallback implementations")
    # Fallback implementations
    def dap_config_open(path): return id(path)
    def dap_config_close(config): pass
    def dap_config_get_item_str(config, section, key, default): return default
    def dap_config_get_item_int(config, section, key, default): return default
    def dap_config_get_item_bool(config, section, key, default): return default
    def dap_config_set_item_str(config, section, key, value): return True
    def dap_config_set_item_int(config, section, key, value): return True
    def dap_config_set_item_bool(config, section, key, value): return True
    def py_m_dap_config_get_item(section, key, default): return default

from ..core.exceptions import DapException


class DapConfigFileError(DapException):
    """DAP Config File specific errors"""
    pass


class DapConfigFile:
    """
    📁 DAP Configuration File wrapper
    
    Direct wrapper over dap_config_open/close and item access functions.
    Provides type-safe configuration file operations.
    
    Example:
        # Basic usage
        config = DapConfigFile("/path/to/config.cfg")
        config.open()
        value = config.get_string("section", "key", "default")
        
        # Context manager
        with DapConfigFile("/path/to/config.cfg") as config:
            value = config.get_string("database", "host", "localhost")
            config.set_string("database", "host", "new_host")
    """
    
    def __init__(self, config_path: Union[str, Path]):
        """
        Initialize configuration file handler
        
        Args:
            config_path: Path to configuration file
        """
        self._config_path = str(config_path)
        self._config_handle: Optional[int] = None
        self._opened = False
        self._logger = logging.getLogger(__name__)
    
    def open(self) -> bool:
        """
        Open configuration file
        
        Returns:
            True if file opened successfully
            
        Raises:
            DapConfigFileError: If opening fails
        """
        if self._opened:
            self._logger.warning(f"Config file {self._config_path} already opened")
            return True
        
        if not self._config_path:
            raise DapConfigFileError("Config file path cannot be empty")
        
        try:
            # Call C function: dap_config_open()
            self._config_handle = dap_config_open(self._config_path)
            if self._config_handle is None:
                raise DapConfigFileError(f"Failed to open config file: {self._config_path}")
            
            self._opened = True
            self._logger.info(f"Opened config file: {self._config_path}")
            return True
            
        except Exception as e:
            raise DapConfigFileError(f"Config file open failed: {e}")
    
    def close(self) -> None:
        """Close configuration file"""
        if not self._opened or self._config_handle is None:
            return
        
        try:
            # Call C function: dap_config_close()
            dap_config_close(self._config_handle)
            self._config_handle = None
            self._opened = False
            self._logger.info(f"Closed config file: {self._config_path}")
            
        except Exception as e:
            self._logger.error(f"Failed to close config file: {e}")
    
    def get_string(self, section: str, key: str, default: str = "") -> str:
        """
        Get string value from configuration
        
        Args:
            section: Configuration section name
            key: Configuration key name
            default: Default value if key not found
            
        Returns:
            Configuration value as string
            
        Raises:
            DapConfigFileError: If file not opened
        """
        if not self._opened or self._config_handle is None:
            raise DapConfigFileError("Config file not opened")
        
        try:
            # Call C function: dap_config_get_item_str()
            value = dap_config_get_item_str(self._config_handle, section, key, default)
            self._logger.debug(f"Got string {section}.{key} = {value}")
            return value
            
        except Exception as e:
            self._logger.error(f"Failed to get config item {section}.{key}: {e}")
            return default
    
    def get_integer(self, section: str, key: str, default: int = 0) -> int:
        """
        Get integer value from configuration
        
        Args:
            section: Configuration section name
            key: Configuration key name
            default: Default value if key not found
            
        Returns:
            Configuration value as integer
        """
        if not self._opened or self._config_handle is None:
            raise DapConfigFileError("Config file not opened")
        
        try:
            # Call C function: dap_config_get_item_int()
            value = dap_config_get_item_int(self._config_handle, section, key, default)
            self._logger.debug(f"Got integer {section}.{key} = {value}")
            return value
            
        except Exception as e:
            self._logger.error(f"Failed to get config item {section}.{key}: {e}")
            return default
    
    def get_boolean(self, section: str, key: str, default: bool = False) -> bool:
        """
        Get boolean value from configuration
        
        Args:
            section: Configuration section name
            key: Configuration key name
            default: Default value if key not found
            
        Returns:
            Configuration value as boolean
        """
        if not self._opened or self._config_handle is None:
            raise DapConfigFileError("Config file not opened")
        
        try:
            # Call C function: dap_config_get_item_bool()
            value = dap_config_get_item_bool(self._config_handle, section, key, default)
            self._logger.debug(f"Got boolean {section}.{key} = {value}")
            return value
            
        except Exception as e:
            self._logger.error(f"Failed to get config item {section}.{key}: {e}")
            return default
    
    def set_string(self, section: str, key: str, value: str) -> bool:
        """
        Set string value in configuration
        
        Args:
            section: Configuration section name
            key: Configuration key name
            value: Value to set
            
        Returns:
            True if value was set successfully
            
        Raises:
            DapConfigFileError: If file not opened
        """
        if not self._opened or self._config_handle is None:
            raise DapConfigFileError("Config file not opened")
        
        try:
            # Call C function: dap_config_set_item_str()
            result = dap_config_set_item_str(self._config_handle, section, key, value)
            if result:
                self._logger.debug(f"Set string {section}.{key} = {value}")
            return result
            
        except Exception as e:
            self._logger.error(f"Failed to set config item {section}.{key}: {e}")
            return False
    
    def set_integer(self, section: str, key: str, value: int) -> bool:
        """
        Set integer value in configuration
        
        Args:
            section: Configuration section name
            key: Configuration key name
            value: Value to set
            
        Returns:
            True if value was set successfully
        """
        if not self._opened or self._config_handle is None:
            raise DapConfigFileError("Config file not opened")
        
        try:
            # Call C function: dap_config_set_item_int()
            result = dap_config_set_item_int(self._config_handle, section, key, value)
            if result:
                self._logger.debug(f"Set integer {section}.{key} = {value}")
            return result
            
        except Exception as e:
            self._logger.error(f"Failed to set config item {section}.{key}: {e}")
            return False
    
    def set_boolean(self, section: str, key: str, value: bool) -> bool:
        """
        Set boolean value in configuration
        
        Args:
            section: Configuration section name
            key: Configuration key name
            value: Value to set
            
        Returns:
            True if value was set successfully
        """
        if not self._opened or self._config_handle is None:
            raise DapConfigFileError("Config file not opened")
        
        try:
            # Call C function: dap_config_set_item_bool()
            result = dap_config_set_item_bool(self._config_handle, section, key, value)
            if result:
                self._logger.debug(f"Set boolean {section}.{key} = {value}")
            return result
            
        except Exception as e:
            self._logger.error(f"Failed to set config item {section}.{key}: {e}")
            return False
    
    @property
    def is_opened(self) -> bool:
        """Check if configuration file is opened"""
        return self._opened
    
    @property
    def config_path(self) -> str:
        """Get configuration file path"""
        return self._config_path
    
    @property
    def handle(self) -> Optional[int]:
        """Get configuration file handle"""
        return self._config_handle
    
    def __enter__(self) -> 'DapConfigFile':
        """Context manager entry"""
        self.open()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
    
    def __repr__(self) -> str:
        return f"DapConfigFile(path='{self._config_path}', opened={self._opened})"


__all__ = ['DapConfigFile', 'DapConfigFileError'] 