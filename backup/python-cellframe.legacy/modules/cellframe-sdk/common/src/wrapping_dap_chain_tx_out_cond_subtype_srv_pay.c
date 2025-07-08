#include "wrapping_dap_chain_tx_out_cond_subtype_srv_pay.h"
#include "math_python.h"
#include "wrapping_dap_pkey.h"
#include "wrapping_dap_chain_common.h"
#include "wrapping_dap_pkey.h"

static PyGetSetDef DapChainTxOutCondSubtypeStvPayGetsSetsDef[]={
        {"unit", (getter)wrapping_dap_chain_tx_out_cond_subtype_srv_pay_get_unit,NULL, "", NULL},
        {"uid", (getter)wrapping_dap_chain_tx_out_cond_subtype_srv_pay_get_uid,NULL, "", NULL},
        {"pkeyHash", (getter)wrapping_dap_chain_tx_out_cond_subtype_srv_pay_get_pkey,NULL, "", NULL},
        {"maxPrice", (getter)wrapping_dap_chain_tx_out_cond_subtype_srv_pay_get_map_price,NULL, "", NULL},
        {"usedBy", (getter)wrapping_dap_chain_tx_out_cound_used_by, NULL, "", NULL},
        {}
};

PyTypeObject DapChainTxOutCondSubTypeSrvPayObjectType = {
        .ob_base =PyVarObject_HEAD_INIT(NULL, 0)
        .tp_name = "CellFrame.ChainTxOutCondSubTypeSrvPay",
        .tp_basicsize = sizeof(PyDapChainTxOutCondObject),
        .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASE_EXC_SUBCLASS,
        "Chain tx cond subtype srv pay object",
        .tp_getset = DapChainTxOutCondSubtypeStvPayGetsSetsDef,
        .tp_base = &DapChainTxOutCondObjectType,
        .tp_new = wrapping_dap_chain_tx_out_cond_subtype_srv_pay_new
};

PyObject *wrapping_dap_chain_tx_out_cond_subtype_srv_pay_get_unit(PyObject *self, void *closure){
    (void)closure;
    return Py_BuildValue("I", ((PyDapChainTxOutCondObject*)self)->out_cond->subtype.srv_pay.unit.uint32);
}
PyObject *wrapping_dap_chain_tx_out_cond_subtype_srv_pay_get_uid(PyObject *self, void *closure){
    (void)closure;
    PyDapChainNetSrvUIDObject *obj_net_srv_uid = PyObject_New(PyDapChainNetSrvUIDObject, &DapChainNetSrvUidObjectType);
    obj_net_srv_uid->net_srv_uid = ((PyDapChainTxOutCondObject*)self)->out_cond->header.srv_uid;
    return (PyObject*)obj_net_srv_uid;
}
PyObject *wrapping_dap_chain_tx_out_cond_subtype_srv_pay_get_pkey(PyObject *self, void *closure){
    (void)closure;
    PyDapHashFastObject *obj_hash = PyObject_New(PyDapHashFastObject, &DapChainHashFastObjectType);
    obj_hash->hash_fast = &((PyDapChainTxOutCondObject*)self)->out_cond->subtype.srv_pay.pkey_hash;
    obj_hash->origin = false;
    return (PyObject*)obj_hash;
}
PyObject *wrapping_dap_chain_tx_out_cond_subtype_srv_pay_get_map_price(PyObject *self, void *closure){
    (void)closure;
    return Py_BuildValue("k", ((PyDapChainTxOutCondObject*)self)->out_cond->subtype.srv_pay.unit_price_max_datoshi);
}

PyObject *wrapping_dap_chain_tx_out_cond_subtype_srv_pay_new(PyTypeObject *type_object, PyObject *argv, PyObject *kwds) {
    (void)type_object;
    PyObject *obj_value;
    PyObject *obj_srv_uid;
    PyObject *obj_pkey;
    PyObject *obj_max_price;
    PyObject *obj_unit;
    PyObject *obj_params = NULL;
    const char *kwlist[] = {
            "value",
            "srv_uid",
            "pub_key",
            "max_price",
            "unit",
            "params",
            NULL
    };
    if (!PyArg_ParseTupleAndKeywords(argv, kwds, "OOOOO|O", (char**)kwlist, &obj_value, &obj_srv_uid, &obj_pkey,
                                     &obj_max_price, &obj_unit, &obj_params))
        return NULL;
    if (!DapMathObject_Check(obj_value)) {
        PyErr_SetString(PyExc_BaseException, "An invalid type for value was passed to the constructor "
                                             "of ChainTxOutCondSubTypeSrvPay object, value must be of type DapMath.");
        return NULL;
    }
    uint256_t l_value =  ((DapMathObject*)obj_value)->value;
    if (!DapMathObject_Check(obj_max_price)){
        PyErr_SetString(PyExc_BaseException, "Incorrect type for max_price was passed to the "
                                             "constructor of ChainTxOutCondSubTypeSrvPay object, max_price "
                                             "should be of type DapMath.");
        return NULL;
    }
    uint256_t l_max_price = ((DapMathObject*)obj_max_price)->value;
    if (!PyCryptoKeyObject_check(obj_pkey)) {
        PyErr_SetString(PyExc_BaseException, "Incorrect type for max_price was passed to the "
                                             "constructor of ChainTxOutCondSubTypeSrvPay object, pkey "
                                             "should be of type CryptoPkey.");
        return NULL;
    }
    dap_pkey_t *l_pkey = ((PyDapPkeyObject*)obj_pkey)->pkey;
    if (!PyDapChainNetSrvUid_Check((PyDapChainNetSrvUIDObject*)obj_srv_uid)) {
        PyErr_SetString(PyExc_BaseException, "Incorrect type for max_price was passed to the "
                                             "constructor of ChainTxOutCondSubTypeSrvPay object, srv_uid "
                                             "should be of type UnitUID.");
        return NULL;
    }
    dap_chain_srv_uid_t l_uid = ((PyDapChainNetSrvUIDObject*)obj_srv_uid)->net_srv_uid;
    dap_chain_net_srv_price_unit_uid_t l_unit_uid = ((PyDapChainNetSrvPriceUnitUIDObject*)obj_unit)->price_unit_uid;
    void *l_bytes = NULL;
    size_t l_bytes_size = 0;
    if (!obj_params) {
        l_bytes = PyBytes_AsString(obj_params);
        l_bytes_size = PyBytes_Size(obj_params);
    }
    dap_chain_tx_out_cond_t *l_out_cond = dap_chain_datum_tx_item_out_cond_create_srv_pay(l_pkey, l_uid, l_value,
                                                                                          l_max_price, l_unit_uid,
                                                                                          l_bytes, l_bytes_size);
    PyDapChainTxOutCondObject *obj_out_cond = PyObject_New(PyDapChainTxOutCondObject, &DapChainTxOutCondSubTypeSrvPayObjectType);
    obj_out_cond->out_cond = l_out_cond;
    return (PyObject*)obj_out_cond;
}
