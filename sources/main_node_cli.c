/*
 * Authors:
 * Dmitriy A. Gearasimov <kahovski@gmail.com>
 * DeM Labs Inc.   https://demlabs.net
 * DeM Labs Open source community https://github.com/demlabsinc
 * Copyright  (c) 2017-2019
 * All rights reserved.

 This file is part of DAP (Demlabs Application Protocol) the open source project

 DAP (Demlabs Application Protocol) is free software: you can redistribute it and/or modify
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

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "dap_common.h"
#include "dap_strfuncs.h"
#include "dap_app_cli.h"
#include "dap_app_cli_net.h"

#ifdef DAP_OS_WINDOWS
#include "registry.h"
#endif

const char *s_node_app = "cellframe-node";

int main(int argc, char **argv)
{
    dap_set_appname("cellframe-node-cli");
#ifdef DAP_OS_WINDOWS
    SetConsoleCP(1252);
    SetConsoleOutputCP(1252);
    WSADATA wsaData;
    WSAStartup(MAKEWORD(2,2), &wsaData);
    g_sys_dir_path = dap_strdup_printf("%s/%s", regGetUsrPath(), s_node_app);
#elif DAP_OS_MAC
    char * l_username = NULL;
    exec_with_ret(&l_username,"whoami|tr -d '\n'");
    if (!l_username){
        printf("Fatal Error: Can't obtain username");
        return 2;
    }
    g_sys_dir_path = dap_strdup_printf("/Users/%s/Applications/Cellframe.app/Contents/Resources", l_username);
    DAP_DELETE(l_username);
#elif DAP_OS_UNIX
    g_sys_dir_path = dap_strdup_printf("/opt/%s", dap_get_appname());
#endif
    dap_log_level_set(L_CRITICAL);
    int res = dap_app_cli_main(s_node_app, argc, argv);
    switch (res) {
        case DAP_CLI_ERROR_FORMAT:
            printf("Response format error!\n");
            break;
        case DAP_CLI_ERROR_SOCKET:
            printf("Socket read error!\n");
            break;
        case DAP_CLI_ERROR_TIMEOUT:
            printf("No response recieved\n");
            break;
        case DAP_CLI_ERROR_INCOMPLETE:
            printf("Connection closed by peer\n");
        default:
            break;
    }
    return res;
}

