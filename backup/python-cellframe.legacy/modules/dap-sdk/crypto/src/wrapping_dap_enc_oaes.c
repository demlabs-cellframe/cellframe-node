#include "wrapping_dap_enc_oaes.h"


PyObject *dap_enc_oaes_key_new_py(PyObject *self, PyObject *args){
    PyObject *in_key;
    if (PyArg_ParseTuple(args, "O", &in_key)){
        return NULL;
    }
    dap_enc_oaes_key_new(((PyCryptoKeyObject*)in_key)->key);
    return  PyLong_FromLong(0);
}
PyObject *dap_enc_oaes_key_delete_py(PyObject *self, PyObject *args){
    PyObject *in_key;
    if (PyArg_ParseTuple(args, "O", &in_key)){
        return NULL;
    }
    dap_enc_oaes_key_delete(((PyCryptoKeyObject*)in_key)->key);
    return  PyLong_FromLong(0);
}
PyObject *dap_enc_oaes_key_generate_py(PyObject *self, PyObject *args){
    PyObject *in_key;
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
    dap_enc_oaes_key_generate(((PyCryptoKeyObject*)in_key)->key, kex_buf, in_kex_size, seed_buf, in_seed_size, key_size);
    return  PyLong_FromLong(0);
}

PyObject *dap_enc_oaes_calc_decode_size_py(PyObject *self, PyObject *args){
    size_t size;
    if (!PyArg_ParseTuple(args, "n", &size)){
        return NULL;
    }
    size_t new_size = dap_enc_oaes_calc_decode_size(size);
    return PyLong_FromSize_t(new_size);
}
PyObject *dap_enc_oaes_calc_encode_size_py(PyObject *self, PyObject *args){
    size_t size;
    if (!PyArg_ParseTuple(args, "n", &size)){
        return NULL;
    }
    size_t new_size = dap_enc_oaes_calc_encode_size(size);
    return PyLong_FromSize_t(new_size);
}

PyObject *dap_enc_oaes_decrypt_py(PyObject *self, PyObject *args){
    //TODO
    return PyLong_FromLong(0);
}
PyObject *dap_enc_oaes_encrypt_py(PyObject *self, PyObject *args){
    //TODO
    return PyLong_FromLong(0);
}

// Writes result ( out ) in already allocated buffer
PyObject *dap_enc_oaes_decrypt_fast_py(PyObject *self, PyObject *args){
    PyObject *in_key;
    PyBytesObject *a_in;
    size_t a_in_size;
    size_t buf_out_size;
    if (!PyArg_ParseTuple(args, "O|S|n|n", &in_key, &a_in, &a_in_size, &buf_out_size)){
        return NULL;
    }
    void *in = PyBytes_AsString((PyObject*)a_in);
    void *out = DAP_NEW_SIZE(void*, buf_out_size);
    size_t res_denc_size = dap_enc_oaes_decrypt_fast(((PyCryptoKeyObject*)in_key)->key, in, a_in_size, out, buf_out_size);
    PyBytesObject *bytes_out = (PyBytesObject*)PyBytes_FromStringAndSize(out, (Py_ssize_t)res_denc_size);
    return Py_BuildValue("S", bytes_out);
}
// Writes result ( out ) in already allocated buffer
PyObject *dap_enc_oaes_encrypt_fast_py(PyObject *self, PyObject *args){
    PyObject *in_key;
    PyBytesObject *a_in;
    size_t a_in_size;
    size_t buf_out_size;
    if (!PyArg_ParseTuple(args, "O|S|n|n", &in_key, &a_in, &a_in_size, &buf_out_size)){
        return NULL;
    }
    void *in = PyBytes_AsString((PyObject*)a_in);
    void *out = DAP_NEW_SIZE(void*, buf_out_size);
    size_t res_enc_size = dap_enc_oaes_encrypt_fast(((PyCryptoKeyObject*)in_key)->key, in, a_in_size, out, buf_out_size);
    PyBytesObject *bytes_out = (PyBytesObject*)PyBytes_FromStringAndSize(out, (Py_ssize_t)res_enc_size);
    return Py_BuildValue("S", bytes_out);
}
