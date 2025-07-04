/*
 * Authors:
 * Dmitriy A. Gerasimov <kahovski@gmail.com>
 * DeM Labs Ltd.   https://demlabs.net
 * CellFrame         https://cellframe.net
 * Copyright  (c) 2017-2020
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

#include "dap_strfuncs.h"
#include <stdlib.h>
#include <stdio.h>
#include <time.h>
#include <stdlib.h>
#include <stddef.h>
#include <stdint.h>
#include <unistd.h>
#include <sys/types.h>
#include <getopt.h>
#include <signal.h>
#include <errno.h>
#include <unistd.h>

#ifdef _WIN32
#include <winsock2.h>
#include <windows.h>
#include <mswsock.h>
#include <ws2tcpip.h>
#include <io.h>
#include <pthread.h>
#include "userenv.h"

#endif

#define LOG_TAG "main"

#ifndef _WIN32
  #include "sig_unix_handler.h"
#else
    #include "sig_win32_handler.h"
    #include "registry.h"
    void  S_SetExceptionFilter( void );
#endif
#include "dap_common.h"
#include "dap_config.h"
#include "dap_server.h"
#include "dap_notify_srv.h"
#include "dap_http_server.h"
#include "dap_http_folder.h"
#include "dap_chain_node_dns_client.h"
#include "dap_chain_node_dns_server.h"
#include "dap_chain_net_balancer.h"
#include "dap_chain_net_node_list.h"

#ifdef DAP_MODULES_DYNAMIC
#include "dap_modules_dynamic_cdb.h"
#endif

#include "dap_events.h"
#include "dap_enc.h"
#include "dap_enc_ks.h"
#include "dap_enc_http.h"

#include "dap_chain.h"
#include "dap_chain_common.h"
#include "dap_chain_wallet.h"

#include "dap_chain_cs_blocks.h"
#include "dap_chain_cs_dag.h"
#include "dap_chain_cs_dag_poa.h"
#include "dap_chain_cs_none.h"
#include "dap_chain_cs_esbocs.h"

//#include "dap_chain_bridge.h"
//#include "dap_chain_bridge_btc.h"

#include "dap_chain_net.h"
#include "dap_chain_net_srv.h"
#include "dap_chain_net_srv_geoip.h"

#if defined(DAP_OS_DARWIN) || ( defined(DAP_OS_LINUX) && ! defined (DAP_OS_ANDROID))
#include "dap_chain_net_srv_vpn.h"
#include "dap_chain_net_vpn_client.h"
#endif

#include "dap_global_db.h"
#include "dap_chain_mempool.h"
#include "dap_chain_node.h"
#include "dap_chain_node_cli.h"
#include "dap_json_rpc.h"

#include "dap_stream.h"
#include "dap_stream_ctl.h"
#include "dap_chain_net_srv_order.h"
#include "dap_chain_net_srv_xchange.h"
#include "dap_chain_net_srv_voting.h"
#include "dap_chain_net_srv_bridge.h"
#include "dap_chain_net_srv_stake_pos_delegate.h"
#include "dap_chain_net_srv_stake_lock.h"
#include "dap_chain_wallet_shared.h"

#include "dap_chain_wallet_cache.h"
#include "dap_chain_policy.h"

#include "dap_events_socket.h"
#include "dap_client.h"
#include "dap_http_simple.h"
#include "dap_process_manager.h"

#include "dap_file_utils.h"
#include "dap_plugin.h"

#ifdef DAP_SUPPORT_PYTHON_PLUGINS
    #include "dap_chain_plugins.h"
    #include "dap_plugins_python_app_context.h"
#endif

#define MEMPOOL_URL "/mempool"
#define MAIN_URL "/"
const char *dap_node_version();
static int s_proc_running_check(const char *a_path);

#ifdef DAP_OS_ANDROID
#include "dap_app_cli.h"
#include <android/log.h>
#include <jni.h>
#endif

#ifndef BUILD_HASH
#define BUILD_HASH "0000000" // 0000000 means uninitialized
#endif

#ifndef BUILD_TS
#define BUILD_TS "undefined"
#endif

#define NODE_NAME "cellframe-node"

const char *dap_node_version() {
    return "CellframeNode, " DAP_VERSION ", " BUILD_TS ", " BUILD_HASH;
}

void set_global_sys_dir(const char *dir)
{
    g_sys_dir_path = dap_strdup(dir);
}

int main( int argc, const char **argv )
{
    if ( argv[1] && !dap_strcmp("-version", argv[1]) )
        return printf("%s\n", dap_node_version()), 0;
        
    dap_server_t *l_server = NULL; // DAP Server instance
    bool l_debug_mode = true;
    bool bServerEnabled = false;
    int rc = 0;

    dap_set_appname(NODE_NAME);
#if defined(_WIN32) && defined(NDEBUG)
    S_SetExceptionFilter( );
#endif

    // get relative path to config
#if !DAP_OS_ANDROID
    if (argc > 2 && !dap_strcmp("-B" , argv[1]))
        g_sys_dir_path = dap_strdup(argv[2]);
#endif

    if (!g_sys_dir_path) {
#ifdef DAP_OS_WINDOWS
        g_sys_dir_path = dap_strdup_printf("%s/%s", regGetUsrPath(), dap_get_appname());
#elif DAP_OS_MAC
        g_sys_dir_path = dap_strdup_printf("/Library/Application Support/CellframeNode/");
#elif DAP_OS_UNIX
        g_sys_dir_path = dap_strdup_printf("/opt/%s", dap_get_appname());
#endif
    }
    if ( !dap_dir_test(g_sys_dir_path) ) {
        printf("Invalid path \"%s\"", g_sys_dir_path);
        rc = -1;
    } else {
        char l_path[MAX_PATH + 1];
        int pos = snprintf(l_path, sizeof(l_path), "%s/var/log", g_sys_dir_path);
        if ( dap_mkdir_with_parents(l_path) ) {
            printf("Can't create directory %s, error %d", l_path, errno);
            rc = -2;
        } else {
            snprintf(l_path + pos, sizeof(l_path) - pos, "/%s.log", dap_get_appname());
            if ( dap_common_init(dap_get_appname(), l_path) ) {
                printf("Fatal Error: Can't init common functions module");
                rc = -3;
            } else {
#if defined (DAP_DEBUG) || !defined(DAP_OS_WINDOWS)
                dap_log_set_external_output(LOGGER_OUTPUT_STDOUT, NULL);
#else
                dap_log_set_external_output(LOGGER_OUTPUT_NONE, NULL);
#endif
#ifdef DAP_OS_ANDROID
                dap_log_set_external_output(LOGGER_OUTPUT_ALOG, "NativeCellframeNode");
#endif
                log_it(L_DEBUG, "Use main path: %s", g_sys_dir_path);
                snprintf(l_path, sizeof(l_path), "%s/etc", g_sys_dir_path);
                if ( dap_config_init(l_path) ) {
                    log_it( L_CRITICAL,"Can't init general config \"%s/%s.cfg\"\n", l_path, NODE_NAME );
                    rc = -4;
                }
            }
        }
    }
    if ( rc )
        return DAP_DELETE(g_sys_dir_path), rc;

    if (!( g_config = dap_config_open(dap_get_appname()) ))
        return log_it( L_CRITICAL,"Can't open general config %s.cfg", dap_get_appname() ), DAP_DELETE(g_sys_dir_path), -5;
#ifndef DAP_OS_WINDOWS
    char l_default_dir[MAX_PATH + 1];
    snprintf(l_default_dir, MAX_PATH + 1, "%s/tmp", g_sys_dir_path);
    char *l_pid_file_path = dap_config_get_item_str_path_default(g_config,  "resources", "pid_path", l_default_dir);
    int l_pid_check = s_proc_running_check(l_pid_file_path);
    DAP_DELETE(l_pid_file_path);
    if (l_pid_check)
        return 2;
#else
    if ( s_proc_running_check("DAP_CELLFRAME_NODE_74E9201D33F7F7F684D2FEF1982799A79B6BF94"
                              "B568446A8D1DE947B00E3C75060F3FD5BF277592D02F77D7E50935E56") )
        return DAP_DELETE(g_sys_dir_path), 2;
#endif

    log_it(L_DEBUG, "Parsing command line args");

    l_debug_mode = dap_config_get_item_bool_default( g_config,"general","debug_mode", false );

    if ( l_debug_mode )
        log_it( L_ATT, "*** DEBUG MODE ***" );
    else
       log_it( L_ATT, "*** NORMAL MODE ***" );

    dap_log_level_set( l_debug_mode ? L_DEBUG : L_NOTICE );

    log_it( L_DAP, "*** CellFrame Node version: %s ***", DAP_VERSION );
    
    if ( dap_config_get_item_bool_default(g_config, "log", "rotate_enabled", false) ) {
        size_t  l_timeout_minutes   = dap_config_get_item_int64(g_config, "log", "rotate_timeout"),
                l_max_file_size     = dap_config_get_item_int64(g_config, "log", "rotate_size");
        log_it(L_NOTICE, "Log rotation every %lu min enabled, max log file size %lu MB",
                         l_timeout_minutes, l_max_file_size);
        dap_common_enable_cleaner_log(l_timeout_minutes * 60000, l_max_file_size);
    }

    if ( dap_enc_init() != 0 ){
        log_it( L_CRITICAL, "Can't init encryption module" );
        return -56;
    }
    // change to dap_config_get_item_int_default when it's will be possible
    uint32_t l_thread_cnt = dap_config_get_item_int32_default(g_config, "resources", "threads_cnt", 0);
    // New event loop init
    dap_events_init(l_thread_cnt, 0);
    dap_events_start();

    bServerEnabled = dap_config_get_item_bool_default( g_config, "server", "enabled", false );

    if ( bServerEnabled && dap_server_init() != 0 ) {
        log_it( L_CRITICAL, "Can't init socket server module" );
        return -4;
    }

    if ( dap_http_init() != 0 ) {
        log_it( L_CRITICAL, "Can't init http server module" );
        return -5;
    }

#if !DAP_OS_ANDROID
    if ( dap_http_folder_init() != 0 ){
        log_it( L_CRITICAL, "Can't init http server module" );
        return -55;
    }
#endif
    
    if ( dap_http_simple_module_init() != 0 ) {
        log_it(L_CRITICAL,"Can't init http simple module");
        return -9;
    }

    if ( enc_http_init() != 0 ) {
        log_it( L_CRITICAL, "Can't init encryption http session storage module" );
        return -81;
    }

    if ( dap_stream_init(g_config) != 0 ) {
        log_it( L_CRITICAL, "Can't init stream server module" );
        return -82;
    }

    if ( dap_stream_ctl_init() != 0 ){
        log_it( L_CRITICAL, "Can't init stream control module" );
        return -83;
    }

    dap_client_init();

    // Create and init notify server
    if ( dap_notify_server_init() != 0 ){
        log_it( L_ERROR, "Can't init notify server module" );
    }

    if ( dap_global_db_init() != 0 ) {
        log_it( L_CRITICAL, "Can't init global db module" );
        return -58;
    }

    // Clear wallet shared GDB group on startup
    int l_cleared_count = dap_chain_clear_gdb_group("local.wallet_shared");
    if (l_cleared_count >= 0) {
        log_it(L_INFO, "Cleared %d wallet shared records from GDB on startup", l_cleared_count);
    } else {
        log_it(L_WARNING, "Failed to clear wallet shared GDB group on startup, error code %d", l_cleared_count);
    }

    if ( dap_datum_mempool_init() ) {
        log_it( L_CRITICAL, "Can't init mempool module" );
        return -59;
    }

    if( dap_chain_init() ) {
        log_it(L_CRITICAL,"Can't init dap chain modules");
        return -60;
    }

    if (dap_chain_net_srv_stake_pos_delegate_init()) {
        log_it(L_ERROR, "Can't start delegated PoS stake service");
    }

    if( dap_chain_cs_dag_init() ) {
        log_it(L_CRITICAL,"Can't init dap chain dag consensus module");
        return -62;
    }

    if( dap_chain_cs_dag_poa_init() ) {
        log_it(L_CRITICAL,"Can't init dap chain dag consensus PoA module");
        return -63;
    }

    if( dap_chain_cs_blocks_init() ) {
        log_it(L_CRITICAL,"Can't init dap chain blocks consensus module");
        return -62;
    }

    if( dap_chain_cs_esbocs_init() ){
        log_it(L_CRITICAL,"Can't init enhanced stake-based blocks operating consensus module");
        return -69;
    }

    if( dap_nonconsensus_init() ) {
        log_it(L_CRITICAL, "Can't init nonconsensus chain module");
        return -71;
    }

    if( dap_chain_net_init() ){
        log_it(L_CRITICAL,"Can't init dap chain network module");
        return -65;
    }

    if( dap_chain_policy_init() ){
        log_it(L_CRITICAL,"Can't init dap chain policy module");
        return -66;
    }

    if( dap_chain_wallet_init() ) {
        log_it(L_CRITICAL,"Can't init dap chain wallet module");
        return -61;
    }

    if( dap_chain_net_srv_init() ){
        log_it(L_CRITICAL,"Can't init dap chain network service module");
        return -66;
    }

    if (dap_chain_net_srv_xchange_init()) {
        log_it(L_ERROR, "Can't provide exchange capability");
    }

    if (dap_chain_net_srv_voting_init()) {
        log_it(L_ERROR, "Can't provide voting capability");
    }
    
    if (dap_chain_net_srv_bridge_init()) {
        log_it(L_ERROR, "Can't provide bridge capability");
    }
    
    if (dap_chain_net_srv_stake_lock_init()) {
        log_it(L_ERROR, "Can't start stake lock service");
    }

#ifndef _WIN32
#   if !DAP_OS_ANDROID
    if( dap_chain_net_srv_vpn_pre_init() ){
        log_it(L_ERROR, "Can't pre-init vpn service");
    }
#   endif
    if (sig_unix_handler_init(dap_config_get_item_str_default(g_config,
                                                              "resources",
                                                              "pid_path",
                                                              "/tmp")) != 0) {
        log_it(L_CRITICAL,"Can't init sig unix handler module");
        return -12;
    }
#else
    if ( sig_win32_handler_init( NULL ) ) {
        log_it( L_CRITICAL,"Can't init sig win32 handler module" );
        return -12;
    }
#endif

    if ( dap_chain_node_cli_init(g_config) ) {
        log_it( L_CRITICAL, "Can't init server for console" );
        return -11;
    }

    
    if( dap_chain_wallet_cache_init() ) {
        log_it(L_CRITICAL,"Can't init dap chain wallet module");
        return -61;
    }
    dap_chain_net_load_all();

    if( dap_chain_net_srv_order_init() )
        return -67;

    if (dap_chain_node_list_clean_init()) {
        log_it( L_CRITICAL, "Can't init node list clean" );
        return -131;
    }

    if (dap_global_db_clean_init()) {
        log_it( L_CRITICAL, "Can't init gdb clean and pin" );
        return -133;
    }

    log_it(L_INFO, "Automatic mempool processing %s",
           dap_chain_node_mempool_autoproc_init() ? "enabled" : "disabled");
    
    uint16_t l_listen_addrs_count = 0;
    if ( bServerEnabled )
        l_server = dap_http_server_new("server", dap_get_appname());

    if ( l_server ) { // If listener server is initialized
        // Handshake URL
        enc_http_add_proc( DAP_HTTP_SERVER(l_server), "/"DAP_UPLINK_PATH_ENC_INIT );

        // Streaming URLs
        dap_stream_add_proc_http( DAP_HTTP_SERVER(l_server), "/"DAP_UPLINK_PATH_STREAM );
        dap_stream_ctl_add_proc( DAP_HTTP_SERVER(l_server), "/"DAP_UPLINK_PATH_STREAM_CTL );

        const char *str_start_mempool = dap_config_get_item_str( g_config, "mempool", "accept" );
        if ( str_start_mempool && !strcmp(str_start_mempool, "true")) {
            dap_chain_mempool_add_proc(DAP_HTTP_SERVER(l_server), MEMPOOL_URL);
        }

        if (dap_json_rpc_init(l_server, g_config)) {
            log_it( L_CRITICAL, "Can't init json-rpc" );
            return -12;
        } 


        // Built in WWW server
#if !DAP_OS_ANDROID
        if (  dap_config_get_item_bool_default(g_config,"www","enabled",false)  ){
                dap_http_folder_add( DAP_HTTP_SERVER(l_server), "/",
                                dap_config_get_item_str(g_config,
                                                            "resources",
                                                            "www_root") );
        }
#endif
        dap_server_set_default(l_server);
        dap_http_simple_proc_add(DAP_HTTP_SERVER(l_server), "/"DAP_UPLINK_PATH_NODE_LIST, 2048, dap_chain_net_node_check_http_issue_link);
        if ( dap_config_get_item_bool_default(g_config, "bootstrap_balancer", "http_server", false) ) {
            log_it(L_DEBUG, "HTTP balancer enabled");
            dap_http_simple_proc_add(DAP_HTTP_SERVER(l_server), "/"DAP_UPLINK_PATH_BALANCER,
                                     DAP_BALANCER_MAX_REPLY_SIZE, dap_chain_net_balancer_http_issue_link);
        }
        if ( dap_config_get_item_bool_default(g_config, "bootstrap_balancer", "dns_server", false) ) {
            log_it(L_DEBUG, "DNS balancer enabled");
            dap_dns_server_start("bootstrap_balancer");
        }
    } else
        log_it( L_INFO, "No enabled server, working in client mode only" );

#if defined(DAP_OS_DARWIN) || ( defined(DAP_OS_LINUX) && ! defined (DAP_OS_ANDROID))
    // vpn server
    if(dap_config_get_item_bool_default(g_config, "srv_vpn", "enabled", false)) {
        if(dap_chain_net_srv_vpn_init(g_config) != 0) {
            log_it(L_ERROR, "Can't init dap chain network service vpn module");
            return -70;
        }
    }
    // vpn client
    if(dap_chain_net_vpn_client_init(g_config) != 0) {
        log_it(L_ERROR, "Can't init dap chain network service vpn client");
        return -72;
    }

    if(dap_config_get_item_bool_default(g_config, "srv_vpn", "geoip_enabled", false)) {
        if(chain_net_geoip_init(g_config) != 0) {
            log_it(L_CRITICAL, "Can't init geoip module");
            return -73;
        }
    }
#endif

    if(dap_config_get_item_bool_default(g_config,"plugins","enabled",false)){
#ifdef DAP_OS_WINDOWS
        char * l_plugins_path_default = dap_strdup_printf("%s/var/lib/plugins/", g_sys_dir_path);
#else
        char * l_plugins_path_default = dap_strdup_printf("%s/var/lib/plugins", g_sys_dir_path);
#endif
        int rc_plugin_init = 0;
        rc_plugin_init = dap_plugin_init( dap_config_get_item_str_default(g_config, "plugins", "path", l_plugins_path_default) );
        if (rc_plugin_init) {
            log_it(L_ERROR, "The initial initialization for working with manifests and binary plugins failed. Error code %d", rc_plugin_init);    
            DAP_DELETE(l_plugins_path_default);
        } else {
            DAP_DELETE(l_plugins_path_default);
#ifdef DAP_SUPPORT_PYTHON_PLUGINS
            //Init python plugins
            log_it(L_NOTICE, "Loading python plugins");
            dap_plugins_python_app_content_init(l_server);
            rc_plugin_init = dap_chain_plugins_init(g_config);
#endif
            dap_plugin_start_all();

#ifdef DAP_SUPPORT_PYTHON_PLUGINS
            if (!rc_plugin_init) {
                dap_chain_plugins_save_thread(g_config);
            } else {
                log_it(L_ERROR, "Failed to initialize python-cellframe plugins. Error code %d", rc_plugin_init);
            }
#endif
        }
    }
    dap_chain_net_try_online_all();
    rc = dap_events_wait();
    log_it( rc ? L_CRITICAL : L_NOTICE, "Server loop stopped with return code %d", rc );
    // Deinit modules

//failure:
    if(dap_config_get_item_bool_default(g_config,"plugins","enabled",false)){
        dap_plugin_stop_all();
        dap_plugin_deinit();
    }

    dap_dns_server_stop();
    dap_stream_deinit();
    dap_stream_ctl_deinit();
#if !DAP_OS_ANDROID
    dap_http_folder_deinit();
#endif
    dap_http_deinit();
    if (bServerEnabled) dap_server_deinit();
    dap_enc_ks_deinit();
    dap_chain_node_mempool_autoproc_deinit();
    dap_chain_net_srv_xchange_deinit();
    dap_chain_net_srv_stake_pos_delegate_deinit();
    dap_chain_net_srv_stake_lock_deinit();
    dap_chain_net_srv_bridge_deinit();
    dap_chain_net_srv_voting_deinit();
    dap_chain_net_deinit();
    dap_global_db_deinit();
    dap_chain_deinit();
    dap_config_close( g_config );
    dap_interval_timer_deinit();
    dap_common_deinit();

    return rc * 10;
}

static struct option long_options[] = {

    { "stop", 0, NULL, 0 },
    { NULL,   0, NULL, 0 } // must be a last element
};

/*void parse_args( int argc, const char **argv ) {

    int opt, option_index = 0, is_daemon = 0;

    while ( (opt = getopt_long(argc, (char *const *)argv, "D0",
                              long_options, &option_index)) != -1) {
        switch ( opt ) {

        case 0: // --stop
        {
#ifndef DAP_OS_WINDOWS
            pid_t pid = get_pid_from_file(s_pid_file_path);

            if ( pid == 0 ) {
                log_it( L_ERROR, "Can't read pid from file" );
                exit( -20 );
            }

            if ( kill_process(pid) ) {
                log_it( L_INFO, "Server successfully stopped" );
                exit( 0 );
            }

            log_it( L_WARNING, "Server not stopped. Maybe he is not running now?" );
            exit( -21 );
#else
    // TODO OpenEvent + SetEvent
                exit (-22);
#endif

        }

        case 'D':
        {
            log_it( L_INFO, "Daemonize server starting..." );
            //exit_if_server_already_running( );
            is_daemon = 1;
            daemonize_process( );
            break;
        }

        default:
        log_it( L_WARNING, "Unknown option from command line" );
        }
    }

    //if( !is_daemon )
    //    exit_if_server_already_running( );
}*/

int s_proc_running_check(const char *a_path) {
#ifdef DAP_OS_WINDOWS
    CreateEvent(0, TRUE, FALSE, a_path);
    return GetLastError() == ERROR_ALREADY_EXISTS ? ( log_it(L_ERROR, "dap_server is already running"), 1 ) : 0;
#else
    FILE *l_pidfile = fopen(a_path, "r");
    if (l_pidfile) {
        pid_t f_pid = 0;
        if ( fscanf( l_pidfile, "%d", &f_pid ) && lockf(fileno(l_pidfile), F_TEST, 0) == -1 ) {
            return log_it(L_ERROR, "Error %d: \"%s\", dap_server is already running with PID %d",
                           errno, dap_strerror(errno), f_pid), 1;
        }
        else
            l_pidfile = freopen(a_path, "w", l_pidfile);
    } else
        l_pidfile = fopen(a_path, "w");
    
    if (!l_pidfile)
        return log_it(L_ERROR, "Can't open file %s for writing, error %d: %s", 
                                a_path, errno, dap_strerror(errno)), 2;
    fprintf(l_pidfile, "%d", getpid());
    fflush(l_pidfile);
    return lockf(fileno(l_pidfile), F_TLOCK, sizeof(pid_t));
#endif
}
