#pragma once

#include "dap_common.h"
#include "dap_strfuncs.h"
#include "dap_http_simple.h"
#include "Python.h"
#include "wrapping_http.h"
#include "wrapping_http_status_code.h"
#include "uthash.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct PyDapHttpSimple{
    PyObject_HEAD
    dap_http_simple_t *sh;
    PyObject *response_http_header;
}PyDapHttpSimpleObject;

PyObject *dap_http_simple_add_proc_py(PyObject *self, PyObject *args);
PyObject *dap_http_simple_module_init_py(PyObject *self, PyObject *args);
PyObject *dap_http_simple_module_deinit_py(PyObject *self, PyObject *args);
PyObject *dap_http_simple_set_supported_user_agents_py(PyObject *self, PyObject *args);
PyObject *dap_http_simple_set_pass_unknown_user_agents_py(PyObject *self, PyObject *args);
PyObject *dap_http_simple_reply_py(PyObject *self, PyObject *args);
PyObject *dap_http_simple_set_flag_generate_default_header_py(PyObject *self, PyObject *args);
PyObject *dap_http_simple_get_response_headers(PyObject *self, PyObject *args);
PyObject *dap_http_simple_set_response_headers(PyObject *self, PyObject *args);
PyObject *dap_http_simple_http_headers_request(PyDapHttpSimpleObject *self, void *closure);

/* Attributes */
PyObject *dap_http_simple_method_py(PyDapHttpSimpleObject *self, void *clouser);
PyObject *dap_http_simple_request_py(PyDapHttpSimpleObject *self, void *clouser);
PyObject *dap_http_simple_url_path_py(PyDapHttpSimpleObject *self, void *clouser);
PyObject *dap_http_simple_query_py(PyDapHttpSimpleObject *self, void *clouser);
PyObject *dap_http_simple_ip_client_py(PyDapHttpSimpleObject *self, void *clouser);

extern PyTypeObject DapHttpSimpleObjectType;

#ifdef __cplusplus
}
#endif
