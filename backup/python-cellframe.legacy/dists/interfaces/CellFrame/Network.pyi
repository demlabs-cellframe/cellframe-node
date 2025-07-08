from typing import Protocol


# === Chain node ===
# DapChainNodeObjectType
class Node(Protocol):
    pass


# DapChainNodeInfoObjectType
class NodeInfo(Protocol):
    pass


# DapChainNodeClientObjectType
class NodeClient(Protocol):
    pass


# DapChainNodeAddrObjectType
class NodeAddr(Protocol):
    pass


# === Chain net ===
# DapChainNetObjectType
class Net(Protocol):
    # properties
    # {"id", (getter)dap_chain_net_python_get_id, NULL, NULL, NULL},
    # {"chains", (getter)dap_chain_net_python_get_chains, NULL, NULL, NULL},
    # {"txFee", (getter)dap_chain_net_get_tx_fee_py, NULL, NULL, NULL},
    # {"txFeeAddr", (getter)dap_chain_net_get_tx_fee_addr_py, NULL, NULL, NULL},
    # {"validatorMaxFee", (getter)dap_chain_net_get_validator_max_fee_py, NULL, NULL, NULL},
    # {"validatorAverageFee", (getter)dap_chain_net_get_validator_average_fee_py, NULL, NULL, NULL},
    # {"validatorMinFee", (getter)dap_chain_net_get_validator_min_fee_py, NULL, NULL, NULL},
    # {"nativeTicker", (getter)dap_chain_net_get_native_ticker_py, NULL, NULL, NULL},
    # {"autoproc", (getter)dap_chain_net_get_mempool_autoproc_py, NULL, NULL, NULL},
    # methods
    def loadAll(self):
        pass
    # {"", dap_chain_net_load_all_py, METH_NOARGS | METH_STATIC, ""},
    # {"stateGoTo", dap_chain_net_state_go_to_py, METH_VARARGS, ""},
    # {"start", dap_chain_net_start_py, METH_VARARGS, ""},
    # {"stop", dap_chain_net_stop_py, METH_VARARGS, ""},
    # {"linksEstablish", dap_chain_net_links_establish_py, METH_VARARGS, ""},
    # {"syncChains", dap_chain_net_sync_all_py, METH_VARARGS, ""},
    # {"syncGdb", dap_chain_net_sync_gdb_py, METH_VARARGS, ""},
    # {"syncAll", dap_chain_net_sync_all_py, METH_VARARGS, ""},
    # {"procDatapool", dap_chain_net_proc_datapool_py, METH_VARARGS, ""},
    # {"byName", dap_chain_net_by_name_py, METH_VARARGS | METH_STATIC, ""},
    # {"getNets", dap_chain_get_nets_py, METH_NOARGS | METH_STATIC, ""},
    # {"byId", dap_chain_net_by_id_py, METH_VARARGS | METH_STATIC, ""},
    # {"idByName", dap_chain_net_id_by_name_py, METH_VARARGS | METH_STATIC, ""},
    # {"ledgerByNetName", dap_chain_ledger_by_net_name_py, METH_VARARGS | METH_STATIC, ""},
    # {"getChainByName", dap_chain_net_get_chain_by_name_py, METH_VARARGS, ""},
    # {"getCurAddr", dap_chain_net_get_cur_addr_py, METH_VARARGS, ""},
    # {"getCurCell", dap_chain_net_get_cur_cell_py, METH_VARARGS, ""},
    # {"getGdbGroupMempool", dap_chain_net_get_gdb_group_mempool_py, METH_VARARGS | METH_STATIC, ""},
    # {"getGdbGroupMempoolByChainType", dap_chain_net_get_gdb_group_mempool_by_chain_type_py, METH_VARARGS, ""},
    # {"linksConnect", dap_chain_net_links_connect_py, METH_VARARGS, ""},
    # {"getChainByChainType", dap_chain_net_get_chain_by_chain_type_py, METH_VARARGS, ""},
    # {"getLedger", dap_chain_net_get_ledger_py, METH_NOARGS, ""},
    # {"getName", dap_chain_net_get_name_py, METH_NOARGS, ""},
    # {"getTxByHash", dap_chain_net_get_tx_by_hash_py, METH_VARARGS, ""},
    # {"addNotify", (PyCFunction)dap_chain_net_add_notify_py, METH_VARARGS, ""},


# DapChainNetIdObjectType
class NetID(Protocol):
    pass


# DapChainNetStateObjectType
class NetState(Protocol):
    pass


# === Chain net srv ===

# DapChainNetSrvObjectType
class Service(Protocol):
    pass


# DapChainNetSrvClientObjectType
class ServiceClient(Protocol):
    pass


# DapChainNetStateObjectType
class ServicePrice(Protocol):
    pass


# DapChainNetSrvOrderObjectType
class ServiceOrder(Protocol):
    pass


# DapChainNetSrvOrderDirectionObjectType
class ServiceOrderDirection(Protocol):
    pass


# DapChainNetSrvUidObjectType
class ServiceUID(Protocol):
    pass


# DapChainNetSrvPriceUnitUidObjectType
class ServicePriceUnitUID(Protocol):
    pass
