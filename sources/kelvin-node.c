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


#include <errno.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include "uthash.h"
#include "dap_udp_server.h"
#include "dap_udp_client.h"
#include "dap_http.h"
#include "stream.h"
#include "node_manager.h"






int main(int argc, char **argv) {
    printf("Kelvin Node version 0.1 \n");
    if (argc > 1)
    {        
        char *l_config_name = strdup(argv[1]);

        node_manager_init();

        node_manager_t* manager = new_node_manager(l_config_name);
        node_manager_start(manager);

        node_manager_deinit();
        free(l_config_name);
    }
    else            
        puts("Please, specify config file path.");

    return 0;
}