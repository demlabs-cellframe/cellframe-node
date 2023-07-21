# KelVPN net config

# General section
[general]
id=0x1807202300000000
name=KelVPN
native_ticker=KEL
gdb_groups_prefix=kelvpn


# Possible values: light, full, archive, master, root
node-role={NODE_TYPE}
seed_nodes_aliases=[kelvpn.root.0,kelvpn.root.1,kelvpn.root.2]
seed_nodes_hostnames=[0.root.kelvpn.com,1.root.kelvpn.com,2.root.kelvpn.com]
seed_nodes_addrs=[1807::2023::0000::0000,1807::2023::0000::0001,1807::2023::0000::0002]
seed_nodes_port=[8079,8079,8079]
require_links=3

#[auth]
#type=ca
#acl_accept_ca_list=[]
#acl_accept_ca_gdb=
#acl_accept_ca_chains=all

[dag-poa]
#events-sign-cert=kelvpn.root.0

[esbocs]
#blocks-sign-cert=mycert
#minimum_fee=1.0
#fee_addr=myaddr

