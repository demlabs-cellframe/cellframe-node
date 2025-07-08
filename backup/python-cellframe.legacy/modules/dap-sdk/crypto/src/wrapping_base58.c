#include "wrapping_base58.h"

PyObject *dap_encode_base58_py(PyObject *self, PyObject *args){
    PyBytesObject *obj;
    if (!PyArg_ParseTuple(args, "S", &obj)){
        return NULL;
    }
    void *in_void = PyBytes_AsString((PyObject*)obj);
    size_t pySize = (size_t)PyBytes_GET_SIZE(obj);
    char result[DAP_ENC_BASE58_ENCODE_SIZE(pySize)];
    dap_enc_base58_encode(in_void, pySize, result);
    return Py_BuildValue("s", result);
}

PyObject *dap_decode_base58_py(PyObject *self, PyObject *args){
    const char *in_str;
    if (!PyArg_ParseTuple(args, "s", &in_str)){
        return NULL;
    }
    void *res = DAP_NEW_SIZE(void*, DAP_ENC_BASE58_DECODE_SIZE(strlen(in_str)));
    size_t decrypted_size = dap_enc_base58_decode(in_str, res);
    PyBytesObject *return_object = (PyBytesObject*)PyBytes_FromStringAndSize(res, (Py_ssize_t)decrypted_size);
    return Py_BuildValue("O", return_object);
}
