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
#undef _WIN32_WINNT
#define _WIN32_WINNT 0x0600
#include <winsock2.h>
#include <windows.h>
#include <mswsock.h>
#include <ws2tcpip.h>
#include <io.h>
//#include "wrappers.h"
#include <wepoll.h>
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

#include "dap_config.h"
#include "dap_server.h"
#include "dap_http.h"
#include "dap_http_folder.h"

#if !defined (_WIN32) && !defined (__ANDROID__)
#include "db_core.h"
#include "db_http.h"
#include "db_http_file.h"
#include "db_auth.h"
#endif

#include "dap_events.h"
#include "dap_enc.h"
#include "dap_enc_ks.h"
#include "dap_enc_http.h"

#include "dap_chain.h"
#include "dap_chain_wallet.h"

#include "dap_chain_cs_dag.h"
#include "dap_chain_cs_dag_poa.h"
#include "dap_chain_cs_dag_pos.h"
#include "dap_chain_gdb.h"

#include "dap_chain_net.h"
#include "dap_chain_net_srv.h"
#include "dap_chain_net_srv_app.h"
#include "dap_chain_net_srv_app_db.h"
#include "dap_chain_net_srv_datum.h"
#include "dap_chain_net_srv_datum_pool.h"

#ifdef DAP_OS_LINUX
#include "dap_chain_net_srv_vpn.h"
#include "dap_chain_net_srv_vpn_cdb.h"
#include "dap_chain_net_srv_vpn_cdb_server_list.h"
#include "dap_chain_net_vpn_client.h"
#endif

#include "dap_chain_global_db.h"
#include "dap_chain_mempool.h"
#include "dap_chain_node_cli.h"

#include "dap_stream_session.h"
#include "dap_stream.h"
#include "dap_stream_ctl.h"
#include "dap_stream_ch_vpn.h"
#include "dap_stream_ch_chain.h"
#include "dap_stream_ch_chain_net.h"
#include "dap_stream_ch_chain_net_srv.h"

#include "dap_common.h"
#include "dap_client_remote.h"
#include "dap_client.h"
#include "dap_http_client.h"
#include "dap_http_client_simple.h"
#include "dap_http_simple.h"
#include "dap_process_manager.h"
#include "dap_traffic_track.h"

#include "dap_defines.h"
#include "dap_file_utils.h"


#define ENC_HTTP_URL "/enc_init"
#define STREAM_CTL_URL "/stream_ctl"

#define STREAM_URL "/stream"
#define MEMPOOL_URL "/mempool"
#define MAIN_URL "/"

#ifdef __ANDROID__
    #include "cellframe_node.h"
#endif

void parse_args( int argc, const char **argv );
void exit_if_server_already_running( void );

static char s_pid_file_path[MAX_PATH];
static void s_auth_callback(enc_http_delegate_t *a_delegate, void * a_arg);

#ifdef __ANDROID__
int cellframe_node_Main(int argc, const char **argv)
#else
int main( int argc, const char **argv )
#endif
{
	dap_server_t *l_server = NULL; // DAP Server instance
	bool bDebugMode = true;
	bool bServerEnabled = true;
	int rc = 0;

	#if defined(_WIN32) && defined(NDEBUG)
		S_SetExceptionFilter( );
	#endif

    {
        char l_log_file_path[MAX_PATH];
#ifdef _WIN32
        dap_sprintf(s_sys_dir_path, "%s/%s", regGetUsrPath(), DAP_APP_NAME);
        l_sys_dir_path_len = strlen(s_sys_dir_path);
        memcpy(l_log_file_path, s_sys_dir_path, l_sys_dir_path_len);
        memcpy(s_pid_file_path, s_sys_dir_path, l_sys_dir_path_len);
#endif

        dap_snprintf(l_log_file_path + l_sys_dir_path_len, sizeof (l_log_file_path), "%s/%s.log", SYSTEM_LOGS_DIR, DAP_APP_NAME);
        dap_mkdir_with_parents(SYSTEM_LOGS_DIR);

        if ( dap_common_init( DAP_APP_NAME, l_log_file_path ) != 0 ) {
            printf( "Fatal Error: Can't init common functions module" );
            return -2;
        }

        dap_snprintf(s_sys_dir_path + l_sys_dir_path_len, sizeof(s_sys_dir_path), "%s", SYSTEM_CONFIGS_DIR);
        dap_config_init( s_sys_dir_path );
        memset(s_sys_dir_path + l_sys_dir_path_len, '\0', MAX_PATH - l_sys_dir_path_len);
        if ( (g_config = dap_config_open(DAP_APP_NAME)) == NULL ) {
            log_it( L_CRITICAL,"Can't init general configurations" );
            return -1;
        }
        dap_sprintf(s_pid_file_path + l_sys_dir_path_len, "%s", dap_config_get_item_str_default( g_config,
                                                                                   "resources",
                                                                                   "pid_path","/tmp") );
    }
    log_it(L_DEBUG, "Parsing command line args");
	parse_args( argc, argv );
	#ifdef _WIN32
        CreateMutexW( NULL, FALSE, (WCHAR *) L"DAP_CELLFRAME_NODE_74E9201D33F7F7F684D2FEF1982799A79B6BF94B568446A8D1DE947B00E3C75060F3FD5BF277592D02F77D7E50935E56" );
	#endif

      bDebugMode = dap_config_get_item_bool_default( g_config,"general","debug_mode", false );
    //  bDebugMode = true;//dap_config_get_item_bool_default( g_config,"general","debug_mode", false );

	if ( bDebugMode )
	    log_it( L_ATT, "*** DEBUG MODE ***" );
	else
 	   log_it( L_ATT, "*** NORMAL MODE ***" );

    dap_log_level_set( bDebugMode ? L_DEBUG: L_INFO );

    log_it( L_DAP, "*** CellFrame Node version: %s ***", DAP_VERSION );

	// change to dap_config_get_item_int_default when it's will be possible
	size_t l_thread_cnt = 0;

	const char *s_thrd_cnt = dap_config_get_item_str( g_config, "resources", "threads_cnt" );
	if ( s_thrd_cnt != NULL )
	    l_thread_cnt = (size_t)atoi( s_thrd_cnt );

	if ( !l_thread_cnt ) {
    	#ifndef _WIN32
      		l_thread_cnt = (size_t)sysconf(_SC_NPROCESSORS_ONLN);
    	#else
      		SYSTEM_INFO si;
      		GetSystemInfo( &si );
      		l_thread_cnt = si.dwNumberOfProcessors;
    	#endif
  	}

	if ( dap_server_init(l_thread_cnt) != 0 ) {
    	log_it( L_CRITICAL, "Can't init socket server module" );
	    return -4;
	}

	if ( dap_http_init() != 0 ) {
    	log_it( L_CRITICAL, "Can't init http server module" );
	    return -5;
	}

	if ( dap_http_folder_init() != 0 ){
	    log_it( L_CRITICAL, "Can't init http server module" );
	    return -55;
	}

	if ( dap_enc_init() != 0 ){
	    log_it( L_CRITICAL, "Can't init encryption module" );
	    return -56;
	}
    
	if ( dap_chain_global_db_init(g_config) ) {
	    log_it( L_CRITICAL, "Can't init global db module" );
	    return -58;
	}

	dap_client_init();

	dap_http_client_simple_init( );

	if ( dap_datum_mempool_init() ) {
	    log_it( L_CRITICAL, "Can't init mempool module" );
	    return -59;
	}

    if( dap_chain_init() !=0){
        log_it(L_CRITICAL,"Can't init dap chain modules");
        return -60;
    }

    if( dap_chain_wallet_init() !=0){
        log_it(L_CRITICAL,"Can't init dap chain wallet module");
        return -61;
    }

    if( dap_chain_cs_dag_init() !=0){
        log_it(L_CRITICAL,"Can't init dap chain dag consensus module");
        return -62;
    }

    if( dap_chain_cs_dag_poa_init() !=0){
        log_it(L_CRITICAL,"Can't init dap chain dag consensus PoA module");
        return -63;
    }

    if( dap_chain_cs_dag_pos_init() !=0){
        log_it(L_CRITICAL,"Can't init dap chain dag consensus PoA module");
        return -64;
    }

    if(dap_chain_gdb_init() != 0) {
        log_it(L_CRITICAL, "Can't init dap chain gdb module");
        return -71;
    }

    if( dap_chain_net_init() !=0){
        log_it(L_CRITICAL,"Can't init dap chain network module");
        return -65;
    }

    if( dap_chain_net_srv_init() !=0){
        log_it(L_CRITICAL,"Can't init dap chain network service module");
        return -66;
    }

    if( dap_chain_net_srv_app_init() !=0){
        log_it(L_CRITICAL,"Can't init dap chain network service applications module");
        return -67;
    }

    if( dap_chain_net_srv_datum_init() !=0){
        log_it(L_CRITICAL,"Can't init dap chain network service datum module");
        return -68;
    }

    if( dap_chain_net_srv_datum_pool_init() !=0){
        log_it(L_CRITICAL,"Can't init dap chain network service datum pool module");
        return -69;
    }
#ifndef _WIN32
    // vpn server
    if(dap_config_get_item_bool_default(g_config, "vpn", "enabled", false)) {
        if(dap_chain_net_srv_vpn_init(g_config) != 0) {
            log_it(L_ERROR, "Can't init dap chain network service vpn module");
            return -70;
        }
    }
    // vpn client
    if(dap_chain_net_vpn_client_init(g_config) != 0) {
        log_it(L_ERROR, "Can't init dap chain network service vpn client");
        return -71;
    }
#endif


	if ( enc_http_init() != 0 ) {
	    log_it( L_CRITICAL, "Can't init encryption http session storage module" );
	    return -81;
	}

	if ( dap_stream_init(dap_config_get_item_bool_default(g_config,"general","debug_dump_stream_headers",false)) != 0 ) {
	    log_it( L_CRITICAL, "Can't init stream server module" );
	    return -82;
	}

	if ( dap_stream_ctl_init(DAP_ENC_KEY_TYPE_OAES, 32) != 0 ){
	    log_it( L_CRITICAL, "Can't init stream control module" );
	    return -83;
	}

	if ( dap_http_simple_module_init() != 0 ) {
	    log_it(L_CRITICAL,"Can't init http simple module");
	    return -9;
	}

	if ( dap_chain_node_cli_init(g_config) ) {
	    log_it( L_CRITICAL, "Can't init server for console" );
	    return -11;
	}

#ifndef _WIN32
    if (sig_unix_handler_init(dap_config_get_item_str_default(g_config,
                                                              "resources",
                                                              "pid_path",
                                                              SYSTEM_PID_FILE_PATH)) != 0) {
        log_it(L_CRITICAL,"Can't init sig unix handler module");
        return -12;
    }
#else
    if ( sig_win32_handler_init( NULL ) ) {
        log_it( L_CRITICAL,"Can't init sig win32 handler module" );
        return -12;
    }
#endif

    save_process_pid_in_file(s_pid_file_path);

	bServerEnabled = dap_config_get_item_bool_default( g_config, "server", "enabled", false );

	log_it ( L_DEBUG,"config server->enabled = \"%u\" ", bServerEnabled );

	if ( bServerEnabled ) {

        int32_t l_port = dap_config_get_item_int32(g_config, "server", "listen_port_tcp");

        if( l_port > 0 ) {
            l_server = dap_server_listen((dap_config_get_item_str(g_config, "server", "listen_address")),
                                   (uint16_t) l_port,
                                   DAP_SERVER_TCP );
        } else
            log_it( L_WARNING, "Server is enabled but no port is defined" );

    }

    if ( l_server ) { // If listener server is initialized
        //bool is_traffick_track_enable = dap_config_get_item_bool_default(g_config, "traffic_track", "enable", false);

#if 0
        if ( is_traffick_track_enable ) {
            time_t timeout = // TODO add default timeout (get_item_int32_default)
                    dap_config_get_item_int32(g_config, "traffic_track", "callback_timeout");

            dap_traffic_track_init( l_server, timeout );
            dap_traffic_callback_set( dap_chain_net_srv_traffic_callback );
            //dap_traffic_callback_set(db_auth_traffic_track_callback);
        }
#endif

        // TCP-specific things
		if ( dap_config_get_item_int32_default(g_config, "server", "listen_port_tcp",-1) > 0) {
            // Init HTTP-specific values
	    	dap_http_new( l_server, DAP_APP_NAME );

	        // Handshake URL
	        enc_http_add_proc( DAP_HTTP(l_server), ENC_HTTP_URL );

	        // Streaming URLs
	        dap_stream_add_proc_http( DAP_HTTP(l_server), STREAM_URL );
	        dap_stream_ctl_add_proc( DAP_HTTP(l_server), STREAM_CTL_URL );


	        const char *str_start_mempool = dap_config_get_item_str( g_config, "mempool", "accept" );
	        if ( str_start_mempool && !strcmp(str_start_mempool, "true")) {
	                dap_chain_mempool_add_proc(DAP_HTTP(l_server), MEMPOOL_URL);
	        }

	        // Built in WWW server

	        if (  dap_config_get_item_bool_default(g_config,"www","enabled",false)  ){
	                dap_http_folder_add( DAP_HTTP(l_server), "/",
	                                dap_config_get_item_str(g_config,
                                                                "resources",
                                                                "www_root") );
	        }

		}
    } else
        log_it( L_INFO, "No enabled server, working in client mode only" );


    // VPN channel
    if(dap_config_get_item_bool_default(g_config,"vpn_old","enabled",false)){
        dap_stream_ch_vpn_init(dap_config_get_item_str_default(g_config, "vpn_old", "network_address", NULL),
                   dap_config_get_item_str_default(g_config, "vpn_old", "network_mask", NULL));

    }

    // Chain Network init

	dap_stream_ch_chain_init( );
	dap_stream_ch_chain_net_init( );

///    dap_stream_ch_chain_net_srv_init();

    // New event loop init
	dap_events_init( 0, 0 );
	dap_events_t *l_events = dap_events_new( );
	dap_events_start( l_events );

///    if (dap_config_get_item_bool_default(g_config,"vpn","enabled",false))
///        dap_stream_ch_vpn_deinit();


    dap_chain_net_load_all();

#ifdef DAP_OS_LINUX
#ifndef __ANDROID__
    // If CDB module switched on
    if( dap_config_get_item_bool_default(g_config,"cdb","enabled",false) ) {
        if ( (rc=dap_chain_net_srv_vpn_cdb_init(DAP_HTTP( l_server ))) != 0 ){
            log_it(L_CRITICAL,"Can't init CDB module, return code %d",rc);
            return -3;

        }
        log_it(L_NOTICE, "Central DataBase (CDB) is initialized");
    }
#endif
#endif

	// Endless loop for server's requests processing
	rc = dap_server_loop(l_server);
	// After loop exit actions
	log_it( rc ? L_CRITICAL : L_NOTICE, "Server loop stopped with return code %d", rc );

    // Deinit modules

failure:

	dap_stream_deinit();
	dap_stream_ctl_deinit();
	dap_http_folder_deinit();
	dap_http_deinit();
	dap_server_deinit();
	dap_enc_ks_deinit();

	dap_config_close( g_config );
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

    pid_t pid = get_pid_from_file(s_pid_file_path);

	bool  mf = false;

	#ifdef _WIN32
        CreateMutexW( NULL, FALSE, (WCHAR *) L"DAP_CELLFRAME_NODE_74E9201D33F7F7F684D2FEF1982799A79B6BF94B568446A8D1DE947B00E3C75060F3FD5BF277592D02F77D7E50935E56" );

		if ( GetLastError( ) == 183 ) {
      		mf = true;
    	}
	#endif

	if ( (pid != 0 && is_process_running(pid)) || mf ) {
    	log_it( L_WARNING, "Proccess %d is running, don't allow "
        	                "to run more than one copy of DapServer, exiting...", pid );
		exit( -2 );
	}
}

