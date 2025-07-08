#pragma once

#include "Python.h"
#include "dap_chain_block.h"
#include "dap_chain_cs_blocks.h"
#include "wrapping_dap_chain_cell.h"
#include "libdap-chain-python.h"
#include "datetime.h"
#include "dap_chain_block_cache.h"
#include "wrapping_dap_chain_atom_ptr.h"

typedef struct PyDapChainCSBlock{
    PyObject_HEAD
    dap_chain_block_t *block;
    size_t block_size;
}PyDapChainCSBlockObject;

PyObject *wrapping_dap_chain_block_get_version(PyObject *self, void *closure);
PyObject *wrapping_dap_chain_block_get_cell_id(PyObject *self, void *closure);
PyObject *wrapping_dap_chain_block_get_chain_id(PyObject *self, void *closure);
PyObject *wrapping_dap_chain_block_get_ts_created(PyObject *self, void *closure);
PyObject *wrapping_dap_chain_block_get_meta_data(PyObject *self, void *closure);
PyObject *wrapping_dap_chain_block_get_datums(PyObject *self, void *closure);
PyObject *wrapping_dap_chain_block_get_signs(PyObject *self, void *closure);
PyObject *wrapping_dap_chain_block_get_hash(PyObject *self, void *closure);
PyObject *wrapping_dap_chain_block_get_ledger_ret_code(PyObject *self, PyObject *argv);
PyObject *wrapping_dap_chain_block_get_block_from_hash(PyObject *self, PyObject *argv);
//PyObject *wrapping_dap_chain_block_get_block_cache(PyObject *self, void *closure);
PyObject *wrapping_dap_chain_cs_block_get_block_signers_rewards(PyObject *self, PyObject *args);

PyObject* dap_chain_cs_block_get_atom(PyObject *self, PyObject *args);

extern PyTypeObject DapChainCsBlockType;
