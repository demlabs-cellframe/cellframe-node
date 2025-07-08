#include "libdap-chain-python.h"
#include "python-cellframe_common.h"
#include "libdap_chain_net_python.h"

#define LOG_TAG "libdap-chain-python"
#include "dap_chain_cs_blocks.h"

int init_chain_py(){
    return  dap_chain_init();
}

void deinit_chain_py(){
    dap_chain_deinit();
}

static PyMethodDef DapChainMethods[] = {
        {"findById", (PyCFunction)dap_chain_find_by_id_py, METH_VARARGS|METH_STATIC, ""},
        {"loadFromCfg", (PyCFunction)dap_chain_load_from_cfg_py, METH_VARARGS|METH_STATIC, ""},
        {"hasFileStore", (PyCFunction)dap_chain_has_file_store_py, METH_NOARGS, ""},
        //{"saveAll", (PyCFunction) dap_chain_save_all_py, METH_NOARGS, ""},
        {"loadAll", (PyCFunction)dap_chain_load_all_py, METH_NOARGS, ""},
        {"createAtomIter", (PyCFunction) dap_chain_python_create_atom_iter, METH_VARARGS, ""},
        {"atomIterGetFirst", (PyCFunction) dap_chain_python_atom_iter_get_first, METH_VARARGS, ""},
        {"atomGetDatums", (PyCFunction) dap_chain_python_atom_get_datums, METH_VARARGS, ""},
        {"atomIterGetNext", (PyCFunction)dap_chain_python_atom_iter_get_next, METH_VARARGS, ""},
        {"getDag", (PyCFunction)dap_chain_python_atom_iter_get_dag, METH_NOARGS, ""},
        {"addMempoolNotify", (PyCFunction)dap_chain_python_add_mempool_notify_callback, METH_VARARGS, ""},
        {"addAtomNotify", (PyCFunction)dap_chain_net_add_atom_notify_callback, METH_VARARGS,"" },
        {"atomFindByHash", (PyCFunction)dap_chain_python_atom_find_by_hash, METH_VARARGS, ""},
        {"countAtom", (PyCFunction)dap_chain_python_get_atom_count, METH_NOARGS, ""},
        {"getAtoms", (PyCFunction)dap_chain_python_get_atoms, METH_VARARGS, ""},
        {"countTx", (PyCFunction)dap_chain_python_get_count_tx, METH_NOARGS, ""},
        {"getTransactions", (PyCFunction)dap_chain_python_get_txs, METH_VARARGS, ""},
        {"getCSName", (PyCFunction)dap_chain_python_get_cs_name, METH_NOARGS, ""},
        {"getNet", (PyCFunction) dap_chain_python_get_net, METH_NOARGS, ""},
        {"configGetItem", (PyCFunction)dap_chain_python_get_config_item, METH_VARARGS, ""},
        {"addAtomConfirmedNotify", (PyCFunction)dap_chain_atom_confirmed_notify_add_py, METH_VARARGS, "Add a callback for confirmed atoms"},
        {"addForkResolvedNotify", (PyCFunction)dap_chain_fork_resolved_notify_add_py, METH_VARARGS|METH_STATIC, "Add a callback for fork resolution (local)"},
        
        {}
};

PyTypeObject DapChainObjectType = {
        .ob_base = PyVarObject_HEAD_INIT(NULL,0)
        .tp_name = "CellFrame.Chain",
        .tp_basicsize = sizeof(PyDapChainObject),
        .tp_str = PyDapChain_str,
        .tp_dealloc = (destructor)PyDapChainObject_dealloc,
        .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
        .tp_methods = DapChainMethods,
        .tp_new = PyDapChainObject_new
};

PyObject *dap_chain_find_by_id_py(PyObject *self, PyObject *args){
    PyObject *obj_net_id;
    PyObject *obj_chain_id;
    if (!PyArg_ParseTuple(args, "O|O", &obj_net_id, &obj_chain_id))
        return NULL;
    PyObject *new_obj = _PyObject_New(&DapChainObjectType);
    ((PyDapChainObject*)new_obj)->chain_t = dap_chain_find_by_id(((PyDapChainNetIdObject*)obj_net_id)->net_id,
                                                                 *(((PyDapChainIDObject*)obj_chain_id)->chain_id));
    return Py_BuildValue("O", &new_obj);
}

PyObject *dap_chain_has_file_store_py(PyObject *self, PyObject *args){
    bool res = dap_chain_has_file_store(((PyDapChainObject*)self)->chain_t);
    if (res)
        Py_RETURN_TRUE;
    else
        Py_RETURN_FALSE;
}

PyObject *dap_chain_load_all_py(PyObject *self, PyObject *args){
    return  PyLong_FromLong(dap_chain_load_all(((PyDapChainObject*)self)->chain_t));
}

PyObject *dap_chain_load_from_cfg_py(PyObject *self, PyObject *args){
    const char *chain_net_name;
    PyObject *obj_net_id;
    const char *cfg_name;
    if (!PyArg_ParseTuple(args, "s|O|s", &chain_net_name, &obj_net_id, &cfg_name))
        return NULL;
    PyObject *res_obj = _PyObject_New(&DapChainObjectType);
    dap_config_t *l_chain_config = dap_config_open(cfg_name);
    ((PyDapChainObject*)res_obj)->chain_t = dap_chain_load_from_cfg(chain_net_name, ((PyDapChainNetIdObject*)obj_net_id)->net_id, l_chain_config);
    return Py_BuildValue("O", &res_obj);
}

PyObject *PyDapChainObject_new(PyTypeObject *type_object, PyObject *args, PyObject *kwds){
    PyDapChainObject *obj = (PyDapChainObject*)PyType_GenericNew(type_object, args, kwds);
    return (PyObject *)obj;
}

void PyDapChainObject_dealloc(PyDapChainObject* chain){
    Py_TYPE(chain)->tp_free((PyObject*)chain);
}

PyObject *dap_chain_python_create_atom_iter(PyObject *self, PyObject *args){
//    PyObject *obj_cell_id;
    PyObject *obj_boolean;
    if (!PyArg_ParseTuple(args, "O", &obj_boolean)){
        PyErr_SetString(PyExc_AttributeError, "This function takes two arguments. ");
        return NULL;
    }
//    if (!PyDapChainCell_Check(obj_cell_id)){
//        PyErr_SetString(PyExc_AttributeError, "The first argument to this function must be of type ChainCell.");
//        return NULL;
//    }
    if (!PyBool_Check(obj_boolean)){
        PyErr_SetString(PyExc_AttributeError, "The second argument accepted by this function is not a boolean value. ");
        return NULL;
    }
    bool with_treshold = (obj_boolean == Py_True) ? 1 : 0;
    PyObject *obj_atom_iter = _PyObject_New(&DapChainAtomIterObjectType);
    PyObject_Init(obj_atom_iter, &DapChainAtomIterObjectType);
//    ((PyDapChainObject*)self)->chain_t->callback_atom_iter_create()
    ((PyChainAtomIterObject*)obj_atom_iter)->atom_iter =
            ((PyDapChainObject*)self)->chain_t->callback_atom_iter_create(
                    ((PyDapChainObject*)self)->chain_t,
                    ((PyDapChainObject*)self)->chain_t->cells->id, NULL);
    return obj_atom_iter;
}

PyObject *dap_chain_python_atom_iter_get_first(PyObject *self, PyObject *args){
    PyObject *obj_iter;
    if (!PyArg_ParseTuple(args, "O", &obj_iter)){
        PyErr_SetString(PyExc_AttributeError, "Function takes exactly one argument");
        return NULL;
    }
    if (!PyDapChainAtomIter_Check(obj_iter)){
        PyErr_SetString(PyExc_ValueError, "Argument must be ChainAtomIter object");
        return NULL;
    }
    PyObject *obj_atom_ptr = _PyObject_New(&DapChainAtomPtrObjectType);
    obj_atom_ptr = PyObject_Init(obj_atom_ptr, &DapChainAtomPtrObjectType);
    size_t l_atom_size = 0;
    ((PyChainAtomObject*)obj_atom_ptr)->atom = ((PyDapChainObject*)self)->chain_t->callback_atom_iter_get(
            ((PyChainAtomIterObject*)obj_iter)->atom_iter, DAP_CHAIN_ITER_OP_FIRST, &l_atom_size
            );
    if (((PyChainAtomObject*)obj_atom_ptr)->atom == NULL){
        Py_RETURN_NONE;
    }

    ((PyChainAtomObject*)obj_atom_ptr)->atom_size = l_atom_size;

    return Py_BuildValue("On", obj_atom_ptr, l_atom_size);
}

/**
 * @brief dap_chain_python_atom_get_datums
 * @param self
 * @param args
 * @return
 */
PyObject *dap_chain_python_atom_get_datums(PyObject *self, PyObject *args){
    PyObject *l_obj_atom_py = NULL;
    if(!PyArg_ParseTuple(args, "O", &l_obj_atom_py)){
        PyErr_SetString(PyExc_AttributeError, "The second argument must be an integer");
        return NULL;
    }
    PyChainAtomObject *l_obj_atom = ((PyChainAtomObject*)l_obj_atom_py);
    PyDapChainObject* l_obj_chain = ((PyDapChainObject*)self);
    size_t datums_count = 0;
    dap_chain_datum_t **l_datums = l_obj_chain->chain_t->callback_atom_get_datums(
                l_obj_atom->atom, l_obj_atom->atom_size, &datums_count);

    PyObject *list_datums = PyList_New(datums_count);
    for (size_t i=0; i < datums_count; i++){
        PyDapChainDatumObject *l_obj_datum_py = PyObject_New(PyDapChainDatumObject, &DapChainDatumObjectType);
        l_obj_datum_py->datum = l_datums[i];
        l_obj_datum_py->origin = false;
        PyList_SetItem(list_datums, i, (PyObject*)l_obj_datum_py);
    }
    DAP_DELETE(l_datums);
    return list_datums;
}

PyObject *dap_chain_python_atom_iter_get_next(PyObject *self, PyObject *args){
    //
    size_t atom_size = 0;
    PyObject *atom_iter = NULL;
    if(!PyArg_ParseTuple(args, "O", &atom_iter)){
        PyErr_SetString(PyExc_AttributeError, "Function takes exactly one argument");
        return NULL;
    }
    if (!PyDapChainAtomIter_Check(atom_iter)){
        PyErr_SetString(PyExc_AttributeError, "The first argument must be ChainAtomIter object.");
        return NULL;
    }
    PyObject *obj_atom_ptr = _PyObject_New(&DapChainAtomPtrObjectType);
    obj_atom_ptr = PyObject_Init(obj_atom_ptr, &DapChainAtomPtrObjectType);
    ((PyChainAtomObject*)obj_atom_ptr)->atom = ((PyDapChainObject*)self)->chain_t->callback_atom_iter_get(
            ((PyChainAtomIterObject*)atom_iter)->atom_iter,
            DAP_CHAIN_ITER_OP_NEXT,
            &atom_size);
    if (((PyChainAtomObject*)obj_atom_ptr)->atom == NULL){
        return Py_BuildValue("On", Py_None, 0);
    }

    ((PyChainAtomObject*)obj_atom_ptr)->atom_size = atom_size;
    return Py_BuildValue("On", obj_atom_ptr, atom_size);
}

PyObject *dap_chain_python_atom_iter_get_dag(PyObject *self, PyObject *args){
    (void)args;
    PyDapChainCsDagObject *obj_dag = PyObject_New(PyDapChainCsDagObject, &DapChainCsDagType);
    obj_dag->dag = DAP_CHAIN_CS_DAG(((PyDapChainObject*)self)->chain_t);
    return (PyObject*)obj_dag;
}

typedef struct _wrapping_chain_mempool_notify_callback {
    PyObject *func;
    PyObject *arg;
    dap_store_obj_t *obj;
} _wrapping_chain_mempool_notify_callback_t;


typedef struct _wrapping_chain_fork_resolved_notify_callback {
    PyObject *func;
    PyObject *arg;
} _wrapping_chain_fork_resolved_notify_callback_t;


bool dap_py_mempool_notifier(void *a_arg)
{
    if (!a_arg)
        return false;
    _wrapping_chain_mempool_notify_callback_t *l_callback = a_arg;
    if (!l_callback->obj) {
        log_it(L_ERROR, "It is not possible to call a python function. An object with arguments was not passed.");
        return false;
    }
    if (!l_callback->obj->group)
    {
        log_it(L_WARNING, "Called mempool notify in python with None group");
        return false;
    }
    PyGILState_STATE state = PyGILState_Ensure();
    dap_store_obj_t *l_obj = l_callback->obj;
    char l_op_code[2];
    l_op_code[0] = (char)dap_store_obj_get_type(l_obj);
    l_op_code[1] = '\0';
    PyObject *l_args;

    PyObject *obj_key = NULL;
    PyObject *obj_value = NULL;
    if (l_obj->key) {
        obj_key = PyUnicode_FromString(l_obj->key);
    } else {
        obj_key = Py_None;
        Py_INCREF(Py_None);
    }
    if (dap_store_obj_get_type(l_obj) == DAP_GLOBAL_DB_OPTYPE_ADD) {
        obj_value = PyBytes_FromStringAndSize((char *)l_obj->value, (Py_ssize_t)l_obj->value_len);
    } else {
        obj_value = Py_None;
        Py_INCREF(Py_None);
    }
    l_args = Py_BuildValue("ssOOO", l_op_code, l_obj->group, obj_key, obj_value, l_callback->arg);
    log_it(L_DEBUG, "Call mempool notifier with key '%s'", l_obj->key ? l_obj->key : "null");
    Py_XINCREF(l_callback->arg);
    Py_XINCREF(l_callback->func);
    PyObject_CallObject(l_callback->func, l_args);
    Py_XDECREF(l_args);
    Py_XDECREF(l_callback->func);
    Py_XDECREF(l_callback->arg);
    Py_XDECREF(obj_key);
    Py_XDECREF(obj_value);
    dap_store_obj_free_one(l_callback->obj);
    PyGILState_Release(state);
    return false;
}

static void _wrapping_dap_chain_mempool_notify_handler(dap_store_obj_t *a_obj, void *a_arg)
{
    // Notify python context from proc thread to avoid deadlock in GDB context with GIL accuire trying
    _wrapping_chain_mempool_notify_callback_t *l_obj = DAP_NEW(_wrapping_chain_mempool_notify_callback_t);
    if (!l_obj) {
        log_it(L_CRITICAL, "Memory allocation error");
        return;
    }
    l_obj->obj = dap_store_obj_copy(a_obj, 1);
    l_obj->func = ((_wrapping_chain_mempool_notify_callback_t *)a_arg)->func;
    l_obj->arg = ((_wrapping_chain_mempool_notify_callback_t *)a_arg)->arg;
    dap_proc_thread_callback_add(NULL, dap_py_mempool_notifier, l_obj);
}
/**
 * @brief _wrapping_dap_chain_atom_notify_handler
 * @param a_arg
 * @param a_chain
 * @param a_id
 * @param a_atom
 * @param a_atom_size
 */
static void _wrapping_dap_chain_atom_notify_handler(void * a_arg, dap_chain_t *a_chain, dap_chain_cell_id_t a_id,
                                                    dap_hash_fast_t *a_hash, void* a_atom, size_t a_atom_size, dap_time_t a_atom_time)
{
    if (!a_arg){
        return;
    }
    _wrapping_chain_mempool_notify_callback_t  *l_callback = (_wrapping_chain_mempool_notify_callback_t *)a_arg;

    PyObject *l_args;
    PyGILState_STATE state = PyGILState_Ensure();

    dap_chain_atom_ptr_t l_atom = (dap_chain_atom_ptr_t) a_atom;
    PyChainAtomObject *l_atom_obj = NULL;
    if(l_atom){
        l_atom_obj= PyObject_New(PyChainAtomObject, &DapChainAtomPtrObjectType);
        l_atom_obj->atom = l_atom;
        l_atom_obj->atom_size = a_atom_size;
        l_args = Py_BuildValue("OO", l_atom_obj, l_callback->arg);
    }else{
        l_args = Py_BuildValue("OO", Py_None, l_callback->arg);
    }

    log_it(L_DEBUG, "Call atom notifier for chain %s with atom size %zd", a_chain->name, a_atom_size );
    PyObject *result = PyObject_CallObject(l_callback->func, l_args);
    if (!result) {
        python_error_in_log_it(LOG_TAG);
    }
    Py_XDECREF(result);
    Py_DECREF(l_args);
    PyGILState_Release(state);
}

static void _wrapping_dap_chain_atom_confirmed_notify_handler(void *a_arg, dap_chain_t *a_chain, dap_chain_cell_id_t a_id,
                                                              dap_hash_fast_t *a_hash, void *a_atom, size_t a_atom_size, dap_time_t a_atom_time)
{
    if (!a_arg) {
        return;
    }
    _wrapping_chain_mempool_notify_callback_t *l_callback = (_wrapping_chain_mempool_notify_callback_t *)a_arg;

    PyGILState_STATE state = PyGILState_Ensure();

    dap_chain_atom_ptr_t l_atom = (dap_chain_atom_ptr_t)a_atom;
    PyChainAtomObject *l_atom_obj = NULL;
    if (l_atom) {
        l_atom_obj = PyObject_New(PyChainAtomObject, &DapChainAtomPtrObjectType);
        l_atom_obj->atom = l_atom;
        l_atom_obj->atom_size = a_atom_size;
        PyObject *l_args = Py_BuildValue("OO", l_atom_obj, l_callback->arg);
        log_it(L_DEBUG, "Call atom confirmed notifier for chain %s with atom size %zd", a_chain->name, a_atom_size);
        PyObject *result = PyObject_CallObject(l_callback->func, l_args);
        if (!result) {
            python_error_in_log_it(LOG_TAG);
        }
        Py_XDECREF(result);
        Py_DECREF(l_args);
        Py_DECREF(l_atom_obj);
    } else {
        PyObject *l_args = Py_BuildValue("OO", Py_None, l_callback->arg);
        PyObject *result = PyObject_CallObject(l_callback->func, l_args);
        if (!result) {
            python_error_in_log_it(LOG_TAG);
        }
        Py_XDECREF(result);
        Py_DECREF(l_args);
    }

    PyGILState_Release(state);
}

PyDapHashFastObject *py_dap_hash_fast_from_hash_fast(dap_hash_fast_t *a_hash_fast)
{
    
    PyDapHashFastObject *obj_hash = PyObject_New(PyDapHashFastObject, &DapChainHashFastObjectType);
    obj_hash->hash_fast = DAP_DUP(a_hash_fast);
    obj_hash->origin = true;
    return obj_hash;
}

static void _wrapping_dap_chain_fork_resolved_notify_handler(dap_chain_t *a_chain, dap_hash_fast_t a_block_before_fork_hash, dap_list_t *a_reverted_blocks, 
                                                                uint64_t a_reverted_blocks_cnt, uint64_t a_main_blocks_cnt, void * a_arg)
{
    log_it(L_DEBUG, "Call fork resolution notifier %s", a_chain->name);

    if (!a_arg) {
        return;
    }
    
    _wrapping_chain_fork_resolved_notify_callback_t *l_callback = (_wrapping_chain_fork_resolved_notify_callback_t *)a_arg;

    PyGILState_STATE state = PyGILState_Ensure();

    PyDapHashFastObject *obj_hash_fast = py_dap_hash_fast_from_hash_fast(&a_block_before_fork_hash);

    PyObject *obj_list = PyList_New(dap_list_length(a_reverted_blocks));
    size_t i = 0;
    for (dap_list_t *l_iter = a_reverted_blocks; l_iter; l_iter = l_iter->next){
        PyList_SetItem(obj_list, i, (PyObject*)py_dap_hash_fast_from_hash_fast(l_iter->data));
        ++i;
    }

    PyObject *chain_obj = _PyObject_New(&DapChainObjectType);
    ((PyDapChainObject*)chain_obj)->chain_t = a_chain;

    PyObject *l_args = Py_BuildValue("OiiOOO", chain_obj, a_reverted_blocks_cnt, a_main_blocks_cnt, obj_hash_fast, obj_list, l_callback->arg);
    PyObject *result = PyObject_CallObject(l_callback->func, l_args);

    if (!result) {
        python_error_in_log_it(LOG_TAG);
    }

    Py_XDECREF(result);
    Py_DECREF(l_args);
    PyGILState_Release(state);    
}

/**
 * @brief dap_chain_python_add_mempool_notify_callback
 * @param self
 * @param args
 * @return
 */
PyObject *dap_chain_python_add_mempool_notify_callback(PyObject *self, PyObject *args){
    dap_chain_t *l_chain = ((PyDapChainObject*)self)->chain_t;
    PyObject *obj_func;
    PyObject *obj_arg;
    if (!PyArg_ParseTuple(args, "OO", &obj_func, &obj_arg)){
        PyErr_SetString(PyExc_AttributeError, "Argument must be callable");
        return NULL;
    }
    if (!PyCallable_Check(obj_func)){
        PyErr_SetString(PyExc_AttributeError, "Invalid first parameter passed to function. The first "
                                              "argument must be an instance of an object of type Chain. ");
        return NULL;
    }
    _wrapping_chain_mempool_notify_callback_t *l_callback = DAP_NEW_Z(_wrapping_chain_mempool_notify_callback_t);
    if (!l_callback) {
        log_it(L_CRITICAL, "Memory allocation error");
        return NULL;
    }
    l_callback->func = obj_func;
    l_callback->arg = obj_arg;
    Py_INCREF(obj_func);
    Py_INCREF(obj_arg);
    dap_chain_add_mempool_notify_callback(l_chain, _wrapping_dap_chain_mempool_notify_handler, l_callback);
    Py_RETURN_NONE;
}

/**
 * @brief dap_chain_net_add_atom_notify_py
 * @param self
 * @param args
 * @return
 */
PyObject *dap_chain_net_add_atom_notify_callback(PyObject *self, PyObject *args){
    dap_chain_t *l_chain = ((PyDapChainObject*)self)->chain_t;
    PyObject *obj_func;
    PyObject *obj_arg;
    if (!PyArg_ParseTuple(args, "OO", &obj_func, &obj_arg)){
        PyErr_SetString(PyExc_AttributeError, "Argument must be callable");
        return NULL;
    }
    if (!PyCallable_Check(obj_func)){
        PyErr_SetString(PyExc_AttributeError, "Invalid first parameter passed to function. The first "
                                              "argument must be a function ");
        return NULL;
    }
    _wrapping_chain_mempool_notify_callback_t *l_callback = DAP_NEW_Z(_wrapping_chain_mempool_notify_callback_t);
    if (!l_callback) {
        log_it(L_CRITICAL, "Memory allocation error");
        return NULL;
    }
    l_callback->func = obj_func;
    l_callback->arg = obj_arg;
    Py_INCREF(obj_func);
    Py_INCREF(obj_arg);
    dap_chain_add_callback_notify(l_chain, _wrapping_dap_chain_atom_notify_handler, NULL, l_callback);
    Py_RETURN_NONE;
}

/**
 * @brief dap_chain_atom_confirmed_notify_add_py
 * @param self
 * @param args
 * @return
 */
PyObject *dap_chain_atom_confirmed_notify_add_py(PyObject *self, PyObject *args)
{
    dap_chain_t *l_chain = ((PyDapChainObject *)self)->chain_t;
    PyObject *obj_func;
    PyObject *obj_arg;
    int conf_cnt = 0;
    if (!PyArg_ParseTuple(args, "OOi", &obj_func, &obj_arg, &conf_cnt)) {
        PyErr_SetString(PyExc_AttributeError, "Arguments must be a callable and an argument");
        return NULL;
    }
    if (!PyCallable_Check(obj_func)) {
        PyErr_SetString(PyExc_AttributeError, "First argument must be a callable function");
        return NULL;
    }
    _wrapping_chain_mempool_notify_callback_t *l_callback = DAP_NEW_Z(_wrapping_chain_mempool_notify_callback_t);
    if (!l_callback) {
        log_it(L_CRITICAL, "Memory allocation error");
        return NULL;
    }
    l_callback->func = obj_func;
    l_callback->arg = obj_arg;
    Py_INCREF(obj_func);
    Py_INCREF(obj_arg);
    log_it(L_DEBUG, "Added confirmed atom notify in %s:%s for %d confirmations", l_chain->net_name, l_chain->name, conf_cnt);

    dap_chain_atom_confirmed_notify_add(l_chain, _wrapping_dap_chain_atom_confirmed_notify_handler, l_callback, conf_cnt);
    Py_RETURN_NONE;
}

PyObject *dap_chain_fork_resolved_notify_add_py(PyObject *self, PyObject *args) {

    PyObject *obj_func;
    PyObject *obj_arg;

    if (!PyArg_ParseTuple(args, "OO", &obj_func, &obj_arg)){
        PyErr_SetString(PyExc_AttributeError, "Argument must be callable");
        return NULL;
    }   
    
    if (!PyCallable_Check(obj_func)) {
        PyErr_SetString(PyExc_AttributeError, "First argument must be a callable function");
        return NULL;
    }

    _wrapping_chain_fork_resolved_notify_callback_t *l_callback = DAP_NEW_Z(_wrapping_chain_fork_resolved_notify_callback_t);
    if (!l_callback) {
        log_it(L_CRITICAL, "Memory allocation error");
        return NULL;
    }

    l_callback->func = obj_func;
    l_callback->arg = obj_arg;

    Py_INCREF(obj_func);
    Py_INCREF(obj_arg);
 
    dap_chain_block_add_fork_notificator(_wrapping_dap_chain_fork_resolved_notify_handler, l_callback);
    
    Py_RETURN_NONE;
    }
/**
 * @brief dap_chain_python_atom_find_by_hash
 * @param self
 * @param args
 * @return
 */
PyObject *dap_chain_python_atom_find_by_hash(PyObject *self, PyObject* args){
    PyObject *obj_iter;
    PyDapHashFastObject *obj_hf;
    if (!PyArg_ParseTuple(args, "OO", &obj_iter, &obj_hf)){
        return NULL;
    }
    if (!PyDapChainAtomIter_Check(obj_iter)){
        PyErr_SetString(PyExc_AttributeError, "The first argument to the function was not correctly "
                                              "passed, the argument must be an instance of a class of type ChainAtomPtr.");
        return NULL;
    }
    if(!PyDapHashFast_Check(obj_hf)){
        PyErr_SetString(PyExc_AttributeError, "The second argument to the function was not correctly passed, the "
                                              "argument must be an instance of a class of type HashFast.");
        return NULL;
    }
    size_t l_size_atom = 0;
    dap_chain_atom_ptr_t l_ptr = ((PyDapChainObject*)self)->chain_t->callback_atom_find_by_hash(
            ((PyChainAtomIterObject*)obj_iter)->atom_iter,
            obj_hf->hash_fast,
            &l_size_atom);
    if (l_ptr == NULL) {
        return Py_BuildValue("On", Py_None, 0);
    } else {
        PyChainAtomObject *l_obj_ptr = PyObject_New(PyChainAtomObject, &DapChainAtomPtrObjectType);
        l_obj_ptr->atom = l_ptr;
        return Py_BuildValue("On", l_obj_ptr, l_size_atom);
    }
}

/**
 * @breif dap_chain_python_get_atom_count
 * @param self
 * @param args
 * @return
 */
PyObject *dap_chain_python_get_atom_count(PyObject *self, PyObject *args){
    (void)args;
    size_t l_count = ((PyDapChainObject*)self)->chain_t->callback_count_atom(((PyDapChainObject*)self)->chain_t);
    return Py_BuildValue("n", l_count);
}

/**
 * @breif dap_chain_python_get_atoms
 * @param self
 * @param args
 * @return
 */
PyObject *dap_chain_python_get_atoms(PyObject *self, PyObject *args) {
    size_t count, page;
    PyObject *obj_reverse;
    if (!PyArg_ParseTuple(args, "nnO", &count, &page, &obj_reverse)) {
        return NULL;
    }
    if (!PyBool_Check(obj_reverse)) {
        PyErr_SetString(PyExc_AttributeError, "");
        return NULL;
    }
    bool reverse = (obj_reverse == Py_True) ? true : false;
    dap_chain_t *l_chain = ((PyDapChainObject *) self)->chain_t;
    dap_list_t *l_atoms = l_chain->callback_get_atoms(l_chain, count, page, reverse);
    if (!l_atoms) {
        Py_RETURN_NONE;
    }
    PyObject *obj_list = PyList_New(dap_list_length(l_atoms) / 2);
    size_t i = 0;
    for (dap_list_t *l_iter = l_atoms; l_iter != NULL; l_iter = l_iter->next, ++i) {
        PyChainAtomObject *obj_atom = PyObject_New(PyChainAtomObject, &DapChainAtomPtrObjectType);
        obj_atom->atom = l_iter->data;
        l_iter = l_iter->next;
        obj_atom->atom_size = *((size_t *) l_iter->data);
        PyList_SetItem(obj_list, i, (PyObject*)obj_atom);
    }
    dap_list_free(l_atoms);
    return obj_list;
}

/**
 * @brief dap_chain_python_get_count_tx
 * @param self
 * @param args
 * @return
 */
PyObject *dap_chain_python_get_count_tx(PyObject *self, PyObject *args){
    (void)args;
    dap_chain_t *l_chain = ((PyDapChainObject*)self)->chain_t;
    size_t cnt = l_chain->callback_count_tx(l_chain);
    return Py_BuildValue("n", cnt);
}

/**
 * @brief dap_chain_python_get_txs
 * @param self
 * @param args
 * @return
 */
PyObject *dap_chain_python_get_txs(PyObject *self, PyObject *args){
    dap_chain_t *l_chain = ((PyDapChainObject*)self)->chain_t;
    size_t count = 0, page = 0;
    PyObject *obj_reverse;
    if (!PyArg_ParseTuple(args, "nnO", &count, &page, &obj_reverse)){
        return NULL;
    }
    if (!PyBool_Check(obj_reverse)){
        PyErr_SetString(PyExc_AttributeError, "");
        return NULL;
    }
    bool l_reverse = (obj_reverse == Py_True) ? true : false;
    dap_list_t *l_list = l_chain->callback_get_txs(l_chain, count, page, l_reverse);
    if (l_list != NULL){
        PyObject *l_obj_list = PyList_New(dap_list_length(l_list));
        size_t i = 0;
        for (dap_list_t *l_ptr = l_list; l_ptr != NULL; l_ptr = l_ptr->next, ++i) {
            PyDapChainDatumTxObject *l_obj_tx = PyObject_New(PyDapChainDatumTxObject, &DapChainDatumTxObjectType);
            l_obj_tx->datum_tx = l_ptr->data;
            l_obj_tx->original = false;
            PyList_SetItem(l_obj_list, i, (PyObject*)l_obj_tx);
        }
        dap_list_free(l_list);
        return l_obj_list;
    }
    Py_RETURN_NONE;
}

PyObject *dap_chain_python_get_cs_name(PyObject *self, PyObject *args){
    (void)args;
    dap_chain_t* l_chain = ((PyDapChainObject*)self)->chain_t;
    dap_chain_pvt_t *l_chain_pvt = DAP_CHAIN_PVT(l_chain);
    return Py_BuildValue("s", l_chain_pvt->cs_name);
}

PyObject *PyDapChain_str(PyObject *self){
    return Py_BuildValue("s", ((PyDapChainObject*)self)->chain_t->name);
}

PyObject *dap_chain_python_get_net(PyObject *self, PyObject *args){
    (void)args;
    PyDapChainNetObject *obj_net = PyObject_New(PyDapChainNetObject, &DapChainNetObjectType);
    obj_net->chain_net = dap_chain_net_by_id(((PyDapChainObject*)self)->chain_t->net_id);
    return (PyObject*)obj_net;
}

PyObject *dap_chain_python_get_config_item(PyObject *self, PyObject *args) {
    const char *section_path;
    const char *item_name;
    PyObject *obj_def = NULL;
    if (!PyArg_ParseTuple(args, "ss|O", &section_path, &item_name, &obj_def))
        return NULL;
    return python_get_config_item(((PyDapChainObject*)self)->chain_t->config, section_path, item_name, obj_def);
}
