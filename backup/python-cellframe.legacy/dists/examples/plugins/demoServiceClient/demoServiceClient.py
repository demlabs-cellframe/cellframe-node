from DAP.Core import logIt
from DAP.Crypto import Cert, HashFast
from CellFrame.Common import TxReceipt
from CellFrame.Network import Net, ServiceUID, ServiceClient

def callback_connected(serviceClient, arg):
    logIt.notice("Python client connected")
    ch_uid = ServiceUID(123)
    net = Net.byName("private")
    #serviceClient.write(ch_uid, "Greetings from test client".encode('utf-8'))
    #serviceClient.check(net, ch_uid, "Any data".encode('utf-8'))
    condHash = HashFast.fromString("0xAF14CB70DB383A4FB840F8BD531A7B58C300B65AD3B3F418DC0713B0F6648643");
    serviceClient.request(net, ch_uid, condHash)

def callback_disconnected(serviceClient, arg):
    logIt.notice("Python client disconnected")

def callback_deleted(serviceClient, arg):
    logIt.notice("Python client deleted")

def callback_check(serviceClient, arg):
    logIt.notice("Python client successfully checked the service")

def callback_sign(serviceClient, txCondRec, arg):
    logIt.notice("Siging receipt by python client")
    signCert = Cert.load("svc_client")
    return txCondRec.sign(signCert)

def callback_success(serviceClient, txCondHash, arg):
    logIt.notice("Python client successfully requested the service")

def callback_error(serviceClient, errorNum, arg):
    logIt.warning(f"Python client got error {errorNum:#x}")

def callback_data(serviceClient, data, arg):
    logIt.notice(f"Python client custom data read back \'{data.decode('utf-8')}\'")

def init():
    logIt.notice("Init demoClient")
#    Command for working cmd client
#    AppCliServer.cmdItemCreate("myClient", clientCMD, "Command for working cmd",
    net = Net.byName("private")
    client = ServiceClient(net, "127.0.0.1", 8089, callback_connected,
                                                   callback_disconnected,
                                                   callback_deleted,
                                                   callback_check,
                                                   callback_sign,
                                                   callback_success,
                                                   callback_error,
                                                   callback_data,
                                                   0)
    return 0
