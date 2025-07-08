#include "wrapping_dap_chain_tx_tsd.h"

PyGetSetDef PyDapChainTxTSDGetsSetsDef[] = {
    {"data", (getter)wrapping_dap_chain_tx_get_tsd_data, NULL, NULL, NULL},
    {"type", (getter)wrapping_dap_chain_tx_get_tsd_type, NULL, NULL, NULL},
    {}
};

PyTypeObject DapChainTxTSDObjectType = DAP_PY_TYPE_OBJECT(
        "CellFrame.ChainTxTSD", sizeof(PyDapChainTxTSDObject),
        "Chain tx tsd object",
        .tp_getset = PyDapChainTxTSDGetsSetsDef);

PyObject *wrapping_dap_chain_tx_get_tsd_data(PyObject *self, void *closure) {
    (void)closure;
    dap_chain_tx_tsd_t *l_item = ((PyDapChainTxTSDObject*)self)->tsd;
    int l_type;
    size_t l_size;
    byte_t *l_data = dap_chain_datum_tx_item_get_data(l_item, &l_type, &l_size);
    if (!l_data || !l_type || !l_size)
        Py_RETURN_NONE;
    return PyBytes_FromStringAndSize((char*)l_data, l_size);
}

PyObject *wrapping_dap_chain_tx_get_tsd_type(PyObject *self, void *closure) {
    (void)closure;
    dap_chain_tx_tsd_t *l_item = ((PyDapChainTxTSDObject*)self)->tsd;
    int l_type;
    size_t l_size;
    dap_chain_datum_tx_item_get_data(l_item, &l_type, &l_size);
    return Py_BuildValue("i", l_type);
}

