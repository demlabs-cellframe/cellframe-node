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

#ifndef _WRAPPING_DAP_PKEY_
#define _WRAPPING_DAP_PKEY_

#include <Python.h>
#include "dap_pkey.h"
#include "wrapping_dap_hash.h"

extern PyTypeObject DapPkeyTypeObject_DapPkeyTypeObjectType;

/* ----------------------------------- */

typedef struct PyDapPkey{
    PyObject_HEAD
    dap_pkey_t *pkey;
}PyDapPkeyObject;

PyObject *wrapping_dap_pkey_get_type(PyObject *self, void *closure);
PyObject *wrapping_dap_pkey_get_hash(PyObject *self, void *closure);
PyObject *wrapping_dap_pkey_get_size(PyObject *self, void *closure);
PyObject *wrapping_dap_pkey_to_bytes(PyObject *self, PyObject *args);
PyObject *wrapping_dap_pkey_from_bytes(PyObject *self, PyObject *args);
PyObject *wrapping_dap_pkey_encrypt(PyDapPkeyObject *self, PyObject *args);

extern PyTypeObject DapPkeyObject_DapPkeyObjectType;

/* ----------------------------------- */

#endif //_WRAPPING_DAP_PKEY_
