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
#include "dap_common.h"
#include "dap_cert.h"
#include "dap_strfuncs.h"

#include "libdap-python.h"
#include "wrapping_cert.h"
#include "libdap_crypto_key_python.h"
#include "wrapping_dap_enc_key_type.h"
#include "wrapping_dap_pkey.h"
#define LOG_TAG "wrapping_cert"

PyMethodDef PyCryptoCertMethods[] = {
        {"generate",dap_cert_generate_py , METH_VARARGS | METH_STATIC, "Generate from seed or randomly the new certificate"},
        {"find", dap_cert_find_py, METH_VARARGS | METH_STATIC, ""},
        {"folderAdd", dap_cert_folder_add_py, METH_VARARGS | METH_STATIC, "Add folders with .dcert files in it"},
        {"folderGet", dap_cert_folder_get_py, METH_VARARGS | METH_STATIC, "Get folder by number or the default one"},
        {"load", dap_cert_load_py, METH_VARARGS | METH_STATIC ,""},
        {"dump", dap_cert_dump_py, METH_VARARGS , ""},
        {"pkey", dap_cert_pkey_py, METH_VARARGS , ""},
        {"sign", dap_cert_sign_py, METH_VARARGS , ""},
        {"certSignAdd", dap_cert_cert_sign_add_py, METH_VARARGS,  ""},
        {"certSigns", dap_cert_cert_signs_py, METH_VARARGS , ""},
        {"compare", dap_cert_compare_py, METH_VARARGS, ""},
        {"save", dap_cert_save_py, METH_VARARGS , "Save to the first directory in cert folders list"},
        {"delete", dap_cert_delete_py, METH_VARARGS, ""},
        {}
};

static PyGetSetDef PyCryptoCertGetSets[] = {
        {"key", (getter)wrapping_cert_get_enc_key, NULL, NULL, NULL},
        {}
};

PyTypeObject DapCryptoCertObjectType = DAP_PY_TYPE_OBJECT(
        "DAP.Crypto.Cert", sizeof(PyCryptoCertObject),
        "Crypto cert object",
        .tp_methods = PyCryptoCertMethods,
        .tp_getset = PyCryptoCertGetSets);

PyObject* dap_cert_generate_py(PyObject *self, PyObject *args)
{
    const char *l_cert_name = NULL;
    const char * l_seed = NULL;

    const char *l_arg_cert_name = NULL;
//    dap_enc_key_type_t l_arg_cert_key_type = DAP_ENC_KEY_TYPE_SIG_DILITHIUM;
    PyObject *l_arg_key_type = NULL;
    const char *l_arg_seed_string = NULL;

    if (!PyArg_ParseTuple(args, "s|Os", &l_arg_cert_name, &l_arg_key_type, &l_arg_seed_string) ){
        PyErr_SetString(PyExc_SyntaxError, "Wrong argument list");
        return NULL;
    }

    if (l_arg_cert_name != 0)
        l_cert_name = l_arg_cert_name;
    else {
        PyErr_SetString(PyExc_SyntaxError, "Certificate name is None");
        return NULL;
    }

    if (l_arg_seed_string != 0)
        l_seed = l_arg_seed_string;

    PyCryptoCertObject *obj_cert = PyObject_New(PyCryptoCertObject, &DapCryptoCertObjectType);
    dap_enc_key_type_t l_arg_cert_key_type = l_arg_key_type ?
            ((PyCryptoKeyTypeObject*)l_arg_key_type)->type : DAP_ENC_KEY_TYPE_SIG_DILITHIUM;
    obj_cert->cert = l_seed ? dap_cert_generate_mem_with_seed( l_cert_name, l_arg_cert_key_type, l_seed, strlen(l_seed) )
              :dap_cert_generate_mem( l_cert_name,l_arg_cert_key_type );
    if (!obj_cert->cert){
        Py_XDECREF(obj_cert);
        Py_RETURN_NONE;
    }
    return (PyObject*)obj_cert;
}

PyObject* dap_cert_dump_py(PyObject *self, PyObject *args)
{
    (void) self;
    (void) args;
    /// TODO: Implement it!
    PyErr_SetString(PyExc_TypeError, "Unimplemented function");
    return NULL;
}

PyObject* dap_cert_pkey_py(PyObject *self, PyObject *args)
{
    (void) args;
    size_t l_bytes_size = 0;
    uint8_t *l_bytes = dap_enc_key_serialize_pub_key(((PyCryptoCertObject*)self)->cert->enc_key, &l_bytes_size);
    if (l_bytes_size == 0) {
        PyErr_SetString(PyExc_ValueError, "This key type does not support serialization into a public key.");
        return NULL;
    }
    PyDapPkeyObject *obj_pkey = PyObject_New(PyDapPkeyObject, &DapPkeyObject_DapPkeyObjectType);
    obj_pkey->pkey = DAP_NEW_Z_SIZE(dap_pkey_t, sizeof(dap_pkey_t) + l_bytes_size);
    obj_pkey->pkey->header.size = l_bytes_size;
    if (((PyCryptoCertObject*)self)->cert->enc_key->type == DAP_ENC_KEY_TYPE_SIG_DILITHIUM) {
        obj_pkey->pkey->header.type.type = DAP_PKEY_TYPE_SIG_DILITHIUM;
        memcpy(obj_pkey->pkey->pkey, l_bytes, l_bytes_size);
        obj_pkey->pkey->header.size = l_bytes_size;
    }
    return (PyObject*)obj_pkey;
}

PyObject* dap_cert_find_py(PyObject *self, PyObject *args)
{
    (void) self;
    (void) args;
    /// TODO: Implement it!
    PyErr_SetString(PyExc_TypeError, "Unimplemented function");
    return NULL;
}

PyObject* dap_cert_sign_py(PyObject *self, PyObject *args)
{
    (void) self;
    (void) args;
    /// TODO: Implement it!
    PyErr_SetString(PyExc_TypeError, "Unimplemented function");
    return NULL;
}

PyObject* dap_cert_cert_sign_add_py(PyObject *self, PyObject *args)
{
    (void) self;
    (void) args;
    /// TODO: Implement it!
    PyErr_SetString(PyExc_TypeError, "Unimplemented function");
    return NULL;
}

PyObject* dap_cert_cert_signs_py(PyObject *self, PyObject *args)
{
    (void) self;
    (void) args;
    /// TODO: Implement it!
    PyErr_SetString(PyExc_TypeError, "Unimplemented function");
    return NULL;
}

PyObject* dap_cert_compare_py(PyObject *self, PyObject *args)
{
    (void) self;
    (void) args;
    /// TODO: Implement it!
    PyErr_SetString(PyExc_TypeError, "Unimplemented function");
    return NULL;
}

PyObject* dap_cert_save_py(PyObject *self, PyObject *args)
{
    (void) args;
    int res = dap_cert_save_to_folder(((PyCryptoCertObject*)self)->cert, dap_cert_get_folder(0) );
    return PyLong_FromLong(res);
}

PyObject* dap_cert_load_py(PyObject *self, PyObject *args)
{
    const char *l_cert_name;
    if (!PyArg_ParseTuple(args, "s", &l_cert_name)) {
        return NULL;
    }
    dap_cert_t *l_ret = dap_cert_find_by_name(l_cert_name);
    if (!l_ret)
        Py_RETURN_NONE;
    if (!self) {
        self = _PyObject_New(&DapCryptoCertObjectType);
    }
    ((PyCryptoCertObject *)self)->cert = l_ret;
    return self;
}

PyObject* dap_cert_close_py(PyObject *self, PyObject *args)
{
    (void) self;
    (void) args;
    /// TODO: Implement it!
    PyErr_SetString(PyExc_TypeError, "Unimplemented function");
    return NULL;
}


PyObject *dap_cert_delete_py(PyObject *self, __attribute__((unused)) PyObject *args)
{
    PyCryptoCertObject *certObject = (PyCryptoCertObject *)self;
    dap_cert_delete( certObject->cert );
    Py_RETURN_NONE;
}


PyObject* dap_cert_folder_add_py(PyObject *self, PyObject *args)
{
    (void) self;
    (void) args;
    /// TODO: Implement it!
    PyErr_SetString(PyExc_TypeError, "Unimplemented function");
    return NULL;
}

PyObject* dap_cert_folder_get_py(PyObject *self, PyObject *args)
{
    (void)self;
    const char *a_folder_path;
    if(!PyArg_ParseTuple(args, "s", &a_folder_path))
        return NULL;
    dap_cert_add_folder(a_folder_path);
    return PyLong_FromLong(0);
}

PyObject *wrapping_cert_get_enc_key(PyObject *self, void *closure){
    (void)closure;
    PyCryptoKeyObject *obj_key = PyObject_New(PyCryptoKeyObject, &PyCryptoKeyObjectType);
    obj_key->key = ((PyCryptoCertObject*)self)->cert->enc_key;
    return (PyObject*)obj_key;
}

int dap_cert_init_py(void)
{
    return dap_cert_init();
}

void dap_cert_deinit_py(void)
{
    dap_cert_deinit();
}

