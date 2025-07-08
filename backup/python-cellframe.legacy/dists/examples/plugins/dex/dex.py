from DAP.Core import logIt, AppContext
from CellFrame import AppCliServer
from DAP.Network import Server as IO, HttpSimple
from CellFrame.Services import Xchange
from CellFrame.Network import Net
from DAP.Core import Math
from CellFrame.Chain import Wallet


def find_arg_value(val, argv):
    for i, arg in enumerate(argv):
        if arg == val:
            if len(argv) > i+1:
                return argv[i+1]

    return None

def find_arg(val, argv):
    for i, arg in enumerate(argv):
        if arg == val:
            return True

    return False


def list_orders(argv, rpi):
    netname = find_arg_value("-net", argv) 
    net = Net.byName(netname)
    orders = Xchange.getOrders(net)   
    msg = f"Net {netname} has {len(orders)} orders:\n"

    for p in orders:
        msg += f"Order: {str(p.orderHash)} [{p.status}]" + "\n"
        msg += f"\t Buying  {int(str(p.datoshiBuy))/10**18} {p.tokenBuy} "
        msg += f"for {int(str(p.datoshiSell))/10**18} {p.tokenSell} "
        msg += f"(rate={int(str(p.rate))/10**18} "
        msg += f"completed={p.completionRate}%) \n"
        msg += f"\t Fee:        {p.fee}" + "\n"
        msg += f"\t Last tx:    {p.txHash}" + "\n"
        msg += "\n"
    AppCliServer.setReplyText(msg, rpi)    


def purchase(argv, rpi):
    
    netname = find_arg_value("-net", argv) 
    orderhash = find_arg_value("-order", argv) 
    value = Math(find_arg_value("-value", argv))
    wallet = Wallet.openFile(find_arg_value("-wallet", argv))

    net = Net.byName(netname)
    order = next(filter(lambda x: str(x.orderHash) == str(orderhash),  Xchange.getOrders(net)),None)

    if not order:
        AppCliServer.setReplyText("Order not found", rpi)
        return    
    
    order.purchase(value, net.validatorAverageFee, wallet)
    
def create(argv, rpi):    
    netname = find_arg_value("-net", argv) 
    tsell = find_arg_value("-tsell", argv) 
    tbuy = find_arg_value("-tbuy", argv) 
    sellval = Math(find_arg_value("-value", argv) )
    rate = Math(find_arg_value("-rate", argv))
    wallet = Wallet.openFile(find_arg_value("-wallet", argv))
    
    net = Net.byName(netname)
    Xchange.createOrder(net, tsell, tbuy, sellval, rate,  net.validatorAverageFee, wallet)
    
def close(argv, rpi):
    netname = find_arg_value("-net", argv) 
    orderhash = find_arg_value("-order", argv) 
    wallet = Wallet.openFile(find_arg_value("-wallet", argv))

    net = Net.byName(netname)
    order = next(filter(lambda x: str(x.orderHash) == str(orderhash),  Xchange.getOrders(net)),None)

    if not order:
        AppCliServer.setReplyText("Order not found", rpi)
        return    
    
    order.invalidate(net.valкidatorAverageFee, wallet)
    

def init():
    logIt.notice("Starting dex test plugin")
    AppCliServer.cmdItemCreate("xlist", list_orders, "Show awailable XChange orders")
    AppCliServer.cmdItemCreate("xpur", purchase, "purchase order")
    AppCliServer.cmdItemCreate("xcreate", create, "create order")
    AppCliServer.cmdItemCreate("xrm", close, "close order")
    return 0
