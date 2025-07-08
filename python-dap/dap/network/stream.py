"""
🌊 DAP Stream Operations

Proper Python wrapper with dap_stream_t* structure management.
Handles streaming data operations with proper C integration.
"""

import logging
import threading
from typing import Optional, Dict, Any, Callable, List
from enum import Enum

# Import existing DAP functions
try:
    from python_cellframe_common import (
        # Core stream functions
        dap_stream_new, dap_stream_delete, dap_stream_open,
        dap_stream_close, dap_stream_write, dap_stream_read,
        dap_stream_get_id, dap_stream_set_callbacks,
        dap_stream_get_remote_addr, dap_stream_get_remote_port,
        # Channel management
        dap_stream_ch_new, dap_stream_ch_delete, dap_stream_ch_write,
        dap_stream_ch_read, dap_stream_ch_set_ready_to_read,
        dap_stream_ch_set_ready_to_write, dap_stream_ch_get_id,
        # Worker management  
        dap_stream_worker_new, dap_stream_worker_delete,
        dap_stream_worker_add_stream, dap_stream_worker_remove_stream,
        dap_stream_worker_get_count, dap_stream_worker_get_stats,
        # System functions
        dap_stream_init, dap_stream_deinit, dap_stream_ctl_init_py,
        dap_stream_ctl_deinit, dap_stream_get_all,
        # Stream state constants
        DAP_STREAM_STATE_NEW, DAP_STREAM_STATE_CONNECTED,
        DAP_STREAM_STATE_LISTENING, DAP_STREAM_STATE_ERROR,
        DAP_STREAM_STATE_CLOSED
    )
except ImportError:
    logging.warning("python_cellframe_common not available - using fallback implementations")
    # Fallback implementations for development
    def dap_stream_new(): return id("stream")
    def dap_stream_delete(stream): pass
    def dap_stream_open(stream, addr, port): return 0
    def dap_stream_close(stream): return 0
    def dap_stream_write(stream, data, size): return size
    def dap_stream_read(stream, buffer, size): return 0
    def dap_stream_get_id(stream): return stream
    def dap_stream_set_callbacks(stream, read_cb, write_cb, error_cb): pass
    def dap_stream_get_remote_addr(stream): return "127.0.0.1"
    def dap_stream_get_remote_port(stream): return 0
    def dap_stream_ch_new(stream, channel_id): return id(f"channel_{channel_id}")
    def dap_stream_ch_delete(channel): pass
    def dap_stream_ch_write(channel, data, size): return size
    def dap_stream_ch_read(channel, buffer, size): return 0
    def dap_stream_ch_set_ready_to_read(channel, ready): pass
    def dap_stream_ch_set_ready_to_write(channel, ready): pass
    def dap_stream_ch_get_id(channel): return 1
    def dap_stream_worker_new(name): return id(f"worker_{name}")
    def dap_stream_worker_delete(worker): pass
    def dap_stream_worker_add_stream(worker, stream): return 0
    def dap_stream_worker_remove_stream(worker, stream): return 0
    def dap_stream_worker_get_count(worker): return 0
    def dap_stream_worker_get_stats(worker): return {}
    def dap_stream_init(config): return 0
    def dap_stream_deinit(): pass
    def dap_stream_ctl_init_py(workers): return 0
    def dap_stream_ctl_deinit(): pass
    def dap_stream_get_all(): return []
    # State constants
    DAP_STREAM_STATE_NEW = 0
    DAP_STREAM_STATE_CONNECTED = 1
    DAP_STREAM_STATE_LISTENING = 2
    DAP_STREAM_STATE_ERROR = 3
    DAP_STREAM_STATE_CLOSED = 4

from ..core.exceptions import DapException


class DapStreamError(DapException):
    """DAP Stream specific errors"""
    pass


class DapStreamState(Enum):
    """DAP stream states"""
    NEW = DAP_STREAM_STATE_NEW
    CONNECTED = DAP_STREAM_STATE_CONNECTED
    LISTENING = DAP_STREAM_STATE_LISTENING
    ERROR = DAP_STREAM_STATE_ERROR
    CLOSED = DAP_STREAM_STATE_CLOSED


class DapStreamChannel:
    """
    📡 DAP Stream Channel
    
    Represents a channel within a stream for organized data flow.
    """
    
    def __init__(self, channel_handle: int, channel_id: int, stream: 'DapStream'):
        """Initialize stream channel"""
        self._channel_handle = channel_handle
        self._channel_id = channel_id
        self._stream = stream
        self._logger = logging.getLogger(__name__)
    
    def write(self, data: bytes) -> int:
        """Write data to channel"""
        try:
            bytes_written = dap_stream_ch_write(
                self._channel_handle, data, len(data)
            )
            return bytes_written
        except Exception as e:
            raise DapStreamError(f"Channel write failed: {e}")
    
    def read(self, max_size: int = 1024) -> Optional[bytes]:
        """Read data from channel"""
        try:
            buffer = bytearray(max_size)
            bytes_read = dap_stream_ch_read(
                self._channel_handle, buffer, max_size
            )
            return bytes(buffer[:bytes_read]) if bytes_read > 0 else None
        except Exception as e:
            self._logger.error(f"Channel read failed: {e}")
            return None
    
    def set_ready_to_read(self, ready: bool) -> None:
        """Set channel ready to read state"""
        dap_stream_ch_set_ready_to_read(self._channel_handle, ready)
    
    def set_ready_to_write(self, ready: bool) -> None:
        """Set channel ready to write state"""
        dap_stream_ch_set_ready_to_write(self._channel_handle, ready)
    
    @property
    def id(self) -> int:
        """Get channel ID"""
        return self._channel_id
    
    @property
    def handle(self) -> int:
        """Get channel handle"""
        return self._channel_handle


class DapStreamWorker:
    """
    👷 DAP Stream Worker
    
    Handles multiple streams in separate thread for performance.
    """
    
    _workers_registry: Dict[int, 'DapStreamWorker'] = {}
    _lock = threading.Lock()
    
    def __init__(self, worker_handle: int, name: str = "", owns_handle: bool = True):
        """Initialize stream worker"""
        self._worker_handle = worker_handle
        self._name = name
        self._owns_handle = owns_handle
        self._logger = logging.getLogger(__name__)
        
        if not worker_handle:
            raise DapStreamError("Invalid worker handle provided")
        
        with self._lock:
            self._workers_registry[worker_handle] = self
    
    @classmethod
    def create_worker(cls, name: str) -> 'DapStreamWorker':
        """Create new stream worker"""
        try:
            worker_handle = dap_stream_worker_new(name)
            if not worker_handle:
                raise DapStreamError(f"Failed to create worker {name}")
            return cls(worker_handle, name)
        except Exception as e:
            raise DapStreamError(f"Worker creation failed: {e}")
    
    def add_stream(self, stream: 'DapStream') -> bool:
        """Add stream to worker"""
        try:
            result = dap_stream_worker_add_stream(
                self._worker_handle, stream.handle
            )
            return result == 0
        except Exception as e:
            self._logger.error(f"Failed to add stream to worker: {e}")
            return False
    
    def remove_stream(self, stream: 'DapStream') -> bool:
        """Remove stream from worker"""
        try:
            result = dap_stream_worker_remove_stream(
                self._worker_handle, stream.handle
            )
            return result == 0
        except Exception as e:
            self._logger.error(f"Failed to remove stream from worker: {e}")
            return False
    
    def get_stream_count(self) -> int:
        """Get number of streams handled by worker"""
        try:
            return dap_stream_worker_get_count(self._worker_handle)
        except Exception as e:
            self._logger.error(f"Failed to get stream count: {e}")
            return 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get worker statistics"""
        try:
            return dap_stream_worker_get_stats(self._worker_handle)
        except Exception as e:
            self._logger.error(f"Failed to get worker stats: {e}")
            return {}
    
    def delete(self) -> None:
        """Delete worker"""
        if self._owns_handle and self._worker_handle:
            try:
                with self._lock:
                    self._workers_registry.pop(self._worker_handle, None)
                dap_stream_worker_delete(self._worker_handle)
                self._worker_handle = None
            except Exception as e:
                self._logger.error(f"Failed to delete worker: {e}")
    
    @property
    def handle(self) -> int:
        """Get worker handle"""
        return self._worker_handle
    
    @property
    def name(self) -> str:
        """Get worker name"""
        return self._name


class DapStream:
    """
    🌊 DAP Stream with proper dap_stream_t* wrapping
    
    Manages streaming data operations with proper C structure integration.
    Supports channels, workers and callback management.
    
    Example:
        # Create and connect stream
        stream = DapStream.create_stream()
        stream.connect_to("192.168.1.100", 8888)
        
        # Set callbacks
        def on_data_received(data):
            print(f"Received: {data}")
        stream.set_read_callback(on_data_received)
        
        # Create channel for organized data flow
        channel = stream.create_channel(1)
        channel.write(b"channel data")
        
        # Write direct stream data
        stream.write_data(b"stream data")
        
        # Read data
        data = stream.read_data()
    """
    
    _streams_registry: Dict[int, 'DapStream'] = {}
    _lock = threading.Lock()
    _system_initialized = False
    
    def __init__(self, stream_handle: int, owns_handle: bool = True):
        """
        Initialize DapStream wrapper
        
        Args:
            stream_handle: Native dap_stream_t* handle
            owns_handle: Whether this instance owns the handle (for cleanup)
        """
        self._stream_handle = stream_handle
        self._owns_handle = owns_handle
        self._logger = logging.getLogger(__name__)
        self._callbacks = {}  # Store Python callbacks
        self._channels = {}  # Track channels
        
        if not stream_handle:
            raise DapStreamError("Invalid stream handle provided")
        
        # Ensure system is initialized
        self._ensure_system_initialized()
        
        # Register in global registry for tracking
        with self._lock:
            self._streams_registry[stream_handle] = self
            
        self._logger.debug(f"DapStream created with handle {stream_handle}")
    
    @classmethod
    def _ensure_system_initialized(cls):
        """Ensure DAP stream system is initialized"""
        if not cls._system_initialized:
            with cls._lock:
                if not cls._system_initialized:
                    try:
                        result = dap_stream_init(None)  # Default config
                        if result != 0:
                            raise DapStreamError(f"Stream system initialization failed with code {result}")
                        cls._system_initialized = True
                        logging.getLogger(__name__).info("DAP stream system initialized")
                    except Exception as e:
                        raise DapStreamError(f"Stream system initialization failed: {e}")
    
    @classmethod
    def create_stream(cls) -> 'DapStream':
        """
        Create new stream
        
        Returns:
            New DapStream instance
            
        Raises:
            DapStreamError: If stream creation fails
        """
        try:
            # Call C function: dap_stream_new()
            stream_handle = dap_stream_new()
            
            if not stream_handle:
                raise DapStreamError("Failed to create new stream")
            
            logging.getLogger(__name__).info("New DAP stream created")
            
            return cls(stream_handle)
            
        except Exception as e:
            raise DapStreamError(f"Stream creation failed: {e}")
    
    def connect_to(self, address: str, port: int) -> bool:
        """
        Connect stream to remote address
        
        Args:
            address: Target address
            port: Target port
            
        Returns:
            True if connection successful
        """
        try:
            # Call C function: dap_stream_open()
            result = dap_stream_open(self._stream_handle, address, port)
            
            if result == 0:
                self._logger.info(f"Stream connected to {address}:{port}")
                return True
            else:
                self._logger.error(f"Failed to connect stream to {address}:{port}")
                return False
                
        except Exception as e:
            raise DapStreamError(f"Stream connection failed: {e}")
    
    def close(self) -> bool:
        """
        Close stream
        
        Returns:
            True if close successful
        """
        try:
            # Call C function: dap_stream_close()
            result = dap_stream_close(self._stream_handle)
            
            if result == 0:
                self._logger.info("Stream closed")
                return True
            else:
                self._logger.error("Failed to close stream")
                return False
                
        except Exception as e:
            self._logger.error(f"Stream close failed: {e}")
            return False
    
    def write_data(self, data: bytes) -> int:
        """
        Write data to stream
        
        Args:
            data: Data to write
            
        Returns:
            Number of bytes written
        """
        try:
            # Call C function: dap_stream_write()
            bytes_written = dap_stream_write(
                self._stream_handle, data, len(data)
            )
            
            self._logger.debug(f"Wrote {bytes_written} bytes to stream")
            return bytes_written
            
        except Exception as e:
            raise DapStreamError(f"Stream write failed: {e}")
    
    def read_data(self, max_size: int = 1024) -> Optional[bytes]:
        """
        Read data from stream
        
        Args:
            max_size: Maximum bytes to read
            
        Returns:
            Read data or None if no data available
        """
        try:
            # Prepare buffer
            buffer = bytearray(max_size)
            
            # Call C function: dap_stream_read()
            bytes_read = dap_stream_read(
                self._stream_handle, buffer, max_size
            )
            
            if bytes_read > 0:
                self._logger.debug(f"Read {bytes_read} bytes from stream")
                return bytes(buffer[:bytes_read])
            else:
                return None
                
        except Exception as e:
            self._logger.error(f"Stream read failed: {e}")
            return None
    
    def get_stream_id(self) -> int:
        """Get stream ID"""
        try:
            return dap_stream_get_id(self._stream_handle)
        except Exception as e:
            self._logger.error(f"Failed to get stream ID: {e}")
            return 0
    
    def get_remote_address(self) -> Optional[str]:
        """Get remote address"""
        try:
            return dap_stream_get_remote_addr(self._stream_handle)
        except Exception as e:
            self._logger.error(f"Failed to get remote address: {e}")
            return None
    
    def get_remote_port(self) -> int:
        """Get remote port"""
        try:
            return dap_stream_get_remote_port(self._stream_handle)
        except Exception as e:
            self._logger.error(f"Failed to get remote port: {e}")
            return 0
    
    def set_callbacks(self,
                     read_callback: Optional[Callable] = None,
                     write_callback: Optional[Callable] = None,
                     error_callback: Optional[Callable] = None) -> None:
        """
        Set stream event callbacks
        
        Args:
            read_callback: Called when data is available to read
            write_callback: Called when stream is ready to write
            error_callback: Called on stream error
        """
        try:
            # Store callbacks
            if read_callback:
                self._callbacks['read'] = read_callback
            if write_callback:
                self._callbacks['write'] = write_callback
            if error_callback:
                self._callbacks['error'] = error_callback
            
            # Call C function: dap_stream_set_callbacks()
            dap_stream_set_callbacks(
                self._stream_handle,
                read_callback,
                write_callback,
                error_callback
            )
            
        except Exception as e:
            self._logger.error(f"Failed to set callbacks: {e}")
    
    def set_read_callback(self, callback: Callable) -> None:
        """Set read callback"""
        self.set_callbacks(read_callback=callback)
    
    def set_write_callback(self, callback: Callable) -> None:
        """Set write callback"""
        self.set_callbacks(write_callback=callback)
    
    def set_error_callback(self, callback: Callable) -> None:
        """Set error callback"""
        self.set_callbacks(error_callback=callback)
    
    def create_channel(self, channel_id: int) -> Optional[DapStreamChannel]:
        """
        Create new channel within stream
        
        Args:
            channel_id: Unique channel identifier
            
        Returns:
            DapStreamChannel instance if successful
        """
        try:
            # Call C function: dap_stream_ch_new()
            channel_handle = dap_stream_ch_new(self._stream_handle, channel_id)
            
            if channel_handle:
                channel = DapStreamChannel(channel_handle, channel_id, self)
                self._channels[channel_id] = channel
                self._logger.debug(f"Created channel {channel_id}")
                return channel
            else:
                return None
                
        except Exception as e:
            raise DapStreamError(f"Channel creation failed: {e}")
    
    def get_channel(self, channel_id: int) -> Optional[DapStreamChannel]:
        """Get existing channel by ID"""
        return self._channels.get(channel_id)
    
    def delete_channel(self, channel_id: int) -> bool:
        """
        Delete channel
        
        Args:
            channel_id: Channel ID to delete
            
        Returns:
            True if deleted successfully
        """
        try:
            channel = self._channels.pop(channel_id, None)
            if channel:
                # Call C function: dap_stream_ch_delete()
                dap_stream_ch_delete(channel.handle)
                self._logger.debug(f"Deleted channel {channel_id}")
                return True
            else:
                return False
                
        except Exception as e:
            self._logger.error(f"Failed to delete channel {channel_id}: {e}")
            return False
    
    def delete(self) -> None:
        """Delete stream and cleanup resources"""
        if self._owns_handle and self._stream_handle:
            try:
                # Close stream first
                self.close()
                
                # Delete all channels
                for channel_id in list(self._channels.keys()):
                    self.delete_channel(channel_id)
                
                # Remove from registry
                with self._lock:
                    self._streams_registry.pop(self._stream_handle, None)
                
                # Call C function: dap_stream_delete()
                dap_stream_delete(self._stream_handle)
                
                self._logger.debug(f"Stream {self._stream_handle} deleted")
                self._stream_handle = None
                self._callbacks.clear()
                
            except Exception as e:
                self._logger.error(f"Failed to delete stream: {e}")
    
    @property
    def handle(self) -> int:
        """Get native stream handle"""
        return self._stream_handle
    
    @property
    def is_valid(self) -> bool:
        """Check if stream handle is valid"""
        return self._stream_handle and self._stream_handle in self._streams_registry
    
    @property
    def channels_count(self) -> int:
        """Get number of channels"""
        return len(self._channels)
    
    def __enter__(self) -> 'DapStream':
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - cleanup stream"""
        self.delete()
    
    def __del__(self):
        """Destructor - ensure cleanup"""
        if hasattr(self, '_owns_handle') and self._owns_handle:
            try:
                self.delete()
            except:
                pass  # Ignore errors in destructor
    
    def __repr__(self) -> str:
        stream_id = self.get_stream_id()
        remote_addr = self.get_remote_address()
        remote_port = self.get_remote_port()
        return f"DapStream(handle={self._stream_handle}, id={stream_id}, remote={remote_addr}:{remote_port}, channels={self.channels_count})"


class DapStreamManager:
    """
    📁 Stream Management System
    
    Provides high-level stream and worker management operations.
    """
    
    @staticmethod
    def get_all_streams() -> List[DapStream]:
        """Get all streams from system"""
        try:
            stream_list = dap_stream_get_all()
            streams = []
            for stream_handle in stream_list:
                if stream_handle:
                    stream = DapStream(stream_handle, owns_handle=False)
                    streams.append(stream)
            return streams
        except Exception as e:
            logging.getLogger(__name__).error(f"Failed to get all streams: {e}")
            return []
    
    @staticmethod
    def initialize_control(workers: int = 32) -> bool:
        """Initialize stream control with workers"""
        try:
            result = dap_stream_ctl_init_py(workers)
            if result == 0:
                logging.getLogger(__name__).info(f"Stream control initialized with {workers} workers")
                return True
            else:
                return False
        except Exception as e:
            logging.getLogger(__name__).error(f"Stream control initialization failed: {e}")
            return False
    
    @staticmethod
    def deinitialize_control() -> None:
        """Deinitialize stream control"""
        try:
            dap_stream_ctl_deinit()
            logging.getLogger(__name__).info("Stream control deinitialized")
        except Exception as e:
            logging.getLogger(__name__).error(f"Stream control deinitialization failed: {e}")
    
    @staticmethod
    def deinitialize_system() -> None:
        """Deinitialize stream system"""
        try:
            dap_stream_deinit()
            DapStream._system_initialized = False
            logging.getLogger(__name__).info("DAP stream system deinitialized")
        except Exception as e:
            logging.getLogger(__name__).error(f"Stream system deinitialization failed: {e}")


# Convenience functions
def create_stream() -> DapStream:
    """Create new stream with default settings"""
    return DapStream.create_stream()


def create_stream_worker(name: str) -> DapStreamWorker:
    """Create new stream worker"""
    return DapStreamWorker.create_worker(name)


def connect_stream(address: str, port: int) -> DapStream:
    """Create stream and connect to address"""
    stream = DapStream.create_stream()
    if stream.connect_to(address, port):
        return stream
    else:
        stream.delete()
        raise DapStreamError(f"Failed to connect to {address}:{port}")


__all__ = [
    'DapStream',
    'DapStreamError',
    'DapStreamState',
    'DapStreamChannel',
    'DapStreamWorker',
    'DapStreamManager',
    'create_stream',
    'create_stream_worker',
    'connect_stream'
] 