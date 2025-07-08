import libDapServerCore as server

print ("Start wrapping libdap server core python module")
res_i = server.init(1, 0, "TestServer", "TestServer.txt")
rc = server.listen("0.0.0.0", 3307, 0)
server.deinit()
