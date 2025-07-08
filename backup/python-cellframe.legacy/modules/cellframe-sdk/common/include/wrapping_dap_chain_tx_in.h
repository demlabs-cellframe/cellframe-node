/*
 * Authors:
 * Alexey V. Stratulat <alexey.stratulat@demlabs.net>
 * DeM Labs Inc.   https://demlabs.net
 * CellFrame       https://cellframe.net
 * Sources         https://gitlab.demlabs.net/cellframe
 * Copyright  (c) 2017-2021
 * All rights reserved.

 This file is part of DAP (Distributed Applications Platform) the open source project

    DAP (Distributed Applications Platform) is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    DAP is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with any DAP based project.  If not, see <http://www.gnu.org/licenses/>.
*/

#ifndef _WRAPPING_DAP_CHAIN_TX_IN_
#define _WRAPPING_DAP_CHAIN_TX_IN_

#include <Python.h>
#include "dap_chain_datum_tx_in.h"
#include "wrapping_dap_hash.h"
#include "dap_chain_datum_tx_items.h"

#ifdef __cplusplus
extern "C"{
#endif

typedef struct PyDapChainTXIn{
    PyObject_HEAD
    dap_chain_tx_in_t *tx_in;
}PyDapChainTXInObject;

int PyDapChainTxIn_init(PyObject *self, PyObject *args, PyObject *kwds);

PyObject *wrapping_dap_chain_tx_in_get_prev_hash(PyObject *self, void *closure);
PyObject *wrapping_dap_chain_tx_in_get_out_prev_idx(PyObject *self, void *closure);

extern PyTypeObject DapChainTxInObjectType;

#ifdef __cplusplus
extern "C"{
#endif

#endif //_WRAPPING_DAP_CHAIN_TX_IN_
