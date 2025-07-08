from DAP.Core import logIt
from DAP.Crypto import HashFast, Algo, CryptoKeyType
from CellFrame.Network import Net, ServiceOrder, ServiceOrderDirection, ServiceUID, ServicePriceUnitUID
from CellFrame import AppCliServer
import time
from datetime import datetime, timedelta

"""This function is designed to get a string representation of the values that are in the order. """
def infoOrder(order):
    reply = "Order: \n"
    reply += "\tVersion:" + str(order.version)+"\n"
    reply += "\tUID: " + str(order.uid) + "\n"
    reply += "\tDirection: " + str(order.direction) + "\n"
    reply += "\tNode addr: " + str(order.nodeAddr) + "\n"
    reply += "\tCond hash: " + str(order.condHash) + "\n"
    reply += "\tPrice unit: " + str(order.priceUnit) + "\n"
    created = datetime.fromtimestamp(order.tsCreated)
    reply += "\tCreated: " + str(created) + "\n"
    expires = datetime.fromtimestamp(order.tsExpires)
    reply += "\tExpires: " + str(expires) + "\n"
    reply += "\tSrv price: " + str(order.srvPrice) + "\n"
    reply += "\tSrv price ticker: " + order.srvPriceTicker + "\n"
    reply += "\textSignSize:" + str(order.extSize) + "\n"
    reply += "\tSignature:\n"
    sign = order.extSign
    if sign is None:
        reply += "Signature none"
    else:
        type = sign.type
        pkey = sign.pkey
        pkey_type = pkey.type
        # pkey_hash = pkey.hash
        pkey_size = pkey.size
        pkey_dict = {
            'type': str(pkey_type),
            'size': pkey_size
        }
        pkey_hash = sign.pkeyHash
        sig_dict = {
            'type': str(sign.type),
            'pkey': pkey_dict,
            'pkey_hash': str(pkey_hash),
            'size': str(sign.size)
        }
        reply += str(sig_dict)
#    reply += "\Signs:" + str(order.ext) + "\n"
    return reply

def pwoCMD(argv, indexStrReply):
    if (len(argv) == 5):
        net = Net.byName(argv[2])
        if argv[3] == "find":
            order = ServiceOrder.find(net, argv[4])
            reply = ""
            if order is None:
                reply = "Order with hash "+argv[4]+" not fined."
            else:
                reply = "Order: \n"
                order_reply = infoOrder(order)
                reply += order_reply
            AppCliServer.setReplyText(reply, indexStrReply)
        elif argv[3] == "del":
            res = ServiceOrder.delete(net, argv[4])
            AppCliServer.setReplyText("Result: "+str(res)+".", indexStrReply)
        else:
            AppCliServer.setReplyText("An unknown action is specified to be performerd on the order.", indexStrReply)
    else:
        AppCliServer.setReplyText("This command takes only four arguments.", indexStrReply)

"""
This function generates the key required to create an order
"""
def create_key():
    """The key generation function accepts the type of the generated key, kex_buf,
    the size of the generated key, and the seed phrase. """
    return Algo.generateNewKey(CryptoKeyType.DAP_ENC_KEY_TYPE_SIG_BLISS(), "SARON00151454_VDGTKHJFY", 512, " I SIMPKLE SEED STRING ")

"""
This function is a notifier, it is triggered when an order is created or deleted from GlobalDB.
It takes the following arguments as input
    * op_code is responsible for the state of the pian order or deleted.
    * group name in globalDB.
    * the key by which the value is located (usually a hash).
    * The data itself, in this case it is the order object
    * the object that was set when setting the notifier, it can be a string, a number, a function, etc. In this case, it is a string. 
"""
def order_notify(op_code, group, key, order, arg):
    logIt.notice("Arg: "+arg)
    logIt.notice("Notify: \n")
    logIt.notice("op_code: "+op_code+"\n")
    logIt.notice("group: "+group+"\n")
    logIt.notice("key: "+key+"\n")
    if order is not None:
        logIt.notice(infoOrder(order))
    else:
        logIt.notice("No order.")

def init():
    logIt.notice("Running plugin order")
    net = Net.byName("kelvin-testnet")
# We add a notifier that will work when creating or deleting an order.
    ServiceOrder.addNotify(net, order_notify, "This is the same line that will be printed out when the notifier "
                                              "argument is printed. ")
# We receive and display information about the group where orders are stored, as well as about the nodelist.
    gdb_group = ServiceOrder.getGdbGroup(net)
    logIt.notice("Ordr in group: "+gdb_group)
    node_list_group = ServiceOrder.getNodelistGroup(net)
    logIt.notice("Node list group: "+node_list_group)
# Creating a new order
#   Set the direction of the order and the UID of the service.
    net_srv = ServiceUID(12345)
    direction = ServiceOrderDirection.getDirSell()
#   We get the address of the node.
    node_addr = net.getCurAddr()
    """tx_cond  - This should be the address of the conditional transaction, but it is not required to create an order.
    But in the order that the service issues, it should be."""
#   We set the price and units of measurement, for which you buy for this price.
    price = 531
    priceUnitUid = ServicePriceUnitUID.mb()
    key = create_key()
#   We determine the lifetime of the order, at the moment it is not used in the SDK.
    dt_exp = datetime.now()
    dt_delta = timedelta(days=30)
    dt_exp += dt_delta
    ts_expires = dt_exp.timestamp()
    """
    With the help of this constructor, an order is created. The constructor takes the following parameters as input:
        * Network object.
        * Direction order
        * Service UID.
        * Node address.
        * Hash of the conditional transaction in this case None.
        * Price.
        * Units of measure.
        * A set of bytes, there can be any information in this case, the URL address.
        * The key with which the order is signed. 
    """
    order = ServiceOrder(net, direction, net_srv, node_addr, None, price, priceUnitUid, "tCELL", ts_expires, "http://myvi.com/?QBS".encode('utf-8'), key)
#   This function simply saves the order and returns its hash, by which the order can be found or deleted.
    hash = order.save(net)
    logIt.notice("HASH order:"+str(hash))
    AppCliServer.cmdItemCreate("pwo", pwoCMD, "Example command for working with orders through the plugin",
"""
    Arguments for command:
    net <net> find <hash order>
    net <net> del <hash order>
""")
    return 0



