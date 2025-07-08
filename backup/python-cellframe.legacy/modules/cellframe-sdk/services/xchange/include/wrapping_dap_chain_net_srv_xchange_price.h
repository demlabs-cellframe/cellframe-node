/*
 * Authors:
 * Alexey Stratulat <alexey.stratulat@demlabs.net>
 * DeM Labs Inc.   https://demlabs.net
 * CellFrame       https://cellframe.net
 * Sources         https://gitlab.demlabs.net/cellframe
 * Copyright  (c) 2017-2024
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
#include <Python.h>
#include "dap_chain_net_srv_xchange.h"

typedef struct PyDapChainNetSrvXchangePrice {
    PyObject_HEAD
    dap_chain_net_srv_xchange_price_t *price;
}PyDapChainNetSrvXchangeOrderObject;

static PyObject *CellFrame_Xchange_Price_error;

PyObject *wrapping_dap_chain_net_srv_xchange_price_get_token_sell(PyObject *self, void *closure);
PyObject *wrapping_dap_chain_net_srv_xchange_price_get_datoshi_sell(PyObject *self, void *closure);
PyObject *wrapping_dap_chain_net_srv_xchange_price_get_net(PyObject *self, void *closure);
PyObject *wrapping_dap_chain_net_srv_xchange_price_get_token_buy(PyObject *self, void *closure);
PyObject *wrapping_dap_chain_net_srv_xchange_price_get_rate(PyObject *self, void *closure);
PyObject *wrapping_dap_chain_net_srv_xchange_price_get_fee(PyObject *self, void *closure);

PyObject *wrapping_dap_chain_net_srv_xchange_price_get_tx_hash(PyObject *self, void *closure);
PyObject *wrapping_dap_chain_net_srv_xchange_price_get_completion_rate(PyObject *self, void *closure);
PyObject *wrapping_dap_chain_net_srv_xchange_price_get_status(PyObject *self, void *closure);
PyObject *wrapping_dap_chain_net_srv_xchange_price_get_order_hash(PyObject *self, void *closure);
PyObject *wrapping_dap_chain_net_srv_xchange_price_get_order_creator_address(PyObject *self, void *closure);
PyObject *wrapping_dap_chain_net_srv_xchange_price_get_order_creation_date(PyObject *self, void *closure);

PyObject *wrapping_dap_chain_net_srv_xchange_price_purchase(PyObject *self, PyObject *argv);
PyObject *wrapping_dap_chain_net_srv_xchange_price_invalidate(PyObject *self, PyObject *argv);

extern PyTypeObject PyDapChainNetSrvXchangeOrderObjectType;
