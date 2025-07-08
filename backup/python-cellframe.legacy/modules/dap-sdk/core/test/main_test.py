from libTPO import *
import os
import sys

def create_config_file(app_name):
    f = open(app_name+".cfg", "w")
    f.write("[server]\nlisten_address=0.0.0.0\n")
    f.close()

print("Start main test")
app_name = "TestAPP"
print("Create config file")
create_config_file(app_name)
path = os.getcwd()

init(app_name, app_name, path, "DEBUG")
logIt(INFO, "Initialization of the DAP done")
setLogLevel(DEBUG)
logIt(INFO,"Level logging ""DEBUG"" done")
logIt(DEBUG, "Test. Outputting a string using the log_it function in the libdap library")
logIt(INFO,"Outputting a string using the log_it function done")
res1 = configGetItem("server", "listen_address")
logIt(INFO, "Output [server] 'listen_address' = "+res1+"\n")
res2 = configGetItemDefault("server1", "listen_address", "8.8.8.8")
logIt(INFO, "Output default value '8.8.8.8' [server1] 'listen_address' = "+res2+"\n")
logIt(INFO, "TEST. Get default config done")
deinit()
logIt(INFO, "Deinitialization done")

os.remove(app_name+".cfg")
logIt(INFO, "Dellete config file")
logIt(INFO, "Main test done");

sys.exit(0)
