# Core testnet
# General section
[general]
id=0xffffffffffffffff
name=core-t
# Possible values: light, full, archive, master, root
node-role={NODE_TYPE}
node_addr_type=auto
bootstrap_hostnames=[ random.bootstrap.core-t.cellframe.net:80, reserved.bootstrap.core-t.cellframe.net:80 ]

#[role-master]
#proc_chains=[0x00000001]

#[dag-poa]
#events-sign-cert=mycert

#[dag-pos]
#events-sign-wallet=mywallet

