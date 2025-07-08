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

typedef struct PyDapChainNetSrvXchange{
    PyObject_HEAD
}PyDapChainNetSrvXchangeObject;

static PyObject *CellFrame_Xchange_error;

PyObject *wrapping_dap_chain_net_srv_xchange_get_orders(PyObject *self, PyObject *argv);
PyObject *wrapping_dap_chain_net_srv_xchange_create(PyObject *self, PyObject *argv);

extern PyTypeObject DapChainNetSrvXchangeObjectType;