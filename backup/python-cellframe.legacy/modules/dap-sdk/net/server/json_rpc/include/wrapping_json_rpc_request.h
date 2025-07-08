#pragma once
#include <Python.h>
#include "wrapping_dap_http_simple.h"
#include "uthash.h"
#include "dap_common.h"
#include "dap_strfuncs.h"
#include "dap_json_rpc_request_handler.h"
#include "dap_json_rpc_params.h"
#include "wrapping_json_rpc_response.h"
#include "python-cellframe_common.h"
//#include "wrapping_dap_json_rpc_

#ifdef __cplusplus
extern "C" {
#endif

typedef struct PyDAPJsonRPCRequest {
    PyObject_HEAD
    dap_json_rpc_request_t *request;
} PyDAPJsonRPCRequestObject;

struct _w_json_rpc_handler{
    char *method;
    PyObject *call_func;
    UT_hash_handle hh;
};

PyObject* dap_json_roc_request_send_py(PyObject *self, PyObject *args);
PyObject* dap_json_rpc_request_reg_handler_py(PyObject *self, PyObject *args);

extern PyTypeObject DapJsonRpcRequestObjectType;

#ifdef __cplusplus
}
#endif
