#pragma once

#include "dap_common.h"
#include "http_status_code.h"
#include "Python.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct PyHTTPStatusCode{
    PyObject_HEAD
    http_status_code_t http_status;
}PyHttpStatusCodeObject;

PyObject *wrapping_http_status_code_set_py(PyObject *self, PyObject *args);

PyObject *wrapping_http_code_set_ok(PyObject *self, PyObject *args);

PyObject *wrapping_http_code_set_bad_request(PyObject *self, PyObject *args);

extern PyTypeObject DapHttpCodeObjectType;

#ifdef __cplusplus
}
#endif
