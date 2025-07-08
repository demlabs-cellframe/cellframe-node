/*
 * Authors:
 * Alexey V. Stratulat <alexey.stratulat@demlabs.net>
 * DeM Labs Inc.   https://demlabs.net
 * CellFrame       https://cellframe.net
 * Sources         https://gitlab.demlabs.net/cellframe
 * Copyright  (c) 2017-2021
 * All rights reserved.

 This file is part of DAP (Distributed Applications Platform) the open source project

    DAP (Distributed Applications Platform) is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    DAP is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with any DAP based project.  If not, see <http://www.gnu.org/licenses/>.
*/

#ifndef _WRAPPING_DAP_NET_PYTHON_
#define _WRAPPING_DAP_NET_PYTHON_

#define PY_SSIZE_T_CLEAN
#include "Python.h"
#include "dap_chain_net.h"
#include "dap_chain_net_tx.h"
#include "wrapping_dap_chain_net_state.h"
//#include "wrapping_dap_chain_net_state.h"
#include "wrapping_dap_chain_common.h"
#include "wrapping_dap_chain_ledger.h"
#include "libdap-chain-python.h"
#include "libdap_chain_type_python.h"
#include "dap_chain_net_srv_stake_pos_delegate.h"

#ifdef __cplusplus
extern "C"{
#endif

typedef struct PyDapChainNet{
    PyObject_HEAD
    dap_chain_net_t *chain_net;
}PyDapChainNetObject;

int dap_chain_net_init_py(void);
void dap_chain_net_deinit_py(void);

PyObject* PyDapChainNet_str(PyObject *self);

PyObject *dap_chain_net_load_all_py(PyObject *self, PyObject *args);
PyObject *dap_chain_net_state_go_to_py(PyObject *self, PyObject *args);
PyObject *dap_chain_net_start_py(PyObject *self, PyObject *args);
PyObject *dap_chain_net_stop_py(PyObject *self, PyObject *args);
PyObject *dap_chain_net_links_establish_py(PyObject *self, PyObject *args);
PyObject *dap_chain_net_sync_chains_py(PyObject *self, PyObject *args);
PyObject *dap_chain_net_sync_gdb_py(PyObject *self, PyObject *args);
PyObject *dap_chain_net_sync_all_py(PyObject *self, PyObject *args);

PyObject *dap_chain_net_proc_datapool_py(PyObject *self, PyObject *args);

PyObject *dap_chain_net_by_name_py(PyObject *self, PyObject *args);
PyObject *dap_chain_get_nets_py(PyObject *self, PyObject *args);
PyObject *dap_chain_net_by_id_py(PyObject *self, PyObject *args);
PyObject *dap_chain_net_id_by_name_py(PyObject *self, PyObject *args);
PyObject *dap_chain_ledger_by_net_name_py(PyObject *self, PyObject *args);

PyObject *dap_chain_net_get_chain_by_name_py(PyObject *self, PyObject *args);

PyObject *dap_chain_net_get_cur_addr_py(PyObject *self, PyObject *args);
PyObject *dap_chain_net_get_cur_cell_py(PyObject *self, PyObject *args);
PyObject *dap_chain_net_get_cur_addr_int_py(PyObject *self, PyObject *args);
PyObject *dap_chain_net_get_config_by_item(PyObject *self, PyObject *args);

PyObject *dap_chain_net_get_gdb_group_mempool_py(PyObject *self, PyObject *args);
PyObject *dap_chain_net_get_gdb_group_mempool_by_chain_type_py(PyObject *self, PyObject *args);
PyObject *dap_chain_net_links_connect_py(PyObject *self, PyObject *args);
PyObject *dap_chain_net_get_chain_by_chain_type_py(PyObject *self, PyObject *args);
PyObject *dap_chain_net_get_ledger_py(PyObject *self, PyObject *args);
PyObject *dap_chain_net_get_name_py(PyObject *self, PyObject *args);
PyObject *dap_chain_net_python_get_id(PyObject *self, void *closure);
PyObject *dap_chain_net_python_get_chains(PyObject *self, void *closure);
PyObject *dap_chain_net_get_tx_by_hash_py(PyObject *self, PyObject *args);
PyObject *dap_chain_net_add_notify_py(PyObject *self, PyObject *args);
PyObject *dap_chain_net_get_tx_fee_py(PyObject *self, void *closure);
PyObject *dap_chain_net_get_tx_fee_addr_py(PyObject *self, void *closure);
PyObject *dap_chain_net_get_validator_max_fee_py(PyObject *self, void *closure);
PyObject *dap_chain_net_get_validator_min_fee_py(PyObject *self, void *closure);
PyObject *dap_chain_net_get_validator_average_fee_py(PyObject *self, void *closure);
PyObject *dap_chain_net_convert_verify_code_to_str(PyObject *self, PyObject *args);
PyObject *dap_chain_net_get_native_ticker_py(PyObject *self, void *closure);
PyObject *dap_chain_net_get_mempool_autoproc_py(PyObject *self, void *closure);
PyObject *dap_chain_net_get_gdb_alias_py(PyObject *self, void *closure);


extern PyTypeObject DapChainNetObjectType;

static bool PyDapChainNet_Check(PyDapChainNetObject *self){
    return PyObject_TypeCheck(self, &DapChainNetObjectType);
}

#ifdef __cplusplus
}
#endif

#endif //_WRAPPING_DAP_NET_PYTHON_
