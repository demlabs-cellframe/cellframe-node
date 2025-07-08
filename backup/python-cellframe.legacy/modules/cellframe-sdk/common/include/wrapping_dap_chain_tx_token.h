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

#ifndef _WRAPPING_DAP_CHAIN_TX_TOKEN_
#define _WRAPPING_DAP_CHAIN_TX_TOKEN_

#include <Python.h>
#include "dap_chain_datum_tx_in_ems.h"
#include "wrapping_dap_hash.h"
#include "wrapping_dap_chain_common.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct PyDapChainTxToken{
    PyObject_HEAD
    dap_chain_tx_in_ems_t *token;
}PyDapChainTxTokenObject;

PyObject *wrapping_dap_chain_tx_token_get_ticker(PyObject *self, void *closure);
PyObject *wrapping_dap_chain_tx_token_get_token_emission_hash(PyObject *self, void *closure);
PyObject *wrapping_dap_chain_tx_token_get_token_emission_chain_id(PyObject *self, void *closure);

extern PyTypeObject DapChainTxTokenObjectType;

#ifdef __cplusplus
}
#endif
#endif //_WRAPPING_DAP_CHAIN_TX_TOKEN_
