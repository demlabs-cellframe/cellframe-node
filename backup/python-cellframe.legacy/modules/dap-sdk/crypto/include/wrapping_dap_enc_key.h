/*
 * Authors:
 * Alexey Stratulat <alexey.stratulat@demlabs.net>
 * DeM Labs Inc.   https://demlabs.net
 * CellFrame       https://cellframe.net
 * Sources         https://gitlab.demlabs.net/cellframe
 * Copyright  (c) 2017-2020
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
#pragma once

#include "dap_enc_key.h"
#include "Python.h"
#include "dap_common.h"
#include "libdap_crypto_key_python.h"
#include "dap_strfuncs.h"

#ifdef __cplusplus
extern "C" {
#endif


PyObject* dap_enc_key_get_enc_size_py(PyObject *self, PyObject *args);//dap_enc_key_t * a_key, const size_t buf_in_size); -> size_t
PyObject* dap_enc_key_get_dec_size_py(PyObject *self, PyObject *args);//dap_enc_key_t * a_key, const size_t buf_in_size); -> size_t


// allocate memory for key struct
PyObject* dap_enc_key_new_py(PyObject *self, PyObject *args);//dap_enc_key_type_t a_key_type);     ->dap_enc_key_t*


// default gen key
PyObject *dap_enc_key_new_generate_py(PyObject *self, PyObject *args);//dap_enc_key_type_t key_type, const void *kex_buf,  ->dap_enc_key_t*
                                        //size_t kex_size, const void* seed,
                                        //size_t seed_size, size_t key_size);

// update struct dap_enc_key_t after insert foreign keys
PyObject* dap_enc_key_update_py(PyObject *self, PyObject *args);//dap_enc_key_t *a_key);            ->void

// for asymmetric gen public key
PyObject *dap_enc_gen_pub_key_from_priv_py(PyObject *self, PyObject *args);//struct dap_enc_key *a_key, void **priv_key, size_t *alice_msg_len);  ->dap_enc_key_t *


PyObject *dap_enc_ser_pub_key_size_py(PyObject *self, PyObject *args);//dap_enc_key_t *a_key); ->size_t
PyObject *dap_enc_gen_key_public_py(PyObject *self, PyObject *args);//dap_enc_key_t *a_key, void * a_output); ->int


#ifdef __cplusplus
}
#endif
