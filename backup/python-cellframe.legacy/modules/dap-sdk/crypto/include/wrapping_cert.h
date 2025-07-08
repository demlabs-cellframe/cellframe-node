/*
 * Authors:
 * Dmitriy A. Gearasimov <gerasimov.dmitriy@demlabs.net>
 * DeM Labs Inc.   https://demlabs.net
 * CellFrame       https://cellframe.net
 * Sources         https://gitlab.demlabs.net/cellframe
 * Copyright  (c) 2017-2020
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
#pragma once
#define PY_SSIZE_T_CLEAN

#include <Python.h>
#include "dap_common.h"
#include "dap_cert.h"
#include "libdap_crypto_key_python.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct PyCryptoCert{
    PyObject_HEAD
    dap_cert_t * cert;
}PyCryptoCertObject;

int dap_cert_init_py();
void dap_cert_deinit_py();

PyObject* dap_cert_generate_py(PyObject *self, PyObject *args);
PyObject* dap_cert_dump_py(PyObject *self, PyObject *args);
PyObject* dap_cert_pkey_py(PyObject *self, PyObject *args);
PyObject* dap_cert_find_py(PyObject *self, PyObject *args);
PyObject* dap_cert_sign_py(PyObject *self, PyObject *args);
PyObject* dap_cert_cert_sign_add_py(PyObject *self, PyObject *args);
PyObject* dap_cert_cert_signs_py(PyObject *self, PyObject *args);
PyObject* dap_cert_compare_py(PyObject *self, PyObject *args);
PyObject* dap_cert_save_py(PyObject *self, PyObject *args);
PyObject* dap_cert_load_py(PyObject *self, PyObject *args);
PyObject *dap_cert_delete_py(PyObject *self, PyObject *args);
PyObject* dap_cert_folder_add_py(PyObject *self, PyObject *args);
PyObject* dap_cert_folder_get_py(PyObject *self, PyObject *args);
PyObject *wrapping_cert_get_enc_key(PyObject *self, void *closure);

extern PyTypeObject DapCryptoCertObjectType;

static bool PyDapCryptoCertObject_Check(PyObject *self) {
    return PyObject_TypeCheck(self, &DapCryptoCertObjectType);
}

#ifdef __cplusplus
}
#endif
