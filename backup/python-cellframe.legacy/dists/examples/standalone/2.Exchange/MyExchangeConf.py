import os
from string import Template

def getJsonString(app_name):
    tmp_dir = os.getcwd() + "/tmp"
    var_dir = os.getcwd() + "/var"
    ret_tpl = Template("""
    {
        "modules": [
            "Crypto", "ServerCore", "Http",
            "HttpFolder","GlobalDB","Client","HttpClientSimple","Mempool",
            "Chain", "Wallet", "ChainCSDag", "ChainCSDagPoa", "ChainCSDagPos", "GDB", "Net", "AppCliServer",
            "ChainNetSrv", "EncHttp","Stream", "StreamCtl", "HttpSimple", "StreamChChain", "StreamChChainNet",
            "StreamChChainNetSrv" ],
        "Core": {
            "config_dir": "${tmpdir}",
            "log_level": "L_DEBUG",
            "application_name": "${appname}",
            "file_name_log": "${vardir}/log/${appname}.log"
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
                "listen_unix_socket_path": "${tmpdir}/node_cli"
            },
            "resources": {
                "threads_cnt": 0,
                "pid_path": "${vardir}/run/${appname}.pid",
                "log_file": "${vardir}/log/${appname}.log",
                "wallets_path": "${vardir}/lib/wallet",
                "ca_folders": [ "${vardir}/lib/ca" ],
                "dap_global_db_path": "${vardir}/lib/global_db",
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
                                "datum_types": ["ca", "transaction"]
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
                                "auth_certs_dir": "${vardir}/lib/ca"
                            }
                        }
                    }
                }
            }
        }
    }"""
    )
    tpl_vars={
        "vardir":var_dir,
        "tmpdir":tmp_dir,
        "appname":app_name
    }
    return ret_tpl.substitute(tpl_vars)
