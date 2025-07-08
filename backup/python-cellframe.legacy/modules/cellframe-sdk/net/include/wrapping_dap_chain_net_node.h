#ifndef _WRAPPING_DAP_CHAIN_NET_NODE_
#define _WRAPPING_DAP_CHAIN_NET_NODE_

#include <Python.h>
#include "dap_chain_node.h"
#include "wrapping_dap_chain_common.h"
#include "libdap_chain_net_python.h"

typedef struct PyDapChainNode{
    PyObject_HEAD
}PyDapChainNodeObject;

PyObject *dap_chain_node_gen_addr_py(PyObject *self, PyObject *args);
PyObject *dap_chain_node_check_addr_py(PyObject *self, PyObject *args);
PyObject *dap_chain_node_alias_find_py(PyObject *self, PyObject *args);
PyObject *dap_chain_node_alias_register_py(PyObject *self, PyObject *args);
PyObject *dap_chain_node_alias_delete_py(PyObject *self, PyObject *args);

extern PyTypeObject DapChainNodeObjectType;

#endif //_WRAPPING_DAP_CHAIN_NET_NODE_
