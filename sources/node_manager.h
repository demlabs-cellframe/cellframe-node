/*
 Copyright (c) 2017-2018 (c) Project "DeM Labs Inc" https://github.com/demlabsinc
  All rights reserved.

 This file is part of DAP (Deus Applications Prototypes) the open source project

    DAP (Deus Applicaions Prototypes) is free software: you can redistribute it and/or modify
    it under the terms of the GNU Lesser General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    DAP is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Lesser General Public License for more details.

    You should have received a copy of the GNU Lesser General Public License
    along with any DAP based project.  If not, see <http://www.gnu.org/licenses/>.
*/
#pragma once
#ifndef _NODE_MANAGER_H_
#define _NODE_MANAGER_H_

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include "dap_server.h"
#include "dap_common.h"
#include "dap_config.h"
#include "dap_udp_server.h"
#include "dap_udp_client.h"
#include "dap_enc.h"
#include "dap_enc_key.h"


typedef struct node_manager{
    dap_server_t* sh;
    dap_config_t *l_config;

} node_manager_t;


int node_manager_init();

node_manager_t* new_node_manager(char* config_file);                             // Create new manager structure

void node_manager_deinit();

void node_manager_start(node_manager_t* manager);        // Start manager work
void node_manager_start_stream();


#endif
