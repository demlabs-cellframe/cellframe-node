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

//#include "dap_client.h"
#include "dap_common.h"
#include "main_node_cli.h"
#include "main_node_cli_net.h"
#include "main_node_cli_shell.h"

static connect_param *cparam;

int com_global_db(int argc, const char ** argv)
{
    printf("com_global_db\n");
    return 0;
}

int com_node(int argc, const char ** argv)
{
    printf("com_node\n");
    return 0;
}

int com_help(int argc, const char ** argv)
{
    printf("com_help\n");
    return 0;
}

typedef int cmdfunc_t(int argc, const char ** argv);

typedef struct {
    char *name; /* User printable name of the function. */
    cmdfunc_t *func; /* Function to call to do the job. */
    char *doc; /* Documentation for this function.  */
} COMMAND;

COMMAND commands[] = {
    { "global_db", com_global_db, "Work with database" },
    { "node", com_node, "Work with node" },
    { "help", com_help, "Display this text" },
    { "?", com_help, "Synonym for `help'" },
    { (char *) NULL, (cmdfunc_t *) NULL, (char *) NULL }
};

/**
 *  Look up NAME as the name of a command, and return a pointer to that
 *  command.  Return a NULL pointer if NAME isn't a command name.
 */
COMMAND* find_command(const char *name)
{
    register int i;

    for(i = 0; commands[i].name; i++)
        if(strcmp(name, commands[i].name) == 0)
            return (&commands[i]);

    return ((COMMAND *) NULL );
}

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
    char **argv = calloc(sizeof(char*), strlen(line));
    int n = 0;
    char *s, *start = line;
    size_t len = strlen(line);
    for(s = line; s < line + len; s++) {
        if(whitespace(*s)) {
            *s = '\0';
            argv[n] = start;
            start = ++s;
            n++;
            // miss spaces
            for(; whitespace(*s); s++)
                ;
        }
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
    COMMAND *command;
    char *word;

    /* Isolate the command word. */
    i = 0;
    while(line[i] && whitespace(line[i]))
        i++;
    word = line + i;

    while(line[i] && !whitespace(line[i]))
        i++;

    if(line[i])
        line[i++] = '\0';

    command = find_command(word);

    if(!command)
    {
        fprintf(stderr, "%s: No such command\n", word);
        return (-1);
    }

    /* Get argument to command, if any. */
    while(whitespace(line[i]))
        i++;

    word = line + i;

    int argc = 0;
    char **argv = split_word(word, &argc);
    /* Call the function. */
    return ((*(command->func))(argc, (const char **) argv));
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

        free(line);
    }
    exit(0);
}

int main(int argc, const char * argv[])
{
    //    set_default_locale();
    //    command_execution_string = shell_script_filename = (char *) NULL;

    // connect to node
    cparam = node_cli_connect();
    if(!cparam)
    {
        printf("Can't connected to kelvin-node\n");
        exit(0);
    }
    {
        printf("start node_cli_post_command()\n");
        cmd_state *cmd = DAP_NEW_Z(cmd_state);
        cmd->cmd_name = "cmd1";
        cmd->cmd_param = "t1 -t2";
        int a = node_cli_post_command(cparam, cmd);
        printf("node_cli_post_command()=%d\n",a);
        DAP_DELETE(cmd);
    }

    COMMAND *command = NULL;
    // in the first argument of command line look for the command
    if(argc > 1)
        command = find_command(argv[1]);

    // command found
    if(command)
    {
        // Call the function
        int ret = ((*(command->func))(argc - 2, argv + 2));
        node_cli_desconnect(cparam);
        return ret;
    }

    // command not found, start interactive shell
    shell_reader_loop();
    node_cli_desconnect(cparam);
    return 0;
}
