#pragma once

#include "Python.h"
#include "dap_chain_net_srv.h"
#include "wrapping_dap_chain_common.h"
#include "libdap_chain_net_python.h"

/*wrapping dap_chain_net_srv_price*/
typedef struct PyDapChainNetSrvPrice{
    PyObject_HEAD
    dap_chain_net_srv_price_t price;
}PyDapChainNetSrvPriceObject;

PyObject *wrapping_dap_chain_net_srv_get_wallet(PyObject *self, void *closure);
PyObject *wrapping_dap_chain_net_srv_get_net_name(PyObject *self, void *closure);
PyObject *wrapping_dap_chain_net_srv_get_net(PyObject *self, void *closure);
PyObject *wrapping_dap_chain_net_srv_get_value_datoshi(PyObject *self, void *closure);
PyObject *wrapping_dap_chain_net_srv_get_token(PyObject *self, void *closure);
PyObject *wrapping_dap_chain_net_srv_get_units(PyObject *self, void *closure);
PyObject *wrapping_dap_chain_net_srv_get_units_uid(PyObject *self, void *closure);

extern PyTypeObject DapChainNetSrvPriceObjectType;

/*wrapping dap_chain_net_srv_order_direction*/
typedef struct PyDapChainNetSrvOrderDirection{
    PyObject_HEAD
    dap_chain_net_srv_order_direction_t direction;
}PyDapChainNetSrvOrderDirectionObject;

PyObject *DapChainNetSrvOrderDirection_str(PyObject *self);

PyObject *wrapping_dap_chain_net_srv_order_direction_get_serv_dir_buy(PyObject *self, PyObject *args);
PyObject *wrapping_dap_chain_net_srv_order_direction_get_serv_dir_sell(PyObject *self, PyObject *args);
PyObject *wrapping_dap_chain_net_srv_order_direction_get_serv_dir_undefined(PyObject *self, PyObject *args);

extern PyTypeObject DapChainNetSrvOrderDirectionObjectType;
