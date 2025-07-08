from DAP import configGetItem
from DAP.Core import logIt
from CellFrame.Chain import Mempool, ChainAddr, Wallet
from CellFrame.Network import Net

def init():

    wallet_path = configGetItem("resources", "wallets_path")
    logIt.notice("wallet path: "+wallet_path)
    wallet = Wallet.open("mywallet1", wallet_path)
    chain_net = Net.byName("subzero")
    chain = chain_net.getChainByName("support")
    key = wallet.getKey(0)
    addr_from = wallet.getAddr(chain_net.id)
    addr_to = ChainAddr.fromStr("mJUUJk6Yk2gBSTjcCmbwJ2ozjDTLPKZTmTVM9AUysMfWt4oQcNwjtCNEbkGo1dWVmkNXaQYbPtMqdHD4ftF5Sfx4mo9ss9r4jauSXDhV")
    addr_fee = None
    value = 50
    value_fee = 0
    # tx_hash = Mempool.txCreate(chain, key, addr_from, addr_to, addr_fee, "tCELL", value, value_fee)
    # tx_hash_str = str(tx_hash)
    # logIt.notice("Created transaction with hash: " + tx_hash_str)
    return 0
