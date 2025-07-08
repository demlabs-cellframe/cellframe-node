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
#include "wrapping_dap_enc_key.h"
#include "wrapping_dap_enc_key_type.h"

#define LOG_TAG "wrapping-dap-enc-key"

PyObject* dap_enc_key_get_enc_size_py(PyObject *self, PyObject *args){
    PyObject *in_key;
    size_t buff_in_size;
    if (!PyArg_ParseTuple(args, "O|i", &in_key, &buff_in_size)){
        return NULL;
    }
//    dap_enc_key_t *key = key_list_get_key(keys, key_id);
//    if (key == NULL)
//        return NULL;
    size_t size_buff = dap_enc_key_get_enc_size(((PyCryptoKeyObject*)in_key)->key->type, buff_in_size);
    if (size_buff == 0)
        return NULL;
    return  PyLong_FromSize_t(size_buff);
}

PyObject* dap_enc_key_get_dec_size_py(PyObject *self, PyObject *args){
    PyObject *in_key;
    size_t buff_in_size;
    if (!PyArg_ParseTuple(args, "O|i", &in_key, &buff_in_size)){
        return NULL;
    }
//    dap_enc_key_t *key = key_list_get_key(keys, key_id);
//    if (key == NULL)
//        return NULL;
    size_t size_buff = dap_enc_key_get_dec_size(((PyCryptoKeyObject*)in_key)->key->type, buff_in_size);
    if (size_buff == 0)
        return NULL;
    return  PyLong_FromSize_t(size_buff);
}

// allocate memory for key struct
PyObject* dap_enc_key_new_py(PyObject *self, PyObject *args){
    PyObject *obj_type_key;
    if(!PyArg_ParseTuple(args, "O", &obj_type_key)){
        return NULL;
    }
    if (!PyObject_TypeCheck(obj_type_key, &DapCryptoKeyTypeObjectType)) {
        PyErr_SetString(PyExc_AttributeError, "An invalid argument was passed to a function. This must "
                                              "be the type of key that needs to be created.");
        return NULL;
    }
    dap_enc_key_t *new_key = dap_enc_key_new(((PyCryptoKeyTypeObject *)obj_type_key)->type);
    PyObject *obj = _PyObject_New(&PyCryptoKeyObjectType);
    ((PyCryptoKeyObject*)obj)->key = new_key;
    return  Py_BuildValue("O", obj);
}

/// default gen key
PyObject *dap_enc_key_new_generate_py(PyObject *self, PyObject *args){
    uint8_t in_type_key;
    PyObject *obj_kex_buf;
    PyObject *obj_seed = NULL;
    size_t in_key_size;
    if (!PyArg_ParseTuple(args, "iOn|O", &in_type_key, &obj_kex_buf, &in_key_size, &obj_seed)){
        return NULL;
    }
    void *l_kex_buf = NULL;
    size_t l_kex_buf_size = 0;
    void *l_seed = NULL;
    size_t l_seed_size = 0;
    if (PyUnicode_Check(obj_kex_buf)){
        const char *l_kex_buf_str = PyUnicode_AsUTF8(obj_kex_buf);
        l_kex_buf_size = dap_strlen(l_kex_buf_str);
        if (l_kex_buf_size < 1){
            PyErr_SetString(PyExc_SyntaxError, "The kex buffer size must be grater than one character");
            return NULL;
        }
        l_kex_buf = DAP_NEW_SIZE(char, l_kex_buf_size);
    } else {
        if (PyBytes_Check(obj_kex_buf)) {
            l_kex_buf = PyBytes_AsString(obj_kex_buf);
            l_kex_buf_size = PyBytes_Size(obj_kex_buf);
        } else {
            PyErr_SetString(PyExc_SyntaxError, "The second argument must be either a string or bytes");
            return NULL;
        }
    }
    if (obj_seed != NULL){
        if (PyUnicode_Check(obj_seed)){
            const char *l_seed_buf_str = PyUnicode_AsUTF8(obj_seed);
            l_seed_size = dap_strlen(l_seed_buf_str);
            l_seed = DAP_NEW_SIZE(char, l_seed_size);
            memcpy(l_seed, l_seed_buf_str, l_seed_size);
        }else{
            if (PyBytes_Check(obj_seed)){
                l_seed = PyBytes_AsString(obj_seed);
                l_seed_size = PyBytes_Size(obj_seed);
            }else{
                PyErr_SetString(PyExc_SyntaxError, "The second argument must be either a string or bytes");
                return NULL;
            }
        }
    }
    PyCryptoKeyObject *obj_key = PyObject_New(PyCryptoKeyObject, &PyCryptoKeyObjectType);
    obj_key->key = dap_enc_key_new_generate(in_type_key, l_kex_buf, l_kex_buf_size,
                                            l_seed, l_seed_size, in_key_size);
    return (PyObject*)obj_key;
}

// update struct dap_enc_key_t after insert foreign keys
PyObject* dap_enc_key_update_py(PyObject *self, PyObject *args){
    PyObject *in_key;
    if (!PyArg_ParseTuple(args, "O", &in_key)){
        return NULL;
    }
//    dap_enc_key_t *key = key_list_get_key(keys, key_id);
//    if (key == NULL) {
//        return NULL;
//    }
    dap_enc_key_update(((PyCryptoKeyObject*)in_key)->key);
    return PyLong_FromLong(0);
}

// for asymmetric gen public key
PyObject *dap_enc_gen_pub_key_from_priv_py(PyObject *self, PyObject *args){ //NOTE libdap-crypto/src/libdap-crypto.c
    return PyLong_FromLong(0);
}


PyObject *dap_enc_ser_pub_key_size_py(PyObject *self, PyObject *args){
    PyObject *in_key;
    if (PyArg_ParseTuple(args, "h", &in_key)){
        return NULL;
    }
//    dap_enc_key_t *key = key_list_get_key(keys, key_id);
//    if (key == NULL){
//        return NULL;
//    }
    size_t size = dap_enc_ser_pub_key_size(((PyCryptoKeyObject*)in_key)->key);
    return PyLong_FromSize_t(size);
}

PyObject *dap_enc_gen_key_public_py(PyObject *self, PyObject *args){
    PyObject *in_key;
    PyObject *obj;
    if (PyArg_ParseTuple(args, "O|O", &in_key, &obj)){
        return NULL;
    }
//    dap_enc_key_t *key = key_list_get_key(keys, key_id);
//    if (key == NULL){
//        return NULL;
//    }
    int size = dap_enc_gen_key_public(((PyCryptoKeyObject*)in_key)->key, obj);
    return PyLong_FromLong(size);
}
