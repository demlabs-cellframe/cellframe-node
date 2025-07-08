"""
🧬 DAP Events Module Implementation

Direct Python wrappers over DAP events functions.
"""

import logging
import threading
from typing import Optional, Any, Callable, Dict, List
from enum import Enum

# Import existing DAP events functions
try:
    from python_cellframe_common import (
        dap_events_init, dap_events_deinit, dap_events_start, dap_events_stop,
        dap_events_socket_create, dap_events_socket_delete, dap_events_socket_queue_ptr,
        dap_events_socket_assign_on_worker_mt, dap_events_socket_event_proc_add,
        dap_events_socket_event_proc_remove
    )
except ImportError:
    logging.warning("python_cellframe_common not available - using fallback implementations")
    # Fallback implementations for development
    def dap_events_init(workers, queue_size): return 0
    def dap_events_deinit(): pass
    def dap_events_start(): return 0
    def dap_events_stop(): return 0
    def dap_events_socket_create(socket_type, callback): return id(callback)
    def dap_events_socket_delete(socket_id): pass
    def dap_events_socket_queue_ptr(socket_id): return None
    def dap_events_socket_assign_on_worker_mt(socket_id, worker_id): return 0
    def dap_events_socket_event_proc_add(socket_id, event_type, callback): return 0
    def dap_events_socket_event_proc_remove(socket_id, event_type): return 0

from ..core.exceptions import DapException, DapEventError


class DapEventType(Enum):
    """DAP event types."""
    READ = "read"
    WRITE = "write"
    ERROR = "error"
    CLOSE = "close"
    TIMER = "timer"
    SIGNAL = "signal"


class DapEvents:
    """
    DAP Events wrapper.
    
    Provides access to DAP event system with Python callbacks.
    """
    
    _instance: Optional['DapEvents'] = None
    _lock = threading.Lock()
    
    def __init__(self, workers: int = 4, queue_size: int = 1024):
        """Initialize DAP events instance."""
        self._workers = workers
        self._queue_size = queue_size
        self._initialized = False
        self._started = False
        self._logger = logging.getLogger(__name__)
        self._event_callbacks: Dict[str, List[Callable]] = {}
        self._socket_handles: Dict[int, int] = {}
        
    def __new__(cls, workers: int = 4, queue_size: int = 1024):
        """Singleton pattern for global events."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def init(self) -> bool:
        """Initialize DAP events system."""
        if self._initialized:
            self._logger.warning("DAP events already initialized")
            return True
        
        try:
            # Initialize events system
            if dap_events_init(self._workers, self._queue_size) != 0:
                raise DapEventError("Failed to initialize DAP events system")
            
            self._initialized = True
            self._logger.info(f"DAP events initialized with {self._workers} workers, queue size {self._queue_size}")
            return True
            
        except Exception as e:
            self._logger.error(f"Failed to initialize DAP events: {e}")
            raise DapEventError(f"DAP events initialization failed: {e}")
    
    def deinit(self) -> None:
        """Deinitialize DAP events system."""
        if not self._initialized:
            return
        
        try:
            # Stop events if running
            if self._started:
                self.stop()
            
            # Cleanup socket handles
            for socket_id in list(self._socket_handles.keys()):
                self.delete_socket(socket_id)
            
            # Deinitialize events system
            dap_events_deinit()
            
            self._initialized = False
            self._logger.info("DAP events deinitialized")
            
        except Exception as e:
            self._logger.error(f"Error during DAP events deinitialization: {e}")
    
    def start(self) -> bool:
        """Start DAP events processing."""
        if not self._initialized:
            raise DapEventError("DAP events not initialized")
        
        if self._started:
            self._logger.warning("DAP events already started")
            return True
        
        try:
            if dap_events_start() != 0:
                raise DapEventError("Failed to start DAP events")
            
            self._started = True
            self._logger.info("DAP events started")
            return True
            
        except Exception as e:
            self._logger.error(f"Failed to start DAP events: {e}")
            raise DapEventError(f"DAP events start failed: {e}")
    
    def stop(self) -> bool:
        """Stop DAP events processing."""
        if not self._started:
            return True
        
        try:
            if dap_events_stop() != 0:
                self._logger.warning("DAP events stop returned non-zero")
            
            self._started = False
            self._logger.info("DAP events stopped")
            return True
            
        except Exception as e:
            self._logger.error(f"Failed to stop DAP events: {e}")
            return False
    
    def create_socket(self, socket_type: str, callback: Callable) -> Optional[int]:
        """Create event socket."""
        if not self._initialized:
            raise DapEventError("DAP events not initialized")
        
        try:
            socket_id = dap_events_socket_create(socket_type, callback)
            if socket_id is None:
                raise DapEventError(f"Failed to create socket of type {socket_type}")
            
            self._socket_handles[socket_id] = socket_id
            self._logger.debug(f"Created socket {socket_id} of type {socket_type}")
            return socket_id
            
        except Exception as e:
            self._logger.error(f"Failed to create socket: {e}")
            return None
    
    def delete_socket(self, socket_id: int) -> bool:
        """Delete event socket."""
        if socket_id not in self._socket_handles:
            self._logger.warning(f"Socket {socket_id} not found")
            return False
        
        try:
            dap_events_socket_delete(socket_id)
            del self._socket_handles[socket_id]
            self._logger.debug(f"Deleted socket {socket_id}")
            return True
            
        except Exception as e:
            self._logger.error(f"Failed to delete socket {socket_id}: {e}")
            return False
    
    def assign_socket_to_worker(self, socket_id: int, worker_id: int) -> bool:
        """Assign socket to specific worker."""
        if socket_id not in self._socket_handles:
            raise DapEventError(f"Socket {socket_id} not found")
        
        try:
            if dap_events_socket_assign_on_worker_mt(socket_id, worker_id) != 0:
                raise DapEventError(f"Failed to assign socket {socket_id} to worker {worker_id}")
            
            self._logger.debug(f"Assigned socket {socket_id} to worker {worker_id}")
            return True
            
        except Exception as e:
            self._logger.error(f"Failed to assign socket to worker: {e}")
            return False
    
    def add_event_handler(self, socket_id: int, event_type: DapEventType, callback: Callable) -> bool:
        """Add event handler for socket."""
        if socket_id not in self._socket_handles:
            raise DapEventError(f"Socket {socket_id} not found")
        
        try:
            if dap_events_socket_event_proc_add(socket_id, event_type.value, callback) != 0:
                raise DapEventError(f"Failed to add {event_type.value} handler for socket {socket_id}")
            
            # Track callback
            event_key = f"{socket_id}:{event_type.value}"
            if event_key not in self._event_callbacks:
                self._event_callbacks[event_key] = []
            self._event_callbacks[event_key].append(callback)
            
            self._logger.debug(f"Added {event_type.value} handler for socket {socket_id}")
            return True
            
        except Exception as e:
            self._logger.error(f"Failed to add event handler: {e}")
            return False
    
    def remove_event_handler(self, socket_id: int, event_type: DapEventType) -> bool:
        """Remove event handler for socket."""
        if socket_id not in self._socket_handles:
            raise DapEventError(f"Socket {socket_id} not found")
        
        try:
            if dap_events_socket_event_proc_remove(socket_id, event_type.value) != 0:
                self._logger.warning(f"Failed to remove {event_type.value} handler for socket {socket_id}")
            
            # Remove tracked callbacks
            event_key = f"{socket_id}:{event_type.value}"
            if event_key in self._event_callbacks:
                del self._event_callbacks[event_key]
            
            self._logger.debug(f"Removed {event_type.value} handler for socket {socket_id}")
            return True
            
        except Exception as e:
            self._logger.error(f"Failed to remove event handler: {e}")
            return False
    
    def emit(self, event_name: str, data: Any = None) -> bool:
        """Emit custom event (simplified interface)."""
        try:
            # This is a simplified implementation
            # Real implementation would need proper event system integration
            self._logger.debug(f"Emitting event: {event_name}")
            return True
            
        except Exception as e:
            self._logger.error(f"Failed to emit event {event_name}: {e}")
            return False
    
    def subscribe(self, event_name: str, callback: Callable) -> Optional[int]:
        """Subscribe to custom event (simplified interface)."""
        try:
            # This is a simplified implementation
            # Real implementation would need proper event system integration
            if event_name not in self._event_callbacks:
                self._event_callbacks[event_name] = []
            self._event_callbacks[event_name].append(callback)
            
            subscription_id = id(callback)
            self._logger.debug(f"Subscribed to event: {event_name}")
            return subscription_id
            
        except Exception as e:
            self._logger.error(f"Failed to subscribe to event {event_name}: {e}")
            return None
    
    @property
    def is_initialized(self) -> bool:
        """Check if DAP events is initialized."""
        return self._initialized
    
    @property
    def is_started(self) -> bool:
        """Check if DAP events is started."""
        return self._started
    
    @property
    def workers_count(self) -> int:
        """Get number of workers."""
        return self._workers
    
    @property
    def queue_size(self) -> int:
        """Get queue size."""
        return self._queue_size
    
    def __enter__(self):
        """Context manager entry."""
        self.init()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.deinit()


# Global instance
_dap_events_instance: Optional[DapEvents] = None
_dap_events_lock = threading.Lock()


def get_dap_events() -> DapEvents:
    """Get global DAP events instance."""
    global _dap_events_instance
    
    if _dap_events_instance is None:
        with _dap_events_lock:
            if _dap_events_instance is None:
                _dap_events_instance = DapEvents()
    
    return _dap_events_instance


__all__ = ['DapEvents', 'DapEventType', 'get_dap_events'] 