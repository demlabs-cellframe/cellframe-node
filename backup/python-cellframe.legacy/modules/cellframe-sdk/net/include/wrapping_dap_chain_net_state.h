#ifndef _WRAPPING_DAP_CHAIN_NET_STATE_
#define _WRAPPING_DAP_CHAIN_NET_STATE_
#include <Python.h>
#include "dap_chain_net.h"

#ifdef __cplusplus
extern "C"{
#endif

typedef struct PyDapChainNetState{
    PyObject_HEAD
    dap_chain_net_state_t state;
}PyDapChainNetStateObject;

PyObject *NET_STATE_OFFLINE_PY();
PyObject *NET_STATE_LINKS_PREPARE_PY();
PyObject *NET_STATE_LINKS_CONNECTING_PY();
PyObject *NET_STATE_LINKS_ESTABLISHED_PY();
PyObject *NET_STATE_ADDR_REQUEST_PY(); // Waiting for address assign
PyObject *NET_STATE_ONLINE_PY();
PyObject *NET_STATE_SYNC_GDB_PY();
PyObject *NET_STATE_SYNC_CHAINS_PY();

extern PyTypeObject DapChainNetStateObjectType;

#ifdef __cplusplus
}
#endif

#endif // _WRAPPING_DAP_CHAIN_NET_STATE_
