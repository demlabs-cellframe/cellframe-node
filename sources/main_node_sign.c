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

#define LOG_TAG "sign_tool"
static dap_chain_datum_tx_t* json_parse_input_tx (json_object* a_in);
static char* convert_tx_to_json_string(dap_chain_datum_tx_t *a_tx);

int main(int argc, const char **argv)
{
  dap_set_appname("cellframe-node");
    char buffer[BUFSIZ] = {0};

    // Get data from stdin
    size_t bytes_read = read (STDIN_FILENO, buffer, sizeof buffer);
    if (!bytes_read){
      log_it( L_ERROR, "Can't read data");
      return -1;
    }

    // Parse json
    struct json_object *l_json = json_tokener_parse(buffer);
    if (!l_json){
      log_it( L_ERROR, "Can't parse json");
      return -1;
    }

    // Make binary transaction
    dap_chain_datum_tx_t *l_tx = json_parce_input_tx (l_json);

    // Sign it
    // add 'sign' items
    dap_enc_key_t *l_owner_key = NULL; //dap_chain_wallet_get_key(l_wallet, 0);
    if(dap_chain_datum_tx_add_sign_item(&l_tx, l_owner_key) != 1) {
        dap_chain_datum_tx_delete(l_tx);
        dap_enc_key_delete(l_owner_key);
        log_it( L_ERROR, "Can't add sign output");
        return -1;
    }

    // Convert to JSON transaction
    char *l_out = convert_tx_to_json_string(l_tx);
    if (!l_out){
      dap_chain_datum_tx_delete(l_tx);
      printf("error\n\r");
      return -1;
    }
    // Send to stdout
    size_t out_bytes = write(STDOUT_FILENO, l_out, bytes_read);
    if (out_bytes <= 0){
        log_it(L_ERROR, "Can't write result\n\r");
        dap_chain_datum_tx_delete(l_tx);
        return -1;
    }

    dap_chain_datum_tx_delete(l_tx);
    return 0;
}



static dap_chain_datum_tx_t* json_parce_input_tx (json_object* a_in)
{
  dap_chain_datum_tx_t *l_tx = NULL;




  return l_tx;
}


static char* convert_tx_to_json_string(dap_chain_datum_tx_t *a_tx)
{
  json_object* l_json_arr_reply = NULL;
  dap_hash_fast_t l_hash_tmp = { };
  byte_t *item; size_t l_size;
  const char *l_hash_str = NULL;
  TX_ITEM_ITER_TX(item, l_size, a_tx) {
      json_object* json_obj_item = json_object_new_object();
      switch (*item) {
      case TX_ITEM_TYPE_IN:
          l_hash_tmp = ((dap_chain_tx_in_t*)item)->header.tx_prev_hash;
          l_hash_str = dap_enc_base58_encode_hash_to_str_static(&l_hash_tmp);
          json_object_object_add(json_obj_item,"item type", json_object_new_string("IN"));
          json_object_object_add(json_obj_item,"Tx prev hash", json_object_new_string(l_hash_str));
          json_object_object_add(json_obj_item,"Tx out prev idx", json_object_new_uint64(((dap_chain_tx_in_t*)item)->header.tx_out_prev_idx));
          break;
      case TX_ITEM_TYPE_OUT_OLD: {
          const char *l_value_str = dap_uint256_to_char(
              dap_chain_uint256_from(((dap_chain_tx_out_old_t*)item)->header.value), NULL );
          json_object_object_add(json_obj_item,"item type", json_object_new_string("OUT OLD"));
          json_object_object_add(json_obj_item,"Value", json_object_new_uint64(((dap_chain_tx_out_old_t*)item)->header.value));
          json_object_object_add(json_obj_item,"Address", json_object_new_string(dap_chain_addr_to_str_static(&((dap_chain_tx_out_old_t*)item)->addr)));
      } break;
      case TX_ITEM_TYPE_OUT: { // 256
          const char *l_coins_str,
                  *l_value_str = dap_uint256_to_char(((dap_chain_tx_out_t*)item)->header.value, &l_coins_str),
                  *l_addr_str = dap_chain_addr_to_str_static(&((dap_chain_tx_out_t*)item)->addr);
          json_object_object_add(json_obj_item,"item type", json_object_new_string("OUT"));
          json_object_object_add(json_obj_item,"Coins", json_object_new_string(l_coins_str));
          json_object_object_add(json_obj_item,"Value", json_object_new_string(l_value_str));
          json_object_object_add(json_obj_item,"Address", json_object_new_string(l_addr_str));            
      } break;
      case TX_ITEM_TYPE_IN_EMS: {
          char l_tmp_buff[70]={0};
          l_hash_tmp = ((dap_chain_tx_in_ems_t*)item)->header.token_emission_hash;
          l_hash_str = dap_enc_base58_encode_hash_to_str_static(&l_hash_tmp);
          json_object_object_add(json_obj_item,"item type", json_object_new_string("IN_EMS"));
          json_object_object_add(json_obj_item,"ticker", json_object_new_string(((dap_chain_tx_in_ems_t*)item)->header.ticker));
          json_object_object_add(json_obj_item,"token_emission_hash", json_object_new_string(l_hash_str));
          sprintf(l_tmp_buff,"0x%016"DAP_UINT64_FORMAT_x"",((dap_chain_tx_in_ems_t*)item)->header.token_emission_chain_id.uint64);
          json_object_object_add(json_obj_item,"token_emission_chain_id", json_object_new_string(l_tmp_buff));
      } break;

      case TX_ITEM_TYPE_IN_REWARD: {
          l_hash_tmp = ((dap_chain_tx_in_reward_t *)item)->block_hash;
          l_hash_str = dap_enc_base58_encode_hash_to_str_static(&l_hash_tmp);
          json_object_object_add(json_obj_item,"item type", json_object_new_string("IN_REWARD"));
          json_object_object_add(json_obj_item,"block_hash", json_object_new_string(l_hash_str));
      } break;

      case TX_ITEM_TYPE_SIG: {
          dap_sign_t *l_sign = dap_chain_datum_tx_item_sign_get_sig((dap_chain_tx_sig_t*)item);
          json_object_object_add(json_obj_item,"item type", json_object_new_string("SIG"));
          dap_sign_get_information_json(l_json_arr_reply, l_sign, json_obj_item, a_hash_out_type);
          dap_chain_addr_t l_sender_addr;
          dap_chain_addr_fill_from_sign(&l_sender_addr, l_sign, a_net_id);
          json_object_object_add(json_obj_item,"Sender addr", json_object_new_string(dap_chain_addr_to_str_static(&l_sender_addr)));            
      } break;
      case TX_ITEM_TYPE_RECEIPT: {
          const char *l_coins_str, *l_value_str = dap_uint256_to_char(((dap_chain_datum_tx_receipt_t*)item)->receipt_info.value_datoshi, &l_coins_str);
          json_object_object_add(json_obj_item,"item type", json_object_new_string("RECEIPT"));
          json_object_object_add(json_obj_item,"size", json_object_new_uint64(((dap_chain_datum_tx_receipt_t*)item)->size));
          json_object_object_add(json_obj_item,"ext size", json_object_new_uint64(((dap_chain_datum_tx_receipt_t*)item)->exts_size));
          json_object_object_add(json_obj_item,"INFO", json_object_new_string(""));
          json_object_object_add(json_obj_item,"units", json_object_new_uint64(((dap_chain_datum_tx_receipt_t*)item)->receipt_info.units));
          json_object_object_add(json_obj_item,"uid", json_object_new_uint64(((dap_chain_datum_tx_receipt_t*)item)->receipt_info.srv_uid.uint64));
          json_object_object_add(json_obj_item,"units type", json_object_new_string(dap_chain_srv_unit_enum_to_str(((dap_chain_datum_tx_receipt_t*)item)->receipt_info.units_type.enm)));
          json_object_object_add(json_obj_item,"coins", json_object_new_string(l_coins_str));
          json_object_object_add(json_obj_item,"value", json_object_new_string(l_value_str));

          json_object_object_add(json_obj_item,"Exts",json_object_new_string(""));                         
          switch ( ((dap_chain_datum_tx_receipt_t*)item)->exts_size ) {
          case (sizeof(dap_sign_t) * 2): {
              dap_sign_t *l_client = DAP_CAST_PTR( dap_sign_t, ((dap_chain_datum_tx_receipt_t*)item)->exts_n_signs + sizeof(dap_sign_t) );
              json_object_object_add(json_obj_item,"Client", json_object_new_string(""));
              dap_sign_get_information_json(l_json_arr_reply, l_client, json_obj_item, a_hash_out_type);                
          }
          case (sizeof(dap_sign_t)): {
              dap_sign_t *l_provider = DAP_CAST_PTR( dap_sign_t, ((dap_chain_datum_tx_receipt_t*)item)->exts_n_signs );
              json_object_object_add(json_obj_item,"Provider", json_object_new_string(""));
              dap_sign_get_information_json(l_json_arr_reply, l_provider,json_obj_item, a_hash_out_type);
              break;
          }
          }
      } break;
      case TX_ITEM_TYPE_PKEY: {
          dap_pkey_t *l_pkey = (dap_pkey_t*)((dap_chain_tx_pkey_t*)item)->pkey;
          dap_chain_hash_fast_t l_pkey_hash;
          dap_hash_fast(l_pkey->pkey, l_pkey->header.size, &l_pkey_hash);
          l_hash_str = dap_strcmp(a_hash_out_type, "hex")
                  ? dap_enc_base58_encode_hash_to_str_static(&l_pkey_hash)
                  : dap_chain_hash_fast_to_str_static(&l_pkey_hash);
          json_object_object_add(json_obj_item,"item type", json_object_new_string("PKey"));
          json_object_object_add(json_obj_item,"PKey", json_object_new_string(""));
          json_object_object_add(json_obj_item,"SIG type", json_object_new_string(dap_sign_type_to_str(((dap_chain_tx_pkey_t*)item)->header.sig_type)));
          json_object_object_add(json_obj_item,"SIG size", json_object_new_uint64(((dap_chain_tx_pkey_t*)item)->header.sig_size));
          json_object_object_add(json_obj_item,"Sequence number", json_object_new_uint64(((dap_chain_tx_pkey_t*)item)->seq_no));
          json_object_object_add(json_obj_item,"Key", json_object_new_string(""));
          json_object_object_add(json_obj_item,"Type", json_object_new_string(dap_pkey_type_to_str(l_pkey->header.type)));
          json_object_object_add(json_obj_item,"Size", json_object_new_uint64(l_pkey->header.size));
          json_object_object_add(json_obj_item,"Hash", json_object_new_string(l_hash_str));

      } break;
      case TX_ITEM_TYPE_TSD: {
          json_object_object_add(json_obj_item,"item type", json_object_new_string("TSD data"));
          json_object_object_add(json_obj_item,"type", json_object_new_uint64(((dap_chain_tx_tsd_t*)item)->header.type));
          json_object_object_add(json_obj_item,"size", json_object_new_uint64(((dap_chain_tx_tsd_t*)item)->header.size));            
      } break;
      case TX_ITEM_TYPE_IN_COND:
          json_object_object_add(json_obj_item,"item type", json_object_new_string("IN COND"));
          l_hash_tmp = ((dap_chain_tx_in_cond_t*)item)->header.tx_prev_hash;
          l_hash_str = dap_strcmp(a_hash_out_type, "hex")
                  ? dap_enc_base58_encode_hash_to_str_static(&l_hash_tmp)
                  : dap_chain_hash_fast_to_str_static(&l_hash_tmp);
          json_object_object_add(json_obj_item,"Receipt_idx", json_object_new_int(((dap_chain_tx_in_cond_t*)item)->header.receipt_idx));
          json_object_object_add(json_obj_item,"Tx_prev_hash", json_object_new_string(l_hash_str));
          json_object_object_add(json_obj_item,"Tx_out_prev_idx", json_object_new_uint64(((dap_chain_tx_in_cond_t*)item)->header.tx_out_prev_idx));
          break;
      case TX_ITEM_TYPE_OUT_COND: {
          char l_tmp_buff[70]={0};
          json_object_object_add(json_obj_item,"item type", json_object_new_string("OUT COND"));
          const char *l_coins_str, *l_value_str = dap_uint256_to_char(((dap_chain_tx_out_cond_t*)item)->header.value, &l_coins_str);
          dap_time_t l_ts_exp = ((dap_chain_tx_out_cond_t*)item)->header.ts_expires;
          dap_time_to_str_rfc822(l_tmp_buf, DAP_TIME_STR_SIZE, l_ts_exp);
          json_object_object_add(json_obj_item,"Header", json_object_new_string(""));
          json_object_object_add(json_obj_item,"ts_expires", l_ts_exp ? json_object_new_string(l_tmp_buf) : json_object_new_string("never"));
          json_object_object_add(json_obj_item,"coins", json_object_new_string(l_coins_str));
          json_object_object_add(json_obj_item,"value", json_object_new_string(l_value_str));
          json_object_object_add(json_obj_item,"subtype", json_object_new_string(dap_chain_tx_out_cond_subtype_to_str(((dap_chain_tx_out_cond_t*)item)->header.subtype)));
          sprintf(l_tmp_buff,"0x%016"DAP_UINT64_FORMAT_x"",((dap_chain_tx_out_cond_t*)item)->header.srv_uid.uint64);
          json_object_object_add(json_obj_item,"uid", json_object_new_string(l_tmp_buff));
          switch (((dap_chain_tx_out_cond_t*)item)->header.subtype) {
              case DAP_CHAIN_TX_OUT_COND_SUBTYPE_SRV_PAY: {
                  const char *l_coins_str, *l_value_str =
                      dap_uint256_to_char( ((dap_chain_tx_out_cond_t*)item)->subtype.srv_pay.unit_price_max_datoshi, &l_coins_str );
                  l_hash_tmp = ((dap_chain_tx_out_cond_t*)item)->subtype.srv_pay.pkey_hash;
                  l_hash_str = dap_strcmp(a_hash_out_type, "hex")
                          ? dap_enc_base58_encode_hash_to_str_static(&l_hash_tmp)
                          : dap_chain_hash_fast_to_str_static(&l_hash_tmp);
                  sprintf(l_tmp_buff,"0x%08x",((dap_chain_tx_out_cond_t*)item)->subtype.srv_pay.unit.uint32);
                  json_object_object_add(json_obj_item,"unit", json_object_new_string(l_tmp_buff));
                  json_object_object_add(json_obj_item,"pkey", json_object_new_string(l_hash_str));
                  json_object_object_add(json_obj_item,"max price(coins)", json_object_new_string(l_coins_str));
                  json_object_object_add(json_obj_item,"max price(value)", json_object_new_string(l_value_str));

              } break;
              case DAP_CHAIN_TX_OUT_COND_SUBTYPE_SRV_STAKE_POS_DELEGATE: {
                  dap_chain_node_addr_t *l_signer_node_addr = &((dap_chain_tx_out_cond_t*)item)->subtype.srv_stake_pos_delegate.signer_node_addr;
                  dap_chain_addr_t *l_signing_addr = &((dap_chain_tx_out_cond_t*)item)->subtype.srv_stake_pos_delegate.signing_addr;
                  l_hash_tmp = l_signing_addr->data.hash_fast;
                  l_hash_str = dap_strcmp(a_hash_out_type, "hex")
                          ? dap_enc_base58_encode_hash_to_str_static(&l_hash_tmp)
                          : dap_chain_hash_fast_to_str_static(&l_hash_tmp);
                  json_object_object_add(json_obj_item,"signing_addr", json_object_new_string(dap_chain_addr_to_str_static(l_signing_addr)));
                  json_object_object_add(json_obj_item,"with pkey hash", json_object_new_string(l_hash_str));                    
                  sprintf(l_tmp_buff,""NODE_ADDR_FP_STR"",NODE_ADDR_FP_ARGS(l_signer_node_addr));
                  json_object_object_add(json_obj_item,"signer_node_addr", json_object_new_string(l_tmp_buff));
                  
              } break;
              case DAP_CHAIN_TX_OUT_COND_SUBTYPE_SRV_XCHANGE: {
                  const char *l_rate_str, *l_tmp_str =
                      dap_uint256_to_char( (((dap_chain_tx_out_cond_t*)item)->subtype.srv_xchange.rate), &l_rate_str );
                  sprintf(l_tmp_buff,"0x%016"DAP_UINT64_FORMAT_x"",((dap_chain_tx_out_cond_t*)item)->subtype.srv_xchange.buy_net_id.uint64);
                  json_object_object_add(json_obj_item,"net id", json_object_new_string(l_tmp_buff));
                  json_object_object_add(json_obj_item,"buy_token", json_object_new_string(((dap_chain_tx_out_cond_t*)item)->subtype.srv_xchange.buy_token));
                  json_object_object_add(json_obj_item,"rate", json_object_new_string(l_rate_str));
              } break;
              case DAP_CHAIN_TX_OUT_COND_SUBTYPE_SRV_STAKE_LOCK: {
                  dap_time_t l_ts_unlock = ((dap_chain_tx_out_cond_t*)item)->subtype.srv_stake_lock.time_unlock;
                  dap_time_to_str_rfc822(l_tmp_buf, DAP_TIME_STR_SIZE, l_ts_unlock);
                  json_object_object_add(json_obj_item,"time_unlock", json_object_new_string(l_tmp_buf));
              } break;
              default: break;
          }
      } break;
      case TX_ITEM_TYPE_OUT_EXT: {
          const char *l_coins_str, *l_value_str = dap_uint256_to_char( ((dap_chain_tx_out_ext_t*)item)->header.value, &l_coins_str );
          json_object_object_add(json_obj_item,"item type", json_object_new_string("OUT EXT"));
          json_object_object_add(json_obj_item,"Addr", json_object_new_string(dap_chain_addr_to_str_static(&((dap_chain_tx_out_ext_t*)item)->addr)));
          json_object_object_add(json_obj_item,"Token", json_object_new_string(((dap_chain_tx_out_ext_t*)item)->token));
          json_object_object_add(json_obj_item,"Coins", json_object_new_string(l_coins_str));
          json_object_object_add(json_obj_item,"Value", json_object_new_string(l_value_str));
          
      } break;
      case TX_ITEM_TYPE_VOTING:{
          size_t l_tsd_size = 0;
          dap_chain_tx_tsd_t *l_item = (dap_chain_tx_tsd_t *)dap_chain_datum_tx_item_get(a_datum, NULL, (byte_t*)item + l_size, TX_ITEM_TYPE_TSD, &l_tsd_size);
          if (!l_item || !l_tsd_size)
                  break;
          dap_chain_datum_tx_voting_params_t *l_voting_params = dap_chain_voting_parse_tsd(a_datum);
          json_object_object_add(json_obj_item,"item type", json_object_new_string("VOTING"));
          json_object_object_add(json_obj_item,"Voting question", json_object_new_string(l_voting_params->voting_question));
          json_object_object_add(json_obj_item,"Answer options", json_object_new_string(""));
          
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
          json_object_object_add(json_obj_item,"item type", json_object_new_string("VOTE"));
          json_object_object_add(json_obj_item,"Voting hash", json_object_new_string(l_hash_str));
          json_object_object_add(json_obj_item,"Vote answer idx", json_object_new_uint64(l_vote_item->answer_idx));

      } break;
      default:
          json_object_object_add(json_obj_item,"item type", json_object_new_string("This transaction have unknown item type"));
          break;
      }
      json_object_array_add(json_arr_items, json_obj_item);
  }

  return NULL;
}