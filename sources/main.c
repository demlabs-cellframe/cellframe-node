#include <unistd.h>
#include <sys/types.h>
#include <getopt.h>
#include <signal.h>

#define LOG_TAG "main"

#include "dap_server.h"
#include "dap_http.h"
#include "dap_http_folder.h"
#include "dap_enc.h"
#include "dap_enc_ks.h"
#include "dap_enc_http.h"

#ifdef DAP_MOD_SERVER_LIST
#include "mods/serverlist/server_list.h"
#endif

#include "stream_session.h"
#include "stream.h"
#include "stream_ctl.h"
#include "dap_stream_ch_vpn.h"
#include "dap_common.h"
#include "db_http.h"
#include "db_http_file.h"
#include "auth/db_auth.h"
#include "dap_server_client.h"
#include "db_core.h"
#include "dap_http_simple.h"
#include "dap_process_manager.h"
#include "sig_unix_handler.h"
#include "dap_server_config.h"
#include "dap_traffic_track.h"

#define SERVER_FILENAME NODE_NETNAME "-node"
#define SERVER_PREFIX="/opt/"SERVER_FILENAME
#define CONFIG_DIR_PATH SERVER_PREFIX"/etc"
#define DEFAULT_PID_FILE_PATH SERVER_PREFIX"/run/dapserver.pid"

#define ENC_HTTP_URL "/enc_init"
#define STREAM_URL "/stream_url"
#define SLIST_URL "/nodelist"
#define MAIN_URL "/"

void parse_args(int argc, const char * argv[]);
void exit_if_server_already_running(void);

static dap_config_t * g_config;

int main(int argc, const char * argv[])
{
    dap_server_t * sh; // DAP Server instance
    int rc;

    if((g_config = dap_server_config_init(CONFIG_DIR_PATH)) == NULL) {
        log_it(L_CRITICAL,"Can't init general configurations module");
        return -1;
    }

    if(dap_common_init(SERVER_FILENAME"_logs.txt")!=0){
        log_it(L_CRITICAL,"Can't init common functions module");
        return -2;
    }

    parse_args(argc, argv);

    // change to dap_config_get_item_int_default when it's will be possible
    size_t thread_cnt = (size_t)sysconf(_SC_NPROCESSORS_ONLN);
    const char *s_thrd_cnt = dap_config_get_item_str(g_config, "configure", "threads_cnt");
    if(s_thrd_cnt != NULL)
        thread_cnt = (size_t)atoi(s_thrd_cnt);

    if(dap_server_init(thread_cnt)!=0){
        log_it(L_CRITICAL,"Can't init socket server module");
        return -4;
    }
    if(dap_http_init()!=0){
        log_it(L_CRITICAL,"Can't init http server module");
        return -5;
    }
    if(dap_http_folder_init()!=0){
        log_it(L_CRITICAL,"Can't init http server module");
        return -55;
    }

    if(dap_enc_init() !=0){
        log_it(L_CRITICAL,"Can't init encryption module");
        return -56;
    }

    if(dap_enc_ks_init() !=0){
        log_it(L_CRITICAL,"Can't init encryption key storage module");
        return -57;
    }

    if(enc_http_init() !=0){
        log_it(L_CRITICAL,"Can't init encryption http session storage module");
        return -58;
    }

    if(stream_init() != 0 ){
        log_it(L_CRITICAL,"Can't init stream server module");
        return -6;
    }

    if (stream_ctl_init() != 0 ){
        log_it(L_CRITICAL,"Can't init stream control module");
        return -7;
    }

    if ( dap_http_simple_module_init() != 0 ) {
        log_it(L_CRITICAL,"Can't init http simple module");
        return -9;
    }

    if (sig_unix_handler_init(dap_config_get_item_str_default(g_config,
                                                              "resources",
                                                              "pid_path",
                                                              DEFAULT_PID_FILE_PATH)) != 0) {
        log_it(L_CRITICAL,"Can't init sig unix handler module");
        return -9;
    }

    save_process_pid_in_file(dap_config_get_item_str_default(g_config,
                                                             "resources",
                                                             "pid_path",
                                                             SERVER_PREFIX"/run/dapserver.pid"));

    sh = dap_server_listen((dap_config_get_item_str_default(g_config,
                                                            "network",
                                                            "listen_address",
                                                            "0.0.0.0")),
                           dap_config_get_item_int32(g_config, "network", "listen_port"), // TODO DEFAULT PORT
                           DAP_SERVER_TCP);

    if(sh) {
        bool is_traffick_track_enable = // TODO change to get_item_bool_feault
                strcmp(dap_config_get_item_str_default(g_config, "traffic_track", "enable", "false"), "true") == 0;

        if(is_traffick_track_enable) {
            time_t timeout = // TODO add default timeout (get_item_int32_default)
                    dap_config_get_item_int32(g_config, "traffic_track", "callback_timeout");

            dap_traffic_track_init(sh, timeout);
            dap_traffic_callback_set(db_auth_traffic_track_callback);
        }

        // Init HTTP-specific values
        dap_http_new(sh,SERVER_FILENAME "DAPServer/1.0 (QNX)");



        dap_http_folder_add(DAP_HTTP(sh), "/",
                            dap_config_get_item_str_default(g_config,
                                                            "resources",
                                                            "www_root",
                                                            "/opt/dapserver/www"));

        server_list_add_proc(DAP_HTTP(sh), SLIST_URL);
        db_http_add_proc(DAP_HTTP(sh), DB_URL);
        db_http_file_proc_add(DAP_HTTP(sh), DB_HTTP_FILE_URL);
        stream_add_proc_http(DAP_HTTP(sh), STREAM_URL);
        stream_ctl_add_proc(DAP_HTTP(sh), CTL_URL);

        enc_http_add_proc(DAP_HTTP(sh), ENC_HTTP_URL);
        ch_sf_init(dap_config_get_item_str_default(g_config, "network", "vpn_addr", "10.0.0.0"),
                   dap_config_get_item_str_default(g_config, "network", "vpn_mask", "255.255.255.0"));

        // Endless loop for server's requests processing
        rc = dap_server_loop(sh);
        // After loop exit actions
        log_it(rc?L_CRITICAL:L_NOTICE,"Server loop stopped with return code %d",rc);

        // Deinit modules
        stream_deinit();
        stream_ctl_deinit();
        db_http_deinit();
        dap_http_folder_deinit();
        dap_http_deinit();
        dap_server_deinit();
        db_core_deinit();
        dap_enc_ks_deinit();
        dap_common_deinit();
        server_list_module_deinit();
        return rc*10;
    }
}

void parse_args(int argc, const char * argv[]) {
    int opt, option_index = 0, is_daemon = 0;
    struct option long_options[] = {
        {"stop", 0, NULL, 0},
        {0, 0, NULL, 0} // mast be a last element
    };

    while ((opt = getopt_long(argc, (char *const *)argv, "D0",
                              long_options, &option_index)) != -1) {
        switch (opt) {
        case 0: { // --stop
            pid_t pid = get_pid_from_file(dap_config_get_item_str_default(g_config,
                                                                          "resources",
                                                                          "pid_path",
                                                                          DEFAULT_PID_FILE_PATH));
            if (pid == 0) {
                log_it(L_ERROR, "Can't read pid from file");
                exit(-20);
            } else if(kill_process(pid)) {
                log_it(L_INFO, "Server successfully stopped");
                exit(0);
            }
            log_it(L_WARNING, "Server not stopped. Maybe he is not running now?");
            exit(-21);
        }
        case 'D':
            log_it(L_INFO, "Daemonize server starting...");
            exit_if_server_already_running();
            is_daemon = 1;
            daemonize_process();
            break;
        default:
            log_it(L_WARNING, "Unknown option from command line");
        }
    }

    if(!is_daemon)
        exit_if_server_already_running();
}

void exit_if_server_already_running(void) {
    pid_t pid = get_pid_from_file(dap_config_get_item_str(g_config, "resources", "pid_path"));
    if (pid != 0 && is_process_running(pid)) {
        log_it(L_WARNING, "Proccess %d is running, don't allow "
                          "to run more than one copy of DapServer, exiting...", pid);
        exit(-2);
    }
}

