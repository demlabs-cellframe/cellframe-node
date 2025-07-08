#include "wrapping_dap_sign.h"
#include "libdap_chain_net_python.h"

/* Sign type*/
PyTypeObject DapCryproSignTypeObjectType = DAP_PY_TYPE_OBJECT(
        "DAP.Crypto.SignType", sizeof(PyDapSignTypeObject),
        "Sign type object",
        .tp_str = PyDapSignType_to_str);

PyObject *PyDapSignType_to_str(PyObject *self){
    return Py_BuildValue("s", dap_sign_type_to_str(((PyDapSignTypeObject*)self)->sign_type));
}

/* Sign */
static PyGetSetDef DapSignObjectGetsSetsDef[] = {
        {"type", (getter)wrapping_dap_sign_get_type, NULL, NULL, NULL},
        {"pkey", (getter)wrapping_dap_sign_get_pkey, NULL, NULL, NULL},
        {"pkeyHash", (getter)wrapping_dap_sign_get_pkey_hash, NULL, NULL, NULL},
        {"size", (getter)wrapping_dap_sign_get_size, NULL, NULL, NULL},
        {}
};

static PyMethodDef DapSignObjectMethods[]= {
        {"verify", wrapping_dap_sign_verify, METH_VARARGS, ""},
        {"fromBytes", wrapping_dap_sign_from_bytes, METH_VARARGS | METH_STATIC, ""},
        {"toBytes", wrapping_dap_sign_get_bytes, METH_NOARGS, ""},
        {"fromBase64", wrapping_dap_sign_from_b64, METH_VARARGS | METH_STATIC, ""},
        {"toBase64", wrapping_dap_sign_to_b64, METH_NOARGS, ""},
        {"getAddr", wrapping_dap_sign_get_addr, METH_VARARGS, ""},
        {}
};

PyTypeObject DapCryptoSignObjectType = DAP_PY_TYPE_OBJECT(
        "DAP.Crypto.Sign", sizeof(PyDapSignObject),
        "Sign object",
        .tp_dealloc = (destructor)PyDapSignObject_free,
        .tp_methods = DapSignObjectMethods,
        .tp_getset = DapSignObjectGetsSetsDef,
        .tp_init = wrapping_dap_sign_create);

void PyDapSignObject_free(PyDapSignObject *self) {
    DAP_DELETE(self->sign);
    Py_TYPE(self)->tp_free((PyObject*)self);
}

PyObject *wrapping_dap_sign_get_type(PyObject *self, void *closure){
    (void)closure;
    PyDapSignTypeObject *obj_type_sign = PyObject_New(PyDapSignTypeObject, &DapCryproSignTypeObjectType);
    obj_type_sign->sign_type = ((PyDapSignObject*)self)->sign->header.type;
    return (PyObject*)obj_type_sign;
}
PyObject *wrapping_dap_sign_get_pkey(PyObject *self, void *closure){
    (void)closure;
    PyDapPkeyObject *obj_pkey = PyObject_New(PyDapPkeyObject, &DapPkeyObject_DapPkeyObjectType);
    obj_pkey->pkey = dap_pkey_get_from_sign(((PyDapSignObject*)self)->sign);
    return (PyObject*)obj_pkey;
}

PyObject *wrapping_dap_sign_get_pkey_hash(PyObject *self, void *closure){
    (void)closure;
    PyDapHashFastObject *obj_hash = PyObject_New(PyDapHashFastObject, &DapChainHashFastObjectType);
    obj_hash->hash_fast = DAP_NEW(dap_chain_hash_fast_t);
    dap_sign_get_pkey_hash(((PyDapSignObject*)self)->sign, obj_hash->hash_fast);
    obj_hash->origin = true;
    return (PyObject*)obj_hash;
}

PyObject *wrapping_dap_sign_get_size(PyObject *self, void *closure){
    (void)closure;
    return Py_BuildValue("I", ((PyDapSignObject*)self)->sign->header.sign_size);
}

PyObject *wrapping_dap_sign_get_addr(PyObject *self, PyObject *args){
    PyObject *obj_net;
    if (!PyArg_ParseTuple(args, "O", &obj_net)){
        return NULL;
    }
    if (!PyDapChainNet_Check((PyDapChainNetObject*)obj_net)){
        PyErr_SetString(PyExc_SyntaxError, "The getAddr function must take an object of type "
                                           "CellFrame.Network.Net as an argument.");
        return NULL;
    }

    PyDapChainAddrObject *obj_addr = PyObject_New(PyDapChainAddrObject, &DapChainAddrObjectType);
    
    obj_addr->addr = DAP_NEW(dap_chain_addr_t);
    
    dap_hash_fast_t l_hf = {0};
    dap_hash_fast(((PyDapSignObject *)self)->sign->pkey_n_sign, ((PyDapSignObject *)self)->sign->header.sign_pkey_size, &l_hf);
    dap_chain_addr_fill(obj_addr->addr,
                        ((PyDapSignObject *)self)->sign->header.type,
                        &l_hf,
                        ((PyDapChainNetObject*)obj_net)->chain_net->pub.id);
    return (PyObject*)obj_addr;
}

int wrapping_dap_sign_create(PyObject *self, PyObject* args, PyObject *kwds){
    //DATUM, DATUM_TX,  DATUM_TOKEN, Bytes
    const char *kwlist[] = {
            "key",
            "data",
            NULL
    };
    PyObject *obj_key;
    PyObject *obj_data;
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "OO", (char**)kwlist, &obj_key, &obj_data))
        return -1;
    if (!PyCryptoKeyObject_check(obj_key)){
        PyErr_SetString(PyExc_AttributeError, "The first argument was passed incorrectly, the first "
                                              "argument must be an object of type Crypto.Key.");
        return -1;
    }
    dap_sign_t *l_sign = NULL;
    //DATA = BYTES
    if (PyBytes_Check(obj_data)){
        void *l_bytes = PyBytes_AsString(obj_data);
        size_t l_bytes_size = PyBytes_Size(obj_data);
        l_sign = dap_sign_create(((PyCryptoKeyObject*)obj_key)->key, l_bytes, l_bytes_size);
    }
    if (DapChainDatumToken_Check(obj_data)){
        l_sign = dap_sign_create(((PyCryptoKeyObject*)obj_key)->key,
                                 ((PyDapChainDatumTokenObject*)obj_data)->token,
                                 ((PyDapChainDatumTokenObject*)obj_data)->token_size);
    }
    if (PyDapChainDatumTokenEmissionObject_check(obj_data)){
        l_sign = dap_sign_create(((PyCryptoKeyObject*)obj_key)->key,
                        ((PyDapChainDatumTokenEmissionObject*)obj_data)->token_emission,
                        ((PyDapChainDatumTokenEmissionObject*)obj_data)->token_size);
    }
    if (PyDapChainDatum_Check(obj_data)) {
        size_t l_datum_size = dap_chain_datum_size(((PyDapChainDatumObject*)obj_data)->datum);
        l_sign = dap_sign_create(
                ((PyCryptoKeyObject*)obj_key)->key,
                ((PyDapChainDatumObject*)obj_data)->datum, l_datum_size);
    }
    if (DapChainDatumTx_Check(obj_data)){
        size_t l_datum_tx_size = dap_chain_datum_tx_get_size(((PyDapChainDatumTxObject*)obj_data)->datum_tx);
        l_sign = dap_sign_create(((PyCryptoKeyObject*)obj_key)->key,
                                 ((PyDapChainDatumTxObject*)obj_data)->datum_tx, l_datum_tx_size);
    }
    if (!l_sign){
        PyErr_SetString(PyExc_AttributeError, "The signature could not be created, the second argument "
                                              "may have been passed incorrectly, or an unsupported argument may have "
                                              "been passed.");
        return -1;
    }
    ((PyDapSignObject*)self)->sign = l_sign;
    return 0;
}

PyObject *wrapping_dap_sign_verify(PyObject *self, PyObject *args){
    PyObject *obj_data;
    if (!PyArg_ParseTuple(args, "O", &obj_data)){
        return NULL;
    }
    void *l_data = NULL;
    size_t l_data_size = 0;
    if (PyBytes_Check(obj_data)){
        l_data = PyBytes_AsString(obj_data);
        l_data_size = PyBytes_Size(obj_data);
    }
    if (DapChainDatumToken_Check(obj_data)){
        l_data = ((PyDapChainDatumTokenObject*)obj_data)->token;
        l_data_size = ((PyDapChainDatumTokenObject*)obj_data)->token_size;
    }
    if (PyDapChainDatumTokenEmissionObject_check(obj_data)){
        l_data = ((PyDapChainDatumTokenEmissionObject*)obj_data)->token_emission;
        l_data_size = ((PyDapChainDatumTokenEmissionObject*)obj_data)->token_size;
    }
    if (PyDapChainDatum_Check(obj_data)) {
        l_data = ((PyDapChainDatumObject*)obj_data)->datum;
        l_data_size = dap_chain_datum_size(((PyDapChainDatumObject*)obj_data)->datum);
    }
    if (DapChainDatumTx_Check(obj_data)){
        l_data = ((PyDapChainDatumTxObject*)obj_data)->datum_tx;
        l_data_size = dap_chain_datum_tx_get_size(((PyDapChainDatumTxObject*)obj_data)->datum_tx);
    }
    if (!l_data || l_data_size == 0){
        PyErr_SetString(PyExc_AttributeError, "The attribute of this function was passed incorrectly, "
                                              "the function accepts the attribute Datum, Datum Token, "
                                              "DatumTokenEmission, DatumTx, byte.");
        return NULL;
    }
    if(dap_sign_verify(((PyDapSignObject*)self)->sign, l_data, l_data_size)){
        Py_RETURN_TRUE;
    } else {
        Py_RETURN_FALSE;
    }
}

PyObject *wrapping_dap_sign_get_bytes(PyObject *self, PyObject *args){
    (void)args;
    dap_sign_t *l_sign = ((PyDapSignObject*)self)->sign;
    size_t l_sign_size = dap_sign_get_size(((PyDapSignObject*)self)->sign);
    PyObject *l_bytes = PyBytes_FromStringAndSize((char *)l_sign, l_sign_size);
    return l_bytes;
}

PyObject *wrapping_dap_sign_from_bytes(PyObject *self, PyObject *args){
    (void)self;
    PyObject *obj_data;
    if (!PyArg_ParseTuple(args, "O", &obj_data)){
        return NULL;
    }
    if (!PyBytes_Check(obj_data)){
        PyErr_SetString(PyExc_AttributeError, "The first argument was not passed correctly, the first argument "
                                              "must be an object of type Bytes.");
        return NULL;
    }
    //size_t l_size = PyBytes_Size(obj_data);
    void *l_buff = PyBytes_AsString(obj_data);
    dap_sign_t *l_sign = (dap_sign_t*)l_buff;
    return PyDapSignObject_Cretae(l_sign);
}

PyObject *wrapping_dap_sign_to_b64(PyObject *self, PyObject *args){
    (void)args;
    dap_sign_t *l_sign = ((PyDapSignObject*)self)->sign;
    size_t l_sign_size = dap_sign_get_size(((PyDapSignObject*)self)->sign);
    char l_str_out[DAP_ENC_BASE64_ENCODE_SIZE(l_sign_size )];
    size_t l_str_out_size = dap_enc_base64_encode(l_sign, l_sign_size, l_str_out, DAP_ENC_DATA_TYPE_B64);
    if (l_str_out_size == 0){
        Py_RETURN_NONE;
    }
    return Py_BuildValue("s", l_str_out);
}

PyObject *wrapping_dap_sign_from_b64(PyObject *self, PyObject *args){
    (void)self;
    char *l_str;
    if (!PyArg_ParseTuple(args, "s", &l_str)){
        return NULL;
    }
    size_t l_str_size = dap_strlen(l_str);
    void *l_out = DAP_NEW_Z_SIZE(void*, DAP_ENC_BASE64_ENCODE_SIZE(l_str_size));
    size_t l_out_size = dap_enc_base64_decode(l_str, l_str_size, l_out, DAP_ENC_DATA_TYPE_B64);
    if (l_out_size == 0)
        Py_RETURN_NONE;
    PyDapSignObject *l_sign_obj = PyObject_New(PyDapSignObject, &DapCryptoSignObjectType);
    l_sign_obj->sign = (dap_sign_t*)l_out;
    return (PyObject*)l_sign_obj;
}

PyObject *PyDapSignObject_Cretae(dap_sign_t *a_sign){
    PyDapSignObject *obj_sign = PyObject_New(PyDapSignObject, &DapCryptoSignObjectType);
    size_t l_sign_size = dap_sign_get_size(a_sign);
    obj_sign->sign = DAP_NEW_Z_SIZE(dap_sign_t, l_sign_size);
    memcpy(obj_sign->sign, a_sign, l_sign_size);
    return (PyObject*)obj_sign;
}
