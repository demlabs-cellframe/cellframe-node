from typing import Protocol

from gi.overrides.GObject import Property


# DapCryptoAlgoObjectType
class Algo(Protocol):
    pass


# DapCryptoCertObjectType
class Cert(Protocol):
    pass


# DapCryproSignTypeObjectType
class SignType(Protocol):
    pass


# DapCryptoSignObjectType
class Sign(Protocol):
    pass


# DapCryptoKeyTypeObjectType
class CryptoKeyType(Protocol):
    pass


# DapCryptoDataTypeObjectType
class CryptoDataType(Protocol):
    pass


# DapChainHashFastObjectType
class HashFast(Protocol):
    pass

class Key(Protocol):
    pass

class PKey(Protocol):
    @Property
    def hash(self) -> HashFast: ...
    @Property
    def type(self) -> str: ...
    @Property
    def size(self) -> int: ...
    def toBytes(self) -> bytes: ...
    @staticmethod
    def fromBytes(self, data : bytes) -> PKey: ...
    def encrypt(self, data : bytes) -> bytes: ...

class GUUID(Protocol):
    def __init__(self, hex_GUUID : str) -> None: ...
    @staticmethod
    def generate() -> GUUID: ...
    @staticmethod
    def compose(net_id : int, service_td : int) ->GUUID: ...
    def __str__(self) -> str: ...
    def __eq__(self, value: GUUID) -> bool: ...
    def __ne__(self, value: GUUID) -> bool: ...
