from typing import Protocol, Any
from xmlrpc.client import DateTime

from Network import Net
from DAP.Crypto import HashFast, PKey, Key, Cert
from DAP.Core import Math, NodeAddr
from Chain import ChainAddr, ChainID, Wallet
from Network import ServiceUID, ServicePriceUnitUID
from Network import NetID
from datetime import datetime


# commonModule

# DapChainDatumTypeIdObjectType
class DatumTypeID(Protocol):
    pass


# DapChainDatumObjectType
class Datum(Protocol):
    hash: str
    versionStr: str
    tsCreated: Any
    raw: Any
    dataRaw: Any

    def getSize(self):
        pass

    def isDatumTX(self):
        pass

    def getDatumTX(self, net : Net) -> DatumTx: ...

    def isDatumToken(self):
        pass

    def getDatumToken(self):
        pass

    def isDatumTokenEmission(self):
        pass

    def getDatumTokenEmission(self):
        pass

    def isDatumCustom(self):
        pass

    def isDatumDecree(self):
        pass

    def getDatumDecree(self):
        pass

    def isDatumAnchor(self):
        pass

    def getDatumAnchor(self):
        pass

    def getTypeStr(self):
        pass

    def getTypeId(self):
        pass


# DapChainDatumIterObjectType
class DatumIter(Protocol):
    pass


# DapChainDatumTokenObjectType
class DatumToken(Protocol):
    pass


# DapChainTxTokenExtType
class DatumTokenExt(Protocol):
    pass


# DapChainDatumTokenEmissionObjectType
class DatumEmission(Protocol):
    hash: Any
    version: Any
    typeStr: Any
    ticker: Any
    addr: Any
    value: Any
    data: Any
    signCount: Any
    signs: Any

    def __init__(self):
        pass

    # Методы объекта
    def addSign(self, args):
        pass

    def appendSign(self, args):
        pass

    def addTSD(self, args):
        pass

    def getTSD(self, args):
        pass


# DapChainDatumDecreeObjectType
class DatumDecree(Protocol):
    pass


# DapChainDatumAnchorObjectType
class DatumAnchor(Protocol):
    pass


# DapChainTxItemTypeObjectType
class TxItemType(Protocol):
    pass


# DapChainDatumTxObjectType
class DatumTx(Protocol):
    hash: Any
    dateCreated: Any

    def __init__(self):
        pass

    def getItems(self):
        pass

    def getSize(self, args):
        pass

    def addItem(self, item : TxIn | TxInCond | TxOut | TxOutExt | TxToken | TxOutCondSubtypeSrvPay |
                             TxOutCondSubtypeSrvStakePosDelegate | TxOutCondSubtypeSrvStakeLock |
                             TxOutCondSubtypeSrvXchange) -> bool:...

    def sign(self, key : Wallet | Key | Cert) -> bool:
        pass

    def verifySign(self, args):
        pass

class ChainTxOutCondSubType(Protocol):
    def __str__(self) -> str: ...

# DapChainTxOutCondObjectType
class TxOutCond(Protocol):
    @property
    def tsExpires(self) -> datetime: ...
    @property
    def value(self) -> Math: ...
    @property
    def typeSubtype(self) -> ChainTxOutCondSubType: ...
    @property
    def usedBy(self) -> HashFast | None: ...
    @property
    def tag(self) -> str | None: ...


# DapChainTxOutCondSubTypeSrvPayObjectType
class TxOutCondSubtypeSrvPay(Protocol):
    def __init__(self, value : Math, srvUID : ServiceUID, pubKey : PKey, maxPrice : Math, units : ServicePriceUnitUID, params : bytes | None = None) -> None: ...
    @property
    def unit(self) -> int: ...
    @property
    def uid(self) -> ServiceUID: ...
    @property
    def pkeyHash(self) -> HashFast: ...
    @property
    def maxPrice(self) -> int: ...
    @property
    def usedBy(self) -> HashFast | None: ...


# DapChainTxOutCondSubTypeSrvStakeLockObjectType
class TxOutCondSubtypeSrvStakeLock(Protocol):
    def __init__(self, srvUID : ServiceUID, value : Math, timeStaking : DateTime, reinvestParcent : Math) -> None: ...
    @property
    def timeUnlock(self) -> datetime:...
    @property
    def flags(self) -> int: ...
    @property
    def reinvestPercent(self) -> int: ...
    @property
    def hashTokenDelegate(self) -> None: ...
    @property
    def usedBy(self) -> HashFast | None: ...

# DapChainTxOutCondSubTypeSrvStakePosDelegateObjectType
class TxOutCondSubtypeSrvStakePosDelegate(Protocol):
    def __init__(self, srvUID : ServiceUID, value : Math, signingAddr : ChainAddr, signerNodeAddr : NodeAddr, sovereignAddr : ChainAddr, sovereignTax : Math) -> None:...
    @property
    def uid(self) -> ServiceUID: ...
    @property
    def addr(self) -> ChainAddr: ...
    @property
    def value(self) -> None: ...
    @property
    def usedBy(self) -> HashFast | None: ...


# DapChainTxOutCondSubTypeSrvXchangeObjectType
class TxOutCondSubtypeSrvXchange(Protocol):
    def __init__(self, UID : ServiceUID, sellNetID : NetID, valueSell : Math, buyNetId : NetID, token : str, valueRate : Math, sellerAddr : ChainAddr) -> None: ...
    @property
    def uid(self) -> ServiceUID: ...
    @property
    def netId(self) -> NetID: ...
    @property
    def token(self) -> str: ...
    @property
    def value(self) -> Math: ...
    @property
    def usedBy(self) -> HashFast | None: ...


# DapChainTxInObjectType
class TxIn(Protocol):
    def __init__(self, prevHash : HashFast, prevIdx : int) -> None: ...
    @property
    def prevHash(self) -> HashFast: ...
    @property
    def prevIdx(self) -> int: ...


# DapChainTxInCondObjectType
class TxInCond(Protocol):
    def __init__(self, prevHash : HashFast, outPrevIdx : int, receiptIdx : int) -> None: ...
    @property
    def receiptPrevIdx(self) -> int: ...
    @property
    def prevHash(self) -> HashFast: ...
    @property
    def outPrevIdx(self) -> int: ...


# DapChainTxOutObjectType
class TxOut(Protocol):
    def __init__(self, addr : ChainAddr, value : Math) -> None: ...
    @property
    def addr(self) -> ChainAddr : ...
    @property
    def value(self) -> Math: ...
    @property
    def usedBy(self) -> HashFast | None: ...


# DapChainTxPkeyObjectType
class TxPkey(Protocol):
    pass


# DapChainTxSigObjectType
class TxSig(Protocol):
    pass


# DapChainTxTokenObjectType
class TxToken(Protocol):
    def __init__(self, chainId : ChainID, hashEmi : HashFast) -> None: ...
    @property
    def ticker(self) -> str: ...
    @property
    def tokenEmissionHash(self) -> HashFast: ...
    @property
    def tokenEmissionChainId(self) -> ChainID: ...


# DapChainTxReceiptObjectType
class TxReceipt(Protocol):
    def __init__(self, srv_uid : ServiceUID, units_type : ServicePriceUnitUID, units : int, value : Math, ext : bytes | None = None) -> None: ...


# DapChainTxOutExtObjectType
class TxOutExt(Protocol):
    def __init__(self, addr : ChainAddr, token : str, value : Math) -> None: ...
    @property
    def addr(self) -> ChainAddr : ...
    @property
    def token(self) -> str : ...
    @property
    def value(self) -> Math: ...
    @property
    def usedBy(self) -> HashFast | None: ...


# DapChainTxTSDObjectType
class TxTSD(Protocol):
    pass


# DapChainTxOutStdObjectType
class TxOutStd(Protocol):
    @property
    def addr(self) -> ChainAddr: ...

    @property
    def token(self) -> str: ...

    @property
    def value(self) -> Math: ...

    @property
    def version(self) -> int: ...

    @property
    def timeLock(self) -> int: ...

    @property
    def usedBy(self) -> HashFast | None: ...