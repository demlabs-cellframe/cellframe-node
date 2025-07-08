#include "wrapping_dap_pkey.h"
#include "dap_enc.h"


static PyGetSetDef PyDapPkeyGetsSetsDef[] = {
        {"hash", (getter)wrapping_dap_pkey_get_hash, NULL, NULL, NULL},
        {"type", (getter)wrapping_dap_pkey_get_type, NULL, NULL, NULL},
        {"size", (getter)wrapping_dap_pkey_get_size, NULL, NULL, NULL},
        {}
};

static PyMethodDef PyDapPkeyMethodsDef[] = {
        {"toBytes", (PyCFunction)wrapping_dap_pkey_to_bytes, METH_NOARGS, ""},
        {"fromBytes", (PyCFunction)wrapping_dap_pkey_from_bytes, METH_VARARGS | METH_STATIC, ""},
        {"encrypt", (PyCFunction)wrapping_dap_pkey_encrypt, METH_VARARGS, ""},
        {}
};

void PyDapPkeyObject_free(PyDapPkeyObject *self) {
    DAP_DELETE(self->pkey);
    Py_TYPE(self)->tp_free((PyObject*)self);
}

PyTypeObject DapPkeyObject_DapPkeyObjectType = DAP_PY_TYPE_OBJECT(
        "CellFrame.Pkey", sizeof(PyDapPkeyObject),
        "Pkey object",
        .tp_methods = PyDapPkeyMethodsDef,
        .tp_dealloc = (destructor)PyDapPkeyObject_free,
        .tp_getset = PyDapPkeyGetsSetsDef);

PyObject *wrapping_dap_pkey_get_type(PyObject *self, void *closure){
    (void)closure;
    const char *str = dap_pkey_type_to_str(((PyDapPkeyObject*)self)->pkey->header.type);
    return Py_BuildValue("s", str);
}

PyObject *wrapping_dap_pkey_get_hash(PyObject *self, void *closure){
    (void)closure;
    PyDapHashFastObject *obj_hash = PyObject_New(PyDapHashFastObject, &DapChainHashFastObjectType);
    obj_hash->hash_fast =  DAP_NEW_Z(dap_chain_hash_fast_t);
    dap_pkey_get_hash(((PyDapPkeyObject*)self)->pkey, obj_hash->hash_fast);
    obj_hash->origin = true;
    return (PyObject*)obj_hash;
}
PyObject *wrapping_dap_pkey_get_size(PyObject *self, void *closure){
    (void)closure;
    return Py_BuildValue("I", ((PyDapPkeyObject*)self)->pkey->header.size);
}

PyObject *wrapping_dap_pkey_to_bytes(PyObject *self, PyObject *args){
    (void)args;
    return PyBytes_FromStringAndSize((char*)((PyDapPkeyObject*)self)->pkey,
                                     sizeof(dap_pkey_t) + ((PyDapPkeyObject*)self)->pkey->header.size);
}

PyObject *wrapping_dap_pkey_from_bytes(PyObject *self, PyObject *args) {
    (void)self;
    PyObject *obj_bytes;
    if (!PyArg_ParseTuple(args, "O", &obj_bytes))
        return NULL;
    if (!PyBytes_Check(obj_bytes)) {
        PyErr_SetString(PyExc_ValueError, "An invalid argument was passed, the incoming argument must be of type bytes.");
        return NULL;
    }
    char *buff;
    Py_ssize_t l_buff_size = 0;
    if (PyBytes_AsStringAndSize(obj_bytes, &buff, &l_buff_size) == -1)
        return NULL;
    PyDapPkeyObject *obj_pkey = PyObject_New(PyDapPkeyObject, &DapPkeyObject_DapPkeyObjectType);
    obj_pkey->pkey = DAP_NEW_Z_SIZE(dap_pkey_t, l_buff_size);
    memcpy(obj_pkey->pkey, buff, l_buff_size);
    return (PyObject*)obj_pkey;
}


PyObject *wrapping_dap_pkey_encrypt(PyDapPkeyObject *self, PyObject *args)
{
    PyObject *obj_bytes;
    if (!PyArg_ParseTuple(args, "O", &obj_bytes))
        return NULL;

    if (!PyBytes_Check(obj_bytes)) {
        PyErr_SetString(PyExc_ValueError, "An invalid argument was passed, the incoming argument must be of type bytes.");
        return NULL;
    }
    
    char *buff;
    Py_ssize_t l_buff_size = 0;
    if (PyBytes_AsStringAndSize(obj_bytes, &buff, &l_buff_size) == -1)
        return NULL;

    dap_enc_key_t *key = dap_enc_key_new(dap_pkey_type_to_enc_key_type(self->pkey->header.type));

    if (dap_enc_key_deserialize_pub_key(key, self->pkey->pkey, self->pkey->header.size) != 0)
    {
        PyErr_SetString(PyExc_ValueError, "Can't deserialize pubkey to enckey.");
        return NULL;
    }

    size_t encrypt_buff_size = dap_enc_code_out_size(key, l_buff_size, DAP_ENC_DATA_TYPE_RAW);
    uint8_t *encrypt_result = DAP_NEW_SIZE(uint8_t, encrypt_buff_size);

    size_t encrypted_size = dap_enc_code(key, buff,
                                            l_buff_size,
                                            encrypt_result,
                                            encrypt_buff_size,
                                            DAP_ENC_DATA_TYPE_RAW);
    UNUSED(encrypted_size);
    dap_enc_key_delete(key);

    return PyBytes_FromStringAndSize((char *)encrypt_result, (Py_ssize_t)encrypt_buff_size);
}

