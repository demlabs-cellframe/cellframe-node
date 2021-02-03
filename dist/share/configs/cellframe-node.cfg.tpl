# General section
[general]
# General debug mode
debug_mode={DEBUG_MODE}
# Debug stream packets
debug_dump_stream_headers=false
# Debug I/O reactor, false by default
#debug_reactor=false

# seed mode. WARNING. Used true only when you start the new network
#seed_mode=false

# Auto bring up links and sync everything over them
auto_online={AUTO_ONLINE}

# Server part
[server]
#   By default you don't need to open you to the world
enabled={SERVER_ENABLED}
news_url_enabled=false
bugreport_url_enabled=false
listen_address={SERVER_ADDR}
listen_port_tcp={SERVER_PORT}
# External IPv4 address
#ext_address=8.9.10.11
# External IPv6 address
#ext_address6=aaaa:bbbb:deee:96ff:feee:3fff
#
# If not set - used listen_port_tcp for node table auto fill
#ext_port_tcp=8089


# Build in DNS client (need for bootstraping)
[dns_client]
#request_timeout=10

# Builtin DNS server
[dns_server]
#enabled=false
#bootstrap_balancer=false

# Ledger defaults
[ledger]
# More debug output
# debug_more=true

# DAG defaults
[dag]
# More debug output
# debug_more=true

[srv]
order_signed_only=false

[srv_dns]
enabled=false
pricelist=[]

# Mempool
[mempool]
# Automaticaly should be true for master ad root node role
# auto_proc=false

# Chain network settings
[chain_net]
# debug_more=true

[stream_ch_chain]
# Uncomment to have more debug information in stream channel Chain
# False by default
#debug_more=true

# Number of hashes packed into the one update packet
# Increase it to reduce update latency
# Decrease if bad networking
# update_pack_size=100


# Central Dataase
[cdb]
enabled=false
servers_list_enabled=false
servers_list_networks=[dapcash-testnet]

# Central Database authorization
[cdb_auth]
enabled=false
domain=mydomain
# auth mode=passwd[default] or serial
mode=passwd
registration_open=true
tx_cond_create=false
# List of condition templates, created for authorized users. Format of condition:
# <wallet name>:<Value per transaction>:<Minimum time(seconds) between transactions>:<network name> 
# tx_cond_templates=[mywallet0:0.00001:3600:DAPT:dapcash-testnet,mywallet1:0.000001:3600:KELT:dapcash-testnet]

# VPN stream channel processing module
[srv_vpn]
#   Turn to true if you want to share VPN service from you node 
enabled=false
geoip_enabled=false
debug_more=false
# Grace period for service , 60 second by default
#grace_period=60 
#   List of loca security access groups. Built in: expats,admins,services,nobody,everybody
network_address=10.11.12.0
network_mask=255.255.255.0
pricelist=[dapcash-testnet:100:DAPT:3600:SEC:mywallet0,dapcash-testnet:100:DAPB:3600:SEC:mywallet1]

# Console interface server
[conserver]
enabled=true
#listen_port_tcp=12345
listen_unix_socket_path=/opt/dapcash-node/var/run/node_cli
# Default permissions 770
#listen_unix_socket_permissions=770

# Application Resources
[resources]
#   0 means auto detect
threads_cnt=0 
pid_path=/opt/dapcash-node/var/run/dapcash-node.pid
log_file=/opt/dapcash-node/var/log/dapcash-node.log
wallets_path=/opt/dapcash-node/var/lib/wallet
geoip_db_path=share/geoip/GeoLite2-City.mmdb
ca_folders=[/opt/dapcash-node/var/lib/ca,/opt/dapcash-node/share/ca]
dap_global_db_path=/opt/dapcash-node/var/lib/global_db
dap_global_db_driver=cdb

