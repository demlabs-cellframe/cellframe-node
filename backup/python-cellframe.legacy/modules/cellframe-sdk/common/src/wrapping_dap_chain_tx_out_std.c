/*
* Authors:
* Roman Khlopkov <roman.khlopkov@demlabs.net>
* Cellframe       https://cellframe.net
* DeM Labs Inc.   https://demlabs.net
* Copyright  (c) 2017-2025
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
#include "wrapping_dap_chain_tx_out_std.h"

static PyGetSetDef DapChainTxOutStdGetsSetsDef[] = {
        {"addr", (getter)wrapping_dap_chain_tx_out_std_get_addr, NULL, "", NULL},
        {"token", (getter)wrapping_dap_chain_tx_out_std_get_token, NULL, "", NULL},
        {"value", (getter)wrapping_dap_chain_tx_out_std_get_value, NULL, "", NULL},
        {"version", (getter)wrapping_dap_chain_tx_out_std_get_version, NULL, "", NULL},
        {"timeLock", (getter)wrapping_dap_chain_tx_out_std_get_timelock, NULL, "", NULL},
        {"usedBy", (getter)wrapping_dap_chain_tx_out_std_get_used_by, NULL, "", NULL},
        {}
};

PyTypeObject DapChainTxOutStdObjectType = DAP_PY_TYPE_OBJECT(
        "CellFrame.ChainTxOutStd", sizeof(PyDapChainTXOutStdObject),
        "Chain standard tx out object",
        .tp_getset = DapChainTxOutStdGetsSetsDef);

PyObject *wrapping_dap_chain_tx_out_std_get_addr(PyObject *self, void UNUSED_ARG *closure)
{
    PyDapChainAddrObject *obj_addr = PyObject_New(PyDapChainAddrObject, &DapChainAddrObjectType);
    obj_addr->addr = DAP_DUP(&((PyDapChainTXOutStdObject *)self)->out->addr);
    return (PyObject *)obj_addr;
}

PyObject *wrapping_dap_chain_tx_out_std_get_token(PyObject *self, void UNUSED_ARG *closure)
{
    return Py_BuildValue("s", ((PyDapChainTXOutStdObject *)self)->out->token);
}

PyObject *wrapping_dap_chain_tx_out_std_get_value(PyObject *self, void UNUSED_ARG *closure)
{
    DapMathObject *l_math = PyObject_New(DapMathObject, &DapMathObjectType);
    l_math->value = ((PyDapChainTXOutStdObject *)self)->out->value;
    return (PyObject*)l_math;
}

PyObject *wrapping_dap_chain_tx_out_std_get_version(PyObject *self, void UNUSED_ARG *closure)
{
    return Py_BuildValue("h", ((PyDapChainTXOutStdObject *)self)->out->version);
}

PyObject *wrapping_dap_chain_tx_out_std_get_timelock(PyObject *self, void *closure)
{
    return Py_BuildValue("I", ((PyDapChainTXOutStdObject *)self)->out->ts_unlock);
}

PyObject *wrapping_dap_chain_tx_out_std_get_used_by(PyObject *self, void UNUSED_ARG *closure)
{
    PyDapChainTXOutStdObject *obj_out = (PyDapChainTXOutStdObject *)self;
    dap_hash_fast_t l_spender_hash = {0};
    if (!dap_ledger_tx_hash_is_used_out_item(obj_out->ledger, &obj_out->tx_hash, obj_out->idx, &l_spender_hash))
        Py_RETURN_NONE;

    PyDapHashFastObject *obj_hf = PyObject_New(PyDapHashFastObject, &DapChainHashFastObjectType);
    obj_hf->hash_fast = DAP_DUP(&l_spender_hash);
    obj_hf->origin = true;
    return (PyObject *)obj_hf;
}
