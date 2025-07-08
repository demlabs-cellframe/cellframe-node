#include "wrapping_dap_chain_tx_token.h"

int PyDaoChainTxToken_new(PyDapChainTxTokenObject *self, PyObject *args, PyObject *kwds);

static PyGetSetDef PyDapChainTxTokenGetsSetsDef[] = {
        {"ticker", (getter)wrapping_dap_chain_tx_token_get_ticker, NULL, NULL, NULL},
        {"tokenEmissionHash", (getter)wrapping_dap_chain_tx_token_get_token_emission_hash, NULL, NULL, NULL},
        {"tokenEmissionChainId", (getter)wrapping_dap_chain_tx_token_get_token_emission_chain_id, NULL, NULL, NULL},
        {}
};

PyTypeObject DapChainTxTokenObjectType  = DAP_PY_TYPE_OBJECT(
        "CellFrame.ChainTxToken", sizeof(PyDapChainTxTokenObject),
        "Chain tx token object",
        .tp_getset = PyDapChainTxTokenGetsSetsDef,
        .tp_init = (initproc)PyDaoChainTxToken_new);

PyObject *wrapping_dap_chain_tx_token_get_ticker(PyObject *self, void *closure){
    (void)closure;
    return Py_BuildValue("s", ((PyDapChainTxTokenObject*)self)->token->header.ticker);
}
PyObject *wrapping_dap_chain_tx_token_get_token_emission_hash(PyObject *self, void *closure){
    (void)closure;
    PyDapHashFastObject *obj_hash = PyObject_New(PyDapHashFastObject, &DapChainHashFastObjectType);
    obj_hash->hash_fast = &((PyDapChainTxTokenObject*)self)->token->header.token_emission_hash;
    obj_hash->origin = false;
    return (PyObject*)obj_hash;
}
PyObject *wrapping_dap_chain_tx_token_get_token_emission_chain_id(PyObject *self, void *closure){
    (void)closure;
    PyDapChainIDObject *obj_chain_id = PyObject_New(PyDapChainIDObject, &DapChainIdObjectType);
    obj_chain_id->chain_id = &((PyDapChainTxTokenObject*)self)->token->header.token_emission_chain_id;
    return (PyObject*)obj_chain_id;
}

int PyDaoChainTxToken_new(PyDapChainTxTokenObject *self, PyObject *args, PyObject *kwds) {
    const char *kwlist[] = {
        "chainId",
        "hashEmi",
        NULL
    };
    PyObject *obj_chain_id;
    PyObject *obj_hash_emi;
    const char *l_token_ticker;
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "OOs", (char **)kwlist, &obj_chain_id, &obj_hash_emi, &l_token_ticker))
        return -1;
    if (!PyObject_TypeCheck(obj_chain_id, &DapChainIdObjectType)) {
        PyErr_SetString(PyExc_Exception, "The first argument is passed incorrectly, it should be Cellframe.Chain.ChainID");
        return -1;
    }
    if (PyDapHashFast_Check((PyDapHashFastObject*)obj_hash_emi)) {
        PyErr_SetString(PyExc_Exception, "The second argument is passed incorrectly, it should be DAP.Crypto.HashFast.");
        return -1;
    }
    self->token = dap_chain_datum_tx_item_in_ems_create(*((PyDapChainIDObject *) obj_chain_id)->chain_id,
                                                        ((PyDapHashFastObject *) obj_hash_emi)->hash_fast,
                                                        l_token_ticker);
    return 0;
}
