/*
 * Authors:
 * Alexey Stratulat <alexey.stratulat@demlabs.net>
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

#include "Python.h"
#include "dap_enc_oaes.h"
#include "dap_common.h"
#include "libdap_crypto_key_python.h"

#ifdef __cplusplus
extern "C" {
#endif

PyObject *dap_enc_oaes_key_new_py(PyObject *self, PyObject *args);
PyObject *dap_enc_oaes_key_delete_py(PyObject *self, PyObject *args);
PyObject *dap_enc_oaes_key_generate_py(PyObject *self, PyObject *args);

PyObject *dap_enc_oaes_calc_decode_size_py(PyObject *self, PyObject *args);
PyObject *dap_enc_oaes_calc_encode_size_py(PyObject *self, PyObject *args);

PyObject *dap_enc_oaes_decrypt_py(PyObject *self, PyObject *args);
PyObject *dap_enc_oaes_encrypt_py(PyObject *self, PyObject *args);

// Writes result ( out ) in already allocated buffer
PyObject *dap_enc_oaes_decrypt_fast_py(PyObject *self, PyObject *args);
// Writes result ( out ) in already allocated buffer
PyObject *dap_enc_oaes_encrypt_fast_py(PyObject *self, PyObject *args);



#ifdef __cplusplus
}
#endif


