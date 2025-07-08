//
// Created by blus on 05.02.2022.
//

#include "Python.h"
#include "datetime.h"
#include "dap_chain_net_srv.h"

#ifndef WRAPPING_DAP_CHAIN_NET_SRV_CLIENT_REMOTE_H
#define WRAPPING_DAP_CHAIN_NET_SRV_CLIENT_REMOTE_H

typedef struct PyDapChainNetSrvClientRemote{
    PyObject_HEAD
    dap_chain_net_srv_client_remote_t *srv_client_remote;
}PyDapChainNetSrvClientRemoteObject;

PyObject *wrapping_dap_chain_net_srv_client_remote_get_ch(PyObject *self, void *closure);
PyObject *wrapping_dap_chain_net_srv_client_remote_get_ts_created(PyObject *self, void *closure);
PyObject *wrapping_dap_chain_net_srv_client_remote_get_created(PyObject *self, void *closure);
PyObject *wrapping_dap_chain_net_srv_client_remote_get_stream_worker(PyObject *self, void *closure);
PyObject *wrapping_dap_chain_net_srv_client_remote_get_session_id(PyObject *self, void *closure);
PyObject *wrapping_dap_chain_net_srv_client_remote_get_bytes_received(PyObject *self, void *closure);
PyObject *wrapping_dap_chain_net_srv_client_remote_get_bytes_send(PyObject *self, void *closure);
//PyObject *wrapping_dap_chain_net_srv_client_remote_get_bytes_prev(PyObject *self, void *closure);
//PyObject *wrapping_dap_chain_net_srv_client_remote_get_bytes_next(PyObject *self, void *closure);

extern PyTypeObject DapChainNetSrvClientRemoteObject_DapChainNetSrvClientRemoteObjectType;

#endif //WRAPPING_DAP_CHAIN_NET_SRV_CLIENT_REMOTE_H

