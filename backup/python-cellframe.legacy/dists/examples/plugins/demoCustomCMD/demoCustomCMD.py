from DAP.Core import logIt
from CellFrame import AppCliServer

"""
This function takes two arguments
argv is an array of incoming arguments
indexStrReply is an internal index that correlates what is needed
 to fill the desired buffer with the data that will be passed to the CLI.
"""
def cmdDemo(argv, indexStrReply):
    reply = "Arguments :\n"
    for i in range(len(argv)):
        reply += "arg["+str(i)+"]: "+argv[i]+"\n"
    AppCliServer.setReplyText(reply, indexStrReply)

def cmdDemo2(argv, indexStrReply):
    AppCliServer.setReplyText("I simple demo command", indexStrReply)

def init():
    logIt.notice("Running plugin order")
    """
          The cmdItemCreate function creates a CLI command. 
          This function takes four arguments.
          Command name, command handler function, short description of 
        of the command, full description of the command.
    """
    AppCliServer.cmdItemCreate("demo", cmdDemo, "Command demo",
"""
    This command is intended to demonstrate the work of custom command in the CellFrame API for Python.
""")
    AppCliServer.cmdItemCreate("demo2", cmdDemo2, "Second command demo",
"""
    This is demo and testing
""")
    return 0
