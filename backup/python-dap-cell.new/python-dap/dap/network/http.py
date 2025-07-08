"""
🌐 DAP HTTP Client

Proper Python wrapper with HTTP session management.
Handles HTTP requests, responses and session state.
"""

import logging
import threading
from typing import Optional, Dict, Any, Union, List
from enum import Enum

# Import existing DAP functions
try:
    from python_cellframe_common import (
        # HTTP client functions
        dap_http_client_new, dap_http_client_delete,
        dap_http_client_request, dap_http_client_request_ex,
        dap_http_client_set_headers, dap_http_client_set_timeout,
        dap_http_client_get_response_code, dap_http_client_get_response_size,
        dap_http_client_get_response_data, dap_http_client_get_response_headers,
        # HTTP request functions
        dap_http_request_new, dap_http_request_delete,
        dap_http_request_add_header, dap_http_request_set_body,
        dap_http_request_set_method, dap_http_request_set_url,
        # HTTP response functions
        dap_http_response_new, dap_http_response_delete,
        dap_http_response_get_code, dap_http_response_get_data,
        dap_http_response_get_headers, dap_http_response_get_header,
        # System functions
        dap_http_client_init, dap_http_client_deinit,
        dap_http_simple_request, dap_http_get_all_clients,
        # HTTP method constants
        DAP_HTTP_METHOD_GET, DAP_HTTP_METHOD_POST,
        DAP_HTTP_METHOD_PUT, DAP_HTTP_METHOD_DELETE,
        DAP_HTTP_METHOD_HEAD, DAP_HTTP_METHOD_OPTIONS
    )
except ImportError:
    logging.warning("python_cellframe_common not available - using fallback implementations")
    # Fallback implementations for development
    def dap_http_client_new(): return id("http_client")
    def dap_http_client_delete(client): pass
    def dap_http_client_request(client, request): return id("response")
    def dap_http_client_request_ex(client, method, url, headers, body): return id("response")
    def dap_http_client_set_headers(client, headers): pass
    def dap_http_client_set_timeout(client, timeout): pass
    def dap_http_client_get_response_code(client): return 200
    def dap_http_client_get_response_size(client): return 0
    def dap_http_client_get_response_data(client): return b"response_data"
    def dap_http_client_get_response_headers(client): return {}
    def dap_http_request_new(): return id("request")
    def dap_http_request_delete(request): pass
    def dap_http_request_add_header(request, key, value): pass
    def dap_http_request_set_body(request, body, size): pass
    def dap_http_request_set_method(request, method): pass
    def dap_http_request_set_url(request, url): pass
    def dap_http_response_new(): return id("response")
    def dap_http_response_delete(response): pass
    def dap_http_response_get_code(response): return 200
    def dap_http_response_get_data(response): return b"response_data"
    def dap_http_response_get_headers(response): return {}
    def dap_http_response_get_header(response, key): return "header_value"
    def dap_http_client_init(): return 0
    def dap_http_client_deinit(): pass
    def dap_http_simple_request(url, method, data): return b"response"
    def dap_http_get_all_clients(): return []
    # Method constants
    DAP_HTTP_METHOD_GET = 0
    DAP_HTTP_METHOD_POST = 1
    DAP_HTTP_METHOD_PUT = 2
    DAP_HTTP_METHOD_DELETE = 3
    DAP_HTTP_METHOD_HEAD = 4
    DAP_HTTP_METHOD_OPTIONS = 5

from ..core.exceptions import DapException


class DapHttpError(DapException):
    """DAP HTTP specific errors"""
    pass


class DapHttpMethod(Enum):
    """HTTP methods"""
    GET = DAP_HTTP_METHOD_GET
    POST = DAP_HTTP_METHOD_POST
    PUT = DAP_HTTP_METHOD_PUT
    DELETE = DAP_HTTP_METHOD_DELETE
    HEAD = DAP_HTTP_METHOD_HEAD
    OPTIONS = DAP_HTTP_METHOD_OPTIONS


class DapHttpRequest:
    """
    📝 HTTP Request Object
    
    Represents an HTTP request with headers, body and method.
    """
    
    def __init__(self, request_handle: int, owns_handle: bool = True):
        """Initialize HTTP request"""
        self._request_handle = request_handle
        self._owns_handle = owns_handle
        self._logger = logging.getLogger(__name__)
        self._headers = {}
        
        if not request_handle:
            raise DapHttpError("Invalid request handle provided")
    
    @classmethod
    def create_request(cls) -> 'DapHttpRequest':
        """Create new HTTP request"""
        try:
            request_handle = dap_http_request_new()
            if not request_handle:
                raise DapHttpError("Failed to create HTTP request")
            return cls(request_handle)
        except Exception as e:
            raise DapHttpError(f"Request creation failed: {e}")
    
    def set_method(self, method: DapHttpMethod) -> None:
        """Set HTTP method"""
        try:
            dap_http_request_set_method(self._request_handle, method.value)
        except Exception as e:
            raise DapHttpError(f"Failed to set method: {e}")
    
    def set_url(self, url: str) -> None:
        """Set request URL"""
        try:
            dap_http_request_set_url(self._request_handle, url)
        except Exception as e:
            raise DapHttpError(f"Failed to set URL: {e}")
    
    def add_header(self, key: str, value: str) -> None:
        """Add header to request"""
        try:
            dap_http_request_add_header(self._request_handle, key, value)
            self._headers[key] = value
        except Exception as e:
            raise DapHttpError(f"Failed to add header: {e}")
    
    def set_body(self, body: bytes) -> None:
        """Set request body"""
        try:
            dap_http_request_set_body(self._request_handle, body, len(body))
        except Exception as e:
            raise DapHttpError(f"Failed to set body: {e}")
    
    def delete(self) -> None:
        """Delete request"""
        if self._owns_handle and self._request_handle:
            try:
                dap_http_request_delete(self._request_handle)
                self._request_handle = None
            except Exception as e:
                self._logger.error(f"Failed to delete request: {e}")
    
    @property
    def handle(self) -> int:
        """Get request handle"""
        return self._request_handle
    
    @property
    def headers(self) -> Dict[str, str]:
        """Get request headers"""
        return self._headers.copy()
    
    def __del__(self):
        """Destructor"""
        if hasattr(self, '_owns_handle') and self._owns_handle:
            try:
                self.delete()
            except:
                pass


class DapHttpResponse:
    """
    📄 HTTP Response Object
    
    Represents an HTTP response with status code, headers and body.
    """
    
    def __init__(self, response_handle: int, owns_handle: bool = True):
        """Initialize HTTP response"""
        self._response_handle = response_handle
        self._owns_handle = owns_handle
        self._logger = logging.getLogger(__name__)
        
        if not response_handle:
            raise DapHttpError("Invalid response handle provided")
    
    def get_status_code(self) -> int:
        """Get HTTP status code"""
        try:
            return dap_http_response_get_code(self._response_handle)
        except Exception as e:
            self._logger.error(f"Failed to get status code: {e}")
            return 0
    
    def get_data(self) -> bytes:
        """Get response body data"""
        try:
            return dap_http_response_get_data(self._response_handle)
        except Exception as e:
            self._logger.error(f"Failed to get response data: {e}")
            return b""
    
    def get_headers(self) -> Dict[str, str]:
        """Get all response headers"""
        try:
            return dap_http_response_get_headers(self._response_handle)
        except Exception as e:
            self._logger.error(f"Failed to get headers: {e}")
            return {}
    
    def get_header(self, key: str) -> Optional[str]:
        """Get specific header value"""
        try:
            return dap_http_response_get_header(self._response_handle, key)
        except Exception as e:
            self._logger.error(f"Failed to get header {key}: {e}")
            return None
    
    def delete(self) -> None:
        """Delete response"""
        if self._owns_handle and self._response_handle:
            try:
                dap_http_response_delete(self._response_handle)
                self._response_handle = None
            except Exception as e:
                self._logger.error(f"Failed to delete response: {e}")
    
    @property
    def handle(self) -> int:
        """Get response handle"""
        return self._response_handle
    
    @property
    def is_success(self) -> bool:
        """Check if response indicates success (2xx)"""
        code = self.get_status_code()
        return 200 <= code < 300
    
    @property
    def is_error(self) -> bool:
        """Check if response indicates error (4xx, 5xx)"""
        code = self.get_status_code()
        return code >= 400
    
    def __del__(self):
        """Destructor"""
        if hasattr(self, '_owns_handle') and self._owns_handle:
            try:
                self.delete()
            except:
                pass


class DapHttp:
    """
    🌐 DAP HTTP Client with proper session management
    
    Manages HTTP client state with proper C structure integration.
    Supports session management, header persistence and timeout control.
    
    Example:
        # Create HTTP client
        client = DapHttp.create_client()
        
        # Set default headers
        client.set_default_headers({
            "User-Agent": "DAP-SDK/2.0",
            "Accept": "application/json"
        })
        
        # Set timeout
        client.set_timeout(30)
        
        # Make requests
        response = client.get("https://api.example.com/data")
        if response.is_success:
            data = response.get_data()
        
        # Post data
        response = client.post("https://api.example.com/submit", b"payload")
    """
    
    _clients_registry: Dict[int, 'DapHttp'] = {}
    _lock = threading.Lock()
    _system_initialized = False
    
    def __init__(self, client_handle: int, owns_handle: bool = True):
        """
        Initialize DapHttp wrapper
        
        Args:
            client_handle: Native HTTP client handle
            owns_handle: Whether this instance owns the handle (for cleanup)
        """
        self._client_handle = client_handle
        self._owns_handle = owns_handle
        self._logger = logging.getLogger(__name__)
        self._default_headers = {}
        self._timeout = 30  # Default timeout in seconds
        
        if not client_handle:
            raise DapHttpError("Invalid HTTP client handle provided")
        
        # Ensure system is initialized
        self._ensure_system_initialized()
        
        # Register in global registry for tracking
        with self._lock:
            self._clients_registry[client_handle] = self
            
        self._logger.debug(f"DapHttp created with handle {client_handle}")
    
    @classmethod
    def _ensure_system_initialized(cls):
        """Ensure DAP HTTP system is initialized"""
        if not cls._system_initialized:
            with cls._lock:
                if not cls._system_initialized:
                    try:
                        result = dap_http_client_init()
                        if result != 0:
                            raise DapHttpError(f"HTTP system initialization failed with code {result}")
                        cls._system_initialized = True
                        logging.getLogger(__name__).info("DAP HTTP system initialized")
                    except Exception as e:
                        raise DapHttpError(f"HTTP system initialization failed: {e}")
    
    @classmethod
    def create_client(cls) -> 'DapHttp':
        """
        Create new HTTP client
        
        Returns:
            New DapHttp instance
            
        Raises:
            DapHttpError: If client creation fails
        """
        try:
            # Call C function: dap_http_client_new()
            client_handle = dap_http_client_new()
            
            if not client_handle:
                raise DapHttpError("Failed to create HTTP client")
            
            logging.getLogger(__name__).info("New DAP HTTP client created")
            
            return cls(client_handle)
            
        except Exception as e:
            raise DapHttpError(f"HTTP client creation failed: {e}")
    
    def set_default_headers(self, headers: Dict[str, str]) -> None:
        """
        Set default headers for all requests
        
        Args:
            headers: Dictionary of headers to set as defaults
        """
        try:
            self._default_headers.update(headers)
            # Call C function: dap_http_client_set_headers()
            dap_http_client_set_headers(self._client_handle, self._default_headers)
            self._logger.debug(f"Set {len(headers)} default headers")
        except Exception as e:
            raise DapHttpError(f"Failed to set default headers: {e}")
    
    def set_timeout(self, timeout_seconds: int) -> None:
        """
        Set request timeout
        
        Args:
            timeout_seconds: Timeout in seconds
        """
        try:
            self._timeout = timeout_seconds
            # Call C function: dap_http_client_set_timeout()
            dap_http_client_set_timeout(self._client_handle, timeout_seconds)
            self._logger.debug(f"Set timeout to {timeout_seconds} seconds")
        except Exception as e:
            raise DapHttpError(f"Failed to set timeout: {e}")
    
    def request(self, method: DapHttpMethod, url: str, 
               headers: Optional[Dict[str, str]] = None,
               body: Optional[bytes] = None) -> DapHttpResponse:
        """
        Make HTTP request
        
        Args:
            method: HTTP method
            url: Request URL
            headers: Optional additional headers
            body: Optional request body
            
        Returns:
            HTTP response object
        """
        try:
            # Merge headers
            all_headers = self._default_headers.copy()
            if headers:
                all_headers.update(headers)
            
            # Call C function: dap_http_client_request_ex()
            response_handle = dap_http_client_request_ex(
                self._client_handle, method.value, url, all_headers, body
            )
            
            if not response_handle:
                raise DapHttpError(f"HTTP {method.name} request to {url} failed")
            
            self._logger.debug(f"HTTP {method.name} request to {url} completed")
            
            return DapHttpResponse(response_handle)
            
        except Exception as e:
            raise DapHttpError(f"HTTP request failed: {e}")
    
    def request_with_object(self, request: DapHttpRequest) -> DapHttpResponse:
        """
        Make HTTP request using request object
        
        Args:
            request: HTTP request object
            
        Returns:
            HTTP response object
        """
        try:
            # Call C function: dap_http_client_request()
            response_handle = dap_http_client_request(
                self._client_handle, request.handle
            )
            
            if not response_handle:
                raise DapHttpError("HTTP request failed")
            
            self._logger.debug("HTTP request with object completed")
            
            return DapHttpResponse(response_handle)
            
        except Exception as e:
            raise DapHttpError(f"HTTP request with object failed: {e}")
    
    def get(self, url: str, headers: Optional[Dict[str, str]] = None) -> DapHttpResponse:
        """Make HTTP GET request"""
        return self.request(DapHttpMethod.GET, url, headers)
    
    def post(self, url: str, body: Optional[bytes] = None,
            headers: Optional[Dict[str, str]] = None) -> DapHttpResponse:
        """Make HTTP POST request"""
        return self.request(DapHttpMethod.POST, url, headers, body)
    
    def put(self, url: str, body: Optional[bytes] = None,
           headers: Optional[Dict[str, str]] = None) -> DapHttpResponse:
        """Make HTTP PUT request"""
        return self.request(DapHttpMethod.PUT, url, headers, body)
    
    def delete(self, url: str, headers: Optional[Dict[str, str]] = None) -> DapHttpResponse:
        """Make HTTP DELETE request"""
        return self.request(DapHttpMethod.DELETE, url, headers)
    
    def head(self, url: str, headers: Optional[Dict[str, str]] = None) -> DapHttpResponse:
        """Make HTTP HEAD request"""
        return self.request(DapHttpMethod.HEAD, url, headers)
    
    def options(self, url: str, headers: Optional[Dict[str, str]] = None) -> DapHttpResponse:
        """Make HTTP OPTIONS request"""
        return self.request(DapHttpMethod.OPTIONS, url, headers)
    
    def get_last_response_code(self) -> int:
        """Get last response status code"""
        try:
            return dap_http_client_get_response_code(self._client_handle)
        except Exception as e:
            self._logger.error(f"Failed to get last response code: {e}")
            return 0
    
    def get_last_response_size(self) -> int:
        """Get last response size"""
        try:
            return dap_http_client_get_response_size(self._client_handle)
        except Exception as e:
            self._logger.error(f"Failed to get last response size: {e}")
            return 0
    
    def delete_client(self) -> None:
        """Delete HTTP client and cleanup resources"""
        if self._owns_handle and self._client_handle:
            try:
                # Remove from registry
                with self._lock:
                    self._clients_registry.pop(self._client_handle, None)
                
                # Call C function: dap_http_client_delete()
                dap_http_client_delete(self._client_handle)
                
                self._logger.debug(f"HTTP client {self._client_handle} deleted")
                self._client_handle = None
                self._default_headers.clear()
                
            except Exception as e:
                self._logger.error(f"Failed to delete HTTP client: {e}")
    
    @property
    def handle(self) -> int:
        """Get native client handle"""
        return self._client_handle
    
    @property
    def is_valid(self) -> bool:
        """Check if client handle is valid"""
        return self._client_handle and self._client_handle in self._clients_registry
    
    @property
    def default_headers(self) -> Dict[str, str]:
        """Get default headers"""
        return self._default_headers.copy()
    
    @property
    def timeout(self) -> int:
        """Get timeout in seconds"""
        return self._timeout
    
    def __enter__(self) -> 'DapHttp':
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - cleanup client"""
        self.delete_client()
    
    def __del__(self):
        """Destructor - ensure cleanup"""
        if hasattr(self, '_owns_handle') and self._owns_handle:
            try:
                self.delete_client()
            except:
                pass  # Ignore errors in destructor
    
    def __repr__(self) -> str:
        return f"DapHttp(handle={self._client_handle}, timeout={self._timeout}s, headers={len(self._default_headers)})"


class DapHttpManager:
    """
    📁 HTTP Client Management System
    
    Provides high-level HTTP client management operations.
    """
    
    @staticmethod
    def get_all_clients() -> List[DapHttp]:
        """Get all HTTP clients from system"""
        try:
            client_list = dap_http_get_all_clients()
            clients = []
            for client_handle in client_list:
                if client_handle:
                    client = DapHttp(client_handle, owns_handle=False)
                    clients.append(client)
            return clients
        except Exception as e:
            logging.getLogger(__name__).error(f"Failed to get all clients: {e}")
            return []
    
    @staticmethod
    def deinitialize_system() -> None:
        """Deinitialize HTTP system"""
        try:
            dap_http_client_deinit()
            DapHttp._system_initialized = False
            logging.getLogger(__name__).info("DAP HTTP system deinitialized")
        except Exception as e:
            logging.getLogger(__name__).error(f"HTTP system deinitialization failed: {e}")


# Convenience functions
def create_http_client() -> DapHttp:
    """Create new HTTP client with default settings"""
    return DapHttp.create_client()


def quick_get(url: str, headers: Optional[Dict[str, str]] = None) -> DapHttpResponse:
    """Quick HTTP GET request"""
    with DapHttp.create_client() as client:
        return client.get(url, headers)


def quick_post(url: str, body: Optional[bytes] = None,
              headers: Optional[Dict[str, str]] = None) -> DapHttpResponse:
    """Quick HTTP POST request"""
    with DapHttp.create_client() as client:
        return client.post(url, body, headers)


def simple_request(url: str, method: str = "GET", data: Optional[bytes] = None) -> Optional[bytes]:
    """Simple HTTP request using legacy function"""
    try:
        return dap_http_simple_request(url, method, data)
    except Exception as e:
        logging.getLogger(__name__).error(f"Simple request failed: {e}")
        return None


__all__ = [
    'DapHttp',
    'DapHttpError',
    'DapHttpMethod',
    'DapHttpRequest',
    'DapHttpResponse',
    'DapHttpManager',
    'create_http_client',
    'quick_get',
    'quick_post',
    'simple_request'
] 