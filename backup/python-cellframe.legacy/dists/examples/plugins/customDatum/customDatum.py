from DAP.Core import logIt
from CellFrame.Common import CustomDatum
from CellFrame.Network import Net
from CellFrame import AppCliServer

def datumCMD(argv, indexStrReply):
    if (len(argv) == 3 or len(argv) == 5):
        if (argv[1] == 'create'):
            net = Net.byName(argv[2])
            chain = net.getChainByName(argv[3])
            res = CustomDatum.create(chain, argv[4].encode('utf-8'))
            AppCliServer.setReplyText("Return hash datum: "+str(res), indexStrReply)
        elif(argv[1] == 'load'):
            data = CustomDatum.read(argv[2])
            AppCliServer.setReplyText("Return data: "+str(data), indexStrReply)
    else:
        logIt.notice("This command can take three or four arguments.")

def init():
    logIt.notice("Start plugin customDatum")
    AppCliServer.cmdItemCreate("pyDatum", datumCMD, "Command for creation datum", """
Command for created and get info from custom datum:
    create <net name> <chain name> <date in datum>
    load <path for file>
    """)
    return 0
