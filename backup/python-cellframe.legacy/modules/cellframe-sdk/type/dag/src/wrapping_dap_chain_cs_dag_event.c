#include "wrapping_dap_chain_cs_dag_event.h"
#include "python-cellframe_common.h"

static PyMethodDef PyDapChainCsDagEventMethodsDef[] = {
        {"fromAtom", (PyCFunction)wrapping_dap_chain_cs_dag_event_from_atom, METH_VARARGS | METH_STATIC, ""},
        {}
};

static PyGetSetDef PyDapChainCsDagEventGetsSetsDef[] = {
        {"hash", (getter)wrapping_dap_chain_cs_dag_event_get_hash, NULL, NULL, NULL},
        {"version", (getter)wrapping_dap_chain_cs_dag_event_get_version, NULL, NULL, NULL},
        {"roundId", (getter)wrapping_dap_chain_cs_dag_event_get_round_id, NULL, NULL, NULL},
        {"created", (getter)wrapping_dap_chain_cs_dag_event_get_ts_created, NULL, NULL, NULL},
        {"chainId", (getter)wrapping_dap_chain_cs_dag_event_get_chain_id, NULL, NULL, NULL},
        {"cellId", (getter)wrapping_dap_chain_cs_dag_event_get_cell_id, NULL, NULL, NULL},
        {"hashCount", (getter)wrapping_dap_chain_cs_dag_event_get_hash_count, NULL, NULL, NULL},
        {"signsCount", (getter)wrapping_dap_chain_cs_dag_event_get_signs_count, NULL, NULL, NULL},
        {"links", (getter)wrapping_dap_chain_cs_dag_event_get_links, NULL, NULL, NULL},
        {"datum", (getter)wrapping_dap_chain_cs_dag_event_get_datum, NULL, NULL, NULL},
        {"signs", (getter)wrapping_dap_chain_cs_dag_event_get_signs, NULL, NULL, NULL},
        {}
};

PyTypeObject DapChainCsDagEventType = DAP_PY_TYPE_OBJECT(
        "CellFrame.ChainCsDagEvent",sizeof(PyDapChainCsDagEventObject),
        "Chain cs dag event objects",
        .tp_methods = PyDapChainCsDagEventMethodsDef,
        .tp_getset = PyDapChainCsDagEventGetsSetsDef);

PyObject *wrapping_dap_chain_cs_dag_event_from_atom(PyObject *self, PyObject *args){
    (void)self;
    PyObject *obj_atom_ptr;
    if (!PyArg_ParseTuple(args, "O", &obj_atom_ptr)){
        return NULL;
    }
    PyDapChainCsDagEventObject *obj_dag = PyObject_New(PyDapChainCsDagEventObject, &DapChainCsDagEventType);
    obj_dag->event = (dap_chain_cs_dag_event_t *)((PyChainAtomObject *)obj_atom_ptr)->atom;
    obj_dag->event_size = ((PyChainAtomObject *)obj_atom_ptr)->atom_size;
    return (PyObject*)obj_dag;
}

PyObject *wrapping_dap_chain_cs_dag_event_get_hash(PyObject *self, void *closure){
    (void)closure;
    PyDapHashFastObject *obj_hf = PyObject_New(PyDapHashFastObject, &DapChainHashFastObjectType);
    obj_hf->hash_fast = DAP_NEW(dap_chain_hash_fast_t);
    dap_hash_fast(
            ((PyDapChainCsDagEventObject*)self)->event,
            ((PyDapChainCsDagEventObject*)self)->event_size,
            obj_hf->hash_fast);
    obj_hf->origin = true;
    return (PyObject*)obj_hf;
}

PyObject *wrapping_dap_chain_cs_dag_event_get_version(PyObject *self, void *closure){
    (void)closure;
    return Py_BuildValue("H", ((PyDapChainCsDagEventObject*)self)->event->header.version);
}
PyObject *wrapping_dap_chain_cs_dag_event_get_round_id(PyObject *self, void *closure){
    (void)closure;
    return Py_BuildValue("k", ((PyDapChainCsDagEventObject*)self)->event->header.round_id);
}
PyObject *wrapping_dap_chain_cs_dag_event_get_ts_created(PyObject *self, void *closure){
    (void)closure;
    PyDateTime_IMPORT;
    PyObject *obj_ts_float = PyLong_FromLong(((PyDapChainCsDagEventObject*)self)->event->header.ts_created);
    PyObject *obj_ts = Py_BuildValue("(O)", obj_ts_float);
    PyDateTime_IMPORT;
    PyObject *obj_dt = PyDateTime_FromTimestamp(obj_ts);
    return obj_dt;
}
PyObject *wrapping_dap_chain_cs_dag_event_get_chain_id(PyObject *self, void *closure){
    (void)closure;
    PyDapChainIDObject *obj_chain_id = PyObject_New(PyDapChainIDObject, &DapChainIdObjectType);
    obj_chain_id->chain_id = &((PyDapChainCsDagEventObject*)self)->event->header.chain_id;
    return (PyObject*)obj_chain_id;
}
PyObject *wrapping_dap_chain_cs_dag_event_get_cell_id(PyObject *self, void *closure){
    (void)closure;
    PyDapChainCellIDObject *obj_cell_id = PyObject_New(PyDapChainCellIDObject, &DapChainCellIdObjectType);
    obj_cell_id->cell_id = ((PyDapChainCsDagEventObject*)self)->event->header.cell_id;
    return (PyObject*)obj_cell_id;
}
PyObject *wrapping_dap_chain_cs_dag_event_get_hash_count(PyObject *self, void *closure){
    (void)closure;
    return Py_BuildValue("H", ((PyDapChainCsDagEventObject*)self)->event->header.hash_count);
}
PyObject *wrapping_dap_chain_cs_dag_event_get_signs_count(PyObject *self, void *closure){
    (void)closure;
    return Py_BuildValue("H", ((PyDapChainCsDagEventObject*)self)->event->header.signs_count);
}
PyObject *wrapping_dap_chain_cs_dag_event_get_links(PyObject *self, void *closure){
    (void)closure;
    PyObject *obj_list = PyList_New(((PyDapChainCsDagEventObject*)self)->event->header.hash_count);
    for (uint16_t i=0; i < ((PyDapChainCsDagEventObject*)self)->event->header.hash_count; i++){
        PyDapHashFastObject  *obj_hf = PyObject_New(PyDapHashFastObject, &DapChainHashFastObjectType);
        obj_hf->hash_fast =
                (dap_chain_hash_fast_t *) (((PyDapChainCsDagEventObject*)self)->event->hashes_n_datum_n_signs +
                                                                    i*sizeof (dap_chain_hash_fast_t));
        obj_hf->origin = false;
        PyList_SetItem(obj_list, i, (PyObject *)obj_hf);
    }
    return obj_list;
}
PyObject *wrapping_dap_chain_cs_dag_event_get_datum(PyObject *self, void *closure){
    (void)closure;
    size_t l_offset =  ((PyDapChainCsDagEventObject*)self)->event->header.hash_count*sizeof (dap_chain_hash_fast_t);
    PyDapChainDatumObject *datum = PyObject_New(PyDapChainDatumObject, &DapChainDatumObjectType);
    datum->datum = (dap_chain_datum_t*) (((PyDapChainCsDagEventObject*)self)->event->hashes_n_datum_n_signs + l_offset);
    datum->origin = false;
    return (PyObject*)datum;
}
PyObject *wrapping_dap_chain_cs_dag_event_get_signs(PyObject *self, void *closure) {
    dap_chain_cs_dag_event_t *l_event = ((PyDapChainCsDagEventObject*)self)->event;
    size_t l_event_size = ((PyDapChainCsDagEventObject*)self)->event_size;
    size_t l_sign_offset = dap_chain_cs_dag_event_calc_size_excl_signs(l_event, l_event_size);
    
    if (l_sign_offset >= l_event_size) {
        _PyErr_logIt(L_ERROR, "event", "<corrupted: invalid signes offset>");
        return PyList_New(0);
    }
    
    //count real signatures (first N not corrupted)
    size_t l_real_signs_count = 0;
    size_t l_signs_count = ((PyDapChainCsDagEventObject*)self)->event->header.signs_count;
    
    for (l_real_signs_count = 0; l_real_signs_count < l_event->header.signs_count && l_sign_offset < l_event_size; ++l_real_signs_count) {
        dap_sign_t *l_sign = (dap_sign_t*)((uint8_t*)l_event + l_sign_offset);
        l_sign_offset += dap_sign_get_size(l_sign);
    }

    
    l_sign_offset = dap_chain_cs_dag_event_calc_size_excl_signs(l_event, l_event_size);
    PyObject *obj_list = PyList_New(l_real_signs_count);

    for (uint8_t i = 0; i < l_real_signs_count; ++i) {
        dap_sign_t *l_sign = (dap_sign_t*)((uint8_t*)l_event + l_sign_offset);
        PyObject *obj_sign = PyDapSignObject_Cretae(l_sign);
        PyList_SetItem(obj_list, i, obj_sign);
        l_sign_offset += dap_sign_get_size(l_sign);
    }
    return obj_list;
}
