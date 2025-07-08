#include "wrapping_dap_http_header.h"
#include "python-cellframe_common.h"

#define PVT(a) ((PyDapHttpHeaderObject*)a)

static PyGetSetDef DapHttpHeaderGetSetDef[] = {
        {"name", (getter)wrapping_dap_http_header_get_name, NULL,  NULL, NULL},
        {"value", (getter)wrapping_dap_http_header_get_value, NULL, NULL, NULL},
        {}
};

static PyMethodDef DapHttpHeaderMethods[] = {
        {"append", wrapping_dap_http_header_append, METH_VARARGS, ""},
        {}
};

PyTypeObject  DapHttpHeaderObjectType = {
        .ob_base = PyVarObject_HEAD_INIT(NULL, 0)
        .tp_name = "DAP.Network.HTTP.Headers",
        .tp_basicsize = sizeof(PyDapHttpHeaderObject),
        .tp_dealloc = (destructor)DapHttpHeaderObject_dealloc,
        .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
        "This wrapper allows you to work with HTTP headers for HttpSimple.",
        .tp_getset = DapHttpHeaderGetSetDef,
        .tp_iter = DapHttpHeaderObject_GetIter,
        .tp_iternext = DapHttpHeaderObject_GetNext,
        .tp_methods = DapHttpHeaderMethods,
        .tp_str = DapHttpHeaderObject_ToStr,
        .tp_new = DapHttpHeaderObject_new
};

PyObject *wrapping_dap_http_header_get_name(PyObject *self, void *closure){
    (void)closure;
    return Py_BuildValue("s", PVT(self)->header->name);
}
PyObject *wrapping_dap_http_header_get_value(PyObject *self, void *closure){
    (void)closure;
    return Py_BuildValue("s", PVT(self)->header->value);
}

PyObject *DapHttpHeaderObject_new(PyTypeObject *type_object, PyObject *args, PyObject *kwds){
    char *obj_name;
    char *obj_value;
    const char *kwlist[] = {
            "name",
            "value",
            NULL
    };
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "ss", (char**)kwlist, &obj_name, &obj_value))
        return NULL;
    PyDapHttpHeaderObject *obj = (PyDapHttpHeaderObject*)PyType_GenericNew(type_object, args, kwds);
    obj->header = NULL;
    obj->root_obj = true;
    dap_http_header_add(&obj->header, obj_name, obj_value);
    Py_INCREF((PyObject*)obj);
    return (PyObject*)obj;
}

void DapHttpHeaderObject_dealloc(void *self){
    if (PVT(self)->root_obj) {
        for (dap_http_header_t *i = ((PyDapHttpHeaderObject *) self)->header; i; i = i->next) {
            dap_http_header_remove(&PVT(self)->header, i);
        }
    }
    Py_TYPE(self)->tp_free((PyObject *)self);
}

PyObject *DapHttpHeaderObject_GetIter(PyObject *self){
    Py_INCREF(self);
    PVT(self)->tmp_iter = PVT(self)->header;
    return self;
}
PyObject *DapHttpHeaderObject_GetNext(PyObject *self){
    dap_http_header_t *l_current = PVT(self)->tmp_iter;
    if (l_current) {
        PyDapHttpHeaderObject *obj = PyObject_New(PyDapHttpHeaderObject, &DapHttpHeaderObjectType);
        obj->header = l_current;
        obj->root_obj = false;
        PVT(self)->tmp_iter = l_current->next ? l_current->next : NULL;
        return (PyObject*)obj;
    } else {
        PyErr_SetNone(PyExc_StopIteration);
        PVT(self)->tmp_iter = PVT(self)->header;
//        Py_DECREF(self);
        return NULL;
    }
}

PyObject *wrapping_dap_http_header_append(PyObject *self, PyObject *args) {
    PyObject *obj_name_or_dapHTTP_Simple;
    char *value = NULL;
    dap_http_header_t **l_top = &PVT(self)->header;
    if (!PyArg_ParseTuple(args, "O|s", &obj_name_or_dapHTTP_Simple, &value))
        return NULL;
    if (PyObject_TypeCheck(obj_name_or_dapHTTP_Simple, &DapHttpHeaderObjectType)) {
        if (value) {
            PyErr_SetString(PyExc_AttributeError, "When setting the first argument as a "
                                                  "DAP.Network.HttpHeader object, the second argument is not set.");
            return NULL;
        }
        dap_http_header_add(&PVT(self)->header,
                            PVT(obj_name_or_dapHTTP_Simple)->header->name,
                            PVT(obj_name_or_dapHTTP_Simple)->header->value);
        Py_RETURN_NONE;
    }
    if (PyUnicode_Check(obj_name_or_dapHTTP_Simple)) {
        if (!value) {
            PyErr_SetString(PyExc_AttributeError, "The second argument was not specified. "
                                                  "The second argument must be the string value of the title.");
            return NULL;
        }
        const char *name = PyUnicode_AsUTF8(obj_name_or_dapHTTP_Simple);
        dap_http_header_add(&(PVT(self)->header), name, value);
        Py_RETURN_NONE;
    }
    PyErr_SetString(PyExc_AttributeError, "Invalid first argument specified. Only a string or an object "
                                          "of type DAP.Network.HttpHeader is accepted as the first argument.");
    return NULL;
}

PyObject *DapHttpHeaderObject_ToStr(PyObject *self) {
    if (!PVT(self)->header) {
        PyErr_SetString(PyExc_Exception, "Can't convert invalid HTTP header.");
    }
    char *l_str = dap_strdup_printf("%s:%s", PVT(self)->header->name, PVT(self)->header->value);
    PyObject *obj_str = PyUnicode_FromString(l_str);
    DAP_DELETE(l_str);
    return obj_str;
}
