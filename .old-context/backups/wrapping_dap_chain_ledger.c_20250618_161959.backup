#include "wrapping_dap_chain_ledger.h"
#include "python-cellframe_common.h"
#include "dap_proc_thread.h"
#include "dap_events.h"

#define LOG_TAG "ledger wrapper"

static PyObject *s_bridged_tx_notify_add(PyObject *self, PyObject *args);

static PyMethodDef DapChainLedgerMethods[] = {
        {"nodeDatumTxCalcHash", (PyCFunction)dap_chain_node_datum_tx_calc_hash_py, METH_VARARGS, ""},
        {"txAdd", (PyCFunction)dap_chain_ledger_tx_add_py, METH_VARARGS, ""},
        {"tokenAdd", (PyCFunction)dap_chain_ledger_token_add_py, METH_VARARGS, ""},
        {"tokenEmissionLoad", (PyCFunction)dap_chain_ledger_token_emission_load_py, METH_VARARGS, ""},
        {"tokenEmissionFind", (PyCFunction)dap_chain_ledger_token_emission_find_py, METH_VARARGS, ""},
        {"tokenAuthSignsTotal", (PyCFunction)dap_chain_ledger_token_auth_signs_total_py, METH_VARARGS, ""},
        {"tokenAuthSignsValid", (PyCFunction)dap_chain_ledger_token_auth_signs_valid_py, METH_VARARGS, ""},
        {"tokenAuthPkeysHashes", (PyCFunction)dap_chain_ledger_token_auth_pkeys_hashes_py, METH_VARARGS, ""},
        {"txGetMainTickerAndLedgerRc", (PyCFunction)dap_chain_ledger_tx_get_main_ticker_py, METH_VARARGS, ""},
        {"txGetTokenTickerByHash", (PyCFunction)dap_chain_ledger_tx_get_token_ticker_by_hash_py, METH_VARARGS, ""},
        {"addrGetTokenTickerAll", (PyCFunction)dap_chain_ledger_addr_get_token_ticker_all_py, METH_VARARGS, ""},
        //{"txAddCheck", (PyCFunction)dap_chain_ledger_tx_add_check_py, METH_VARARGS, ""},
        {"datumTxCacheCheck", (PyCFunction)dap_chain_node_datum_tx_cache_check_py, METH_VARARGS, ""},
        {"purge", (PyCFunction)dap_chain_ledger_purge_py, METH_VARARGS, ""},
        {"count", (PyCFunction)dap_chain_ledger_count_py, METH_VARARGS, ""},
        {"countFromTo", (PyCFunction)dap_chain_ledger_count_from_to_py, METH_VARARGS, ""},
        {"txHashIsUsedOutItem", (PyCFunction)dap_chain_ledger_tx_hash_is_used_out_item_py, METH_VARARGS, ""},
        {"calcBalance", (PyCFunction)dap_chain_ledger_calc_balance_py, METH_VARARGS, ""},
        {"calcBalanceFull", (PyCFunction)dap_chain_ledger_calc_balance_full_py, METH_VARARGS, ""},
        {"txFindByHash", (PyCFunction)dap_chain_ledger_tx_find_by_hash_py, METH_VARARGS, ""},
        {"txFindByAddr", (PyCFunction)dap_chain_ledger_tx_find_by_addr_py, METH_VARARGS, ""},
        {"getTransactions", (PyCFunction) dap_chain_ledger_get_txs_py, METH_VARARGS, ""},
        {"txAddNotify", (PyCFunction)dap_chain_ledger_tx_add_notify_py, METH_VARARGS, ""},
        {"bridgedTxNotifyAdd", (PyCFunction)s_bridged_tx_notify_add, METH_VARARGS, ""},
        {"txHashIsUsedOutItemHash", (PyCFunction)dap_chain_ledger_tx_hash_is_used_out_item_hash_py, METH_VARARGS, ""},
        {}
};

PyTypeObject DapChainLedgerObjectType = DAP_PY_TYPE_OBJECT(
        "CellFrame.ChainLedger", sizeof(PyDapChainLedgerObject),
        "Chain ledger objects",
        .tp_methods = DapChainLedgerMethods);

PyObject *DapChainLedgerObject_create(PyTypeObject *type_object, PyObject *args, PyObject *kwds){
    uint16_t check_flag;
    char *net_name;
    if (!PyArg_ParseTuple(args, "H|s", &check_flag, &net_name))
        return NULL;
    PyDapChainLedgerObject *obj = (PyDapChainLedgerObject *)PyType_GenericNew(type_object, args, kwds);
    // TODO add relevant arguments for ledger create
    //obj->ledger = dap_chain_ledger_create(check_flag, net_name);
    return (PyObject *)obj;
}
void DapChainLedgerObject_free(PyDapChainLedgerObject* object){
    dap_ledger_handle_free(object->ledger);
    Py_TYPE(object)->tp_free(object);
}

PyObject *dap_chain_node_datum_tx_calc_hash_py(PyObject *self, PyObject *args){
    (void)self;
    PyObject *obj_tx;
    if (!PyArg_ParseTuple(args, "O", &obj_tx))
        return NULL;
    PyDapHashFastObject *obj_hash_fast = PyObject_New(PyDapHashFastObject, &DapChainHashFastObjectType);
    dap_hash_fast_t l_hash = dap_chain_node_datum_tx_calc_hash(((PyDapChainDatumTxObject*)obj_tx)->datum_tx);
    obj_hash_fast->hash_fast = DAP_DUP(&l_hash);
    obj_hash_fast->origin = true;
    return (PyObject*)obj_hash_fast;

}
PyObject *dap_chain_ledger_tx_add_py(PyObject *self, PyObject *args){
    PyDapChainDatumTxObject *obj_datum_tx;
    if (!PyArg_ParseTuple(args, "O", &obj_datum_tx))
        return NULL;
    dap_hash_fast_t l_tx_hash;
    dap_hash_fast(obj_datum_tx->datum_tx, dap_chain_datum_tx_get_size(obj_datum_tx->datum_tx), &l_tx_hash);
    int res = dap_ledger_tx_add(((PyDapChainLedgerObject*)self)->ledger, obj_datum_tx->datum_tx, &l_tx_hash, false, NULL);
    return PyLong_FromLong(res);
}
PyObject *dap_chain_ledger_token_add_py(PyObject *self, PyObject *args)
{
    PyObject *token;
    size_t token_size;
    if (!PyArg_ParseTuple(args, "O|n", &token, &token_size))
        return NULL;
    int res = dap_ledger_token_add(((PyDapChainLedgerObject*)self)->ledger,
                                         (byte_t *)((PyDapChainDatumTokenObject*)token)->token, token_size);
    return PyLong_FromLong(res);
}
PyObject *dap_chain_ledger_token_emission_load_py(PyObject *self, PyObject *args){
    PyDapChainDatumTokenEmissionObject *token_emission;
    size_t token_emissiom_size;
    if (!PyArg_ParseTuple(args, "O|n", &token_emission, &token_emissiom_size))
        return NULL;
    dap_hash_fast_t l_emission_hash;
    dap_hash_fast(token_emission->token_emission, token_emissiom_size, &l_emission_hash);
    int res = dap_ledger_token_emission_load(((PyDapChainLedgerObject*)self)->ledger,
                                                   (byte_t *)token_emission->token_emission,
                                                   token_emissiom_size,
                                                   &l_emission_hash);
    return PyLong_FromLong(res);
}

PyObject *dap_chain_ledger_token_emission_find_py(PyObject *self, PyObject *args){
    PyObject *h_fast;

    if (!PyArg_ParseTuple(args, "O", &h_fast))
        return NULL;
    
    PyDapChainDatumTokenEmissionObject *token_emission = PyObject_New(PyDapChainDatumTokenEmissionObject,
                                                                      &DapChainDatumTokenEmissionObjectType);

    token_emission->token_emission = dap_ledger_token_emission_find(
                ((PyDapChainLedgerObject*)self)->ledger, ((PyDapHashFastObject*)h_fast)->hash_fast);
    if (token_emission->token_emission)
    {
        token_emission->token_size = dap_chain_datum_emission_get_size((uint8_t*) token_emission->token_emission);
        token_emission->copy = false;
    
        return (PyObject *)token_emission;
    }
    else
        Py_RETURN_NONE;
}

PyObject *dap_chain_ledger_token_auth_signs_total_py(PyObject *self, PyObject *args) {
    const char *token_ticker;
    if (!PyArg_ParseTuple(args, "s", &token_ticker)) {
        PyErr_SetString(PyExc_AttributeError, "This function, as the first argument, must take the"
                                              " token ticker string");
        return NULL;
    }
    size_t res = dap_ledger_token_get_auth_signs_total(((PyDapChainLedgerObject*)self)->ledger, token_ticker);
    if (res == 0)
        Py_RETURN_NONE;
    return Py_BuildValue("i", res);
}

PyObject *dap_chain_ledger_token_auth_signs_valid_py(PyObject *self, PyObject *args) {
    const char *token_ticker;
    if (!PyArg_ParseTuple(args, "s", &token_ticker)) {
        PyErr_SetString(PyExc_AttributeError, "This function, as the first argument, must take the"
                                              " token ticker string");
        return NULL;
    }
    size_t res = dap_ledger_token_get_auth_signs_valid(((PyDapChainLedgerObject*)self)->ledger, token_ticker);
    if (res == 0)
        Py_RETURN_NONE;

    return Py_BuildValue("i", res);
}

PyObject *dap_chain_ledger_token_auth_pkeys_hashes_py(PyObject *self, PyObject *args)
{
    const char *token_ticker;
    if (!PyArg_ParseTuple(args, "s", &token_ticker)) {
        PyErr_SetString(PyExc_AttributeError, "This function, as the first argument, must take the"
                                              " token ticker string");
        return NULL;
    }
    dap_list_t * l_hashes = dap_ledger_token_get_auth_pkeys_hashes(((PyDapChainLedgerObject*)self)->ledger, token_ticker);
    PyObject *obj_list = PyList_New(dap_list_length(l_hashes));
    size_t i = 0;
    for (dap_list_t *l_iter = l_hashes; l_iter != NULL; l_iter = l_iter->next, ++i){
        PyDapHashFastObject *obj_hash = PyObject_New(PyDapHashFastObject, &DapChainHashFastObjectType);
        obj_hash->hash_fast = (dap_chain_hash_fast_t *)l_iter->data;
        obj_hash->origin = false;
        PyList_SetItem(obj_list, i, (PyObject*)obj_hash);
    }

    dap_list_free(l_hashes);
    return obj_list;
}


PyObject *dap_chain_ledger_tx_get_token_ticker_by_hash_py(PyObject *self, PyObject *args){
    PyObject *obj_hash;
    if (!PyArg_ParseTuple(args, "O", &obj_hash)){
        PyErr_SetString(PyExc_AttributeError, "Function takes exactly one argument which must be HashFast object");
        return NULL;
    }
    const char *l_ticker = dap_ledger_tx_get_token_ticker_by_hash(
            ((PyDapChainLedgerObject*)self)->ledger,
            ((PyDapHashFastObject*)obj_hash)->hash_fast);
    return Py_BuildValue("s", l_ticker);
}
PyObject *dap_chain_ledger_addr_get_token_ticker_all_py(PyObject *self, PyObject *args){
    PyObject *obj_addr = NULL;
    if (!PyArg_ParseTuple(args, "|O", &obj_addr))
        return NULL;
    dap_chain_addr_t *l_addr = NULL;
    if (obj_addr) {
        if (!PyDapChainAddrObject_Check((PyDapChainAddrObject*)obj_addr)) {
            PyErr_SetString(PyExc_AttributeError, "An invalid argument was passed, the first argument "
                                                  "is optional and must be an object of type ChainAddr.");
            return NULL;
        }
        l_addr = PY_DAP_CHAIN_ADDR(obj_addr);
    }
    char **l_tickers = NULL;
    size_t l_ticker_count = 0;
    dap_ledger_addr_get_token_ticker_all(((PyDapChainLedgerObject*)self)->ledger, l_addr, &l_tickers, &l_ticker_count);
    PyObject *l_obj_tickers = PyList_New((Py_ssize_t)l_ticker_count);
    for (size_t i = 0; i < l_ticker_count; i++) {
        PyObject *obj_unicode = PyUnicode_FromString(l_tickers[i]);
        DAP_DELETE(l_tickers[i]);
        PyList_SetItem(l_obj_tickers, (Py_ssize_t)i, obj_unicode);
    }
    DAP_DELETE(l_tickers);
    return l_obj_tickers;
}

// TODO implement tx_add_check wrapping

PyObject *dap_chain_node_datum_tx_cache_check_py(PyObject *self, PyObject *args){
    //TODO
    //Missing implementation of dap_chain_node_datum_tx_cache_check function in dap_chain_ledger
    return NULL;
//    PyObject *obj_datum_tx;
//    PyObject *list_bound_items;
//    if (!PyArg_ParseTuple(args, "O|O", &obj_datum_tx, &list_bound_items))
//        return NULL;
//    Py_ssize_t size = PyList_Size(list_bound_items);
//    dap_list_t **bound_items = calloc(sizeof (dap_list_t**), (size_t)size);
//    for (int i = 0; i < size ; i++){
//        PyObject *obj = PyList_GetItem(list_bound_items, i);
//        dap_list_t *l = pyListToDapList(obj);
//        bound_items[i] = l;
//    }
//    int res = dap_chain_node_datum_tx_cache_check(((PyDapChainDatumTxObject*)obj_datum_tx)->datum_tx, bound_items);
//    return PyLong_FromLong(res);
}

PyObject *dap_chain_ledger_purge_py(PyObject *self, PyObject *args){
    dap_ledger_purge(((PyDapChainLedgerObject*)self)->ledger, false);
    return PyLong_FromLong(0);
}
PyObject *dap_chain_ledger_count_py(PyObject *self, PyObject *args){
    long long  res = (long long)dap_ledger_count(((PyDapChainLedgerObject*)self)->ledger);
    return PyLong_FromLongLong(res);
}
PyObject *dap_chain_ledger_count_from_to_py(PyObject *self, PyObject *args){
    long ts_from = 0, ts_to = 0;
    if (!PyArg_ParseTuple(args, "|ll", &ts_from, &ts_to))
        return NULL;
    uint64_t res = 0;
    if (ts_from && ts_to){
        res = dap_ledger_count_from_to(((PyDapChainLedgerObject*)self)->ledger, (time_t)ts_from, (time_t)ts_to);
    }else if(ts_from){
        res = dap_ledger_count_from_to(((PyDapChainLedgerObject*)self)->ledger, (time_t)ts_from, 0);
    }else if (ts_to){
        res = dap_ledger_count_from_to(((PyDapChainLedgerObject*)self)->ledger, 0, ts_to);
    } else {
        res = dap_ledger_count_from_to(((PyDapChainLedgerObject*)self)->ledger, 0, 0);
    }
    return PyLong_FromUnsignedLongLong(res);
}
PyObject *dap_chain_ledger_tx_hash_is_used_out_item_py(PyObject *self, PyObject *args){
    PyObject *obj_h_fast;
    int idx_out;
    if (!PyArg_ParseTuple(args, "O|i", &obj_h_fast, &idx_out))
            return NULL;
    bool res = dap_ledger_tx_hash_is_used_out_item(((PyDapChainLedgerObject*)self)->ledger, ((PyDapHashFastObject*)obj_h_fast)->hash_fast, idx_out, NULL);
    if (res)
        Py_RETURN_TRUE;
    else
        Py_RETURN_FALSE;
}
PyObject *dap_chain_ledger_calc_balance_py(PyObject *self, PyObject *args){
    PyObject *addr;
    const char *token_ticker;
    if (!PyArg_ParseTuple(args, "Os", &addr, &token_ticker))
        return NULL;
    uint256_t balance = dap_ledger_calc_balance(
            ((PyDapChainLedgerObject*)self)->ledger,
            PY_DAP_CHAIN_ADDR(addr),
            token_ticker
    );
    DapMathObject *l_obj_balance = PyObject_New(DapMathObject, &DapMathObjectType);
    l_obj_balance->value = balance;
    return (PyObject*)l_obj_balance;
}
PyObject *dap_chain_ledger_calc_balance_full_py(PyObject *self, PyObject *args){
    PyObject *addr;
    const char *token_ticker;
    if (!PyArg_ParseTuple(args, "Os", &addr, &token_ticker))
        return NULL;
    DapMathObject *l_obj_balance = PyObject_New(DapMathObject, &DapMathObjectType);
    l_obj_balance->value = dap_ledger_calc_balance_full(
        ((PyDapChainLedgerObject*)self)->ledger,
        PY_DAP_CHAIN_ADDR(addr), token_ticker);
    return (PyObject*)l_obj_balance;
}
PyObject *dap_chain_ledger_tx_find_by_hash_py(PyObject *self, PyObject *args){
    PyObject *h_fast;
    if (!PyArg_ParseTuple(args, "O", &h_fast))
        return NULL;
    PyDapChainDatumTxObject *res = PyObject_NEW(PyDapChainDatumTxObject, &DapChainDatumTxObjectType);
    res->datum_tx = dap_ledger_tx_find_by_hash(((PyDapChainLedgerObject*)self)->ledger, ((PyDapHashFastObject*)h_fast)->hash_fast);
    
    res->original = false;
    if (res->datum_tx == NULL) {
        PyObject_DEL(res);
        Py_RETURN_NONE;
    }
    return Py_BuildValue("O", res);
}
PyObject *dap_chain_ledger_tx_find_by_addr_py(PyObject *self, PyObject *args){
    const char *token;
    PyObject *addr;
    PyObject *first_hash;
    if (!PyArg_ParseTuple(args, "s|O|O", &token, &addr, &first_hash))
        return NULL;
    PyDapChainDatumTxObject *res = PyObject_New(PyDapChainDatumTxObject, &DapChainDatumTxObjectType);
    res->datum_tx = dap_ledger_tx_find_by_addr(((PyDapChainLedgerObject*)self)->ledger, token, PY_DAP_CHAIN_ADDR(addr), ((PyDapHashFastObject*)first_hash)->hash_fast, false);
    res->original = false;
    
    return (PyObject*)res;
}

static char*** ListStringToArrayStringFormatChar(PyObject *list){
    Py_ssize_t size = PyList_Size(list);
    char ***data = calloc(sizeof(char**), (size_t)size);
    if(!data) {
        log_it(L_CRITICAL, "Memory allocation error");
        return NULL;
    }
    for (Py_ssize_t i = 0; i < size; i++){
        PyObject *obj_two = PyList_GetItem(list,i);
        Py_ssize_t size_seentenses = PyList_Size(obj_two);
        char **sentences = calloc(sizeof(char**), (size_t)size_seentenses);
        if(!sentences) {
        log_it(L_CRITICAL, "Memory allocation error");
            DAP_DELETE(data);
            return NULL;
        }
        for (int j=0; j < size_seentenses;j++){
            PyObject *obj_byte = PyList_GetItem(obj_two, j);
            char *word = PyBytes_AsString(obj_byte);
            sentences[j] = word;
        }
        data[i] = sentences;
    }
    return data;
}

static size_t *ListIntToSizeT(PyObject *list){
    Py_ssize_t size = PyList_Size(list);
    size_t *res_size_t = calloc(sizeof(size_t), (size_t)size);
    if(!res_size_t) {
        log_it(L_CRITICAL, "Memory allocation error");
        return NULL;
    }
    for (Py_ssize_t i=0; i<size;i++){
        PyObject *obj = PyList_GetItem(list, i);
        res_size_t[i] = (size_t)PyLong_AsSsize_t(obj);
    }
    return res_size_t;
}

PyObject *dap_chain_ledger_get_txs_py(PyObject *self, PyObject *args){
    size_t count, page;
    PyObject *obj_reverse, *obj_unspent;
    if (!PyArg_ParseTuple(args, "nnOO",&count, &page, &obj_reverse, &obj_unspent)){
        return NULL;
    }
    if (!PyBool_Check(obj_reverse)){
        PyErr_SetString(PyExc_AttributeError, "");
        return NULL;
    }
    bool    reverse = obj_reverse == Py_True ? true : false,
            unspent = obj_unspent == Py_True ? true : false;
    dap_list_t *l_txs = dap_ledger_get_txs(
            ((PyDapChainLedgerObject*)self)->ledger,
            count,
            page,
            reverse, unspent);
    if (!l_txs){
        Py_RETURN_NONE;
    }
    PyObject *obj_list = PyList_New(dap_list_length(l_txs));
    size_t i = 0;
    for (dap_list_t *l_iter = l_txs; l_iter != NULL; l_iter = l_iter->next, ++i) {
        PyDapChainDatumTxObject *obj_tx = PyObject_New(PyDapChainDatumTxObject, &DapChainDatumTxObjectType);
        obj_tx->datum_tx = l_iter->data;
        obj_tx->original = false;
        PyList_SetItem(obj_list, i, (PyObject*)obj_tx);
    }
    dap_list_free(l_txs);
    return obj_list;
}

typedef struct pvt_ledger_notify{
    PyObject *func;
    PyObject *argv;
}pvt_ledger_notify_t;

static void pvt_wrapping_dap_chain_ledger_tx_add_notify(void *a_arg, dap_ledger_t *a_ledger,
                                                        dap_chain_datum_tx_t *a_tx, dap_ledger_notify_opcodes_t a_opcode){
    if (!a_arg)
        return;
    if (a_opcode == DAP_LEDGER_NOTIFY_OPCODE_ADDED){
        pvt_ledger_notify_t *notifier = (pvt_ledger_notify_t*)a_arg;
        PyGILState_STATE state = PyGILState_Ensure();
        PyDapChainLedgerObject *obj_ledger = PyObject_NEW(PyDapChainLedgerObject, &DapChainLedgerObjectType);
        PyDapChainDatumTxObject *obj_tx = PyObject_NEW(PyDapChainDatumTxObject, &DapChainDatumTxObjectType);
        obj_ledger->ledger = a_ledger;
        obj_tx->datum_tx = a_tx;
        PyObject *notify_arg = !notifier->argv ? Py_None : notifier->argv;
        PyObject *argv = Py_BuildValue("OOO", (PyObject*)obj_ledger, (PyObject*)obj_tx, notify_arg);
        log_it(L_DEBUG, "Call tx added ledger notifier for net %s", a_ledger->net->pub.name);
        PyObject* result = PyObject_CallObject(notifier->func, argv);
        if (!result){
            python_error_in_log_it(LOG_TAG);
        }
        Py_XDECREF(result);
        Py_XDECREF(argv);
        PyGILState_Release(state);
    } else {

    }
}

PyObject *dap_chain_ledger_tx_add_notify_py(PyObject *self, PyObject *args) {
    PyObject *obj_func, *obj_argv = NULL;
    if (!PyArg_ParseTuple(args, "O|O", &obj_func, &obj_argv)) {
        return NULL;
    }
    if (!PyCallable_Check(obj_func)) {
        PyErr_SetString(PyExc_AttributeError, "This function, as the first argument, must take the"
                                              " function called by the callback.");
        return NULL;
    }
    pvt_ledger_notify_t *notifier = DAP_NEW(pvt_ledger_notify_t);
    if(!notifier) {
        log_it(L_CRITICAL, "Memory allocation error");
        return NULL;
    }
    notifier->func = obj_func;
    notifier->argv = obj_argv;
    Py_INCREF(obj_func);
    Py_XINCREF(obj_argv);
    dap_ledger_tx_add_notify(((PyDapChainLedgerObject*)self)->ledger, pvt_wrapping_dap_chain_ledger_tx_add_notify, notifier);
    Py_RETURN_NONE;
}

struct py_notifier_callback_args {
    dap_ledger_t *ledger;
    dap_chain_datum_tx_t *tx;
    dap_hash_fast_t tx_hash;
    void *arg;
};

static bool s_python_obj_notifier(void *a_arg)
{
    struct py_notifier_callback_args *l_args = a_arg;
    pvt_ledger_notify_t *l_notifier = l_args->arg;
    PyDapChainLedgerObject *obj_ledger = PyObject_NEW(PyDapChainLedgerObject, &DapChainLedgerObjectType);
    obj_ledger->ledger = l_args->ledger;
    PyDapChainDatumTxObject *obj_tx = PyObject_NEW(PyDapChainDatumTxObject, &DapChainDatumTxObjectType);
    obj_tx->datum_tx = l_args->tx;
    obj_tx->original = false;
    PyObject *l_notify_arg = !l_notifier->argv ? Py_None : l_notifier->argv;
    Py_INCREF(l_notify_arg);
    log_it(L_DEBUG, "Call bridged tx ledger notifier for net %s", l_args->ledger->net->pub.name);
    PyGILState_STATE state = PyGILState_Ensure();
    PyObject *obj_argv = Py_BuildValue("OOO", obj_ledger, obj_tx, l_notify_arg);
    Py_INCREF(l_notifier->func);
    PyObject *result = PyEval_CallObject(l_notifier->func, obj_argv);
    Py_XDECREF(l_notifier->func);
    Py_DECREF(obj_argv);
    Py_DECREF(obj_ledger);
    Py_DECREF(obj_tx);
    Py_DECREF(l_notify_arg);
    if (!result)
        python_error_in_log_it(LOG_TAG);
    Py_XDECREF(result);
    DAP_DELETE(l_args->tx);
    DAP_DELETE(l_args);
    PyGILState_Release(state);
    return false;
}

static void s_python_proc_notifier(dap_ledger_t *a_ledger, dap_chain_datum_tx_t *a_tx, dap_hash_fast_t *a_tx_hash, void *a_arg, dap_ledger_notify_opcodes_t a_opcode)
{
    if (!a_arg)
        return;
    
    struct py_notifier_callback_args *l_args = DAP_NEW_Z(struct py_notifier_callback_args);
    l_args->ledger = a_ledger;
    l_args->tx = DAP_DUP_SIZE(a_tx, dap_chain_datum_tx_get_size(a_tx));
    l_args->tx_hash = *a_tx_hash;
    l_args->arg = a_arg;
    dap_proc_thread_callback_add(NULL, s_python_obj_notifier, l_args);
}

static PyObject *s_bridged_tx_notify_add(PyObject *self, PyObject *args)
{
    PyObject *obj_func, *obj_argv = NULL;
    if (!PyArg_ParseTuple(args, "O|O", &obj_func, &obj_argv)) {
        return NULL;
    }
    if (!PyCallable_Check(obj_func)) {
        PyErr_SetString(PyExc_AttributeError, "This function, as the first argument, must take the"
                                              " function called by the callback.");
        return NULL;
    }
    pvt_ledger_notify_t *l_notifier = DAP_NEW(pvt_ledger_notify_t);
    if (!l_notifier) {
        log_it(L_CRITICAL, "Memory allocation error");
        return NULL;
    }
    l_notifier->func = obj_func;
    l_notifier->argv = obj_argv;
    Py_INCREF(obj_func);
    Py_XINCREF(obj_argv);
    dap_ledger_bridged_tx_notify_add(((PyDapChainLedgerObject*)self)->ledger, s_python_proc_notifier, l_notifier);
    Py_RETURN_NONE;
}

PyObject *dap_chain_ledger_tx_get_main_ticker_py(PyObject *self, PyObject *args)
{
    PyObject *l_obj_tx = NULL;
    if (!PyArg_ParseTuple(args, "O", &l_obj_tx)) {
         PyErr_SetString(PyExc_AttributeError, "This function, as the first argument, accepts DatumTx.");
        return NULL;
    }
    
    PyDapChainDatumTxObject *obj_tx = (PyDapChainDatumTxObject *)l_obj_tx;

    int l_ledger_rc = DAP_LEDGER_CHECK_INVALID_ARGS;
    const char * ticker = dap_ledger_tx_calculate_main_ticker(((PyDapChainLedgerObject*)self)->ledger, obj_tx->datum_tx, &l_ledger_rc);
    return Py_BuildValue("(s,i)", ticker ? ticker : "UNKWNOWN", l_ledger_rc);
}

PyObject *dap_chain_ledger_tx_hash_is_used_out_item_hash_py(PyObject *self, PyObject *args){
    PyObject *tx_hash;
    uint64_t idx;
    if (!PyArg_ParseTuple(args, "OK", &tx_hash, &idx)) {
        return NULL;
    }
    dap_hash_fast_t l_spender_hash = {0};
    if (dap_ledger_tx_hash_is_used_out_item(((PyDapChainLedgerObject*)self)->ledger, ((PyDapHashFastObject*)tx_hash)->hash_fast, idx, &l_spender_hash)){
        PyDapHashFastObject *obj_hf = PyObject_New(PyDapHashFastObject, &DapChainHashFastObjectType);
        obj_hf->hash_fast = DAP_NEW(dap_hash_fast_t);
        memcpy(obj_hf->hash_fast, &l_spender_hash, sizeof(dap_hash_fast_t));
        obj_hf->origin = true;
        return (PyObject*)obj_hf;
    }
    Py_RETURN_NONE;
}
