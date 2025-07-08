#pragma once

#include "dap_common.h"
#include "dap_enc_http.h"
#include "dap_server_python.h"
#include "dap_http_server.h"
#include "dap_http_simple.h"
#include "wrapping_dap_http_simple.h"
#include "Python.h"

typedef struct PyDapEncServer{
    PyObject_HEAD
    enc_http_delegate_t *enc_http_delegate;
}PyDapEncServerObject;

PyObject *enc_http_reply_py(PyObject *self, PyObject *args);
PyObject *enc_http_request_decode_py(PyObject *self, PyObject *args);
PyObject *enc_http_is_null_py(PyObject *self, PyObject *args);
PyObject *enc_http_reply_encode_py(PyObject *self, PyObject *args);
void enc_http_delegate_delete_py(PyObject *self);
PyObject *enc_http_add_proc_py(PyObject *self, PyObject *args);

PyObject *enc_http_get_action_py(PyDapEncServerObject *self, void *clouser);
PyObject *enc_http_get_request_py(PyDapEncServerObject *self, void *clouser);
PyObject *enc_http_get_url_path_py(PyDapEncServerObject *self, void *clouser);
PyObject *enc_http_get_in_query_py(PyDapEncServerObject *self, void *clouser);

extern PyTypeObject DapEncServerObjectType;
