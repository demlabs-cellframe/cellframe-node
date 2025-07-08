#ifndef _WRAPPING_DAP_CHAIN_NODE_CLIENT_
#define _WRAPPING_DAP_CHAIN_NODE_CLIENT_

#include <Python.h>
#include "dap_chain_node_client.h"
#include "wrapping_dap_chain_net_node_info.h"
#include "libdap_client_python.h"
#include "wrapping_dap_client_stage.h"

#ifdef __cplusplus
extern "C"{
#endif

typedef struct PyDapChainNodeClient{
    PyObject_HEAD
    dap_chain_node_client_t *node_client;
}PyDapChainNodeClientObject;

int dap_chain_node_client_init_py(void);
void dap_chain_node_client_deinit_py(void);

PyObject *dap_chain_client_connect_py(PyObject *self, PyObject *args);
PyObject *dap_chain_node_client_connect_py(PyObject *self, PyObject *args);
PyObject *dap_chain_node_client_close_py(PyObject *self, PyObject *args);
PyObject *dap_chain_node_client_send_ch_pkt_py(PyObject *self, PyObject *args);
PyObject *dap_chain_node_client_wait_py(PyObject *self, PyObject *args);
PyObject *dap_chain_node_client_set_notify_callbacks_py(PyObject *self, PyObject *args);

extern PyTypeObject DapChainNodeClientObjectType;

#ifdef __cplusplus
}
#endif

#endif //_WRAPPING_DAP_CHAIN_NODE_CLIENT_
