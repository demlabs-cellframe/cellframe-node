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
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/types.h>
#include <getopt.h>
#include <string.h>

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
#endif

#include <pthread.h>

#include "dap_common.h"

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

#include "dap_chain_cs_dag.h"
#include "dap_chain_cs_dag_event.h"
#include "dap_chain_cs_dag_poa.h"
#include "dap_chain_cs_dag_pos.h"

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

#include "dap_chain_wallet.h"

#include "dap_client.h"
#include "dap_http_simple.h"
#include "dap_process_manager.h"

#define DAP_APP_NAME NODE_NETNAME "-node"
#ifdef _WIN32
  #define SYSTEM_PREFIX "opt/"DAP_APP_NAME
#else
  #define SYSTEM_PREFIX "/opt/"DAP_APP_NAME
#endif

#define LOCAL_PREFIX "~/."DAP_APP_NAME

#define SYSTEM_CONFIGS_DIR SYSTEM_PREFIX"/etc"
#define LOCAL_CONFIGS_DIR LOCAL_PREFIX"/etc"

#define SYSTEM_CA_DIR SYSTEM_PREFIX"/var/lib/ca"
#define LOCAL_CA_DIR LOCAL_PREFIX"/ca"

#define SYSTEM_WALLET_DIR SYSTEM_PREFIX"/var/lib/wallet"
#define LOCAL_WALLET_DIR LOCAL_PREFIX"/wallet"

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

static int s_init( int argc, const char * argv[] );
static void s_help( );

static const char *s_appname = "kelvin-node-tool";

int main( int argc, const char **argv )
{
  uint8_t *buff = (uint8_t *)malloc( 8192 );
  int ret = s_init( argc, argv );

  if ( ret ) {
    log_it( L_ERROR, "Can't init modules" );
    return ret;
  }

  if ( argc < 2 ) {
    log_it( L_INFO, "No params. Nothing to do" );
    s_help( );
    exit( -1000 );
  }

  if ( strcmp ( argv[1], "wallet" ) == 0 ) {

    if ( argc < 3 ) {
      log_it(L_ERROR,"Wrong 'wallet' command params");
      s_help();
      exit(-2001);
    }

    if ( strcmp( argv[2],"create") == 0 ) {

      // wallet create <network name> <wallet name> <wallet_sign>
      if ( argc < 6 ) {
        log_it( L_ERROR, "Wrong 'wallet create' command params" );
        s_help( );
        exit( -2003 );
      }

      dap_chain_net_id_t l_network_id = dap_chain_net_id_by_name( argv[3] );
      if ( !l_network_id.raw ) {
        log_it( L_ERROR, "No such network name '%s'", argv[3] );
        s_help() ;
        exit( -2005 );
      }

      const char *l_wallet_name = argv[4];
      dap_chain_sign_type_t l_sig_type = dap_chain_sign_type_from_str( argv[5] );
      dap_chain_wallet_t *l_wallet = NULL;

      if ( l_sig_type.type == SIG_TYPE_NULL ) {
        log_it( L_ERROR, "Wrong signature '%s'", argv[4] );
        s_help( );
        exit( -2004 );
      }

      size_t l_wallet_path_size = strlen( l_wallet_name ) + strlen( SYSTEM_WALLET_DIR ) + 10;
      char * l_wallet_path = DAP_NEW_Z_SIZE( char, l_wallet_path_size );
      snprintf( l_wallet_path, l_wallet_path_size, "%s/%s.dwallet", SYSTEM_WALLET_DIR, l_wallet_name );
      l_wallet = dap_chain_wallet_create( l_wallet_name, SYSTEM_WALLET_DIR, l_network_id, l_sig_type );
      DAP_DELETE (l_wallet_path);

    }
    else if ( strcmp( argv[2],"sign_file") == 0 ) {

      // wallet sign_file <wallet name> <cert index> <data file path> <data offset> <data length> <dsign file path>
      if ( argc < 8 ) {
        log_it(L_ERROR,"Wrong 'wallet sign_file' command params");
        s_help();
        exit(-3000);
      }
      dap_chain_wallet_t *l_wallet = dap_chain_wallet_open( argv[3], SYSTEM_WALLET_DIR );
      if ( !l_wallet ) {
        log_it(L_ERROR,"Can't open wallet \"%s\"",argv[3]);
        s_help();
        exit(-3001);
      }

      int l_cert_index = atoi(argv[4]);

      size_t l_wallet_certs_number = dap_chain_wallet_get_certs_number( l_wallet );
      if ( (l_cert_index > 0) && (l_wallet_certs_number > (size_t)l_cert_index) ) {
        FILE *l_data_file = fopen( argv[5],"rb" );
        if ( l_data_file ) {}
      } 
      else {
        log_it( L_ERROR, "Cert index %d can't be found in wallet with %u certs inside"
                                           ,l_cert_index,l_wallet_certs_number );
        s_help();
        exit( -3002 );
      }
    }
                   /* if ( strcmp( argv[2],"create_from") == 0 ){
                        }else if ( argc >=7){
                            // wallet create_from <wallet name> from <wallet ca1> [<wallet ca2> ...<wallet caN>]
                            dap_chain_cert_t ** l_wallet_cert = NULL;
                            size_t l_wallet_cert_size = 0;
                            l_wallet_cert_size = (argc - 3 )
                            l_wallet_cert = DAP_NEW_Z_SIZE (dap_chain_cert_t*, l_wallet_cert_size );
                        }else {
                            log_it(L_ERROR,"Wrong 'wallet create_from' command params");
                            s_help();
                            exit(-2002);
                        }

                        if ( l_wallet_cert ){
                            if (l_wallet_cert_size > 0)
                                for (size_t i = 0; i < l_wallet_cert_size; i++)
                                    dap_chain_cert_delete( l_wallet_cert[i]->);
                        }

                    }*/
  } // wallet
  else if (strcmp (argv[1],"cert") == 0 ) {
    if ( argc >=3 ) {
      if ( strcmp( argv[2],"dump") == 0 ){
        if (argc>=4) {
          const char * l_cert_name = argv[3];
          dap_chain_cert_t * l_cert = dap_chain_cert_add_file(l_cert_name,SYSTEM_CA_DIR);
          if ( l_cert ) {
            dap_chain_cert_dump(l_cert);
            dap_chain_cert_delete_by_name(l_cert_name);
            ret = 0;
          }
          else {
            exit(-702);
          }
        }
     } else if ( strcmp( argv[2],"create_pkey") == 0 ){
       if (argc < 5) exit(-7023);
         const char *l_cert_name = argv[3];
         const char *l_cert_pkey_path = argv[4];
         dap_chain_cert_t *l_cert = dap_chain_cert_add_file(l_cert_name,SYSTEM_CA_DIR);
         if ( !l_cert ) exit( -7021 );
           l_cert->enc_key->pub_key_data_size = dap_enc_gen_key_public_size(l_cert->enc_key);
           if ( l_cert->enc_key->pub_key_data_size ) {
             //l_cert->key_private->pub_key_data = DAP_NEW_SIZE(void, l_cert->key_private->pub_key_data_size);
             //if ( dap_enc_gen_key_public(l_cert->key_private, l_cert->key_private->pub_key_data) == 0){
             dap_chain_pkey_t * l_pkey = dap_chain_pkey_from_enc_key( l_cert->enc_key );
             if (l_pkey) {
               FILE *l_file = fopen(l_cert_pkey_path,"wb");
               if (l_file) {
                 fwrite(l_pkey,1,l_pkey->header.size + sizeof(l_pkey->header),l_file);
                 fclose(l_file);
               }
             } else {
               log_it(L_ERROR, "Can't produce pkey from the certificate");
               exit(-7022);
             }
             dap_chain_cert_delete_by_name(l_cert_name);
             ret = 0;
             //}else{
             //    log_it(L_ERROR,"Can't produce public key with this key type");
             //    exit(-7024);
             //}
           } else {
             log_it(L_ERROR,"Can't produce pkey from this cert type");
             exit(-7023);
           }
     } else if ( strcmp( argv[2],"create_cert_pkey") == 0 ) {
       if ( argc >= 5 ) {
         const char *l_cert_name = argv[3];
         const char *l_cert_new_name = argv[4];
         dap_chain_cert_t *l_cert = dap_chain_cert_add_file(l_cert_name,SYSTEM_CA_DIR);
         if ( l_cert ) {
           if ( l_cert->enc_key->pub_key_data_size ) {
             // Create empty new cert
             dap_chain_cert_t * l_cert_new = dap_chain_cert_new(l_cert_new_name);
             l_cert_new->enc_key = dap_enc_key_new( l_cert->enc_key->type);

             // Copy only public key
             l_cert_new->enc_key->pub_key_data = DAP_NEW_Z_SIZE(uint8_t,
                                                                l_cert_new->enc_key->pub_key_data_size =
                                                                l_cert->enc_key->pub_key_data_size );
             memcpy(l_cert_new->enc_key->pub_key_data, l_cert->enc_key->pub_key_data,l_cert->enc_key->pub_key_data_size);

             dap_chain_cert_save_to_folder(l_cert_new, SYSTEM_CA_DIR);
             //dap_chain_cert_delete_by_name(l_cert_name);
             //dap_chain_cert_delete_by_name(l_cert_new_name);
           } else {
             log_it(L_ERROR,"Can't produce pkey from this cert type");
             exit(-7023);
           }
         } else {
           exit(-7021);
         }
       }
     }
     else if ( strcmp( argv[2],"create" ) == 0 ) {
       if ( argc < 5 ) {
         s_help();
         exit(-500);
       }
       size_t l_key_length = 0;
       const char *l_cert_name = argv[3];
       size_t l_cert_path_length = strlen(argv[3])+8+strlen(SYSTEM_CA_DIR);
       char *l_cert_path = DAP_NEW_Z_SIZE(char,l_cert_path_length);
       snprintf(l_cert_path,l_cert_path_length,"%s/%s.dcert",SYSTEM_CA_DIR,l_cert_name);
       if ( access( l_cert_path, F_OK ) != -1 ) {
         log_it (L_ERROR, "File %s is already exists! Who knows, may be its smth important?", l_cert_path);
         exit(-700);
       }

       dap_enc_key_type_t l_key_type = DAP_ENC_KEY_TYPE_NULL;

       if ( strcmp (argv[4],"sig_bliss") == 0 ){
         l_key_type = DAP_ENC_KEY_TYPE_SIG_BLISS;
       } else if ( strcmp (argv[4],"sig_tesla") == 0) {
         l_key_type = DAP_ENC_KEY_TYPE_SIG_TESLA;
       } else if ( strcmp (argv[4],"sig_picnic") == 0){
         l_key_type = DAP_ENC_KEY_TYPE_SIG_PICNIC;
       } else {
         log_it (L_ERROR, "Wrong key create action \"%s\"",argv[4]);
         exit(-600);
       }

       if ( l_key_type != DAP_ENC_KEY_TYPE_NULL ) {
         int l_key_length = argc >=6 ? atoi(argv[5]) : 0;
         dap_chain_cert_t * l_cert = dap_chain_cert_generate(l_cert_name,l_cert_path,l_key_type ); // key length ignored!
         if (l_cert == NULL){
           log_it(L_ERROR, "Can't create %s",l_cert_path);
         }
       } else {
           s_help();
           DAP_DELETE(l_cert_path);
           exit(-500);
       }
       DAP_DELETE(l_cert_path);

     } else {
       log_it(L_ERROR,"Wrong params");
       s_help();
       exit(-1000);
     }
   } else {
     log_it(L_ERROR,"Wrong params");
     s_help();
     exit(-1000);
   }
 }else {
   log_it(L_ERROR,"Wrong params");
   s_help();
   exit(-1000);
 }

}

/**
 * @brief s_init
 * @param argc
 * @param argv
 * @return
 */
static int s_init( int argc, const char **argv )
{
  if ( dap_common_init( DAP_APP_NAME, DAP_APP_NAME"_logs.txt") != 0 ) {
    printf( "Fatal Error: Can't init common functions module" );
    return -2;
  }

  dap_config_init( SYSTEM_CONFIGS_DIR );

  if ( (g_config = dap_config_open(DAP_APP_NAME)) == NULL ) {
    log_it( L_ERROR, "Can't init general configurations" );
    return -1;
  }

  //    if(dap_common_init(DAP_APP_NAME"_logs.txt")!=0){
  //        log_it(L_ERROR,"Can't init common functions module");
  //        return -2;
  //    }

  if ( dap_chain_init() != 0 ) {
    log_it( L_ERROR, "Can't chain module" );
    return -3;
  }

  if ( dap_chain_cert_init() != 0 ) {
    log_it( L_ERROR, "Can't chain certificate storage module" );
    return -4;
  }

  if ( dap_chain_wallet_init() != 0 ) {
    log_it( L_ERROR, "Can't chain wallet storage module" );
    return -5;
  }

  if ( dap_server_init(0) != 0 ) {
    log_it( L_ERROR, "Can't server module" );
    return -6;
  }

  if ( dap_stream_init(false) != 0 ) {
    log_it( L_ERROR, "Can't init stream module" );
    return -7;
  }

  if ( dap_stream_ch_init() != 0 ) {
    log_it( L_ERROR, "Can't init stream ch module" );
    return -8;
  }

  if ( dap_stream_ch_chain_init() != 0 ) {
    log_it( L_ERROR, "Can't init stream ch chain module" );
    return -9;
  }

  if ( dap_stream_ch_chain_net_init() != 0 ) {
    log_it( L_ERROR, "Can't init stream ch chain net module" );
    return -10;
  }

  if ( dap_stream_ch_chain_net_srv_init() != 0 ) {
    log_it( L_ERROR, "Can't init stream ch chain net srv module" );
    return -11;
  }

  if ( dap_client_init() != 0 ) {
    log_it( L_ERROR, "Can't chain wallet storage module" );
    return -12;
  }

  return 0;
}

/**
 * @brief s_help
 * @param a_appname
 */
static void s_help()
{
#ifdef _WIN32
  SetConsoleTextAttribute( GetStdHandle(STD_OUTPUT_HANDLE), 7 );
#endif

  printf( "\n" );
  printf( "%s usage:\n\n", s_appname );

  printf(" * Create new key wallet and generate signatures with same names plus index \n" );
  printf("\t%s wallet create <network name> <wallet name> <signature type> [<signature type 2>[...<signature type N>]]\n\n", s_appname );

  printf(" * Create new key wallet from existent certificates in the system\n");
  printf("\t%s wallet create_from <network name> <wallet name> <wallet ca1> [<wallet ca2> [...<wallet caN>]]\n\n", s_appname );

  printf(" * Create new key file with randomly produced key stored in\n");
  printf("\t%s cert create <cert name> <key type> [<key length>]\n\n", s_appname );

  printf(" * Dump cert data stored in <file path>\n");
  printf("\t%s cert dump <cert name>\n\n", s_appname );

  printf(" * Sign some data with cert \n");
  printf("\t%s cert sign <cert name> <data file path> <sign file output> [<sign data length>] [<sign data offset>]\n\n", s_appname );

  printf(" * Create pkey from <cert name> and store it on <pkey path>\n");
  printf("\t%s cert create_pkey <cert name> <pkey path>\n\n", s_appname );

  printf(" * Export only public key from <cert name> and stores it \n");
  printf("\t%s cert create_cert_pkey <cert name> <new cert name>\n\n",s_appname);

}
