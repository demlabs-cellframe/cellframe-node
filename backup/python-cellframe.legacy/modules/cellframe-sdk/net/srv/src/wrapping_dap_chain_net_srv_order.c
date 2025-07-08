#include "wrapping_dap_chain_net_srv_order.h"
#include "node_address.h"

#define WRAPPING_DAP_CHAIN_NET_SRV_ORDER(a) ((PyDapChainNetSrvOrderObject*)a)

#define LOG_TAG "Service order wrapper"

static PyMethodDef DapChainNetSrvOrderMethods[]={
        {"size", (PyCFunction)wrapping_dap_chain_net_srv_order_get_size, METH_VARARGS, ""},
        {"find", (PyCFunction)wrapping_dap_chain_net_srv_order_find, METH_VARARGS | METH_STATIC, ""},
        {"delete", (PyCFunction)wrapping_dap_chain_net_srv_order_delete, METH_VARARGS | METH_STATIC, ""},
        {"save", (PyCFunction)wrapping_dap_chain_net_srv_order_save, METH_VARARGS, ""},
        {"getGdbGroup", (PyCFunction)wrapping_dap_chain_net_srv_order_get_gdb_group, METH_VARARGS | METH_STATIC, ""},
        {"addNotify", (PyCFunction)wrapping_dap_chain_net_srv_order_add_notify_callback, METH_VARARGS | METH_STATIC, ""},
        {}
};

static PyGetSetDef DapChaiNetSrvOrderGetsSets[] = {
        {"version", (getter)wrapping_dap_chain_net_srv_order_get_version, NULL, NULL, NULL},
        {"uid", (getter)wrapping_dap_chain_net_srv_order_get_srv_uid, NULL, NULL, NULL},
        {"direction", (getter)wrapping_dap_chain_net_srv_order_get_srv_direction, NULL, NULL, NULL},
        {"nodeAddr", (getter)wrapping_dap_chain_net_srv_order_get_srv_node_addr, NULL, NULL, NULL},
        {"condHash", (getter)wrapping_dap_chain_net_srv_order_get_srv_tx_cond_hash, NULL, NULL, NULL},
        {"priceUnit", (getter)wrapping_dap_chain_net_srv_order_get_srv_price_unit, NULL, NULL, NULL},
        {"tsCreated", (getter)wrapping_dap_chain_net_srv_order_get_srv_ts_created, NULL, NULL, NULL},
        {"tsExpires", (getter)wrapping_dap_chain_net_srv_order_get_srv_ts_expires, NULL, NULL, NULL},
        {"srvPrice", (getter)wrapping_dap_chain_net_srv_order_get_srv_price, NULL, NULL, NULL},
        {"srvPriceTicker", (getter)wrapping_dap_chain_net_srv_order_get_srv_price_ticker, NULL, NULL, NULL},
        {"extSize", (getter)wrapping_dap_chain_net_srv_order_get_srv_ext_size, NULL, NULL, NULL},
        {"extSign", (getter)wrapping_dap_chain_net_srv_order_get_srv_ext_n_sign, NULL, NULL, NULL},
        {}
};

PyTypeObject DapChainNetSrvOrderObjectType = DAP_PY_TYPE_OBJECT(
        "CellFrame.ChainNetSrvOrder", sizeof(PyDapChainNetSrvOrderObject),
        "Chain net srv client object",
        .tp_methods = DapChainNetSrvOrderMethods,
        .tp_getset = DapChaiNetSrvOrderGetsSets,
        .tp_init = (initproc)PyDapChainNetSrvOrder_init);


typedef struct _wrapping_order_callable{
    PyObject *func;
    PyObject *arg;
}_wrapping_order_callable_t;

void _wrapping_handler_add_order_notify(dap_store_obj_t *a_obj, void *a_arg)
{
    if (!a_arg)
        return;
    _wrapping_order_callable_t *l_callback = (_wrapping_order_callable_t *)a_arg;
    PyGILState_STATE state = PyGILState_Ensure();
    PyDapChainNetSrvOrderObject *l_obj_order = (PyDapChainNetSrvOrderObject *)Py_None;
    if (a_obj->value_len != 0 && dap_store_obj_get_type(a_obj) != DAP_GLOBAL_DB_OPTYPE_DEL) {
        l_obj_order = PyObject_New(PyDapChainNetSrvOrderObject, &DapChainNetSrvOrderObjectType);
        l_obj_order->order = DAP_DUP_SIZE(a_obj->value, a_obj->value_len);
    }
    char l_op_code[2];
    l_op_code[0] = dap_store_obj_get_type(a_obj);
    l_op_code[1] = '\0';
    PyObject *l_args = Py_BuildValue("sssOO", l_op_code, a_obj->group, a_obj->key, l_obj_order, l_callback->arg);
    PyObject_CallObject(l_callback->func, l_args);
    Py_DECREF(l_args);
    PyGILState_Release(state);
}

int PyDapChainNetSrvOrder_init(PyDapChainNetSrvOrderObject *self, PyObject *args, PyObject *kwds){
    const char *kwlist[] = {
            "net",
            "direction",
            "srvUID",
            "nodeAddr",
            "txCondHash",
            "price",
            "priceUnit",
            "priceTicker",
            "expires",
            "ext",
            "units",
//            "extSize",
//            "region",
//            "continentNum",
            "key",
            NULL
    };
    PyObject *obj_direction, *obj_srv_uid, *obj_node_addr, *obj_tx_cond_hash, *obj_price_unit;
    PyDapChainNetObject *obj_net;
    uint64_t price;
    char *price_ticker;
    unsigned long expires;
    unsigned long units;
    PyObject *obj_ext, *obj_key;
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "OOOOOkOsOOIO", (char **)kwlist, &obj_net, &obj_direction, &obj_srv_uid,
                                     &obj_node_addr, &obj_tx_cond_hash, &price, &obj_price_unit, &price_ticker,
                                     &expires, &obj_ext, &units, &obj_key)){
        return -1;
    }
    if (!PyDapChainNet_Check(obj_net)){
        return -1;
    }
    void* l_ext = (void*)PyBytes_AsString(obj_ext);
    size_t l_ext_size = PyBytes_Size(obj_ext);
    uint256_t l_price = dap_chain_uint256_from(price);
    dap_chain_hash_fast_t l_hf = {};
    if (obj_tx_cond_hash != Py_None)
        l_hf = *((PyDapHashFastObject *)obj_tx_cond_hash)->hash_fast;
    self->order = dap_chain_net_srv_order_compose(
            ((PyDapChainNetObject *) obj_net)->chain_net,
            ((PyDapChainNetSrvOrderDirectionObject *) obj_direction)->direction,
            ((PyDapChainNetSrvUIDObject *) obj_srv_uid)->net_srv_uid,
            ((PyDapNodeAddrObject *) obj_node_addr)->addr,
            l_hf,
            &l_price,
            ((PyDapChainNetSrvPriceUnitUIDObject *) obj_price_unit)->price_unit_uid,
            price_ticker,
            (time_t) expires,
            l_ext,
            l_ext_size,
            units,
            "",
            0,
            ((PyCryptoKeyObject *) obj_key)->key
    );
    return 0;
}

PyObject *wrapping_dap_chain_net_srv_order_get_version(PyObject *self, void *closure){
    (void)closure;
    if(WRAPPING_DAP_CHAIN_NET_SRV_ORDER(self)->order == NULL){
        return Py_BuildValue("H", 0);
    }else{
        return Py_BuildValue("H", WRAPPING_DAP_CHAIN_NET_SRV_ORDER(self)->order->version);
    }
}
PyObject *wrapping_dap_chain_net_srv_order_get_srv_uid(PyObject *self, void *closure){
    (void)closure;
    PyDapChainNetSrvUIDObject *obj_srv_uid = PyObject_New(PyDapChainNetSrvUIDObject,
                                                          &DapChainNetSrvUidObjectType);
    if(WRAPPING_DAP_CHAIN_NET_SRV_ORDER(self)->order == NULL){
        obj_srv_uid->net_srv_uid.uint64 = 0;
    }else{
        obj_srv_uid->net_srv_uid = WRAPPING_DAP_CHAIN_NET_SRV_ORDER(self)->order->srv_uid;
    }
    return (PyObject*)obj_srv_uid;
}
PyObject *wrapping_dap_chain_net_srv_order_get_srv_direction(PyObject *self, void *closure){
    (void)closure;
    PyDapChainNetSrvOrderDirectionObject *srv_direction =
            PyObject_New(PyDapChainNetSrvOrderDirectionObject,
                         &DapChainNetSrvOrderDirectionObjectType);
    if(WRAPPING_DAP_CHAIN_NET_SRV_ORDER(self)->order == NULL){
        srv_direction->direction = 0;
    }else{
        srv_direction->direction = WRAPPING_DAP_CHAIN_NET_SRV_ORDER(self)->order->direction;
    }
    return (PyObject*)srv_direction;
}
PyObject *wrapping_dap_chain_net_srv_order_get_srv_node_addr(PyObject *self, void *closure){
    (void)closure;
    if(WRAPPING_DAP_CHAIN_NET_SRV_ORDER(self)->order == NULL){
        Py_RETURN_NONE;
    }else{
        PyDapNodeAddrObject *l_obj_node_addr = PyObject_New(PyDapNodeAddrObject, &DapNodeAddrObjectType);
        l_obj_node_addr->addr = WRAPPING_DAP_CHAIN_NET_SRV_ORDER(self)->order->node_addr;
        return (PyObject*)l_obj_node_addr;
    }
}
PyObject *wrapping_dap_chain_net_srv_order_get_srv_tx_cond_hash(PyObject *self, void *closure){
    (void)closure;
    if(WRAPPING_DAP_CHAIN_NET_SRV_ORDER(self)->order == NULL){
        Py_RETURN_NONE;
    }else{
        PyDapHashFastObject *l_obj_hf = PyObject_New(PyDapHashFastObject, &DapChainHashFastObjectType);
        l_obj_hf->hash_fast = &WRAPPING_DAP_CHAIN_NET_SRV_ORDER(self)->order->tx_cond_hash;
        l_obj_hf->origin = false;
        return (PyObject*)l_obj_hf;
    }
}
PyObject *wrapping_dap_chain_net_srv_order_get_srv_price_unit(PyObject *self, void *closure){
    (void)closure;
    PyDapChainNetSrvPriceUnitUIDObject *l_obj_srv_price_uid = PyObject_New(PyDapChainNetSrvPriceUnitUIDObject,
                                                                           &DapChainNetSrvPriceUnitUidObjectType);
    if(WRAPPING_DAP_CHAIN_NET_SRV_ORDER(self)->order == NULL){
        l_obj_srv_price_uid->price_unit_uid.enm = SERV_UNIT_UNDEFINED;
    }else{
        l_obj_srv_price_uid->price_unit_uid = WRAPPING_DAP_CHAIN_NET_SRV_ORDER(self)->order->price_unit;
    }
    return (PyObject*)l_obj_srv_price_uid;
}
PyObject *wrapping_dap_chain_net_srv_order_get_srv_ts_created(PyObject *self, void *closure){
    (void)closure;
    if(WRAPPING_DAP_CHAIN_NET_SRV_ORDER(self)->order == NULL){
        return Py_BuildValue("k", 0);
    }else{
        return Py_BuildValue("k", WRAPPING_DAP_CHAIN_NET_SRV_ORDER(self)->order->ts_created);
    }
}
PyObject *wrapping_dap_chain_net_srv_order_get_srv_ts_expires(PyObject *self, void *closure){
    (void)closure;
    if(WRAPPING_DAP_CHAIN_NET_SRV_ORDER(self)->order == NULL){
        return Py_BuildValue("k", 0);
    }else{
        return Py_BuildValue("k", WRAPPING_DAP_CHAIN_NET_SRV_ORDER(self)->order->ts_expires);
    }
}
PyObject *wrapping_dap_chain_net_srv_order_get_srv_price(PyObject *self, void *closure){
    (void)closure;
    if(WRAPPING_DAP_CHAIN_NET_SRV_ORDER(self)->order == NULL){
        return Py_BuildValue("k", 0);
    }else{
        return Py_BuildValue("k", WRAPPING_DAP_CHAIN_NET_SRV_ORDER(self)->order->price);
    }
}
PyObject *wrapping_dap_chain_net_srv_order_get_srv_price_ticker(PyObject *self, void *closure){
    (void)closure;
    if(WRAPPING_DAP_CHAIN_NET_SRV_ORDER(self)->order == NULL){
        return Py_BuildValue("s", "");
    }else{
        return Py_BuildValue("s", WRAPPING_DAP_CHAIN_NET_SRV_ORDER(self)->order->price_ticker);
    }
}
//PyObject *wrapping_dap_chain_net_srv_order_get_srv_free_space(PyObject *self, void *closure){}
PyObject *wrapping_dap_chain_net_srv_order_get_srv_ext_size(PyObject *self, void *closure){
    (void)closure;
    if(WRAPPING_DAP_CHAIN_NET_SRV_ORDER(self)->order == NULL){
        return Py_BuildValue("I", 0);
    }else{
        return Py_BuildValue("I", WRAPPING_DAP_CHAIN_NET_SRV_ORDER(self)->order->ext_size);
    }
}
PyObject *wrapping_dap_chain_net_srv_order_get_srv_ext_n_sign(PyObject *self, void *closure) {
    (void) closure;
    if (WRAPPING_DAP_CHAIN_NET_SRV_ORDER(self)->order != NULL) {
        dap_sign_t *l_sign = (dap_sign_t*)&WRAPPING_DAP_CHAIN_NET_SRV_ORDER(self)->order->ext_n_sign[WRAPPING_DAP_CHAIN_NET_SRV_ORDER(self)->order->ext_size];
        PyObject *obj_sign = PyDapSignObject_Cretae(l_sign);
        return obj_sign;
    }
    Py_RETURN_NONE;
}

//Functions
PyObject *wrapping_dap_chain_net_srv_order_get_size(PyObject *self, PyObject *args){
    (void)args;
    if (WRAPPING_DAP_CHAIN_NET_SRV_ORDER(self)->order == NULL){
        return Py_BuildValue("n", 0);
    }else {
        return Py_BuildValue("n", dap_chain_net_srv_order_get_size(WRAPPING_DAP_CHAIN_NET_SRV_ORDER(self)->order));
    }
}
//PyObject *wrapping_dap_chain_net_srv_order_set_continent_region(PyObject *self, PyObject *args){}
//PyObject *wrapping_dap_chain_net_srv_order_get_continent_region(PyObject *self, PyObject *args){}

//PyObject *wrapping_dap_chain_net_srv_order_get_country_code(PyObject *self, PyObject *args){}
//PyObject *wrapping_dap_chain_net_srv_order_continents_count(PyObject *self, PyObject *args){}
//PyObject *wrapping_dap_chain_net_srv_order_continent_to_str(PyObject *self, PyObject *args){}
//PyObject *wrapping_dap_chain_net_srv_order_continent_to_num(PyObject *self, PyObject *args){}

PyObject *wrapping_dap_chain_net_srv_order_find(PyObject *self, PyObject *args){
    (void)self;
    PyDapChainNetObject *obj_net;
    PyDapHashFastObject *obj_order_hash;
    if (!PyArg_ParseTuple(args, "OO", &obj_net, &obj_order_hash)){
        PyErr_SetString(PyExc_ValueError, "Function takes exactly two arguments");
        return NULL;
    }
    dap_chain_net_srv_order_t *l_order = NULL;
    if(!PyDapChainNet_Check(obj_net)){
        PyErr_SetString(PyExc_ValueError, "The first argument must be ChainNet object");
        return NULL;
    }
    if (PyUnicode_Check(obj_order_hash)){
        const char *l_str = PyUnicode_AsUTF8((PyObject *)obj_order_hash);
        l_order = dap_chain_net_srv_order_find_by_hash_str(obj_net->chain_net, l_str);
        if (l_order == NULL){
            Py_RETURN_NONE;
        }
        PyDapChainNetSrvOrderObject *l_obj_order = PyObject_New(PyDapChainNetSrvOrderObject,
                                                                &DapChainNetSrvOrderObjectType);
        l_obj_order->order = l_order;
        return (PyObject*)l_obj_order;
    }
    if (PyDapHashFast_Check(obj_order_hash)){
        l_order = dap_chain_net_srv_order_find_by_hash(obj_net->chain_net, obj_order_hash->hash_fast);
        if (l_order == NULL){
            Py_RETURN_NONE;
        }
        PyDapChainNetSrvOrderObject *l_obj_order = PyObject_New(PyDapChainNetSrvOrderObject,
                                                                &DapChainNetSrvOrderObjectType);
        l_obj_order->order = l_order;
        return (PyObject*)l_obj_order;
    }
    PyErr_SetString(PyExc_ValueError, "The second argument must be a string or HashFast object");
    return NULL;
}

PyObject *wrapping_dap_chain_net_srv_order_delete(PyObject *self, PyObject *args){
    (void)self;
    PyDapChainNetObject *obj_net;
    PyDapHashFastObject *obj_order_hash;
    if (!PyArg_ParseTuple(args, "OO", &obj_net, &obj_order_hash)){
        PyErr_SetString(PyExc_ValueError, "Function takes exactly two arguments");
        return NULL;
    }
    if(!PyDapChainNet_Check(obj_net)){
        PyErr_SetString(PyExc_ValueError, "The first argument must be ChainNet object");
        return NULL;
    }
    int res = -1;
    if (PyUnicode_Check(obj_order_hash)){
        const char *l_str = PyUnicode_AsUTF8((PyObject *)obj_order_hash);
        res = dap_chain_net_srv_order_delete_by_hash_str_sync(obj_net->chain_net, l_str);
        return Py_BuildValue("i", res);
    }
    if (PyDapHashFast_Check(obj_order_hash)) {
        res =dap_chain_net_srv_order_delete_by_hash(obj_net->chain_net,
                                               ((PyDapHashFastObject*)obj_order_hash)->hash_fast);
        return Py_BuildValue("i", res);
    }
    PyErr_SetString(PyExc_ValueError, "The second argument must be a string or HashFast object");
    return NULL;
}

PyObject *wrapping_dap_chain_net_srv_order_find_all_by(PyObject *self, PyObject *args){
    return NULL;
}

PyObject *wrapping_dap_chain_net_srv_order_save(PyObject *self, PyObject *args){
    PyDapChainNetObject *obj_net;
    if(!PyArg_ParseTuple(args, "O", &obj_net)){
        PyErr_SetString(PyExc_ValueError, "Function takes exactly one argument");
        return NULL;
    }
    if(!PyDapChainNet_Check(obj_net)){
        PyErr_SetString(PyExc_ValueError, "The first argument must be ChainNet object");
        return NULL;
    }
    char* res = NULL;
    dap_chain_net_t *l_net = obj_net->chain_net;
    res = dap_chain_net_srv_order_save(l_net, WRAPPING_DAP_CHAIN_NET_SRV_ORDER(self)->order, false);
    if (res == NULL)
        Py_RETURN_NONE;
    PyObject *l_obj_ret = Py_BuildValue("s", res);
    DAP_DELETE(res);
    return l_obj_ret;
}
PyObject *wrapping_dap_chain_net_srv_order_get_gdb_group(PyObject *self, PyObject *args){
    (void)self;
    PyDapChainNetObject *obj_net;
    if(!PyArg_ParseTuple(args, "O", &obj_net)){
        PyErr_SetString(PyExc_ValueError, "Function takes exactly one argument");
        return NULL;
    }
    if(!PyDapChainNet_Check(obj_net)){
        PyErr_SetString(PyExc_ValueError, "The first argument must be ChainNet object");
        return NULL;
    }
    char *l_str_srv_order_gdb_group = dap_chain_net_srv_order_get_gdb_group(obj_net->chain_net);
    PyObject *l_str_ret_obj = Py_BuildValue("s", l_str_srv_order_gdb_group);
    DAP_DELETE(l_str_srv_order_gdb_group);
    return l_str_ret_obj;
}

PyObject *wrapping_dap_chain_net_srv_order_add_notify_callback(PyObject *self, PyObject *args){
    (void)self;
    PyDapChainNetObject *obj_net;
    PyObject *func_call, *call_arg;
    if (!PyArg_ParseTuple(args, "OOO", &obj_net, &func_call, &call_arg)){
        return NULL;
    }
    if (!PyDapChainNet_Check(obj_net)){
        PyErr_SetString(PyExc_AttributeError, "The first argument must be ChainNet object");
        return NULL;
    }
    if (!PyCallable_Check(func_call)){
        PyErr_SetString(PyExc_AttributeError, "The second argument must be a callable");
        return NULL;
    }
    _wrapping_order_callable_t *l_callback = DAP_NEW(_wrapping_order_callable_t);
    if (!l_callback) {
        log_it(L_CRITICAL, "Memory allocation error");
        return NULL;
    }
    l_callback->func = func_call;
    l_callback->arg = call_arg;
    Py_INCREF(func_call);
    Py_INCREF(call_arg);
    dap_chain_net_srv_order_add_notify_callback(obj_net->chain_net,
                                                _wrapping_handler_add_order_notify, l_callback);
    Py_RETURN_NONE;
}
