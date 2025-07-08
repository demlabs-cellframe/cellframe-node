#pragma once

#include "Python.h"
#include "dap_chain_net_srv.h"
#include "dap_chain_net_srv_stream_session.h"
#include "uthash.h"
#include "wrapping_dap_chain_common.h"
#include "wrapping_dap_chain_net_srv_client_remote.h"
#include "python-cellframe_common.h"

typedef struct PyDapChainNetSrv{
    PyObject_HEAD
    dap_chain_net_srv_t *srv;
    PyObject *callbackRequested;
    PyObject *callbackSuccess;
    PyObject *callbackError;
    PyObject *callbackReceiptNext;
    PyObject *callbackReadWithOutData;
}PyDapChainNetSrvObject;

int PyDapChainNetSrv_init(PyDapChainNetSrvObject* self, PyObject *args, PyObject *kwds);
void PyDapChainNetSrv_dealloc(PyDapChainNetSrvObject* self);

PyObject *wrapping_dap_chain_net_srv_get_uid(PyObject *self, void *closure);
PyObject *wrapping_dap_chain_net_srv_get_abstract(PyObject *self, void *closure);
PyObject *wrapping_dap_chain_net_srv_get_price_list(PyObject *self, void *closure);
PyObject *wrapping_dap_chain_net_srv_get_ban_list(PyObject *self, void *closure);
PyObject *wrapping_dap_chain_net_srv_get_grace_period(PyObject *self, void *closure);


//Function
PyObject *wrapping_dap_chain_net_srv_set_callback_channel(PyObject *self, PyObject *args);
//PyObject *wrapping_dap_chain_net_srv_issue_receipt(PyObject *self, PyObject *args);

extern PyTypeObject DapChainNetSrvObjectType;
