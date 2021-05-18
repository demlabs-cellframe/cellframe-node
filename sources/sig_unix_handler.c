#include <signal.h>
#include <stdio.h>
#include <string.h>

#include "dap_common.h"
#include "dap_events.h"
#include "dap_chain_global_db.h"
#include "sig_unix_handler.h"

#define LOG_TAG "sig_unix_handler"

static const char *s_pid_path = NULL;

static void clear_pid_file() {
    FILE * f = fopen(s_pid_path, "w");
    if (f == NULL)
        log_it(L_WARNING, "Pid file not cleared");
    else
        fclose(f);
}

static void sig_exit_handler(int sig_code) {
    log_it(L_DEBUG, "Got exit code: %d", sig_code);
    clear_pid_file();
    dap_chain_global_db_deinit();
    //dap_events_stop_all();
    exit(0);
}

int sig_unix_handler_init(const char *a_pid_path) 
{
    //char * l_pid_dir = dap_path_get_dirname(a_pid_path);
    //sleep(1); // Don't know why but without it it crashes O_o 
    //dap_mkdir_with_parents(l_pid_dir);
    //DAP_DELETE(l_pid_dir);

    s_pid_path = strdup(a_pid_path);
    
    struct sigaction new_action, old_action;
    new_action.sa_handler = sig_exit_handler;
    new_action.sa_flags = 0;
    sigaction(SIGTERM, &new_action, &old_action);
    sigaction(SIGINT, &new_action, &old_action);
    sigaction(SIGHUP, &new_action, &old_action);
    return 0;
}

int sig_unix_handler_deinit() {
    if( s_pid_path )
    DAP_DELETE((void *)s_pid_path);
    signal(SIGTERM, SIG_DFL);
    signal(SIGINT, SIG_DFL);
    signal(SIGHUP, SIG_DFL);
    return 0;
}
