/*
 * Cellframe Node CLI compatibility layer
 * This file provides dap_chain_node_cli functions for cellframe-node
 * using the new dap_cli_server API from dap-sdk
 */

#include "dap_chain_node_cli_compat.h"
#include "dap_cli_server.h"
#include "dap_common.h"

#define LOG_TAG "node_cli_compat"

static bool s_debug_cli = false;

int dap_chain_node_cli_init(dap_config_t *g_config)
{
    if (!dap_config_get_item_bool_default(g_config, "cli-server", "enabled", true))
        return log_it(L_WARNING, "CLI server is disabled"), 0;
    
    s_debug_cli = dap_config_get_item_bool_default(g_config, "cli-server", "debug-cli", false);
    
    if (dap_cli_server_init(s_debug_cli, "cli-server")) {
        log_it(L_ERROR, "Can't init CLI server!");
        return -1;
    }
    
    // TODO: Register additional node-specific CLI commands here if needed
    // The basic CLI commands are registered by the SDK modules themselves
    
    log_it(L_INFO, "CLI server initialized successfully");
    return 0;
}

void dap_chain_node_cli_delete(void)
{
    dap_cli_server_deinit();
}
