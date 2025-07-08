#include "wrapping_dap_chain_tx_out_cond_subtype_srv_xchange.h"
#include "math_python.h"

int DapChainTxOutCondSubtypeSrvXchange_init(PyDapChainTxOutCondObject *self, PyObject *args, PyObject *kwds);

static PyGetSetDef DapChainTxOutCondSubtypeSrvXchangeGetsSetsDef[]={
        {"uid", (getter)wrapping_dap_chain_tx_out_cond_subtype_srv_xchange_get_uid,NULL, "", NULL},
        {"netId", (getter)wrapping_dap_chain_tx_out_cond_subtype_srv_xchange_get_net_id,NULL, "", NULL},
        {"token", (getter)wrapping_dap_chain_tx_out_cond_subtype_srv_xchange_get_token,NULL, "", NULL},
        {"value", (getter)wrapping_dap_chain_tx_out_cond_subtype_srv_xchange_get_value,NULL, "", NULL},
        {"usedBy", (getter)wrapping_dap_chain_tx_out_cound_used_by, NULL, "", NULL},
        {}
};

PyTypeObject DapChainTxOutCondSubTypeSrvXchangeObjectType = {
        .ob_base = PyVarObject_HEAD_INIT(NULL, 0)
        .tp_name = "CellFrame.ChainTxOutCondSubTypeSrvXchange",
        .tp_basicsize = sizeof(PyDapChainTxOutCondObject),
        .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASE_EXC_SUBCLASS,
        "Chain tx cond subtype srv xchange object",
        .tp_getset = DapChainTxOutCondSubtypeSrvXchangeGetsSetsDef,
        .tp_base = &DapChainTxOutCondObjectType,
        .tp_init = (initproc)DapChainTxOutCondSubtypeSrvXchange_init,
        .tp_new = PyType_GenericNew
};

PyObject *wrapping_dap_chain_tx_out_cond_subtype_srv_xchange_get_uid(PyObject *self, void *closure){
    (void)closure;
    PyDapChainNetSrvUIDObject *obj_net_srv_uid = PyObject_New(PyDapChainNetSrvUIDObject, &DapChainNetSrvUidObjectType);
    obj_net_srv_uid->net_srv_uid = ((PyDapChainTxOutCondObject*)self)->out_cond->header.srv_uid;
    return (PyObject*)obj_net_srv_uid;
}
PyObject *wrapping_dap_chain_tx_out_cond_subtype_srv_xchange_get_net_id(PyObject *self, void *closure){
    (void)closure;
    PyDapChainNetIdObject *obj_net_id = PyObject_New(PyDapChainNetIdObject, &DapChainNetIdObjectType);
    obj_net_id->net_id = ((PyDapChainTxOutCondObject*)self)->out_cond->subtype.srv_xchange.buy_net_id;
    return (PyObject*)obj_net_id;
}
PyObject *wrapping_dap_chain_tx_out_cond_subtype_srv_xchange_get_token(PyObject *self, void *closure){
    (void)closure;
    return Py_BuildValue("s", ((PyDapChainTxOutCondObject*)self)->out_cond->subtype.srv_xchange.buy_token);
}
PyObject *wrapping_dap_chain_tx_out_cond_subtype_srv_xchange_get_value(PyObject *self, void *closure){
    (void)closure;
    DapMathObject *obj_math = PyObject_New(DapMathObject, &DapMathObjectType);
    obj_math->value = ((PyDapChainTxOutCondObject*)self)->out_cond->header.value;
    return (PyObject*)obj_math;
}

int DapChainTxOutCondSubtypeSrvXchange_init(PyDapChainTxOutCondObject *self, PyObject *args, PyObject *kwds) {
    const char *kwlist[] = {
        "UID",
        "sellNetId",
        "valueSell",
        "buyNetId",
        "token",
        "valueRate",
        "sellerAddr",
        "params",
        NULL
    };
    PyObject *obj_srv_uid;
    PyObject *obj_sell_net_id;
    PyObject *obj_value_sell;
    PyObject *obj_buy_net_id;
    const char *token;
    PyObject *obj_value_rate;
    PyObject *obj_seller_addr;
    // PyObject *obj_params;
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "OOOOsOO", (char **)kwlist, &obj_srv_uid, &obj_sell_net_id,
        &obj_value_sell, &obj_buy_net_id, &token, &obj_value_rate, &obj_seller_addr))
        return -1;
    if (!PyDapChainNetSrvUid_Check((PyDapChainNetSrvUIDObject*)obj_srv_uid)) {
        return -1;
    }
    if (!PyObject_TypeCheck(obj_sell_net_id, &DapChainNetIdObjectType)) {
        return -1;
    }
    if (!DapMathObject_Check(obj_value_sell)) {
        return -1;
    }
    if (!PyObject_TypeCheck(obj_buy_net_id, &DapChainNetIdObjectType)) {
        return -1;
    }
    if (!DapMathObject_Check(obj_value_rate)) {
        return -1;
    }
    if (!PyDapChainAddrObject_Check((PyDapChainAddrObject*)obj_seller_addr)) {
        return -1;
    }
    dap_chain_srv_uid_t l_srv_uid = ((PyDapChainNetSrvUIDObject*)obj_srv_uid)->net_srv_uid;
    self->out_cond = dap_chain_datum_tx_item_out_cond_create_srv_xchange(
        l_srv_uid, ((PyDapChainNetIdObject*)obj_sell_net_id)->net_id, ((DapMathObject*)obj_value_sell)->value,
        ((PyDapChainNetIdObject*)obj_buy_net_id)->net_id, token, ((DapMathObject*)obj_value_rate)->value,
        ((PyDapChainAddrObject*)obj_seller_addr)->addr, NULL, 0);

    return 0;
}
