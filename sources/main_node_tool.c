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
#include <unistd.h>
#include <stdlib.h>
#include <stdio.h>
#include <sys/types.h>
#include <getopt.h>
#include <string.h>

#include "sig_unix_handler.h"
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

#include "dap_chain_cert.h"
#include "dap_chain_cert_file.h"

#include "dap_chain_block.h"
#include "dap_chain_blocks.h"
#include "dap_chain_block_cs.h"
#include "dap_chain_block_cs_poa.h"


#include "dap_chain_dag.h"
#include "dap_chain_dag_cs.h"
#include "dap_chain_dag_cs_hashgraph.h"
#include "dap_chain_dag_cs_poa.h"
#include "dap_chain_dag_cs_poh.h"

#include "dap_chain_net.h"
#include "dap_chain_net_srv.h"
#include "dap_chain_net_srv_app.h"
#include "dap_chain_net_srv_app_db.h"
#include "dap_chain_net_srv_datum.h"
#include "dap_chain_net_srv_datum_pool.h"
#include "dap_chain_net_srv_vpn.h"


#include "dap_stream_session.h"
#include "dap_stream.h"
#include "dap_stream_ch_vpn.h"
#include "dap_stream_ch_chain.h"
#include "dap_stream_ch_chain_net.h"
#include "dap_stream_ch_chain_net_srv.h"

#include "dap_common.h"
#include "dap_client.h"
#include "dap_http_simple.h"
#include "dap_process_manager.h"

#define DAP_APP_NAME NODE_NETNAME"-node"
#define SYSTEM_PREFIX "/opt/"DAP_APP_NAME
#define LOCAL_PREFIX "~/."DAP_APP_NAME

#define SYSTEM_CONFIGS_DIR SYSTEM_PREFIX"/etc"
#define LOCAL_CONFIGS_DIR LOCAL_PREFIX"/etc"

#define SYSTEM_CA_DIR SYSTEM_PREFIX"/var/lib/ca"
#define LOCAL_CA_DIR LOCAL_PREFIX"/ca"

#define SYSTEM_CONFIG_GLOBAL_FILENAME SYSTEM_PREFIX"/etc/"DAP_APP_NAME".cfg"
#define LOCAL_CONFIG_GLOBAL LOCAL_PREFIX"/etc/"DAP_APP_NAME".cfg"

#define SYSTEM_PID_FILE_PATH SYSTEM_PREFIX"/run/"DAP_APP_NAME".pid"
#define LOCAL_PID_FILE_PATH SYSTEM_PREFIX"/run/"DAP_APP_NAME".pid"

#define ENC_HTTP_URL "/enc_init"
#define STREAM_CTL_URL "/stream_ctl"
#define STREAM_URL "/stream"
#define SLIST_URL "/nodelist"
#define MAIN_URL "/"
#define LOG_TAG "main_node_tool"



static int s_init(int argc, const char * argv[]);
static void s_help();

static dap_config_t * g_config;
static const char * s_appname;
int main(int argc, const char * argv[])
{
    int ret;
    s_appname = argv[0];
    ret = s_init(argc, argv);
    if (ret == 0){
        if( argc >= 2 ){
            if (strcmp (argv[1],"cert") == 0 ){
                if ( argc >=3 ){
                    if ( strcmp( argv[2],"dump") == 0 ){
                        if (argc>=4) {
                            const char * l_cert_name = argv[3];
                            dap_chain_cert_t * l_cert = dap_chain_cert_add_file(l_cert_name,SYSTEM_CA_DIR);
                            if ( l_cert ){
                                dap_chain_cert_dump(l_cert);
                                dap_chain_cert_delete(l_cert_name);
                                ret = 0;
                            }else{
                                exit(-702);
                            }
                        }
                    }else if ( strcmp( argv[2],"create_pkey") == 0 ){
                        if (argc>=5) {
                            const char * l_cert_name = argv[3];
                            const char * l_cert_pkey_path = argv[4];
                            dap_chain_cert_t * l_cert = dap_chain_cert_add_file(l_cert_name,SYSTEM_CA_DIR);
                            if ( l_cert ){
                                l_cert->key_private->pub_key_data_size = dap_enc_gen_key_public_size(l_cert->key_private);
                                if ( l_cert->key_private->pub_key_data_size ){
                                    //l_cert->key_private->pub_key_data = DAP_NEW_SIZE(void, l_cert->key_private->pub_key_data_size);
                                    //if ( dap_enc_gen_key_public(l_cert->key_private, l_cert->key_private->pub_key_data) == 0){
                                        dap_chain_pkey_t * l_pkey = dap_chain_pkey_from_enc_key( l_cert->key_private );
                                        if (l_pkey){
                                            FILE * l_file = fopen(l_cert_pkey_path,"w");
                                            if (l_file){
                                                fwrite(l_pkey,1,l_pkey->header.size + sizeof(l_pkey->header),l_file);
                                                fclose(l_file);
                                            }
                                        }else {
                                            log_it(L_CRITICAL, "Can't produce pkey from the certificate");
                                            exit(-7022);
                                        }
                                        dap_chain_cert_delete(l_cert_name);

                                        ret = 0;
                                    //}else{
                                    //    log_it(L_CRITICAL,"Can't produce public key with this key type");
                                    //    exit(-7024);
                                    //}
                                }else{
                                    log_it(L_CRITICAL,"Can't produce pkey from this cert type");
                                    exit(-7023);
                                }
                            }else{
                                exit(-7021);
                            }
                        }
                    }
                    else if ( strcmp( argv[2],"create" ) == 0 ){
                        if (argc>=5) {
                            size_t l_key_length = 0;
                            const char * l_cert_name = argv[3];
                            size_t l_cert_path_length = strlen(argv[3])+8+strlen(SYSTEM_CA_DIR);
                            char * l_cert_path = DAP_NEW_Z_SIZE(char,l_cert_path_length);
                            snprintf(l_cert_path,l_cert_path_length,"%s/%s.dcert",SYSTEM_CA_DIR,l_cert_name);
                            if( access( l_cert_path, F_OK ) != -1 ) {
                                log_it (L_ERROR, "File %s is already exists! Who knows, may be its smth important?", l_cert_path);
                                exit(-700);
                            }
                            dap_enc_key_type_t l_key_type = DAP_ENC_KEY_TYPE_NULL;
                            if ( strcmp (argv[4],"sig_bliss") == 0 ){
                                l_key_type = DAP_ENC_KEY_TYPE_SIG_BLISS;
                            } else if ( strcmp (argv[4],"sig_tesla") == 0){
                                l_key_type = DAP_ENC_KEY_TYPE_SIG_TESLA;
                            } else if ( strcmp (argv[4],"sig_picnic") == 0){
                                l_key_type = DAP_ENC_KEY_TYPE_SIG_PICNIC;
                            }else{
                               log_it (L_ERROR, "Wrong key create action \"%s\"",argv[4]);
                                exit(-600);
                            }
                            if ( l_key_type != DAP_ENC_KEY_TYPE_NULL ){
                                int l_key_length = argc >=6 ? atoi(argv[5]) : 0;
                                dap_chain_cert_t * l_cert = dap_chain_cert_generate(l_cert_name,l_cert_path,l_key_type ); // key length ignored!
                                if (l_cert == NULL){
                                    log_it(L_CRITICAL, "Can't create %s",l_cert_path);
                                }
                            } else {
                                s_help();
                                DAP_DELETE(l_cert_path);
                                exit(-500);
                            }
                            DAP_DELETE(l_cert_path);
                        }else{
                            s_help();
                            exit(-500);
                        }
                    }else {
                        log_it(L_CRITICAL,"Wrong params");
                        s_help();
                        exit(-1000);
                    }
                }else {
                    log_it(L_CRITICAL,"Wrong params");
                    s_help();
                    exit(-1000);
                }
            }else {
                log_it(L_CRITICAL,"Wrong params");
                s_help();
                exit(-1000);
            }
        }else {
            log_it(L_CRITICAL,"Wrong params");
            s_help();
            exit(-1000);
        }
    }else
        log_it(L_CRITICAL,"Can't init modules");
    return ret;
}

/**
 * @brief s_init
 * @param argc
 * @param argv
 * @return
 */
static int s_init(int argc, const char * argv[])
{
    dap_config_init(SYSTEM_CONFIGS_DIR);
    if((g_config = dap_config_open(DAP_APP_NAME) ) == NULL) {
        log_it(L_CRITICAL,"Can't init general configurations");
        return -1;
    }

    if(dap_common_init(DAP_APP_NAME"_logs.txt")!=0){
        log_it(L_CRITICAL,"Can't init common functions module");
        return -2;
    }

    if (dap_chain_cert_init() != 0) {
        log_it(L_CRITICAL,"Can't chain certificate storage module");
        return -3;

    }

}

/**
 * @brief s_help
 * @param a_appname
 */
static void s_help()
{
    printf("%s usage:\n",s_appname);
    printf("\t\t%s cert create <cert name> <key type> [<key length>]\n",s_appname);
    printf("\nCreate new key file with randomly produced key stored in\n\n");
    printf("\t\t%s cert dump <cert name>\n",s_appname);
    printf("\nDump cert data stored in <file path>\n");
    printf("\t\t%s cert create_pkey <cert name> <pkey path>\n",s_appname);
    printf("\nCreate pkey from <cert name> and store it on <pkey path>\n");
}

