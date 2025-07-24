/*
 * Python DAP HTTP Module Header  
 * HTTP client function wrappers around DAP SDK
 */

#ifndef PYTHON_DAP_HTTP_H
#define PYTHON_DAP_HTTP_H

#define PY_SSIZE_T_CLEAN
#include <Python.h>

// HTTP client management functions
PyObject* dap_http_client_init_wrapper(PyObject* self, PyObject* args);
PyObject* dap_http_client_deinit_wrapper(PyObject* self, PyObject* args);
PyObject* dap_http_client_new_wrapper(PyObject* self, PyObject* args);
PyObject* dap_http_client_delete_wrapper(PyObject* self, PyObject* args);
PyObject* dap_http_get_all_clients_wrapper(PyObject* self, PyObject* args);

// HTTP client request functions
PyObject* dap_http_client_request_wrapper(PyObject* self, PyObject* args);
PyObject* dap_http_client_request_ex_wrapper(PyObject* self, PyObject* args);
PyObject* dap_http_simple_request_wrapper(PyObject* self, PyObject* args);

// HTTP client configuration functions
PyObject* dap_http_client_set_headers_wrapper(PyObject* self, PyObject* args);
PyObject* dap_http_client_set_timeout_wrapper(PyObject* self, PyObject* args);

// HTTP client response functions
PyObject* dap_http_client_get_response_code_wrapper(PyObject* self, PyObject* args);
PyObject* dap_http_client_get_response_size_wrapper(PyObject* self, PyObject* args);
PyObject* dap_http_client_get_response_data_wrapper(PyObject* self, PyObject* args);
PyObject* dap_http_client_get_response_headers_wrapper(PyObject* self, PyObject* args);

// HTTP request object functions
PyObject* dap_http_request_new_wrapper(PyObject* self, PyObject* args);
PyObject* dap_http_request_delete_wrapper(PyObject* self, PyObject* args);
PyObject* dap_http_request_add_header_wrapper(PyObject* self, PyObject* args);
PyObject* dap_http_request_set_body_wrapper(PyObject* self, PyObject* args);
PyObject* dap_http_request_set_method_wrapper(PyObject* self, PyObject* args);
PyObject* dap_http_request_set_url_wrapper(PyObject* self, PyObject* args);

// HTTP response object functions
PyObject* dap_http_response_new_wrapper(PyObject* self, PyObject* args);
PyObject* dap_http_response_delete_wrapper(PyObject* self, PyObject* args);
PyObject* dap_http_response_get_code_wrapper(PyObject* self, PyObject* args);
PyObject* dap_http_response_get_data_wrapper(PyObject* self, PyObject* args);
PyObject* dap_http_response_get_headers_wrapper(PyObject* self, PyObject* args);
PyObject* dap_http_response_get_header_wrapper(PyObject* self, PyObject* args);

// Method definitions array for Python module
extern PyMethodDef dap_http_methods[];

#endif // PYTHON_DAP_HTTP_H 