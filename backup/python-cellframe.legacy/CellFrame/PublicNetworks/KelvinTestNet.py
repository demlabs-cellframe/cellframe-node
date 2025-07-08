import os
from string import Template

# @brief getJsonString()
# In dist_dir should be root ceritificates, 
# var_dir used for created files during the work 
# where poa or pos certs are also should be found if 'master' or 'root' role
def getJsonString(var_dir, dist_dir, node_role="full", poa_sign_cert=None,pos_sign_wallet=None):
    # Extension section including in the config below
    ext_section_0=""
    if pos_sign_wallet not None:
        ext_section_0+="                    \"dag-pos\":{ \"events-sign-wallet\":\""+pos_sign_wallet+"\" },\n"
    if poa_sign_cert not None:
        ext_section_0+="                    \"dag-poa\":{ \"events-sign-cert\":\""+poa_sign_cert+"\" },\n"

    ret_tpl = Template("""
                "kelvin-testnet": {
                    "general":{
                        "id": "0x0000000000000001",
                        "name": "kelvin-testnet",
                        "node-role": "{$node_role}",
                        "gdb_groups_prefix": "kelvin-testnet"
                    },
                    {$ext_section_0}
                    "name_cfg_files": ["zerochain","plasma"],
                    "conf_files":{
                        "zerochain": {
                            "general": {
                                "id": "0xf000000000000000",
                                "name": "zerochain",
                                "load_priority":1,
                                "datum_types":["token,token_update,emission,shard,ca"],
                                "consensus": "dag-poa",
                                "datum_types": ["ca", "transaction"]
                            },
                            "dag":{
                                "is_single_line": true,
                                "is_celled": false,
                                "is_add_directly": true,
                                "datum_and_hash_count": 1
                            },
                            "dag-poa":{
                                "auth_certs_prefix": "kelvin.testnet.root",
                                "auth_certs_number": 5,
                                "auth_certs_number_verify":1,
                                "auth_certs_dir": "${dist_dir}/ca"
                            }
                            "files":{
                                "storage_dir":"{$var_dir}/lib/network/kelvin-testnet/zerochain"
                            }
                        }
                        "plasma": {
                            "general": {
                                "id": "0xf000000000000001",
                                "name": "plasma",
                                "load_priority":2,
                                "datum_types":["transaction,ca,custom"],
                                "consensus": "dag-pos",
                                "datum_types": ["ca", "transaction"]
                            },
                            "dag":{
                                "is_single_line": false,
                                "is_celled": true,
                                "is_add_directly": true,
                                "datum_and_hash_count": 3
                            },
                            "dag-pos":{
                                "tokens_hold": ["KELT","KEL"],
                                "tokens_hold_value": [1000000000,1000000000],
                                "confirmations_minumum": 1,
                            }
                            "files":{
                                "storage_dir":"{$var_dir}/lib/network/kelvin-testnet/pasma"
                            }
                        }
                    }
                }""")

    tpl_vars={
        "var_dir":var_dir,
        "dist_dir":dist_dir,
        "node_role":node_role,
        "ext_section_0": ext_sec_0
    }
    return ret_tpl.substitute(tpl_vars)
