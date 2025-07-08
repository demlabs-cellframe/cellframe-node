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

#ifdef __cplusplus
extern "C"{
#endif


typedef struct dap_chain_plugins_list_char{
    char *value;
    struct dap_chain_plugins_list_char *next;
}dap_chain_plugins_list_char_t;

void dap_chain_plugins_list_char_delete_all(dap_chain_plugins_list_char_t *a_list);

typedef struct dap_list_manifest{
    char *name;
    char *version;
    char *author;
    char *description;
    dap_chain_plugins_list_char_t *dependencies;
    struct dap_list_manifest *next;
}dap_chain_plugins_list_manifest_t;

extern dap_chain_plugins_list_manifest_t* s_manifests;

int dap_chain_plugins_manifest_name_cmp(dap_chain_plugins_list_manifest_t *a_man, const char *a_name);

dap_chain_plugins_list_manifest_t *dap_chain_plugins_manifest_new(const char *a_name, const char *a_version,
                                                                  const dap_chain_plugins_list_char_t *a_dep,
                                                                  const char *a_author,
                                                                  const char *a_description);

void dap_chain_plugins_manifest_list_create();

dap_chain_plugins_list_manifest_t* dap_chain_plugins_manifests_get_list(void);
dap_chain_plugins_list_manifest_t *dap_chain_plugins_manifest_list_get_name(const char *a_name);

char* dap_chain_plugins_manifests_get_list_dependencyes(dap_chain_plugins_list_manifest_t *a_element);

dap_chain_plugins_list_manifest_t* dap_chain_plugins_add_manifest_from_file(const char *a_file_path);

bool dap_chain_plugins_manifest_list_add_from_file(const char *a_path_file);

bool dap_chain_plugins_manifest_list_delete_name(const char *a_name);
void dap_chain_plugins_manifest_list_delete_all(void);

#ifdef __cplusplus
}
#endif
