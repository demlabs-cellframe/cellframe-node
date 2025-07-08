#include "wrapping_dap_chain_tx_in_cond.h"

static PyGetSetDef DapChainTxInCondGetsSetsDef[] = {
        {"receiptPrevIdx",(getter)wrapping_dap_chain_tx_in_cond_get_receipt_prev_idx, NULL, NULL, NULL},
        {"prevHash", (getter)wrapping_dap_chain_tx_in_cond_get_prev_hash, NULL, NULL, NULL},
        {"outPrevIdx", (getter)wrapping_dap_chain_tx_in_cond_get_out_prev_idx, NULL, NULL, NULL},
        {NULL}
};

static PyMethodDef  DapChainTxInCondMethodsDef[] = {
        {NULL, NULL, 0, NULL}
};

PyTypeObject DapChainTxInCondObjectType = DAP_PY_TYPE_OBJECT(
        "CellFrame.ChainTxInCond", sizeof(PyDapChainTXInCondObject),
        "Chain tx in cond object",
        .tp_methods = DapChainTxInCondMethodsDef,
        .tp_getset = DapChainTxInCondGetsSetsDef,
        .tp_init = (initproc)PyDapChainTxInCond_init);

int PyDapChainTxInCond_init(PyDapChainTXInCondObject* self, PyObject *args, PyObject *kwds){
    const char* kwlist[] = {
            "prevHash",
            "outPrevIdx",
            "receiptIdx",
            NULL
    };
    PyDapHashFastObject *obj_tx_prev_hash;
    uint32_t l_tx_out_prev_idx;
    uint32_t l_receipt_idx;
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "OII", (char **)kwlist, &obj_tx_prev_hash, &l_tx_out_prev_idx, &l_receipt_idx)){
        return -1;
    }
    if (!PyDapHashFast_Check(obj_tx_prev_hash)){
        return -1;
    }
    self->tx_in_cond = dap_chain_datum_tx_item_in_cond_create(
            obj_tx_prev_hash->hash_fast,
            l_tx_out_prev_idx,
            l_receipt_idx);
    return 0;
}

PyObject *wrapping_dap_chain_tx_in_cond_get_receipt_prev_idx(PyObject *self, void *closure){
    (void)closure;
    return Py_BuildValue("I", ((PyDapChainTXInCondObject*)self)->tx_in_cond->header.receipt_idx);
}
PyObject *wrapping_dap_chain_tx_in_cond_get_prev_hash(PyObject *self, void *closure){
    (void)closure;
    PyDapHashFastObject *obj_hash = PyObject_New(PyDapHashFastObject, &DapChainHashFastObjectType);
    obj_hash->hash_fast = &((PyDapChainTXInCondObject*)self)->tx_in_cond->header.tx_prev_hash;
    obj_hash->origin = false;
    return (PyObject*)obj_hash;
}
PyObject *wrapping_dap_chain_tx_in_cond_get_out_prev_idx(PyObject *self, void *closure){
    (void)closure;
    return Py_BuildValue("I", ((PyDapChainTXInCondObject*)self)->tx_in_cond->header.tx_out_prev_idx);
}
