from typing import Any, Protocol, Callable
from enum import Enum


class ServerType(Enum):
    SERVER_TCP = 0
    SERVER_UDP = 1
    SERVER_LOCAL = 2


# PyDapServerObject
# TODO: уточнить верно ли я понял сишную реализацию
class Server(Protocol):
    @staticmethod
    def listen(addr: str, port: int, type: ServerType) -> Server:
        pass


# DapEventsObjectType
class Events(Protocol):
    pass


# DapEventsSocketObjectType
class EventsSocket(Protocol):
    pass


# DapHttpObjectType
class Http(Protocol):
    pass


# DapHttpCodeObjectType
class HttpCode(Protocol):
    def set(self, http_status_code: int, /) -> None:
        """Set status code Http response"""
        pass

    def OK(self) -> None:
        """Set status code OK(200) for this object"""
        pass

    def BadRequest(self) -> None:
        """Set status code Bad request(400) for this object"""
        pass

# DapHttpSimpleObjectType
class HttpSimple(Protocol):
    # read-only
    # action: str
    # query: str
    # ipClient: str
    # urlPath: str
    # request: Any

    @property
    def query(self) -> str:
        pass

    @property
    def ipClient(self) -> str:
        pass

    @property
    def urlPath(self) -> str:
        pass

    @property
    def request(self) -> Any:
        pass

    def init(self):
        pass

    def deinit(self):
        pass

    @staticmethod
    def addProc(server, url, reply_size_max, callback):
        pass

    def setPassUnknownUserAgents(self):
        pass

    def setFlagGenerateDefaultHeader(self):
        pass

    def replyAdd(self, reply_message: bytes):
        pass

    def setResponseHeader(self):
        pass

    def getResponseHeader(self):
        pass

# DapHttpHeaderObjectType
class HttpHeader(Protocol):
    pass


# DapEncServerObjectType
class EncHttp(Protocol):
    pass


# DapStreamObjectType
class Stream(Protocol):
    pass

# DapStreamCtlObjectType
class StreamCtl(Protocol):
    pass

# DapJsonRpcRequestObjectType
class JSONRPCRequest(Protocol):
    pass

# DapJsonRpcResponseobjectType
class JSONRPCResponse(Protocol):
    pass

class Member(Protocol):
    pass

class ClusterRole(Protocol):
    pass

class ClusterRoles(Protocol):
    @property
    def INVALID(self) -> ClusterRole: ...
    @property
    def EMBEDDED(self) -> ClusterRole: ...
    @property
    def AUTONOMIC(self) -> ClusterRole: ...
    @property
    def ISOLATED(self) -> ClusterRole: ...
    @property
    def VIRTUAL(self) -> ClusterRole: ...
    pass






