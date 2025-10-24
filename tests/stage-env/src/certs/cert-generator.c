/**
 * @file cert-generator.c
 * @brief DAP Certificate Generator for Cellframe Node E2E Testing
 * @details Generates real DAP certificates using DAP SDK crypto module
 * 
 * @author Cellframe Development Team
 * @date 2025-09-30
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/stat.h>
#include <time.h>
#include <errno.h>
#include <stdint.h>
#include <stdarg.h>

/* DAP SDK includes */
#include "dap_common.h"
#include "dap_cert.h"
#include "dap_cert_file.h"
#include "dap_enc_key.h"
#include "dap_enc_base58.h"
#include "dap_sign.h"
#include "dap_hash.h"
#include "dap_chain_common.h"
#include "dap_stream.h"

/* === Constants === */
#define LOG_TAG "cf-cert-generator"

/* Debug flag for verbose logging */
static bool s_debug_more = false;

/* Buffer sizes following DAP SDK conventions */
#define DAP_CERT_GEN_MAX_NODE_NAME_LEN       32
#define DAP_CERT_GEN_MAX_CERT_NAME_LEN       128
/* Use DAP SDK constant for address string size */
#define DAP_CERT_GEN_MAX_VALIDATOR_ADDR_LEN  DAP_ENC_BASE58_ENCODE_SIZE(sizeof(dap_chain_addr_t))
#define DAP_CERT_GEN_MAX_PATH_LEN            512
#define DAP_CERT_GEN_MAX_TIMESTAMP_LEN       64
#define DAP_CERT_GEN_FILE_BUFFER_SIZE        4096

/* Node configuration constants */
#define DAP_CERT_GEN_BASE_IP_OFFSET          9
#define DAP_CERT_GEN_CHAIN_ID_HEX           "0x1234"
#define DAP_CERT_GEN_MAX_NODE_COUNT          100 /* Maximum supported nodes */

/* Address generation constants */
#define DAP_CERT_GEN_ADDR_COMPONENTS        4
#define DAP_CERT_GEN_ADDR_COMPONENT_BITS    16

/* File permissions */
#define DAP_CERT_GEN_DIR_PERMISSIONS        0755
#define DAP_CERT_GEN_FILE_PERMISSIONS       0644

/* Return codes */
#define DAP_CERT_GEN_RET_SUCCESS            0
#define DAP_CERT_GEN_RET_ERROR              -1

/* === Data Structures === */

/**
 * @struct dap_cert_generator_node_t
 * @brief Structure representing a node certificate
 */
typedef struct dap_cert_generator_node {
    char node_name[DAP_CERT_GEN_MAX_NODE_NAME_LEN];
    int node_id;
    char validator_addr[DAP_CERT_GEN_MAX_VALIDATOR_ADDR_LEN];
    char cert_path[DAP_CERT_GEN_MAX_PATH_LEN];
    dap_cert_t *cert;
} dap_cert_generator_node_t;

/* === Forward Declarations === */
static int s_safe_strncpy(char *a_dest, size_t a_dest_size, const char *a_src);
static int s_safe_snprintf(char *a_dest, size_t a_dest_size, const char *a_format, ...);
static int s_create_directory(const char *a_path);
static int s_validator_address_generate(dap_cert_t *a_cert, char *a_addr_out, size_t a_addr_size, uint64_t a_network_id);
static int s_copy_file(const char *a_src_path, const char *a_dst_path);
static int s_save_to_file(const char *a_file_path, const char *a_content);
static int s_node_certificate_generate(dap_cert_generator_node_t *a_node, const char *a_output_dir, const char *a_network_name, uint64_t a_network_id);
static int s_pki_config_generate(const dap_cert_generator_node_t *a_nodes, int a_node_count, const char *a_output_dir);

/* === Helper Functions === */

/**
 * @brief Safely copy string with size checking
 */
static int s_safe_strncpy(char *a_dest, size_t a_dest_size, const char *a_src) {
    if (!a_dest || !a_src || a_dest_size == 0) {
        log_it(L_ERROR, "Invalid parameters for s_safe_strncpy");
        return DAP_CERT_GEN_RET_ERROR;
    }
    
    size_t l_src_len = strlen(a_src);
    if (l_src_len >= a_dest_size) {
        log_it(L_ERROR, "String truncation would occur (len=%zu, max=%zu)", 
               l_src_len, a_dest_size - 1);
        return DAP_CERT_GEN_RET_ERROR;
    }
    
    strncpy(a_dest, a_src, a_dest_size - 1);
    a_dest[a_dest_size - 1] = '\0';
    return DAP_CERT_GEN_RET_SUCCESS;
}

/**
 * @brief Safely format string with size checking
 */
static int s_safe_snprintf(char *a_dest, size_t a_dest_size, const char *a_format, ...) {
    if (!a_dest || !a_format || a_dest_size == 0) {
        log_it(L_ERROR, "Invalid parameters for s_safe_snprintf");
        return DAP_CERT_GEN_RET_ERROR;
    }
    
    va_list l_args;
    va_start(l_args, a_format);
    int l_result = vsnprintf(a_dest, a_dest_size, a_format, l_args);
    va_end(l_args);
    
    if (l_result < 0 || (size_t)l_result >= a_dest_size) {
        log_it(L_ERROR, "snprintf truncation or error (result=%d, size=%zu)", 
               l_result, a_dest_size);
        return DAP_CERT_GEN_RET_ERROR;
    }
    
    return DAP_CERT_GEN_RET_SUCCESS;
}

/**
 * @brief Create directory with proper error handling
 */
static int s_create_directory(const char *a_path) {
    if (!a_path || strlen(a_path) == 0) {
        log_it(L_ERROR, "Invalid directory path");
        return DAP_CERT_GEN_RET_ERROR;
    }
    
    struct stat l_st = {0};
    
    if (stat(a_path, &l_st) == 0) {
        if (S_ISDIR(l_st.st_mode)) {
            return DAP_CERT_GEN_RET_SUCCESS;
        } else {
            log_it(L_ERROR, "Path exists but is not a directory: %s", a_path);
            return DAP_CERT_GEN_RET_ERROR;
        }
    }
    
    if (mkdir(a_path, DAP_CERT_GEN_DIR_PERMISSIONS) != 0) {
        log_it(L_ERROR, "Failed to create directory %s: %s", a_path, strerror(errno));
        return DAP_CERT_GEN_RET_ERROR;
    }
    
    return DAP_CERT_GEN_RET_SUCCESS;
}

/**
 * @brief Generate validator address from certificate public key
 * Uses proper DAP SDK function for address generation
 * @param cert Certificate to generate address from
 * @param addr_out Output buffer for address string
 * @param addr_size Size of output buffer
 * @param network_id Network ID to use for address generation
 */
static int s_validator_address_generate(dap_cert_t *a_cert, char *a_addr_out, size_t a_addr_size, uint64_t a_network_id) {
    dap_return_val_if_pass(!a_cert || !a_cert->enc_key || !a_addr_out || a_addr_size < DAP_CERT_GEN_MAX_VALIDATOR_ADDR_LEN, DAP_CERT_GEN_RET_ERROR);
    
    debug_if(s_debug_more, L_DEBUG, "Generating validator node address for cert=%p, network_id=0x%llX", 
             (void*)a_cert, (unsigned long long)a_network_id);
    
    /* Generate node address from certificate (NOT wallet address!) */
    /* cellframe network node addresses in format: 1234::5678::9ABC::DEF0 */
    dap_stream_node_addr_t l_node_addr = dap_stream_node_addr_from_cert(a_cert);
    
    if (l_node_addr.uint64 == 0) {
        log_it(L_ERROR, "Failed to generate node address from certificate");
        return DAP_CERT_GEN_RET_ERROR;
    }
    
    debug_if(s_debug_more, L_DEBUG, "Node address structure generated, converting to string");
    
    /* Convert node address to hex string format: 1234::5678::9ABC::DEF0 */
    char *l_addr_str = dap_stream_node_addr_to_str(l_node_addr, false);
    if (!l_addr_str) {
        log_it(L_ERROR, "Failed to convert node address to string");
        return DAP_CERT_GEN_RET_ERROR;
    }
    
    /* Copy to output buffer with safety check */
    int l_result = s_safe_strncpy(a_addr_out, a_addr_size, l_addr_str);
    DAP_DELETE(l_addr_str);
    
    dap_return_val_if_pass(l_result != DAP_CERT_GEN_RET_SUCCESS, DAP_CERT_GEN_RET_ERROR);
    
    debug_if(s_debug_more, L_DEBUG, "Validator node address generated successfully: %s", a_addr_out);
    return DAP_CERT_GEN_RET_SUCCESS;
}

/**
 * @brief Copy file safely
 */
static int s_copy_file(const char *src_path, const char *dst_path) {
    if (!src_path || !dst_path) {
        log_it(L_ERROR, "Invalid file paths for copy operation");
        return DAP_CERT_GEN_RET_ERROR;
    }
    
    FILE *src = fopen(src_path, "rb");
    dap_return_val_if_pass(!src, DAP_CERT_GEN_RET_ERROR);
    
    FILE *dst = fopen(dst_path, "wb");
    if (!dst) {
        fclose(src);
        log_it(L_ERROR, "Failed to open destination file %s", dst_path);
        return DAP_CERT_GEN_RET_ERROR;
    }
    
    char buffer[DAP_CERT_GEN_FILE_BUFFER_SIZE];
    size_t bytes_read;
    int result = DAP_CERT_GEN_RET_SUCCESS;
    
    while ((bytes_read = fread(buffer, 1, sizeof(buffer), src)) > 0) {
        size_t bytes_written = fwrite(buffer, 1, bytes_read, dst);
        if (bytes_written != bytes_read) {
            log_it(L_ERROR, "Write error during file copy");
            result = DAP_CERT_GEN_RET_ERROR;
            break;
        }
    }
    
    fclose(src);
    fclose(dst);
    
    if (result == DAP_CERT_GEN_RET_SUCCESS && chmod(dst_path, DAP_CERT_GEN_FILE_PERMISSIONS) != 0) {
        log_it(L_WARNING, "Failed to set permissions on %s", dst_path);
    }
    
    return result;
}

/**
 * @brief Save text to file
 */
static int s_save_to_file(const char *file_path, const char *content) {
    if (!file_path || !content) {
        log_it(L_ERROR, "Invalid parameters for s_save_to_file");
        return DAP_CERT_GEN_RET_ERROR;
    }
    
    FILE *fp = fopen(file_path, "w");
    dap_return_val_if_pass(!fp, DAP_CERT_GEN_RET_ERROR);
    
    fprintf(fp, "%s\n", content);
    fclose(fp);
    
    if (chmod(file_path, DAP_CERT_GEN_FILE_PERMISSIONS) != 0) {
        log_it(L_WARNING, "Failed to set permissions on %s", file_path);
    }
    
    return DAP_CERT_GEN_RET_SUCCESS;
}

/**
 * @brief Generate node certificate using DAP SDK crypto
 */
static int s_node_certificate_generate(dap_cert_generator_node_t *node, const char *output_dir, const char *network_name, uint64_t network_id) {
    if (!node || !output_dir) {
        log_it(L_ERROR, "Invalid parameters for certificate generation");
        return DAP_CERT_GEN_RET_ERROR;
    }
    
    char node_dir[DAP_CERT_GEN_MAX_PATH_LEN];
    char cert_name[DAP_CERT_GEN_MAX_CERT_NAME_LEN];
    char cert_file_main[DAP_CERT_GEN_MAX_PATH_LEN];
    char cert_file_esbocs[DAP_CERT_GEN_MAX_PATH_LEN];
    char addr_file[DAP_CERT_GEN_MAX_PATH_LEN];
    
    /* Build paths */
    dap_return_val_if_pass(s_safe_snprintf(node_dir, sizeof(node_dir), 
                                          "%s/%s", output_dir, node->node_name) != DAP_CERT_GEN_RET_SUCCESS, 
                          DAP_CERT_GEN_RET_ERROR);
    
    /* Use standard Cellframe node certificate name */
    dap_return_val_if_pass(s_safe_snprintf(cert_name, sizeof(cert_name), 
                                          "node-addr") != DAP_CERT_GEN_RET_SUCCESS, 
                          DAP_CERT_GEN_RET_ERROR);
    
    /* Create node directory */
    dap_return_val_if_pass(s_create_directory(node_dir) != DAP_CERT_GEN_RET_SUCCESS, DAP_CERT_GEN_RET_ERROR);
    
    /* Save node directory path */
    dap_return_val_if_pass(s_safe_strncpy(node->cert_path, sizeof(node->cert_path), 
                                         node_dir) != DAP_CERT_GEN_RET_SUCCESS, 
                          DAP_CERT_GEN_RET_ERROR);
    
    log_it(L_INFO, "Generating certificate for %s (node_id=%d)", node->node_name, node->node_id);
    debug_if(s_debug_more, L_DEBUG, "Calling dap_cert_generate_mem for %s", cert_name);
    
    /* Generate DAP certificate in memory with Dilithium signature */
    node->cert = dap_cert_generate_mem(cert_name, DAP_ENC_KEY_TYPE_SIG_FALCON);
    if (!node->cert) {
        log_it(L_ERROR, "Failed to generate DAP certificate for %s", node->node_name);
        return DAP_CERT_GEN_RET_ERROR;
    }
    
    debug_if(s_debug_more, L_DEBUG, "Certificate generated in memory, saving to files");
    log_it(L_INFO, "Certificate generated successfully with Dilithium key");
    log_it(L_INFO, "  node->cert pointer: %p", (void*)node->cert);
    
    /* Save certificate to files FIRST (before extracting address) */
    if (s_safe_snprintf(cert_file_main, sizeof(cert_file_main), 
                      "%s/%s.dcert", node_dir, cert_name) != DAP_CERT_GEN_RET_SUCCESS) {
        dap_cert_delete(node->cert);
        node->cert = NULL;
        return DAP_CERT_GEN_RET_ERROR;
    }
    
    log_it(L_INFO, "About to save node->cert to: %s (cert pointer=%p)", cert_file_main, (void*)node->cert);
    /* Save certificate to file using DAP SDK function */
    if (dap_cert_file_save(node->cert, cert_file_main) != 0) {
        log_it(L_ERROR, "Failed to save certificate to file: %s", cert_file_main);
        dap_cert_delete(node->cert);
        node->cert = NULL;
        return DAP_CERT_GEN_RET_ERROR;
    }
    
    debug_if(s_debug_more, L_DEBUG, "Certificate saved to %s", cert_file_main);
    log_it(L_INFO, "Certificate file saved: %s", cert_file_main);
    
    /* Generate NODE address from node-addr.dcert (for node_addr.txt) */
    char node_addr_str[DAP_CERT_GEN_MAX_VALIDATOR_ADDR_LEN];
    if (s_validator_address_generate(node->cert, node_addr_str, 
                                   sizeof(node_addr_str), network_id) != DAP_CERT_GEN_RET_SUCCESS) {
        log_it(L_ERROR, "Failed to generate node address");
        dap_cert_delete(node->cert);
        node->cert = NULL;
        return DAP_CERT_GEN_RET_ERROR;
    }
    
    debug_if(s_debug_more, L_DEBUG, "Node address generated from node-addr.dcert: %s", node_addr_str);
    
    /* Save NODE address (this is for general node identification) */
    if (s_safe_snprintf(addr_file, sizeof(addr_file), 
                      "%s/node_addr.txt", node_dir) == DAP_CERT_GEN_RET_SUCCESS) {
        s_save_to_file(addr_file, node_addr_str);
        log_it(L_INFO, "Node address saved: %s", node_addr_str);
    }
    /* Delete node->cert to ensure it does not interfere with validator cert */
    dap_cert_delete(node->cert);
    node->cert = NULL;
    
    /* Create SEPARATE VALIDATOR certificate for ESBocs (not related to node-addr!) */
    /* ESBOCS expects certificates named as: {network}.master.{index} (auth_certs_prefix in chain config) */
    /* Private cert: pvt.stagenet.master.0.dcert (with private key, only for this node) */
    /* Public cert: stagenet.master.0.dcert (without private key, for all nodes) */
    /* Note: Only root/seed nodes (first N nodes) get validator certificates */
    
    log_it(L_INFO, "Generating SEPARATE validator certificate for %s", node->node_name);
    
    /* Generate NEW certificate for validator (separate from node-addr!) */
    /* CRITICAL: Use UNIQUE name with index to avoid "already present in memory" errors */
    char l_validator_cert_name[DAP_CERT_GEN_MAX_CERT_NAME_LEN];
    snprintf(l_validator_cert_name, sizeof(l_validator_cert_name), 
             "pvt.%s.master.%d", network_name, node->node_id - 1);
    
    dap_cert_t *l_validator_cert = dap_cert_generate_mem(l_validator_cert_name, DAP_ENC_KEY_TYPE_SIG_DILITHIUM);
    if (!l_validator_cert) {
        log_it(L_ERROR, "Failed to generate validator certificate");
        return DAP_CERT_GEN_RET_ERROR;
    }
    
    log_it(L_INFO, "Validator certificate created with unique name: %s", l_validator_cert_name);
    
    /* Validator address = node address (they must be the same!) */
    /* Validator cert is ONLY for signing blocks/events, NOT for address generation */
    if (s_safe_strncpy(node->validator_addr, sizeof(node->validator_addr), 
                      node_addr_str) != DAP_CERT_GEN_RET_SUCCESS) {
        log_it(L_ERROR, "Failed to copy node address to validator address");
        dap_cert_delete(l_validator_cert);
        return DAP_CERT_GEN_RET_ERROR;
    }
    
    debug_if(s_debug_more, L_DEBUG, "Validator address = node address: %s", node->validator_addr);
    
    /* Save VALIDATOR address (same as node address) */
    if (s_safe_snprintf(addr_file, sizeof(addr_file), 
                      "%s/validator_addr.txt", node_dir) == DAP_CERT_GEN_RET_SUCCESS) {
        s_save_to_file(addr_file, node->validator_addr);
        log_it(L_INFO, "Validator address (= node address) saved: %s", node->validator_addr);
    }
    
    log_it(L_INFO, "About to save l_validator_cert to: %s (cert pointer=%p)", cert_file_esbocs, (void*)l_validator_cert);
    /* Save private validator certificate with pvt. prefix */
    if (s_safe_snprintf(cert_file_esbocs, sizeof(cert_file_esbocs), 
                      "%s/pvt.%s.master.%d.dcert", node_dir, network_name, node->node_id - 1) == DAP_CERT_GEN_RET_SUCCESS) {
        if (dap_cert_file_save(l_validator_cert, cert_file_esbocs) == 0) {
            log_it(L_INFO, "ESBocs private validator certificate saved: pvt.%s.master.%d", network_name, node->node_id - 1);
        }
    }
    
    /* Create public-only certificate using DAP SDK functions */
    /* Extract public key from the VALIDATOR certificate */
    dap_pkey_t *l_pkey = dap_cert_to_pkey(l_validator_cert);
    if (!l_pkey) {
        log_it(L_ERROR, "Failed to extract public key from validator certificate");
        dap_cert_delete(l_validator_cert);
    } else {
        /* Create new certificate with only public key */
        char l_pub_cert_name[DAP_CERT_GEN_MAX_CERT_NAME_LEN];
        snprintf(l_pub_cert_name, sizeof(l_pub_cert_name), "%s.master.%d", network_name, node->node_id - 1);
        
        /* Create encryption key from public key only */
        dap_enc_key_t *l_pub_key = dap_enc_key_new(l_validator_cert->enc_key->type);
        if (l_pub_key) {
            /* Serialize public key */
            size_t l_pub_key_size = 0;
            uint8_t *l_pub_key_data = dap_enc_key_serialize_pub_key(l_validator_cert->enc_key, &l_pub_key_size);
            
            if (l_pub_key_data && l_pub_key_size > 0) {
                /* Deserialize into new key (without private part) */
                if (dap_enc_key_deserialize_pub_key(l_pub_key, l_pub_key_data, l_pub_key_size) == 0) {
                    /* Create certificate with public key only */
                    dap_cert_t *l_pub_cert = DAP_NEW_Z(dap_cert_t);
                    if (l_pub_cert) {
                        snprintf(l_pub_cert->name, sizeof(l_pub_cert->name), "%s", l_pub_cert_name);
                        l_pub_cert->enc_key = l_pub_key;
                        
                        /* Save public certificate */
                        if (s_safe_snprintf(cert_file_esbocs, sizeof(cert_file_esbocs), 
                                          "%s/%s.dcert", node_dir, l_pub_cert_name) == DAP_CERT_GEN_RET_SUCCESS) {
                            if (dap_cert_file_save(l_pub_cert, cert_file_esbocs) == 0) {
                                log_it(L_INFO, "ESBocs public validator certificate: %s", l_pub_cert_name);
                            } else {
                                log_it(L_ERROR, "Failed to save public certificate");
                            }
                        }
                        
                        /* Cleanup: set enc_key to NULL before delete to avoid double-free */
                        l_pub_cert->enc_key = NULL;
                        dap_cert_delete(l_pub_cert);
                    }
                    dap_enc_key_delete(l_pub_key);
                } else {
                    log_it(L_ERROR, "Failed to deserialize public key");
                    dap_enc_key_delete(l_pub_key);
                }
                DAP_DELETE(l_pub_key_data);
            } else {
                log_it(L_ERROR, "Failed to serialize public key");
                dap_enc_key_delete(l_pub_key);
            }
        }
        DAP_DELETE(l_pkey);
        dap_cert_delete(l_validator_cert);
    }
    
    log_it(L_INFO, "Certificates generated for %s", node->node_name);
    log_it(L_INFO, "  Node address (from node-addr.dcert): %s", node_addr_str);
    log_it(L_INFO, "  Validator address (from pvt.stagenet.master.N.dcert): %s", node->validator_addr);
    
    return DAP_CERT_GEN_RET_SUCCESS;
}

/**
 * @brief Generate PKI configuration JSON
 */
static int s_pki_config_generate(const dap_cert_generator_node_t *nodes, int node_count, const char *output_dir) {
    if (!nodes || !output_dir || node_count <= 0) {
        log_it(L_ERROR, "Invalid parameters for PKI config generation");
        return DAP_CERT_GEN_RET_ERROR;
    }
    
    char config_path[DAP_CERT_GEN_MAX_PATH_LEN];
    char timestamp[DAP_CERT_GEN_MAX_TIMESTAMP_LEN];
    time_t now;
    struct tm *tm_info;
    
    now = time(NULL);
    dap_return_val_if_pass(now == (time_t)-1, DAP_CERT_GEN_RET_ERROR);
    
    tm_info = gmtime(&now);
    dap_return_val_if_pass(!tm_info, DAP_CERT_GEN_RET_ERROR);
    
    dap_return_val_if_pass(strftime(timestamp, sizeof(timestamp), 
                                     "%Y-%m-%dT%H:%M:%SZ", tm_info) == 0, 
                          DAP_CERT_GEN_RET_ERROR);
    
    dap_return_val_if_pass(s_safe_snprintf(config_path, sizeof(config_path), 
                                          "%s/pki-config.json", output_dir) != DAP_CERT_GEN_RET_SUCCESS, 
                          DAP_CERT_GEN_RET_ERROR);
    
    FILE *fp = fopen(config_path, "w");
    dap_return_val_if_pass(!fp, DAP_CERT_GEN_RET_ERROR);
    
    /* Write JSON configuration */
    fprintf(fp, "{\n");
    fprintf(fp, "    \"network\": {\n");
    fprintf(fp, "        \"name\": \"stagenet\",\n");
    fprintf(fp, "        \"chain_id\": \"%s\",\n", DAP_CERT_GEN_CHAIN_ID_HEX);
    fprintf(fp, "        \"consensus\": \"esbocs\"\n");
    fprintf(fp, "    },\n");
    fprintf(fp, "    \"nodes\": {\n");
    
    for (int i = 0; i < node_count; i++) {
        int cert_id = nodes[i].node_id - 1;
        int ip_last_octet = DAP_CERT_GEN_BASE_IP_OFFSET + nodes[i].node_id;
        
        fprintf(fp, "        \"%s\": {\n", nodes[i].node_name);
        fprintf(fp, "            \"id\": %d,\n", nodes[i].node_id);
        fprintf(fp, "            \"cert_id\": %d,\n", cert_id);
        fprintf(fp, "            \"dap_cert\": \"/certs/%s/stagenet-node%d.dcert\",\n",
                nodes[i].node_name, nodes[i].node_id);
        fprintf(fp, "            \"esbocs_cert\": \"/certs/%s/stagenet.master.pvt.%d.dcert\",\n",
                nodes[i].node_name, cert_id);
        fprintf(fp, "            \"validator_addr\": \"%s\",\n", nodes[i].validator_addr);
        fprintf(fp, "            \"ip\": \"172.20.0.%d\"\n", ip_last_octet);
        fprintf(fp, "        }%s\n", (i < node_count - 1) ? "," : "");
    }
    
    fprintf(fp, "    },\n");
    fprintf(fp, "    \"validators_addrs\": [");
    
    for (int i = 0; i < node_count; i++) {
        fprintf(fp, "\"%s\"%s", nodes[i].validator_addr, 
                (i < node_count - 1) ? ", " : "");
    }
    
    fprintf(fp, "],\n");
    fprintf(fp, "    \"generated\": \"%s\"\n", timestamp);
    fprintf(fp, "}\n");
    
    fclose(fp);
    
    if (chmod(config_path, DAP_CERT_GEN_FILE_PERMISSIONS) != 0) {
        log_it(L_WARNING, "Failed to set permissions on %s", config_path);
    }
    
    log_it(L_INFO, "PKI configuration generated: %s", config_path);
    
    return DAP_CERT_GEN_RET_SUCCESS;
}

/**
 * @brief Main entry point
 */
int main(int argc, char *argv[]) {
    const char *output_dir = "/certs";
    const char *network_name = "stagenet";  /* Default network name */
    dap_cert_generator_node_t *nodes = NULL;
    int ret = DAP_CERT_GEN_RET_SUCCESS;
    uint64_t network_id = 0x1234;  /* Default stagenet network ID */
    int node_count = 0;
    
    /* Initialize DAP SDK FIRST - before ANY other DAP calls */
    dap_log_level_set(L_DEBUG);
    dap_enc_key_init();
    
    debug_if(s_debug_more, L_NOTICE, "=== Initializing DAP Certificate Generator ===");
    
    /* Parse command line arguments */
    if (argc < 4) {
        log_it(L_ERROR, "Usage: %s <output_directory> <node_count> <network_name> [network_id_hex]", argv[0]);
        log_it(L_ERROR, "Example: %s /certs 6 stagenet 0x1234  # 6 nodes for stagenet", argv[0]);
        log_it(L_ERROR, "Example: %s /certs 3 testnet 0x5678  # 3 nodes for testnet", argv[0]);
        dap_enc_key_deinit();
        return DAP_CERT_GEN_RET_ERROR;
    }
    
    output_dir = argv[1];
    
    /* Parse node count */
    node_count = atoi(argv[2]);
    if (node_count <= 0 || node_count > DAP_CERT_GEN_MAX_NODE_COUNT) {
        log_it(L_ERROR, "Invalid node count: %d (must be 1-%d)", node_count, DAP_CERT_GEN_MAX_NODE_COUNT);
        dap_enc_key_deinit();
        return DAP_CERT_GEN_RET_ERROR;
    }
    
    /* Parse network name */
    network_name = argv[3];
    if (strlen(network_name) == 0 || strlen(network_name) >= DAP_CERT_GEN_MAX_NODE_NAME_LEN) {
        log_it(L_ERROR, "Invalid network name length");
        dap_enc_key_deinit();
        return DAP_CERT_GEN_RET_ERROR;
    }
    
    /* Parse optional network ID argument */
    if (argc >= 5) {
        char *endptr;
        network_id = strtoull(argv[4], &endptr, 0);  /* 0 base allows 0x prefix */
        if (*endptr != '\0' || network_id == 0) {
            log_it(L_ERROR, "Invalid network ID format. Use hex format like 0x1234");
            dap_enc_key_deinit();
            return DAP_CERT_GEN_RET_ERROR;
        }
    }
    
    /* Allocate nodes array dynamically */
    nodes = DAP_NEW_Z_COUNT(dap_cert_generator_node_t, node_count);
    if (!nodes) {
        log_it(L_CRITICAL, "%s", c_error_memory_alloc);
        dap_enc_key_deinit();
        return DAP_CERT_GEN_RET_ERROR;
    }
    
    /* Validate output directory path */
    size_t path_len = strlen(output_dir);
    if (path_len == 0 || path_len >= DAP_CERT_GEN_MAX_PATH_LEN) {
        log_it(L_ERROR, "Invalid output directory path length");
        dap_enc_key_deinit();
        return DAP_CERT_GEN_RET_ERROR;
    }
    
    log_it(L_NOTICE, "=== DAP Certificate Generator for Cellframe Node E2E Testing ===");
    log_it(L_INFO, "Output directory: %s", output_dir);
    log_it(L_INFO, "Network ID: 0x%llX", (unsigned long long)network_id);
    log_it(L_INFO, "Node count: %d", node_count);
    log_it(L_INFO, "Signature type: Dilithium (post-quantum)");
    
    /* Create main output directory */
    if (s_create_directory(output_dir) != DAP_CERT_GEN_RET_SUCCESS) {
        DAP_DELETE(nodes);
        dap_enc_key_deinit();
        return DAP_CERT_GEN_RET_ERROR;
    }
    
    /* Initialize and generate certificates for each node */
    for (int i = 0; i < node_count; i++) {
        char node_name[DAP_CERT_GEN_MAX_NODE_NAME_LEN];
        snprintf(node_name, sizeof(node_name), "node%d", i + 1);
        
        log_it(L_INFO, "Processing node %d/%d: %s", i+1, node_count, node_name);
        
        if (s_safe_strncpy(nodes[i].node_name, sizeof(nodes[i].node_name), 
                        node_name) != DAP_CERT_GEN_RET_SUCCESS) {
            log_it(L_ERROR, "Failed to copy node name");
            ret = DAP_CERT_GEN_RET_ERROR;
            goto cleanup;
        }
        
        nodes[i].node_id = i + 1;
        
        log_it(L_INFO, "Generating certificate for %s...", nodes[i].node_name);
        if (s_node_certificate_generate(&nodes[i], output_dir, network_name, network_id) != DAP_CERT_GEN_RET_SUCCESS) {
            log_it(L_ERROR, "Failed to generate certificate for %s", nodes[i].node_name);
            ret = DAP_CERT_GEN_RET_ERROR;
            goto cleanup;
        }
        
        log_it(L_NOTICE, "Certificate generated successfully for %s", nodes[i].node_name);
    }
    
    /* Generate PKI configuration */
    if (s_pki_config_generate(nodes, node_count, output_dir) != DAP_CERT_GEN_RET_SUCCESS) {
        ret = DAP_CERT_GEN_RET_ERROR;
        goto cleanup;
    }
    
    if (ret == DAP_CERT_GEN_RET_SUCCESS) {
        log_it(L_NOTICE, "=== Certificate generation completed successfully ===");
        log_it(L_INFO, "Total certificates: %d", node_count);
    }
    
cleanup:
    /* Cleanup certificates */
    for (int i = 0; i < node_count; i++) {
        if (nodes[i].cert) {
            dap_cert_delete(nodes[i].cert);
            nodes[i].cert = NULL;
        }
    }
    
    /* Free nodes array */
    DAP_DELETE(nodes);
    
    /* Deinitialize DAP SDK encryption key subsystem */
    dap_enc_key_deinit();
    
    if (ret != DAP_CERT_GEN_RET_SUCCESS) {
        log_it(L_ERROR, "=== Certificate generation failed ===");
    }
    
    return ret;
}