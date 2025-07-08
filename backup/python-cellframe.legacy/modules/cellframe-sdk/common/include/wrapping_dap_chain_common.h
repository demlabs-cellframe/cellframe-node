/*
 * Authors:
 * Alexey V. Stratulat <alexey.stratulat@demlabs.net>
 * DeM Labs Inc.   https://demlabs.net
 * CellFrame       https://cellframe.net
 * Sources         https://gitlab.demlabs.net/cellframe
 * Copyright  (c) 2017-2022
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

#ifndef _WRAPPING_DAP_CHAIN_COMMON_
#define _WRAPPING_DAP_CHAIN_COMMON_
#include <Python.h>
#include "dap_chain_common.h"
#include "libdap_crypto_key_python.h"
#include "wrapping_dap_chain_ledger.h"
//#include "wrapping_dap_chain_ledger"

#ifdef __cplusplus
extern "C" {
#endif

/* Chain hash slow */
typedef struct PyDapChainHashSlow{
    PyObject_HEAD
    dap_chain_hash_slow_t *hash_slow;
}PyDapChainHashSlowObject;

PyObject *dap_chain_hash_slow_to_str_py(PyObject *self, PyObject *args);

extern PyTypeObject DapChainHashSlowObjectType;

/*=================*/

/* Chain addr */
typedef struct PyDapChainAddr{
    PyObject_HEAD
    dap_chain_addr_t *addr;
} PyDapChainAddrObject;
#define PY_DAP_CHAIN_ADDR(a) ((PyDapChainAddrObject*)a)->addr

PyObject *dap_chain_addr_to_str_py(PyObject *self, PyObject *args);
PyObject *dap_chain_addr_from_str_py(PyObject *self, PyObject *args);
PyObject *dap_chain_addr_fill_py(PyObject *self, PyObject *args);
PyObject *dap_chain_addr_fill_from_key_py(PyObject *self, PyObject *args);
PyObject *dap_chain_addr_check_sum_py(PyObject *self, PyObject *args);

PyObject *dap_chain_addr_get_net_id_py(PyObject *self, PyObject *args);

PyObject *obj_addr_str(PyObject *self);

extern PyTypeObject DapChainAddrObjectType;

DAP_STATIC_INLINE bool PyDapChainAddrObject_Check(PyDapChainAddrObject *self) {
    return PyObject_TypeCheck(self, &DapChainAddrObjectType);
}

/*=================*/

/* Chain net id */

typedef struct PyDapChainNetId{
    PyObject_HEAD
    dap_chain_net_id_t net_id;
}PyDapChainNetIdObject;

PyObject *dap_chain_net_id_from_str_py(PyObject *self, PyObject *args);
PyObject *dap_chain_net_id_get_long(PyObject *self, PyObject *args);

extern PyTypeObject DapChainNetIdObjectType;

/*=================*/

/* Chain net srv uid */

typedef struct PyDapChainNetSrvUID{
    PyObject_HEAD
    dap_chain_srv_uid_t net_srv_uid;
}PyDapChainNetSrvUIDObject;

int PyDapChainNetSrvUIDObject_init(PyObject *self, PyObject *args, PyObject *kwds);
PyObject* PyDapChainNetSrvUIDObject_str(PyObject *self);

extern PyTypeObject DapChainNetSrvUidObjectType;

DAP_STATIC_INLINE bool PyDapChainNetSrvUid_Check(PyDapChainNetSrvUIDObject *a_obj){
    return PyObject_TypeCheck(a_obj, &DapChainNetSrvUidObjectType);
}

/*=================*/

/* Chain net srv price unit uid */
typedef struct PyDapChainNetSrvPriceUnitUID{
    PyObject_HEAD
    dap_chain_net_srv_price_unit_uid_t price_unit_uid;
}PyDapChainNetSrvPriceUnitUIDObject;

PyObject *PyDapChainNetSrvPriceUnitUID_str(PyObject *self);

PyObject *wrapping_dap_chain_net_srv_price_unit_uid_get_undefined(PyObject *self, PyObject *args);
PyObject *wrapping_dap_chain_net_srv_price_unit_uid_get_sec(PyObject *self, PyObject *args);
PyObject *wrapping_dap_chain_net_srv_price_unit_uid_get_b(PyObject *self, PyObject *args);

extern PyTypeObject DapChainNetSrvPriceUnitUidObjectType;
DAP_STATIC_INLINE bool PyDapChainNetSrvPriceUnitUidObject_Check(PyObject *self) {
    return PyObject_TypeCheck(self, &DapChainNetSrvPriceUnitUidObjectType);
}
/*=================*/

/* Chain cell id */
typedef struct PyDapChainID{
    PyObject_HEAD
    dap_chain_id_t *chain_id;
}PyDapChainIDObject;

PyObject *DapChainIdObject_str(PyObject *self);

extern PyTypeObject DapChainIdObjectType;

/*=================*/

/* Chain cell id */
typedef struct PyDapChainCellID{
    PyObject_HEAD
    dap_chain_cell_id_t cell_id;
}PyDapChainCellIDObject;

PyObject *PyDapChainCellIdObject_str(PyObject *self);

extern PyTypeObject DapChainCellIdObjectType;

/*=================*/

/* Chain hash slow kind */
typedef struct PyDapChainHashSlowKind{
    PyObject_HEAD
    dap_chain_hash_slow_kind_t *slow_kind;
}PyDapChainHashSlowKindObject;

extern PyTypeObject DapChainHashSlowKindObjectType;

/*=================*/


#ifdef __cplusplus
}
#endif
#endif //_WRAPPING_DAP_CHAIN_COMMON_
