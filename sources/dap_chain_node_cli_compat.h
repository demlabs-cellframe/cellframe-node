/*
 * Cellframe Node CLI compatibility layer
 * This file provides dap_chain_node_cli functions for cellframe-node
 * using the new dap_cli_server API from dap-sdk
 */

#pragma once

#include "dap_config.h"

#ifdef __cplusplus
extern "C" {
#endif

/**
 * Initialize the CLI server and register node commands
 * @param g_config - configuration object
 * @return 0 on success, non-zero on error
 */
int dap_chain_node_cli_init(dap_config_t *g_config);

/**
 * Deinitialize the CLI server
 */
void dap_chain_node_cli_delete(void);

#ifdef __cplusplus
}
#endif
