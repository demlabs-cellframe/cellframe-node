/*
 * Cellframe Node — thin loader
 *
 * All module initialization is delegated to dap_sdk_init() / cellframe_sdk_init().
 * The node only handles CLI arguments, config loading, HTTP proc registration,
 * signal handlers, and the main event loop.
 *
 * Authors:
 *   Dmitriy A. Gerasimov <kahovski@gmail.com>
 *   DeM Labs Ltd.   https://demlabs.net
 * Copyright (c) 2017-2026
 * License: GPLv3
 */

#include <stdlib.h>
#include <stdio.h>
#include <stdint.h>
#include <unistd.h>
#include <errno.h>
#include <signal.h>

#ifdef _WIN32
#include <winsock2.h>
#include <windows.h>
#include <io.h>
#include "userenv.h"
#endif

#include "dap_common.h"
#include "dap_strfuncs.h"
#include "dap_file_utils.h"
#include "dap_config.h"
#include "dap_events.h"
#include "dap_sdk.h"
#include "cellframe-sdk.h"

#ifndef _WIN32
#include "sig_unix_handler.h"
#else
#include "sig_win32_handler.h"
#include "registry.h"
void S_SetExceptionFilter(void);
#endif

#ifndef DAP_OS_WASM
#include "dap_daemon.h"
#include "dap_server.h"
#include "dap_http_server.h"
#include "dap_http_folder.h"
#include "dap_http_simple.h"
#include "dap_enc_http.h"
#include "dap_stream.h"
#include "dap_stream_ctl.h"
#include "dap_net_trans_http_stream.h"
#include "dap_dns_server.h"
#include "dap_chain_net.h"
#include "dap_chain_net_cli.h"
#include "dap_chain_net_balancer.h"
#include "dap_chain_net_node_list.h"
#include "dap_plugin.h"
#include "dap_dl.h"
#include "dap_chain.h"
#endif

#define LOG_TAG "main"
#define NODE_NAME "cellframe-node"

#ifndef BUILD_HASH
#define BUILD_HASH "0000000"
#endif
#ifndef BUILD_TS
#define BUILD_TS "undefined"
#endif

const char *dap_node_version(void)
{
    return "CellframeNode, " DAP_VERSION ", " BUILD_TS ", " BUILD_HASH;
}

void set_global_sys_dir(const char *dir)
{
    g_sys_dir_path = dap_strdup(dir);
}

static int s_proc_running_check(const char *a_path);

int main(int argc, const char **argv)
{
    if (argv[1] && !dap_strcmp("-version", argv[1]))
        return printf("%s\n", dap_node_version()), 0;

    bool l_seed_mode = false;
    int rc = 0;

    dap_set_appname(NODE_NAME);
#if defined(_WIN32) && defined(NDEBUG)
    S_SetExceptionFilter();
#endif

    for (int i = 1; i < argc; i++) {
        if (!dap_strcmp("--seed-mode", argv[i]))
            l_seed_mode = true;
        else if (!dap_strcmp("--help", argv[i]) || !dap_strcmp("-h", argv[i])) {
            printf("Cellframe Node %s\n\nUsage: %s [options]\n\n"
                   "Options:\n"
                   "  -version               Print version and exit\n"
                   "  -B <path>              Set base directory path\n"
                   "  --seed-mode            Start seed mode on all chains\n"
                   "  --help, -h             Show this help\n\n",
                   dap_node_version(), argv[0]);
            return 0;
        }
    }

    /* ---------- 1. Determine base directory ---------- */
#if !DAP_OS_ANDROID
    if (argc > 2 && !dap_strcmp("-B", argv[1]))
        g_sys_dir_path = dap_strdup(argv[2]);
#endif
    if (!g_sys_dir_path) {
#ifdef DAP_OS_WINDOWS
        g_sys_dir_path = dap_strdup_printf("%s/%s", regGetUsrPath(), dap_get_appname());
#elif defined(DAP_OS_WASM)
        g_sys_dir_path = dap_strdup("/dap");
#elif DAP_OS_MAC
        g_sys_dir_path = dap_strdup_printf("/Library/Application Support/CellframeNode/");
#elif DAP_OS_UNIX
        g_sys_dir_path = dap_strdup_printf("/opt/%s", dap_get_appname());
#endif
    }

    if (!dap_dir_test(g_sys_dir_path))
        return printf("Invalid path \"%s\"\n", g_sys_dir_path), DAP_DELETE(g_sys_dir_path), -1;

    /* ---------- 2. Prepare log path and config dir ---------- */
    char l_log_path[MAX_PATH + 1];
    char l_config_dir[MAX_PATH + 1];
    snprintf(l_log_path, sizeof(l_log_path), "%s/var/log", g_sys_dir_path);
    if (dap_mkdir_with_parents(l_log_path))
        return printf("Can't create %s (errno %d)\n", l_log_path, errno), DAP_DELETE(g_sys_dir_path), -2;

    {
        size_t n = strlen(l_log_path);
        snprintf(l_log_path + n, sizeof(l_log_path) - n, "/%s.log", dap_get_appname());
    }
    snprintf(l_config_dir, sizeof(l_config_dir), "%s/etc", g_sys_dir_path);

    /* ---------- 3. DAP SDK init ---------- */
    dap_sdk_config_t l_sdk_cfg = {
        .modules     = DAP_SDK_MODULE_FULL_NET | DAP_SDK_MODULE_NET_DNS | DAP_SDK_MODULE_PLUGIN,
        .app_name    = dap_get_appname(),
        .log_level   = L_NOTICE,
        .sys_dir     = g_sys_dir_path,
        .config_dir  = l_config_dir,
        .config_name = dap_get_appname(),
        .log_file    = l_log_path,
    };
    if ((rc = dap_sdk_init(&l_sdk_cfg)) != 0) {
        printf("dap_sdk_init failed: %d\n", rc);
        return DAP_DELETE(g_sys_dir_path), rc;
    }

#if defined(DAP_DEBUG) || !defined(DAP_OS_WINDOWS)
    dap_log_set_external_output(LOGGER_OUTPUT_STDOUT, NULL);
#endif
#ifdef DAP_OS_ANDROID
    dap_log_set_external_output(LOGGER_OUTPUT_ALOG, "NativeCellframeNode");
#endif

    log_it(L_DAP, "*** CellFrame Node version: %s ***", DAP_VERSION);

#ifndef DAP_OS_WASM
    if (g_config && dap_config_get_item_bool_default(g_config, "log", "rotate_enabled", false)) {
        size_t l_timeout = dap_config_get_item_int64(g_config, "log", "rotate_timeout");
        size_t l_maxsize = dap_config_get_item_int64(g_config, "log", "rotate_size");
        dap_daemon_enable_log_cleaner(l_timeout * 60000, l_maxsize);
    }
#endif

    /* ---------- 4. PID file check ---------- */
#ifndef DAP_OS_WINDOWS
    {
        char l_default_pid[MAX_PATH + 1];
        snprintf(l_default_pid, sizeof(l_default_pid), "%s/tmp", g_sys_dir_path);
        char *l_pid_path = dap_config_get_item_str_path_default(g_config, "resources", "pid_path", l_default_pid);
        int l_check = s_proc_running_check(l_pid_path);
        DAP_DELETE(l_pid_path);
        if (l_check)
            return dap_sdk_deinit(), DAP_DELETE(g_sys_dir_path), 2;
    }
#else
    if (s_proc_running_check("DAP_CELLFRAME_NODE_74E9201D33F7F7F684D2FEF1982799A79B6BF94"
                              "B568446A8D1DE947B00E3C75060F3FD5BF277592D02F77D7E50935E56"))
        return dap_sdk_deinit(), DAP_DELETE(g_sys_dir_path), 2;
#endif

    /* ---------- 5. Signal handlers ---------- */
#ifndef _WIN32
    if (sig_unix_handler_init(dap_config_get_item_str_default(g_config, "resources", "pid_path", "/tmp")) != 0) {
        log_it(L_CRITICAL, "Can't init sig unix handler");
        return dap_sdk_deinit(), -12;
    }
#else
    if (sig_win32_handler_init(NULL)) {
        log_it(L_CRITICAL, "Can't init sig win32 handler");
        return dap_sdk_deinit(), -12;
    }
#endif

    /* ---------- 6. Cellframe SDK init ---------- */
    if ((rc = cellframe_sdk_init(CF_MODULE_NODE)) != 0) {
        log_it(L_CRITICAL, "cellframe_sdk_init failed: %d", rc);
        return dap_sdk_deinit(), rc;
    }

#ifndef DAP_OS_WASM
    dap_chain_net_cli_set_version_info(dap_node_version());

    /* ---------- 7. Seed mode ---------- */
    if (l_seed_mode) {
        log_it(L_NOTICE, "Seed mode enabled via --seed-mode");
        for (dap_chain_net_t *net = dap_chain_net_iterate(NULL); net; net = dap_chain_net_iterate(net)) {
            dap_chain_t *chain;
            dap_dl_foreach(net->pub.chains, chain) {
                chain->seed_mode = true;
                log_it(L_NOTICE, "  Seed mode ON: net '%s' chain '%s'", net->pub.name, chain->name);
            }
        }
    }

    /* ---------- 8. HTTP server setup (node-specific) ---------- */
    bool l_server_enabled = g_config && dap_config_get_item_bool_default(g_config, "server", "enabled", false);
    dap_server_t *l_server = l_server_enabled ? dap_http_server_new("server", dap_get_appname()) : NULL;

    if (l_server) {
        enc_http_add_proc(DAP_HTTP_SERVER(l_server), "/" DAP_UPLINK_PATH_ENC_INIT);
        dap_stream_add_proc_http(DAP_HTTP_SERVER(l_server), "/" DAP_UPLINK_PATH_STREAM);
        dap_stream_ctl_add_proc(DAP_HTTP_SERVER(l_server), "/" DAP_UPLINK_PATH_STREAM_CTL);
#if !DAP_OS_ANDROID
        if (dap_config_get_item_bool_default(g_config, "www", "enabled", false))
            dap_http_folder_add(DAP_HTTP_SERVER(l_server), "/",
                                dap_config_get_item_str(g_config, "resources", "www_root"));
#endif
        dap_server_set_default(l_server);
        dap_http_simple_proc_add(DAP_HTTP_SERVER(l_server), "/" DAP_UPLINK_PATH_NODE_LIST,
                                 2048, dap_chain_net_node_check_http_issue_link);
        if (dap_config_get_item_bool_default(g_config, "bootstrap_balancer", "http_server", false))
            dap_http_simple_proc_add(DAP_HTTP_SERVER(l_server), "/" DAP_UPLINK_PATH_BALANCER,
                                     DAP_BALANCER_MAX_REPLY_SIZE, dap_chain_net_balancer_http_issue_link);
    } else {
        log_it(L_INFO, "No enabled server, client mode only");
    }

    /* ---------- 9. Plugins ---------- */
    if (g_config && dap_config_get_item_bool_default(g_config, "plugins", "enabled", false))
        dap_plugin_start_all();

    /* ---------- 10. Bring networks online ---------- */
    dap_chain_net_try_online_all();
    dap_chain_net_announce_addr_all(NULL);
#endif /* !DAP_OS_WASM */

    /* ---------- 11. Main event loop ---------- */
    rc = dap_events_wait();
    log_it(rc ? L_CRITICAL : L_NOTICE, "Server loop stopped with return code %d", rc);

    /* ---------- 12. Cleanup ---------- */
    cellframe_sdk_deinit();
    dap_config_close(g_config);
    dap_sdk_deinit();

    return rc * 10;
}

static int s_proc_running_check(const char *a_path)
{
#ifdef DAP_OS_WINDOWS
    CreateEvent(0, TRUE, FALSE, a_path);
    return GetLastError() == ERROR_ALREADY_EXISTS ? (log_it(L_ERROR, "dap_server is already running"), 1) : 0;
#else
    FILE *l_pidfile = fopen(a_path, "r");
    if (l_pidfile) {
        pid_t f_pid = 0;
        if (fscanf(l_pidfile, "%d", &f_pid) && lockf(fileno(l_pidfile), F_TEST, 0) == -1)
            return log_it(L_ERROR, "Error %d: \"%s\", dap_server already running PID %d",
                          errno, dap_strerror(errno), f_pid), 1;
        else
            l_pidfile = freopen(a_path, "w", l_pidfile);
    } else
        l_pidfile = fopen(a_path, "w");

    if (!l_pidfile)
        return log_it(L_ERROR, "Can't open %s for writing, errno %d: %s",
                       a_path, errno, dap_strerror(errno)), 2;
    fprintf(l_pidfile, "%d", getpid());
    fflush(l_pidfile);
    return lockf(fileno(l_pidfile), F_TLOCK, sizeof(pid_t));
#endif
}
