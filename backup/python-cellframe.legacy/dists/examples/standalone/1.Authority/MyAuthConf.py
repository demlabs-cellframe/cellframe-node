import os
from string import Template


def getNetworkName(appName, sep="-"):
    return appName.lower()+sep+"dev"


def getJsonString(app_name, log_level="DEBUG"):
    tmp_dir = os.getcwd() + "/tmp"
    var_dir = os.getcwd() + "/var"

    ret_tpl = Template("""
    {
        "modules": [
            "Crypto", "Events", "Server", "Http",
            "HttpFolder","GlobalDB","Client","HttpClientSimple", "EncHttp", "Mempool", "Stream", "StreamCtl",
            "Chain", "Wallet", "ChainCSDag", "ChainCSDagPoa", "ChainCSDagPos", "GDB", "Net", "AppCliServer",
            "ChainNetSrv","HttpSimple", "StreamChChain", "StreamChChainNet",
            "StreamChChainNetSrv" ],
        "Core": {
            "config_dir": "${tmp_dir}",
            "log_level": "${log_level}",
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
            "server": {
                "enabled": true,
                "listen_address": "0.0.0.0",
                "listen_port_tcp": 8099
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
                "${net_name}": {
                    "general":{
                        "id": "0xFF00000000000003",
                        "name": "${net_name}",
                        "node-role": "root",
                        "gdb_groups_prefix": "${net_name}"
                    },
                    "name_cfg_files": ["main"],
                    "conf_files":{
                        "main": {
                            "chain":{
                                "id": "0x0A0000000000000F",
                                "name": "main",
                                "consensus": "dag_poa",
                                "datum_types": ["ca", "transaction","token","token_update","emission","shard"]
                            },
                            "dag":{
                                "is_single_line": false,
                                "is_celled": true,
                                "is_add_directly": true,
                                "datum_and_hash_count": 3
                            },
                            "dag-poa":{
                                "auth_certs_prefix": "${net_name}.root",
                                "auth_certs_number": 5,
                                "auth_certs_number_verify":1,
                                "auth_certs_dir": "${var_dir}/lib/ca"
                            },
                            "files":{
                                "storage_dir":"{$var_dir}/lib/network/${net_name}/main"
                            }
                        }
                    }
                }
            }
        }
    }"""
    )
    tpl_vars = {
        "var_dir": var_dir,
        "tmp_dir": tmp_dir,
        "app_name": app_name,
        "net_name": getNetworkName(app_name),
        "log_level": log_level

    }
    return ret_tpl.substitute(tpl_vars)
