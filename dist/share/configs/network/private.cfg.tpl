# Kelvin Blockchain: development network
# General section
[general]
id=0xFF00000000000001
name=private
# Possible values: light, full, archive, master, root
node-role={NODE_TYPE}
gdb_groups_prefix=my-private
#node-alias=addr-%node_addr%
#node-addr=0x10
# node addr exired time in hours (168h=1w 720h=1m 8760h=1y), by default 720h(1week)
# node-addr-expired=168
# type of node addr [auto, static, dinamic]
node_addr_type=auto

seed_nodes_ipv4=[195.154.133.160, 62.210.90.227]
seed_nodes_port=[8079, 8079]
seed_nodes_aliases=[kelvin.testnet.root.0,kelvin.testnet.root.1]
seed_nodes_addrs=[ffff::0000::0000::0001,ffff::0000::0000::0002]

#[dag-poa]
#events-sign-cert=mycert

#[dag-pos]
#events-sign-wallet=mywallet
