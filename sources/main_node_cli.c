/*
 * Authors:
 * Dmitriy A. Gearasimov <kahovski@gmail.com>
 * DeM Labs Inc.   https://demlabs.net
 * DeM Labs Open source community https://github.com/demlabsinc
 * Copyright  (c) 2017-2019
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

#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "dap_chain_node_cli.h"
#include "dap_common.h"
#include "dap_file_utils.h"
#include "dap_strfuncs.h"
#include "dap_app_cli.h"
#include "dap_app_cli_net.h"
#include "dap_app_cli_shell.h"

#ifdef DAP_OS_WINDOWS
#include "registry.h"
#elif defined DAP_OS_ANDROID

#include <android/log.h>
#include <jni.h>
#endif

#define NODE_NAME "cellframe-node"

static dap_app_cli_connect_param_t *cparam;
static const char *listen_socket = NULL;

#if !DAP_OS_ANDROID
int main(int argc, const char *argv[])

{
    dap_set_appname(NODE_NAME "-cli");
#ifdef DAP_OS_WINDOWS
    SetConsoleCP(1252);
    SetConsoleOutputCP(1252);
    WSADATA wsaData;
    WSAStartup(MAKEWORD(2,2), &wsaData);
#endif

    // get relative path to config
    int l_rel_path = 0;
    if (argv[1] && argv[2] && !dap_strcmp("-B" , argv[1])) {
        g_sys_dir_path = (char*)argv[2];
        l_rel_path = 1;
    }
    if (!g_sys_dir_path) {
    #ifdef DAP_OS_WINDOWS
        g_sys_dir_path = dap_strdup_printf("%s/%s", regGetUsrPath(), NODE_NAME);
    #elif DAP_OS_MAC
        g_sys_dir_path = dap_strdup_printf("/Applications/CellframeNode.app/Contents/Resources");
    #elif DAP_OS_ANDROID
        g_sys_dir_path = dap_strdup_printf("/storage/emulated/0/opt/%s", NODE_NAME);
    #elif DAP_OS_UNIX
        g_sys_dir_path = dap_strdup_printf("/opt/%s", NODE_NAME);
    #endif
    }


    /*if (dap_common_init(dap_get_appname(), NULL, NULL) != 0) {
        printf("Fatal Error: Can't init common functions module");
        return -2;
    }

    */{
        char l_config_dir[MAX_PATH] = {'\0'};
        sprintf(l_config_dir, "%s/etc", g_sys_dir_path);
        dap_config_init(l_config_dir);
    }
    dap_log_level_set(L_CRITICAL);
    int res = dap_app_cli_main(NODE_NAME, l_rel_path ? argc - 2 : argc, l_rel_path ? argv + 2 : argv);
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
#endif
