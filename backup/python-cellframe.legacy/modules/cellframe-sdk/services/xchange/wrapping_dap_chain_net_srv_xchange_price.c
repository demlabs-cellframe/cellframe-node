#include "wrapping_dap_chain_net_srv_xchange_price.h"
#include "libdap-python.h"
#include "libdap_chain_net_python.h"
#include "libdap_crypto_key_python.h"
#include "dap_chain_wallet_python.h"
#include "dap_chain_srv.h"

#define PRICE(a) ((PyDapChainNetSrvXchangeOrderObject*)a)->price

PyGetSetDef DapChainNetSrvXchangePriceGetSetDef[] = {
        {"tokenSell", (getter)wrapping_dap_chain_net_srv_xchange_price_get_token_sell, NULL, NULL, NULL},
        {"datoshiSell", (getter)wrapping_dap_chain_net_srv_xchange_price_get_datoshi_sell, NULL, NULL, NULL},
        {"net", (getter)wrapping_dap_chain_net_srv_xchange_price_get_net, NULL, NULL, NULL},
        {"tokenBuy", (getter)wrapping_dap_chain_net_srv_xchange_price_get_token_buy, NULL, NULL, NULL},
        {"rate", (getter)wrapping_dap_chain_net_srv_xchange_price_get_rate, NULL, NULL, NULL},
        {"fee", (getter)wrapping_dap_chain_net_srv_xchange_price_get_fee, NULL, NULL, NULL},
        {"txHash", (getter)wrapping_dap_chain_net_srv_xchange_price_get_tx_hash, NULL, NULL, NULL},
        {"orderHash", (getter)wrapping_dap_chain_net_srv_xchange_price_get_order_hash, NULL, NULL, NULL},
        {"completionRate", (getter)wrapping_dap_chain_net_srv_xchange_price_get_completion_rate, NULL, NULL, NULL},
        {"status", (getter)wrapping_dap_chain_net_srv_xchange_price_get_status, NULL, NULL, NULL},
        {"creator_addr", (getter)wrapping_dap_chain_net_srv_xchange_price_get_order_creator_address, NULL, NULL, NULL},
        {"creation_date", (getter)wrapping_dap_chain_net_srv_xchange_price_get_order_creation_date, NULL, NULL, NULL},
        {}
};

PyMethodDef DapChainNetSrvXchangePriceMethods[] = {
        {
                "purchase",
                wrapping_dap_chain_net_srv_xchange_price_purchase,
                METH_VARARGS,
                "Function for partial or full purchase of an order."
        },
        {
                "invalidate",
                wrapping_dap_chain_net_srv_xchange_price_invalidate,
                METH_VARARGS,
                "Function for order invalidation."
        },
        {NULL}
};

void DapChainNetSrvXchangePrice_free(PyDapChainNetSrvXchangeOrderObject *self){
    DAP_DELETE(self->price);
    Py_TYPE(self)->tp_free((PyObject*)self);
}


PyObject *wrapping_dap_chain_net_srv_xchange_price_get_token_sell(PyObject *self, void *closure){
    UNUSED(closure);
    return Py_BuildValue("s", PRICE(self)->token_sell);
}
PyObject *wrapping_dap_chain_net_srv_xchange_price_get_datoshi_sell(PyObject *self, void *closure){
    UNUSED(closure);
    DapMathObject *obj_math = PyObject_NEW(DapMathObject, &DapMathObjectType);
    obj_math->value = PRICE(self)->datoshi_sell;
    return (PyObject*)obj_math;
}
PyObject *wrapping_dap_chain_net_srv_xchange_price_get_net(PyObject *self, void *closure){
    UNUSED(closure);
    PyDapChainNetObject *obj_net = PyObject_NEW(PyDapChainNetObject, &DapChainNetObjectType);
    obj_net->chain_net = PRICE(self)->net;
    return (PyObject*)obj_net;
}
PyObject *wrapping_dap_chain_net_srv_xchange_price_get_token_buy(PyObject *self, void *closure){
    UNUSED(closure);
    return Py_BuildValue("s", PRICE(self)->token_buy);
}
PyObject *wrapping_dap_chain_net_srv_xchange_price_get_rate(PyObject *self, void *closure){
    UNUSED(closure);
    DapMathObject *obj_math = PyObject_New(DapMathObject, &DapMathObjectType);
    obj_math->value = PRICE(self)->rate;
    return (PyObject*)obj_math;
}
PyObject *wrapping_dap_chain_net_srv_xchange_price_get_fee(PyObject *self, void *closure){
    UNUSED(closure);
    DapMathObject *order_fee = PyObject_New(DapMathObject, &DapMathObjectType);
    DapMathObject *network_fee = PyObject_New(DapMathObject, &DapMathObjectType);

    uint256_t current_net_fee_val;
    dap_chain_addr_t comission_addr;
    uint16_t comission_type;
    dap_chain_net_srv_xchange_get_fee(PRICE(self)->net->pub.id, &current_net_fee_val, &comission_addr,  &comission_type);

    order_fee->value = PRICE(self)->fee;
    network_fee->value = current_net_fee_val;

    PyDapChainAddrObject *obj_addr = PyObject_New(PyDapChainAddrObject, &DapChainAddrObjectType);
    obj_addr->addr = DAP_DUP(&comission_addr);

    PyObject *res = PyDict_New();
    PyDict_SetItemString(res, "order_fee", (PyObject *)order_fee);
    PyDict_SetItemString(res, "network_fee", (PyObject *)network_fee);
    PyDict_SetItemString(res, "address", (PyObject *)obj_addr);
    PyDict_SetItemString(res, "type", Py_BuildValue("s", dap_chain_srv_fee_type_to_str(comission_type)));

    const char *l_native_ticker = PRICE(self)->net->pub.native_ticker;
    const char *l_service_ticker = (comission_type == SERVICE_FEE_OWN_FIXED || comission_type == SERVICE_FEE_OWN_PERCENT) ?
                                   PRICE(self)->token_buy : l_native_ticker;

    PyDict_SetItemString(res, "token", Py_BuildValue("s", l_service_ticker));
    return (PyObject*)res;
}
PyObject *wrapping_dap_chain_net_srv_xchange_price_get_tx_hash(PyObject *self, void *closure){
    UNUSED(closure);
    PyDapHashFastObject *obj_hash = PyObject_New(PyDapHashFastObject, &DapChainHashFastObjectType);
    obj_hash->hash_fast = DAP_NEW(dap_chain_hash_fast_t);
    dap_chain_hash_fast_t l_hf = PRICE(self)->tx_hash;
    memcpy(obj_hash->hash_fast, &l_hf, sizeof(dap_chain_hash_fast_t));
    obj_hash->origin = true;
    return (PyObject*)obj_hash;
}
PyObject *wrapping_dap_chain_net_srv_xchange_price_get_order_hash(PyObject *self, void *closure){
    UNUSED(closure);
    PyDapHashFastObject *obj_hf = PyObject_New(PyDapHashFastObject, &DapChainHashFastObjectType);
    obj_hf->hash_fast = DAP_NEW(dap_hash_fast_t);
    dap_chain_hash_fast_t l_hf = PRICE(self)->order_hash;
    memcpy(obj_hf->hash_fast, &l_hf, sizeof(dap_chain_hash_fast_t));
    obj_hf->origin = true;
    return (PyObject*)obj_hf;
}

PyObject *wrapping_dap_chain_net_srv_xchange_price_get_completion_rate(PyObject *self, void *closure){
    return Py_BuildValue("l",dap_chain_net_srv_xchange_get_order_completion_rate(PRICE(self)->net, PRICE(self)->order_hash));
}

PyObject *wrapping_dap_chain_net_srv_xchange_price_get_order_creator_address(PyObject *self, void *closure){

    PyDapChainAddrObject *obj_addr = PyObject_New(PyDapChainAddrObject, &DapChainAddrObjectType);
    obj_addr->addr = DAP_DUP(&PRICE(self)->creator_addr);
    return (PyObject *)obj_addr;
}

PyObject *wrapping_dap_chain_net_srv_xchange_price_get_order_creation_date(PyObject *self, void *closure){

    PyObject *obj_ts_float = PyLong_FromLong(PRICE(self)->creation_date);
    PyObject *obj_ts = Py_BuildValue("(O)", obj_ts_float);
    PyDateTime_IMPORT;
    PyObject *obj_dt = PyDateTime_FromTimestamp(obj_ts);
    return obj_dt;
}

PyObject *wrapping_dap_chain_net_srv_xchange_price_get_status(PyObject *self, void *closure){
    switch (dap_chain_net_srv_xchange_get_order_status(PRICE(self)->net, PRICE(self)->order_hash))
    {
        case XCHANGE_ORDER_STATUS_OPENED:
            return Py_BuildValue("s", "OPENED");

        case XCHANGE_ORDER_STATUS_CLOSED:
            return Py_BuildValue("s", "CLOSED");

        default:;
    }
    return Py_BuildValue("s", "UNKNOWN");
}

PyObject *wrapping_dap_chain_net_srv_xchange_price_invalidate(PyObject *self, PyObject *argv) {
    (void) self;
    PyObject *obj_fee;
    PyObject *obj_wallet;

    if (!PyArg_ParseTuple(argv, "OO", &obj_fee, &obj_wallet))
        return NULL;

    if (!DapMathObject_Check(obj_fee)) {
        PyErr_SetString(PyExc_AttributeError, "The first argument was passed incorrectly. This must be "
                                              "an instance of an object of type Math.");
        return NULL;
    }

    if (!PyDapChainWalletObject_Check(obj_wallet)) {
        PyErr_SetString(PyExc_AttributeError, "The second parameter to the function passed an incorrect "
                                              "argument. This must be an instance of the Wallet class.");
        return NULL;
    }

    char *l_tx_hash_out = NULL;
    int l_ret_code = dap_chain_net_srv_xchange_remove(PRICE(self)->net,
                                                      &PRICE(self)->order_hash,
                                                      ((DapMathObject *) obj_fee)->value,
                                                      ((PyDapChainWalletObject *) obj_wallet)->wallet, &l_tx_hash_out);
    switch (l_ret_code) {
        case XCHANGE_REMOVE_ERROR_OK: {
            return Py_BuildValue("s", l_tx_hash_out);
        }
        case XCHANGE_REMOVE_ERROR_INVALID_ARGUMENT: {
            PyErr_SetString(PyExc_RuntimeError, "One of the input arguments is not set correctly.");
            return NULL;
        }
        case XCHANGE_REMOVE_ERROR_FEE_IS_ZERO: {
            PyErr_SetString(PyExc_RuntimeError, "Fee is zero.");
            return NULL;
        }
        case XCHANGE_REMOVE_ERROR_CAN_NOT_FIND_TX: {
            PyErr_SetString(PyExc_RuntimeError, "Specified order not found.");
            return NULL;
        }
        case XCHANGE_REMOVE_ERROR_CAN_NOT_CREATE_PRICE: {
            PyErr_SetString(PyExc_RuntimeError, "Can't create price object from order.");
            return NULL;
        }
        case XCHANGE_REMOVE_ERROR_CAN_NOT_INVALIDATE_TX: {
            PyErr_SetString(PyExc_RuntimeError, "Can't create invalidate transaction.");
            return NULL;
        }
        default: {
            char *l_ret = dap_strdup_printf("An error occurred with an unknown code: %d.", l_ret_code);
            PyErr_SetString(PyExc_RuntimeError, l_ret);
            DAP_DELETE(l_ret);
            return NULL;
        }
    }
}

PyTypeObject PyDapChainNetSrvXchangeOrderObjectType = DAP_PY_TYPE_OBJECT(
        "CellFrame.Service.Xchange.Order", sizeof(PyDapChainNetSrvXchangeOrderObject),
        "Order from service xchange",
        .tp_dealloc = (destructor)DapChainNetSrvXchangePrice_free,
        .tp_getset = DapChainNetSrvXchangePriceGetSetDef,
        .tp_methods = DapChainNetSrvXchangePriceMethods);


PyObject *wrapping_dap_chain_net_srv_xchange_price_purchase(PyObject *self, PyObject *argv){
    PyObject *obj_wallet, *obj_fee, *obj_value;
    if (!PyArg_ParseTuple(argv, "OOO", &obj_value, &obj_fee, &obj_wallet)) {
        return NULL;
    }
    if (!DapMathObject_Check(obj_value)) {
        PyErr_SetString(PyExc_AttributeError, "The first argument was passed incorrectly. This must be "
                                              "an instance of an object of type Math.");
        return NULL;
    }
    if (!DapMathObject_Check(obj_fee)) {
        PyErr_SetString(PyExc_AttributeError, "The second argument was passed incorrectly. This must be "
                                              "an instance of an object of type Math.");
        return NULL;
    }
    if (!PyDapChainWalletObject_Check(obj_wallet)) {
        PyErr_SetString(PyExc_AttributeError, "The third parameter to the function passed an incorrect "
                                              "argument. This must be an instance of the Wallet class.");
        return NULL;
    }
    char *l_ret_tx_hash = NULL;
    dap_chain_net_srv_xchange_price_t *l_price = PRICE(self);
    int l_ret_code = dap_chain_net_srv_xchange_purchase(l_price->net, &l_price->order_hash,
                                                        ((DapMathObject*)obj_value)->value,
                                                        ((DapMathObject*)obj_fee)->value,
                                                        ((PyDapChainWalletObject*)obj_wallet)->wallet,
                                                        &l_ret_tx_hash);
    switch (l_ret_code) {
        case XCHANGE_PURCHASE_ERROR_OK: {
            return Py_BuildValue("s", l_ret_tx_hash);
        }
        default: {
            Py_RETURN_NONE;
        }
    }
}
