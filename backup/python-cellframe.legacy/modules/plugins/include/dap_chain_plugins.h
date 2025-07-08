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

#pragma once
#include <Python.h>
#include "dap_config.h"

#ifdef __cplusplus
extern "C"{
#endif

extern PyObject *s_sys_path;
extern const char *s_plugins_root_path;

int dap_chain_plugins_init(dap_config_t *a_config);
void dap_chain_plugins_deinit();
void* dap_chain_plugins_load_plugin_importing(const char *a_dir_path, const char *a_name);
int dap_chain_plugins_reload_plugin(const char * a_name_plugin);
void dap_chain_plugins_save_thread(dap_config_t *a_config);

#ifdef __cplusplus
}
#endif
