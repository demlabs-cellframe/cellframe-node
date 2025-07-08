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

#ifndef _WRAPPING_DAP_CHAIN_DATUM_TX_
#define _WRAPPING_DAP_CHAIN_DATUM_TX_

#include "Python.h"
#include "datetime.h"
#include "wrapping_dap_chain_common.h"
#include "libdap_crypto_key_python.h"
#include "dap_chain_datum_tx_out_cond.h"
#include "wrapping_dap_hash.h"
#include "dap_chain_datum_tx_items.h"
#include "wrapping_dap_hash.h"
#include "wrapping_dap_chain_tx_in.h"
#include "wrapping_dap_chain_tx_in_cond.h"
#include "wrapping_dap_chain_tx_out.h"
#include "wrapping_dap_chain_tx_out_cond.h"
#include "wrapping_dap_chain_tx_out_cond_subtype_srv_pay.h"
#include "wrapping_dap_chain_tx_out_cond_subtype_srv_stake.h"
#include "wrapping_dap_chain_tx_out_cond_subtype_srv_stake_lock.h"
#include "wrapping_dap_chain_tx_out_cond_subtype_srv_xchange.h"
#include "wrapping_dap_chain_tx_out_ext.h"
#include "wrapping_dap_chain_tx_out_std.h"
#include "wrapping_dap_chain_tx_pkey.h"
#include "wrapping_dap_chain_tx_sig.h"
#include "wrapping_dap_chain_tx_receipt.h"
#include "wrapping_dap_chain_tx_token.h"
#include "wrapping_dap_chain_tx_token_ext.h"
#include "wrapping_dap_chain_tx_tsd.h"
#include "wrapping_dap_chain_datum_tx_voting.h"

#ifdef __cplusplus
extern "C" {
#endif

/* DAP chain tx iter type */
typedef struct PyDapChainTxItemType{
    PyObject_HEAD
}PyDapChainTxItemTypeObject;

PyObject *TX_ITEM_TYPE_IN_PY(PyObject *self, PyObject *args);
PyObject *TX_ITEM_TYPE_OUT_PY(PyObject *self, PyObject *args);
PyObject *TX_ITEM_TYPE_PKEY_PY(PyObject *self, PyObject *args);
PyObject *TX_ITEM_TYPE_SIG_PY(PyObject *self, PyObject *args);
PyObject *TX_ITEM_TYPE_IN_EMS_PY(PyObject *self, PyObject *args);
PyObject *TX_ITEM_TYPE_IN_COND_PY(PyObject *self, PyObject *args);
PyObject *TX_ITEM_TYPE_OUT_COND_PY(PyObject *self, PyObject *args);
PyObject *TX_ITEM_TYPE_RECEIPT_PY(PyObject *self, PyObject *args);
PyObject *TX_ITEM_TYPE_RECEIPT_OLD_PY(PyObject *self, PyObject *args);
PyObject *TX_ITEM_TYPE_TSD_PY(PyObject *self, PyObject *args);

extern PyTypeObject DapChainTxItemTypeObjectType;

/* -------------------------------------- */

extern PyTypeObject DapChainTxCondTypeObjectType;

/* -------------------------------------- */

/* DAP chain datum tx */
typedef struct PyDapChainDatumTx{
    PyObject_HEAD
    dap_chain_datum_tx_t *datum_tx;
    bool original;
}PyDapChainDatumTxObject;

PyObject *PyDapChainDatumTxObject_create(PyTypeObject *type_object, PyObject *args, PyObject *kwds);
void PyDapChainDatumTxObject_delete(PyDapChainDatumTxObject* datumTx);
PyObject *dap_chain_datum_tx_get_size_py(PyObject *self, PyObject *args);
PyObject *dap_chain_datum_tx_add_item_py(PyObject *self, PyObject *args);
PyObject *dap_chain_datum_tx_add_in_item_py(PyObject *self, PyObject *args);
PyObject *dap_chain_datum_tx_add_in_cond_item_py(PyObject *self, PyObject *args);
PyObject *dap_chain_datum_tx_add_out_item_py(PyObject *self, PyObject *args);
PyObject *dap_chain_datum_tx_add_out_cond_item_py(PyObject *self, PyObject *args);
PyObject *dap_chain_datum_tx_add_sign_item_py(PyObject *self, PyObject *args);

PyObject *dap_chain_datum_tx_append_sign_item_py(PyObject *self, PyObject *args);
PyObject *dap_chain_datum_tx_verify_sign_py(PyObject *self, PyObject *args);


PyObject *wrapping_dap_chain_datum_tx_get_items(PyObject *self, PyObject *args);

PyObject *wrapping_dap_chain_datum_tx_get_hash(PyObject *self, void* closure);
PyObject *wrapping_dap_chain_datum_tx_get_tsCreated(PyObject *self, void* closure);

bool DapChainDatumTx_Check(PyObject *self);

extern PyTypeObject DapChainDatumTxObjectType;

/* -------------------------------------- */

#ifdef __cplusplus
}
#endif

#endif //_WRAPPING_DAP_CHAIN_DATUM_TX_
