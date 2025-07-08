#include"libdap-python.h"
#include "wrapping_http.h"

static PyMethodDef DapHttpMethods[] = {
        {"new", dap_http_new_py, METH_VARARGS | METH_STATIC, ""},
        {}
};

PyTypeObject DapHttpObjectType = DAP_PY_TYPE_OBJECT(
        "DAP.Net.Http", sizeof(PyDapHttpObject),
        "Dap Http object",
        .tp_methods = DapHttpMethods);

PyObject *dap_http_new_py(PyObject *self, PyObject *args){
    PyErr_SetString(PyExc_AttributeError, "python http dap_server not implemented!");
    return NULL;
}
