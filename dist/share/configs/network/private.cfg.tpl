# Kelvin Blockchain: development network
# General section
[general]
id=0xFF00000000000001
name=private
native_ticker=TST
links_static_only=true
# Possible values: light, full, archive, master, root
node-role={NODE_TYPE}
# type of node addr [auto, static, dinamic]
node_addr_type=auto
#node_addr_type=static
#node-addr=[ffff::0000::0000::0001]

seed_nodes_ipv4=[195.154.133.160, 62.210.90.227]
seed_nodes_port=[8080, 8080]
seed_nodes_aliases=[private.root.0,private.root.1]
seed_nodes_addrs=[ffff::0000::0000::0001,ffff::0000::0000::0002]

#[dag-poa]
#events-sign-cert=mycert

#[dag-pos]
#events-sign-wallet=mywallet
