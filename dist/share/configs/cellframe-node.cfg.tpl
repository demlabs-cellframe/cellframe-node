# General section
[general]
# General debug mode
debug_mode={DEBUG_MODE}
# Debug stream packets
debug_dump_stream_headers=false
# Debug I/O reactor, false by default
#debug_reactor=false
# Debug HTTP protocol, false by default
#debug_http=false

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

[notify_server]
# Listening path have priority above listening address 
#listen_path={PREFIX}/var/run/node_notify
#listen_path_mode=600
listen_address={NOTIFY_SRV_ADDR}
listen_port={NOTIFY_SRV_PORT}

[stream]
# For now its IAES but thats depricated
#preferred_encryption=SALSA2012 
# Debug stream protocol
#debug=true

# Build in DNS client (need for bootstraping)
[dns_client]
#request_timeout=10

# Bootstrap balancer server
[bootstrap_balancer]
dns_server=false
http_server=false

# Ledger defaults
[ledger]
# More debug output
# debug_more=true

# DAG defaults
[dag]
# More debug output
# debug_more=true
#threshold_enabled=true

# Synchronizatiob defaults
[node_client]
#timer_update_states=300

[srv]
allow_unsigned_orders=false
allow_unverified_orders=false
unverified_orders_lifetime=21600

[srv_dns]
enabled=false
pricelist=[]

# Mempool
[mempool]
# Automatically false, for enabling need role master or higher
auto_proc=false

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

# VPN stream channel processing module
[srv_vpn]
#   Turn to true if you want to share VPN service from you node 
enabled=false
debug_more=false
# Grace period for service , 60 second by default
#grace_period=60 
#   List of loca security access groups. Built in: expats,admins,services,nobody,everybody
network_address=10.11.12.0
network_mask=255.255.255.0
# The network on which the service operates
#net=KelVPN
# Wallet address for transferring payment for the service.
#wallet_addr=
# The name of the certificate for signing receipts. Must match the master node certificate.
#receipt_sign_cert=

# Console interface server
[conserver]
enabled=true
#listen_port_tcp=12345
listen_unix_socket_path={PREFIX}/var/run/node_cli
# Default permissions 770
# IMPORTANT! Its accessible for all the users in system!
listen_unix_socket_permissions=777

# Application Resources
[resources]
#   0 means auto detect
threads_cnt=0 
# By default notify opens at {PREFIX}/var/run/node_notify
notify_path={PREFIX}/var/run/node_notify
#notify_permissions=770
#notify_user=myuser
#notify_group=mygroup
pid_path={PREFIX}/var/run/cellframe-node.pid
log_file={PREFIX}/var/log/cellframe-node.log
wallets_path={PREFIX}/var/lib/wallet
ca_folders=[{PREFIX}/var/lib/ca,{PREFIX}/share/ca]

[global_db]
path={PREFIX}/var/lib/global_db
#driver={DB_DRIVER}
#debug_more=true

# Plugins
[plugins]
py_path={PREFIX}/var/lib/plugins
# enabled=true
# Load Python-based plugins
#py_load=true   
# Path to Pyhon-based plugins

