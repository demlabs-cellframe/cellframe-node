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
#define __USE_XOPEN_EXTENDED
#include <ftw.h>

#include "dap_config.h"
#include "dap_server.h"
#include "dap_http.h"
#include "dap_http_folder.h"
#include "dap_events.h"
#include "dap_enc.h"
#include "dap_enc_ks.h"
#include "dap_enc_http.h"

#include "dap_chain.h"
#include "dap_chain_wallet.h"

#include "dap_chain_gdb.h"

#include "dap_chain_net.h"
#include "dap_chain_net_srv.h"

#include "dap_chain_global_db.h"
#include "dap_chain_mempool.h"
#include "dap_chain_node_cli.h"

#include "dap_stream_session.h"
#include "dap_stream.h"
#include "dap_stream_ctl.h"

#include "dap_stream_ch_chain.h"
#include "dap_stream_ch_chain_net.h"

#include "dap_common.h"
#include "dap_client_remote.h"
#include "dap_client.h"
#include "dap_http_client.h"
#include "dap_http_client_simple.h"
#include "dap_http_simple.h"
#include "dap_process_manager.h"
#include "dap_traffic_track.h"
#include "dap_file_utils.h"
#include "dap_chain_node_cli_cmd.h"

#include "dap_tx_test.h"

static const char *wallet_from_create_args[] = {
    "wallet",
    "new",
    "-w", "wallet_from"
};

static const char *wallet_to_create_args[] = {
    "wallet",
    "new",
    "-w", "wallet_to"
};

static const char *mempool_proc_args[] = {
    "mempool_proc",
    "-net"          ,"local-testnet",
    "-chain"        ,"gdb"
};

typedef struct arg_data {
    char **call_args;
    char *str_reply;
} arg_data;

void *call_com_tx_create(void *arg) {
    arg_data *args = (arg_data*)arg;
    com_tx_create(15, args->call_args, &(args->str_reply));
    DAP_DELETE(args->str_reply);
    return NULL;
}

static int rm_r(const char *path, const struct stat *sbuf, int type, struct FTW *ftwb){
    return remove(path);
}

int cleanup() {
    if(dap_dir_test("./locale/var/lib/global_db")){
        nftw("./locale/var/lib/global_db", rm_r, 10, FTW_DEPTH | FTW_MOUNT | FTW_PHYS);
        mkdir("./locale/var/lib/global_db", S_IRWXU | S_IRWXG | S_IRWXO);
    }
    if(dap_dir_test("./locale/var/lib/wallet")){
        nftw("./locale/var/lib/wallet", rm_r, 10, FTW_DEPTH | FTW_MOUNT | FTW_PHYS);
        mkdir("./locale/var/lib/wallet", S_IRWXU | S_IRWXG | S_IRWXO);
    }
    return 0;
}

int dap_node_run_action(scenario_t action) {
    char *str_reply = NULL;
    if (action == VAIN) {
    } else if (action == EMIT) {
        dap_assert_PIF(com_tx_wallet(4, wallet_from_create_args, &str_reply) == 0, str_reply);
        dap_test_msg(str_reply);
        DAP_DELETE(str_reply);
        str_reply = NULL;

        dap_assert_PIF(com_tx_wallet(4, wallet_to_create_args, &str_reply) == 0, str_reply);
        dap_test_msg(str_reply);
        DAP_DELETE(str_reply);
        str_reply = NULL;

        dap_chain_wallet_t *l_wallet_from   = dap_chain_wallet_open_file("./locale/var/lib/wallet/wallet_from.dwallet");
        dap_chain_net_id_t l_net_id        = dap_chain_net_id_by_name("local-testnet");
        dap_chain_addr_t *l_addr_from       = dap_chain_wallet_get_addr(l_wallet_from, l_net_id);
        const char *l_addr_str_from         = dap_chain_addr_to_str(l_addr_from);
        dap_test_msg("%s", l_addr_str_from);
        dap_chain_wallet_close(l_wallet_from);

        const char *token_decl_args[] = {
            "token_decl",
            "-net"          ,"local-testnet",
            "-chain"        ,"gdb",
            "token"         ,"MAVRODI",
            "total_supply"  ,"1001000000000000",
            "signs_total"   ,"1",
            "signs_emission","1",
            "certs"         ,"mavrodi-cert"
        };

        dap_assert_PIF(com_token_decl(15, token_decl_args, &str_reply) == 0, str_reply);
        dap_test_msg(str_reply);
        DAP_DELETE(str_reply);
        str_reply = NULL;

        const char *token_emit_args[] = {
            "token_emit",
            "-net"              ,"local-testnet",
            "-chain_emission"   ,"gdb",
            "-chain_base_tx"    ,"gdb",
            "-addr"             ,l_addr_str_from,
            "-token"            ,"MAVRODI",
            "-certs"            ,"mavrodi-cert",
            "-emission_value"   ,"1001000000000000"
        };

        dap_assert_PIF(com_token_emit(15, token_emit_args, &str_reply) == 0, str_reply);
        dap_test_msg(str_reply);
        DAP_DELETE(str_reply);
        str_reply = NULL;

        dap_assert_PIF(com_mempool_proc(4, mempool_proc_args, &str_reply) == 0, str_reply);
        dap_test_msg(str_reply);
        DAP_DELETE(str_reply);
        str_reply = NULL;
        DAP_DELETE(l_addr_str_from);
    } else if (action == TX) {
        dap_chain_wallet_t *l_wallet_to = dap_chain_wallet_open_file("./locale/var/lib/wallet/wallet_to.dwallet");
        dap_chain_net_id_t l_net_id        = dap_chain_net_id_by_name("local-testnet");
        dap_chain_addr_t *l_addr_to     = dap_chain_wallet_get_addr(l_wallet_to, l_net_id);
        const char *l_addr_str_to       = dap_chain_addr_to_str(l_addr_to);
        dap_test_msg(l_addr_str_to);
        dap_chain_wallet_close(l_wallet_to);

        const char *tx_create_args[] = {
            "tx_create",
            "-net"          ,"local-testnet",
            "-chain"        ,"gdb",
            "-from_wallet"  ,"wallet_from",
            "-to_addr"      ,l_addr_str_to,
            "-token"        ,"MAVRODI",
            "-value"        ,"1000000000000",
            "-tx_num"       ,"200"
        };

        pthread_t thrds[5];
        arg_data args[5];
        for (int i = 0; i < 5; ++i) {
            args[i].call_args = tx_create_args;
            args[i].str_reply = NULL;
            pthread_create(&thrds[i], NULL, call_com_tx_create, (void*)&args[i]);
        }

        int status;
        for (int i = 0; i < 5; ++i) {
            pthread_join(thrds[i], (void**)&status);
        }
        DAP_DELETE(l_addr_str_to);
        dap_assert_PIF(com_mempool_proc(4, mempool_proc_args, &str_reply) == 0, str_reply);
    }
    else if (action == CHECK) {
        dap_chain_wallet_t *l_wallet_from   = dap_chain_wallet_open_file("./locale/var/lib/wallet/wallet_from.dwallet");
        dap_chain_net_id_t l_net_id        = dap_chain_net_id_by_name("local-testnet");
        dap_chain_addr_t *l_addr_from       = dap_chain_wallet_get_addr(l_wallet_from, l_net_id);

        dap_chain_wallet_t *l_wallet_to     = dap_chain_wallet_open_file("./locale/var/lib/wallet/wallet_to.dwallet");
        dap_chain_addr_t *l_addr_to         = dap_chain_wallet_get_addr(l_wallet_to, l_net_id);

        dap_ledger_t *l_ledger = dap_chain_ledger_by_net_name("local-testnet");
        size_t l_addr_tokens_size = 0;
        char **l_addr_tokens = NULL;
        dap_chain_ledger_addr_get_token_ticker_all_fast(l_ledger, l_addr_to, &l_addr_tokens, &l_addr_tokens_size);
        dap_assert_PIF(l_addr_tokens_size > 0, "No tokens found on wallet.");
        uint64_t l_balance_to = dap_chain_ledger_calc_balance(l_ledger, l_addr_to, l_addr_tokens[0]);
        dap_assert_PIF(l_balance_to == 1000000000000000, "Balance TO is not equal what it must be.");
        l_balance_to = dap_chain_ledger_calc_balance(l_ledger, l_addr_from, l_addr_tokens[0]);
        dap_assert_PIF(l_balance_to == 1000000000000, "Balance FROM is not equal what it must be.");
        DAP_DELETE(l_addr_tokens[0]);
        DAP_DELETE(l_addr_tokens);
        dap_chain_wallet_close(l_wallet_from);
        dap_chain_wallet_close(l_wallet_to);
    }
    return 0;
}

int dap_node_init() {
    dap_assert_PIF(dap_common_init("locale", "locale_logs.txt") == 0, "Can't init common functions module");
    dap_assert_PIF(dap_config_init("./locale/etc") == 0,     "Can't init config");
    g_config = dap_config_open("local");
    dap_assert_PIF(g_config != NULL,                        "Config not found");
    dap_assert_PIF(dap_server_init(1) == 0,                 "Can't init server");
    dap_assert_PIF(dap_http_init() == 0,                    "Can't init HTTP cli submodule");
    dap_http_folder_init();
    dap_assert_PIF(dap_enc_init() == 0,                     "Can't init encryption module");
    //dap_assert_PIF(dap_enc_ks_init(false, 60 *60 * 2) == 0, "Can't init encryption key storage module");
    dap_assert_PIF(dap_chain_global_db_init(g_config) == 0, "Can't init DB");
    dap_client_init();
    dap_http_client_simple_init();
    dap_datum_mempool_init();
    dap_assert_PIF(dap_chain_init() == 0,                   "Can't init CA storage");
    dap_chain_wallet_init();
    dap_chain_gdb_init();
    dap_chain_net_init();
    dap_chain_net_srv_init(g_config);
    enc_http_init();
    dap_stream_init(dap_config_get_item_bool_default(g_config, "general", "debug_dump_stream_headers", false));
    dap_stream_ctl_init(DAP_ENC_KEY_TYPE_OAES, 32);
    dap_http_simple_module_init();


    dap_assert_PIF(dap_chain_node_cli_init(g_config) == 0,  "Can't init server for console");

    dap_stream_ch_chain_init();
    dap_stream_ch_chain_net_init();
    dap_events_init(0, 0);
    dap_events_t *l_events = dap_events_new();
    dap_events_start(l_events);
    dap_chain_net_load_all();
    return 0;
}

int dap_node_deinit() {
    dap_stream_deinit();
    dap_stream_ctl_deinit();
    dap_http_folder_deinit();
    dap_http_deinit();
    dap_server_deinit();
    dap_enc_ks_deinit();
    dap_db_driver_deinit();
    //dap_config_close(g_config); // sisegv
    dap_common_deinit();
    return 0;
}

void dap_tx_tests_run() {
    cleanup();
    dap_node_init();
    dap_node_run_action(EMIT);
    dap_node_run_action(TX);
    dap_node_deinit();
    dap_node_init();
    dap_node_run_action(CHECK);
    dap_node_deinit();
}
