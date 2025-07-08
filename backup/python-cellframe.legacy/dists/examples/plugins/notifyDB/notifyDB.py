from DAP.Core import logIt
from CellFrame.Network import Net

def notify_net_db(op_code, group, key, value, arg):
    logIt.notice("Notificator")
    logIt.notice("    op_code: "+op_code)
    logIt.notice("    group: "+group)
    logIt.notice("    key:"+key)
    logIt.notice("    value:"+str(value))
    logIt.notice("    Arg: "+str(arg))

def init():
    logIt.notice("Start plugin notifyDB")
    net = Net.byName("kelvin-testnet")
    net.addNotify(notify_net_db, "This is notificator work with net db in network "+str(net))
    return 0

