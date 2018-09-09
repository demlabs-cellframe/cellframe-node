# General section
[general]
network-name=kelvin-test  # Network config name (without trailing .cfg )
network-role=light  #  Possible values: light,full,archive,master,root

# Server part
[server]
enabled=false #  By default you don't need to open you to the world
listen_address=127.0.0.1
listen_port=8079

# VPN stream channel processing module
[vpn]
enabled=false  # Turn to true if you want to share VPN service from you node 
access_groups=expats,services,admins # list of loca security access groups. Built in: expats,admins,services,nobody,everybody
network_address=10.0.0.0
network_mask=255.255.255.0

[resources]
pid_path=/opt/kelvin-node/var/run/kelvin-node.pid
log_file=/opt/kelvin-node/var/log/kelvin-node.log

# Small built in WWW server
[www]
enabled=false # Really who need this??
www_root=/opt/dapserver/www
url=/
