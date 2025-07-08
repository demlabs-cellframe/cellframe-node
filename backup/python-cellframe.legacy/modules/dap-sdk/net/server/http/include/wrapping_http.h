#ifndef _WRAPPING_HTTP_
#define _WRAPPING_HTTP_

#include <Python.h>
#include "dap_http_server.h"
#include "dap_server_python.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct PyDapHttp{
    PyObject_HEAD
    struct dap_http_server*http;
}PyDapHttpObject;

PyObject *dap_http_new_py(PyObject *self, PyObject *args);

extern PyTypeObject DapHttpObjectType;

#ifdef __cplusplus
}
#endif

#endif // _WRAPPING_HTTP_
