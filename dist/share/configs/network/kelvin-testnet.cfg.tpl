# Kelvin Blockchain: development network
# General section
[general]
id=0x0000000000000001
name=kelvin-testnet
type=development
# Possible values: light, full, archive, master, root
node-role=full
node-alias=addr-%node_addr%
gdb_groups_prefix=kelvin.testnet
seed_nodes_ipv4=[159.89.228.115,165.227.17.239,104.248.89.205,157.230.240.104,167.99.87.197,46.101.149.240,159.89.122.48]
seed_nodes_aliases=[kelvin.testnet.root.0,kelvin.testnet.root.1,kelvin.testnet.root.2,kelvin.testnet.root.3,kelvin.testnet.root.4,kelvin.testnet.root.5,kelvin.testnet.root.6]

#[dag-poa]
#events-sign-cert=mycert

#[dag-pos]
#events-sign-wallet=mywallet
