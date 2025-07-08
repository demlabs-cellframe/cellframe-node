#include "wrapping_dap_cluster_member.h"
#include "libdap-python.h"

PyTypeObject DapClusterMemberObjectType = DAP_PY_TYPE_OBJECT("DAP.Netowk.Member", sizeof(PyDapClusterMemberObject),
                                                             "Object member class");