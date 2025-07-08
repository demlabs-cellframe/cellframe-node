#include "wrapping_dap_chain_cs_dag.h"
#include "dap_chain_cell.h"
#include "wrapping_dap_chain_cs_dag_round.h"

static PyMethodDef DapChainCsDagMethods[] = {
        {"findByHash", (PyCFunction)dap_chain_cs_dag_find_event_by_hash_py, METH_VARARGS, ""},
        {"getCurrentRound", dap_chain_cs_dag_get_current_round_py, METH_NOARGS, ""},
        {}
};

PyTypeObject DapChainCsDagType = DAP_PY_TYPE_OBJECT(
        "CellFrame.Consensus.ChainCSDag", sizeof(PyDapChainCsDagObject),
        "Chain cs dag objects",
        .tp_methods = DapChainCsDagMethods);

PyObject *dap_chain_cs_dag_get_current_round_py(PyObject *self, PyObject *args) {
    const char *l_round_event_group = ((PyDapChainCsDagObject*)self)->dag->gdb_group_events_round_new;
    if (!l_round_event_group) Py_RETURN_NONE;

    size_t l_objs_count = 0;
    dap_global_db_obj_t * l_objs = dap_global_db_get_all_sync(l_round_event_group,&l_objs_count);
    if (!l_objs && !l_objs_count) Py_RETURN_NONE;
    PyDapChainCsDagRoundObject *obj_round = WRAPPING_DAP_CHAIN_CS_DAG_ROUND_NEW;
    dap_chain_cs_dag_event_round_item_t *l_item = (dap_chain_cs_dag_event_round_item_t*)l_objs[0].value;
    obj_round->item = DAP_NEW_SIZE(dap_chain_cs_dag_event_round_item_t, l_objs[0].value_len);
    memcpy(obj_round->item, l_objs[0].value, l_objs[0].value_len);
    dap_global_db_objs_delete(l_objs, l_objs_count);
    return (PyObject*)obj_round;
}

PyObject *dap_chain_cs_dag_find_event_by_hash_py(PyObject *self, PyObject *args){
    PyObject *obj_hash;
//    PyObject *obj_atom_iter;
    if (!PyArg_ParseTuple(args, "O", &obj_hash)){
        PyErr_SetString(PyExc_AttributeError, "Function takes exactly two arguments. ");
        return NULL;
    }
    bool isCheck = PyObject_TypeCheck(obj_hash, &DapChainHashFastObjectType);
    if (!isCheck){
        PyErr_SetString(PyExc_AttributeError, "The first argument to this function is not a DapHash object.");
        return NULL;
    }
//    if (!PyDapChainAtomIter_Check(obj_atom_iter)){
//        PyErr_SetString(PyExc_AttributeError, "The second argument received to this function is not an object of type ChainAtomIter.");
//        return NULL;
//    }
    dap_chain_cell_t *l_cell = ((PyDapChainCsDagObject*)self)->dag->chain->cells;
    size_t size_atom = 0;
    dap_chain_atom_iter_t *l_iter = ((PyDapChainCsDagObject*)self)->dag->chain->callback_atom_iter_create(
            ((PyDapChainCsDagObject*)self)->dag->chain,
            l_cell->id, 0
            );
    dap_chain_atom_ptr_t l_ptr = ((PyDapChainCsDagObject*)self)->dag->chain->callback_atom_find_by_hash(
            l_iter,
            ((PyDapHashFastObject*)obj_hash)->hash_fast,
            &size_atom);
    if (l_ptr == NULL){
        Py_RETURN_NONE;
    }
    PyDapChainCsDagEventObject *obj_event = PyObject_New(PyDapChainCsDagEventObject,
                                                         &DapChainCsDagEventType);
    obj_event->event = (dap_chain_cs_dag_event_t *)l_iter->cur;
    obj_event->event_size = l_iter->cur_size;
    return (PyObject*)obj_event;
}
