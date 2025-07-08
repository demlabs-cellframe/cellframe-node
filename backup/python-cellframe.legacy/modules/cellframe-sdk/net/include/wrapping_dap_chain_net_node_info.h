#ifndef _WRAPPING_DAP_CHAIN_NODE_INFO
#define _WRAPPING_DAP_CHAIN_NODE_INFO
#include <Python.h>
#include "dap_chain_node.h"
#include "libdap_chain_net_python.h"
#include "wrapping_dap_chain_common.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct PyDapChainNodeInfo{
    PyObject_HEAD
    dap_chain_node_info_t *node_info;
}PyDapChainNodeInfoObject;

PyObject *dap_chain_node_info_save_py(PyObject *self, PyObject *args);
PyObject *dap_chain_node_info_read_py(PyObject *self, PyObject *args);

extern PyTypeObject DapChainNodeInfoObjectType;

#ifdef __cplusplus
}
#endif

#endif //_WRAPPING_DAP_CHAIN_NODE_INFO
