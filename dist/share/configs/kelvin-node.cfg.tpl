# General section
[general]
#   Network config name (without trailing .cfg )
network-name=kelvin-dev  
#   Possible values: light,full,archive,master,root
network-role=root  

# Server part
[server]
#   By default you don't need to open you to the world
enabled=true 
listen_address=0.0.0.0
listen_port_tcp=8079

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
dap_global_db_path=/opt/kelvin-node/var/whitelist.ldb

# Small builtin WWW server
[www]
#   Really who need this??
enabled=false 
www_root=/opt/dapserver/www
url=/
