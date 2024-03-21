# Subzero testnet

# General section
[general]
id=0x000000000000acca
name=subzero
native_ticker=tCELL
gdb_groups_prefix=subzero

# Possible values: light, full, archive, master, root
node-role={NODE_TYPE}

# If true connecting only to seed_nodes_addrs and permanent_nodes_addrs
#links_static_only=true
seed_nodes_aliases=[subzero.cellframe.root.0,subzero.cellframe.root.1,subzero.cellframe.root.2]
seed_nodes_hosts=[0.root.subzero.cellframe.net:8190, 1.root.subzero.cellframe.net:8190, 2.root.subzero.cellframe.net:8190]
seed_nodes_addrs=[608C::F7B7::D476::2438,7497::4FB4::CFA1::9823,5641::292F::13F5::F039]
#permanent_nodes_addrs=[ACCA::0000::0000::0003,ACCA::0000::0000::0004]

#[auth]
#type=ca
#acl_accept_ca_list=[]
#acl_accept_ca_gdb=
#acl_accept_ca_chains=all

#[dag-poa]
#events-sign-cert=mycert

#[esbocs]
#blocks-sign-cert=mycert
#minimum_fee=1.0
#fee_addr=myaddr