# Raiden testnet

# General section
[general]
id=0x000000000000bbbb
name=raiden
native_ticker=tCELL
gdb_groups_prefix=raiden

# Possible values: light, full, archive, master, root
node-role={NODE_TYPE}

# If true connecting only to seed_nodes_addrs and permanent_nodes_addrs
#links_static_only=true
seed_nodes_aliases=[raiden.cellframe.root.0,raiden.cellframe.root.1,raiden.cellframe.root.2]
seed_nodes_hostnames=[0.root.raiden.cellframe.net,1.root.raiden.cellframe.net,2.root.raiden.cellframe.net]
seed_nodes_port=[8079,8079,8079]
seed_nodes_addrs=[BBBB::0000::0000::0000,BBBB::0000::0000::0001,BBBB::0000::0000::0002]
#permanent_nodes_addrs=[DDDD::0000::0000::0003,DDDD::0000::0000::0004]

#[auth]
#type=ca
#acl_accept_ca_list=[]
#acl_accept_ca_gdb=
#acl_accept_ca_chains=all

#[dag-poa]
#events-sign-cert=raiden.root.pvt.0

#[esbocs]
#blocks-sign-cert=mycert
#minimum_fee=1.0
#fee_addr=myaddr
