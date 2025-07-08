"""
🌐 DAP Network Server

Proper Python wrapper with dap_server_t* structure management.
Handles server-side network operations with proper C integration.
"""

import logging
import threading
from typing import Optional, Dict, Any, Callable, List
from enum import Enum

# Import existing DAP functions
try:
    from python_cellframe_common import (
        # Core server functions
        dap_server_new, dap_server_delete, dap_server_listen,
        dap_server_stop, dap_server_start, dap_server_add_proc,
        dap_server_get_clients_count, dap_server_get_clients,
        dap_server_client_disconnect, dap_server_set_callbacks,
        # Listener management
        dap_server_add_listener, dap_server_remove_listener,
        dap_server_get_listeners, dap_server_get_listener_port,
        # System functions
        dap_server_init, dap_server_deinit, dap_server_get_all,
        # Configuration
        dap_server_set_auth_required, dap_server_set_ssl_enabled,
        dap_server_set_worker_count, dap_server_get_worker_count,
        # Processing callbacks
        dap_server_proc_http_request, dap_server_proc_stream_request,
        # Server type constants
        DAP_SERVER_TYPE_HTTP, DAP_SERVER_TYPE_JSON_RPC,
        DAP_SERVER_TYPE_TCP, DAP_SERVER_TYPE_WEBSOCKET
    )
except ImportError:
    logging.warning("python_cellframe_common not available - using fallback implementations")
    # Fallback implementations for development
    def dap_server_new(name, type_val): return id(f"server_{name}")
    def dap_server_delete(server): pass
    def dap_server_listen(server, addr, port): return 0
    def dap_server_stop(server): return 0
    def dap_server_start(server): return 0
    def dap_server_add_proc(server, path, callback): return 0
    def dap_server_get_clients_count(server): return 0
    def dap_server_get_clients(server): return []
    def dap_server_client_disconnect(server, client_id): return 0
    def dap_server_set_callbacks(server, new_client_cb, client_disconnect_cb): pass
    def dap_server_add_listener(server, addr, port): return 0
    def dap_server_remove_listener(server, listener_id): return 0
    def dap_server_get_listeners(server): return []
    def dap_server_get_listener_port(listener): return 0
    def dap_server_init(): return 0
    def dap_server_deinit(): pass
    def dap_server_get_all(): return []
    def dap_server_set_auth_required(server, enabled): pass
    def dap_server_set_ssl_enabled(server, enabled): pass
    def dap_server_set_worker_count(server, count): pass
    def dap_server_get_worker_count(server): return 1
    def dap_server_proc_http_request(server, request, response): return 0
    def dap_server_proc_stream_request(server, stream, request): return 0
    # Server type constants
    DAP_SERVER_TYPE_HTTP = 0
    DAP_SERVER_TYPE_JSON_RPC = 1
    DAP_SERVER_TYPE_TCP = 2
    DAP_SERVER_TYPE_WEBSOCKET = 3

from ..core.exceptions import DapException


class DapServerError(DapException):
    """DAP Server specific errors"""
    pass


class DapServerType(Enum):
    """DAP server types"""
    HTTP = DAP_SERVER_TYPE_HTTP
    JSON_RPC = DAP_SERVER_TYPE_JSON_RPC
    TCP = DAP_SERVER_TYPE_TCP
    WEBSOCKET = DAP_SERVER_TYPE_WEBSOCKET


class DapServer:
    """
    🌐 DAP Network Server with proper dap_server_t* wrapping
    
    Manages server-side network operations with proper C structure integration.
    Supports multiple listeners, client management and request processing.
    
    Example:
        # Create HTTP server
        server = DapServer.create_server("web-server", DapServerType.HTTP)
        
        # Add listener
        listener_id = server.add_listener("0.0.0.0", 8080)
        
        # Add request processor
        def handle_status(request, response):
            return b"OK"
        server.add_processor("/status", handle_status)
        
        # Start server
        server.start()
        
        # Check clients
        client_count = server.get_clients_count()
    """
    
    _servers_registry: Dict[int, 'DapServer'] = {}
    _lock = threading.Lock()
    _system_initialized = False
    
    def __init__(self, server_handle: int, name: str = "", owns_handle: bool = True):
        """
        Initialize DapServer wrapper
        
        Args:
            server_handle: Native dap_server_t* handle
            name: Server name
            owns_handle: Whether this instance owns the handle (for cleanup)
        """
        self._server_handle = server_handle
        self._name = name
        self._owns_handle = owns_handle
        self._logger = logging.getLogger(__name__)
        self._callbacks = {}  # Store Python callbacks
        self._processors = {}  # Store request processors
        self._listeners = {}  # Track listeners
        
        if not server_handle:
            raise DapServerError("Invalid server handle provided")
        
        # Ensure system is initialized
        self._ensure_system_initialized()
        
        # Register in global registry for tracking
        with self._lock:
            self._servers_registry[server_handle] = self
            
        self._logger.debug(f"DapServer created with handle {server_handle}, name: {name}")
    
    @classmethod
    def _ensure_system_initialized(cls):
        """Ensure DAP server system is initialized"""
        if not cls._system_initialized:
            with cls._lock:
                if not cls._system_initialized:
                    try:
                        result = dap_server_init()
                        if result != 0:
                            raise DapServerError(f"Server system initialization failed with code {result}")
                        cls._system_initialized = True
                        logging.getLogger(__name__).info("DAP server system initialized")
                    except Exception as e:
                        raise DapServerError(f"Server system initialization failed: {e}")
    
    @classmethod
    def create_server(cls, name: str, server_type: DapServerType) -> 'DapServer':
        """
        Create new server
        
        Args:
            name: Server name
            server_type: Type of server to create
            
        Returns:
            New DapServer instance
            
        Raises:
            DapServerError: If server creation fails
        """
        try:
            # Call C function: dap_server_new()
            server_handle = dap_server_new(name, server_type.value)
            
            if not server_handle:
                raise DapServerError(f"Failed to create server {name}")
            
            logging.getLogger(__name__).info(
                f"Server {name} created with type {server_type.name}"
            )
            
            return cls(server_handle, name)
            
        except Exception as e:
            raise DapServerError(f"Server creation failed: {e}")
    
    @classmethod
    def create_http_server(cls, name: str) -> 'DapServer':
        """Create HTTP server"""
        return cls.create_server(name, DapServerType.HTTP)
    
    @classmethod
    def create_tcp_server(cls, name: str) -> 'DapServer':
        """Create TCP server"""
        return cls.create_server(name, DapServerType.TCP)
    
    @classmethod
    def create_websocket_server(cls, name: str) -> 'DapServer':
        """Create WebSocket server"""
        return cls.create_server(name, DapServerType.WEBSOCKET)
    
    def add_listener(self, address: str, port: int) -> Optional[int]:
        """
        Add listener on address:port
        
        Args:
            address: Address to listen on
            port: Port to listen on
            
        Returns:
            Listener ID if successful, None otherwise
        """
        try:
            # Call C function: dap_server_add_listener()
            listener_id = dap_server_add_listener(
                self._server_handle, address, port
            )
            
            if listener_id:
                # Track listener
                self._listeners[listener_id] = {
                    'address': address,
                    'port': port,
                    'active': True
                }
                
                self._logger.info(f"Listener added on {address}:{port} (ID: {listener_id})")
                return listener_id
            else:
                return None
                
        except Exception as e:
            raise DapServerError(f"Failed to add listener: {e}")
    
    def remove_listener(self, listener_id: int) -> bool:
        """
        Remove listener
        
        Args:
            listener_id: Listener ID to remove
            
        Returns:
            True if removed successfully
        """
        try:
            # Call C function: dap_server_remove_listener()
            result = dap_server_remove_listener(self._server_handle, listener_id)
            
            if result == 0:
                # Remove from tracking
                listener_info = self._listeners.pop(listener_id, {})
                self._logger.info(f"Listener {listener_id} removed")
                return True
            else:
                return False
                
        except Exception as e:
            self._logger.error(f"Failed to remove listener {listener_id}: {e}")
            return False
    
    def get_listeners(self) -> List[Dict[str, Any]]:
        """
        Get all listeners
        
        Returns:
            List of listener information
        """
        try:
            # Call C function: dap_server_get_listeners()
            listener_handles = dap_server_get_listeners(self._server_handle)
            
            listeners = []
            for handle in listener_handles:
                port = dap_server_get_listener_port(handle)
                listener_info = {
                    'handle': handle,
                    'port': port,
                    'address': self._listeners.get(handle, {}).get('address', 'unknown')
                }
                listeners.append(listener_info)
            
            return listeners
            
        except Exception as e:
            self._logger.error(f"Failed to get listeners: {e}")
            return []
    
    def start(self) -> bool:
        """
        Start server
        
        Returns:
            True if started successfully
        """
        try:
            # Call C function: dap_server_start()
            result = dap_server_start(self._server_handle)
            
            if result == 0:
                self._logger.info(f"Server {self._name} started")
                return True
            else:
                self._logger.error(f"Failed to start server {self._name}")
                return False
                
        except Exception as e:
            raise DapServerError(f"Server start failed: {e}")
    
    def stop(self) -> bool:
        """
        Stop server
        
        Returns:
            True if stopped successfully
        """
        try:
            # Call C function: dap_server_stop()
            result = dap_server_stop(self._server_handle)
            
            if result == 0:
                self._logger.info(f"Server {self._name} stopped")
                return True
            else:
                self._logger.error(f"Failed to stop server {self._name}")
                return False
                
        except Exception as e:
            self._logger.error(f"Server stop failed: {e}")
            return False
    
    def add_processor(self, path: str, processor: Callable) -> bool:
        """
        Add request processor for path
        
        Args:
            path: Request path to handle
            processor: Processing function
            
        Returns:
            True if processor added successfully
        """
        try:
            # Store processor
            self._processors[path] = processor
            
            # Call C function: dap_server_add_proc()
            result = dap_server_add_proc(
                self._server_handle, path, processor
            )
            
            if result == 0:
                self._logger.debug(f"Processor added for path {path}")
                return True
            else:
                return False
                
        except Exception as e:
            raise DapServerError(f"Failed to add processor: {e}")
    
    def get_clients_count(self) -> int:
        """
        Get number of connected clients
        
        Returns:
            Number of clients
        """
        try:
            # Call C function: dap_server_get_clients_count()
            return dap_server_get_clients_count(self._server_handle)
            
        except Exception as e:
            self._logger.error(f"Failed to get clients count: {e}")
            return 0
    
    def get_clients(self) -> List[int]:
        """
        Get list of connected client handles
        
        Returns:
            List of client handles
        """
        try:
            # Call C function: dap_server_get_clients()
            return dap_server_get_clients(self._server_handle)
            
        except Exception as e:
            self._logger.error(f"Failed to get clients: {e}")
            return []
    
    def disconnect_client(self, client_handle: int) -> bool:
        """
        Disconnect specific client
        
        Args:
            client_handle: Client handle to disconnect
            
        Returns:
            True if disconnected successfully
        """
        try:
            # Call C function: dap_server_client_disconnect()
            result = dap_server_client_disconnect(
                self._server_handle, client_handle
            )
            
            if result == 0:
                self._logger.info(f"Client {client_handle} disconnected")
                return True
            else:
                return False
                
        except Exception as e:
            self._logger.error(f"Failed to disconnect client {client_handle}: {e}")
            return False
    
    def set_callbacks(self, 
                     new_client_callback: Optional[Callable] = None,
                     client_disconnect_callback: Optional[Callable] = None) -> None:
        """
        Set server event callbacks
        
        Args:
            new_client_callback: Called when new client connects
            client_disconnect_callback: Called when client disconnects
        """
        try:
            # Store callbacks
            if new_client_callback:
                self._callbacks['new_client'] = new_client_callback
            if client_disconnect_callback:
                self._callbacks['client_disconnect'] = client_disconnect_callback
            
            # Call C function: dap_server_set_callbacks()
            dap_server_set_callbacks(
                self._server_handle,
                new_client_callback,
                client_disconnect_callback
            )
            
        except Exception as e:
            self._logger.error(f"Failed to set callbacks: {e}")
    
    def set_new_client_callback(self, callback: Callable) -> None:
        """Set new client callback"""
        self.set_callbacks(new_client_callback=callback)
    
    def set_client_disconnect_callback(self, callback: Callable) -> None:
        """Set client disconnect callback"""
        self.set_callbacks(client_disconnect_callback=callback)
    
    # Configuration methods
    def set_auth_required(self, enabled: bool) -> None:
        """Set whether authentication is required"""
        try:
            dap_server_set_auth_required(self._server_handle, enabled)
            self._logger.debug(f"Authentication required: {enabled}")
        except Exception as e:
            self._logger.error(f"Failed to set auth required: {e}")
    
    def set_ssl_enabled(self, enabled: bool) -> None:
        """Set whether SSL is enabled"""
        try:
            dap_server_set_ssl_enabled(self._server_handle, enabled)
            self._logger.debug(f"SSL enabled: {enabled}")
        except Exception as e:
            self._logger.error(f"Failed to set SSL enabled: {e}")
    
    def set_worker_count(self, count: int) -> None:
        """Set number of worker threads"""
        try:
            dap_server_set_worker_count(self._server_handle, count)
            self._logger.debug(f"Worker count set to: {count}")
        except Exception as e:
            self._logger.error(f"Failed to set worker count: {e}")
    
    def get_worker_count(self) -> int:
        """Get number of worker threads"""
        try:
            return dap_server_get_worker_count(self._server_handle)
        except Exception as e:
            self._logger.error(f"Failed to get worker count: {e}")
            return 1
    
    def process_http_request(self, request: Any, response: Any) -> bool:
        """
        Process HTTP request
        
        Args:
            request: HTTP request object
            response: HTTP response object
            
        Returns:
            True if processed successfully
        """
        try:
            # Call C function: dap_server_proc_http_request()
            result = dap_server_proc_http_request(
                self._server_handle, request, response
            )
            return result == 0
            
        except Exception as e:
            self._logger.error(f"Failed to process HTTP request: {e}")
            return False
    
    def process_stream_request(self, stream: Any, request: Any) -> bool:
        """
        Process stream request
        
        Args:
            stream: Stream object
            request: Request object
            
        Returns:
            True if processed successfully
        """
        try:
            # Call C function: dap_server_proc_stream_request()
            result = dap_server_proc_stream_request(
                self._server_handle, stream, request
            )
            return result == 0
            
        except Exception as e:
            self._logger.error(f"Failed to process stream request: {e}")
            return False
    
    def delete(self) -> None:
        """Delete server and cleanup resources"""
        if self._owns_handle and self._server_handle:
            try:
                # Stop server first
                self.stop()
                
                # Remove from registry
                with self._lock:
                    self._servers_registry.pop(self._server_handle, None)
                
                # Call C function: dap_server_delete()
                dap_server_delete(self._server_handle)
                
                self._logger.debug(f"Server {self._name} deleted")
                self._server_handle = None
                self._callbacks.clear()
                self._processors.clear()
                self._listeners.clear()
                
            except Exception as e:
                self._logger.error(f"Failed to delete server: {e}")
    
    @property
    def handle(self) -> int:
        """Get native server handle"""
        return self._server_handle
    
    @property
    def name(self) -> str:
        """Get server name"""
        return self._name
    
    @property
    def is_valid(self) -> bool:
        """Check if server handle is valid"""
        return self._server_handle and self._server_handle in self._servers_registry
    
    @property
    def listeners_count(self) -> int:
        """Get number of listeners"""
        return len(self._listeners)
    
    def __enter__(self) -> 'DapServer':
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - cleanup server"""
        self.delete()
    
    def __del__(self):
        """Destructor - ensure cleanup"""
        if hasattr(self, '_owns_handle') and self._owns_handle:
            try:
                self.delete()
            except:
                pass  # Ignore errors in destructor
    
    def __repr__(self) -> str:
        return f"DapServer(handle={self._server_handle}, name='{self._name}', clients={self.get_clients_count()}, listeners={self.listeners_count})"


class DapServerManager:
    """
    📁 Server Management System
    
    Provides high-level server management operations.
    """
    
    @staticmethod
    def get_all_servers() -> List[DapServer]:
        """
        Get all servers from system
        
        Returns:
            List of all DapServer instances
        """
        try:
            # Call C function: dap_server_get_all()
            server_list = dap_server_get_all()
            
            servers = []
            for server_handle in server_list:
                if server_handle:
                    # Create wrapper without owning the handle
                    server = DapServer(server_handle, "system_server", owns_handle=False)
                    servers.append(server)
            
            return servers
            
        except Exception as e:
            logging.getLogger(__name__).error(f"Failed to get all servers: {e}")
            return []
    
    @staticmethod
    def deinitialize_system() -> None:
        """Deinitialize server system"""
        try:
            dap_server_deinit()
            DapServer._system_initialized = False
            logging.getLogger(__name__).info("DAP server system deinitialized")
        except Exception as e:
            logging.getLogger(__name__).error(f"Server system deinitialization failed: {e}")


# Convenience functions
def create_http_server(name: str, address: str = "0.0.0.0", port: int = 8080) -> DapServer:
    """Create HTTP server with default listener"""
    server = DapServer.create_http_server(name)
    server.add_listener(address, port)
    return server


def create_tcp_server(name: str, address: str = "0.0.0.0", port: int = 8888) -> DapServer:
    """Create TCP server with default listener"""
    server = DapServer.create_tcp_server(name)
    server.add_listener(address, port)
    return server


def create_websocket_server(name: str, address: str = "0.0.0.0", port: int = 8081) -> DapServer:
    """Create WebSocket server with default listener"""
    server = DapServer.create_websocket_server(name)
    server.add_listener(address, port)
    return server


__all__ = [
    'DapServer',
    'DapServerError',
    'DapServerType',
    'DapServerManager',
    'create_http_server',
    'create_tcp_server',
    'create_websocket_server'
] 