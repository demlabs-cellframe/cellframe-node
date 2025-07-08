#pragma once

#include <Python.h>
#include "wrapping_dap_chain_common.h"
#include "dap_chain_datum_tx_tsd.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct PyDapChainTxTSD{
    PyObject_HEAD
    dap_chain_tx_tsd_t *tsd;
} PyDapChainTxTSDObject;

PyObject *wrapping_dap_chain_tx_get_tsd_data(PyObject *self, void *closure);
PyObject *wrapping_dap_chain_tx_get_tsd_type(PyObject *self, void *closure);

extern PyTypeObject DapChainTxTSDObjectType;

#ifdef __cplusplus
}
#endif
