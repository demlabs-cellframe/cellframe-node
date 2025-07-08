#pragma once

#include <Python.h>
#include <datetime.h>
#include "dap_chain_cs_dag_event.h"
#include "wrapping_dap_chain_common.h"
#include "wrapping_dap_hash.h"
#include "wrapping_dap_chain_datum.h"
#include "wrapping_dap_chain_atom_ptr.h"

typedef struct PyDapChainCsDagEvent{
    PyObject_HEAD
    dap_chain_cs_dag_event_t *event;
    size_t event_size;
}PyDapChainCsDagEventObject;

PyObject *wrapping_dap_chain_cs_dag_event_from_atom(PyObject *self, PyObject *args);
PyObject *wrapping_dap_chain_cs_dag_event_get_hash(PyObject *self, void *closure);
PyObject *wrapping_dap_chain_cs_dag_event_get_version(PyObject *self, void *closure);
PyObject *wrapping_dap_chain_cs_dag_event_get_round_id(PyObject *self, void *closure);
PyObject *wrapping_dap_chain_cs_dag_event_get_ts_created(PyObject *self, void *closure);
PyObject *wrapping_dap_chain_cs_dag_event_get_chain_id(PyObject *self, void *closure);
PyObject *wrapping_dap_chain_cs_dag_event_get_cell_id(PyObject *self, void *closure);
PyObject *wrapping_dap_chain_cs_dag_event_get_hash_count(PyObject *self, void *closure);
PyObject *wrapping_dap_chain_cs_dag_event_get_signs_count(PyObject *self, void *closure);
PyObject *wrapping_dap_chain_cs_dag_event_get_links(PyObject *self, void *closure);
PyObject *wrapping_dap_chain_cs_dag_event_get_datum(PyObject *self, void *closure);
PyObject *wrapping_dap_chain_cs_dag_event_get_signs(PyObject *self, void *closure);

extern PyTypeObject DapChainCsDagEventType;
