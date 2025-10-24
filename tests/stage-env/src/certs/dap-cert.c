/**
 * @file dap-cert.c
 * @brief DAP Certificate Management Tool
 * @details Universal certificate utility 
 * 
 * Commands:
 *   create    - Create new certificate
 *   info      - Show certificate information
 *   addr      - Generate validator address from certificate (base58 long format)
 *   node-addr - Extract node address from certificate (short format for authorized_nodes_addrs)
 * 
 * @author Dmitrii A. Gearasimov <gerasimov.dmitriy@demlabs.net>
 * @date 2025-09-30
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <inttypes.h>

/* DAP SDK includes */
#include "dap_common.h"
#include "dap_cert.h"
#include "dap_cert_file.h"
#include "dap_enc_key.h"
#include "dap_enc_base58.h"
#include "dap_chain_common.h"
#include "dap_stream.h"

#define LOG_TAG "dap-cert"

/* Global debug flag for detailed logging */
static bool s_debug_more = false;

/* Return codes following DAP SDK convention */
#define DAP_CERT_SUCCESS  0
#define DAP_CERT_ERROR   -1

/* Command handlers */
typedef int (*dap_cert_cmd_handler_t)(int argc, char **argv);

/**
 * @brief Parse signature type from string
 * @param a_type_str Signature type string
 * @return Signature type enum or INVALID
 */
static dap_enc_key_type_t s_parse_sig_type(const char *a_type_str)
{
    dap_return_val_if_pass(!a_type_str, DAP_ENC_KEY_TYPE_INVALID);
    
    if (dap_strcmp(a_type_str, "dilithium") == 0) 
        return DAP_ENC_KEY_TYPE_SIG_DILITHIUM;
    if (dap_strcmp(a_type_str, "falcon") == 0) 
        return DAP_ENC_KEY_TYPE_SIG_FALCON;
    if (dap_strcmp(a_type_str, "sphincsplus") == 0) 
        return DAP_ENC_KEY_TYPE_SIG_SPHINCSPLUS;
    if (dap_strcmp(a_type_str, "picnic") == 0) 
        return DAP_ENC_KEY_TYPE_SIG_PICNIC;
    
    return DAP_ENC_KEY_TYPE_INVALID;
}

/**
 * @brief Generate validator address from certificate
 * @param a_cert Certificate
 * @param a_addr_out Output buffer for address string  
 * @param a_addr_size Output buffer size
 * @param a_net_id Network ID
 * @return DAP_CERT_SUCCESS or DAP_CERT_ERROR
 */
static int s_generate_validator_address(dap_cert_t *a_cert, char *a_addr_out, 
                                        size_t a_addr_size, dap_chain_net_id_t a_net_id)
{
    dap_return_val_if_pass(!a_cert || !a_cert->enc_key || !a_addr_out, DAP_CERT_ERROR);
    
    debug_if(s_debug_more, L_DEBUG, "Generating validator address for cert, network_id=0x%016" PRIx64, 
             a_net_id.uint64);
    
    /* Create address from certificate key */
    dap_chain_addr_t l_addr;
    memset(&l_addr, 0, sizeof(l_addr));
    
    int l_ret = dap_chain_addr_fill_from_key(&l_addr, a_cert->enc_key, a_net_id);
    dap_return_val_if_pass(l_ret != 0, DAP_CERT_ERROR);
    
    /* Convert address to string */
    const char *l_addr_str = dap_chain_addr_to_str(&l_addr);
    dap_return_val_if_pass(!l_addr_str, DAP_CERT_ERROR);
    
    /* Safe copy to output */
    dap_strncpy(a_addr_out, l_addr_str, a_addr_size);
    
    debug_if(s_debug_more, L_DEBUG, "Validator address: %s", a_addr_out);
    return DAP_CERT_SUCCESS;
}

/**
 * @brief Command: create - Create new certificate
 * Usage: dap-cert create <name> <output_path> <sig_type> <network_id>
 */
static int s_cmd_create(int argc, char **argv)
{
    dap_return_val_if_pass(argc < 4, DAP_CERT_ERROR);
    
    const char *l_cert_name = argv[0];
    const char *l_output_path = argv[1];
    const char *l_sig_type_str = argv[2];
    const char *l_net_id_str = argv[3];
    
    debug_if(s_debug_more, L_INFO, "Creating certificate: %s", l_cert_name);
    
    /* Parse signature type */
    dap_enc_key_type_t l_sig_type = s_parse_sig_type(l_sig_type_str);
    if (l_sig_type == DAP_ENC_KEY_TYPE_INVALID) {
        log_it(L_ERROR, "Invalid signature type: %s", l_sig_type_str);
        log_it(L_ERROR, "Supported: dilithium, falcon, sphincsplus, picnic");
        return DAP_CERT_ERROR;
    }
    
    /* Parse network ID */
    char *l_endptr;
    uint64_t l_net_id_uint = strtoull(l_net_id_str, &l_endptr, 0);
    dap_return_val_if_pass(*l_endptr != '\0' || l_net_id_uint == 0, DAP_CERT_ERROR);
    
    dap_chain_net_id_t l_net_id = { .uint64 = l_net_id_uint };
    
    log_it(L_INFO, "Generating certificate '%s' with %s signature", l_cert_name, l_sig_type_str);
    log_it(L_INFO, "Network ID: 0x%016" PRIx64, l_net_id.uint64);
    
    /* Generate certificate in memory */
    dap_cert_t *l_cert = dap_cert_generate_mem(l_cert_name, l_sig_type);
    dap_return_val_if_pass(!l_cert, DAP_CERT_ERROR);
    
    debug_if(s_debug_more, L_DEBUG, "Certificate generated in memory");
    
    /* Generate validator address */
    char l_validator_addr[DAP_ENC_BASE58_ENCODE_SIZE(sizeof(dap_chain_addr_t))];
    int l_ret = s_generate_validator_address(l_cert, l_validator_addr, 
                                             sizeof(l_validator_addr), l_net_id);
    if (l_ret != DAP_CERT_SUCCESS) {
        dap_cert_delete(l_cert);
        return DAP_CERT_ERROR;
    }
    
    /* Save certificate to file */
    if (dap_cert_file_save(l_cert, l_output_path) != 0) {
        log_it(L_ERROR, "Failed to save certificate: %s", l_output_path);
        dap_cert_delete(l_cert);
        return DAP_CERT_ERROR;
    }
    
    log_it(L_NOTICE, "Certificate created: %s", l_output_path);
    log_it(L_NOTICE, "Validator address: %s", l_validator_addr);
    
    /* Output validator address to stdout for scripting */
    printf("%s\n", l_validator_addr);
    
    dap_cert_delete(l_cert);
    return DAP_CERT_SUCCESS;
}

/**
 * @brief Command: info - Show certificate information
 * Usage: dap-cert info <cert_path>
 */
static int s_cmd_info(int argc, char **argv)
{
    dap_return_val_if_pass(argc < 1, DAP_CERT_ERROR);
    
    const char *l_cert_path = argv[0];
    
    dap_cert_t *l_cert = dap_cert_file_load(l_cert_path);
    dap_return_val_if_pass(!l_cert, DAP_CERT_ERROR);
    
    log_it(L_INFO, "Certificate: %s", l_cert_path);
    log_it(L_INFO, "Name: %s", l_cert->name);
    
    if (l_cert->enc_key) {
        log_it(L_INFO, "Key type: %d", l_cert->enc_key->type);
        log_it(L_INFO, "Key size: %zu bytes", l_cert->enc_key->priv_key_data_size);
    }
    
    dap_cert_delete(l_cert);
    return DAP_CERT_SUCCESS;
}

/**
 * @brief Command: addr - Generate validator address
 * Usage: dap-cert addr <cert_path> <network_id>
 */
static int s_cmd_addr(int argc, char **argv)
{
    dap_return_val_if_pass(argc < 2, DAP_CERT_ERROR);
    
    const char *l_cert_path = argv[0];
    const char *l_net_id_str = argv[1];
    
    /* Parse network ID */
    char *l_endptr;
    uint64_t l_net_id_uint = strtoull(l_net_id_str, &l_endptr, 0);
    dap_return_val_if_pass(*l_endptr != '\0' || l_net_id_uint == 0, DAP_CERT_ERROR);
    
    dap_chain_net_id_t l_net_id = { .uint64 = l_net_id_uint };
    
    /* Load certificate */
    dap_cert_t *l_cert = dap_cert_file_load(l_cert_path);
    dap_return_val_if_pass(!l_cert, DAP_CERT_ERROR);
    
    /* Generate address */
    char l_addr[DAP_ENC_BASE58_ENCODE_SIZE(sizeof(dap_chain_addr_t))];
    int l_ret = s_generate_validator_address(l_cert, l_addr, sizeof(l_addr), l_net_id);
    
    dap_cert_delete(l_cert);
    dap_return_val_if_pass(l_ret != DAP_CERT_SUCCESS, DAP_CERT_ERROR);
    
    /* Output address */
    printf("%s\n", l_addr);
    return DAP_CERT_SUCCESS;
}

/**
 * @brief Command: node-addr - Extract short node address from certificate
 * Usage: dap-cert node-addr <cert_path>
 * @details Extracts dap_stream_node_addr_t (short format like 3FDA::0325::3A71::2C74)
 *          This is the format needed for authorized_nodes_addrs in chain config
 */
static int s_cmd_node_addr(int argc, char **argv)
{
    dap_return_val_if_pass(argc < 1, DAP_CERT_ERROR);
    
    const char *l_cert_path = argv[0];
    
    /* Load certificate */
    dap_cert_t *l_cert = dap_cert_file_load(l_cert_path);
    if (!l_cert) {
        log_it(L_ERROR, "Can't read specified certificate %s", l_cert_path);
        return DAP_CERT_ERROR;
    }
    
    /* Extract node address (dap_stream_node_addr_t) */
    dap_stream_node_addr_t l_node_addr = dap_stream_node_addr_from_cert(l_cert);
    
    dap_cert_delete(l_cert);
    
    /* Check if address is valid (not all zeros) */
    if (l_node_addr.uint64 == 0) {
        log_it(L_ERROR, "Failed to extract node address from certificate");
        return DAP_CERT_ERROR;
    }
    
    /* Convert to string format (short address) */
    const char *l_addr_str = dap_stream_node_addr_to_str_static(l_node_addr);
    if (!l_addr_str) {
        log_it(L_ERROR, "Failed to convert node address to string");
        return DAP_CERT_ERROR;
    }
    
    /* Output short address */
    printf("%s\n", l_addr_str);
    return DAP_CERT_SUCCESS;
}

/**
 * @brief Print usage information
 */
static void s_print_usage(const char *a_prog_name)
{
    printf("DAP Certificate Management Tool\n");
    printf("\n");
    printf("Usage: %s <command> [arguments]\n", a_prog_name);
    printf("\n");
    printf("Commands:\n");
    printf("  create <name> <output> <sig_type> <net_id>\n");
    printf("      Create new certificate\n");
    printf("      sig_type: dilithium, falcon, sphincsplus, picnic\n");
    printf("      net_id: hex format (e.g. 0x1234)\n");
    printf("\n");
    printf("  info <cert_path>\n");
    printf("      Show certificate information\n");
    printf("\n");
    printf("  addr <cert_path> <net_id>\n");
    printf("      Generate validator address from certificate (base58 long format)\n");
    printf("\n");
    printf("  node-addr <cert_path>\n");
    printf("      Extract node address from certificate (short format for authorized_nodes_addrs)\n");
    printf("      Output format: 3FDA::0325::3A71::2C74\n");
    printf("\n");
    printf("Examples:\n");
    printf("  %s create stagenet.master.pvt.0 /certs/cert.dcert dilithium 0x1234\n", a_prog_name);
    printf("  %s info /certs/cert.dcert\n", a_prog_name);
    printf("  %s addr /certs/cert.dcert 0x1234\n", a_prog_name);
    printf("  %s node-addr /certs/node-addr.dcert\n", a_prog_name);
}

/**
 * @brief Main entry point
 */
int main(int argc, char **argv)
{
    int l_ret = DAP_CERT_ERROR;
    
    if (argc < 2) {
        s_print_usage(argv[0]);
        return DAP_CERT_ERROR;
    }
    
    const char *l_cmd = argv[1];
    
    /* Initialize DAP SDK */
    dap_log_level_set(L_INFO);
    dap_enc_key_init();
    
    debug_if(s_debug_more, L_DEBUG, "Initialized DAP SDK crypto");
    
    /* Dispatch command */
    if (dap_strcmp(l_cmd, "create") == 0) {
        l_ret = s_cmd_create(argc - 2, argv + 2);
    } else if (dap_strcmp(l_cmd, "info") == 0) {
        l_ret = s_cmd_info(argc - 2, argv + 2);
    } else if (dap_strcmp(l_cmd, "addr") == 0) {
        l_ret = s_cmd_addr(argc - 2, argv + 2);
    } else if (dap_strcmp(l_cmd, "node-addr") == 0) {
        l_ret = s_cmd_node_addr(argc - 2, argv + 2);
    } else {
        log_it(L_ERROR, "Unknown command: %s", l_cmd);
        s_print_usage(argv[0]);
        l_ret = DAP_CERT_ERROR;
    }
    
    /* Cleanup */
    dap_enc_key_deinit();
    
    return l_ret == DAP_CERT_SUCCESS ? 0 : 1;
}
