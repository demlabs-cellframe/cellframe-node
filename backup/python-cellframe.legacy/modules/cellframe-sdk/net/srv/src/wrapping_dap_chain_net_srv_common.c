#include "wrapping_dap_chain_net_srv_common.h"

/* Attribute for ChainNetSrvPrice */
#define WRAPPING_DAP_CHAIN_NET_SRV_PRICE(a) ((PyDapChainNetSrvPriceObject*) a)

static PyGetSetDef DapChainNetSrvPrice_GetsSetsDef[] = {
        {"wallet", (getter)wrapping_dap_chain_net_srv_get_wallet, NULL, NULL, NULL},
        {"netName", (getter)wrapping_dap_chain_net_srv_get_net_name, NULL, NULL, NULL},
        {"net", (getter)wrapping_dap_chain_net_srv_get_net, NULL, NULL, NULL},
        {"valueDatoshi", (getter)wrapping_dap_chain_net_srv_get_value_datoshi, NULL, NULL, NULL},
        {"token", (getter)wrapping_dap_chain_net_srv_get_token, NULL, NULL, NULL},
        {"units", (getter)wrapping_dap_chain_net_srv_get_units, NULL, NULL, NULL},
        {"unitsUid", (getter)wrapping_dap_chain_net_srv_get_units_uid, NULL, NULL, NULL},
        {}
};

PyTypeObject DapChainNetSrvPriceObjectType = DAP_PY_TYPE_OBJECT(
        "CellFrame.ChainNetSrvPrice", sizeof(PyDapChainNetSrvPriceObject),
        "Chain net srv price object",
        .tp_getset = DapChainNetSrvPrice_GetsSetsDef);

PyObject *wrapping_dap_chain_net_srv_get_wallet(PyObject *self, void *closure){
    (void)closure;
    return NULL;
}
PyObject *wrapping_dap_chain_net_srv_get_net_name(PyObject *self, void *closure){
    (void)closure;
    Py_RETURN_NONE;
}
PyObject *wrapping_dap_chain_net_srv_get_net(PyObject *self, void *closure){
    (void)closure;
    Py_RETURN_NONE;
}
PyObject *wrapping_dap_chain_net_srv_get_value_datoshi(PyObject *self, void *closure){
    (void)closure;
    return Py_BuildValue("k", WRAPPING_DAP_CHAIN_NET_SRV_PRICE(self)->price.value_datoshi);
}
PyObject *wrapping_dap_chain_net_srv_get_token(PyObject *self, void *closure){
    (void)closure;
    return Py_BuildValue("s", WRAPPING_DAP_CHAIN_NET_SRV_PRICE(self)->price.token);
}
PyObject *wrapping_dap_chain_net_srv_get_units(PyObject *self, void *closure){
    (void)closure;
    return Py_BuildValue("k", WRAPPING_DAP_CHAIN_NET_SRV_PRICE(self)->price.units);
}
PyObject *wrapping_dap_chain_net_srv_get_units_uid(PyObject *self, void *closure){
    (void)closure;
    PyDapChainNetSrvPriceUnitUIDObject *l_price_unit_uid = PyObject_New(PyDapChainNetSrvPriceUnitUIDObject, &DapChainNetSrvPriceUnitUidObjectType);
    l_price_unit_uid->price_unit_uid = WRAPPING_DAP_CHAIN_NET_SRV_PRICE(self)->price.units_uid;
    return (PyObject*)l_price_unit_uid;
}

/* wrapping dap_chain_net_srv_order_direction */
static PyMethodDef DapChainNetSrvOrderDirection_Methods[] = {
        {"getDirBuy", (PyCFunction)wrapping_dap_chain_net_srv_order_direction_get_serv_dir_buy, METH_NOARGS | METH_STATIC, ""},
        {"getDirSell", (PyCFunction)wrapping_dap_chain_net_srv_order_direction_get_serv_dir_sell, METH_NOARGS | METH_STATIC, ""},
        {"getDirUndefined", (PyCFunction)wrapping_dap_chain_net_srv_order_direction_get_serv_dir_undefined, METH_NOARGS | METH_STATIC, ""},
        {}
};

PyTypeObject DapChainNetSrvOrderDirectionObjectType = DAP_PY_TYPE_OBJECT(
        "CellFrame.ChainNetSrvOrderDirection", sizeof(PyDapChainNetSrvOrderDirectionObject),
        "Chain net srv order direction object",
        .tp_str = DapChainNetSrvOrderDirection_str,
        .tp_methods = DapChainNetSrvOrderDirection_Methods);

PyObject *DapChainNetSrvOrderDirection_str(PyObject *self){
    char *ret;
    switch (((PyDapChainNetSrvOrderDirectionObject*)self)->direction) {
        case 1:
            ret = "SERV_DIR_BUY";
            break;
        case 2:
            ret = "SERV_DIR_SELL";
            break;
        default:
            ret = "SERV_DIR_UNDEFINED";
            break;
    }
    return Py_BuildValue("s", ret);
}

PyObject *wrapping_dap_chain_net_srv_order_direction_get_serv_dir_buy(PyObject *self, PyObject *args){
    (void)self;
    (void)args;
    PyDapChainNetSrvOrderDirectionObject *l_obj = PyObject_New(
            PyDapChainNetSrvOrderDirectionObject,
            &DapChainNetSrvOrderDirectionObjectType);
    l_obj->direction = SERV_DIR_BUY;
    return (PyObject*)l_obj;
}
PyObject *wrapping_dap_chain_net_srv_order_direction_get_serv_dir_sell(PyObject *self, PyObject *args){
    (void)self;
    (void)args;
    PyDapChainNetSrvOrderDirectionObject *l_obj = PyObject_New(
            PyDapChainNetSrvOrderDirectionObject,
            &DapChainNetSrvOrderDirectionObjectType);
    l_obj->direction = SERV_DIR_SELL;
    return (PyObject*)l_obj;
}
PyObject *wrapping_dap_chain_net_srv_order_direction_get_serv_dir_undefined(PyObject *self, PyObject *args){
    (void)self;
    (void)args;
    PyDapChainNetSrvOrderDirectionObject *l_obj = PyObject_New(
            PyDapChainNetSrvOrderDirectionObject,
            &DapChainNetSrvOrderDirectionObjectType);
    l_obj->direction = SERV_DIR_UNDEFINED;
    return (PyObject*)l_obj;
}
