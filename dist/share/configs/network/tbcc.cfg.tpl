# TBCC
# General section
[general]
id=0x0000000000000002
name=tbcc
# Possible values: light, full, archive, master, root
node-role={NODE_TYPE}
node_addr_type=auto
default_chain=plasma
seed_nodes_hostnames=[0.cdb.tbcc.chains.demlabs.net,1.cdb.tbcc.chains.demlabs.net]
seed_nodes_aliases=[tbcc.root.0,tbcc.root.1]
seed_nodes_addrs=[ffff::0000::0000::0001,ffff::0000::0000::0002]
seed_nodes_port=[80,80]


#[role-master]
#proc_chains=[0x00000001]

[dag-poa]
events-sign-cert=pvt.tbcc.root.0

[dag-pos]
events-sign-wallet=cdb1
