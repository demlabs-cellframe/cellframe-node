# mileena net config

# General section
[general]
id=0x000000000000cccc
name=mileena
auth_cert=mileena.0.root
gdb_groups_prefix=mileena
# Possible values: light, full, archive, master, root
node-role={NODE_TYPE}
node_addr_type=static
node-addr=CCCC::0000::0000::0000
seed_nodes_aliases=[0.root.mileena,1.root.mileena,2.root.mileena,3.root.mileena,4.root.mileena]
seed_nodes_hostnames=[0.root.mileena.cellframe.net,1.root.mileena.cellframe.net,2.root.mileena.cellframe.net,3.root.mileena.cellframe.net,4.root.mileena.cellframe.net]
seed_nodes_addrs=[CCCC::0000::0000::0000,CCCC::0000::0000::0001,CCCC::0000::0000::0002,CCCC::0000::0000::0003,CCCC::0000::0000::0004]
seed_nodes_port=[8079,8079,8079,8079,8079]
require_links=4
private=false

#[auth]
#type=ca
#acl_accept_ca_list=[]
#acl_accept_ca_gdb=
#acl_accept_ca_chains=all


[dag-poa]
events-sign-cert=mileena.0.root

[block-ton]
blocks-sign-cert=mileena.0.root

#[block-poa]
#blocks-sign-cert=mycert