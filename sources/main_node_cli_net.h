/*
 * Authors:
 * Dmitriy A. Gearasimov <kahovski@gmail.com>
 * DeM Labs Inc.   https://demlabs.net
 * DeM Labs Open source community https://github.com/demlabsinc
 * Copyright  (c) 2017-2019
 * All rights reserved.

 This file is part of DAP (Deus Applications Prototypes) the open source project

 DAP (Deus Applicaions Prototypes) is free software: you can redistribute it and/or modify
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

#include <curl/curl.h>
#include "main_node_cli.h"

// connection description
typedef struct connect_param_ {
    CURL    *curl;
    //SOCKET sock;
} connect_param;

/**
 * Connect to node unix socket server
 *
 * return struct connect_param if connect established, else NULL
 */
connect_param* node_cli_connect(void);

/**
 * Send request to kelvin-node
 *
 * return 0 if OK, else error code
 */
int node_cli_post_command(connect_param *conn, cmd_state *cmd);

int node_cli_disconnect(connect_param *conn);
