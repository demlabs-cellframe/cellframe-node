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

#ifndef _WRAPPING_DAP_CHAIN_TX_RECEIPT_
#define _WRAPPING_DAP_CHAIN_TX_RECEIPT_

#include <Python.h>
#include "dap_chain_datum_tx_receipt.h"
#include "wrapping_dap_sign.h"
#include "dap_chain_common.h"
#include "wrapping_dap_sign.h"
#include "dap_sign.h"

#ifdef __cplusplus
extern "C"{
#endif

typedef struct PyDapChainTXReceiptOld{
    PyObject_HEAD
    dap_chain_datum_tx_receipt_old_t *tx_receipt;
}PyDapChainTXReceiptOldObject;

typedef struct PyDapChainTXReceipt{
    PyObject_HEAD
    dap_chain_datum_tx_receipt_t *tx_receipt;
}PyDapChainTXReceiptObject;

PyObject *wrapping_dap_chain_tx_receipt_get_size(PyObject *self, void *closure);
PyObject *wrapping_dap_chain_tx_receipt_get_ext_size(PyObject *self, void *closure);
PyObject *wrapping_dap_chain_tx_receipt_get_units(PyObject *self, void *closure);
PyObject *wrapping_dap_chain_tx_receipt_get_uid(PyObject *self, void *closure);
PyObject *wrapping_dap_chain_tx_receipt_get_units_type(PyObject *self, void *closure);
PyObject *wrapping_dap_chain_tx_receipt_get_value(PyObject *self, void *closure);
PyObject *wrapping_dap_chain_tx_receipt_get_sig_provider(PyObject *self, void *closure);
PyObject *wrapping_dap_chain_tx_receipt_get_sig_client(PyObject *self, void *closure);
PyObject *wrapping_dap_chain_tx_receipt_sign(PyObject *self, PyObject *sign);

extern PyTypeObject DapChainTxReceiptObjectType;
extern PyTypeObject DapChainTxReceiptOldObjectType;

#ifdef __cplusplus
extern "C"{
#endif

#endif //_WRAPPING_DAP_CHAIN_TX_RECEIPT_
