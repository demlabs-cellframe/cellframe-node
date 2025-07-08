from DAP.Core import logIt
from DAP.Core import NodeAddr
from DAP.Crypto import GUUID
from DAP.Network import ClusterRoles
from DAP.GlobalDB import Instance, Cluster, MemberRoles, DB

GUUID_DEFAULT  =  GUUID("0x064c4cb8e2af23f9623f0c75330f1cd2")

def cluster_notify(group, key, value, argv):
    logIt.att(f"group: {group}, key: {key} value: \'{value}\'")

def init():
    logIt.dap("Start testGDB plugin")
    member_addr = NodeAddr("9339::D537::1630::9839")
    default_instance = Instance()
    my_cluster = Cluster(default_instance, "testWDI", GUUID_DEFAULT, "*.WDI", 100, True, MemberRoles.USER, ClusterRoles.EMBEDDED)
    my_cluster.notifyAdd(cluster_notify, None)
    my_cluster.memberAdd(member_addr, MemberRoles.DEFAULT)
    logIt.notice(f"Member {member_addr} added")
    DB.set_sync("test1", "test.WDI", bytes("This test record", "UTF-8"))
    my_cluster.memberDelete(member_addr)
    logIt.notice(f"Member {member_addr} delleted")
    return 0