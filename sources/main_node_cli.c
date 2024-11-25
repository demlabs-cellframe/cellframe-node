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
    // get relative path to config
    if (argc > 2 && !dap_strcmp("-B" , argv[1])) {
        g_sys_dir_path = dap_strdup(argv[2]);
        if (! dap_dir_test(g_sys_dir_path) )
            return printf("Invalid path \"%s\"", g_sys_dir_path), DAP_DELETE(g_sys_dir_path), -1;
        argc -= 2;
        argv += 2;
    } else {
        g_sys_dir_path =
#ifdef DAP_OS_WINDOWS
            dap_strdup_printf("%s/%s", regGetUsrPath(), NODE_NAME);
#elif defined DAP_OS_MAC
            dap_strdup_printf("/Applications/CellframeNode.app/Contents/Resources");
#elif defined DAP_OS_UNIX
            dap_strdup_printf("/opt/%s", NODE_NAME);
#endif
    }
#ifdef DAP_OS_WINDOWS
    SetConsoleCP(1252);
    SetConsoleOutputCP(1252);
    WSADATA wsaData;
    WSAStartup(MAKEWORD(2,2), &wsaData);
#endif
    dap_log_level_set(L_CRITICAL);
    int res = dap_app_cli_main(NODE_NAME, argc, argv);
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
    DAP_DELETE(g_sys_dir_path);
#ifdef DAP_OS_WINDOWS
    WSACleanup();
#endif
    return res;
}
#endif