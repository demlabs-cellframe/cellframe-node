#include "wrapping_dap_chain_tx_pkey.h"

static PyGetSetDef DapChainTxPkeyGetsSetsDef[] = {
        {"sigType", (getter)wrapping_dap_chain_tx_pkey_sig_type, NULL, NULL, NULL},
        {"sigSize", (getter)wrapping_dap_chain_tx_pkey_sig_size, NULL, NULL, NULL},
        {"sequenceNumber", (getter)wrapping_dap_chain_tx_pkey_seq_no, NULL, NULL, NULL},
        {"pkey", (getter)wrapping_dap_chain_tx_pkey_get_pkey, NULL, NULL, NULL},
        {}
};

PyTypeObject DapChainTxPkeyObjectType = DAP_PY_TYPE_OBJECT(
        "CellFrame.ChainTxPkey", sizeof(PyDapChainTXPkeyObject),
        "Chain tx pkey object",
        .tp_getset = DapChainTxPkeyGetsSetsDef);

PyObject *wrapping_dap_chain_tx_pkey_sig_type(PyObject *self, void *closure){
    (void)closure;
    PyDapSignTypeObject *obj_sign_type = PyObject_New(PyDapSignTypeObject, &DapCryproSignTypeObjectType);
    obj_sign_type->sign_type= ((PyDapChainTXPkeyObject*)self)->tx_pkey->header.sig_type;
    return (PyObject*)obj_sign_type;
}
PyObject *wrapping_dap_chain_tx_pkey_sig_size(PyObject *self, void *closure){
    (void)closure;
    return Py_BuildValue("I", ((PyDapChainTXPkeyObject*)self)->tx_pkey->header.sig_size);
}
PyObject *wrapping_dap_chain_tx_pkey_seq_no(PyObject *self, void *closure){
    return Py_BuildValue("I", ((PyDapChainTXPkeyObject*)self)->tx_pkey->seq_no);
}
PyObject *wrapping_dap_chain_tx_pkey_get_pkey(PyObject *self, void *closure){
    (void)closure;
    PyDapPkeyObject *obj_pkey = PyObject_NEW(PyDapPkeyObject, &DapPkeyObject_DapPkeyObjectType);
    obj_pkey->pkey = (dap_pkey_t *)((PyDapChainTXPkeyObject*)self)->tx_pkey->pkey;
    return (PyObject*)obj_pkey;
}
