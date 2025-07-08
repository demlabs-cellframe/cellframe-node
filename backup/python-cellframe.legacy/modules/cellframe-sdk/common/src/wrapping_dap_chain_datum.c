#include "wrapping_dap_chain_datum.h"
#include "libdap_chain_net_python.h"
#define LOG_TAG "wrapping_dap_chain_datum"
//void PyDapChainDatumObject_dealloc(PyDapChainDatumObject* object){
//}

/* Dap chain datum type id */

PyTypeObject DapChainDatumTypeIdObjectType = DAP_PY_TYPE_OBJECT(
        "CellFrame.Chain.DatumTypeId", sizeof(PyDapChainDatumTypeIdObject),
        "Chain datum type id object");

/* DAP chain datum */
static PyMethodDef DapChainDatumMethods[] = {
        {"getSize", dap_chain_datum_size_py, METH_NOARGS, ""},
        {"isDatumTX", dap_chain_datum_is_type_tx, METH_NOARGS, ""},
        {"getDatumTX", wrapping_dap_chain_datum_get_datum_tx, METH_VARARGS, ""},
        {"isDatumToken", dap_chain_datum_is_type_token, METH_NOARGS, ""},
        {"getDatumToken", wrapping_dap_chain_datum_get_datum_token, METH_NOARGS, ""},
        {"isDatumTokenEmission", dap_chain_datum_is_type_emission, METH_NOARGS, ""},
        {"getDatumTokenEmission", wrapping_dap_chain_datum_get_datum_token_emission, METH_NOARGS, ""},
        {"isDatumCustom", wrapping_dap_chain_datum_is_type_custom, METH_NOARGS, ""},
        {"isDatumDecree", wrapping_dap_chain_datum_is_type_decree, METH_NOARGS, ""},
        {"getDatumDecree", wrapping_dap_chain_datum_get_decree, METH_NOARGS, ""},
        {"isDatumAnchor", wrapping_dap_chain_datum_is_type_anchor, METH_NOARGS, ""},
        {"getDatumAnchor", wrapping_dap_chain_datum_get_anchor, METH_NOARGS, ""},
        {"getTypeStr", dap_chain_datum_get_type_str_py, METH_NOARGS, ""},
        {"getTypeId", wrapping_dap_chain_datum_get_type_id_py, METH_NOARGS, ""},
        {"fromBytes", wrapping_dap_chain_datum_create_from_bytes, METH_VARARGS | METH_STATIC, ""},
        {NULL}
};

static PyGetSetDef  DapChainDatumGetSet[] = {
        {"hash", (getter)wrapping_dap_chain_datum_get_hash_py, NULL, NULL, NULL},
        {"versionStr", (getter)wrapping_dap_chain_datum_get_version_str_py, NULL, NULL, NULL},
        {"tsCreated", (getter)dap_chain_datum_get_ts_created_py, NULL, NULL, NULL},
        {"raw", (getter)wrapping_dap_chain_datum_get_raw_py, NULL, NULL, NULL},
        {"dataRaw", (getter)wrapping_dap_chain_datum_get_data_raw_py, NULL, NULL, NULL},
        {NULL}
};

PyTypeObject DapChainDatumObjectType = {
        .ob_base = PyVarObject_HEAD_INIT(NULL, 0)
        .tp_name = "CellFrame.Chain.Datum",
        .tp_basicsize = sizeof(PyDapChainDatumObject),
        .tp_dealloc = (destructor)PyDapChainDatumObject_dealloc,
        .tp_doc = "Chain datum object",
        .tp_methods = DapChainDatumMethods,
        .tp_getset = DapChainDatumGetSet,
        .tp_new = PyDapChainDatumObject_new
};

void PyDapChainDatumObject_dealloc(PyDapChainDatumObject* self) {
    if (self->origin) {
        DAP_DELETE(self->datum);
    }
    Py_TYPE(self)->tp_free((PyObject*)self);
}

bool PyDapChainDatum_Check(PyObject *self){
    return PyObject_TypeCheck(self, &DapChainDatumObjectType);
}

PyObject *PyDapChainDatumObject_new(PyTypeObject *type_object, PyObject *args, PyObject *kwds){
    PyObject *obj_arg_first;
    PyObject *obj_arg_second = NULL;
    if (!PyArg_ParseTuple(args, "O|O", &obj_arg_first, &obj_arg_second))
        return NULL;
    if (PyLong_Check(obj_arg_first)){
        if (!PyBytes_Check(obj_arg_second)){
            PyErr_SetString(PyExc_AttributeError, "The datum constructor can only take an instance of an object of "
                                                  "the bytes type as an instance");
            return NULL;
        }
        uint16_t type_id = (uint16_t)PyLong_AsUnsignedLong(obj_arg_first);
        void *l_bytes = (void*)PyBytes_AsString(obj_arg_second);
        size_t l_bytes_size = PyBytes_Size(obj_arg_second);
        PyDapChainDatumObject *obj = (PyDapChainDatumObject*)PyType_GenericNew(type_object, args, kwds);
        obj->datum = dap_chain_datum_create(type_id, l_bytes, l_bytes_size);
        obj->origin = true;
        return (PyObject *)obj;
    } else {
        if (!PyBytes_Check(obj_arg_first)){
            PyErr_SetString(PyExc_AttributeError, "The datum constructor can only take an instance of an object of "
                                                  "the bytes type as an instance");
            return NULL;
        }
        void *l_bytes = (void*)PyBytes_AsString(obj_arg_first);
        size_t l_bytes_size = PyBytes_Size(obj_arg_first);
        PyDapChainDatumObject *obj = (PyDapChainDatumObject*)PyType_GenericNew(type_object, args, kwds);
        obj->datum = DAP_NEW_Z_SIZE(dap_chain_datum_t, l_bytes_size);
        memcpy(obj->datum, l_bytes, l_bytes_size);
        obj->origin = true;
        return (PyObject *)obj;
    }
}

PyObject *dap_chain_datum_size_py(PyObject *self, PyObject *args){
    (void)args;
    size_t size = dap_chain_datum_size(((PyDapChainDatumObject*)self)->datum);
    return PyLong_FromSize_t(size);
}

PyObject *dap_chain_datum_get_ts_created_py(PyObject *self, void* closure){
    (void)closure;
    PyDateTime_IMPORT;
    PyObject *obj_ts_long =  Py_BuildValue("(k)",((PyDapChainDatumObject*)self)->datum->header.ts_create);
    PyObject *obj_ts = PyDateTime_FromTimestamp(obj_ts_long);
    return obj_ts;
}

PyObject *dap_chain_datum_is_type_tx(PyObject *self, PyObject *args){
    (void)args;
    if (((PyDapChainDatumObject*)self)->datum->header.type_id == DAP_CHAIN_DATUM_TX){
        Py_RETURN_TRUE;
    } else {
        Py_RETURN_FALSE;
    }
}

PyObject *dap_chain_datum_is_type_token(PyObject *self, PyObject *args){
    (void)args;
    if (((PyDapChainDatumObject*)self)->datum->header.type_id == DAP_CHAIN_DATUM_TOKEN ){
        Py_RETURN_TRUE;
    } else {
        Py_RETURN_FALSE;
    }
}

PyObject *wrapping_dap_chain_datum_get_datum_token(PyObject *self, PyObject *args){
    (void)args;
    if (((PyDapChainDatumObject*)self)->datum->header.type_id == DAP_CHAIN_DATUM_TOKEN ){
        PyDapChainDatumTokenObject *obj_token = PyObject_New(PyDapChainDatumTokenObject,
                                                             &DapChainDatumTokenObjectType);
        size_t l_size_token = ((PyDapChainDatumObject*)self)->datum->header.data_size;
        obj_token->token = dap_chain_datum_token_read(((PyDapChainDatumObject*)self)->datum->data,
                                                      &l_size_token);
        obj_token->copy = true;
        return (PyObject*)obj_token;
    }else{
        PyErr_SetString(PyExc_Exception, "Due to the type of this datum, it is not possible to get the token datum.");
        return NULL;
    }
}

PyObject *dap_chain_datum_is_type_emission(PyObject *self, PyObject *args){
    (void)args;
    if (((PyDapChainDatumObject*)self)->datum->header.type_id == DAP_CHAIN_DATUM_TOKEN_EMISSION){
        Py_RETURN_TRUE;
    }else{
        Py_RETURN_FALSE;
    }
}

PyObject *wrapping_dap_chain_datum_get_datum_token_emission(PyObject *self, PyObject *args){
    (void)args;
    if (((PyDapChainDatumObject*)self)->datum->header.type_id == DAP_CHAIN_DATUM_TOKEN_EMISSION) {
        size_t l_token_emission_size = ((PyDapChainDatumObject*)self)->datum->header.data_size;
        dap_chain_datum_token_emission_t *l_token_emission =
                dap_chain_datum_emission_read(((PyDapChainDatumObject*)self)->datum->data, &l_token_emission_size);
        if ((void*)l_token_emission->tsd_n_signs + l_token_emission->data.type_auth.tsd_total_size
                > (void*)l_token_emission + l_token_emission_size)
        {
            /*char *l_strerr = dap_strdup_printf("Malformed datum type '%d', TSD sections are out-of-buf (%lu > %lu)",
                                               l_token_emission->hdr.type, l_token_emission->data.type_auth.tsd_total_size,
                                               l_token_emission_size);
            PyErr_SetString(PyExc_ValueError, l_strerr);
            DAP_DELETE(l_strerr);
            DAP_DELETE(l_token_emission);
            return NULL;*/
            log_it(L_ERROR, "Malformed datum type '%d', TSD sections are out-of-buf (%lu > %lu)",
                   l_token_emission->hdr.type, l_token_emission->data.type_auth.tsd_total_size,
                   l_token_emission_size);
            
            DAP_DELETE(l_token_emission);
            Py_RETURN_NONE;
        }
        PyDapChainDatumTokenEmissionObject *obj_emission = PyObject_New(
                PyDapChainDatumTokenEmissionObject,
                &DapChainDatumTokenEmissionObjectType
                );
        obj_emission->token_emission = l_token_emission;
        obj_emission->token_size = l_token_emission_size;
        obj_emission->copy = true;
        return (PyObject*)obj_emission;

    } else {
        PyErr_SetString(PyExc_Exception, "Incorrect of a datum type. Can't get a token datum");
        return NULL;
    }
}

PyObject *wrapping_dap_chain_datum_is_type_custom(PyObject *self, PyObject *args){
    (void)args;
    if (((PyDapChainDatumObject*)self)->datum->header.type_id == DAP_CHAIN_DATUM_CUSTOM)
        Py_RETURN_TRUE;
    else
        Py_RETURN_FALSE;
}

PyObject *wrapping_dap_chain_datum_get_datum_tx(PyObject *self, PyObject *args){
    PyObject *obj_net;
    if(((PyDapChainDatumObject *)self)->datum->header.type_id == DAP_CHAIN_DATUM_TX){
        PyDapChainDatumTxObject *obj_datum_tx = PyObject_New(PyDapChainDatumTxObject, &DapChainDatumTxObjectType);

        dap_chain_datum_tx_t *l_datum_tx = (dap_chain_datum_tx_t *)((PyDapChainDatumObject*)self)->datum->data;
        obj_datum_tx->datum_tx = DAP_DUP_SIZE( l_datum_tx, dap_chain_datum_tx_get_size(l_datum_tx));
                                                                                                                                        ;
        obj_datum_tx->original = false; //destructor delets this in case of !original for some reason
        return (PyObject*)obj_datum_tx;
    }else{
        PyErr_SetString(PyExc_Exception, "Due to the type of this datum, it is not possible to get the transaction datum.");
        return NULL;
    }
}

PyObject *dap_chain_datum_get_type_str_py(PyObject *self, PyObject *args){
    (void)args;
    const char *l_ret;
    DAP_DATUM_TYPE_STR(((PyDapChainDatumObject*)self)->datum->header.type_id, l_ret);
    if (l_ret == NULL)
        Py_RETURN_NONE;
    return Py_BuildValue("s", l_ret);
}

PyObject *wrapping_dap_chain_datum_get_type_id_py(PyObject *self, PyObject *args){
    (void)args;
    return Py_BuildValue("H", ((PyDapChainDatumObject*)self)->datum->header.type_id);
}

PyObject *wrapping_dap_chain_datum_get_hash_py(PyObject *self, void* closure){
    (void)closure;
    PyDapHashFastObject *obj_hf = PyObject_New(PyDapHashFastObject,  &DapChainHashFastObjectType);
    obj_hf->hash_fast = DAP_NEW(dap_hash_fast_t);
    dap_hash_fast(
            ((PyDapChainDatumObject*)self)->datum->data,
            ((PyDapChainDatumObject*)self)->datum->header.data_size,
            obj_hf->hash_fast);
    obj_hf->origin = true;
    return (PyObject*)obj_hf;
}

PyObject *wrapping_dap_chain_datum_get_version_str_py(PyObject *self, void* closure){
    (void)closure;
    char *l_version = dap_strdup_printf("0x%02X",((PyDapChainDatumObject*)self)->datum->header.version_id);
    PyObject *l_obj_version = Py_BuildValue("s", l_version);
    DAP_FREE(l_version);
    return l_obj_version;
}

PyObject *wrapping_dap_chain_datum_get_raw_py(PyObject *self, void* closure){
    (void)closure;
    size_t l_size = dap_chain_datum_size(((PyDapChainDatumObject*)self)->datum);
    PyObject *obj_bytes = PyBytes_FromStringAndSize(
            (char*)((PyDapChainDatumObject*)self)->datum,
            (Py_ssize_t)l_size);
    return obj_bytes;
}

PyObject *wrapping_dap_chain_datum_get_data_raw_py(PyObject *self, void* closure){
    (void)closure;
    PyObject *obj_bytes = PyBytes_FromStringAndSize(
            (char*)((PyDapChainDatumObject*)self)->datum->data,
            ((PyDapChainDatumObject*)self)->datum->header.data_size);
    return obj_bytes;
}

PyObject *wrapping_dap_chain_datum_is_type_decree(PyObject *self, PyObject *args) {
    (void)args;
    if (((PyDapChainDatumObject*)self)->datum->header.type_id == DAP_CHAIN_DATUM_DECREE)
        Py_RETURN_TRUE;
    else
        Py_RETURN_FALSE;
}
PyObject *wrapping_dap_chain_datum_get_decree(PyObject *self, PyObject *args) {
    (void)args;
    PyDapChainDatumDecreeObject *obj_decree = PyObject_New(PyDapChainDatumDecreeObject, &DapChainDatumDecreeObjectType);
    size_t l_data_size = ((PyDapChainDatumObject*)self)->datum->header.data_size;
    obj_decree->decree = DAP_NEW_Z_SIZE(dap_chain_datum_decree_t, l_data_size);
    memcpy(obj_decree->decree, ((PyDapChainDatumObject*)self)->datum->data, l_data_size);
    return (PyObject*)obj_decree;
}
PyObject *wrapping_dap_chain_datum_is_type_anchor(PyObject *self, PyObject *args) {
    (void)args;
    if (((PyDapChainDatumObject*)self)->datum->header.type_id == DAP_CHAIN_DATUM_ANCHOR)
        Py_RETURN_TRUE;
    else
        Py_RETURN_FALSE;
}
PyObject *wrapping_dap_chain_datum_get_anchor(PyObject *self, PyObject *args) {
    (void)args;
    PyDapChainDatumAnchorObject *obj_anchor = PyObject_New(PyDapChainDatumAnchorObject, &DapChainDatumAnchorObjectType);
    obj_anchor->anchor = (dap_chain_datum_anchor_t*)((PyDapChainDatumObject*)self)->datum->data;
    return (PyObject*)obj_anchor;
}

PyObject *wrapping_dap_chain_datum_create_from_bytes(PyObject *self, PyObject *args){
    (void)self;
    PyObject *obj_bytes;
    if (!PyArg_ParseTuple(args, "O", &obj_bytes)){
        return NULL;
    }
    if (!PyBytes_Check(obj_bytes)){
        PyErr_SetString(PyExc_AttributeError, "An invalid attribute was passed to the function. An "
                                              "object of type Bytes is required.");
        return NULL;
    }
    size_t l_bytes_size = PyBytes_Size(obj_bytes);
    PyDapChainDatumObject *obj_datum = PyObject_New(PyDapChainDatumObject, &DapChainDatumObjectType);
    obj_datum->datum = DAP_NEW_Z_SIZE(dap_chain_datum_t, l_bytes_size);
    void *l_btd = PyBytes_AsString(obj_bytes);
    memcpy(obj_datum->datum, l_btd, l_bytes_size);
    obj_datum->origin = true;
    return (PyObject*)obj_datum;
}

/* DAP chain datum iter */
PyTypeObject DapChainDatumIterObjectType = DAP_PY_TYPE_OBJECT(
        "CellFrame.Chain.DatumIter", sizeof(PyDapChainDatumIterObject),
        "Chain datum iter object");
