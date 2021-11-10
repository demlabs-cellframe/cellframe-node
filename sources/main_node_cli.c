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

#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "dap_chain_node_cli.h"
//#include "dap_client.h"
#include "dap_common.h"
#include "dap_file_utils.h"
#include "dap_strfuncs.h"
#include "dap_app_cli.h"
#include "dap_app_cli_net.h"
#include "dap_app_cli_shell.h"

#ifdef __ANDROID__
    #include "cellframe_node.h"
#endif

#ifdef _WIN32
#include "registry.h"
#endif

#include "dap_defines.h"

static dap_app_cli_connect_param_t *cparam;

/**
 * split string to argc and argv
 */
static char** split_word(char *line, int *argc)
{
    if(!line)
    {
        if(argc)
            *argc = 0;
        return NULL ;
    }
    char **argv = DAP_NEW_Z_SIZE(char*, sizeof(char*) * strlen(line));
    int n = 0;
    char *s, *start = line;
    size_t len = strlen(line);
    for(s = line; s <= line + len; s++) {
        if(whitespace(*s)) {
            *s = '\0';
            argv[n] = start;
            s++;
            // miss spaces
            for(; whitespace(*s); s++)
                ;
            start = s;
            n++;
        }
    }
    // last param
    if(len) {
        argv[n] = start;
        n++;
    }
    if(argc)
        *argc = n;
    return argv;
}

/*
 * Execute a command line.
 */
int execute_line(char *line)
{
    register int i;
    char *word;

    /* Isolate the command word. */
    i = 0;
    while(line[i] && whitespace(line[i]))
        i++;
    word = line + i;

    /*    while(line[i] && !whitespace(line[i]))
     i++;

     if(line[i])
     line[i++] = '\0';

     command = find_command(word);

     if(!command)
     {
     fprintf(stderr, "%s: No such command\n", word);
     return (-1);
     }*/

    /* Get argument to command, if any.
     while(whitespace(line[i]))
     i++;
     word = line + i;*/

    int argc = 0;
    char **argv = split_word(word, &argc);

    // Call the function
    if(argc > 0) {
        dap_app_cli_cmd_state_t cmd;
        memset(&cmd, 0, sizeof(dap_app_cli_cmd_state_t));
        cmd.cmd_name = (char *) argv[0];
        cmd.cmd_param_count = argc - 1;
        if(cmd.cmd_param_count > 0)
            cmd.cmd_param = (char**) (argv + 1);
        // Send command
        int res = dap_app_cli_post_command(cparam, &cmd);
        DAP_DELETE(argv);
        return res;
    }
    fprintf(stderr, "No command\n");
    DAP_DELETE(argv);
    return -1; //((*(command->func))(argc, (const char **) argv, NULL));
}

/**
 * Clear and delete memory of structure cmd_state
 */
void free_cmd_state(dap_app_cli_cmd_state_t *cmd) {
    if(!cmd->cmd_param)
        return;
    for(int i = 0; i < cmd->cmd_param_count; i++)
            {
        DAP_DELETE(cmd->cmd_param[i]);
    }
    DAP_DELETE(cmd->cmd_res);
    DAP_DELETE(cmd);
}

/**
 *  Read and execute commands until EOF is reached.  This assumes that
 *  the input source has already been initialized.
 */
int shell_reader_loop()
{
    char *line, *s;

    rl_initialize(); /* Bind our completer. */
    int done = 0;
    // Loop reading and executing lines until the user quits.
    for(; done == 0;) {
        // Read a line of input
        line = rl_readline("> ");

        if(!line)
            break;

        /* Remove leading and trailing whitespace from the line.
         Then, if there is anything left, add it to the history list
         and execute it. */
        s = rl_stripwhite(line);

        if(*s)
        {
            add_history(s);
            execute_line(s);
        }

        DAP_DELETE(line);
    }

    return 0;
}

#ifdef __ANDROID__
int cellframe_node__cli_Main(int argc, const char *argv[])
#else

int main(int argc, const char *argv[])
#endif
{
    dap_set_appname("cellframe-node");
#ifdef _WIN32
    SetConsoleCP(1252);
    SetConsoleOutputCP(1252);
    g_sys_dir_path = dap_strdup_printf("%s/%s", regGetUsrPath(), dap_get_appname());
#elif DAP_OS_MAC
    char * l_username = NULL;
    exec_with_ret(&l_username,"whoami|tr -d '\n'");
    if (!l_username){
        printf("Fatal Error: Can't obtain username");
        return 2;
    }
    g_sys_dir_path = dap_strdup_printf("/Users/%s/Applications/Cellframe.app/Contents/Resources", l_username);
    DAP_DELETE(l_username);
#elif DAP_OS_ANDROID
    g_sys_dir_path = dap_strdup_printf("/storage/emulated/0/opt/%s",dap_get_appname());
#elif DAP_OS_UNIX
    g_sys_dir_path = dap_strdup_printf("/opt/%s", dap_get_appname());
#endif
    if (dap_common_init(dap_get_appname(), NULL, NULL) != 0) {
        printf("Fatal Error: Can't init common functions module");
        return -2;
    }

    {
        char l_config_dir[MAX_PATH] = {'\0'};
        dap_sprintf(l_config_dir, "%s/etc", g_sys_dir_path);
        dap_config_init(l_config_dir);
    }
    dap_log_level_set(L_CRITICAL);

    if((g_config = dap_config_open(dap_get_appname())) == NULL) {
        printf("Can't init general configurations %s.cfg\n", dap_get_appname());
        exit(-1);
    }

    // connect to node

#ifndef _WIN32
    const char* listen_socket = dap_config_get_item_str( g_config, "conserver", "listen_unix_socket_path"); // unix socket mode
#else
    const char* listen_socket = NULL;
    WSADATA wsaData;
    WSAStartup(MAKEWORD(2,2), &wsaData);
#endif

    cparam = dap_app_cli_connect(listen_socket);
    if(!cparam)
    {
        printf("Can't connect to %s\n",dap_get_appname());
        exit(-1);
    }

    /*{
     printf("start node_cli_post_command()\n");
     cmd_state *cmd = DAP_NEW_Z(cmd_state);
     cmd->cmd_name = "cmd1";
     cmd->cmd_param_count = 2;
     cmd->cmd_param = DAP_NEW_Z_SIZE(char*, cmd->cmd_param_count * sizeof(char*));
     cmd->cmd_param[0] = strdup("t2-t1");
     cmd->cmd_param[1] = strdup("-opt");
     int a = node_cli_post_command(cparam, cmd);
     printf("node_cli_post_command()=%d\n", a);
     free_cmd_state(cmd);
     }*/

    if(argc > 1){
        // Call the function
        //int res = ((*(command->func))(argc - 2, argv + 2));
        dap_app_cli_cmd_state_t cmd;
        memset(&cmd, 0, sizeof(dap_app_cli_cmd_state_t));
        cmd.cmd_name = strdup(argv[1]);
        cmd.cmd_param_count = argc - 2;
        if(cmd.cmd_param_count > 0)
            cmd.cmd_param = (char**) (argv + 2);
        // Send command
        int res = dap_app_cli_post_command(cparam, &cmd);
        dap_app_cli_disconnect(cparam);
#ifdef _WIN32
        WSACleanup();
#endif
        switch (res) {
            case DAP_CLI_ERROR_FORMAT:
                printf("Response format error!\n");
                break;
            case DAP_CLI_ERROR_SOCKET:
                printf("Socket read error!\n");
                break;
            case DAP_CLI_ERROR_TIMEOUT:
                printf("No response recieved.\n");
                break;
            case DAP_CLI_ERROR_INCOMPLETE:
                printf("Connection closed by peer");
            default:
                break;
        }
        return res;
    }else{
        // command not found, start interactive shell
        shell_reader_loop();
        dap_app_cli_disconnect(cparam);
    }
#ifdef _WIN32
        WSACleanup();
#endif
    return 0;
}

