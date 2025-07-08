#include <Python.h>
#include "dap_http_header.h"

typedef struct PyDapHttpHeader{
    PyObject_HEAD
    dap_http_header_t *header;
    dap_http_header_t *tmp_iter;
    bool root_obj;
}PyDapHttpHeaderObject;

PyObject *wrapping_dap_http_header_get_name(PyObject *self, void *closure);
PyObject *wrapping_dap_http_header_get_value(PyObject *self, void *closure);
PyObject *wrapping_dap_http_header_append(PyObject *self, PyObject *args);

PyObject *DapHttpHeaderObject_new(PyTypeObject *type_object, PyObject *args, PyObject *kwds);
void DapHttpHeaderObject_dealloc(void *self);
PyObject *DapHttpHeaderObject_GetIter(PyObject *self);
PyObject *DapHttpHeaderObject_GetNext(PyObject *self);
PyObject *DapHttpHeaderObject_ToStr(PyObject *self);

extern PyTypeObject DapHttpHeaderObjectType;
