/*
* Authors:
* Alexey V. Stratulat <alexey.stratulat@demlabs.net>
* DeM Labs Inc.   https://demlabs.net
* DeM Labs Open source community https://gitlab.demlabs.net/cellframe/libdap-plugins-python
* Copyright  (c) 2017-2020
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

#ifndef _DAP_CHAIN_PLUGINS_LIST_
#define _DAP_CHAIN_PLUGINS_LIST_

#include "Python.h"
#include "stdbool.h"
#include "dap_common.h"
#include "dap_strfuncs.h"
#include "utlist.h"
#include "dap_chain_plugins_manifest.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dap_chain_list_plugin_module{
    char *name;
    PyObject *obj_module;
    struct dap_chain_list_plugin_module *next;
}dap_chain_plugin_list_module_t;

static dap_chain_plugin_list_module_t* s_dap_chain_plugins_module_list;

void dap_chain_plugins_list_init();

dap_chain_plugin_list_module_t* dap_chain_plugins_list_get();

bool dap_chain_plugins_list_check_load_plugins(dap_chain_plugins_list_char_t *a_list);

void dap_chain_plugins_list_add(PyObject *a_module, const char *a_name);
void dap_chain_plugins_list_name_del(const char *a_name);
int dap_chain_plugins_list_name_cmp(dap_chain_plugin_list_module_t *a_element, const char *a_name);

#ifdef __cplusplus
extern "C" {
#endif
#endif // _DAP_CHAIN_PLUGINS_LIST_
