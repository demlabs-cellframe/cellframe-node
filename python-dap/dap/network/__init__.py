"""
🌐 DAP Network Module

Comprehensive network operations for DAP SDK.
All classes now properly wrap corresponding C structures.

Example:
    # Client operations
    with DapClient() as client:
        conn = client.connect("192.168.1.100", 8080)
        client.send_data(conn, b"hello")
    
    # Server operations
    with DapServer() as server:
        server.start("0.0.0.0", 8080)
        
    # HTTP operations
    with DapHttp() as http:
        response = http.get("https://api.example.com/data")
        
    # Stream operations
    with DapStream(workers=16) as stream:
        stream_id = stream.create_stream()
        stream.send_data(b"data", stream_id)
"""

from .client import (
    DapClient,
    DapClientError,
    DapClientStage,
    DapClientManager,
    create_client,
    connect_to_peer
)

from .server import (
    DapServer,
    DapServerError,
    DapServerType,
    DapServerManager,
    create_http_server,
    create_tcp_server,
    create_websocket_server
)

from .stream import (
    DapStream,
    DapStreamError,
    DapStreamState,
    DapStreamChannel,
    DapStreamWorker,
    DapStreamManager,
    create_stream,
    create_stream_worker,
    connect_stream
)

from .http import (
    DapHttp,
    DapHttpError,
    DapHttpMethod,
    DapHttpRequest,
    DapHttpResponse,
    DapHttpManager,
    create_http_client,
    quick_get,
    quick_post,
    simple_request
)

__all__ = [
    # Client operations
    'DapClient',
    'DapClientError',
    'DapClientStage',
    'DapClientManager',
    'create_client',
    'connect_to_peer',
    
    # Server operations
    'DapServer',
    'DapServerError',
    'DapServerType',
    'DapServerManager',
    'create_http_server',
    'create_tcp_server',
    'create_websocket_server',
    
    # Stream operations
    'DapStream',
    'DapStreamError',
    'DapStreamState',
    'DapStreamChannel',
    'DapStreamWorker',
    'DapStreamManager',
    'create_stream',
    'create_stream_worker',
    'connect_stream',
    
    # HTTP operations
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

# Version info
__version__ = "2.0.0"
__author__ = "Demlabs"
__description__ = "DAP SDK Network Module - Proper C structure wrapping"
