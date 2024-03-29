# Riemann testnet

# General section
[general]
id=0x000000000000dddd
name=riemann
native_ticker=tKEL
gdb_groups_prefix=riemann

# Possible values: light, full, archive, master, root
node-role={NODE_TYPE}
seed_nodes_aliases=[riemann.cellframe.root.0,riemann.cellframe.root.1,riemann.cellframe.root.2]
seed_nodes_hostnames=[0.root.riemann.cellframe.net,1.root.riemann.cellframe.net,2.root.riemann.cellframe.net]
seed_nodes_addrs=[DDDD::0000::0000::0000,DDDD::0000::0000::0001,DDDD::0000::0000::0002]
seed_nodes_port=[8079,8079,8079]

#[auth]
#type=ca
#acl_accept_ca_list=[]
#acl_accept_ca_gdb=
#acl_accept_ca_chains=all

#[esbocs]
#blocks-sign-cert=mycert
#minimum_fee=1.0
#fee_addr=myaddr
