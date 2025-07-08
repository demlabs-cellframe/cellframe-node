#pragma once
#include <Python.h>
#include "dap_client_http.h"
#include "utlist.h"

typedef struct PyDapClientHttp
{
    PyObject_HEAD
    dap_client_http_t *client_http;
}PyDapClientHttpObject;

void PyDapClientHttp_deinit(PyDapClientHttpObject *self);
int PyDapClientHttp_create(PyObject *self, PyObject *argv, PyObject *kwds);

PyObject *wrapping_dap_client_http_get_connect_timeout_ms(PyObject *self, PyObject *argv);

extern PyTypeObject DapClientHttpObjectType;
