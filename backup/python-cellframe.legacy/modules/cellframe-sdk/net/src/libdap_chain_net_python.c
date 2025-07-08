#include "python-cellframe_common.h"
#include "libdap_chain_net_python.h"
#include "node_address.h"
#include "dap_chain_mempool.h"

static PyMethodDef DapChainNetMethods[] = {
        {"loadAll", dap_chain_net_load_all_py, METH_NOARGS | METH_STATIC, ""},
        {"stateGoTo", dap_chain_net_state_go_to_py, METH_VARARGS, ""},
        {"start", dap_chain_net_start_py, METH_VARARGS, ""},
        {"stop", dap_chain_net_stop_py, METH_VARARGS, ""},
        {"linksEstablish", dap_chain_net_links_establish_py, METH_VARARGS, ""},
        {"syncAll", dap_chain_net_sync_all_py, METH_VARARGS, ""},
        {"procDatapool", dap_chain_net_proc_datapool_py, METH_VARARGS, ""},
        {"byName", dap_chain_net_by_name_py, METH_VARARGS | METH_STATIC, ""},
        {"getNets", dap_chain_get_nets_py, METH_NOARGS | METH_STATIC, ""},
        {"byId", dap_chain_net_by_id_py, METH_VARARGS | METH_STATIC, ""},
        {"idByName", dap_chain_net_id_by_name_py, METH_VARARGS | METH_STATIC, ""},
        {"ledgerByNetName", dap_chain_ledger_by_net_name_py, METH_VARARGS | METH_STATIC, ""},
        {"getChainByName", dap_chain_net_get_chain_by_name_py, METH_VARARGS, ""},
        {"getCurAddr", dap_chain_net_get_cur_addr_py, METH_VARARGS, ""},
        {"getCurCell", dap_chain_net_get_cur_cell_py, METH_VARARGS, ""},
        {"getGdbGroupMempool", dap_chain_net_get_gdb_group_mempool_py, METH_VARARGS | METH_STATIC, ""},
        {"getGdbGroupMempoolByChainType", dap_chain_net_get_gdb_group_mempool_by_chain_type_py, METH_VARARGS, ""},
        {"linksConnect", dap_chain_net_links_connect_py, METH_VARARGS, ""},
        {"getChainByChainType", dap_chain_net_get_chain_by_chain_type_py, METH_VARARGS, ""},
        {"getLedger", dap_chain_net_get_ledger_py, METH_NOARGS, ""},
        {"getName", dap_chain_net_get_name_py, METH_NOARGS, ""},
        {"getTxByHash", dap_chain_net_get_tx_by_hash_py, METH_VARARGS, ""},
        {"verifyCodeToStr", (PyCFunction)dap_chain_net_convert_verify_code_to_str, METH_VARARGS | METH_STATIC, ""},
        {"configGetItem", (PyCFunction)dap_chain_net_get_config_by_item, METH_VARARGS, ""},
        {}
};

static PyGetSetDef DapChainNetGetsSetsDef[] = {
        {"id", (getter)dap_chain_net_python_get_id, NULL, NULL, NULL},
        {"chains", (getter)dap_chain_net_python_get_chains, NULL, NULL, NULL},
        {"txFee", (getter)dap_chain_net_get_tx_fee_py, NULL, NULL, NULL},
        {"txFeeAddr", (getter)dap_chain_net_get_tx_fee_addr_py, NULL, NULL, NULL},
        {"validatorMaxFee", (getter)dap_chain_net_get_validator_max_fee_py, NULL, NULL, NULL},
        {"validatorAverageFee", (getter)dap_chain_net_get_validator_average_fee_py, NULL, NULL, NULL},
        {"validatorMinFee", (getter)dap_chain_net_get_validator_min_fee_py, NULL, NULL, NULL},
        {"nativeTicker", (getter)dap_chain_net_get_native_ticker_py, NULL, NULL, NULL},
        {"autoproc", (getter)dap_chain_net_get_mempool_autoproc_py, NULL, NULL, NULL},
        {"gdb_group_alias", (getter)dap_chain_net_get_gdb_alias_py, NULL, NULL, NULL},

        {}
};

PyTypeObject DapChainNetObjectType = DAP_PY_TYPE_OBJECT(
        "CellFrame.ChainNet", sizeof(PyDapChainNetObject),
        "Chain net object",
        .tp_str = PyDapChainNet_str,
        .tp_methods = DapChainNetMethods,
        .tp_getset = DapChainNetGetsSetsDef);

int dap_chain_net_init_py(void){
    int res = dap_chain_net_init();
    return res;
}
void dap_chain_net_deinit_py(void){
    dap_chain_net_deinit();
}

PyObject* PyDapChainNet_str(PyObject *self){
    return Py_BuildValue("s", ((PyDapChainNetObject*)self)->chain_net->pub.name);
}

PyObject *dap_chain_net_load_all_py(PyObject *self, PyObject *args){
    dap_chain_net_load_all();
    return PyLong_FromLong(0);
}
PyObject *dap_chain_net_state_go_to_py(PyObject *self, PyObject *args){
    PyObject *obj_net_state;
    if (!PyArg_ParseTuple(args, "O", &obj_net_state))
        return NULL;
    int res = dap_chain_net_state_go_to(((PyDapChainNetObject*)self)->chain_net, ((PyDapChainNetStateObject*)obj_net_state)->state);
    return PyLong_FromLong(res);
}
PyObject *dap_chain_net_start_py(PyObject *self, PyObject *args){
    int res = dap_chain_net_start(((PyDapChainNetObject*)self)->chain_net);
    return PyLong_FromLong(res);
}
PyObject *dap_chain_net_stop_py(PyObject *self, PyObject *args){
    int res = dap_chain_net_stop(((PyDapChainNetObject*)self)->chain_net);
    return PyLong_FromLong(res);
}
PyObject *dap_chain_net_links_establish_py(PyObject *self, PyObject *args){
    int res = dap_chain_net_links_establish(((PyDapChainNetObject*)self)->chain_net);
    return PyLong_FromLong(res);
}
PyObject *dap_chain_net_sync_all_py(PyObject *self, PyObject *args){
    int res = dap_chain_net_sync(((PyDapChainNetObject*)self)->chain_net);
    return PyLong_FromLong(res);
}

PyObject *dap_chain_net_proc_datapool_py(PyObject *self, PyObject *args){
    //dap_chain_net_proc_datapool(((PyDapChainNetObject*)self)->chain_net);
    //return PyLong_FromLong(0);
    return NULL;
}

PyObject *dap_chain_net_by_name_py(PyObject *self, PyObject *args){
    const char *a_name;
    if (!PyArg_ParseTuple(args, "s", &a_name)) {
        PyErr_SetString(PyExc_AttributeError,
                        "Invalid argument specified. The first argument for this function must be a string. ");
        return NULL;
    }
    PyDapChainNetObject *obj_chain_net = PyObject_New(PyDapChainNetObject, &DapChainNetObjectType);
    ((PyDapChainNetObject*)obj_chain_net)->chain_net = dap_chain_net_by_name(a_name);
    if (((PyDapChainNetObject*)obj_chain_net)->chain_net == NULL){
        PyObject_Del(obj_chain_net);
        Py_RETURN_NONE;
    }
    return Py_BuildValue("O", obj_chain_net);
}
PyObject *dap_chain_get_nets_py(PyObject *self, PyObject *args){
    (void)self;
    (void)args;
    size_t l_net_count = dap_chain_net_count();
    PyObject *obj_nets = PyList_New(l_net_count);
    size_t i = 0;
    for (dap_chain_net_t *l_net = dap_chain_net_iter_start(); l_net; l_net = dap_chain_net_iter_next(l_net)) {    
        PyDapChainNetObject *l_obj_net = PyObject_New(PyDapChainNetObject, &DapChainNetObjectType);
        l_obj_net->chain_net = l_net;
        PyList_SetItem(obj_nets, i++, (PyObject*)l_obj_net);
    }
    return obj_nets;
}

PyObject *dap_chain_net_by_id_py(PyObject *self, PyObject *args){
    
    PyObject *obj_net_id;
    if (!PyArg_ParseTuple(args, "O", &obj_net_id))
        return NULL;
    
    dap_chain_net_t * net = dap_chain_net_by_id(((PyDapChainNetIdObject*)obj_net_id)->net_id);
    
    if (!net)
        return Py_BuildNone;

    PyDapChainNetObject *obj_net = PyObject_New(PyDapChainNetObject, &DapChainNetObjectType);
    obj_net->chain_net = net;

    return (PyObject*)obj_net;
}
PyObject *dap_chain_net_id_by_name_py(PyObject *self, PyObject *args){
    const char *name;
    if (!PyArg_ParseTuple(args, "s", &name))
        return NULL;
    PyObject *obj_net_id = _PyObject_New(&DapChainNetIdObjectType);
    ((PyDapChainNetIdObject*)obj_net_id)->net_id = dap_chain_net_id_by_name(name);
    return Py_BuildValue("O", obj_net_id);
}
PyObject *dap_chain_ledger_by_net_name_py(PyObject *self, PyObject *args){
    const char *net_name;
    if (!PyArg_ParseTuple(args, "s", &net_name))
        return NULL;
    PyObject *obj_ledger = _PyObject_New(&DapChainLedgerObjectType);
    ((PyDapChainLedgerObject*)obj_ledger)->ledger = dap_ledger_by_net_name(net_name);
    return Py_BuildValue("O", obj_ledger);
}

PyObject *dap_chain_net_get_chain_by_name_py(PyObject *self, PyObject *args){
    const char* chain_name;
    if (!PyArg_ParseTuple(args, "s", &chain_name)) {
        PyErr_SetString(PyExc_AttributeError, "Function takes exactly one argument, which must be a string.");
        return NULL;
    }
    PyDapChainObject *obj_chain = PyObject_New(PyDapChainObject, &DapChainObjectType);
    ((PyDapChainObject*)obj_chain)->chain_t = dap_chain_net_get_chain_by_name(((PyDapChainNetObject*)self)->chain_net, chain_name);
    if (!((PyDapChainObject*)obj_chain)->chain_t){
        Py_XDECREF(obj_chain);
        Py_RETURN_NONE;
    }
    return Py_BuildValue("O", obj_chain);
}

PyObject *dap_chain_net_python_get_id(PyObject *self, void *closure){
    (void)closure;
    PyDapChainNetIdObject *obj_net_id = PyObject_New(PyDapChainNetIdObject, &DapChainNetIdObjectType);
    obj_net_id->net_id = ((PyDapChainNetObject*)self)->chain_net->pub.id;
    return (PyObject*)obj_net_id;
}

PyObject *dap_chain_net_python_get_chains(PyObject *self, void *closure){
    (void)closure;
    dap_chain_t *l_chain = NULL;
    size_t l_count = 0, i = 0;
    DL_COUNT(((PyDapChainNetObject*)self)->chain_net->pub.chains, l_chain, l_count);
    PyObject *obj_list = PyList_New(l_count);
    l_chain = NULL;
    DL_FOREACH(((PyDapChainNetObject*)self)->chain_net->pub.chains, l_chain) {
        PyDapChainObject *obj_chain = PyObject_New(PyDapChainObject, &DapChainObjectType);
        obj_chain->chain_t = l_chain;
        PyList_SetItem(obj_list, i++, (PyObject*)obj_chain);
    }
    return obj_list;
}

PyObject *dap_chain_net_get_cur_addr_py(PyObject *self, PyObject *args){
    PyObject *obj_node_addr = _PyObject_New(&DapNodeAddrObjectType);
    ((PyDapNodeAddrObject*)obj_node_addr)->addr = g_node_addr;
    return Py_BuildValue("O", obj_node_addr);
}
PyObject *dap_chain_net_get_cur_cell_py(PyObject *self, PyObject *args){
    PyObject *obj_cell_id = _PyObject_New(&DapNodeAddrObjectType);
    ((PyDapChainCellIDObject*)obj_cell_id)->cell_id = *(dap_chain_net_get_cur_cell(((PyDapChainNetObject*)self)->chain_net));
    return Py_BuildValue("O", obj_cell_id);
}
PyObject *dap_chain_net_get_cur_addr_int_py(PyObject *self, PyObject *args){
    uint64_t res = dap_chain_net_get_cur_addr_int(((PyDapChainNetObject*)self)->chain_net);
    return PyLong_FromUnsignedLongLong(res);
}

PyObject *dap_chain_net_get_config_by_item(PyObject *self, PyObject *args){
    const char *section_path;
    const char *item_name;
    PyObject *obj_def = NULL;
    if (!PyArg_ParseTuple(args, "ss|O", &section_path, &item_name, &obj_def))
        return NULL;
    return python_get_config_item(((PyDapChainNetObject *)self)->chain_net->pub.config,
                                  section_path, item_name, obj_def);
}

PyObject *dap_chain_net_get_gdb_group_mempool_py(PyObject *self, PyObject *args){
    PyObject *obj_chain;
    if (!PyArg_ParseTuple(args, "O", &obj_chain))
        return NULL;
    char *res = dap_chain_mempool_group_new(((PyDapChainObject*)obj_chain)->chain_t);
    if (!res)
        Py_RETURN_NONE;
    PyObject *l_obj_res = Py_BuildValue("s", res);
    DAP_DELETE(res);
    return l_obj_res;
}
PyObject *dap_chain_net_get_gdb_group_mempool_by_chain_type_py(PyObject *self, PyObject *args){
    PyObject *obj_chain_type;
    if (!PyArg_ParseTuple(args, "O", &obj_chain_type))
        return NULL;
    char *res = dap_chain_net_get_gdb_group_mempool_by_chain_type(((PyDapChainNetObject*)self)->chain_net,
                                                                  ((PyChainTypeObject*)obj_chain_type)->chain_type);
    if (!res)
        Py_RETURN_NONE;
    PyObject *l_obj_res = Py_BuildValue("s", res);
    DAP_DELETE(res);
    return l_obj_res;
}
PyObject *dap_chain_net_links_connect_py(PyObject *self, PyObject *args){
//    dap_chain_net_links_connect(((PyDapChainNetObject*)self)->chain_net);
//    PyLong_FromLong(0);
    return NULL;
}
PyObject *dap_chain_net_get_chain_by_chain_type_py(PyObject *self, PyObject *args){
    PyObject *obj_chain_type;
    if(!PyArg_ParseTuple(args, "O", &obj_chain_type))
        return NULL;
    PyObject *obj_chain = _PyObject_New(&DapChainObjectType);
    ((PyDapChainObject*)obj_chain)->chain_t = dap_chain_net_get_chain_by_chain_type(
                ((PyDapChainNetObject*)self)->chain_net,
                ((PyChainTypeObject*)obj_chain_type)->chain_type);
    return Py_BuildValue("O", obj_chain);
}

PyObject *dap_chain_net_get_ledger_py(PyObject *self, PyObject *args){
    (void)args;
    PyDapChainLedgerObject *obj_ledger = PyObject_New(PyDapChainLedgerObject, &DapChainLedgerObjectType);
    obj_ledger->ledger = ((PyDapChainNetObject*)self)->chain_net->pub.ledger;
    return (PyObject*)obj_ledger;
}

PyObject *dap_chain_net_get_name_py(PyObject *self, PyObject *args){
    (void)args;
    PyObject *obj_name = PyUnicode_FromString(((PyDapChainNetObject*)self)->chain_net->pub.name);
    return obj_name;
}

PyObject *dap_chain_net_get_tx_by_hash_py(PyObject *self, PyObject *args){
    PyDapHashFastObject *obj_hash;
    if (!PyArg_ParseTuple(args, "O", &obj_hash)){
        return NULL;
    }
    if (!PyDapHashFast_Check(obj_hash)){
        return NULL;
    }
    PyDapChainDatumTxObject *l_tx = PyObject_New(PyDapChainDatumTxObject, &DapChainDatumTxObjectType);
    l_tx->datum_tx = dap_chain_net_get_tx_by_hash(
            ((PyDapChainNetObject*)self)->chain_net,
            obj_hash->hash_fast,
            TX_SEARCH_TYPE_NET);
    if (l_tx->datum_tx == NULL){
        Py_TYPE(l_tx)->tp_free((PyObject*)l_tx);
        Py_RETURN_NONE;
    }
    l_tx->original = false;
    return (PyObject*)l_tx;
}

typedef struct _wrapping_dap_chain_net_notify_callback{
    PyObject *arg;
    PyObject *func;
    dap_store_obj_t *store_obj;
}_wrapping_dap_chain_net_notify_callback_t;

bool dap_py_chain_net_gdb_notifier(void *a_arg) {
    if (!a_arg)
        return true;

    _wrapping_dap_chain_net_notify_callback_t *l_callback = (_wrapping_dap_chain_net_notify_callback_t *)a_arg;
    PyGILState_STATE state = PyGILState_Ensure();
    char l_op_code[2];
    l_op_code[0] = dap_store_obj_get_type(l_callback->store_obj);
    l_op_code[1] = '\0';
    PyObject *l_obj_value = NULL;
    if (!l_callback->store_obj->value || !l_callback->store_obj->value_len)
        l_obj_value = Py_None;
    else
        l_obj_value = PyBytes_FromStringAndSize((char *)l_callback->store_obj->value, (Py_ssize_t)l_callback->store_obj->value_len);
    PyObject *argv = Py_BuildValue("sssOO", l_op_code, l_callback->store_obj->group, l_callback->store_obj->key, l_obj_value, l_callback->arg);
    Py_XINCREF(l_callback->func);
    Py_XINCREF(l_callback->arg);
    PyObject_CallObject(l_callback->func, argv);
    
    if (argv)
        Py_DECREF(argv);

    Py_XDECREF(l_callback->func);
    Py_XDECREF(l_callback->arg);
    PyGILState_Release(state);
    dap_store_obj_free_one(l_callback->store_obj);
    return false;
}

void pvt_dap_chain_net_py_notify_handler(dap_global_db_instance_t UNUSED_ARG *a_dbi, dap_store_obj_t *a_obj, void *a_arg)
{
    if (!a_arg)
        return;

    _wrapping_dap_chain_net_notify_callback_t *l_obj = DAP_NEW(_wrapping_dap_chain_net_notify_callback_t);
    if (!l_obj)
        return;
        
    l_obj->store_obj = dap_store_obj_copy(a_obj, 1);
    l_obj->func = ((_wrapping_dap_chain_net_notify_callback_t*)a_arg)->func;
    l_obj->arg = ((_wrapping_dap_chain_net_notify_callback_t*)a_arg)->arg;
    dap_proc_thread_callback_add(NULL, dap_py_chain_net_gdb_notifier, l_obj);
}

PyObject *dap_chain_net_get_tx_fee_py(PyObject *self, void *closure){
    (void)closure;
    uint256_t l_fee = {0};
    dap_chain_addr_t l_addr = {0};
    if (dap_chain_net_tx_get_fee(((PyDapChainNetObject*)self)->chain_net->pub.id, &l_fee, &l_addr)) {
        DapMathObject *l_obj_fee = PyObject_New(DapMathObject, &DapMathObjectType);
        l_obj_fee->value = l_fee;
        return (PyObject*)l_obj_fee;
    } else {
        Py_RETURN_NONE;
    }
}

PyObject *dap_chain_net_get_tx_fee_addr_py(PyObject *self, void *closure){
    (void)closure;
    uint256_t l_fee = {0};
    dap_chain_addr_t *l_addr = DAP_NEW(dap_chain_addr_t);
    if (dap_chain_net_tx_get_fee(((PyDapChainNetObject*)self)->chain_net->pub.id, &l_fee, l_addr)) {
        PyDapChainAddrObject *obj_addr = PyObject_New(PyDapChainAddrObject, &DapChainAddrObjectType);
        
        obj_addr->addr = l_addr;
        return (PyObject*)obj_addr;
    } else {
        Py_RETURN_NONE;
    }
}

PyObject *dap_chain_net_get_validator_max_fee_py(PyObject *self, void *closure){
    (void)closure;
    uint256_t l_max = {0};
    dap_chain_net_srv_stake_get_fee_validators(((PyDapChainNetObject*)self)->chain_net, &l_max, NULL, NULL, NULL);
    DapMathObject *l_obj_value = PyObject_New(DapMathObject, &DapMathObjectType);
    l_obj_value->value = l_max;
    return (PyObject*)l_obj_value;
}
PyObject *dap_chain_net_get_validator_min_fee_py(PyObject *self, void *closure){
    (void)closure;
    uint256_t l_min = {0};
    dap_chain_net_srv_stake_get_fee_validators(((PyDapChainNetObject*)self)->chain_net, NULL, NULL, &l_min, NULL);
    DapMathObject *l_obj_value = PyObject_New(DapMathObject, &DapMathObjectType);
    l_obj_value->value = l_min;
    return (PyObject*)l_obj_value;
}
PyObject *dap_chain_net_get_validator_average_fee_py(PyObject *self, void *closure){
    (void)closure;
    uint256_t l_average = {0};
    dap_chain_net_srv_stake_get_fee_validators(((PyDapChainNetObject*)self)->chain_net, NULL, &l_average, NULL, NULL);
    DapMathObject *l_obj_value = PyObject_New(DapMathObject, &DapMathObjectType);
    l_obj_value->value = l_average;
    return (PyObject*)l_obj_value;
}

PyObject *dap_chain_net_convert_verify_code_to_str(PyObject *self, PyObject *args){
    (void)self;
    PyObject *obj_datum = NULL;
    unsigned int a_code = 0;
    if (!PyArg_ParseTuple(args, "OI", &obj_datum, &a_code)) {
        return NULL;
    }
    if (!PyDapChainDatum_Check(obj_datum)) {
        PyErr_SetString(PyExc_AttributeError, "The first argument was not passed correctly. The first "
                                              "argument must be an instance of a datum object.");
        return NULL;
    }
    return Py_BuildValue("s", dap_chain_net_verify_datum_err_code_to_str(
            ((PyDapChainDatumObject*)obj_datum)->datum, (int)a_code));
}
PyObject *dap_chain_net_get_native_ticker_py(PyObject *self, void *closure){
    (void)closure;
    return Py_BuildValue("s", ((PyDapChainNetObject*)self)->chain_net->pub.native_ticker);
}

PyObject *dap_chain_net_get_mempool_autoproc_py(PyObject *self, void *closure)
{
    (void)closure;
    bool autoproc =  ((PyDapChainNetObject*)self)->chain_net->pub.mempool_autoproc;    
    return Py_BuildValue("O", autoproc ? Py_True: Py_False);
}

PyObject *dap_chain_net_get_gdb_alias_py(PyObject *self, void *closure)
{
    return Py_BuildValue("s", ((PyDapChainNetObject*)self)->chain_net->pub.gdb_groups_prefix);
}
