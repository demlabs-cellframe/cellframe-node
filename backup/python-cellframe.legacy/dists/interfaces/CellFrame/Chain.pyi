from typing import Protocol, Any
from .Common import DatumEmission
from DAP.Crypto import HashFast


# chainModule
# DapChainObjectType
class Chain(Protocol):
    @staticmethod
    def findById(*args):
        pass

    @staticmethod
    def loadFromCfg(*args):
        pass

    @staticmethod
    def hasFileStore():
        pass

    @staticmethod
    def saveAll():
        pass

    @staticmethod
    def loadAll():
        pass

    @staticmethod
    def createAtomIter(*args):
        pass

    @staticmethod
    def atomIterGetFirst(*args):
        pass

    @staticmethod
    def atomGetDatums(*args):
        pass

    @staticmethod
    def atomIterGetNext(*args):
        pass

    @staticmethod
    def getDag():
        pass

    @staticmethod
    def addMempoolNotify(*args):
        pass

    @staticmethod
    def addAtomNotify(*args):
        pass

    @staticmethod
    def addAtomConfirmedNotify(*args):
        pass

    @staticmethod
    def atomFindByHash(*args):
        pass

    @staticmethod
    def countAtom():
        pass

    @staticmethod
    def getAtoms(*args):
        pass

    @staticmethod
    def countTx():
        pass

    @staticmethod
    def getTransactions(*args):
        pass

    @staticmethod
    def getCSName():
        pass


# DapChainTypeObjectType
class ChainType(Protocol):
    @staticmethod
    def CHAIN_TYPE_FIRST():
        pass

    @staticmethod
    def CHAIN_TYPE_TOKEN():
        pass

    @staticmethod
    def CHAIN_TYPE_EMISSION():
        pass

    @staticmethod
    def CHAIN_TYPE_TX():
        pass

    @staticmethod
    def CHAIN_TYPE_LAST():
        pass


# DapChainAtomIterObjectType
class ChainAtomIter(Protocol):
    # no methods
    pass


# DapChainAtomPtrObjectType
class ChainAtomPtr(Protocol):
    # no methods
    pass


# DapChainCellObjectType
class ChainCell(Protocol):
    @staticmethod
    def load(obj_chain, cell_file_path=None):
        pass

    def update(self):
        pass

    def append(self, atom_bytes, atom_size=None):
        pass


# DapChainIdObjectType
class ChainID(Protocol):
    # no methods
    pass


# DapChainCellIdObjectType
class ChainCellID(Protocol):
    # no methods
    pass


# DapChainHashSlowObjectType
class ChainHashSlow(Protocol):
    @staticmethod
    def toStr(*args):
        pass


# DapChainHashSlowKindObjectType
class ChainHashSlowKind(Protocol):
    # no methods
    pass


# DapChainAddrObjectType
class ChainAddr(Protocol):
    def toStr(self, *args):
        pass

    @staticmethod
    def fromStr(*args):
        pass

    @staticmethod
    def fill(*args):
        pass

    @staticmethod
    def fillFromKey(*args):
        pass

    def checkSum(self, *args):
        pass

    def getNetId(self):
        pass


# DapChainCsObjectType
class ChainCS(Protocol):
    def csAdd(self, *args):
        pass

    def csCreate(self, *args):
        pass

    def classAdd(self, *args):
        pass

    def classCreate(self, *args):
        pass

# DapChainWalletObjectType
class Wallet(Protocol):
    @staticmethod
    def getPath(self) -> str:
        pass

    @staticmethod
    def createWithSeed(wallet_name: str, path_wallets: str, sig_type: object, seed: bytes) -> 'Wallet':
        pass

    @staticmethod
    def openFile(file_path: str, password: str = None, /) -> 'Wallet':
        pass

    @staticmethod
    def open(wallet_name: str, wallet_path: str) -> 'Wallet':
        pass

    def save(self) -> int:
        pass

    @staticmethod
    def certToAddr(cert: object, net_id: object) -> 'ChainAddr':
        pass

    def getAddr(net_id: object) -> 'ChainAddr':
        pass

    def getCertsNumber(self) -> int:
        pass

    def getPKey(self, key_idx: int) -> 'DapPkey':
        pass

    def getKey(self, key_idx: int) -> 'CryptoKey':
        pass


# DapChainMempoolObjectType
class Mempool(Protocol):
    @staticmethod
    def proc(hash_str: str, chain: Chain) -> None:
        pass

    @staticmethod
    def emissionPlace(chain: Any, emission: Any) -> str:
        pass

    @staticmethod
    def emissionGet(chain: Any, emission_hash: str) -> None | str:
        pass

    @staticmethod
    def emissionExtract(chain: Any, bytes_obj: Any) -> None | DatumEmission:
        pass

    @staticmethod
    def txCreate(chain: Any, key_from: Any, addr_from: Any, addr_to: Any, token_ticker: str,
                 value: str, value_fee: str) -> None | str:
        pass

    @staticmethod
    def baseTxCreate(chain: Any, emi_hash: Any, emi_chain: Any, emission_value: str, ticker: str,
                     addr_to: Any, value_fee: str, wallet_or_cert: Any) -> None | str:
        pass

    @staticmethod
    def txCreateCond(chain: Any, key_from: Any, key_cond: Any, token_ticker: str, value: str,
                     value_per_unit_max: str, unit: Any, srv_uid: Any, fee: str, condition: Any) -> None | str:
        pass

    @staticmethod
    def txCreateCondInput(chain: Any, tx_prev_hash: Any, addr_to: Any, key_tx_sign: Any, receipt: Any) -> None | str:
        pass

    @staticmethod
    def remove(chain: Any, hash_str: str) -> bool:
        pass

    @staticmethod
    def list(chain_net: Any, chain: Any | None = None) -> dict[str, Any]:
        pass

    @staticmethod
    def addDatum(data: Any, chain: Any) -> None | str:
        pass


# DapChainLedgerObjectType
class Ledger(Protocol):
    def setLocalCellId(self, *args):
        pass

    def nodeDatumTxCalcHash(self, *args):
        pass

    def txAdd(self, *args):
        pass

    def tokenAdd(self, *args):
        pass

    def tokenEmissionLoad(self, *args):
        pass

    def tokenEmissionFind(self, *args):
        pass

    def tokenAuthSignsTotal(self, *args):
        pass

    def tokenAuthSignsValid(self, *args):
        pass

    def tokenAuthPkeysHashes(self, *args):
        pass

    def txGetTokenTickerByHash(self, *args):
        pass

    def addrGetTokenTickerAll(self, *args):
        pass

    def txCacheCheck(self, *args):
        pass

    def datumTxCacheCheck(self, *args):
        pass

    def txRemove(self, *args):
        pass

    def purge(self, *args):
        pass

    def count(self, *args):
        pass

    def countFromTo(self, *args):
        pass

    def txHashIsUsedOutItem(self, *args):
        pass

    def calcBalance(self, *args):
        pass

    def calcBalanceFull(self, *args):
        pass

    def txFindByHash(self, *args):
        pass

    def txFindByAddr(self, *args):
        pass

    def txFindByPkey(self, *args):
        pass

    def txCacheFindOutCond(self, *args):
        pass

    def txCacheGetOutCondValue(self, *args):
        pass

    def getTransactions(self, *args):
        pass

    def txAddNotify(self, *args):
        pass

    def bridgedTxNotifyAdd(self, *args):
        pass

    def txHashIsUsedOutItemHash(self, tx_hash : HashFast, idx : int) -> HashFast | None: ...
