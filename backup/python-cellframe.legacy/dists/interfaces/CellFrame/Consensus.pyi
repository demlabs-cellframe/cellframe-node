from typing import Protocol
from DAP.Crypto import HashFast
from DAP.Crypto import Sign
from datetime import datetime


# DapChainCsDagPoaObjectType
class DagPoa(Protocol):
    pass

# DapChainCsBlockType
class Block(Protocol):
    pass

#DapChainCsDagRoundType
class DagRound(Protocol):
    @property
    def info(self) -> DagRoundInfo: ...
    @property
    def event(self) -> DAG: ...
    @property
    def signs(self) -> [Sign]: ...

#DapChainCsDagRoundInfoType
class DagRoundInfo(Protocol):
    @property
    def reject_count(self) -> int: ...
    @property
    def ts_update(self) -> datetime: ...
    @property
    def datum_hash(self) -> HashFast: ...

# DapChainCsDagType
class ChainCSDag(Protocol):
    @staticmethod
    def findByHash(hash : HashFast) -> DAG:...
    @staticmethod
    def getCurrentRound() -> DagRound:...


# DapChainCsDagEventType
class DAG(Protocol):
    pass

# DapChainGdbObjectType
class GDB(Protocol):
    pass

