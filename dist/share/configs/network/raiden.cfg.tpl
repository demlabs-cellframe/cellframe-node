# Raiden testnet

# General section
[general]
id=0x000000000000bbbb
name=raiden
native_ticker=tCELL
gdb_groups_prefix=raiden

# Possible values: light, full, archive, master, root
node-role={NODE_TYPE}

# Number of active uplinks node will try to supply 
#links_required=3
# Will be used first. If count of permanent links less than required than missing links will be filled with net balancer
#permanent_nodes_addrs=[]
# If permanent addresses pointed without hosts then information about host will be retrieved from GDB
#permanent_nodes_hosts=[]
# This addresses will have priviledged acceess to some GDB groups
authorized_nodes_addrs=[BCA3::B097::DCDC::CB2B, 038E::0C9B::A3E8::C533, CC88::3F68::5313::1577]
# This hosts wiil be used as bootstrap balancers for first net access
seed_nodes_hosts=[0.root.raiden.cellframe.net:8079, 1.root.raiden.cellframe.net:8079, 2.root.raiden.cellframe.net:8079]

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
