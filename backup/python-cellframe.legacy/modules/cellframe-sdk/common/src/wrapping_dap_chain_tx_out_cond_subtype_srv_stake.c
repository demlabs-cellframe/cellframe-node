#include "wrapping_dap_chain_tx_out_cond_subtype_srv_stake.h"
#include "node_address.h"

int DapChainTxOutCondSubtypeSrvStakePosDelegate_init(PyDapChainTxOutCondObject *self, PyObject *args, PyObject *kwds);
static PyGetSetDef DapChainTxOutCondSubtypeSrvStakePosDelegateGetsSetsDef[]={
        {"uid", (getter)wrapping_dap_chain_tx_out_cond_subtype_srv_stake_get_uid,NULL, "", NULL},
        {"addr", (getter)wrapping_dap_chain_tx_out_cond_subtype_srv_stake_get_addr,NULL, "", NULL},
        {"value", (getter)wrapping_dap_chain_tx_out_cond_subtype_srv_stake_get_value, NULL, "", NULL},
        {"usedBy", (getter)wrapping_dap_chain_tx_out_cound_used_by, NULL, "", NULL},
        {NULL}
};

PyTypeObject DapChainTxOutCondSubTypeSrvStakePosDelegateObjectType = {
        .ob_base = PyVarObject_HEAD_INIT(NULL, 0)
        .tp_name = "CellFrame.ChainTxOutCondSubTypeSrvStake",
        .tp_basicsize = sizeof(PyDapChainTxOutCondObject),
        .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASE_EXC_SUBCLASS,
        "Chain tx cond subtype srv stake object",
        .tp_getset = DapChainTxOutCondSubtypeSrvStakePosDelegateGetsSetsDef,
        .tp_base = &DapChainTxOutCondObjectType,
        .tp_init = (initproc)DapChainTxOutCondSubtypeSrvStakePosDelegate_init,
        .tp_new = PyType_GenericNew
};

PyObject *wrapping_dap_chain_tx_out_cond_subtype_srv_stake_get_uid(PyObject *self, void *closure){
    (void)closure;
    PyDapChainNetSrvUIDObject *obj_net_srv_uid = PyObject_New(PyDapChainNetSrvUIDObject, &DapChainNetSrvUidObjectType);
    obj_net_srv_uid->net_srv_uid = ((PyDapChainTxOutCondObject*)self)->out_cond->header.srv_uid;
    return (PyObject*)obj_net_srv_uid;
}
PyObject *wrapping_dap_chain_tx_out_cond_subtype_srv_stake_get_addr(PyObject *self, void *closure){
    (void)closure;
    PyDapChainAddrObject *obj_addr = PyObject_New(PyDapChainAddrObject, &DapChainAddrObjectType);
    obj_addr->addr = DAP_NEW(dap_chain_addr_t);
    dap_mempcpy(obj_addr->addr,&((PyDapChainTxOutCondObject*)self)->out_cond->subtype.srv_stake_pos_delegate.signing_addr, sizeof(dap_chain_addr_t));

    return (PyObject*)obj_addr;
}
PyObject *wrapping_dap_chain_tx_out_cond_subtype_srv_stake_get_value(PyObject *self, void *closure){
    (void)closure;
    Py_RETURN_NONE; // TODO return a string with 256 bit representation of (((PyDapChainTxOutCondObject*)self)->out_cond->subtype.srv_stake.fee_value);
}

int DapChainTxOutCondSubtypeSrvStakePosDelegate_init(PyDapChainTxOutCondObject *self, PyObject *args, PyObject *kwds){
    PyObject *obj_srv_uid;
    PyObject *obj_value;
    PyObject *obj_signing_addr;
    PyObject *obj_signer_node_addr;
    PyObject *obj_sovereign_addr;
    PyObject *obj_sovereign_tax;
    const char *kwlist[] = {
            "srv_uid",
            "value",
            "signing_addr",
            "signer_node_addr",
            "sovereign_addr",
            "sovereign_tax",
            NULL
    };
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "OOOOOO", (char**)kwlist, &obj_srv_uid, &obj_value, &obj_signing_addr,
                                    &obj_signer_node_addr, &obj_sovereign_addr, &obj_sovereign_tax)) {
        return -1;
    }
    if (!PyDapChainNetSrvUid_Check((PyDapChainNetSrvUIDObject*)obj_srv_uid)) {
        PyErr_SetString(PyExc_BaseException, "An invalid type is specified for srv_uid. There must be "
                                             "an instance of DapChainNetSrvUID object.");
        return -1;
    }
    if (!DapMathObject_Check(obj_value)) {
        PyErr_SetString(PyExc_BaseException, "An invalid type is specified for value. There must be "
                                             "an instance of DapMath object.");
        return -1;
    }
    if (!PyDapChainAddrObject_Check((PyDapChainAddrObject*)obj_signing_addr)){
        PyErr_SetString(PyExc_BaseException, "An invalid type is specified for signing_addr. "
                                             "It must be an instance of ChainAddr object.");
        return -1;
    }
    if (!PyDapNodeAddrObject_Check(obj_signer_node_addr)) {
        PyErr_SetString(PyExc_BaseException, "An invalid type is specified for signer_node_addr. "
                                             "It must be an instance of NodeAddr object.");
        return -1;
    }
    if (!PyDapChainAddrObject_Check((PyDapChainAddrObject*)obj_sovereign_addr)) {
        PyErr_SetString(PyExc_BaseException, "Incorrect type is specified for sovereign_addr. "
                                             "It must be an instance of ChainAddr object.");
        return -1;
    }
    if (!DapMathObject_Check(obj_sovereign_tax)) {
        PyErr_SetString(PyExc_AttributeError, "Incorrect type is specified for sovereign_tax. "
                                              "It must be an instance of DapMath object.");
        return -1;
    }
    dap_chain_srv_uid_t l_uid = ((PyDapChainNetSrvUIDObject*)obj_srv_uid)->net_srv_uid;
    uint256_t l_value = ((DapMathObject*)obj_value)->value;
    dap_chain_addr_t *l_signing_addr = ((PyDapChainAddrObject*)obj_signing_addr)->addr;
    dap_stream_node_addr_t l_node_addr = ((PyDapNodeAddrObject*)obj_signer_node_addr)->addr;
    dap_chain_addr_t  *l_sovereign_addr = ((PyDapChainAddrObject*)obj_sovereign_addr)->addr;
    uint256_t l_sovereign_tax = ((DapMathObject*)obj_sovereign_tax)->value;
    dap_chain_tx_out_cond_t *l_out_cond = dap_chain_datum_tx_item_out_cond_create_srv_stake(l_uid, l_value,
                                                                                            l_signing_addr, &l_node_addr,
                                                                                            l_sovereign_addr, l_sovereign_tax, NULL);
    self->out_cond = l_out_cond;
    return 0;
}
