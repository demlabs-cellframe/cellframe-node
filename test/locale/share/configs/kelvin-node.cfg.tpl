# General section
[general]
debug_mode=false
wallets_path=/opt/kelvin-node/var/lib/wallet
wallets_default=default
node_role=full
# seed mode. WARNING. Used true only when you start the new network
#seed_mode=false


# Server part
[server]
#   By default you don't need to open you to the world
enabled=true 
listen_address=0.0.0.0
listen_port_tcp=8079

# Mempool
[mempool]
accept=false

# VPN stream channel processing module
[vpn]
#   Turn to true if you want to share VPN service from you node 
enabled=false
#   List of loca security access groups. Built in: expats,admins,services,nobody,everybody
access_groups=expats,services,admins 
network_address=10.0.0.0
network_mask=255.255.255.0

# Application Resources
[resources]
#   0 means auto detect
threads_cnt=0 
pid_path=/opt/kelvin-node/var/run/kelvin-node.pid
log_file=/opt/kelvin-node/var/log/kelvin-node.log
ca_folders=[/opt/kelvin-node/var/lib/ca,/opt/kelvin-node/share/ca]
dap_global_db_path=/opt/kelvin-node/var/whitelist.ldb

