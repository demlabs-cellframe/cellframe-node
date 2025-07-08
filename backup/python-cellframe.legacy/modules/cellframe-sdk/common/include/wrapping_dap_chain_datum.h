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

#ifndef _WRAPPING_DAP_CHAIN_DATUM_
#define _WRAPPING_DAP_CHAIN_DATUM_
#include "Python.h"
#include "dap_chain.h"
#include "dap_chain_datum.h"
#include "datetime.h"
#include "wrapping_dap_chain_datum_tx.h"
#include "wrapping_dap_chain_datum_token.h"
#include "wrapping_dap_chain_datum_anchor.h"
#include "wrapping_dap_chain_datum_decree.h"

#ifdef __cplusplus
extern "C" {
#endif

/* DAP Chain datum type id */
typedef struct PyDapChainDatumTypeId{
    PyObject_HEAD
    dap_chain_datum_typeid_t *type_id;
}PyDapChainDatumTypeIdObject;

extern PyTypeObject DapChainDatumTypeIdObjectType;

/* -------------------------------- */

typedef struct PyDapChainDatum{
    PyObject_HEAD
    dap_chain_datum_t *datum;
    bool origin;
}PyDapChainDatumObject;

bool PyDapChainDatum_Check(PyObject *self);
void PyDapChainDatumObject_dealloc(PyDapChainDatumObject* self);
PyObject *PyDapChainDatumObject_new(PyTypeObject *type_object, PyObject *args, PyObject *kwds);
PyObject *wrapping_dap_chain_datum_create_from_bytes(PyObject *self, PyObject *args);
PyObject *dap_chain_datum_size_py(PyObject *self, PyObject *args);
PyObject *dap_chain_datum_get_ts_created_py(PyObject *self, void* closure);
PyObject *dap_chain_datum_is_type_tx(PyObject *self, PyObject *args);
PyObject *wrapping_dap_chain_datum_get_datum_tx(PyObject *self, PyObject *args);
PyObject *dap_chain_datum_is_type_token(PyObject *self, PyObject *args);
PyObject *wrapping_dap_chain_datum_get_datum_token(PyObject *self, PyObject *args);
PyObject *dap_chain_datum_is_type_emission(PyObject *self, PyObject *args);
PyObject *wrapping_dap_chain_datum_get_datum_token_emission(PyObject *self, PyObject *args);
PyObject *wrapping_dap_chain_datum_is_type_custom(PyObject *self, PyObject *args);
PyObject *dap_chain_datum_get_type_str_py(PyObject *self, PyObject *args);
PyObject *wrapping_dap_chain_datum_get_type_id_py(PyObject *self, PyObject *args);
PyObject *wrapping_dap_chain_datum_get_hash_py(PyObject *self, void* closure);
PyObject *wrapping_dap_chain_datum_get_version_str_py(PyObject *self, void* closure);
PyObject *wrapping_dap_chain_datum_get_raw_py(PyObject *self, void* closure);
PyObject *wrapping_dap_chain_datum_get_data_raw_py(PyObject *self, void* closure);
PyObject *wrapping_dap_chain_datum_is_type_decree(PyObject *self, PyObject *args);
PyObject *wrapping_dap_chain_datum_get_decree(PyObject *self, PyObject *args);
PyObject *wrapping_dap_chain_datum_is_type_anchor(PyObject *self, PyObject *args);
PyObject *wrapping_dap_chain_datum_get_anchor(PyObject *self, PyObject *args);

extern PyTypeObject DapChainDatumObjectType;
/* -------------------------------- */

/* DAP Chain datum iter*/
typedef struct PyDapChainDatumIter{
    PyObject_HEAD
    dap_chain_datum_iter_t *datum_iter;
}PyDapChainDatumIterObject;

extern PyTypeObject DapChainDatumIterObjectType;
/* -------------------------------- */

#ifdef __cplusplus
}
#endif

#endif //_WRAPPING_DAP_CHAIN_DATUM_
