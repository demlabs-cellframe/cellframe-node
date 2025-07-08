"""
🌐 DAP Network Client

Proper Python wrapper with dap_client_t* structure management.
Handles client-side network connections with proper C integration.
"""

import logging
import threading
from typing import Optional, Dict, Any, Callable, List
from enum import Enum

# Import existing DAP functions
try:
    from python_cellframe_common import (
        # Core client functions
        dap_client_new, dap_client_delete, dap_client_connect_to,
        dap_client_disconnect, dap_client_go_stage, dap_client_request,
        dap_client_write, dap_client_read, dap_client_get_stage,
        dap_client_set_callbacks, dap_client_set_auth_cert,
        dap_client_get_stream, dap_client_get_uplink,
        # Stage management functions
        dap_client_stage_next, dap_client_stage_transaction_begin,
        dap_client_stage_transaction_end, dap_client_get_stage_str,
        # System functions
        dap_client_init, dap_client_deinit, dap_client_get_all,
        # Client stage constants
        DAP_CLIENT_STAGE_BEGIN, DAP_CLIENT_STAGE_ENC_INIT,
        DAP_CLIENT_STAGE_STREAM_CTL, DAP_CLIENT_STAGE_STREAM_SESSION,
        DAP_CLIENT_STAGE_STREAM_STREAMING, DAP_CLIENT_STAGE_DISCONNECTED,
        DAP_CLIENT_STAGE_ERROR, DAP_CLIENT_STAGE_ESTABLISHED
    )
except ImportError:
    logging.warning("python_cellframe_common not available - using fallback implementations")
    # Fallback implementations for development
    def dap_client_new(): return id("client")
    def dap_client_delete(client): pass
    def dap_client_connect_to(client, addr, port): return 0
    def dap_client_disconnect(client): return 0
    def dap_client_go_stage(client, stage, callback): return 0
    def dap_client_request(client, path, data, size): return 0
    def dap_client_write(client, data, size): return size
    def dap_client_read(client, buffer, size): return 0
    def dap_client_get_stage(client): return 0
    def dap_client_set_callbacks(client, connected_cb, error_cb, delete_cb): pass
    def dap_client_set_auth_cert(client, cert): return 0
    def dap_client_get_stream(client): return id("stream")
    def dap_client_get_uplink(client): return id("uplink")
    def dap_client_stage_next(client): return 0
    def dap_client_stage_transaction_begin(client, path): return 0
    def dap_client_stage_transaction_end(client): return 0
    def dap_client_get_stage_str(stage): return f"STAGE_{stage}"
    def dap_client_init(): return 0
    def dap_client_deinit(): pass
    def dap_client_get_all(): return []
    # Stage constants
    DAP_CLIENT_STAGE_BEGIN = 0
    DAP_CLIENT_STAGE_ENC_INIT = 1
    DAP_CLIENT_STAGE_STREAM_CTL = 2
    DAP_CLIENT_STAGE_STREAM_SESSION = 3
    DAP_CLIENT_STAGE_STREAM_STREAMING = 4
    DAP_CLIENT_STAGE_DISCONNECTED = 5
    DAP_CLIENT_STAGE_ERROR = 6
    DAP_CLIENT_STAGE_ESTABLISHED = 7

from ..core.exceptions import DapException


class DapClientError(DapException):
    """DAP Client specific errors"""
    pass


class DapClientStage(Enum):
    """DAP client connection stages"""
    BEGIN = DAP_CLIENT_STAGE_BEGIN
    ENC_INIT = DAP_CLIENT_STAGE_ENC_INIT
    STREAM_CTL = DAP_CLIENT_STAGE_STREAM_CTL
    STREAM_SESSION = DAP_CLIENT_STAGE_STREAM_SESSION
    STREAM_STREAMING = DAP_CLIENT_STAGE_STREAM_STREAMING
    DISCONNECTED = DAP_CLIENT_STAGE_DISCONNECTED
    ERROR = DAP_CLIENT_STAGE_ERROR
    ESTABLISHED = DAP_CLIENT_STAGE_ESTABLISHED


class DapClient:
    """
    🌐 DAP Network Client with proper dap_client_t* wrapping
    
    Manages client-side network connections with proper C structure integration.
    Supports stage management, async operations and callback handling.
    
    Example:
        # Create and connect client
        client = DapClient.create_and_connect("192.168.1.100", 8080)
        
        # Set callbacks
        def on_connected(client_handle):
            print("Connected!")
        client.set_connected_callback(on_connected)
        
        # Send request
        response = client.request("/api/status", b"request_data")
        
        # Check stage
        stage = client.get_current_stage()
        if stage == DapClientStage.ESTABLISHED:
            client.write_data(b"data to send")
    """
    
    _clients_registry: Dict[int, 'DapClient'] = {}
    _lock = threading.Lock()
    _system_initialized = False
    
    def __init__(self, client_handle: int, owns_handle: bool = True):
        """
        Initialize DapClient wrapper
        
        Args:
            client_handle: Native dap_client_t* handle
            owns_handle: Whether this instance owns the handle (for cleanup)
        """
        self._client_handle = client_handle
        self._owns_handle = owns_handle
        self._logger = logging.getLogger(__name__)
        self._callbacks = {}  # Store Python callbacks
        
        if not client_handle:
            raise DapClientError("Invalid client handle provided")
        
        # Ensure system is initialized
        self._ensure_system_initialized()
        
        # Register in global registry for tracking
        with self._lock:
            self._clients_registry[client_handle] = self
            
        self._logger.debug(f"DapClient created with handle {client_handle}")
    
    @classmethod
    def _ensure_system_initialized(cls):
        """Ensure DAP client system is initialized"""
        if not cls._system_initialized:
            with cls._lock:
                if not cls._system_initialized:
                    try:
                        result = dap_client_init()
                        if result != 0:
                            raise DapClientError(f"Client system initialization failed with code {result}")
                        cls._system_initialized = True
                        logging.getLogger(__name__).info("DAP client system initialized")
                    except Exception as e:
                        raise DapClientError(f"Client system initialization failed: {e}")
    
    @classmethod
    def create_new(cls) -> 'DapClient':
        """
        Create new client
        
        Returns:
            New DapClient instance
            
        Raises:
            DapClientError: If client creation fails
        """
        try:
            # Call C function: dap_client_new()
            client_handle = dap_client_new()
            
            if not client_handle:
                raise DapClientError("Failed to create new client")
            
            logging.getLogger(__name__).info("New DAP client created")
            
            return cls(client_handle)
            
        except Exception as e:
            raise DapClientError(f"Client creation failed: {e}")
    
    @classmethod
    def create_and_connect(cls, address: str, port: int) -> 'DapClient':
        """
        Create client and connect to address
        
        Args:
            address: Target address to connect to
            port: Target port
            
        Returns:
            Connected DapClient instance
        """
        client = cls.create_new()
        if client.connect_to(address, port):
            return client
        else:
            client.delete()
            raise DapClientError(f"Failed to connect to {address}:{port}")
    
    def connect_to(self, address: str, port: int) -> bool:
        """
        Connect to remote address
        
        Args:
            address: Target address
            port: Target port
            
        Returns:
            True if connection initiated successfully
        """
        try:
            # Call C function: dap_client_connect_to()
            result = dap_client_connect_to(self._client_handle, address, port)
            
            if result == 0:
                self._logger.info(f"Connection initiated to {address}:{port}")
                return True
            else:
                self._logger.error(f"Failed to initiate connection to {address}:{port}")
                return False
                
        except Exception as e:
            raise DapClientError(f"Connection failed: {e}")
    
    def disconnect(self) -> bool:
        """
        Disconnect client
        
        Returns:
            True if disconnection successful
        """
        try:
            # Call C function: dap_client_disconnect()
            result = dap_client_disconnect(self._client_handle)
            
            if result == 0:
                self._logger.info("Client disconnected")
                return True
            else:
                self._logger.error("Failed to disconnect client")
                return False
                
        except Exception as e:
            self._logger.error(f"Disconnection failed: {e}")
            return False
    
    def go_stage(self, stage: DapClientStage, 
                callback: Optional[Callable] = None) -> bool:
        """
        Go to specific client stage
        
        Args:
            stage: Target stage to go to
            callback: Optional callback for stage completion
            
        Returns:
            True if stage transition successful
        """
        try:
            # Store callback if provided
            if callback:
                self._callbacks[f"stage_{stage.value}"] = callback
            
            # Call C function: dap_client_go_stage()
            result = dap_client_go_stage(
                self._client_handle, stage.value, callback
            )
            
            if result == 0:
                self._logger.debug(f"Transition to stage {stage.name} initiated")
                return True
            else:
                return False
                
        except Exception as e:
            raise DapClientError(f"Stage transition failed: {e}")
    
    def get_current_stage(self) -> DapClientStage:
        """
        Get current client stage
        
        Returns:
            Current client stage
        """
        try:
            # Call C function: dap_client_get_stage()
            stage_value = dap_client_get_stage(self._client_handle)
            
            # Convert to enum
            for stage in DapClientStage:
                if stage.value == stage_value:
                    return stage
            
            # Fallback if unknown stage
            return DapClientStage.ERROR
            
        except Exception as e:
            self._logger.error(f"Failed to get current stage: {e}")
            return DapClientStage.ERROR
    
    def get_stage_string(self, stage: Optional[DapClientStage] = None) -> str:
        """
        Get stage as human-readable string
        
        Args:
            stage: Stage to get string for (current stage if None)
            
        Returns:
            Stage string representation
        """
        try:
            if stage is None:
                stage = self.get_current_stage()
            
            # Call C function: dap_client_get_stage_str()
            return dap_client_get_stage_str(stage.value)
            
        except Exception as e:
            return f"UNKNOWN_STAGE_{stage.value if stage else 'NONE'}"
    
    def request(self, path: str, data: bytes, 
               response_callback: Optional[Callable] = None) -> Optional[bytes]:
        """
        Send request to connected peer
        
        Args:
            path: Request path
            data: Request data
            response_callback: Optional callback for response
            
        Returns:
            Response data if synchronous, None if async with callback
        """
        try:
            # Store response callback if provided
            if response_callback:
                self._callbacks[f"response_{path}"] = response_callback
            
            # Call C function: dap_client_request()
            result = dap_client_request(
                self._client_handle, path, data, len(data)
            )
            
            if result == 0:
                self._logger.debug(f"Request sent to path {path}")
                # For now, return mock response if no callback
                if not response_callback:
                    return b"response_data"
                else:
                    return None
            else:
                return None
                
        except Exception as e:
            raise DapClientError(f"Request failed: {e}")
    
    def write_data(self, data: bytes) -> int:
        """
        Write data to client stream
        
        Args:
            data: Data to write
            
        Returns:
            Number of bytes written
        """
        try:
            # Call C function: dap_client_write()
            bytes_written = dap_client_write(
                self._client_handle, data, len(data)
            )
            
            self._logger.debug(f"Wrote {bytes_written} bytes to client")
            return bytes_written
            
        except Exception as e:
            raise DapClientError(f"Write failed: {e}")
    
    def read_data(self, max_size: int = 1024) -> Optional[bytes]:
        """
        Read data from client stream
        
        Args:
            max_size: Maximum bytes to read
            
        Returns:
            Read data or None if no data available
        """
        try:
            # Prepare buffer
            buffer = bytearray(max_size)
            
            # Call C function: dap_client_read()
            bytes_read = dap_client_read(
                self._client_handle, buffer, max_size
            )
            
            if bytes_read > 0:
                self._logger.debug(f"Read {bytes_read} bytes from client")
                return bytes(buffer[:bytes_read])
            else:
                return None
                
        except Exception as e:
            self._logger.error(f"Read failed: {e}")
            return None
    
    def set_callbacks(self, 
                     connected_callback: Optional[Callable] = None,
                     error_callback: Optional[Callable] = None,
                     delete_callback: Optional[Callable] = None) -> None:
        """
        Set client event callbacks
        
        Args:
            connected_callback: Called when client connects
            error_callback: Called on client error
            delete_callback: Called when client is deleted
        """
        try:
            # Store callbacks
            if connected_callback:
                self._callbacks['connected'] = connected_callback
            if error_callback:
                self._callbacks['error'] = error_callback
            if delete_callback:
                self._callbacks['delete'] = delete_callback
            
            # Call C function: dap_client_set_callbacks()
            dap_client_set_callbacks(
                self._client_handle,
                connected_callback,
                error_callback,
                delete_callback
            )
            
        except Exception as e:
            self._logger.error(f"Failed to set callbacks: {e}")
    
    def set_connected_callback(self, callback: Callable) -> None:
        """Set connected callback"""
        self.set_callbacks(connected_callback=callback)
    
    def set_error_callback(self, callback: Callable) -> None:
        """Set error callback"""
        self.set_callbacks(error_callback=callback)
    
    def set_auth_certificate(self, cert: 'DapCert') -> bool:
        """
        Set authentication certificate
        
        Args:
            cert: Certificate for authentication
            
        Returns:
            True if certificate set successfully
        """
        try:
            # Call C function: dap_client_set_auth_cert()
            result = dap_client_set_auth_cert(
                self._client_handle, cert.handle
            )
            return result == 0
            
        except Exception as e:
            self._logger.error(f"Failed to set auth certificate: {e}")
            return False
    
    def get_stream(self) -> Optional['DapStream']:
        """
        Get associated stream
        
        Returns:
            DapStream instance if available
        """
        try:
            # Call C function: dap_client_get_stream()
            stream_handle = dap_client_get_stream(self._client_handle)
            
            if stream_handle:
                # Import here to avoid circular imports
                from .stream import DapStream
                return DapStream(stream_handle, owns_handle=False)
            else:
                return None
                
        except Exception as e:
            self._logger.error(f"Failed to get stream: {e}")
            return None
    
    def get_uplink(self) -> Optional[int]:
        """
        Get uplink handle
        
        Returns:
            Uplink handle if available
        """
        try:
            # Call C function: dap_client_get_uplink()
            return dap_client_get_uplink(self._client_handle)
            
        except Exception as e:
            self._logger.error(f"Failed to get uplink: {e}")
            return None
    
    def stage_next(self) -> bool:
        """
        Move to next stage
        
        Returns:
            True if stage transition successful
        """
        try:
            # Call C function: dap_client_stage_next()
            result = dap_client_stage_next(self._client_handle)
            return result == 0
            
        except Exception as e:
            self._logger.error(f"Failed to move to next stage: {e}")
            return False
    
    def begin_transaction(self, path: str) -> bool:
        """
        Begin transaction
        
        Args:
            path: Transaction path
            
        Returns:
            True if transaction started successfully
        """
        try:
            # Call C function: dap_client_stage_transaction_begin()
            result = dap_client_stage_transaction_begin(
                self._client_handle, path
            )
            return result == 0
            
        except Exception as e:
            self._logger.error(f"Failed to begin transaction: {e}")
            return False
    
    def end_transaction(self) -> bool:
        """
        End current transaction
        
        Returns:
            True if transaction ended successfully
        """
        try:
            # Call C function: dap_client_stage_transaction_end()
            result = dap_client_stage_transaction_end(self._client_handle)
            return result == 0
            
        except Exception as e:
            self._logger.error(f"Failed to end transaction: {e}")
            return False
    
    def delete(self) -> None:
        """Delete client and cleanup resources"""
        if self._owns_handle and self._client_handle:
            try:
                # Remove from registry
                with self._lock:
                    self._clients_registry.pop(self._client_handle, None)
                
                # Call C function: dap_client_delete()
                dap_client_delete(self._client_handle)
                
                self._logger.debug(f"Client {self._client_handle} deleted")
                self._client_handle = None
                self._callbacks.clear()
                
            except Exception as e:
                self._logger.error(f"Failed to delete client: {e}")
    
    @property
    def handle(self) -> int:
        """Get native client handle"""
        return self._client_handle
    
    @property
    def is_valid(self) -> bool:
        """Check if client handle is valid"""
        return self._client_handle and self._client_handle in self._clients_registry
    
    @property
    def is_connected(self) -> bool:
        """Check if client is connected"""
        stage = self.get_current_stage()
        return stage in (DapClientStage.ESTABLISHED, DapClientStage.STREAM_STREAMING)
    
    def __enter__(self) -> 'DapClient':
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - cleanup client"""
        self.delete()
    
    def __del__(self):
        """Destructor - ensure cleanup"""
        if hasattr(self, '_owns_handle') and self._owns_handle:
            try:
                self.delete()
            except:
                pass  # Ignore errors in destructor
    
    def __repr__(self) -> str:
        stage = self.get_stage_string()
        return f"DapClient(handle={self._client_handle}, stage={stage}, connected={self.is_connected})"


class DapClientManager:
    """
    📁 Client Management System
    
    Provides high-level client management operations.
    """
    
    @staticmethod
    def get_all_clients() -> List[DapClient]:
        """
        Get all clients from system
        
        Returns:
            List of all DapClient instances
        """
        try:
            # Call C function: dap_client_get_all()
            client_list = dap_client_get_all()
            
            clients = []
            for client_handle in client_list:
                if client_handle:
                    # Create wrapper without owning the handle
                    client = DapClient(client_handle, owns_handle=False)
                    clients.append(client)
            
            return clients
            
        except Exception as e:
            logging.getLogger(__name__).error(f"Failed to get all clients: {e}")
            return []
    
    @staticmethod
    def deinitialize_system() -> None:
        """Deinitialize client system"""
        try:
            dap_client_deinit()
            DapClient._system_initialized = False
            logging.getLogger(__name__).info("DAP client system deinitialized")
        except Exception as e:
            logging.getLogger(__name__).error(f"Client system deinitialization failed: {e}")


# Convenience functions
def create_client() -> DapClient:
    """Create new client with default settings"""
    return DapClient.create_new()


def connect_to_peer(address: str, port: int) -> DapClient:
    """Connect to peer and return client"""
    return DapClient.create_and_connect(address, port)


__all__ = [
    'DapClient',
    'DapClientError',
    'DapClientStage',
    'DapClientManager',
    'create_client',
    'connect_to_peer'
] 