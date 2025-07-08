#pragma once

#include <Python.h>
#include "dap_chain_cs_dag.h"
#include "wrapping_dap_chain_cs_dag_event.h"
#include "wrapping_dap_hash.h"
#include "wrapping_dap_chain_atom_ptr.h"
#include "libdap_chain_atom_iter_python.h"

#ifdef __cplusplus
extern "C"{
#endif

typedef struct PyDapChainCsDag {
    PyObject_HEAD
    dap_chain_cs_dag_t *dag;
} PyDapChainCsDagObject;

PyObject *dap_chain_cs_dag_find_event_by_hash_py(PyObject *self, PyObject *args);
PyObject *dap_chain_cs_dag_get_current_round_py(PyObject *self, PyObject *args);

extern PyTypeObject DapChainCsDagType;

#ifdef __cplusplus
};
#endif
