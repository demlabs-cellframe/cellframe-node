#pragma once

#include "Python.h"
#include "dap_chain_net_srv_order.h"
#include "wrapping_dap_chain_common.h"
#include "libdap_chain_net_python.h"
#include "wrapping_dap_chain_net_srv_common.h"
#include "datetime.h"
#include "libdap_crypto_key_python.h"

typedef struct PyDapChainNetSrvOrder{
    PyObject_HEAD
    dap_chain_net_srv_order_t *order;
}PyDapChainNetSrvOrderObject;

//constructor
int PyDapChainNetSrvOrder_init(PyDapChainNetSrvOrderObject *self, PyObject *args, PyObject *kwds);

//Attributes
PyObject *wrapping_dap_chain_net_srv_order_get_version(PyObject *self, void *closure);
PyObject *wrapping_dap_chain_net_srv_order_get_srv_uid(PyObject *self, void *closure);
PyObject *wrapping_dap_chain_net_srv_order_get_srv_direction(PyObject *self, void *closure);
PyObject *wrapping_dap_chain_net_srv_order_get_srv_node_addr(PyObject *self, void *closure);
PyObject *wrapping_dap_chain_net_srv_order_get_srv_tx_cond_hash(PyObject *self, void *closure);
PyObject *wrapping_dap_chain_net_srv_order_get_srv_price_unit(PyObject *self, void *closure);
PyObject *wrapping_dap_chain_net_srv_order_get_srv_ts_created(PyObject *self, void *closure);
PyObject *wrapping_dap_chain_net_srv_order_get_srv_ts_expires(PyObject *self, void *closure);
PyObject *wrapping_dap_chain_net_srv_order_get_srv_price(PyObject *self, void *closure);
PyObject *wrapping_dap_chain_net_srv_order_get_srv_price_ticker(PyObject *self, void *closure);
//PyObject *wrapping_dap_chain_net_srv_order_get_srv_free_space(PyObject *self, void *closure);
PyObject *wrapping_dap_chain_net_srv_order_get_srv_ext_size(PyObject *self, void *closure);
PyObject *wrapping_dap_chain_net_srv_order_get_srv_ext_n_sign(PyObject *self, void *closure);
//Functions
PyObject *wrapping_dap_chain_net_srv_order_get_size(PyObject *self, PyObject *args);
//PyObject *wrapping_dap_chain_net_srv_order_set_continent_region(PyObject *self, PyObject *args);
//PyObject *wrapping_dap_chain_net_srv_order_get_continent_region(PyObject *self, PyObject *args);

//PyObject *wrapping_dap_chain_net_srv_order_get_country_code(PyObject *self, PyObject *args);
//PyObject *wrapping_dap_chain_net_srv_order_continents_count(PyObject *self, PyObject *args);
//PyObject *wrapping_dap_chain_net_srv_order_continent_to_str(PyObject *self, PyObject *args);
//PyObject *wrapping_dap_chain_net_srv_order_continent_to_num(PyObject *self, PyObject *args);

PyObject *wrapping_dap_chain_net_srv_order_find(PyObject *self, PyObject *args);
PyObject *wrapping_dap_chain_net_srv_order_delete(PyObject *self, PyObject *args);

PyObject *wrapping_dap_chain_net_srv_order_find_all_by(PyObject *self, PyObject *args);
PyObject *wrapping_dap_chain_net_srv_order_save(PyObject *self, PyObject *args);
PyObject *wrapping_dap_chain_net_srv_order_get_gdb_group(PyObject *self, PyObject *args);
PyObject *wrapping_dap_chain_net_srv_order_add_notify_callback(PyObject *self, PyObject *args);

extern PyTypeObject DapChainNetSrvOrderObjectType;
