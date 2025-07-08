#include "Python.h"
#include "dap_chain_net.h"

typedef struct PyDapChainNetSrvStakePosDelegate{
    PyObject_HEAD
    dap_chain_net_t *net;
}PyDapChainNetSrvStakePosDelegateObject;

PyObject *wrapping_dap_chain_net_srv_stake_check_validator(PyObject *self, PyObject *argv);
PyObject *wrapping_dap_chain_net_srv_stake_check_validator_full_info(PyObject *self, PyObject *argv);
PyObject *wrapping_dap_chain_net_srv_stake_get_count_validator(PyObject *self, void *closure);
PyObject *wrapping_dap_chain_net_srv_stake_get_total_weight(PyObject *self, void *closure);

extern PyTypeObject PyDapChainNetSrvStakePosDelegateObjectType;
