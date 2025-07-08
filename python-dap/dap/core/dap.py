"""
🧬 DAP Core System

Central initialization and management for all DAP subsystems.
Coordinates logging, config, type utilities, time utilities, and system utilities.
"""

import logging
import threading
from typing import Optional, Dict, Any

# Import existing DAP functions
try:
    from python_cellframe_common import (
        dap_common_init, dap_common_deinit, dap_config_init, dap_config_deinit
    )
except ImportError:
    logging.warning("python_cellframe_common not available - using fallback implementations")
    # Fallback implementations
    def dap_common_init(): return 0
    def dap_common_deinit(): pass
    def dap_config_init(): return 0
    def dap_config_deinit(): pass

from .exceptions import DapException, DapInitializationError
from .types import DapType
from .logging import DapLogging, DapLogLevel
from .time import DapTime
from .system import DapSystem


class DapCoreError(DapException):
    """DAP Core specific errors"""
    pass


class Dap:
    """
    🧬 DAP Core coordinator
    
    Central initialization and management for all DAP subsystems.
    Manages DAP system initialization and provides type integration utilities.
    Python handles memory management automatically.
    
    Example:
        # Basic usage
        core = Dap()
        core.init()
        
        # Context manager (recommended)
        with Dap() as dap:
            # All DAP systems are initialized
            logging = dap.logging
            time = dap.time
            system = dap.system
    """
    
    _instance: Optional['Dap'] = None
    _lock = threading.Lock()
    
    def __init__(self):
        """Initialize DAP core coordinator"""
        self._initialized = False
        self._logger = logging.getLogger(__name__)
        
        # Initialize subsystems
        self._type = DapType()
        self._logging = DapLogging()
        self._time = DapTime()
        self._system = DapSystem()
        
        # Initialization state
        self._subsystems_initialized = {
            'common': False,
            'config': False,
            'memory': False,
            'logging': False
        }
        
        self._logger.debug("DAP Core coordinator created")
    
    def __new__(cls):
        """Singleton pattern implementation"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def init(self) -> bool:
        """
        Initialize all DAP core systems
        
        Returns:
            True if initialization successful
            
        Raises:
            DapCoreError: If initialization fails
        """
        if self._initialized:
            self._logger.warning("DAP core already initialized")
            return True
        
        try:
            # Initialize DAP common systems
            self._logger.info("Initializing DAP common systems...")
            if dap_common_init() != 0:
                raise DapCoreError("Failed to initialize DAP common systems")
            self._subsystems_initialized['common'] = True
            
            # Initialize configuration system
            self._logger.info("Initializing DAP config system...")
            if dap_config_init() != 0:
                raise DapCoreError("Failed to initialize DAP config system")
            self._subsystems_initialized['config'] = True
            
            # Mark as initialized
            self._initialized = True
            self._logger.info("DAP core initialized successfully")
            
            return True
            
        except Exception as e:
            self._logger.error(f"Failed to initialize DAP: {e}")
            # Cleanup on failure
            self._cleanup_on_failure()
            raise DapCoreError(f"DAP core initialization failed: {e}")
    
    def deinit(self) -> None:
        """Deinitialize all DAP core systems"""
        if not self._initialized:
            self._logger.debug("DAP core not initialized, nothing to deinitialize")
            return
        
        try:
            self._logger.info("Deinitializing DAP core...")
            
            # No memory cleanup needed - Python handles memory automatically
            
            # Deinitialize in reverse order
            if self._subsystems_initialized['config']:
                dap_config_deinit()
                self._subsystems_initialized['config'] = False
            
            if self._subsystems_initialized['common']:
                dap_common_deinit()
                self._subsystems_initialized['common'] = False
            
            self._initialized = False
            self._logger.info("DAP core deinitialized successfully")
            
        except Exception as e:
            self._logger.error(f"Error during DAP core deinitialization: {e}")
    
    def _cleanup_on_failure(self) -> None:
        """Cleanup partially initialized systems on failure"""
        try:
            if self._subsystems_initialized['config']:
                dap_config_deinit()
                self._subsystems_initialized['config'] = False
            
            if self._subsystems_initialized['common']:
                dap_common_deinit()
                self._subsystems_initialized['common'] = False
                
        except Exception as e:
            self._logger.error(f"Cleanup on failure error: {e}")
    
    def status(self) -> Dict[str, Any]:
        """
        Get detailed status of all DAP systems
        
        Returns:
            Status dictionary with system information
        """
        return {
            'initialized': self._initialized,
            'subsystems': self._subsystems_initialized.copy(),
            'logging': {
                'level': self._logging.get_level() if self._initialized else 'unknown'
            },
            'timestamp': self._time.now_dap() if self._initialized else 0
        }
    
    # Properties for accessing subsystems
    @property
    def type(self) -> DapType:
        """Get type helper"""
        return self._type
    
    @property
    def logging(self) -> DapLogging:
        """Get logging manager"""
        return self._logging
    
    @property
    def time(self) -> DapTime:
        """Get time helper"""
        return self._time
    
    @property
    def system(self) -> DapSystem:
        """Get system helper"""
        return self._system
    
    @property
    def is_initialized(self) -> bool:
        """Check if DAP core is initialized"""
        return self._initialized
    
    # Context manager support
    def __enter__(self) -> 'Dap':
        """Context manager entry"""
        self.init()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.deinit()
    
    def __repr__(self) -> str:
        status = "initialized" if self._initialized else "not initialized"
        return f"Dap({status})"


# Global instance management
_dap: Optional[Dap] = None
_dap_lock = threading.Lock()


def get_dap() -> Dap:
    """
    Get global DAP core instance
    
    Returns:
        Global Dap instance
    """
    global _dap
    
    if _dap is None:
        with _dap_lock:
            if _dap is None:
                _dap = Dap()
    
    return _dap


def init_dap() -> bool:
    """
    Initialize global DAP core
    
    Returns:
        True if initialization successful
    """
    dap = get_dap()
    return dap.init()


def deinit_dap() -> None:
    """Deinitialize global DAP core"""
    dap = get_dap()
    dap.deinit()


def dap_status() -> Dict[str, Any]:
    """
    Get global DAP status
    
    Returns:
        Status dictionary
    """
    dap = get_dap()
    return dap.status()


__all__ = [
    'Dap',
    'DapCoreError',
    'get_dap',
    'init_dap',
    'deinit_dap',
    'dap_status'
] 