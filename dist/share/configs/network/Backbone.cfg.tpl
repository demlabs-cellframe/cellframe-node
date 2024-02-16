# Backbone net config

# General section
[general]
id=0x0404202200000000
name=Backbone
gdb_groups_prefix=scorpion
native_ticker=CELL
bridged_network_ids=[0x1807202300000000]

# Possible values: light, full, archive, master, root
node-role={NODE_TYPE}

# If true connecting only to seed_nodes_addrs and permanent_nodes_addrs
#links_static_only=true
seed_nodes_aliases=[0.root.scorpion,1.root.scorpion,2.root.scorpion,3.root.scorpion,4.root.scorpion]
seed_nodes_hostnames=[0.root.scorpion.cellframe.net,1.root.scorpion.cellframe.net,2.root.scorpion.cellframe.net,3.root.scorpion.cellframe.net,4.root.scorpion.cellframe.net]
seed_nodes_port=[8079,8079,8079,8079,8079]
seed_nodes_addrs=[0404::2022::0000::0000,0404::2022::0000::0001,0404::2022::0000::0002,0404::2022::0000::0003,0404::2022::0000::0004]
#permanent_nodes_addrs=[0404::2022::0000::0005,0404::2022::0000::0006]

#[auth]
#type=ca
#acl_accept_ca_list=[]
#acl_accept_ca_gdb=
#acl_accept_ca_chains=all

[dag-poa]
#events-sign-cert=scorpion.root.0

[esbocs]
#blocks-sign-cert=mycert
#minimum_fee=1.0
#fee_addr=myaddr

