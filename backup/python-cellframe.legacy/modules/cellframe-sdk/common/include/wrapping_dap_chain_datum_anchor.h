#pragma once

#include <Python.h>
#include "dap_chain_datum_anchor.h"

typedef struct PyDapChainDatumAnchor{
    PyObject_HEAD
    dap_chain_datum_anchor_t *anchor;
}PyDapChainDatumAnchorObject;

PyObject *wrapping_dap_chain_datum_anchor_get_ts_created(PyObject *self, void *closure);
PyObject *wrapping_dap_chain_datum_anchor_get_tsd(PyObject *self, void *closure);
PyObject *wrapping_dap_chain_datum_anchor_get_decree_hash(PyObject *self, void *closure);
PyObject *wrapping_dap_chain_datum_anchor_get_sign(PyObject *self, void *closure);
PyObject *wrapping_dap_chain_datum_anchor_get_hash(PyObject *self, void *closure);

extern PyTypeObject DapChainDatumAnchorObjectType;

bool DapChainDatumAnchor_Check(PyObject *self);