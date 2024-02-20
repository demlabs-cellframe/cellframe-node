/*
 * Authors:
 * Dmitriy A. Gerasimov <kahovski@gmail.com>
 * DeM Labs Ltd.   https://demlabs.net
 * CellFrame         https://cellframe.net
 * Copyright  (c) 2017-2020
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
#include "dap_chain_wallet.h"

#include "dap_chain_cs_blocks.h"
#include "dap_chain_cs_block_poa.h"
#include "dap_chain_cs_block_pos.h"
#include "dap_chain_cs_dag.h"
#include "dap_chain_cs_dag_poa.h"
#include "dap_chain_cs_dag_pos.h"
#include "dap_chain_cs_none.h"
#include "dap_chain_cs_esbocs.h"

//#include "dap_chain_bridge.h"
//#include "dap_chain_bridge_btc.h"

#include "dap_chain_net.h"
#include "dap_chain_net_srv.h"
#include "dap_chain_net_srv_app.h"
#include "dap_chain_net_srv_app_db.h"
#include "dap_chain_net_srv_datum.h"
#include "dap_chain_net_srv_geoip.h"

#if defined(DAP_OS_DARWIN) || ( defined(DAP_OS_LINUX) && ! defined (DAP_OS_ANDROID))
#include "dap_chain_net_srv_vpn.h"
#include "dap_chain_net_vpn_client.h"
#endif

#include "dap_global_db.h"
#include "dap_chain_mempool.h"
#include "dap_chain_node.h"
#include "dap_chain_node_cli.h"

#include "dap_stream_session.h"
#include "dap_stream.h"
#include "dap_stream_ctl.h"
#include "dap_chain_ch.h"
#include "dap_stream_ch_chain_net.h"
#include "dap_stream_ch_chain_net_srv.h"
#include "dap_chain_net_srv_xchange.h"
#include "dap_chain_net_srv_stake_pos_delegate.h"
#include "dap_chain_net_srv_stake_lock.h"

#include "dap_common.h"
#include "dap_events_socket.h"
#include "dap_client.h"
#include "dap_http_client.h"
#include "dap_http_simple.h"
#include "dap_process_manager.h"

#include "dap_defines.h"
#include "dap_file_utils.h"
#include "dap_plugin.h"

#ifdef DAP_SUPPORT_PYTHON_PLUGINS
    #include "dap_chain_plugins.h"
    #include "dap_plugins_python_app_context.h"
#endif

#define MEMPOOL_URL "/mempool"
#define MAIN_URL "/"

#ifdef __ANDROID__
    #include "cellframe_node.h"
#endif

void parse_args( int argc, const char **argv );
void exit_if_server_already_running( void );

#ifndef DAP_OS_WINDOWS
static const char *s_pid_file_path = NULL;
#endif

#ifdef __ANDROID__
int cellframe_node_Main(int argc, const char **argv)
#else
int main( int argc, const char **argv )
#endif
{
    dap_server_t *l_server = NULL; // DAP Server instance
    bool l_debug_mode = true;
    bool bServerEnabled = false;
    int rc = 0;

    dap_set_appname("cellframe-node");
    #if defined(_WIN32) && defined(NDEBUG)
        S_SetExceptionFilter( );
    #endif
#ifdef _WIN32
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

    {
        char *l_log_dir = dap_strdup_printf("%s/var/log", g_sys_dir_path);
        dap_mkdir_with_parents(l_log_dir);
        char * l_log_file = dap_strdup_printf( "%s/%s.log", l_log_dir, dap_get_appname());
        if (dap_common_init(dap_get_appname(), l_log_file, l_log_dir) != 0) {
            printf("Fatal Error: Can't init common functions module");
            return -2;
        }
        DAP_DELETE(l_log_dir);
        DAP_DELETE(l_log_file);
    }

    {
        char l_config_dir[MAX_PATH] = {'\0'};
        sprintf(l_config_dir, "%s/etc", g_sys_dir_path);
        dap_config_init(l_config_dir);
    }

    if ((g_config = dap_config_open(dap_get_appname())) == NULL ) {
        log_it( L_CRITICAL,"Can't init general configurations" );
        return -1;
    }
#ifndef DAP_OS_WINDOWS
    char l_default_dir[MAX_PATH] = {'\0'};
    sprintf(l_default_dir, "%s/tmp", g_sys_dir_path);
    s_pid_file_path = dap_config_get_item_str_default(g_config,  "resources", "pid_path", l_default_dir) ;
    save_process_pid_in_file(s_pid_file_path);
#endif

    log_it(L_DEBUG, "Parsing command line args");
    parse_args( argc, argv );

      l_debug_mode = dap_config_get_item_bool_default( g_config,"general","debug_mode", false );
    //  bDebugMode = true;//dap_config_get_item_bool_default( g_config,"general","debug_mode", false );

    if ( l_debug_mode )
        log_it( L_ATT, "*** DEBUG MODE ***" );
    else
       log_it( L_ATT, "*** NORMAL MODE ***" );

    dap_log_level_set( l_debug_mode ? L_DEBUG : L_NOTICE );

    log_it( L_DAP, "*** CellFrame Node version: %s ***", DAP_VERSION );

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

    if ( dap_chain_net_link_manager_init() ) {
        log_it( L_CRITICAL, "Can't init link manager module" );
        return -5;
    }

    if ( dap_http_init() != 0 ) {
        log_it( L_CRITICAL, "Can't init http server module" );
        return -5;
    }

    if ( dap_http_folder_init() != 0 ){
        log_it( L_CRITICAL, "Can't init http server module" );
        return -55;
    }
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

    if ( dap_datum_mempool_init() ) {
        log_it( L_CRITICAL, "Can't init mempool module" );
        return -59;
    }

    if( dap_chain_init() ) {
        log_it(L_CRITICAL,"Can't init dap chain modules");
        return -60;
    }

    if( dap_chain_wallet_init() ) {
        log_it(L_CRITICAL,"Can't init dap chain wallet module");
        return -61;
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

    if( dap_chain_cs_dag_pos_init() ) {
        log_it(L_CRITICAL,"Can't init dap chain dag consensus PoS module");
        return -64;
    }

    if( dap_chain_cs_blocks_init() ) {
        log_it(L_CRITICAL,"Can't init dap chain blocks consensus module");
        return -62;
    }

    if( dap_chain_cs_block_poa_init() ) {
        log_it(L_CRITICAL,"Can't init dap chain blocks consensus PoA module");
        return -63;
    }

    if( dap_chain_cs_block_pos_init() ) {
        log_it(L_CRITICAL,"Can't init dap chain blocks consensus PoS module");
        return -64;
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

    if( dap_chain_net_srv_init() ){
        log_it(L_CRITICAL,"Can't init dap chain network service module");
        return -66;
    }

    if( dap_chain_net_srv_order_init() )
        return -67;

    if (dap_chain_net_srv_xchange_init()) {
        log_it(L_ERROR, "Can't provide exchange capability");
    }

    if (dap_chain_net_srv_stake_lock_init()) {
        log_it(L_ERROR, "Can't start stake lock service");
    }

    if( dap_chain_net_srv_app_init() ){
        log_it(L_CRITICAL,"Can't init dap chain network service applications module");
        return -67;
    }

    if( dap_chain_net_srv_datum_init() ){
        log_it(L_CRITICAL,"Can't init dap chain network service datum module");
        return -68;
    }

#ifndef _WIN32
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

    dap_chain_net_load_all();

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

    if ( dap_chain_node_cli_init(g_config) ) {
        log_it( L_CRITICAL, "Can't init server for console" );
        return -11;
    }

    log_it(L_INFO, "Automatic mempool processing %s",
           dap_chain_node_mempool_autoproc_init() ? "enabled" : "disabled");
    
    uint16_t l_listen_addrs_count = 0;
    if ( bServerEnabled ) {
        char **l_listen_addrs = dap_config_get_array_str(g_config, "server", "listen_address", &l_listen_addrs_count);
        if(!l_listen_addrs || !l_listen_addrs_count || !(l_server = dap_server_new(l_listen_addrs, l_listen_addrs_count, DAP_SERVER_TCP, NULL)))
            log_it( L_WARNING, "Server is enabled but no address is defined" );
    }

    if ( l_server ) { // If listener server is initialized
        // TCP-specific things
            // Init HTTP-specific values
        dap_http_new( l_server, dap_get_appname() );

#ifdef DAP_MODULES_DYNAMIC
        if( dap_config_get_item_bool_default(g_config,"cdb","enabled",false) ) {
            if(dap_modules_dynamic_load_cdb(DAP_HTTP_SERVER( l_server ))){
                log_it(L_CRITICAL,"Can't init CDB module");
                return -3;
            }else{
                log_it(L_NOTICE, "Central DataBase (CDB) is initialized");
            }
        }
#endif

        // Handshake URL
        enc_http_add_proc( DAP_HTTP_SERVER(l_server), "/"DAP_UPLINK_PATH_ENC_INIT );

        // Streaming URLs
        dap_stream_add_proc_http( DAP_HTTP_SERVER(l_server), "/"DAP_UPLINK_PATH_STREAM );
        dap_stream_ctl_add_proc( DAP_HTTP_SERVER(l_server), "/"DAP_UPLINK_PATH_STREAM_CTL );

        const char *str_start_mempool = dap_config_get_item_str( g_config, "mempool", "accept" );
        if ( str_start_mempool && !strcmp(str_start_mempool, "true")) {
                dap_chain_mempool_add_proc(DAP_HTTP_SERVER(l_server), MEMPOOL_URL);
        }

        // Built in WWW server

        if (  dap_config_get_item_bool_default(g_config,"www","enabled",false)  ){
                dap_http_folder_add( DAP_HTTP_SERVER(l_server), "/",
                                dap_config_get_item_str(g_config,
                                                            "resources",
                                                            "www_root") );
        }
        dap_server_set_default(l_server);
        dap_chain_net_announce_addrs();
        dap_http_simple_proc_add(DAP_HTTP_SERVER(l_server), "/"DAP_UPLINK_PATH_NODE_LIST, 2048, dap_chain_net_node_check_http_issue_link);

        bool http_bootstrap_balancer_enabled = dap_config_get_item_bool_default(g_config, "bootstrap_balancer", "http_server", false);
        log_it(L_DEBUG, "config bootstrap_balancer->http_server = \"%u\" ", http_bootstrap_balancer_enabled);
        if (http_bootstrap_balancer_enabled) {
            // HTTP URL add
            dap_http_simple_proc_add(DAP_HTTP_SERVER(l_server), "/"DAP_UPLINK_PATH_BALANCER, 2048, dap_chain_net_balancer_http_issue_link);
        }
    } else
        log_it( L_INFO, "No enabled server, working in client mode only" );

    bool dns_bootstrap_balancer_enabled = dap_config_get_item_bool_default(g_config, "bootstrap_balancer", "dns_server", false);
    log_it(L_DEBUG, "config bootstrap_balancer->dns_server = \"%u\" ", dns_bootstrap_balancer_enabled);
    if (dns_bootstrap_balancer_enabled) {
        // DNS server start
        dap_dns_server_start((char *)dap_config_get_item_str_default(g_config, "bootstrap_balancer", "dns_listen_port", DNS_LISTEN_PORT_STR));
    }

    if(dap_config_get_item_bool_default(g_config,"plugins","enabled",false)){
#ifdef DAP_OS_WINDOWS
        char * l_plugins_path_default = dap_strdup_printf("%s/var/lib/plugins/", g_sys_dir_path);
#else
        char * l_plugins_path_default = dap_strdup_printf("%s/var/lib/plugins", g_sys_dir_path);
#endif
        dap_plugin_init( dap_config_get_item_str_default(g_config, "plugins", "path", l_plugins_path_default) );
        DAP_DELETE(l_plugins_path_default);
#ifdef DAP_SUPPORT_PYTHON_PLUGINS
        //Init python plugins
        log_it(L_NOTICE, "Loading python plugins");
        dap_plugins_python_app_content_init(l_server);
        dap_chain_plugins_init(g_config);
#endif
        dap_plugin_start_all();

#ifdef DAP_SUPPORT_PYTHON_PLUGINS
        dap_chain_plugins_save_thread();
#endif
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
    dap_http_folder_deinit();
    dap_http_deinit();
    if (bServerEnabled) dap_server_deinit();
    dap_enc_ks_deinit();
    dap_chain_node_mempool_autoproc_deinit();
    dap_chain_net_srv_xchange_deinit();
    dap_chain_net_srv_stake_pos_delegate_deinit();
    dap_chain_net_srv_stake_lock_deinit();
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

void parse_args( int argc, const char **argv ) {

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
            exit_if_server_already_running( );
            is_daemon = 1;
            daemonize_process( );
            break;
        }

        default:
        log_it( L_WARNING, "Unknown option from command line" );
        }
    }

    if( !is_daemon )
        exit_if_server_already_running( );
}

void exit_if_server_already_running( void ) {

#ifdef DAP_OS_WINDOWS
    CreateEvent(0, TRUE, FALSE, "DAP_CELLFRAME_NODE_74E9201D33F7F7F684D2FEF1982799A79B6BF94B568446A8D1DE947B00E3C75060F3FD5BF277592D02F77D7E50935E56");
    if ( GetLastError() == ERROR_ALREADY_EXISTS ) {
        log_it( L_WARNING, "DapServer is already running, multiple instances are prohibited by config. Exiting...");
        exit( -2 );
    }
#else
    pid_t pid = get_pid_from_file(s_pid_file_path);
    struct flock lock = { .l_type = F_WRLCK };
    int fd = open(s_pid_file_path, O_WRONLY);
    if (fcntl(fd, F_SETLK, &lock) == -1) {
        log_it( L_WARNING, "DapServer is already running, pid %"DAP_UINT64_FORMAT_U
                          ", multiple instances are prohibited by config. Exiting...", (uint64_t)pid);
        exit( -2 );
    }
#endif
}

