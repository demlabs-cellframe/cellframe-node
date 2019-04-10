#include <signal.h>
#include <stdio.h>
#include <string.h>
#include "dap_common.h"
#include "sig_unix_handler.h"

#define LOG_TAG "sig_unix_handler"

static const char *l_pid_path;

static void clear_pid_file() {
    FILE * f = fopen(l_pid_path, "w");
    if (f == NULL)
        log_it(L_WARNING, "Pid file not cleared");
    else
        fclose(f);
}

_Noreturn static void sig_exit_handler(int sig_code) {
    log_it(L_DEBUG, "Got exit code: %d", sig_code);
    clear_pid_file();
    exit(0);
}

int sig_unix_handler_init(const char *pid_path) {
    l_pid_path = strdup(pid_path);
    signal(SIGINT, sig_exit_handler);
    signal(SIGTERM, sig_exit_handler);
    signal(SIGHUP, sig_exit_handler);
    return 0;
}

int sig_unix_handler_deinit() {
    free((char*)l_pid_path);
    signal(SIGTERM, SIG_DFL);
    signal(SIGINT, SIG_DFL);
    signal(SIGHUP, SIG_DFL);
    return 0;
}
