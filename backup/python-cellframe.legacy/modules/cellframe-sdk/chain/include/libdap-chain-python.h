#pragma once

#define PY_SSIZE_T_CLEAN

#include "Python.h"
//#define DAP_APP_NAME "BINDING_CHAIN_PYTHON"
#include "dap_chain.h"
#include "dap_chain_node_client.h"
#include "libdap-python.h"
#include "wrapping_dap_chain_ledger.h"
#include "wrapping_dap_chain_common.h"
#include "libdap_chain_atom_iter_python.h"
#include "wrapping_dap_chain_atom_ptr.h"
#include "wrapping_dap_chain_datum.h"
#include "wrapping_dap_chain_cell.h"
#include "wrapping_dap_chain_cs_dag.h"
#include "wrapping_dap_chain_datum_tx.h"


typedef struct PyDapChain{
    PyObject_HEAD
    dap_chain_t *chain_t;
} PyDapChainObject;

int init_chain_py();
void deinit_chain_py();

void PyDapChainObject_dealloc(PyDapChainObject* chain);
PyObject *PyDapChainObject_new(PyTypeObject *type_object, PyObject *args, PyObject *kwds);


PyObject *dap_chain_find_by_id_py(PyObject *self, PyObject *args);
PyObject *dap_chain_has_file_store_py(PyObject *self, PyObject *args);
PyObject *dap_chain_load_all_py(PyObject *self, PyObject *args);
PyObject *dap_chain_load_from_cfg_py(PyObject *self, PyObject *args);
//PyObject *dap_chain_init_net_cfg_name_py(PyObject *self, PyObject *args); //dap_chain_init_net_cfg_name
//PyObject *dap_chain_close_py(PyObject *self, PyObject *args);
PyObject *dap_chain_python_create_atom_iter(PyObject *self, PyObject *args);
PyObject *dap_chain_python_atom_iter_get_first(PyObject *self, PyObject *args);
PyObject *dap_chain_python_atom_get_datums(PyObject *self, PyObject *args);

PyObject *dap_chain_python_atom_iter_get_next(PyObject *self, PyObject *args);
PyObject *dap_chain_python_atom_iter_get_dag(PyObject *self, PyObject *args);
PyObject *dap_chain_python_add_mempool_notify_callback(PyObject *self, PyObject *args);
PyObject *dap_chain_net_add_atom_notify_callback(PyObject *self, PyObject *args);
PyObject *dap_chain_atom_confirmed_notify_add_py(PyObject *self, PyObject *args);
PyObject *dap_chain_fork_resolved_notify_add_py(PyObject *self, PyObject *args);

PyObject *dap_chain_python_atom_find_by_hash(PyObject *self, PyObject* args);

PyObject *dap_chain_python_get_atom_count(PyObject *self, PyObject *args);
PyObject *dap_chain_python_get_atoms(PyObject *self, PyObject *args);

PyObject *dap_chain_python_get_count_tx(PyObject *self, PyObject *args);
PyObject *dap_chain_python_get_txs(PyObject *self, PyObject *args);

PyObject *dap_chain_python_get_cs_name(PyObject *self, PyObject *args);

PyObject *dap_chain_python_get_net(PyObject *self, PyObject *args);

PyObject *dap_chain_python_get_config_item(PyObject *self, PyObject *args);

PyObject *PyDapChain_str(PyObject *self);

extern PyTypeObject DapChainObjectType;

DAP_STATIC_INLINE bool PyDapChain_Check(PyDapChainObject* self){
    return PyObject_TypeCheck(self, &DapChainObjectType);
}


