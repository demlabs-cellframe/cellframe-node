#pragma once
#include "Python.h"
#include "dap_json_rpc_response.h"

typedef struct PyDapJSONRPCResponse{
    PyObject_HEAD
    dap_json_rpc_response_t *response;
}PyDapJSONRPCResponseObject;

int wrapping_json_rpc_response_set_result(PyObject *self, PyObject *args, void *closure);
PyObject *wrapping_json_rpc_response_get_result(PyObject *self, void *closure);
PyObject *wrapping_json_rpc_response_get_error(PyObject *self, void *closure);
int wrapping_json_rpc_response_set_error(PyObject *self, PyObject *args, void *closure);
PyObject *wrapping_json_rpc_response_get_id(PyObject *self, void *closure);

extern PyTypeObject DapJsonRpcResponseobjectType;
