#include <signal.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>

#include "dap_common.h"
#include "dap_events.h"
#include "dap_chain_global_db.h"
#include "dap_chain_node.h"
#include "dap_chain_net_srv_xchange.h"
#include "dap_chain_net_srv_stake_lock.h"
#include "dap_chain_net_srv_stake_pos_delegate.h"
#include "dap_chain.h"
#include "dap_stream.h"
#include "dap_stream_ctl.h"
#include "dap_enc_ks.h"
#include "dap_enc_http.h"
#include "dap_http.h"
#include "dap_chain_node_dns_server.h"
#include "sig_unix_handler.h"
#ifdef DAP_MODULES_DYNAMIC
#include "dap_modules_dynamic_cdb.h"
#endif

#define LOG_TAG "sig_unix_handler"

void dap_chain_plugins_deinit();

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
	
#ifdef DAP_SUPPORT_PYTHON_PLUGINS
    dap_chain_plugins_deinit();
#endif
    dap_chain_node_mempool_autoproc_deinit();
    dap_chain_net_srv_xchange_deinit();
    dap_chain_net_srv_stake_lock_deinit();
    dap_chain_net_srv_stake_pos_delegate_deinit();
    dap_chain_net_deinit();
    dap_chain_global_db_deinit();
    dap_chain_deinit();
    dap_stream_ctl_deinit();
    dap_stream_deinit();
    dap_enc_ks_deinit();
    enc_http_deinit();
    dap_http_deinit();
#ifdef DAP_MODULES_DYNAMIC
    dap_modules_dynamic_close_cdb();
#endif
    dap_interval_timer_deinit();
    dap_common_deinit();

    log_it(L_NOTICE,"Stopped Cellframe Node");
    fflush(stdout);

    exit(0);
}


int sig_unix_handler_init(const char *a_pid_path) 
{
    //char * l_pid_dir = dap_path_get_dirname(a_pid_path);
    //sleep(1); // Don't know why but without it it crashes O_o 
    //dap_mkdir_with_parents(l_pid_dir);
    //DAP_DELETE(l_pid_dir);

    //log_it(L_DEBUG, "Init");

    s_pid_path = strdup(a_pid_path);

    signal(SIGINT, sig_exit_handler);
    signal(SIGHUP, sig_exit_handler);
    signal(SIGTERM, sig_exit_handler);
    signal(SIGQUIT, sig_exit_handler);
    signal(SIGTSTP, sig_exit_handler);
    return 0;
}

int sig_unix_handler_deinit() {
    //log_it(L_DEBUG, "Deinit");

    if( s_pid_path )
    DAP_DELETE((void *)s_pid_path);

    signal(SIGTERM, SIG_DFL);
    signal(SIGINT, SIG_DFL);
    signal(SIGHUP, SIG_DFL);
    signal(SIGQUIT, SIG_DFL);
    signal(SIGTSTP, SIG_DFL);

    return 0;
}

