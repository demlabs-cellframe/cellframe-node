# Kelvin Testnet
# General section
[general]
id=0x0000000000000001
name=kelvin-testnet
# Possible values: light, full, archive, master, root
node-role={NODE_TYPE}

seed_nodes_hostnames=[0.root.testnet.kelvpn.com,1.root.testnet.kelvpn.com,2.root.testnet.kelvpn.com,3.root.testnet.kelvpn.com,4.root.testnet.kelvpn.com]
seed_nodes_aliases=[kelvin.testnet.root.0,kelvin.testnet.root.1,kelvin.testnet.root.2,kelvin.testnet.root.3,kelvin.testnet.root.4]
seed_nodes_addrs=[ffff::0000::0000::0001,ffff::0000::0000::0002,ffff::0000::0000::0003,ffff::0000::0000::0004,ffff::0000::0000::0005]
seed_nodes_port=[8079,8079,8079,8079,8079]

private=false

#[auth]
#type=ca
#acl_accept_ca_list=[]
#acl_accept_ca_gdb=
#acl_accept_ca_chains=all

#[role-master]
#proc_chains=[0x00000001]

#[dag-poa]
#events-sign-cert=mycert

#[dag-pos]
#events-sign-wallet=mywallet

