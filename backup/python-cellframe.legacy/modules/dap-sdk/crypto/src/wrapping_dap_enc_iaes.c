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
#include "wrapping_dap_enc_iaes.h"

#define LOG_TAG "wrapping-dap-enc-iaes"


PyObject* dap_enc_iaes_key_new_py(PyObject *self, PyObject *args){
    PyObject *obj_key;
    if (PyArg_ParseTuple(args, "O", &obj_key)){
        return NULL;
    }
    dap_enc_aes_key_new(((PyCryptoKeyObject*)obj_key)->key);
    return  PyLong_FromLong(0);
}

PyObject* dap_enc_iaes_key_delete_py(PyObject *self, PyObject *args){
    PyObject *obj_key;
    if (PyArg_ParseTuple(args, "O", &obj_key)){
        return NULL;
    }
    dap_enc_aes_key_delete(((PyCryptoKeyObject*)obj_key)->key);
    return  PyLong_FromLong(0);
}

PyObject* dap_enc_iaes_key_generate_py(PyObject *self, PyObject *args){
    // TODO
    PyObject* in_key;
    PyBytesObject *in_kex_buf;
    size_t in_kex_size;
    PyBytesObject *in_seed;
    size_t in_seed_size;
    if (PyArg_ParseTuple(args, "O|S|n|S|n", &in_key, &in_kex_buf, &in_kex_size, &in_seed, &in_seed_size)){
        return NULL;
    }
    size_t key_size = sizeof(((PyCryptoKeyObject*)in_key)->key);
    void* kex_buf = NULL;
    PyBytes_AsStringAndSize((PyObject*)in_kex_buf, kex_buf, (Py_ssize_t*)in_kex_size);
    void* seed_buf = NULL;
    PyBytes_AsStringAndSize((PyObject*)in_seed, seed_buf, (Py_ssize_t*)in_seed_size);
    dap_enc_aes_key_generate(((PyCryptoKeyObject*)in_key)->key, kex_buf, in_kex_size, seed_buf, in_seed_size, key_size);
    return  PyLong_FromLong(0);
}

PyObject* dap_enc_iaes256_calc_encode_size_py(PyObject *self, PyObject *args)
{
    UNUSED(self);
    size_t size;
    if (!PyArg_ParseTuple(args, "n", &size)){
        return NULL;
    }
    size_t new_size = dap_enc_iaes256_calc_encode_size(size);
    return PyLong_FromSize_t(new_size);
}


PyObject* dap_enc_iaes256_calc_decode_size_py(PyObject *self, PyObject *args)
{
    UNUSED(self);
    size_t size;
    if (!PyArg_ParseTuple(args, "n", &size)){
        return NULL;
    }
    size_t new_size = dap_enc_iaes256_calc_decode_max_size(size);
    return PyLong_FromSize_t(new_size);
}

PyObject* dap_enc_iaes256_cbc_decrypt_py(PyObject *self, PyObject *args)
{
    UNUSED(self);
    UNUSED(args);

    //TODO
    return PyLong_FromLong(0);
}
PyObject* dap_enc_iaes256_cbc_encrypt_py(PyObject *self, PyObject *args)
{
    UNUSED(self);
    UNUSED(args);
    //TODO
    return PyLong_FromLong(0);
}

// Writes result ( out ) in already allocated buffer
PyObject* dap_enc_iaes256_cbc_decrypt_fast_py(PyObject *self, PyObject *args)
{
    UNUSED(self);
    PyObject* in_key;
    PyBytesObject *a_in;
    size_t a_in_size;
    size_t buf_out_size;
    if (!PyArg_ParseTuple(args, "O|S|n|n", &in_key, &a_in, &a_in_size, &buf_out_size)){
        return NULL;
    }
    void *in = PyBytes_AsString((PyObject*)a_in);
    void *out = DAP_NEW_SIZE(void*, buf_out_size);
    size_t res_denc_size = dap_enc_iaes256_cbc_decrypt_fast(((PyCryptoKeyObject*)in_key)->key, in, a_in_size, out, buf_out_size);
    PyBytesObject *bytes_out = (PyBytesObject*)PyBytes_FromStringAndSize(out, (Py_ssize_t)res_denc_size);
    return Py_BuildValue("S", bytes_out);
}

// if "a_in size mod IAES_BLOCK_SIZE = 0" encryption will be faster
PyObject* dap_enc_iaes256_cbc_encrypt_fast_py(PyObject *self, PyObject *args)
{
    UNUSED(self);
    PyObject *in_key;
    PyBytesObject *a_in;
    size_t a_in_size;
    size_t buf_out_size;
    if (!PyArg_ParseTuple(args, "O|S|n|n", &in_key, &a_in, &a_in_size, &buf_out_size)){
        return NULL;
    }
    void *in = PyBytes_AsString((PyObject*)a_in);
    void *out = DAP_NEW_SIZE(void*, buf_out_size);
    size_t res_enc_size = dap_enc_iaes256_cbc_encrypt_fast(((PyCryptoKeyObject*)in_key)->key, in, a_in_size, out, buf_out_size);
    PyBytesObject *bytes_out = (PyBytesObject*)PyBytes_FromStringAndSize(out, (Py_ssize_t)res_enc_size);
    return Py_BuildValue("S", bytes_out);
}

