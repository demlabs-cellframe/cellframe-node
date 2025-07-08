#include "wrapping_dap_chain_tx_sig.h"

static PyGetSetDef DapChainTxSigGetsSetsDef[] = {
        {"sign", (getter)wrapping_dap_chain_tx_sig_get_sign, NULL, NULL, NULL},
        {"sigSize", (getter)wrapping_dap_chain_tx_sig_get_sig_size, NULL, NULL, NULL},
        {}
};

PyTypeObject DapChainTxSigObjectType = DAP_PY_TYPE_OBJECT(
        "CellFrame.ChainTxSig", sizeof(PyDapChainTXSigObject),
        "Chain tx signature object",
        .tp_getset = DapChainTxSigGetsSetsDef);

PyObject *wrapping_dap_chain_tx_sig_get_sign(PyObject *self, void *closure){
    (void)closure;
    PyObject *obj_sign = PyDapSignObject_Cretae((dap_sign_t*)((PyDapChainTXSigObject*)self)->tx_sig->sig);
    return (PyObject*)obj_sign;
}

PyObject *wrapping_dap_chain_tx_sig_get_sig_size(PyObject *self, void *closure){
    (void)closure;
    return Py_BuildValue("I", ((PyDapChainTXSigObject*)self)->tx_sig->header.sig_size);
}
