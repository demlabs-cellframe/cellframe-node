#pragma once

#include "Python.h"
#include "dap_chain_net_srv_client.h"
#include "dap_chain_node_client.h"
#include "libdap_chain_net_python.h"

typedef struct PyDapChainNetSrvClient{
    PyObject_HEAD
    dap_chain_net_srv_client_t *srv_client;
    
    PyObject *callback_connected;
    PyObject *callback_disconnected;
    PyObject *callback_check;
    PyObject *callback_sign;
    PyObject *callback_success;
    PyObject *callback_error;
    PyObject *callback_data;
    
}PyDapChainNetSrvClientObject;

int PyDapChainNetSrvClient_init(PyDapChainNetSrvClientObject* self, PyObject *args, PyObject *kwds);
void PyDapChainNetSrvClient_dealloc(PyDapChainNetSrvClientObject* self);

PyObject *wrapping_dap_chain_net_srv_client_check(PyObject *self, PyObject *args);
PyObject *wrapping_dap_chain_net_srv_client_request(PyObject *self, PyObject *args);
PyObject *wrapping_dap_chain_net_srv_client_write(PyObject *self, PyObject *args);
PyObject *wrapping_dap_chain_net_srv_client_close(PyObject *self, void *closure);

extern PyTypeObject DapChainNetSrvClientObjectType;
