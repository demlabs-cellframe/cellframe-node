import os
from string import Template

def getJsonString(app_name):
    tmp_dir = os.getcwd() + "/tmp"
    var_dir = os.getcwd() + "/var"
    if os.path.isdir(var_dir) is False and os.path.isdir(var_dir+"/log") is False:
        os.mkdir(var_dir)
        os.mkdir(var_dir+"/log")
    ret_tpl = Template("""
    {
        "modules": [
            "Crypto", "ServerCore", "Http",
            "HttpFolder","GlobalDB","Client","HttpClientSimple","Mempool",
            "Chain", "Wallet", "ChainCSDag", "ChainCSDagPoa", "ChainCSDagPos", "GDB", "Net", "AppCliServer",
            "ChainNetSrv", "EncHttp","Stream", "StreamCtl", "HttpSimple", "StreamChChain", "StreamChChainNet",
            "StreamChChainNetSrv" ],
        "Core": {
            "config_dir": "${tmp_dir}",
            "log_level": "L_DEBUG",
            "application_name": "${app_name}",
            "file_name_log": "${var_dir}/log/${app_name}.log"
        },
        "Stream" : {
            "DebugDumpStreamHeaders": false
        },
        "ServerCore" : {
            "thread_cnt": 0,
            "conn": 0
        },
        "Configuration" : {
            "general": {
                "debug_mode": false,
                "debug_dump_stream_headers": false,
                "wallets_default": "default"
            },
            "server": {
                "enabled": true,
                "listen_address": "0.0.0.0",
                "listen_port_tcp": 8079
            },
            "conserver": {
                "enabled": true,
                "listen_unix_socket_path": "${tmp_dir}/node_cli"
            },
            "resources": {
                "threads_cnt": 0,
                "pid_path": "${var_dir}/run/${app_name}.pid",
                "log_file": "${var_dir}/log/${app_name}.log",
                "wallets_path": "${var_dir}/lib/wallet",
                "ca_folders": [ "${var_dir}/lib/ca" ],
                "dap_global_db_path": "${var_dir}/lib/global_db",
                "dap_global_db_driver": "cdb"
            },
            "networks":{
                "mystock-dev": {
                    "general":{
                        "id": "0xFF00000000000003",
                        "name": "mystock-dev",
                        "node-role": "root",
                        "gdb_groups_prefix": "mystock"
                    },
                    "name_cfg_files": ["main"],
                    "conf_files":{
                        "main": {
                            "general": {
                                "id": "0xf00000000000000f",
                                "name": "main",
                                "consensus": "dag-poa",
                                "datum_types": ["ca", "transaction","token","token_update","emission","shard"]
                            },
                            "dag":{
                                "is_single_line": false,
                                "is_celled": true,
                                "is_add_directly": true,
                                "datum_and_hash_count": 3
                            },
                            "dag-poa":{
                                "auth_certs_prefix": "mystock-dev.root",
                                "auth_certs_number": 1,
                                "auth_certs_number_verify":1,
                                "auth_certs_dir": "${var_dir}/lib/ca"
                            },
                            "files":{
                                "storage_dir":"{$var_dir}/lib/network/mystock-dev/main"
                            }
                        }
                    }
                }
            }
        }
    }"""
    )
    tpl_vars={
        "var_dir":var_dir,
        "tmp_dir":tmp_dir,
        "app_name":app_name
    }
    return ret_tpl.substitute(tpl_vars)
