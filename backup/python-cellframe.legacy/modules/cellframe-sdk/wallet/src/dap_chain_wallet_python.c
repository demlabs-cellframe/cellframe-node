#include "dap_chain_wallet_python.h"

#define LOG_TAG "dap_chain_wallet_python"

int dap_chain_wallet_init_py(void){
    return dap_chain_wallet_init();
}
void dap_chain_wallet_deinit_py(void){
    dap_chain_wallet_deinit();
}

static PyMethodDef ChainWalletMethods[] = {
        {"getPath", (PyCFunction)dap_chain_wallet_get_path_py, METH_VARARGS | METH_STATIC, ""},
        {"createWithSeed", (PyCFunction)dap_chain_wallet_create_with_seed_py, METH_VARARGS | METH_STATIC, ""},
        {"openFile", (PyCFunction)dap_chain_wallet_open_file_py, METH_VARARGS | METH_STATIC, ""},
        {"open", (PyCFunction)dap_chain_wallet_open_py, METH_VARARGS | METH_STATIC, ""},
        {"save", (PyCFunction)dap_chain_wallet_save_py, METH_NOARGS, ""},
        {"certToAddr", (PyCFunction)dap_cert_to_addr_py, METH_VARARGS | METH_STATIC, ""},
        {"getAddr", (PyCFunction)dap_chain_wallet_get_addr_py, METH_VARARGS, ""},
        {"getCertsNumber", (PyCFunction)dap_chain_wallet_get_certs_number_py, METH_NOARGS, ""},
        {"getPKey", (PyCFunction)dap_chain_wallet_get_pkey_py, METH_VARARGS, ""},
        {"getKey", (PyCFunction)dap_chain_wallet_get_key_py, METH_VARARGS, ""},
        {}
};

PyTypeObject DapChainWalletObjectType = {
        .ob_base = PyVarObject_HEAD_INIT(NULL, 0)
        .tp_name = "CellFrame.ChainWallet",
        .tp_basicsize = sizeof(PyDapChainWalletObject),
        .tp_dealloc = (destructor)dap_chain_wallet_close_py,
        .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
        "Chain wallet object",
        .tp_methods = ChainWalletMethods,
        .tp_new = dap_chain_wallet_create_py
};

PyObject *dap_chain_wallet_get_path_py(PyObject *self, PyObject *argv){
    (void)self;
    (void)argv;
    const char *path = dap_chain_wallet_get_path(g_config);
    return Py_BuildValue("s", path);
}

PyObject *dap_chain_wallet_create_with_seed_py(PyObject *self, PyObject *argv){
    (void)self;
    const char *wallet_name;
    const char *path_wallets;
    PyObject *obj_sig_type;
    PyObject *obj_seed;
    if (!PyArg_ParseTuple(argv, "ssOO", &wallet_name, &path_wallets, &obj_sig_type, &obj_seed))
        return NULL;
    if (PyBytes_Check(obj_seed)){
        PyErr_SetString(PyExc_TypeError, "The fourth argument must be bytes");
        return NULL;
    }
    void *seed = (void *)PyBytes_AsString(obj_seed);
    size_t seed_size = PyBytes_Size(obj_seed);
    PyDapChainWalletObject *obj_wallet = PyObject_New(PyDapChainWalletObject, &DapChainWalletObjectType);
    obj_wallet->wallet = dap_chain_wallet_create_with_seed(
                wallet_name,
                path_wallets,
                ((PyDapSignTypeObject*)obj_sig_type)->sign_type,
                seed,
                seed_size,
                NULL);
    return (PyObject*)obj_wallet;
}
PyObject *dap_chain_wallet_create_py(PyTypeObject *type, PyObject *argv, PyObject *kwds){
    (void)kwds;
    PyDapChainWalletObject *self;
    const char *wallet_name;
    const char *path_wallets;
    PyObject *obj_sign_type;
    if (!PyArg_ParseTuple(argv, "ssO", &wallet_name, &path_wallets, &obj_sign_type))
        return NULL;
    self = (PyDapChainWalletObject*)type->tp_alloc(type, 0);
    if (self != NULL){
        self->wallet = dap_chain_wallet_create(wallet_name, path_wallets, ((PyDapSignTypeObject*)obj_sign_type)->sign_type, NULL);
        if (self->wallet == NULL){
            Py_XDECREF(self);
            return NULL;
        }
    }
    return (PyObject*)self;
}
PyObject *dap_chain_wallet_open_file_py(PyObject *self, PyObject *argv){
    (void)self;
    const char *file_path;
    const char *pass = NULL;
    if (!PyArg_ParseTuple(argv, "s|s", &file_path, &pass))
        return NULL;
    PyDapChainWalletObject *obj_wallet = PyObject_New(PyDapChainWalletObject, &DapChainWalletObjectType);
    obj_wallet->wallet = dap_chain_wallet_open_file(file_path, pass, NULL);
    return (PyObject*)obj_wallet;
}
PyObject *dap_chain_wallet_open_py(PyObject *self, PyObject *argv){
    (void)self;
    const char *wallet_name;
    const char *wallet_path;
    if (!PyArg_ParseTuple(argv, "ss", &wallet_name, &wallet_path))
        return NULL;
    PyDapChainWalletObject *obj_wallet = PyObject_New(PyDapChainWalletObject, &DapChainWalletObjectType);
    obj_wallet->wallet = dap_chain_wallet_open(wallet_name, wallet_path,NULL);
    return (PyObject*)obj_wallet;
}
PyObject *dap_chain_wallet_save_py(PyObject *self, PyObject *argv){
    (void)argv;
    int result = dap_chain_wallet_save(((PyDapChainWalletObject*)self)->wallet, NULL);
    return PyLong_FromLong(result);
}

void dap_chain_wallet_close_py(PyDapChainWalletObject *self){
    dap_chain_wallet_close(self->wallet);
    Py_TYPE(self)->tp_free((PyObject*)self);
}

PyObject *dap_cert_to_addr_py(PyObject *self, PyObject *argv){
    (void)self;
    PyObject *obj_certs;
    PyObject *obj_net_id;
    if (!PyArg_ParseTuple(argv, "OO", &obj_certs, &obj_net_id))
        return NULL;
    if (!PyList_Check(obj_certs)) {
        PyErr_SetString(PyExc_AttributeError, "An invalid function argument was specified. The first argument must be "
                                              "an array of certificates.");
        return NULL;
    }
    size_t l_certs_size = PyList_Size(obj_certs);
    dap_cert_t **l_certs = DAP_NEW_Z_SIZE(dap_cert_t*, l_certs_size);
    for (size_t i = 0; i < l_certs_size; i++){
        PyObject *obj_cert = PyList_GetItem(obj_certs, i);
        if (!PyCryptoKeyObject_check(obj_cert)) {
            char *l_str_err = dap_strdup_printf("The %zu element in the list of certificates is not a certificate.", i);
            PyErr_SetString(PyExc_RuntimeError, l_str_err);
            DAP_DELETE(l_str_err);
            DAP_DELETE(l_certs);
            return NULL;
        }
        l_certs[i] = ((PyCryptoCertObject*)obj_cert)->cert;
    }
    PyDapChainAddrObject *obj_addr = PyObject_New(PyDapChainAddrObject, &DapChainAddrObjectType);
    obj_addr->addr = dap_cert_to_addr(l_certs, l_certs_size, 0, ((PyDapChainNetIdObject*)obj_net_id)->net_id);
    DAP_DELETE(l_certs);
    return (PyObject*)obj_addr;
}

PyObject *dap_chain_wallet_get_addr_py(PyObject *self, PyObject *argv){
    PyObject *obj_net_id;
    if (!PyArg_ParseTuple(argv, "O", &obj_net_id))
        return NULL;
    PyDapChainAddrObject *obj_addr = PyObject_New(PyDapChainAddrObject, &DapChainAddrObjectType);
    obj_addr->addr = dap_chain_wallet_get_addr(
                ((PyDapChainWalletObject*)self)->wallet,
                ((PyDapChainNetIdObject*)obj_net_id)->net_id
                );
    return (PyObject*)obj_addr;
}
PyObject *dap_chain_wallet_get_certs_number_py(PyObject *self, PyObject *argv){
    (void)argv;
    size_t result = dap_chain_wallet_get_certs_number(((PyDapChainWalletObject*)self)->wallet);
    return PyLong_FromLong(result);
}
PyObject *dap_chain_wallet_get_pkey_py(PyObject *self, PyObject *argv){
    uint32_t key_idx;
    if (!PyArg_ParseTuple(argv, "I", &key_idx))
            return NULL;
    PyDapPkeyObject *obj_pkey = PyObject_New(PyDapPkeyObject, &DapPkeyObject_DapPkeyObjectType);
    obj_pkey->pkey = dap_chain_wallet_get_pkey(((PyDapChainWalletObject*)self)->wallet,
                                                                   key_idx);
    return (PyObject*)obj_pkey;
}
PyObject *dap_chain_wallet_get_key_py(PyObject *self, PyObject *argv){
    uint32_t key_idx;
    if (!PyArg_ParseTuple(argv, "I", &key_idx))
            return NULL;
    PyCryptoKeyObject *obj_key = PyObject_New(PyCryptoKeyObject, &PyCryptoKeyObjectType);
    obj_key->key = dap_chain_wallet_get_key(
                ((PyDapChainWalletObject*)self)->wallet,
                key_idx
                );
    return (PyObject*)obj_key;
}
