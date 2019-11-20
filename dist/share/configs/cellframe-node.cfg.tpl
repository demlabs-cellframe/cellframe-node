# General section
[general]
debug_mode={DEBUG_MODE}
debug_dump_stream_headers={DEBUG_STREAM_HEADERS}
wallets_default=default
# seed mode. WARNING. Used true only when you start the new network
#seed_mode=false
auto_online={AUTO_ONLINE}

# Console

# Server part
[server]
#   By default you don't need to open you to the world
enabled={SERVER_ENABLED}
listen_address={SERVER_ADDR}
listen_port_tcp={SERVER_PORT}

# Mempool
[mempool]
accept=false

# Central Dataase
[cdb]
enabled=false
db_path=mongodb://localhost/db
servers_list_enabled=false
networks=[kelvin-testnet,private]

# Central Database authorization
[cdb_auth]
enabled=false
collection_name=mycollection
domain=mydomain
tx_cond_create=false

# VPN stream channel processing module
[vpn]
#   Turn to true if you want to share VPN service from you node 
enabled=false
#   List of loca security access groups. Built in: expats,admins,services,nobody,everybody
access_groups=expats,services,admins 
network_address=10.11.12.0
network_mask=255.255.255.0

# old VPN server
[vpn_old]
enabled=true
network_address=10.11.11.0
network_mask=255.255.255.0

# Console interface server
[conserver]
enabled=true
#listen_port_tcp=12345
listen_unix_socket_path=/opt/cellframe-node/var/run/node_cli
# Default permissions 770
#listen_unix_socket_permissions=770

# Application Resources
[resources]
#   0 means auto detect
threads_cnt=0 
pid_path=/opt/cellframe-node/var/run/cellframe-node.pid
log_file=/opt/cellframe-node/var/log/cellframe-node.log
wallets_path=/opt/cellframe-node/var/lib/wallet
ca_folders=[/opt/cellframe-node/var/lib/ca,/opt/cellframe-node/share/ca]
dap_global_db_path=/opt/cellframe-node/var/lib/global_db
dap_global_db_driver=cdb

