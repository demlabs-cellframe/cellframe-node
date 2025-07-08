#!/usr/bin/python3
# CellFrame SDK.Python v0.9 Example Application #1
from CellFrame import *
import os
import json
import sys
import MyAuthConf
import MyAuthCmd
app_name = "MyAuth"

jsonCfg=MyAuthConf.getJsonString(app_name)
try:
    rsi = init( jsonCfg )
except json.decoder.JSONDecodeError as jex:
    sys.stderr.write("load_json_config JSONdecode :%s" % jex)
    exit(-1)

setLogLevel(DEBUG)
ev = rsi[1]

server_host_name = configGetItem("server", "listen_address")
server_port = int(configGetItem("server", "listen_port_tcp"))
sr = ServerCore.listen(ev, server_host_name, server_port, 0)
Http.new(sr, app_name)
EncHttp.addProc(sr, "/enc_http")
Stream.addProcHttp(sr, "/stream")
StreamCtl.addProcHttp(sr, "/stream_ctl")

ev.start()

MyAuthCmd.init()

print(app_name+" v0.1 runned on port "+str(server_port))

rc = ev.wait()
deinit()
