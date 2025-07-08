from CellFrame import *
import pickle
import os
import sys
from time import sleep

def create_config_file(app_name):
    f = open(app_name+".cfg", "w")
    f.write("[server]\nlisten_address=0.0.0.0\n")
    f.close()

print("Start main test")
app_name = "testAPP"

dir_cfg = os.getcwd() + "/testdir"
print (dir_cfg)

json_string = """{
    "modules": ["Crypto", "ServerCore", "Http", "HttpFolder", "GlobalDB", "Client", "HttpClientSimple", "Mempool",
     "Chain", "Wallet", "ChainCSDag", "ChainCSDagPoa", "ChainCSDagPos", "GDB", "Net", "ChainNetSrv", "EncHttp",
     "Stream", "StreamCtl", "HttpSimple", "StreamChChain", "StreamChChainNet", "StreamChChainNetSrv"],
    "DAP": {
       "config_dir": \""""+dir_cfg+"""\",
       "log_level": "L_DEBUG",
       "application_name": \""""+app_name+"""\",
       "file_name_log": \""""+app_name+""".text\"
    },
    "Configuration" : {
        "general": {
            "debug_mode": false,
            "debug_dump_stream_headers": false,
            "wallets_default": "default"
        },
        "server": {
            "enabled": false,
            "listen_address": "0.0.0.0",
            "listen_port_tcp": 8079
        },
        "mempool": {
             "accept": false
        },
        "cdb": {
            "enabled": false,
            "db_path": "mongodb://localhost/db",
            "servers_list_enabled": false,
            "servers_list_networks": ["kelvin-testnet", "private"]
        },
        "cdb_auth": {
            "enabled": false,
            "collection_name": "mycollection",
            "domain": "mydomain",
            "tx_cond_create": false
        },
        "srv_vpn": {
            "enabled": false,
            "network_address": "10.11.12.0",
            "network_mask": "255.255.255.0",
            "pricelist": [
                "kelvin-testnet:0.00001:KELT:3600:SEC:mywallet0", "kelvin-testnet:0.00001:cETH:3600:SEC:mywallet1", "private:1:WOOD:10:SEC:mywallet0"
            ]
         },
        "conserver": {
            "enabled": true,
            "listen_unix_socket_path": \""""+dir_cfg+"""/run/node_cli\"
        },
        "resources": {
            "threads_cnt": 0,
            "pid_path": \""""+dir_cfg+"""/run/cellframe-node.pid\",
            "log_file": \""""+dir_cfg+"""/log/cellframe-node.log\",
            "wallets_path": \""""+dir_cfg+"""/lib/wallet\",
            "ca_folders": [
                \""""+dir_cfg+"""/lib/ca\",
                \""""+dir_cfg+"""/share/ca\"
            ],
            "dap_global_db_path": \""""+dir_cfg+"""/lib/global_db\",
            "dap_global_db_driver": "cdb"
        },
        "networks":{
            "private": {
                "general":{
                    "id": "0xFF00000000000001",
                    "name": "private",
                    "type": "testing",
                    "node-role": "full",
                    "gdb_groups_prefix": "private",
                    "node-addr-expired": 168,
                    "seed_nodes_ipv4": ["153.256.133.160", "62.216.90.227"],
                    "seed_nodes_port": [8079, 8079],
                    "seed_nodes_aliases": ["kelvin.testnet.root.0", "kelvin.testnet.root.1"],
                    "seed_nodes_addrs": ["ffff::0000::0000::0001","ffff::0000::0000::0002"]
                },
                "name_cfg_files": ["chain-gdb"],
                "conf_files":{
                    "chain-gdb": {
                        "general": {
                            "id": "0xf00000000000000f",
                            "name": "gdb",
                            "consensus": "gdb",
                            "class": "gdb",
                            "datum_types": ["token", "emission", "shard", "ca", "transaction"]
                        },
                        "gdb":{
                            "celled": false
                        }
                    }
                }
            }
        }
    },
    "Stream" : {
        "DebugDumpStreamHeaders": false
    },
    "ServerCore" : {
        "thread_cnt": 0,
        "conn": 0
    }
    }"""

print("init start")
init(json_string)
logItInfo("Initialization of the DAP done")
setLogLevel(DEBUG)
logItInfo("Level logging ""DEBUG"" done")
logItInfo( "Test. Outputting a string using the log_it function in the libdap library")
logItInfo("Outputting a string using the log_it function done")
res1 = configGetItem("server", "listen_address")
logItInfo("Output [server] 'listen_address' = "+res1+"\n")
res2 = configGetItemDefault("server1", "listen_address", "8.8.8.8")
logItInfo("Output default value '8.8.8.8' [server1] 'listen_address' = "+res2+"\n")
logItInfo( "TEST. Get default config done")

logItInfo ("Create KEY")
key = Crypto.newKey(CryptoKeyType.DAP_ENC_KEY_TYPE_IAES())
del key
logItInfo("Create KEY TWO")
key2 = Crypto.newKey(CryptoKeyType.DAP_ENC_KEY_TYPE_OAES())
logItInfo ("Dellete key")
del key2

logItInfo("TEST BASE58. START...")
s = """Test! I will crush Base58!"""
base_in = pickle.dumps(s)
crypt = Crypto.encodeBase58(base_in)
decrypt = Crypto.decodeBase58(crypt)
out_data = pickle.loads(decrypt)
if s == out_data:
    logItInfo ("TEST 1. Encode/Decode base58 done")
else:
    logItInfo ("TEST 1. Encode/Decode base58 faild")
    sys.exit(1)
logItInfo("TEST. BASE64 START...")
s = "Test! I will crush Base64!"
crypt = Crypto.encodeBase64(bytes(s, "utf-8"), CryptoDataType.DAP_ENC_DATA_TYPE_B64())
decrypt = Crypto.decodeBase64(crypt, CryptoDataType.DAP_ENC_DATA_TYPE_B64())
if bytes(s, "utf-8") == decrypt:
    logItInfo ("TEST 1. Encode/Decode base64 done")
else:
    logItInfo ("TEST 1. Encode/Decode base64 faild")
    sys.exit(1)
logItInfo ("TEST.BASE64 URLSAFE START...")
u = "http://kelvin.foundation/"
crypt_u = Crypto.encodeBase64(bytes(u, "utf-8"), CryptoDataType.DAP_ENC_DATA_TYPE_B64_URLSAFE())
decrypt_u = Crypto.decodeBase64(crypt_u, CryptoDataType.DAP_ENC_DATA_TYPE_B64_URLSAFE())
if bytes(u, "utf-8") == decrypt_u:
     logItInfo ("TEST 2. Encode/Decode base64 urlsafe done")
else:
     logItInfo ("TEST 2. Encode/Decode base64 urlsafe faild")
     sys.exit(2)

logItInfo ("TEST. IAES256 CBC START...")
s = "Test! I will crush iaes256!"
kex_buff = bytes("123", "utf-8")
size_kex_buff = len(kex_buff)
seed = bytes(112771128)
seed_size = len(seed)
key_n = Crypto.generateNewKey(CryptoKeyType.DAP_ENC_KEY_TYPE_IAES(), kex_buff, size_kex_buff, seed, seed_size, 0)
source = bytes(s, "utf-8")
enc = Crypto.encryptIAES256CBCFast(key_n, source, len(source), 2048)
decrypt = Crypto.decryptIAES256CBCFast(key_n, enc, len(enc), 2048)
if bytes(s, "utf-8") == decrypt:
    logItInfo ("TEST 1. Encode/Decode IAES256 CBC FAST done")
else:
    logItInfo ("TEST 1. Encode/Decode IAES256 CBC FAST faild")
    sys.exit(1)

logItInfo ("TEST. OAES START...")
s = "Test! I will crush OAES!"
kex_buff = bytes("114151400014314485131FGXVGHcJFIH", "utf-8")
size_kex_buff = len(kex_buff)
seed = bytes(112771128)
seed_size = len(seed)
key_id = Crypto.generateNewKey(CryptoKeyType.DAP_ENC_KEY_TYPE_OAES(), kex_buff, size_kex_buff, seed, seed_size, 32)
source = bytes(s, "utf-8")
enc = Crypto.encryptOAESFast(key_id, source, len(source), 2048)
decrypt = Crypto.decryptOAESFast(key_id, enc, len(enc), 2048)
if bytes(s, "utf-8") == decrypt:
    logItInfo ("TEST 1. Encode/Decode OAES FAST done")
else:
    logItInfo ("TEST 1. Encode/Decode OAES CBC FAST faild")
    sys.exit(1)


sleep
deinit()
logItInfo("Deinitialization done")

logItInfo( "Main test done");

sys.exit(0)
