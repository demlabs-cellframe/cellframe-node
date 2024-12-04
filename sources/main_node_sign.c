/*
 * Authors:
 * Dmitriy A. Gearasimov <kahovski@gmail.com>
 * DeM Labs Inc.   https://demlabs.net
 * DeM Labs Open source community https://github.com/demlabsinc
 * Copyright  (c) 2017-2019
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
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/types.h>
#include <getopt.h>
#include <string.h>
#include <getopt.h>

#include "dap_common.h"
#include "dap_config.h"
#include "dap_cert.h"
#include "dap_cert_file.h"
#include "dap_chain_wallet.h"
#include "dap_file_utils.h"
#include "json.h"
#include "dap_chain_datum.h"
#include "dap_chain_datum_tx.h"
#include "dap_chain_datum_token.h"
#include "dap_chain_datum_tx_items.h"
#include "dap_chain_datum_decree.h"
#include "dap_chain_datum_anchor.h"
#include "dap_chain_datum_tx_voting.h"
#include "dap_enc_base64.h"
#include "dap_chain_net_srv.h"


#define LOG_TAG "sign_tool"

static struct option const options[] =
{
  {"wallet", required_argument, 0, 'w'},
  {"passwd", required_argument, 0, 'p'},
  {"filename", required_argument, 0, 'f'},
  {"out", required_argument, 0, 'o'},
  {"create", no_argument, 0, 'c'},
  {"sign-type", required_argument, 0, 's'},
  {"path", required_argument, 0, 'd'},
  {"help", no_argument, 0, 'h'},
  {"seed", required_argument, 0, 'z'},
  {"beauty", required_argument, 0, 'b'},
  {"get-addr", required_argument, 0, 'a'},
  {"net-id", required_argument, 0, 'i'},
};

static dap_chain_datum_tx_t* json_parse_input_tx (json_object* a_in);
static char* convert_tx_to_json_string(dap_chain_datum_tx_t *a_tx, bool a_beauty);
static int s_wallet_create(const char *a_wallet_path, const char *a_wallet_name, const char *a_pass, const char *a_sig_type, const char *a_seed);

void bad_option(){
    printf("Usage: %s {{-w, --wallet <path_to_wallet_file> | -z, --seed <seed_phrase> -s <sign_type>} [OPTIONS] | {-c -w <wallet_name> -d <path_to_save_wallet_file> -s <sign_type> -z <seed_phrase>} | {-a {-w <path_to_wallet_file> | -z, --seed <seed_phrase> -s <sign_type>} -i 0x<net_id>}} \n\r"
            "Signs the datum passed to the input by specified wallet and send its items in json-format.\n\r"
            "Datum sign options:\n\r"
            "\t-w, --wallet     specifies path to wallet for datum sign or wallet name\n\r"
            "\t-p, --passwd     specifies walled password if needed\n\r"
            "\t-f, --filename   specifies input json-file wits datum items. If not specified, it will be received from stdin\n\r"
            "\t-o, --out        specifies output json-file. If not specified, it will be send into stdout\n\r"
            "\t-b, --beauty     enables output JSON beautification\n\r"
            "\n\r"
            "\t-c, --create     create wallet -w with password -p\n\r"
            "Wallet create options:\n\r"
            "\t-w, --wallet     specifies wallet name\n\r"
            "\t-d, --path       specifies path to save wallet file\n\r"
            "\t-s, --sign-type  specifies wallet sign type. Available options: sig_dil, sig_falcon\n\r"
            "\t-z, --seed       specifies seed phrase\n\r"
            "Wallet get address:\n\r"
            "\t-a, --get-addr   print wallet address in specified net\n\r"
            "\t-w, --wallet     specifies path to wallet file\n\r"
            "\t-z, --seed       specifies seed phrase\n\r"
            "\t-i, --net-id     hex id of net\n\r"
            "Exapmple of usage for datum sign:\n\r\n\r"
            "\tUsing .dwallet file: cellframe-sign-tool --wallet /home/user1/wallets/mywal.dwallet -f ~/in.json -o ~/out.json\n\r\n\r"
            "\tUsing seed phrase: cellframe-sign-tool -seed \"my seed phrase\" -s sig_dil -f ~/in.json -o ~/out.json\n\r\n\r"
            "Exapmple of usage for wallet creating:\n\r\n\r"
            "\tcellframe-sign-tool --create -d /home/user1/wallets -w mywal -s sig_dil -z \"word1 word2 word3\"\n\r\n\r"
            "Exapmple of usage for printing wallet address:\n\r\n\r"
            "\tBackbone net:\n\r"
            "\tUsing .dwallet file: cellframe-sign-tool --get-addr -w /home/user1/wallets/mywal.dcert -i 0x0404202200000000\n\r\n\r"
            "\tUsing seed phrase: cellframe-sign-tool --get-addr -seed \"my seed phrase\" -s sig_dil -i 0x0404202200000000\n\r\n\r"
            "\tKelVPN net:\n\r"
            "\tUsing .dwallet file: cellframe-sign-tool --get-addr -w /home/user1/wallets/mywal.dcert -i 0x1807202300000000\n\r\n\r"
            "\tUsing seed phrase: cellframe-sign-tool --get-addr -seed \"my seed phrase\" -s sig_dil -i 0x1807202300000000\n\r\n\r",

            dap_get_appname());

    exit(EXIT_FAILURE);
}

int main(int argc, char **argv)
{
    dap_set_appname("cellframe-sign-tool");
   
    if (argc == 1){
        bad_option();
    }

    char *l_input_data = NULL;

    // get relative path to config
    const char *l_wallet_str = NULL;
    const char *l_wallet_path = NULL;
    const char *l_wallet_name = NULL;
    const char *l_in_file_path = NULL;
    const char *l_out_file_path = NULL;
    const char *l_pwd = NULL;
    const char *l_seed_str = NULL;
    const char *l_sign_type = NULL;
    const char *l_net_id_str = NULL;
    bool l_beautification = false;
    bool l_create_wallet = false;
    bool l_get_wallet_addr = false;

    int optc = 0;
    int option_index = 0;
    while ((optc = getopt_long(argc, argv, "w:p:f:o:bcs:d:hz:ai:", options, &option_index)) != -1){
        switch(optc){
        case 'w':{
            l_wallet_str = dap_strdup(optarg);
        }break;
        case 'p':{
            l_pwd = dap_strdup(optarg);       
        }break;
        case 'f':{
            l_in_file_path = dap_strdup(optarg);
        }break;
        case 'o':{
            l_out_file_path = dap_strdup(optarg);
        }break;
        case 'b':{
            l_beautification = true;
        }break;
        case 'c':{
            l_create_wallet = true;
        }break;
        case 'd':{
            l_wallet_path = dap_strdup(optarg);
        }break;
        case 's':{
            l_sign_type = dap_strdup(optarg);
        }break;
        case 'z':{
            l_seed_str = dap_strdup(optarg);
        }break;
        case 'a':{
            l_get_wallet_addr = true;
        }break;
        case 'i':{
            l_net_id_str = dap_strdup(optarg);
        }break;
        default:
            bad_option();
        }
    }

    if (l_create_wallet){
        l_wallet_name = l_wallet_str;
    } else {
        l_wallet_path = l_wallet_str;
    }
    
    if (!l_wallet_path && !l_seed_str){
        printf("Path to wallet or seed phrase must be specified!\n\r");
        return -1;
    }

    if (l_get_wallet_addr && !l_net_id_str){
        printf("Net id must be specified for getting wallet addr!\n\r");
        return -1;
    }

    if (l_create_wallet){
        int l_res = s_wallet_create(l_wallet_path, l_wallet_name, l_pwd, l_sign_type, l_seed_str);
        if (l_res)
            printf("Error %d (%s)\n\r", errno, strerror(errno));
        return l_res;
    } else {
        l_wallet_path = l_wallet_str;
    }

    if (l_get_wallet_addr){
        if (l_wallet_path){
            dap_chain_wallet_t *l_wallet = dap_chain_wallet_open_file(l_wallet_path, l_pwd, NULL);
            if(!l_wallet) {
                printf("Can't open wallet %s. Error %d (%s)\n\r", l_wallet_path, errno, strerror(errno));
                return errno;
            }
            uint64_t l_net_id_ui64 = strtoull(l_net_id_str, NULL, 16);
            dap_chain_net_id_t l_net_id = {.uint64 = l_net_id_ui64};
            dap_chain_addr_t *l_addr = dap_chain_wallet_get_addr(l_wallet, l_net_id);
            const char*l_addr_str = dap_chain_addr_to_str_static(l_addr);
            printf("Wallet addr for net with id %"DAP_UINT64_FORMAT_X":\n\r%s\n\r", l_net_id_ui64, l_addr_str);
            return 0;
        } else if (l_seed_str && l_sign_type) {
            const char* l_seed_hash_str = dap_get_data_hash_str(l_seed_str, strlen(l_seed_str)).s;
            size_t l_restore_str_size = dap_strlen(l_seed_hash_str);
            uint8_t *l_seed = NULL;
            size_t l_seed_size = 0;
            if (l_restore_str_size > 3 && !dap_strncmp(l_seed_hash_str, "0x", 2) && (!dap_is_hex_string(l_seed_hash_str + 2, l_restore_str_size - 2))) {
                l_seed_size = (l_restore_str_size - 2) / 2;
                l_seed = DAP_NEW_Z_SIZE(uint8_t, l_seed_size + 1);
                if(!l_seed) {
                    printf("Memory allocation error.\n\r");
                    exit(-100);
                }
                dap_hex2bin(l_seed, l_seed_hash_str + 2, l_restore_str_size - 2);
            } else {
                printf("Restored hash is invalid or too short, wallet is not created. Please use -seed 0x<hex_value>\n\r");
                exit(-1);
            }

            uint64_t l_net_id_ui64 = strtoull(l_net_id_str, NULL, 16);
            dap_chain_net_id_t l_net_id = {.uint64 = l_net_id_ui64};
            dap_enc_key_t *l_enc_key = dap_enc_key_new_generate(dap_sign_type_to_key_type(dap_sign_type_from_str(l_sign_type)), NULL, 0, l_seed, l_seed_size, 0);
            dap_chain_addr_t l_addr = {};
            dap_chain_addr_fill_from_key(&l_addr, l_enc_key, l_net_id);
            const char* l_addr_str = dap_chain_addr_to_str_static(&l_addr);
            printf("Wallet addr for net with id %"DAP_UINT64_FORMAT_X":\n\r%s\n\r", l_net_id_ui64, l_addr_str);
            dap_enc_key_delete(l_enc_key);
            return 0;
        } else {
            printf("-get-addr command requires --wallet or -seed, -sign_type parameters.\n\r");
            return -2;
        }       
    }

    FILE *l_input_file = NULL;
    if (!l_in_file_path){
        l_input_file = stdin;
    } else {
        l_input_file = fopen(l_in_file_path, "r");
        if (!l_input_file){
            printf("Can't open %s\n\r", l_in_file_path);
            return -1;
        }
    }

    char buffer[BUFSIZ] = {0};
    size_t l_bytes_read = 0;
    size_t l_total_bytes = 0;
    while((l_bytes_read = fread(buffer, sizeof(char), BUFSIZ, l_input_file)) > 0){
        l_input_data = DAP_REALLOC_COUNT(l_input_data, l_total_bytes + l_bytes_read);
        memcpy(l_input_data + l_total_bytes, buffer, l_bytes_read);
        l_total_bytes += l_bytes_read;
    }

    if (!l_input_data && !l_total_bytes){
        printf("Can't read input data. Error: ");
        perror(l_in_file_path);
        printf("\n\r");
        if (l_in_file_path)
            fclose(l_input_file);
        return -1;
    }

    if (l_in_file_path){
        fclose(l_input_file);
    }

    // Parse json
    struct json_object *l_json = json_tokener_parse(l_input_data);
    if (!l_json){
        printf("Can't parse json\n\r");
        DAP_DELETE(l_input_data);
        return -1;
    }

    // Make binary transaction
    dap_chain_datum_tx_t *l_tx = json_parse_input_tx (l_json);
    if (!l_tx){
        printf("Can't create tx\n\r");
        DAP_DELETE(l_input_data);
        return -1;
    }

    // Sign it
    // add 'sign' items
    dap_enc_key_t *l_owner_key = NULL;
    if (l_seed_str && l_sign_type) {
            const char* l_seed_hash_str = dap_get_data_hash_str(l_seed_str, strlen(l_seed_str)).s;
            size_t l_restore_str_size = dap_strlen(l_seed_hash_str);
            uint8_t *l_seed = NULL;
            size_t l_seed_size = 0;
            if (l_restore_str_size > 3 && !dap_strncmp(l_seed_hash_str, "0x", 2) && (!dap_is_hex_string(l_seed_hash_str + 2, l_restore_str_size - 2))) {
                l_seed_size = (l_restore_str_size - 2) / 2;
                l_seed = DAP_NEW_Z_SIZE(uint8_t, l_seed_size + 1);
                if(!l_seed) {
                    printf("Memory allocation error.\n\r");
                    dap_chain_datum_tx_delete(l_tx);
                    DAP_DELETE(l_input_data);
                    exit(-100);
                }
                dap_hex2bin(l_seed, l_seed_hash_str + 2, l_restore_str_size - 2);
            } else {
                printf("Restored hash is invalid or too short, wallet is not created. Please use -seed 0x<hex_value>\n\r");
                dap_chain_datum_tx_delete(l_tx);
                DAP_DELETE(l_input_data);
                exit(-1);
            }
            l_owner_key = dap_enc_key_new_generate(dap_sign_type_to_key_type(dap_sign_type_from_str(l_sign_type)), NULL, 0, l_seed, l_seed_size, 0);
    } else if (l_wallet_path){
        dap_chain_wallet_t *l_wallet = dap_chain_wallet_open_file(l_wallet_path, l_pwd, NULL);
        if(!l_wallet) {
            dap_chain_datum_tx_delete(l_tx);
            printf("Can't open wallet\n\r");
            DAP_DELETE(l_input_data);
            return -1;
        }
        l_owner_key = dap_chain_wallet_get_key(l_wallet, 0);
    } else {
        dap_chain_datum_tx_delete(l_tx);
        printf("Wallet or seed_phrase+sig_type+net_id required for tx signing\n\r");
        DAP_DELETE(l_input_data);
        return -1;
    }

    if(!l_owner_key || dap_chain_datum_tx_add_sign_item(&l_tx, l_owner_key) != 1) {
        dap_chain_datum_tx_delete(l_tx);
        dap_enc_key_delete(l_owner_key);
        printf("Can't add sign output\n\r");
        DAP_DELETE(l_input_data);
        return -1;
    }
    dap_enc_key_delete(l_owner_key);

    // Convert to JSON transaction
    char *l_out = convert_tx_to_json_string(l_tx, l_beautification);
    if (!l_out){
        dap_chain_datum_tx_delete(l_tx);
        printf("error\n\r");
        DAP_DELETE(l_input_data);
        return -1;
    }
    dap_chain_datum_tx_delete(l_tx);

    FILE *l_output_file = NULL;
    if (!l_out_file_path){
        l_output_file = stdout;
    } else {
        l_output_file = fopen(l_out_file_path, "w");
        if (!l_output_file){
            printf("Can't open %s\n\r", l_out_file_path);
            DAP_DELETE(l_out);
            DAP_DELETE(l_input_data);
            return -1;
        }
    }

    size_t out_bytes = fwrite(l_out, 1, strlen(l_out), l_output_file);
    if (l_out_file_path){
        fclose(l_output_file);
    }
    if (out_bytes <= 0){
        printf("Can't write result\n\r");
        DAP_DELETE(l_out);
        DAP_DELETE(l_input_data);
        return -1;
    }

    DAP_DELETE(l_out);
    DAP_DELETE(l_input_data);
    return 0;
}

static const char* s_json_get_text(struct json_object *a_json, const char *a_key)
{
    if(!a_json || !a_key)
        return NULL;
    struct json_object *l_json = json_object_object_get(a_json, a_key);
    if(l_json && json_object_is_type(l_json, json_type_string)) {
        // Read text
        return json_object_get_string(l_json);
    }
    return NULL;
}

static bool s_json_get_int64(struct json_object *a_json, const char *a_key, int64_t *a_out)
{
    if(!a_json || !a_key || !a_out)
        return false;
    struct json_object *l_json = json_object_object_get(a_json, a_key);
    if(l_json) {
        if(json_object_is_type(l_json, json_type_int)) {
            // Read number
            *a_out = json_object_get_int64(l_json);
            return true;
        }
    }
    return false;
}

static bool s_json_get_unit(struct json_object *a_json, const char *a_key, dap_chain_net_srv_price_unit_uid_t *a_out)
{
    const char *l_unit_str = s_json_get_text(a_json, a_key);
    if(!l_unit_str || !a_out)
        return false;
    dap_chain_net_srv_price_unit_uid_t l_unit = dap_chain_net_srv_price_unit_uid_from_str(l_unit_str);
    if(l_unit.enm == SERV_UNIT_UNDEFINED)
        return false;
    a_out->enm = l_unit.enm;
    return true;
}

static bool s_json_get_uint256(struct json_object *a_json, const char *a_key, uint256_t *a_out)
{
    const char *l_uint256_str = s_json_get_text(a_json, a_key);
    if(!a_out || !l_uint256_str)
        return false;
    uint256_t l_value = dap_chain_balance_scan(l_uint256_str);
    if(!IS_ZERO_256(l_value)) {
        memcpy(a_out, &l_value, sizeof(uint256_t));
        return true;
    }
    return false;
}

// service names: srv_stake, srv_vpn, srv_xchange
static bool s_json_get_srv_uid(struct json_object *a_json, const char *a_key_service_id, const char *a_key_service, uint64_t *a_out)
{
    uint64_t l_srv_id;
    if(!a_out)
        return false;
    // Read service id
    if(s_json_get_int64(a_json, a_key_service_id, (int64_t*) &l_srv_id)) {
        *a_out = l_srv_id;
        return true;
    }
    else {
        // Read service as name
        const char *l_service = s_json_get_text(a_json, a_key_service);
        if(l_service) {
            dap_chain_net_srv_t *l_srv = dap_chain_net_srv_get_by_name(l_service);
            if(!l_srv)
                return false;
            *a_out = l_srv->uid.uint64;
            return true;
        }
    }
    return false;
}

static dap_chain_wallet_t* s_json_get_wallet(struct json_object *a_json, const char *a_key)
{
    return dap_chain_wallet_open(s_json_get_text(a_json, a_key), dap_chain_wallet_get_path(g_config), NULL);
}

static const dap_cert_t* s_json_get_cert(struct json_object *a_json, const char *a_key)
{
    return dap_cert_find_by_name(s_json_get_text(a_json, a_key));
}

// Read pkey from wallet or cert
static dap_pkey_t* s_json_get_pkey(struct json_object *a_json)
{
    dap_pkey_t *l_pub_key = NULL;
    // From wallet
    dap_chain_wallet_t *l_wallet = s_json_get_wallet(a_json, "wallet");
    if(l_wallet) {
        l_pub_key = dap_chain_wallet_get_pkey(l_wallet, 0);
        dap_chain_wallet_close(l_wallet);
        if(l_pub_key) {
            return l_pub_key;
        }
    }
    // From cert
    const dap_cert_t *l_cert = s_json_get_cert(a_json, "cert");
    if(l_cert) {
        l_pub_key = dap_pkey_from_enc_key(l_cert->enc_key);
    }
    return l_pub_key;
}

static dap_chain_datum_tx_t* json_parse_input_tx (json_object* a_json_in)
{
    dap_list_t *l_sign_list = NULL;// list 'sing' items
    size_t l_items_ready = 0;

    // Read items from json file
    struct json_object *l_json_items = json_object_object_get(a_json_in, "items");
    size_t l_items_count = json_object_array_length(l_json_items);
    if(!l_json_items || !json_object_is_type(l_json_items, json_type_array) || !(l_items_count = json_object_array_length(l_json_items))) {
        printf("%s", "Wrong json format: not found array 'items' or array is empty\n\r");
        return NULL;
    }

    dap_chain_datum_tx_t *l_tx = DAP_NEW_Z_SIZE(dap_chain_datum_tx_t, sizeof(dap_chain_datum_tx_t));
    if(!l_tx) {
        printf("%s\n\r", c_error_memory_alloc);
        return NULL;
    }

    for(size_t i = 0; i < l_items_count; ++i) {
        struct json_object *l_json_item_obj = json_object_array_get_idx(l_json_items, i);
        if(!l_json_item_obj || !json_object_is_type(l_json_item_obj, json_type_object)) {
            continue;
        }
        struct json_object *l_json_item_type = json_object_object_get(l_json_item_obj, "type");
        if(!l_json_item_type && json_object_is_type(l_json_item_type, json_type_string)) {
            continue;
        }
        const char *l_item_type_str = json_object_get_string(l_json_item_type);
        dap_chain_tx_item_type_t l_item_type = dap_chain_datum_tx_item_str_to_type(l_item_type_str);
        if(l_item_type == TX_ITEM_TYPE_UNKNOWN) {
            continue;
        }
        // Create an item depending on its type
        const uint8_t *l_item = NULL;
        switch (l_item_type) {
        case TX_ITEM_TYPE_IN: {
            const char *l_prev_hash_str = s_json_get_text(l_json_item_obj, "prev_hash");
            int64_t l_out_prev_idx;
            bool l_is_out_prev_idx = s_json_get_int64(l_json_item_obj, "out_prev_idx", &l_out_prev_idx);
            // If prev_hash and out_prev_idx were read
            if(l_prev_hash_str && l_is_out_prev_idx) {
                dap_chain_hash_fast_t l_tx_prev_hash;
                if(!dap_chain_hash_fast_from_str(l_prev_hash_str, &l_tx_prev_hash)) {
                    // Create IN item
                    dap_chain_tx_in_t *l_in_item = dap_chain_datum_tx_item_in_create(&l_tx_prev_hash, (uint32_t) l_out_prev_idx);
                    if (!l_in_item) {
                        printf("Unable to create in for transaction.\n\r");
                        DAP_DEL_Z(l_tx);
                        dap_list_free_full(l_sign_list, NULL);
                        return NULL;
                    }
                    dap_chain_datum_tx_add_item(&l_tx, (const uint8_t*) l_in_item);
                } else {
                    printf("Invalid 'in' item, bad prev_hash %s\n\r", l_prev_hash_str);
                }
            } 
        }
            break;

        case TX_ITEM_TYPE_OUT:
        case TX_ITEM_TYPE_OUT_EXT: {
            // Read address and value
            uint256_t l_value = { };
            const char *l_json_item_addr_str = s_json_get_text(l_json_item_obj, "addr");
            bool l_is_value = s_json_get_uint256(l_json_item_obj, "value", &l_value);
            if(l_is_value && l_json_item_addr_str) {
                dap_chain_addr_t *l_addr = dap_chain_addr_from_str(l_json_item_addr_str);
                if(l_addr && !IS_ZERO_256(l_value)) {
                    if(l_item_type == TX_ITEM_TYPE_OUT) {
                        // Create OUT item
                        dap_chain_tx_out_t *l_out_item = dap_chain_datum_tx_item_out_create(l_addr, l_value);
                        if (!l_out_item) {
                            printf("Failed to create transaction out. There may not be enough funds in the wallet.\n\r");
                            DAP_DEL_Z(l_tx);
                            dap_list_free_full(l_sign_list, NULL);
                            return NULL;
                        }
                        l_item = (const uint8_t*) l_out_item;
                    }
                    else if(l_item_type == TX_ITEM_TYPE_OUT_EXT) {
                        // Read address and value
                        const char *l_token = s_json_get_text(l_json_item_obj, "token");
                        if(l_token) {
                            // Create OUT_EXT item
                            dap_chain_tx_out_ext_t *l_out_ext_item = dap_chain_datum_tx_item_out_ext_create(l_addr, l_value, l_token);
                            if (!l_out_ext_item) {
                                printf("Failed to create a out ext\n\r");
                                DAP_DEL_Z(l_tx);
                                return NULL;
                            }
                            l_item = (const uint8_t*) l_out_ext_item;
                        }
                    }
                }
            }
        }
            break;
        case TX_ITEM_TYPE_OUT_COND: {
            // Read subtype of item
            const char *l_subtype_str = s_json_get_text(l_json_item_obj, "subtype");
            dap_chain_tx_out_cond_subtype_t l_subtype = dap_chain_tx_out_cond_subtype_from_str(l_subtype_str);
            switch (l_subtype) {

            case DAP_CHAIN_TX_OUT_COND_SUBTYPE_SRV_PAY:{
                uint256_t l_value = { };
                bool l_is_value = s_json_get_uint256(l_json_item_obj, "value", &l_value);
                if(!l_is_value || IS_ZERO_256(l_value)) {
                    printf("Json TX: bad value in OUT_COND_SUBTYPE_SRV_PAY\n\r");
                    break;
                }
                uint256_t l_value_max_per_unit = { };
                l_is_value = s_json_get_uint256(l_json_item_obj, "value_max_per_unit", &l_value_max_per_unit);
                if(!l_is_value || IS_ZERO_256(l_value_max_per_unit)) {
                    printf("Json TX: bad value_max_per_unit in OUT_COND_SUBTYPE_SRV_PAY\n\r");
                    break;
                }
                dap_chain_net_srv_price_unit_uid_t l_price_unit;
                if(!s_json_get_unit(l_json_item_obj, "price_unit", &l_price_unit)) {
                    printf("Json TX: bad price_unit in OUT_COND_SUBTYPE_SRV_PAY\n\r");
                    break;
                }
                dap_chain_net_srv_uid_t l_srv_uid;
                if(!s_json_get_srv_uid(l_json_item_obj, "service_id", "service", &l_srv_uid.uint64)){
                    // Default service DAP_CHAIN_NET_SRV_VPN_ID
                    l_srv_uid.uint64 = 0x0000000000000001;
                }

                // From "wallet" or "cert"
                dap_pkey_t *l_pkey = s_json_get_pkey(l_json_item_obj);
                if(!l_pkey) {
                    printf("Json TX: bad pkey in OUT_COND_SUBTYPE_SRV_PAY\n\r");
                    break;
                }
                const char *l_params_str = s_json_get_text(l_json_item_obj, "params");
                size_t l_params_size = dap_strlen(l_params_str);
                dap_chain_tx_out_cond_t *l_out_cond_item = dap_chain_datum_tx_item_out_cond_create_srv_pay(l_pkey, l_srv_uid, l_value, l_value_max_per_unit,
                        l_price_unit, l_params_str, l_params_size);
                l_item = (const uint8_t*) l_out_cond_item;
                // Save value for using in In item
                if(!l_item) {
                    printf("Unable to create conditional out for transaction "
                                                        "can of type %s described in item %zu.\n", l_subtype_str, i);
                }
                DAP_DELETE(l_pkey);
            }
                break;
            case DAP_CHAIN_TX_OUT_COND_SUBTYPE_SRV_XCHANGE: {

                dap_chain_net_srv_uid_t l_srv_uid;
                if(!s_json_get_srv_uid(l_json_item_obj, "service_id", "service", &l_srv_uid.uint64)) {
                    // Default service DAP_CHAIN_NET_SRV_XCHANGE_ID
                    l_srv_uid.uint64 = 0x2;
                }
                dap_chain_net_t *l_net = dap_chain_net_by_name(s_json_get_text(l_json_item_obj, "net"));
                if(!l_net) {
                    printf("Json TX: bad net in OUT_COND_SUBTYPE_SRV_XCHANGE\n\r");
                    break;
                }
                const char *l_token = s_json_get_text(l_json_item_obj, "token");
                if(!l_token) {
                    printf("Json TX: bad token in OUT_COND_SUBTYPE_SRV_XCHANGE\n\r");
                    break;
                }
                uint256_t l_value = { };
                if(!s_json_get_uint256(l_json_item_obj, "value", &l_value) || IS_ZERO_256(l_value)) {
                    printf("Json TX: bad value in OUT_COND_SUBTYPE_SRV_XCHANGE\n\r");
                    break;
                }
                //const char *l_params_str = s_json_get_text(l_json_item_obj, "params");
                //size_t l_params_size = dap_strlen(l_params_str);
                dap_chain_tx_out_cond_t *l_out_cond_item = NULL; //dap_chain_datum_tx_item_out_cond_create_srv_xchange(l_srv_uid, l_net->pub.id, l_token, l_value, l_params_str, l_params_size);
                l_item = (const uint8_t*) l_out_cond_item;
                // Save value for using in In item
                if(l_item){
                    printf("Unable to create conditional out for transaction "
                                                         "can of type %s described in item %zu.\n\r", l_subtype_str, i);
                }
            }
                break;
            case DAP_CHAIN_TX_OUT_COND_SUBTYPE_SRV_STAKE_POS_DELEGATE:{
                dap_chain_net_srv_uid_t l_srv_uid;
                if(!s_json_get_srv_uid(l_json_item_obj, "service_id", "service", &l_srv_uid.uint64)) {
                    // Default service DAP_CHAIN_NET_SRV_STAKE_ID
                    l_srv_uid.uint64 = 0x13;
                }
                uint256_t l_value = { };
                if(!s_json_get_uint256(l_json_item_obj, "value", &l_value) || IS_ZERO_256(l_value)) {
                    printf("Json TX: bad value in OUT_COND_SUBTYPE_SRV_STAKE_POS_DELEGATE\n\r");
                    break;
                }
                uint256_t l_fee_value = { };
                if(!s_json_get_uint256(l_json_item_obj, "fee", &l_fee_value) || IS_ZERO_256(l_fee_value)) {
                    break;
                }
                
                const char *l_signing_addr_str = s_json_get_text(l_json_item_obj, "signing_addr");
                dap_chain_addr_t *l_signing_addr = dap_chain_addr_from_str(l_signing_addr_str);
                if(!l_signing_addr) {
                {
                    printf("Json TX: bad signing_addr in OUT_COND_SUBTYPE_SRV_STAKE_POS_DELEGATE\n\r");
                    break;
                }
                dap_chain_node_addr_t l_signer_node_addr;
                const char *l_node_addr_str = s_json_get_text(l_json_item_obj, "node_addr");
                if(!l_node_addr_str || dap_chain_node_addr_from_str(&l_signer_node_addr, l_node_addr_str)) {
                    printf("Json TX: bad node_addr in OUT_COND_SUBTYPE_SRV_STAKE_POS_DELEGATE\n\r");
                    break;
                }
                dap_chain_tx_out_cond_t *l_out_cond_item = dap_chain_datum_tx_item_out_cond_create_srv_stake(l_srv_uid, l_value, l_signing_addr,
                                                                                                             &l_signer_node_addr, NULL, uint256_0);
                l_item = (const uint8_t*) l_out_cond_item;
                // Save value for using in In item
                if(l_item) {
                    printf("Unable to create conditional out for transaction "
                                                        "can of type %s described in item %zu.\n\r", l_subtype_str, i);
                }
                }
            }
                break;
            case DAP_CHAIN_TX_OUT_COND_SUBTYPE_FEE: {
                uint256_t l_value = { };
                s_json_get_uint256(l_json_item_obj, "value", &l_value);
                if(!IS_ZERO_256(l_value)) {
                    dap_chain_tx_out_cond_t *l_out_cond_item = dap_chain_datum_tx_item_out_cond_create_fee(l_value);
                    l_item = (const uint8_t*) l_out_cond_item;
                    // Save value for using in In item
                    if(!l_item){
                        printf("Unable to create conditional out for transaction "
                                                            "can of type %s described in item %zu.\n\r", l_subtype_str, i);
                    }
                }
                else
                    printf("Json TX: zero value in OUT_COND_SUBTYPE_FEE");
            }
                break;
            case DAP_CHAIN_TX_OUT_COND_SUBTYPE_UNDEFINED:
                printf("Undefined subtype: '%s' of 'out_cond' item %zu \n\r", l_subtype_str, i);
                break;
            }
        }

            break;
        case TX_ITEM_TYPE_RECEIPT: {
            dap_chain_net_srv_uid_t l_srv_uid;
            if(!s_json_get_srv_uid(l_json_item_obj, "service_id", "service", &l_srv_uid.uint64)) {
                printf("Json TX: bad service_id in TYPE_RECEIPT\n\r");
                break;
            }
            dap_chain_net_srv_price_unit_uid_t l_price_unit;
            if(!s_json_get_unit(l_json_item_obj, "price_unit", &l_price_unit)) {
                printf("Json TX: bad price_unit in TYPE_RECEIPT\n\r");
                break;
            }
            int64_t l_units;
            if(!s_json_get_int64(l_json_item_obj, "units", &l_units)) {
                printf("Json TX: bad units in TYPE_RECEIPT\n\r");
                break;
            }
            uint256_t l_value = { };
            if(!s_json_get_uint256(l_json_item_obj, "value", &l_value) || IS_ZERO_256(l_value)) {
                printf("Json TX: bad value in TYPE_RECEIPT\n\r");
                break;
            }
            const char *l_params_str = s_json_get_text(l_json_item_obj, "params");
            size_t l_params_size = dap_strlen(l_params_str);
            dap_chain_datum_tx_receipt_t *l_receipt = dap_chain_datum_tx_receipt_create(l_srv_uid, l_price_unit, l_units, l_value, l_params_str, l_params_size);
            l_item = (const uint8_t*) l_receipt;
            if (!l_item) {
                printf("Unable to create receipt out for transaction "
                                                    "described by item %zu.\n\r", i);
            }
        }
            break;
        case TX_ITEM_TYPE_TSD: {
            int64_t l_tsd_type;
            if(!s_json_get_int64(l_json_item_obj, "type_tsd", &l_tsd_type)) {
                printf("Json TX: bad type_tsd in TYPE_TSD\n\r");
                break;
            }
            const char *l_tsd_data = s_json_get_text(l_json_item_obj, "data");
            if (!l_tsd_data) {
                printf("Json TX: bad data in TYPE_TSD\n\r");
                break;
            }
            size_t l_data_size = dap_strlen(l_tsd_data);
            dap_chain_tx_tsd_t *l_tsd = dap_chain_datum_tx_item_tsd_create((void*)l_tsd_data, (int)l_tsd_type, l_data_size);
            dap_chain_datum_tx_add_item(&l_tx, l_tsd);
        }
            break;
        }
        // Add item to transaction
        if(l_item) {
            dap_chain_datum_tx_add_item(&l_tx, (const uint8_t*) l_item);
            DAP_DELETE(l_item);
        }
    }     

    return l_tx;
}


static char* convert_tx_to_json_string(dap_chain_datum_tx_t *a_tx, bool a_beauty)
{
    json_object* json_obj_out = json_object_new_object();
    json_object* l_json_arr_reply = NULL;
    dap_hash_fast_t l_hash_tmp = { };
    byte_t *item; size_t l_size;
    char *l_hash_str = NULL;
    char l_tmp_buf[DAP_TIME_STR_SIZE];
    json_object* json_arr_items = json_object_new_array();
    //   const char *
    TX_ITEM_ITER_TX(item, l_size, a_tx) {
        json_object* json_obj_item = json_object_new_object();
        switch (*item) {
        case TX_ITEM_TYPE_IN:
            l_hash_tmp = ((dap_chain_tx_in_t*)item)->header.tx_prev_hash;
            l_hash_str = dap_hash_fast_to_str_static(&l_hash_tmp);
            json_object_object_add(json_obj_item,"type", json_object_new_string("in"));
            json_object_object_add(json_obj_item,"prev_hash", json_object_new_string(l_hash_str));
            json_object_object_add(json_obj_item,"out_prev_idx", json_object_new_uint64(((dap_chain_tx_in_t*)item)->header.tx_out_prev_idx));
            break;
        case TX_ITEM_TYPE_OUT: { // 256
            const char *l_coins_str,
                    *l_value_str = dap_uint256_to_char(((dap_chain_tx_out_t*)item)->header.value, &l_coins_str),
                    *l_addr_str = dap_chain_addr_to_str_static(&((dap_chain_tx_out_t*)item)->addr);
            json_object_object_add(json_obj_item,"type", json_object_new_string("out"));
            json_object_object_add(json_obj_item,"value", json_object_new_string(l_value_str));
            json_object_object_add(json_obj_item,"addr", json_object_new_string(l_addr_str));            
        } break;
        case TX_ITEM_TYPE_SIG: {
            dap_sign_t *l_sign = dap_chain_datum_tx_item_sign_get_sig((dap_chain_tx_sig_t*)item);
            json_object_object_add(json_obj_item,"type", json_object_new_string("sign"));
            dap_chain_hash_fast_t l_hash_pkey;
            json_object_object_add(json_obj_item,"sig_type",json_object_new_string(dap_sign_type_to_str(l_sign->header.type)));
            json_object_object_add(json_obj_item,"pub_key_size",json_object_new_uint64(l_sign->header.sign_pkey_size));
            json_object_object_add(json_obj_item,"sig_size",json_object_new_uint64(l_sign->header.sign_size));
            json_object_object_add(json_obj_item,"hash_type",json_object_new_uint64(l_sign->header.hash_type));
            
            char l_pkey_base64[DAP_ENC_BASE64_ENCODE_SIZE(l_sign->header.sign_pkey_size) + 1];
            size_t l_pkey_base64_size = dap_enc_base64_encode(l_sign->pkey_n_sign, l_sign->header.sign_pkey_size, l_pkey_base64, DAP_ENC_DATA_TYPE_B64_URLSAFE); 
            l_pkey_base64[l_pkey_base64_size] = '\0';   
            json_object_object_add(json_obj_item,"pub_key_b64", json_object_new_string(l_pkey_base64));     

            char l_sign_base64[DAP_ENC_BASE64_ENCODE_SIZE(l_sign->header.sign_size) + 1];
            size_t l_sign_base64_size = dap_enc_base64_encode(l_sign->pkey_n_sign + l_sign->header.sign_pkey_size, l_sign->header.sign_size, l_sign_base64, DAP_ENC_DATA_TYPE_B64_URLSAFE); 
            l_sign_base64[l_sign_base64_size] = '\0';   
            json_object_object_add(json_obj_item,"sig_b64", json_object_new_string(l_sign_base64));

        } break;
        case TX_ITEM_TYPE_TSD: {
            json_object_object_add(json_obj_item,"type", json_object_new_string("data"));
            json_object_object_add(json_obj_item,"type", json_object_new_uint64(((dap_chain_tx_tsd_t*)item)->header.type));
            json_object_object_add(json_obj_item,"size", json_object_new_uint64(((dap_chain_tx_tsd_t*)item)->header.size));            
        } break;
        case TX_ITEM_TYPE_IN_COND:
            json_object_object_add(json_obj_item,"type", json_object_new_string("in_cond"));
            l_hash_tmp = ((dap_chain_tx_in_cond_t*)item)->header.tx_prev_hash;
            l_hash_str = dap_hash_fast_to_str_static(&l_hash_tmp);
            json_object_object_add(json_obj_item,"receipt_idx", json_object_new_int(((dap_chain_tx_in_cond_t*)item)->header.receipt_idx));
            json_object_object_add(json_obj_item,"out_prev_idx", json_object_new_string(l_hash_str));
            json_object_object_add(json_obj_item,"prev_hash", json_object_new_uint64(((dap_chain_tx_in_cond_t*)item)->header.tx_out_prev_idx));
            break;
        case TX_ITEM_TYPE_OUT_COND: {
            char l_tmp_buff[70]={0};
            json_object_object_add(json_obj_item,"type", json_object_new_string("out_cond"));
            const char *l_coins_str, *l_value_str = dap_uint256_to_char(((dap_chain_tx_out_cond_t*)item)->header.value, &l_coins_str);
            dap_time_t l_ts_exp = ((dap_chain_tx_out_cond_t*)item)->header.ts_expires;
            dap_time_to_str_rfc822(l_tmp_buf, DAP_TIME_STR_SIZE, l_ts_exp);
            json_object_object_add(json_obj_item,"ts_expires", l_ts_exp ? json_object_new_string(l_tmp_buf) : json_object_new_string("never"));
            json_object_object_add(json_obj_item,"value", json_object_new_string(l_value_str));
            sprintf(l_tmp_buff,"0x%016"DAP_UINT64_FORMAT_x"",((dap_chain_tx_out_cond_t*)item)->header.srv_uid.uint64);
            json_object_object_add(json_obj_item,"service_id", json_object_new_string(l_tmp_buff));
            switch (((dap_chain_tx_out_cond_t*)item)->header.subtype) {
                case DAP_CHAIN_TX_OUT_COND_SUBTYPE_FEE:
                    json_object_object_add(json_obj_item,"subtype", json_object_new_string("fee"));
                    break;
                case DAP_CHAIN_TX_OUT_COND_SUBTYPE_SRV_PAY: {
                    const char *l_coins_str, *l_value_str =
                        dap_uint256_to_char( ((dap_chain_tx_out_cond_t*)item)->subtype.srv_pay.unit_price_max_datoshi, &l_coins_str );
                    l_hash_tmp = ((dap_chain_tx_out_cond_t*)item)->subtype.srv_pay.pkey_hash;
                    l_hash_str = dap_hash_fast_to_str_static(&l_hash_tmp);
                    sprintf(l_tmp_buff,"0x%08x",((dap_chain_tx_out_cond_t*)item)->subtype.srv_pay.unit.uint32);
                    json_object_object_add(json_obj_item,"price_unit", json_object_new_string(l_tmp_buff));
                    json_object_object_add(json_obj_item,"pkey", json_object_new_string(l_hash_str));
                    json_object_object_add(json_obj_item,"value_max_per_unit", json_object_new_string(l_value_str));
                    json_object_object_add(json_obj_item,"subtype", json_object_new_string("srv_pay"));
                } break;
                case DAP_CHAIN_TX_OUT_COND_SUBTYPE_SRV_STAKE_POS_DELEGATE: {
                    dap_chain_node_addr_t *l_signer_node_addr = &((dap_chain_tx_out_cond_t*)item)->subtype.srv_stake_pos_delegate.signer_node_addr;
                    dap_chain_addr_t *l_signing_addr = &((dap_chain_tx_out_cond_t*)item)->subtype.srv_stake_pos_delegate.signing_addr;
                    l_hash_tmp = l_signing_addr->data.hash_fast;
                    l_hash_str = dap_hash_fast_to_str_static(&l_hash_tmp);
                    json_object_object_add(json_obj_item,"signing_addr", json_object_new_string(dap_chain_addr_to_str_static(l_signing_addr)));            
                    sprintf(l_tmp_buff,""NODE_ADDR_FP_STR"",NODE_ADDR_FP_ARGS(l_signer_node_addr));
                    json_object_object_add(json_obj_item,"signer_node_addr", json_object_new_string(l_tmp_buff));
                    json_object_object_add(json_obj_item,"subtype", json_object_new_string("srv_stake_pos_delegate"));
                } break;
                case DAP_CHAIN_TX_OUT_COND_SUBTYPE_SRV_XCHANGE: {
                    const char *l_rate_str, *l_tmp_str =
                        dap_uint256_to_char( (((dap_chain_tx_out_cond_t*)item)->subtype.srv_xchange.rate), &l_rate_str );
                    sprintf(l_tmp_buff,"0x%016"DAP_UINT64_FORMAT_x"",((dap_chain_tx_out_cond_t*)item)->subtype.srv_xchange.buy_net_id.uint64);
                    json_object_object_add(json_obj_item,"net_id", json_object_new_string(l_tmp_buff));
                    json_object_object_add(json_obj_item,"token", json_object_new_string(((dap_chain_tx_out_cond_t*)item)->subtype.srv_xchange.buy_token));
                    json_object_object_add(json_obj_item,"rate", json_object_new_string(l_rate_str));
                    json_object_object_add(json_obj_item,"subtype", json_object_new_string("srv_xchange"));
                } break;
                case DAP_CHAIN_TX_OUT_COND_SUBTYPE_SRV_STAKE_LOCK: {
                    dap_time_t l_ts_unlock = ((dap_chain_tx_out_cond_t*)item)->subtype.srv_stake_lock.time_unlock;
                    dap_time_to_str_rfc822(l_tmp_buf, DAP_TIME_STR_SIZE, l_ts_unlock);
                    json_object_object_add(json_obj_item,"time_unlock", json_object_new_string(l_tmp_buf));
                    json_object_object_add(json_obj_item,"subtype", json_object_new_string("srv_stake_lock"));
                } break;
                default: break;
            }
        } break;
        case TX_ITEM_TYPE_OUT_EXT: {
            const char *l_coins_str, *l_value_str = dap_uint256_to_char( ((dap_chain_tx_out_ext_t*)item)->header.value, &l_coins_str );
            json_object_object_add(json_obj_item,"type", json_object_new_string("out_ext"));
            json_object_object_add(json_obj_item,"addr", json_object_new_string(dap_chain_addr_to_str_static(&((dap_chain_tx_out_ext_t*)item)->addr)));
            json_object_object_add(json_obj_item,"token", json_object_new_string(((dap_chain_tx_out_ext_t*)item)->token));
            json_object_object_add(json_obj_item,"value", json_object_new_string(l_value_str));
            
        } break;
        case TX_ITEM_TYPE_VOTING:{
            size_t l_tsd_size = 0;
            dap_chain_tx_tsd_t *l_item = (dap_chain_tx_tsd_t *)dap_chain_datum_tx_item_get(a_tx, NULL, (byte_t*)item + l_size, TX_ITEM_TYPE_TSD, &l_tsd_size);
            if (!l_item || !l_tsd_size)
                    break;
            dap_chain_datum_tx_voting_params_t *l_voting_params = dap_chain_voting_parse_tsd(a_tx);
            json_object_object_add(json_obj_item,"type", json_object_new_string("voting"));
            json_object_object_add(json_obj_item,"voting_question", json_object_new_string(l_voting_params->voting_question));
            json_object_object_add(json_obj_item,"answer_options", json_object_new_string(""));
            
            dap_list_t *l_temp = l_voting_params->answers_list;
            uint8_t l_index = 0;
            while (l_temp) {
                json_object_object_add(json_obj_item, dap_itoa(l_index), json_object_new_string((char *)l_temp->data));
                l_index++;
                l_temp = l_temp->next;
            }
            if (l_voting_params->voting_expire) {
                dap_time_to_str_rfc822(l_tmp_buf, DAP_TIME_STR_SIZE, l_voting_params->voting_expire);
                json_object_object_add(json_obj_item,"Voting expire", json_object_new_string(l_tmp_buf));                
            }
            if (l_voting_params->votes_max_count) {
                json_object_object_add(json_obj_item, "Votes max count", json_object_new_uint64(l_voting_params->votes_max_count));
            }
            json_object_object_add(json_obj_item,"Changing vote is", l_voting_params->vote_changing_allowed ? json_object_new_string("available") : 
                                    json_object_new_string("not available"));
            l_voting_params->delegate_key_required ? 
                json_object_object_add(json_obj_item,"Delegated key for participating in voting", json_object_new_string("required")):
                json_object_object_add(json_obj_item,"Delegated key for participating in voting", json_object_new_string("not required"));                 

            dap_list_free_full(l_voting_params->answers_list, NULL);
            DAP_DELETE(l_voting_params->voting_question);
            DAP_DELETE(l_voting_params);
        } break;
        case TX_ITEM_TYPE_VOTE:{
            dap_chain_tx_vote_t *l_vote_item = (dap_chain_tx_vote_t *)item;
            const char *l_hash_str = dap_chain_hash_fast_to_str_static(&l_vote_item->voting_hash);
            json_object_object_add(json_obj_item,"type", json_object_new_string("vote"));
            json_object_object_add(json_obj_item,"voting_hash", json_object_new_string(l_hash_str));
            json_object_object_add(json_obj_item,"vote_answer_idx", json_object_new_uint64(l_vote_item->answer_idx));

        } break;
        default:
            json_object_object_add(json_obj_item,"type", json_object_new_string("This transaction have unknown item type"));
            break;
        }
        json_object_array_add(json_arr_items, json_obj_item);
    }

    json_object_object_add(json_obj_out, "items", json_arr_items);

    json_object_object_add(json_obj_out, "timestamp", json_object_new_int64(dap_time_now()));
    json_object_object_add(json_obj_out, "datum_type", json_object_new_string("tx"));


    const char *l_out_buf = json_object_to_json_string_ext(json_obj_out, a_beauty ? JSON_C_TO_STRING_PRETTY : JSON_C_TO_STRING_PLAIN);
    char *l_out = DAP_DUP_SIZE(l_out_buf, strlen(l_out_buf));
    json_object_put(json_obj_out);

    return l_out;
}



static int s_wallet_create(const char *a_wallet_path, const char *a_wallet_name, const char *a_pass, const char *a_sig_type, const char *a_seed){
    dap_sign_type_t l_sig_type = dap_sign_type_from_str(a_sig_type);
    dap_chain_wallet_t *l_wallet = NULL;

    if ( l_sig_type.type == SIG_TYPE_NULL ) {
      printf("Invalid signature type '%s', you can use the following:\n\r%s",
              a_sig_type, dap_sign_get_str_recommended_types());
      exit( -2004 );
    }

    if (dap_sign_type_is_depricated(l_sig_type))
    {
        printf("Tesla, picnic, bliss algorithms is not supported, please, use another variant:\n\r%s",
                dap_sign_get_str_recommended_types());
        exit( -2004 );
    }

    uint8_t *l_seed = NULL;
    size_t l_seed_size = 0;

    if(a_seed) {
        const char* l_seed_hash_str = dap_get_data_hash_str(a_seed, strlen(a_seed)).s;
        size_t l_restore_str_size = dap_strlen(l_seed_hash_str);
        if (l_restore_str_size > 3 && !dap_strncmp(l_seed_hash_str, "0x", 2) && (!dap_is_hex_string(l_seed_hash_str + 2, l_restore_str_size - 2))) {
            l_seed_size = (l_restore_str_size - 2) / 2;
            l_seed = DAP_NEW_Z_SIZE(uint8_t, l_seed_size + 1);
            if(!l_seed) {
                printf("Memory allocation error.\n\r");
                exit(-100);
            }
            dap_hex2bin(l_seed, l_seed_hash_str + 2, l_restore_str_size - 2);
        } else {
            printf("Restored hash is invalid or too short, wallet is not created. Please use -seed 0x<hex_value>\n\r");
            exit(-1);
        }
    }

    if (l_sig_type.type == SIG_TYPE_MULTI_CHAINED){
        // if (argc < 7) {
        //     log_it(L_ERROR, "For a signature with type sig_multi_chained, two more signature type parameters must be set.");
        //     exit(-2006);
        // }
        // dap_sign_type_t l_types[MAX_ENC_KEYS_IN_MULTYSIGN] = {0};
        // size_t l_count_signs  = 0;
        // for (int i = 6; i < argc; i++) {
        //     l_types[l_count_signs] = dap_sign_type_from_str(argv[i]);
        //     if (l_types[l_count_signs].type == SIG_TYPE_NULL) {
        //         log_it( L_ERROR, "Invalid signature type '%s', you can use the following:\n%s",
        //                 argv[i], dap_sign_get_str_recommended_types());
        //         exit(-2007);
        //     }
        //     if (dap_sign_type_is_depricated(l_types[l_count_signs]))
        //     {
        //         log_it( L_ERROR, "Tesla, picnic, bliss algorithms is not supported, please, use another variant:\n%s",
        //                 dap_sign_get_str_recommended_types());
        //         exit( -2008 );
        //     }
        //     l_count_signs++;
        // }
        // l_wallet = dap_chain_wallet_create_with_seed_multi(l_wallet_name, s_system_wallet_dir,
        //                                                        l_types, l_count_signs,
        //                                                        NULL, 0, NULL);
        printf("Multisigned wallet not supported yet.\n\r");
        return -1;
    } else {
        if (!l_seed)
            l_wallet = dap_chain_wallet_create(a_wallet_name, a_wallet_path, l_sig_type, a_pass);
        else 
            l_wallet = dap_chain_wallet_create_with_seed(a_wallet_name, a_wallet_path, l_sig_type, l_seed, l_seed_size, a_pass);
    }
        

    if (l_wallet) {
        printf("Wallet %s has been created.\n\r", a_wallet_name);
        return 0;
    } else {
        printf("Failed to create a wallet.\n\r");
        return -1;
    }
}