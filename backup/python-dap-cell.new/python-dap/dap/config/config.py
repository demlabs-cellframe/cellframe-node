"""
🧬 DAP Config Module Implementation

Direct Python wrappers over DAP config functions.
"""

import logging
import threading
from typing import Optional, Any, Dict, List
from pathlib import Path

# Import existing DAP config functions
try:
    from python_cellframe_common import (
        dap_config_init, dap_config_deinit, dap_config_open, dap_config_close,
        dap_config_get_item_str, dap_config_get_item_int, dap_config_get_item_bool,
        dap_config_set_item_str, dap_config_set_item_int, dap_config_set_item_bool,
        dap_config_get_sys_dir, py_m_dap_config_get_item, py_m_dap_config_get_sys_dir
    )
except ImportError:
    logging.warning("python_cellframe_common not available - using fallback implementations")
    # Fallback implementations for development
    def dap_config_init(): return 0
    def dap_config_deinit(): pass
    def dap_config_open(path): return id(path)
    def dap_config_close(config): pass
    def dap_config_get_item_str(config, section, key, default): return default
    def dap_config_get_item_int(config, section, key, default): return default
    def dap_config_get_item_bool(config, section, key, default): return default
    def dap_config_set_item_str(config, section, key, value): return True
    def dap_config_set_item_int(config, section, key, value): return True
    def dap_config_set_item_bool(config, section, key, value): return True
    def dap_config_get_sys_dir(): return "/tmp"
    def py_m_dap_config_get_item(section, key, default): return default
    def py_m_dap_config_get_sys_dir(): return "/tmp"

from ..core.exceptions import DapException, DapConfigError


class DapConfig:
    """
    DAP Configuration wrapper.
    
    Provides access to DAP configuration system with type-safe methods.
    """
    
    _instance: Optional['DapConfig'] = None
    _lock = threading.Lock()
    
    def __init__(self, config_file: Optional[str] = None):
        """Initialize DAP config instance."""
        self._config_handle: Optional[int] = None
        self._config_file = config_file
        self._initialized = False
        self._logger = logging.getLogger(__name__)
        
    def __new__(cls, config_file: Optional[str] = None):
        """Singleton pattern for global config."""
        if config_file is None:
            if cls._instance is None:
                with cls._lock:
                    if cls._instance is None:
                        cls._instance = super().__new__(cls)
            return cls._instance
        else:
            # Return new instance for specific config file
            return super().__new__(cls)
    
    def init(self) -> bool:
        """Initialize DAP config system."""
        if self._initialized:
            self._logger.warning("DAP config already initialized")
            return True
        
        try:
            # Initialize config system
            if dap_config_init() != 0:
                raise DapConfigError("Failed to initialize DAP config system")
            
            # Open config file if specified
            if self._config_file:
                self._config_handle = dap_config_open(self._config_file)
                if self._config_handle is None:
                    raise DapConfigError(f"Failed to open config file: {self._config_file}")
            
            self._initialized = True
            self._logger.info("DAP config initialized successfully")
            return True
            
        except Exception as e:
            self._logger.error(f"Failed to initialize DAP config: {e}")
            raise DapConfigError(f"DAP config initialization failed: {e}")
    
    def deinit(self) -> None:
        """Deinitialize DAP config system."""
        if not self._initialized:
            return
        
        try:
            # Close config file
            if self._config_handle:
                dap_config_close(self._config_handle)
                self._config_handle = None
            
            # Deinitialize config system
            dap_config_deinit()
            
            self._initialized = False
            self._logger.info("DAP config deinitialized")
            
        except Exception as e:
            self._logger.error(f"Error during DAP config deinitialization: {e}")
    
    def get_item_str(self, section: str, key: str, default: str = "") -> str:
        """Get string configuration item."""
        try:
            if self._config_handle:
                return dap_config_get_item_str(self._config_handle, section, key, default)
            else:
                # Use global config function
                return py_m_dap_config_get_item(section, key, default)
                
        except Exception as e:
            self._logger.error(f"Failed to get config item {section}.{key}: {e}")
            return default
    
    def get_item_int(self, section: str, key: str, default: int = 0) -> int:
        """Get integer configuration item."""
        try:
            if self._config_handle:
                return dap_config_get_item_int(self._config_handle, section, key, default)
            else:
                # Use global config function and convert
                value = py_m_dap_config_get_item(section, key, str(default))
                return int(value) if value.isdigit() else default
                
        except Exception as e:
            self._logger.error(f"Failed to get config item {section}.{key}: {e}")
            return default
    
    def get_item_bool(self, section: str, key: str, default: bool = False) -> bool:
        """Get boolean configuration item."""
        try:
            if self._config_handle:
                return dap_config_get_item_bool(self._config_handle, section, key, default)
            else:
                # Use global config function and convert
                value = py_m_dap_config_get_item(section, key, str(default).lower())
                return value.lower() in ('true', '1', 'yes', 'on')
                
        except Exception as e:
            self._logger.error(f"Failed to get config item {section}.{key}: {e}")
            return default
    
    def set_item_str(self, section: str, key: str, value: str) -> bool:
        """Set string configuration item."""
        if not self._config_handle:
            raise DapConfigError("Config not opened for writing")
        
        try:
            return dap_config_set_item_str(self._config_handle, section, key, value)
            
        except Exception as e:
            self._logger.error(f"Failed to set config item {section}.{key}: {e}")
            return False
    
    def set_item_int(self, section: str, key: str, value: int) -> bool:
        """Set integer configuration item."""
        if not self._config_handle:
            raise DapConfigError("Config not opened for writing")
        
        try:
            return dap_config_set_item_int(self._config_handle, section, key, value)
            
        except Exception as e:
            self._logger.error(f"Failed to set config item {section}.{key}: {e}")
            return False
    
    def set_item_bool(self, section: str, key: str, value: bool) -> bool:
        """Set boolean configuration item."""
        if not self._config_handle:
            raise DapConfigError("Config not opened for writing")
        
        try:
            return dap_config_set_item_bool(self._config_handle, section, key, value)
            
        except Exception as e:
            self._logger.error(f"Failed to set config item {section}.{key}: {e}")
            return False
    
    def get_sys_dir(self) -> str:
        """Get system configuration directory."""
        try:
            return py_m_dap_config_get_sys_dir()
            
        except Exception as e:
            self._logger.error(f"Failed to get system directory: {e}")
            return "/tmp"
    
    @property
    def is_initialized(self) -> bool:
        """Check if DAP config is initialized."""
        return self._initialized
    
    @property
    def config_file(self) -> Optional[str]:
        """Get config file path."""
        return self._config_file
    
    def __enter__(self):
        """Context manager entry."""
        self.init()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.deinit()


# Global instance
_dap_config_instance: Optional[DapConfig] = None
_dap_config_lock = threading.Lock()


def get_dap_config() -> DapConfig:
    """Get global DAP config instance."""
    global _dap_config_instance
    
    if _dap_config_instance is None:
        with _dap_config_lock:
            if _dap_config_instance is None:
                _dap_config_instance = DapConfig()
    
    return _dap_config_instance


__all__ = ['DapConfig', 'get_dap_config'] 