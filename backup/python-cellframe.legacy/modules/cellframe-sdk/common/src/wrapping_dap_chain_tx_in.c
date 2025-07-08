#include "wrapping_dap_chain_tx_in.h"

static PyGetSetDef DapChainTxGetsSetsDef[] = {
        {"prevHash", (getter)wrapping_dap_chain_tx_in_get_prev_hash, NULL, NULL, NULL},
        {"prevIdx", (getter)wrapping_dap_chain_tx_in_get_out_prev_idx, NULL, NULL, NULL},
        {}
};

PyTypeObject DapChainTxInObjectType = DAP_PY_TYPE_OBJECT(
        "CellFrame.ChainTxIn", sizeof(PyDapChainTXInObject),
        "Chain tx in object",
        .tp_getset = DapChainTxGetsSetsDef,
        .tp_init = (initproc)PyDapChainTxIn_init);

int PyDapChainTxIn_init(PyObject *self, PyObject *args, PyObject *kwds){
    const char *kwlist[] = {
            "prevHash",
            "prevIdx",
            NULL
    };
    PyDapHashFastObject *obj_prev_hash;
    uint32_t l_tx_prev_idx;
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "OI", (char **)kwlist, &obj_prev_hash, &l_tx_prev_idx)){
        return -1;
    }
    if (!PyDapHashFast_Check(obj_prev_hash)){
        return -1;
    }
    ((PyDapChainTXInObject*)self)->tx_in = dap_chain_datum_tx_item_in_create(
            obj_prev_hash->hash_fast, l_tx_prev_idx);
    return 0;
}

PyObject *wrapping_dap_chain_tx_in_get_prev_hash(PyObject *self, void *closure){
    (void)closure;
    PyDapHashFastObject *obj_hash = PyObject_New(PyDapHashFastObject, &DapChainHashFastObjectType);
    obj_hash->hash_fast = &((PyDapChainTXInObject*)self)->tx_in->header.tx_prev_hash;
    obj_hash->origin = false;
    return  (PyObject*)obj_hash;
}
PyObject *wrapping_dap_chain_tx_in_get_out_prev_idx(PyObject *self, void *closure){
    (void)closure;
    return Py_BuildValue("I", ((PyDapChainTXInObject*)self)->tx_in->header.tx_out_prev_idx);
}

