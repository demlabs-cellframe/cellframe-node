#pragma once

#include "dap_common.h"
#include "dap_server.h"
#include "dap_server_python.h"
#include "wrapping_http.h"
#include <Python.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dap_plugins_python_app_context{
    dap_server_t *server;
}dap_plugins_python_app_context_t;

int dap_plugins_python_app_content_init(dap_server_t *a_server);

typedef  struct PyDapAppContext{
    PyObject_HEAD
}PyDapAppContextObject;

PyObject *dap_plugins_python_app_context_get_server(PyObject *self, PyObject *args);
PyObject *dap_plugins_python_app_context_get_http(PyObject *self, PyObject *args);

extern PyTypeObject DapAppContextObjectType;

#ifdef __cplusplus
}
#endif
