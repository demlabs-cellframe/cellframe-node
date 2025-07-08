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

#ifndef _WRAPPING_DAP_CHAIN_DATUM_TOKEN_
#define _WRAPPING_DAP_CHAIN_DATUM_TOKEN_

#include "Python.h"
#include "dap_chain_datum_token.h"
#include "wrapping_dap_chain_common.h"
#include "dap_tsd.h"

#ifdef __cplusplus
extern "C" {
#endif

/* DAP chain datum token */

typedef struct PyDapChainDatumToken{
    PyObject_HEAD
    dap_chain_datum_token_t *token;
    size_t token_size;
    bool copy;
}PyDapChainDatumTokenObject;

PyObject *wrapping_dap_chain_datum_token_get_ticker(PyObject *self, void *closure);
PyObject *wrapping_dap_chain_datum_token_get_type_str(PyObject *self, void *closure);
//PyObject *wrapping_dap_chain_datum_token_get_size(PyObject *self, void *closure);
PyObject *wrapping_dap_chain_datum_token_get_data(PyObject *self, void *closure);

bool DapChainDatumToken_Check(PyObject *self);

extern PyTypeObject DapChainDatumTokenObjectType;

/* ------------------------------------------- */

/* DAP chain datum token emission */

typedef struct PyDapChainDatumTokenEmission{
    PyObject_HEAD
    dap_chain_datum_token_emission_t *token_emission;
    size_t token_size;
    bool copy;
} PyDapChainDatumTokenEmissionObject;

void PyDapChainDatumTokenEmissionObject_dealloc(PyObject *self);

int PyDapChainDatumTokenEmissionObject_init(PyDapChainDatumTokenEmissionObject *self, PyObject *argv, PyObject *kwds);

PyObject *wrapping_dap_chain_datum_token_emission_get_hash(PyObject *self, void *closure);
PyObject *wrapping_dap_chain_datum_token_emission_get_version(PyObject *self, void *closure);
PyObject *wrapping_dap_chain_datum_token_emission_get_type_str(PyObject *self, void *closure);
PyObject *wrapping_dap_chain_datum_token_emission_get_ticker(PyObject *self, void *closure);
PyObject *wrapping_dap_chain_datum_token_emission_get_addr(PyObject *self, void *closure);
PyObject *wrapping_dap_chain_datum_token_emission_get_value(PyObject *self, void *closure);
PyObject *wrapping_dap_chain_datum_token_emission_get_nonce(PyObject *self, void *closure);
PyObject *wrapping_dap_chain_datum_token_emission_get_data(PyObject *self, void *closure);
PyObject *wrapping_dap_chain_datum_token_emission_get_sign_count(PyObject *self, void *closure);
PyObject *wrapping_dap_chain_datum_token_emission_get_signs(PyObject *self, void *closure);
PyObject *wrapping_dap_chain_datum_emission_add_sign(PyObject*self, PyObject *args);
PyObject *wrapping_dap_chain_datum_emission_append_sign(PyObject*self, PyObject *args);
PyObject *wrapping_dap_chain_datum_emission_add_tsd(PyObject*self, PyObject *args);
PyObject *wrapping_dap_chain_datum_emission_get_tsd(PyObject*self, PyObject *args);

extern PyTypeObject DapChainDatumTokenEmissionObjectType;

static bool PyDapChainDatumTokenEmissionObject_check(PyObject *self){
    return PyObject_TypeCheck(self, &DapChainDatumTokenEmissionObjectType);
}

/* ------------------------------------------- */

#ifdef __cplusplus
}
#endif

#endif //_WRAPPING_DAP_CHAIN_DATUM_TOKEN_
