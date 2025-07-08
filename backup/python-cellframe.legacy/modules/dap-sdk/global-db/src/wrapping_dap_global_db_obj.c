#include "libdap-python.h"
#include "wrapping_dap_global_db_obj.h"

static PyGetSetDef DapGlobalDBContainerGetSet[] = {
        {"key", (getter)wrapping_dap_global_db_obj_get_key, NULL, NULL, NULL},
        {"value", (getter)wrapping_dap_global_db_obj_get_value, NULL, NULL, NULL},
        {NULL}
};

void PyDapGlobalDBObject_dealloc(PyObject *self) {
    
    DAP_DEL_Z(((PyDapGlobalDBContainerObject*)self)->obj.key);
    DAP_DEL_Z(((PyDapGlobalDBContainerObject*)self)->obj.value);
    PyTypeObject *tp = Py_TYPE(self);
    tp->tp_free(self);
}

PyTypeObject DapGlobalDBContainerObjectType = DAP_PY_TYPE_OBJECT(
        "DAP.GlobalDB.Container", sizeof(PyDapGlobalDBContainerObject),
        "GlobalDB container object",
        .tp_getset = DapGlobalDBContainerGetSet,
        .tp_dealloc = PyDapGlobalDBObject_dealloc
        );

PyObject *wrapping_dap_global_db_obj_get_key(PyObject *self, void *closure){
    (void)closure;
    return Py_BuildValue("s", ((PyDapGlobalDBContainerObject*)self)->obj.key);
}
PyObject *wrapping_dap_global_db_obj_get_value(PyObject *self, void *closure){
    (void)closure;
    size_t l_size_value = ((PyDapGlobalDBContainerObject*)self)->obj.value_len;
    if (l_size_value == 0 || !((PyDapGlobalDBContainerObject*)self)->obj.value){
        Py_RETURN_NONE;
    }
    PyObject *obj_bytes = PyBytes_FromStringAndSize((char *)((PyDapGlobalDBContainerObject*)self)->obj.value, l_size_value);
    return obj_bytes;
}

