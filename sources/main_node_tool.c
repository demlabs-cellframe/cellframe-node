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

#define LOG_TAG "main_node_tool"

#undef log_it
#ifdef DAP_OS_WINDOWS
#include "registry.h"
#define log_it(_log_level, string, ...) __mingw_printf(string, ##__VA_ARGS__)
#else
#define log_it(_log_level, string, ...) printf(string, ##__VA_ARGS__)
#endif

static int s_init();
static void s_help( );
static int s_is_file_available (char *l_path, const char *name, const char *ext);
static void s_fill_hash_key_for_data(dap_enc_key_t *key, void *data);

static char s_system_ca_dir[MAX_PATH];
static char s_system_wallet_dir[MAX_PATH];

static int s_wallet_create(int argc, const char **argv);
static int s_wallet_create_from(int argc, const char **argv);
static int s_wallet_create_wp(int argc, const char **argv);
static int s_wallet_sign_file(int argc, const char **argv);
static int s_cert_create(int argc, const char **argv);
static int s_cert_dump(int argc, const char **argv);
static int s_cert_copy(int argc, const char **argv, bool a_pvt_key_copy);
static int s_cert_create_pkey(int argc, const char **argv);
static inline int s_cert_create_cert_pkey(int argc, const char **argv){
    int res = s_cert_copy(argc, argv, false);
    if (res == 0) {
        log_it(L_NOTICE, "A certificate with a public key has been created.\n");
    } else {
        log_it(L_ERROR, "\nFailed to create a certificate with a public key. Error code: %d.", res);
    }
    return res;
}
static inline int s_cert_rename(int argc, const char **argv) {
    int res = s_cert_copy(argc, argv, true);
    if (res == 0) {
        log_it(L_NOTICE, "Certificate renaming has been completed.\n");
    } else {
        log_it(L_ERROR, "\nFailed to rename the certificate.");
    }
    return res;
}
static int s_cert_add_metadata(int argc, const char **argv);
static int s_cert_sign(int argc, const char **argv);
static int s_cert_pkey_show(int argc, const char **argv);
static int s_cert_get_addr(int argc, const char **argv);

struct options {
    char *cmd;
    char *subcmd[5];
    int count_of_subcommands;
    int (*handler) (int argc, const char **argv);
} s_opts[] = {
{ "wallet", {"create"}, 1, s_wallet_create },
{ "wallet", {"create_from"}, 1, s_wallet_create_from },
{"wallet", {"create_wp"}, 1, s_wallet_create_wp},
//{ "wallet", {"sign_file"}, 1, s_wallet_sign_file },
{ "cert", {"create"}, 1, s_cert_create },
{ "cert", {"dump"}, 1, s_cert_dump },
{ "cert", {"create_pkey"}, 1, s_cert_create_pkey },
{ "cert", {"create_cert_pkey"}, 1, s_cert_create_cert_pkey },
{ "cert", {"rename"}, 1, s_cert_rename },
{ "cert", {"add_metadata"}, 1, s_cert_add_metadata },
{ "cert", {"sign"}, 1, s_cert_sign },
{ "cert", {"pkey", "show"}, 2, s_cert_pkey_show },
{"cert", {"addr", "show"}, 2, s_cert_get_addr }
};

#ifdef __ANDROID__
int cellframe_node_tool_Main(int argc, const char **argv)
#else
int main(int argc, const char **argv)
#endif
{
  dap_set_appname("cellframe-node");

    // get relative path to config
    int l_rel_path = 0;
    if (argv[1] && argv[2] && !dap_strcmp("-B" , argv[1])) {
        g_sys_dir_path = (char*)argv[2];
        l_rel_path = 1;
    }

    if (!g_sys_dir_path) {
    #ifdef DAP_OS_WINDOWS
        g_sys_dir_path = dap_strdup_printf("%s/%s", regGetUsrPath(), dap_get_appname());
    #elif DAP_OS_MAC
        g_sys_dir_path = dap_strdup_printf("/Applications/CellframeNode.app/Contents/Resources");
    #elif DAP_OS_ANDROID
        g_sys_dir_path = dap_strdup_printf("/storage/emulated/0/opt/%s",dap_get_appname());
    #elif DAP_OS_UNIX
        g_sys_dir_path = dap_strdup_printf("/opt/%s", dap_get_appname());
    #endif
    }

  int ret = s_init();

  if ( ret ) {
    log_it( L_ERROR, "Can't init modules" );
    return ret;
  }

  if ( argc < 2 ) {
    log_it( L_INFO, "No params. Nothing to do" );
    s_help( );
    exit( -1000 );
  }

  size_t l_size = sizeof(s_opts) / sizeof(struct options);
  bool l_find_cmd = false;
  bool l_find_subcmd = true;
  for (size_t i = 0; i < l_size; i++) {
      int argv_index = 1 + l_rel_path*2;
      if (argc >= argv_index && !strncmp(s_opts[i].cmd, argv[argv_index], strlen (argv[argv_index]) + 1)) {
          l_find_cmd = true;
          l_find_subcmd = false;
          int match = 1;
          for (int isub = 0; isub < s_opts[i].count_of_subcommands; isub++) {
              if ((argc - 1) < ++argv_index) {
                  match = 0;
                  break;
              }
              if (strncmp(s_opts[i].subcmd[isub], argv[argv_index], strlen(argv[argv_index]) + 1)) {
                  match = 0;
                  break;
              }
          }
          if (match) {
              int l_ret = s_opts[i].handler(l_rel_path ? argc-2 : argc, l_rel_path ? argv+2 : argv);
              return l_ret;
          }
      }
  }
  if (!l_find_cmd) {
      printf("Command %s not found.\n", argv[1]);
  }
  if (!l_find_subcmd) {
      printf("No subcommand was found for the %s command or the number of command arguments is less than the minimum.\n",
             argv[1]);
  }

  s_help();
  dap_config_close(g_config);
  return -1;
}

static int s_wallet_create(int argc, const char **argv) {
    if ( argc < 5 ) {
      log_it( L_ERROR, "Wrong 'wallet create' command params" );
      s_help( );
      exit( -2003 );
    }
      const char *l_wallet_name = argv[3];
    dap_sign_type_t l_sig_type = dap_sign_type_from_str( argv[4] );
    dap_chain_wallet_t *l_wallet = NULL;

    //
    // Check if wallet name has only digits and English letters
    //

    size_t is_str = dap_isstralnum(l_wallet_name);

    if (!is_str)
    {
        log_it( L_ERROR, "Wallet name must contain digits and alphabet symbols");
        exit( -2004 );
    }

    if ( l_sig_type.type == SIG_TYPE_NULL ) {
      log_it( L_ERROR, "Invalid signature type '%s', you can use the following:\n%s",
              argv[4], dap_sign_get_str_recommended_types());
      s_help( );
      exit( -2004 );
    }

    //
    // Check unsupported tesla algorithm
    //
    if (dap_sign_type_is_depricated(l_sig_type))
    {
        log_it( L_ERROR, "Tesla, picnic, bliss algorithms is not supported, please, use another variant:\n%s",
                dap_sign_get_str_recommended_types());
        exit( -2004 );
    }

    char *l_file_name = dap_strdup_printf("%s/%s.dwallet", dap_chain_wallet_get_path(g_config), l_wallet_name);
    if (dap_file_test(l_file_name)) {
        log_it(L_ERROR, "The '%s' wallet already exists.\n", l_wallet_name);
        exit(-2007);
    }
    DAP_DELETE(l_file_name);

    if (l_sig_type.type == SIG_TYPE_MULTI_CHAINED){
        if (argc < 7) {
            log_it(L_ERROR, "For a signature with type sig_multi_chained, two more signature type parameters must be set.");
            exit(-2006);
        }
        dap_sign_type_t l_types[MAX_ENC_KEYS_IN_MULTYSIGN] = {0};
        size_t l_count_signs  = 0;
        for (int i = 5; i < argc; i++) {
            l_types[l_count_signs] = dap_sign_type_from_str(argv[i]);
            if (l_types[l_count_signs].type == SIG_TYPE_NULL) {
                log_it( L_ERROR, "Invalid signature type '%s', you can use the following:\n%s",
                        argv[i], dap_sign_get_str_recommended_types());
                exit(-2007);
            }
            if (dap_sign_type_is_depricated(l_types[l_count_signs]))
            {
                log_it( L_ERROR, "Tesla, picnic, bliss algorithms is not supported, please, use another variant:\n%s",
                        dap_sign_get_str_recommended_types());
                exit( -2008 );
            }
            l_count_signs++;
        }
        l_wallet = dap_chain_wallet_create_with_seed_multi(l_wallet_name, s_system_wallet_dir,
                                                               l_types, l_count_signs,
                                                               NULL, 0, NULL);
    } else
        l_wallet = dap_chain_wallet_create(l_wallet_name, s_system_wallet_dir, l_sig_type, NULL);

    if (l_wallet) {
        log_it(L_NOTICE, "Wallet %s has been created.\n", l_wallet_name);
        return 0;
    } else {
        log_it(L_ERROR, "Failed to create a wallet.");
        return -1;
    }
}

static int s_wallet_create_wp(int argc, const char **argv) {
    if ( argc < 5 ) {
      log_it( L_ERROR, "Wrong 'wallet create' command params" );
      s_help( );
      exit( -2003 );
    }

    const char *l_wallet_name = argv[3], *l_pass_str = argv[4];
    dap_sign_type_t l_sig_type = dap_sign_type_from_str( argv[5] );
    dap_chain_wallet_t *l_wallet = NULL;

    //
    // Check if wallet name has only digits and English letters
    //

    size_t is_str = dap_isstralnum(l_wallet_name);

    if (!is_str)
    {
        log_it( L_ERROR, "Wallet name must contain digits and alphabet symbols");
        exit( -2004 );
    }

    if ( l_sig_type.type == SIG_TYPE_NULL ) {
      log_it( L_ERROR, "Invalid signature type '%s', you can use the following:\n%s",
              argv[4], dap_sign_get_str_recommended_types());
      s_help( );
      exit( -2004 );
    }

    //
    // Check unsupported tesla algorithm
    //
    if (dap_sign_type_is_depricated(l_sig_type))
    {
        log_it( L_ERROR, "Tesla, picnic, bliss algorithms is not supported, please, use another variant:\n%s",
                dap_sign_get_str_recommended_types());
        exit( -2004 );
    }

    char *l_file_name = dap_strdup_printf("%s/%s.dwallet", dap_chain_wallet_get_path(g_config), l_wallet_name);
    if (dap_file_test(l_file_name)) {
        log_it(L_ERROR, "The '%s' wallet already exists.\n", l_wallet_name);
        exit(-2007);
    }
    DAP_DELETE(l_file_name);

    if (l_sig_type.type == SIG_TYPE_MULTI_CHAINED){
        if (argc < 8) {
            log_it(L_ERROR, "For a signature with type sig_multi_chained, two more signature type parameters must be set.\n");
            exit(-2006);
        }
        dap_sign_type_t l_types[MAX_ENC_KEYS_IN_MULTYSIGN] = {0};
        size_t l_count_signs  = 0;
        for (int i = 6; i < argc; i++) {
            l_types[l_count_signs] = dap_sign_type_from_str(argv[i]);
            if (l_types[l_count_signs].type == SIG_TYPE_NULL) {
                log_it( L_ERROR, "Invalid signature type '%s', you can use the following:\n%s",
                        argv[i], dap_sign_get_str_recommended_types());
                exit(-2007);
            }
            if (dap_sign_type_is_depricated(l_types[l_count_signs]))
            {
                log_it( L_ERROR, "Tesla, picnic, bliss algorithms is not supported, please, use another variant:\n%s",
                        dap_sign_get_str_recommended_types());
                exit( -2008 );
            }
            l_count_signs++;
        }
        l_wallet = dap_chain_wallet_create_with_seed_multi(l_wallet_name, s_system_wallet_dir,
                                                               l_types, l_count_signs,
                                                               NULL, 0, l_pass_str);
    } else
        l_wallet = dap_chain_wallet_create(l_wallet_name, s_system_wallet_dir, l_sig_type, l_pass_str);

    if (l_wallet) {
        log_it(L_NOTICE, "Wallet %s has been created.\n", l_wallet_name);
        return 0;
    } else {
        log_it(L_ERROR, "Failed to create a wallet.");
        return -1;
    }
}

static int s_wallet_create_from(int argc, const char **argv) {
    printf("The wallet create_from command is not implemented.");
    return -1;
}

static int s_wallet_sign_file(int argc, const char **argv) {
    if ( argc < 8 ) {
      log_it(L_ERROR,"Wrong 'wallet sign_file' command params");
      s_help();
      exit(-3000);
    }
    dap_chain_wallet_t *l_wallet = dap_chain_wallet_open(argv[3], s_system_wallet_dir, NULL);
    if ( !l_wallet ) {
      log_it(L_ERROR,"Can't open wallet \"%s\"",argv[3]);
      s_help();
      exit(-3001);
    }

    int l_cert_index = atoi(argv[4]);

    size_t l_wallet_certs_number = dap_chain_wallet_get_certs_number( l_wallet );
    if ( (l_cert_index > 0) && (l_wallet_certs_number > (size_t)l_cert_index) ) {
      FILE *l_data_file = fopen( argv[5],"rb" );
      if ( l_data_file ) {
        fclose(l_data_file);
        log_it(L_NOTICE, "Certificate %s was successfully created from wallet %s.\n", argv[5], argv[3]);
        exit(0);
      }
    } else {
      log_it( L_ERROR, "Cert index %d can't be found in wallet with %zu certs inside"
                                         ,l_cert_index,l_wallet_certs_number );
      s_help();
      exit( -3002 );
    }
    return 0;
}

static int s_cert_create(int argc, const char **argv) {
    if ( argc < 5 ) {
      log_it( L_ERROR, "Wrong 'cert create' command params\n");
      s_help();
      exit(-500);
    }
    const char *l_cert_name = argv[3];
    size_t l_cert_path_length = strlen(argv[3])+8+strlen(s_system_ca_dir);
    char *l_cert_path = DAP_NEW_Z_SIZE(char,l_cert_path_length);
    snprintf(l_cert_path,l_cert_path_length,"%s/%s.dcert",s_system_ca_dir,l_cert_name);
    if ( access( l_cert_path, F_OK ) != -1 ) {
      log_it (L_ERROR, "File \"%s\" already exists!\n", l_cert_path);
      exit(-700);
    }

    dap_sign_type_t l_sig_type = dap_sign_type_from_str( argv[4] );

    if (l_sig_type.type == SIG_TYPE_NULL || l_sig_type.type == SIG_TYPE_MULTI_CHAINED) {
        log_it(L_ERROR, "Unknown signature type %s specified, recommended signatures:\n%s",
               argv[4], dap_cert_get_str_recommended_sign());
        exit(-600);
    } else if (l_sig_type.type == SIG_TYPE_MULTI_CHAINED) {
        log_it(L_ERROR, "The sig_multi_chained signature is not applicable for certificate creation. "
                              "Use the following signatures:\\n%s", dap_cert_get_str_recommended_sign());
        exit(-601);
    }


    //
    // Check unsupported algorithm
    //
    if (dap_sign_type_is_depricated(l_sig_type)) {
        log_it(L_ERROR, "Signature type %s is obsolete, we recommend the following signatures:\n%s",
               argv[4], dap_cert_get_str_recommended_sign());
        exit(-602);
    }

    dap_enc_key_type_t l_key_type = dap_sign_type_to_key_type(l_sig_type);

    if ( l_key_type != DAP_ENC_KEY_TYPE_INVALID ) {
      dap_cert_t * l_cert = dap_cert_generate(l_cert_name,l_cert_path,l_key_type ); // key length ignored!
      if (l_cert == NULL){
        log_it(L_ERROR, "Can't create \"%s\"",l_cert_path);
      }
      dap_cert_delete(l_cert);
    } else {
        log_it (L_ERROR, "Wrong key create action \"%s\"",argv[4]);
        s_help();
        DAP_DELETE(l_cert_path);
        exit(-500);
    }
    log_it(L_NOTICE, "Cert \"%s\" created\n", l_cert_path);
    DAP_DELETE(l_cert_path);
    return 0;
}

static int s_cert_dump(int argc, const char **argv)
{
    if (argc>=4) {
      const char * l_cert_name = argv[3];
      dap_cert_t * l_cert = dap_cert_add_file(l_cert_name, s_system_ca_dir);
      if ( l_cert ) {
        char *l_cert_dump = dap_cert_dump(l_cert);
        printf("%s", l_cert_dump);
        dap_cert_delete_by_name(l_cert_name);
      }
      else {
        log_it( L_ERROR, "Can't open '%s' cert\n", l_cert_name);
        exit(-702);
      }
    } else {
        log_it( L_ERROR, "Wrong 'cert dump' command params\n");
    }
    return 0;
}

static int s_cert_create_pkey(int argc, const char **argv) {
    if (argc < 5) {
        log_it( L_ERROR, "Wrong 'cert create_pkey' command params\n");
        exit(-7023);
    }
      const char *l_cert_name = argv[3];
      const char *l_cert_pkey_path = argv[4];
      dap_cert_t *l_cert = dap_cert_add_file(l_cert_name, s_system_ca_dir);
      if ( !l_cert ) {
          log_it(L_ERROR, "Failed to open \"%s\" certificate.", l_cert_name);
          exit(-7021);
      }
        l_cert->enc_key->pub_key_data_size = dap_enc_ser_pub_key_size(l_cert->enc_key);
        if ( l_cert->enc_key->pub_key_data_size ) {
          //l_cert->key_private->pub_key_data = DAP_NEW_SIZE(void, l_cert->key_private->pub_key_data_size);
          //if ( dap_enc_gen_key_public(l_cert->key_private, l_cert->key_private->pub_key_data) == 0){
          dap_pkey_t * l_pkey = dap_pkey_from_enc_key( l_cert->enc_key );
          if (l_pkey) {
            if (dap_file_test(l_cert_pkey_path)){
                log_it(L_ERROR, "The file \"%s\" exists.\n", l_cert_pkey_path);
                exit(-7023);
            }
            FILE *l_file = fopen(l_cert_pkey_path,"wb");
            if (l_file) {
              fwrite(l_pkey,1,l_pkey->header.size + sizeof(l_pkey->header),l_file);
              fclose(l_file);
            }
          } else {
            log_it(L_ERROR, "Can't produce pkey from the certificate\n");
            exit(-7022);
          }
          dap_cert_delete_by_name(l_cert_name);
          log_it(L_NOTICE, "Created \"%s\" public key based on \"%s\" private key.\n", l_cert_pkey_path, l_cert_name);
          return 0;
        } else {
          log_it(L_ERROR,"Can't produce pkey from this cert type\n");
          exit(-7023);
        }
}

static int s_cert_copy(int argc, const char **argv, bool a_pvt_key_copy)
{
    if (argc < 5) {
        log_it(L_ERROR, "Incorrect arguments count");
        exit(-7021);
    }
    const char *l_cert_name = argv[3];
    const char *l_cert_new_name = argv[4];
    dap_cert_t *l_cert = dap_cert_add_file(l_cert_name, s_system_ca_dir);
    if (!l_cert) {
        log_it(L_ERROR, "Can't read specified certificate");
        exit(-7023);
    }
    if (!l_cert->enc_key->pub_key_data || !l_cert->enc_key->pub_key_data_size) {
        log_it(L_ERROR, "Invalid certificate key, no public key found");
        exit(-7022);
    }
    char *l_cert_new_path = dap_strdup_printf("%s/%s.dcert", s_system_ca_dir, l_cert_new_name);
    if (dap_file_test(l_cert_new_path)) {
        log_it(L_ERROR, "The \"%s\" file already exists.\n", l_cert_new_path);
        exit(-7023);
    }
    DAP_DELETE(l_cert_new_path);
    // Create empty new cert
    dap_cert_t *l_cert_new = dap_cert_new(l_cert_new_name);
    l_cert_new->enc_key = dap_enc_key_new(l_cert->enc_key->type);
    // Copy public key (copy only memory address of key storage)
    l_cert_new->enc_key->pub_key_data = DAP_DUP_SIZE(l_cert->enc_key->pub_key_data,
                                                     l_cert->enc_key->pub_key_data_size);
    if (!l_cert_new->enc_key->pub_key_data) {
        log_it(L_CRITICAL, "%s", c_error_memory_alloc);
        return -1;
    }
    l_cert_new->enc_key->pub_key_data_size = l_cert->enc_key->pub_key_data_size;
    // Copy private key for rename (copy only memory address of key storage)
    if (l_cert->enc_key->priv_key_data && l_cert->enc_key->priv_key_data_size && a_pvt_key_copy) {
        l_cert_new->enc_key->priv_key_data = DAP_DUP_SIZE(l_cert->enc_key->priv_key_data,
                                                          l_cert->enc_key->priv_key_data_size);
        if (!l_cert_new->enc_key->priv_key_data) {
            log_it(L_CRITICAL, "%s", c_error_memory_alloc);
            return -1;
        }
        l_cert_new->enc_key->priv_key_data_size = l_cert->enc_key->priv_key_data_size;
    }
    int ret = dap_cert_save_to_folder(l_cert_new, s_system_ca_dir);
    if (!ret && a_pvt_key_copy) // Remove original cert after renaming
        ret = dap_cert_delete_file(l_cert_name, s_system_ca_dir);
    dap_cert_delete(l_cert);    // Do not remove it before disk saving op
    DAP_DEL_Z(l_cert_new->enc_key->pub_key_data);
    DAP_DEL_Z(l_cert_new->enc_key->priv_key_data);
    dap_cert_delete(l_cert_new); 
    return ret;
}

static int s_cert_add_metadata(int argc, const char **argv) {
    if (argc >= 5) {
        const char *l_cert_name = argv[3];
        dap_cert_t *l_cert = dap_cert_add_file(l_cert_name, s_system_ca_dir);
        if ( l_cert ) {
            char **l_params = dap_strsplit(argv[4], ":", 4);
            dap_cert_metadata_type_t l_type = (dap_cert_metadata_type_t)atoi(l_params[1]);
            if (l_type == DAP_CERT_META_STRING || l_type == DAP_CERT_META_SIGN || l_type == DAP_CERT_META_CUSTOM) {
                dap_cert_add_meta(l_cert, l_params[0], l_type, (void *)l_params[3], strtoul(l_params[2], NULL, 10));
            } else {
                dap_cert_add_meta_scalar(l_cert, l_params[0], l_type,
                                   strtoull(l_params[3], NULL, 10), strtoul(l_params[2], NULL, 10));
            }
            dap_strfreev(l_params);
            dap_cert_save_to_folder(l_cert, s_system_ca_dir);
            dap_cert_delete_by_name(l_cert_name);
            log_it(L_NOTICE, "The metainformation was successfully added to %s certificate\n", l_cert_name);
            return 0;
        }
        else {
            log_it(L_ERROR, "Can't open %s certificate", l_cert_name);
            exit(-800);
        }
    } else {
        log_it( L_ERROR, "Wrong 'cert add_metadata' command params\n");
        exit(-800);
    }
}
static int s_cert_sign(int argc, const char **argv) {
    log_it(L_ERROR, "The command 'cert sign' is not implemented.");
    return -1;
}
static int s_cert_pkey_show(int argc, const char **argv)
{
    if (argc != 5) {
        log_it( L_ERROR, "Wrong 'cert pkey show' command params\n");
        exit(-800);
    }
    dap_cert_t *l_cert = dap_cert_find_by_name(argv[4]);
    if (!l_cert) {
        printf("Not found cert %s\n", argv[4]);
        exit(-134);
    }

    dap_hash_fast_t l_hash;
    if (dap_cert_get_pkey_hash(l_cert, &l_hash)) {
        printf("Can't serialize cert %s", argv[4]);
        exit(-135);
    }
    printf("%s\n", dap_chain_hash_fast_to_str_static(&l_hash));
    return 0;
}

static int s_cert_get_addr(int argc, const char **argv) {
    if (argc != 5) {
        log_it( L_ERROR, "Wrong 'cert pkey show' command params\n");
        exit(-900);
    }
    dap_cert_t *l_cert = dap_cert_find_by_name(argv[4]);
    if (!l_cert) {
        printf("Not found cert %s\n", argv[4]);
        exit(-134);
    }
    dap_stream_node_addr_t l_addr = dap_stream_node_addr_from_cert(l_cert);
    printf("%s\n", dap_stream_node_addr_to_str_static(l_addr));
    return 0;
}

/**
 * @brief s_init
 * @param argc
 * @param argv
 * @return
 */
static int s_init()
{
    if (dap_common_init(dap_get_appname(), NULL, NULL) != 0)
        return printf("Fatal Error: Can't init common functions module"), -2;
#if defined (DAP_DEBUG) || !defined(DAP_OS_WINDOWS)
        dap_log_set_external_output(LOGGER_OUTPUT_STDOUT, NULL);
#else
        dap_log_set_external_output(LOGGER_OUTPUT_NONE, NULL);
#endif
    dap_log_level_set(L_ERROR);
    char l_config_dir[MAX_PATH] = {'\0'};
    sprintf(l_config_dir, "%s/etc", g_sys_dir_path);
    dap_config_init(l_config_dir);
    g_config = dap_config_open(dap_get_appname());
    if (g_config) {
        uint16_t l_ca_folders_size = 0;
        char **l_ca_folders = dap_config_get_item_str_path_array(g_config, "resources", "ca_folders", &l_ca_folders_size);
        dap_stpcpy(s_system_ca_dir, l_ca_folders[0]);
        dap_config_get_item_str_path_array_free(l_ca_folders, &l_ca_folders_size);
        int t = dap_strlen(s_system_ca_dir);
        if (s_system_ca_dir[t - 1] == '/')
            s_system_ca_dir[t-1] = '\0';
        char *l_wallet_folder = dap_config_get_item_str_path_default(g_config, "resources", "wallets_path", NULL);
        dap_stpcpy(s_system_wallet_dir, l_wallet_folder);
        DAP_DEL_Z(l_wallet_folder);
    } else {
        dap_stpcpy(s_system_ca_dir, "./");
        dap_stpcpy(s_system_wallet_dir, "./");
    }
    return 0;
}

/**
 * @brief static_is_file_available
 * @param l_path
 * @param name
 * @return
 */
static int s_is_file_available (char *l_path, const char *name, const char *ext)
{
    char l_buf_path[255];
    snprintf (l_buf_path, 255, "%s/%s%s", l_path, name, ext ? ext : 0);
    if (access (l_buf_path, F_OK)) return -1;
    return 0;
}

/**
 * @brief s_fill_hash_key_for_data
 * @param key
 * @param data
 */
static void s_fill_hash_key_for_data(dap_enc_key_t *l_key, void *l_data)
{
    size_t l_sign_unserialized_size = dap_sign_create_output_unserialized_calc_size(l_key, sizeof(dap_hash_fast_t));
    if(l_sign_unserialized_size > 0) {
        size_t l_pub_key_size = 0;
        uint8_t *l_pub_key = dap_enc_key_serialize_pub_key(l_key, &l_pub_key_size);
        if (!l_pub_key)
            return;
        uint8_t* l_sign_unserialized = DAP_NEW_Z_SIZE(uint8_t, l_sign_unserialized_size);
        size_t l_sign_ser_size = l_sign_unserialized_size;
        uint8_t *l_sign_ser = dap_enc_key_serialize_sign(l_key->type, l_sign_unserialized, &l_sign_ser_size);
        if ( l_sign_ser ) {
            dap_sign_t *l_ret;
            DAP_NEW_Z_SIZE_RET(l_ret, dap_sign_t, sizeof(dap_sign_hdr_t) + l_sign_ser_size + l_pub_key_size, NULL);
            // write serialized public key to dap_sign_t
            memcpy(l_ret->pkey_n_sign, l_pub_key, l_pub_key_size);
            l_ret->header.type = dap_sign_type_from_key_type(l_key->type);
            // write serialized signature to dap_sign_t
            memcpy(l_ret->pkey_n_sign + l_pub_key_size, l_sign_ser, l_sign_ser_size);
            l_ret->header.sign_pkey_size = (uint32_t) l_pub_key_size;
            l_ret->header.sign_size = (uint32_t) l_sign_ser_size;
            DAP_DELETE(l_sign_ser);
            dap_enc_key_signature_delete(l_key->type, l_sign_unserialized);
            DAP_DELETE(l_pub_key);
            dap_chain_hash_fast_t fast_hash;
            dap_hash_fast(l_ret->pkey_n_sign, l_ret->header.sign_pkey_size, &fast_hash);
            uint8_t *s = (uint8_t *) l_data;
            for (int i = 0; i < DAP_CHAIN_HASH_FAST_SIZE; i++) {
                s[i] = fast_hash.raw[i];
            }
            DAP_DEL_Z(l_ret);
        }
    }
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
    char *l_tool_appname = dap_strdup_printf("%s-tool", dap_get_appname());
    printf( "\n" );
    printf( "%s usage:\n\n", l_tool_appname);

    printf(" * Create new key wallet and generate signatures with same names plus index \n" );
    printf("\t%s wallet create <wallet name> <signature type> [<signature type 2>[...<signature type N>]]\n\n", l_tool_appname);

    printf(" * Create a new key wallet and generate signatures with the same names plus index. The wallet will be password protected. \n" );
    printf("\t%s wallet create_wp <wallet name> <password> <signature type> [<signature type 2>[...<signature type N>]]\n\n", l_tool_appname);


#if 0
    printf(" * Create new key wallet from existent certificates in the system\n");
    printf("\t%s wallet create_from <network name> <wallet name> <wallet ca1> [<wallet ca2> [...<wallet caN>]]\n\n", l_tool_appname);
#endif

    //printf(" * Sign file\n");
    //printf("\t%s wallet sign_file <wallet name> <cert index> <data file>\n\n", l_tool_appname);

    printf(" * Create new key file with randomly produced key stored in\n");
    printf("\t%s cert create <cert name> <sign type> [<key length>]\n\n", l_tool_appname);

    printf(" * Dump cert data stored in <file path>\n");
    printf("\t%s cert dump <cert name>\n\n", l_tool_appname);

    printf(" * Sign some data with cert \n");
    printf("\t%s cert sign <cert name> <data file path> <sign file output> [<sign data length>] [<sign data offset>]\n\n", l_tool_appname);

    printf(" * Create pkey from <cert name> and store it on <pkey path>\n");
    printf("\t%s cert create_pkey <cert name> <pkey path>\n\n", l_tool_appname);

    printf(" * Export only public key from <cert name> and stores it \n");
    printf("\t%s cert create_cert_pkey <cert name> <new cert name>\n\n", l_tool_appname);

    printf(" * Print hash of cert <cert name>\n");
    printf("\t%s cert pkey show <cert name>\n\n", l_tool_appname);

    printf(" * Print addr of cert <cert name>\n");
    printf("\t%s cert addr show <cert name>\n\n", l_tool_appname);

    printf(" * Add metadata item to <cert name>\n");
    printf("\t%s cert add_metadata <cert name> <key:type:length:value>\n\n", l_tool_appname);

    DAP_DELETE(l_tool_appname);
}
