/*
* Authors:
* Roman Khlopkov <roman.khlopkov@demlabs.net>
* Cellframe       https://cellframe.net
* DeM Labs Inc.   https://demlabs.net
* Copyright  (c) 2017-2023
* All rights reserved.

This file is part of CellFrame SDK the open source project

CellFrame SDK is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

CellFrame SDK is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with any CellFrame SDK based project.  If not, see <http://www.gnu.org/licenses/>.
*/

#pragma once

#include <Python.h>
#include "wrapping_dap_chain_common.h"
#include "libdap-chain-python.h"

#ifdef __cplusplus
extern "C"{
#endif

typedef struct PyDapChainTXOutStd {
    PyObject_HEAD
    dap_chain_tx_out_std_t *out;
    dap_ledger_t *ledger;
    dap_hash_fast_t tx_hash;
    uint64_t idx;
} PyDapChainTXOutStdObject;

PyObject *wrapping_dap_chain_tx_out_std_get_addr(PyObject *self, void *closure);
PyObject *wrapping_dap_chain_tx_out_std_get_token(PyObject *self, void *closure);
PyObject *wrapping_dap_chain_tx_out_std_get_value(PyObject *self, void *closure);
PyObject *wrapping_dap_chain_tx_out_std_get_used_by(PyObject *self, void *closure);
PyObject *wrapping_dap_chain_tx_out_std_get_version(PyObject *self, void *closure);
PyObject *wrapping_dap_chain_tx_out_std_get_timelock(PyObject *self, void *closure);

extern PyTypeObject DapChainTxOutStdObjectType;

#ifdef __cplusplus
extern "C"{
#endif
