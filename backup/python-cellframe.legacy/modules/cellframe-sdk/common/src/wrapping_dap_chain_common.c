#include "wrapping_dap_chain_common.h"

/* Chain hash slow  */
static PyMethodDef DapChainHashSlowMethod[] = {
        {"toStr", (PyCFunction)dap_chain_hash_slow_to_str_py, METH_VARARGS | METH_STATIC, ""},
        {}
};

PyTypeObject DapChainHashSlowObjectType = DAP_PY_TYPE_OBJECT(
        "CellFrame.ChainHashSlow", sizeof(PyDapChainHashSlowObject),
        "Chain hash slow object",
        .tp_methods = DapChainHashSlowMethod);

/* Hash slow kind */
PyTypeObject DapChainHashSlowKindObjectType = DAP_PY_TYPE_OBJECT(
        "CellFrame.ChainSlowKind", sizeof(PyDapChainHashSlowKindObject),
        "Chain slow kind object");

/* Chain addr */
static PyMethodDef DapChainAddrMethods[] = {
        {"toStr", (PyCFunction)dap_chain_addr_to_str_py, METH_VARARGS, ""},
        {"fromStr", (PyCFunction)dap_chain_addr_from_str_py, METH_VARARGS | METH_STATIC, ""},
        {"fill", (PyCFunction)dap_chain_addr_fill_py, METH_VARARGS | METH_STATIC, ""},
        {"fillFromKey", (PyCFunction)dap_chain_addr_fill_from_key_py, METH_VARARGS | METH_STATIC, ""},
        {"checkSum", (PyCFunction)dap_chain_addr_check_sum_py, METH_VARARGS, ""},
        {"getNetId", (PyCFunction)dap_chain_addr_get_net_id_py, METH_NOARGS, ""},
        {NULL}
};

void PyDapChainAddrObject_free(PyDapChainAddrObject *self) {
    DAP_DELETE(self->addr);
    Py_TYPE(self)->tp_free((PyObject*)self);
}

PyTypeObject DapChainAddrObjectType = DAP_PY_TYPE_OBJECT(
        "CellFrame.ChainAddr", sizeof(PyDapChainAddrObject),
         "Chain address object",
        .tp_str = obj_addr_str,
        .tp_dealloc = (destructor)PyDapChainAddrObject_free,
        .tp_methods = DapChainAddrMethods);

/* Chain net id */
static PyMethodDef DapChainNetIdObjectMethods[] = {
        {"fromStr", (PyCFunction)dap_chain_net_id_from_str_py, METH_VARARGS | METH_STATIC, ""},
        {"long", (PyCFunction)dap_chain_net_id_get_long, METH_VARARGS, ""},
        {NULL}
};

PyTypeObject DapChainNetIdObjectType = DAP_PY_TYPE_OBJECT(
        "CellFrame.ChainNetID", sizeof(PyDapChainNetIdObject),
        "Chain net ID object",
        .tp_methods = DapChainNetIdObjectMethods);

PyTypeObject DapChainNetSrvUidObjectType = DAP_PY_TYPE_OBJECT(
        "CellFrame.ChainNetSrvUID", sizeof(PyDapChainNetSrvUIDObject),
        "Chain net srv uid object",
        .tp_str = PyDapChainNetSrvUIDObject_str,
        .tp_init = (initproc)PyDapChainNetSrvUIDObject_init);

/* Chain id */
PyTypeObject DapChainIdObjectType = DAP_PY_TYPE_OBJECT(
        "CellFrame.ChainID", sizeof(PyDapChainIDObject),
        "Chain id object",
        .tp_str = DapChainIdObject_str);

PyObject *DapChainIdObject_str(PyObject *self){
    char *l_str = dap_strdup_printf("0x%016"DAP_UINT64_FORMAT_x, ((PyDapChainIDObject*)self)->chain_id->uint64);
    PyObject *l_obj = Py_BuildValue("s", l_str);
    DAP_FREE(l_str);
    return l_obj;
}

/* Dap chain cell id */
PyTypeObject DapChainCellIdObjectType = DAP_PY_TYPE_OBJECT(
        "CellFrame.ChainCellID", sizeof(PyDapChainCellIDObject),
        "Chain cell id object",
        .tp_str = PyDapChainCellIdObject_str);

PyObject *PyDapChainCellIdObject_str(PyObject *self){
    char *l_str = dap_strdup_printf("0x%016"DAP_UINT64_FORMAT_x, ((PyDapChainCellIDObject*)self)->cell_id.uint64);
    PyObject *l_obj = Py_BuildValue("s", l_str);
    DAP_FREE(l_str);
    return l_obj;
}

PyObject *dap_chain_hash_slow_to_str_py(PyObject *self, PyObject *args){
    PyObject *obj_hash_slow;
    char *str;
    size_t str_max;
    if (!PyArg_ParseTuple(args, "O|s|n", &obj_hash_slow, &str, &str_max))
            return NULL;
    size_t res = dap_chain_hash_slow_to_str(((PyDapChainHashSlowObject*)obj_hash_slow)->hash_slow, str, str_max);
    return Py_BuildValue("ns", res, str_max);
}

PyObject *dap_chain_addr_to_str_py(PyObject *self, PyObject *args){
    PyObject *obj_chain_addr;
    if (!PyArg_ParseTuple(args, "O", &obj_chain_addr))
        return NULL;
    const dap_chain_addr_t *addr = PY_DAP_CHAIN_ADDR(obj_chain_addr);
    const char *res = dap_chain_addr_to_str_static(addr);
    PyObject *l_obj_res =  Py_BuildValue("s", res);
    return l_obj_res;
}

PyObject *dap_chain_addr_from_str_py(PyObject *self, PyObject *args){
    const char *str;
    if (!PyArg_ParseTuple(args, "s", &str))
        return NULL;
    dap_chain_addr_t *l_addr = dap_chain_addr_from_str(str);
    if (!l_addr){
        Py_RETURN_NONE;
    }
    PyDapChainAddrObject *obj = PyObject_New(PyDapChainAddrObject, &DapChainAddrObjectType);
    obj->addr = l_addr;
    return (PyObject*)obj;
}

PyObject *dap_chain_addr_fill_py(PyObject *self, PyObject *args){
    PyObject *obj_sign_type;
    PyObject *obj_pkey_hash;
    PyObject *obj_chain_net_id;
    if (!PyArg_ParseTuple(args, "OOO", &obj_sign_type, &obj_pkey_hash, &obj_chain_net_id)){
        PyErr_SetString(PyExc_AttributeError, "Function takes three arguments, signature type, public key hash, chain network ID.");
        return NULL;
    }
    if (self == NULL){
        PyDapChainAddrObject *obj_addr = PyObject_New(PyDapChainAddrObject, &DapChainAddrObjectType);
        obj_addr->addr = DAP_NEW(dap_chain_addr_t);
        dap_chain_addr_fill(
                obj_addr->addr,
                ((PyDapSignTypeObject*)obj_sign_type)->sign_type,
                ((PyDapHashFastObject*)obj_pkey_hash)->hash_fast,
                ((PyDapChainNetIdObject*)obj_chain_net_id)->net_id);
        return (PyObject*)obj_addr;
    }else{
        dap_chain_addr_fill(
                ((PyDapChainAddrObject*)self)->addr,
                ((PyDapSignTypeObject*)obj_sign_type)->sign_type,
                ((PyDapHashFastObject*)obj_pkey_hash)->hash_fast,
                ((PyDapChainNetIdObject*)obj_chain_net_id)->net_id);
        Py_RETURN_NONE;
    }
}

PyObject *dap_chain_addr_fill_from_key_py(PyObject *self, PyObject *args){
    (void)self;
    PyObject *key;
    PyObject *net_id;
    if (!PyArg_ParseTuple(args, "O|O", &key, &net_id))
        return NULL;
    PyDapChainAddrObject *obj_addr = PyObject_New(PyDapChainAddrObject, &DapChainAddrObjectType);
    obj_addr->addr = DAP_NEW(dap_chain_addr_t);
    dap_chain_addr_fill_from_key(obj_addr->addr, ((PyCryptoKeyObject*)key)->key, (((PyDapChainNetIdObject*)net_id)->net_id));
    return (PyObject*)obj_addr;
}

PyObject *dap_chain_addr_check_sum_py(PyObject *self, PyObject *args){
    return PyLong_FromLong(dap_chain_addr_check_sum(PY_DAP_CHAIN_ADDR(self)));
}

PyObject *obj_addr_str(PyObject *self){
    const char *l_addr = dap_chain_addr_to_str_static(PY_DAP_CHAIN_ADDR(self));
    PyObject* l_obj_res = Py_BuildValue("s", l_addr);
    return l_obj_res;
}

PyObject* dap_chain_addr_get_net_id_py(PyObject *self, PyObject *args){
    (void)args;
    PyObject *obj_net_id = _PyObject_New(&DapChainNetIdObjectType);
    ((PyDapChainNetIdObject*)obj_net_id)->net_id = PY_DAP_CHAIN_ADDR(self)->net_id;
    return Py_BuildValue("O", obj_net_id);
}

PyObject *dap_chain_net_id_from_str_py(PyObject *self, PyObject *args){
    const char *str;
    if (!PyArg_ParseTuple(args, "s", &str))
        return NULL;
    PyObject *obj_net_id = _PyObject_New(&DapChainNetIdObjectType);
    if (sscanf(str, "0x%016"DAP_UINT64_FORMAT_X, &((PyDapChainNetIdObject*)obj_net_id)->net_id.uint64) != 1) {
        char *l_err = dap_strdup_printf("Wrong id format (\"%s\"). Must be like \"0x0123456789ABCDE\"" , str);
        PyErr_SetString(PyExc_AttributeError, l_err);
        DAP_DELETE(l_err);
        return NULL;
    }
    return Py_BuildValue("O", obj_net_id);
}

PyObject *dap_chain_net_id_get_long(PyObject *self, PyObject *args)
{
    uint64_t l_id =((PyDapChainNetIdObject*)self)->net_id.uint64;
    return Py_BuildValue("L", l_id);
}


/* Chain net srv price unit uid */
static PyMethodDef PyDapChainNetSrvPriceUnitUID_Methods[] = {
        {"undefined", (PyCFunction)wrapping_dap_chain_net_srv_price_unit_uid_get_undefined, METH_NOARGS | METH_STATIC, ""},
        {"sec", (PyCFunction)wrapping_dap_chain_net_srv_price_unit_uid_get_sec, METH_NOARGS | METH_STATIC, ""},
        {"b", (PyCFunction)wrapping_dap_chain_net_srv_price_unit_uid_get_b, METH_NOARGS | METH_STATIC, ""},
        {}
};

PyTypeObject DapChainNetSrvPriceUnitUidObjectType = DAP_PY_TYPE_OBJECT(
        "CellFrame.ChainNetSrvPriceUnitUID", sizeof(PyDapChainNetSrvPriceUnitUIDObject),
        "Chain net srv price unit uid object",
        .tp_str = PyDapChainNetSrvPriceUnitUID_str,
        .tp_methods = PyDapChainNetSrvPriceUnitUID_Methods);

int PyDapChainNetSrvUIDObject_init(PyObject *self, PyObject *args, PyObject *kwds){
    (void)kwds;
    uint64_t uid;
    if (!PyArg_ParseTuple(args, "k", &uid)){
        return -1;
    }
    PyDapChainNetSrvUIDObject *l_obj_srv_uid = (PyDapChainNetSrvUIDObject*)self;
    l_obj_srv_uid->net_srv_uid.uint64 = uid;
    return 0;
}

PyObject *PyDapChainNetSrvPriceUnitUID_str(PyObject *self){
    dap_chain_srv_unit_enum_t l_enm = ((PyDapChainNetSrvPriceUnitUIDObject*)self)->price_unit_uid.enm;
    return Py_BuildValue("s", dap_chain_srv_unit_enum_to_str(l_enm));
}

PyObject *wrapping_dap_chain_net_srv_price_unit_uid_get_undefined(PyObject *self, PyObject *args){
    (void)self;
    (void)args;
    PyDapChainNetSrvPriceUnitUIDObject *obj_srv_price_uid = PyObject_New(PyDapChainNetSrvPriceUnitUIDObject,
                                                                         &DapChainNetSrvPriceUnitUidObjectType);
    obj_srv_price_uid->price_unit_uid.uint32 = SERV_UNIT_UNDEFINED;
    obj_srv_price_uid->price_unit_uid.enm = SERV_UNIT_UNDEFINED;
    return (PyObject*)obj_srv_price_uid;
}
PyObject *wrapping_dap_chain_net_srv_price_unit_uid_get_sec(PyObject *self, PyObject *args){
    (void)self;
    (void)args;
    PyDapChainNetSrvPriceUnitUIDObject *obj_srv_price_uid = PyObject_New(PyDapChainNetSrvPriceUnitUIDObject,
                                                                         &DapChainNetSrvPriceUnitUidObjectType);
    obj_srv_price_uid->price_unit_uid.uint32 = SERV_UNIT_SEC;
    obj_srv_price_uid->price_unit_uid.enm = SERV_UNIT_SEC;
    return (PyObject*)obj_srv_price_uid;
}
PyObject *wrapping_dap_chain_net_srv_price_unit_uid_get_b(PyObject *self, PyObject *args){
    (void)self;
    (void)args;
    PyDapChainNetSrvPriceUnitUIDObject *obj_srv_price_uid = PyObject_New(PyDapChainNetSrvPriceUnitUIDObject,
                                                                         &DapChainNetSrvPriceUnitUidObjectType);
    obj_srv_price_uid->price_unit_uid.uint32 = SERV_UNIT_B;
    obj_srv_price_uid->price_unit_uid.enm = SERV_UNIT_B;
    return (PyObject*)obj_srv_price_uid;
}

/* wrapping dap_chain_srv_uid_t */
PyObject* PyDapChainNetSrvUIDObject_str(PyObject *self){
    char *res = dap_strdup_printf("0x%016"DAP_UINT64_FORMAT_X, ((PyDapChainNetSrvUIDObject*)self)->net_srv_uid.uint64);
    PyObject *l_obj = Py_BuildValue("s", res);
    DAP_FREE(res);
    return l_obj;
}
