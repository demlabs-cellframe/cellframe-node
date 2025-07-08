#include "wrapping_dap_chain_tx_out_ext.h"

static PyGetSetDef DapChainTxOutExtGetsSetsDef[] = {
        {"addr", (getter)wrapping_dap_chain_tx_out_ext_get_addr, NULL, "", NULL},
        {"token", (getter)wrapping_dap_chain_tx_out_ext_get_token, NULL, "", NULL},
        {"value", (getter)wrapping_dap_chain_tx_out_ext_get_value, NULL, "", NULL},
        {"usedBy", (getter)wrapping_dap_chain_tx_out_ext_get_used_by, NULL, "", NULL},
        {}
};

PyTypeObject DapChainTxOutExtObjectType = DAP_PY_TYPE_OBJECT(
        "CellFrame.ChainTxOutExt", sizeof(PyDapChainTXOutExtObject),
        "Chain tx out ext object",
        .tp_getset = DapChainTxOutExtGetsSetsDef,
        .tp_init = (initproc)DapChainTxOutExt_init);

int DapChainTxOutExt_init(PyDapChainTXOutExtObject *self, PyObject *args, PyObject *kwds){
    const char* kwlist[] = {
            "addr",
            "token",
            "value",
            NULL
    };
    PyObject *obj_addr;
    const char *str_token;
    PyObject *obj_value;
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "OsO", (char **)kwlist, &obj_addr, &str_token, &obj_value))
        return -1;
    self->out_ext = dap_chain_datum_tx_item_out_ext_create(PY_DAP_CHAIN_ADDR(obj_addr), ((DapMathObject*)obj_value)->value, str_token);
    return 0;
}

PyObject *wrapping_dap_chain_tx_out_ext_get_addr(PyObject *self, void *closure){
    (void)closure;

    PyDapChainAddrObject *obj_addr = PyObject_New(PyDapChainAddrObject, &DapChainAddrObjectType);
    obj_addr->addr = DAP_NEW(dap_chain_addr_t);
    dap_mempcpy(obj_addr->addr, &((PyDapChainTXOutObject*)self)->tx_out->addr, sizeof(dap_chain_addr_t));
    return (PyObject *)obj_addr;
}
PyObject *wrapping_dap_chain_tx_out_ext_get_token(PyObject *self, void *closure){
    (void)closure;
    return Py_BuildValue("s", ((PyDapChainTXOutExtObject*)self)->out_ext->token);
}
PyObject *wrapping_dap_chain_tx_out_ext_get_value(PyObject *self, void *closure){
    (void)closure;
    DapMathObject *l_math = PyObject_New(DapMathObject, &DapMathObjectType);
    l_math->value = ((PyDapChainTXOutExtObject*)self)->out_ext->header.value;
    return (PyObject*)l_math;
}

PyObject *wrapping_dap_chain_tx_out_ext_get_used_by(PyObject *self, void *closure){
    (void)closure;
    PyDapChainTXOutExtObject *obj_ext = ((PyDapChainTXOutExtObject*)self);
    dap_hash_fast_t l_spender_hash = {0};
    if (dap_ledger_tx_hash_is_used_out_item(obj_ext->ledger, &obj_ext->tx_hash, obj_ext->idx, &l_spender_hash)) {
        PyDapHashFastObject *obj_hf = PyObject_New(PyDapHashFastObject, &DapChainHashFastObjectType);
        obj_hf->hash_fast = DAP_NEW(dap_hash_fast_t);
        memcpy(obj_hf->hash_fast, &l_spender_hash, sizeof(dap_hash_fast_t));
        obj_hf->origin = true;
        return (PyObject*)obj_hf;
    }
    Py_RETURN_NONE;
}
