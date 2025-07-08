#include "libdap-python.h"
#include "wrapping_dap_global_db.h"
#include "dap_events.h"
#include "dap_proc_thread.h"

static PyMethodDef DapGlobalDBMethods[] = {
        {"get", (PyCFunction)wrapping_dap_global_db_gr_get, METH_VARARGS | METH_STATIC, ""},
        {"set", (PyCFunction)wrapping_dap_global_db_gr_set, METH_VARARGS | METH_STATIC, ""},
        {"set_sync", (PyCFunction)wrapping_dap_global_db_gr_set_sync, METH_VARARGS | METH_STATIC, ""},
        {"delete", (PyCFunction)wrapping_dap_global_db_gr_del, METH_VARARGS | METH_STATIC, ""},
        {"pin", (PyCFunction)wrapping_dap_global_db_gr_pin, METH_VARARGS | METH_STATIC, ""},
        {"unpin", (PyCFunction)wrapping_dap_global_db_gr_unpin, METH_VARARGS | METH_STATIC, ""},
        {"grLoad", (PyCFunction)wrapping_dap_global_db_gr_load, METH_VARARGS | METH_STATIC, ""},
        {NULL, NULL, 0, NULL}
};

PyTypeObject DapGlobalDBObjectType = DAP_PY_TYPE_OBJECT(
        "DAP.GlobalDB.DB", sizeof(PyDapGlobalDBObject),
        "GlobalDB.DB object",
        .tp_methods = DapGlobalDBMethods);

PyObject *wrapping_dap_global_db_gr_get(PyObject *self, PyObject *args){
    (void)self;
    const char *l_key;
    const char *l_group;
    if (!PyArg_ParseTuple(args, "ss", &l_key, &l_group)){
        return NULL;
    }
    size_t l_size_data = 0;
    void *l_bytes = dap_global_db_get_sync(l_group, l_key, &l_size_data, NULL, NULL);
    if (l_size_data == 0)
        Py_RETURN_NONE;
    PyObject *l_obj_bytes = PyBytes_FromStringAndSize(l_bytes, (Py_ssize_t)l_size_data);
    DAP_DELETE(l_bytes);
    return l_obj_bytes;
}

/**
 * @brief wrapping_dap_global_db_gr_set
 * @param self
 * @param args
 * @return
 */
PyObject *wrapping_dap_global_db_gr_set(PyObject *self, PyObject *args){
    (void)self;
    char *l_key;
    char *l_group;
    bool l_is_pinned = false;
    PyObject *obj_byte;
    if (!PyArg_ParseTuple(args, "ssO|p", &l_key, &l_group, &obj_byte, &l_is_pinned)){
        return NULL;
    }
    if (!PyBytes_Check(obj_byte)){
        PyErr_SetString(PyExc_AttributeError, "In the set function of the globalDB object, the third "
                                              "argument must take an object of type bytes.");
        return NULL;
    }
    void *l_bytes = PyBytes_AsString(obj_byte);
    size_t l_bytes_size = PyBytes_Size(obj_byte);
    int ret = dap_global_db_set(l_group, l_key, l_bytes, l_bytes_size, l_is_pinned, NULL, NULL);
    if (ret == DAP_GLOBAL_DB_RC_SUCCESS) {
        Py_RETURN_TRUE;
    } else {
        Py_RETURN_FALSE;
    }
}

/**
 * @brief wrapping_dap_global_db_gr_set_sync
 * @param self
 * @param args
 * @return
 */
PyObject *wrapping_dap_global_db_gr_set_sync(PyObject *self, PyObject *args){
    (void)self;
    char *l_key;
    char *l_group;
    bool l_is_pinned = false;
    PyObject *obj_byte;
    if (!PyArg_ParseTuple(args, "ssO|p", &l_key, &l_group, &obj_byte, &l_is_pinned)){
        return NULL;
    }
    if (!PyBytes_Check(obj_byte)){
        PyErr_SetString(PyExc_AttributeError, "In the set function of the globalDB object, the third "
                                              "argument must take an object of type bytes.");
        return NULL;
    }
    void *l_bytes = PyBytes_AsString(obj_byte);
    size_t l_bytes_size = PyBytes_Size(obj_byte);
    int ret = dap_global_db_set_sync(l_group, l_key, l_bytes, l_bytes_size, l_is_pinned);
    if (ret == DAP_GLOBAL_DB_RC_SUCCESS) {
        Py_RETURN_TRUE;
    } else {
        Py_RETURN_FALSE;
    }
}

/**
 * @brief wrapping_dap_global_db_gr_del
 * @param self
 * @param args
 * @return
 */
PyObject *wrapping_dap_global_db_gr_del(PyObject *self, PyObject *args){
    (void)self;
    const char *l_key;
    const char *l_group;
    if (!PyArg_ParseTuple(args, "ss",&l_key, &l_group)){
        return NULL;
    }
    int ret = dap_global_db_del(l_group, l_key, NULL, NULL);
    if (ret == DAP_GLOBAL_DB_RC_SUCCESS)
        Py_RETURN_TRUE;
    else
        Py_RETURN_FALSE;
}

PyObject *wrapping_dap_global_db_gr_pin(PyObject *self, PyObject *args){
    (void)self;
    char *l_key;
    char *l_group;
    if (!PyArg_ParseTuple(args, "ss", &l_key, &l_group)){
        return NULL;
    }

    int ret = dap_global_db_pin(l_group, l_key, NULL, NULL);
    if (ret == DAP_GLOBAL_DB_RC_SUCCESS)
        Py_RETURN_TRUE;
    else
        Py_RETURN_FALSE;
}

PyObject *wrapping_dap_global_db_gr_unpin(PyObject *self, PyObject *args){
    (void)self;
    char *l_key;
    char *l_group;

    if (!PyArg_ParseTuple(args, "ss", &l_key, &l_group)){
        return NULL;
    }

    int ret = dap_global_db_unpin(l_group, l_key, NULL, NULL);
    if (ret == DAP_GLOBAL_DB_RC_SUCCESS)
        Py_RETURN_TRUE;
    else
        Py_RETURN_FALSE;
}


PyObject *wrapping_dap_global_db_gr_load(PyObject *self, PyObject *args){
    (void)self;
    char *l_group;
    if (!PyArg_ParseTuple(args, "s", &l_group)){
        return NULL;
    }
    size_t l_data_out = 0;
    dap_global_db_obj_t *l_db_obj = dap_global_db_get_all_sync(l_group, &l_data_out);
    PyObject* l_list = PyList_New(l_data_out);
    for (size_t i = 0; i < l_data_out; i++){
        PyDapGlobalDBContainerObject *l_obj = PyObject_New(PyDapGlobalDBContainerObject ,
                                                                &DapGlobalDBContainerObjectType);
        l_obj->obj = l_db_obj[i];
        PyList_SetItem(l_list, i, (PyObject*)l_obj);
    }

    DAP_DELETE(l_db_obj); 
    
    return l_list;
}
