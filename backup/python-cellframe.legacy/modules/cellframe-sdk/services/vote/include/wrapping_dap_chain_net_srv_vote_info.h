#include "Python.h"
#include "dap_chain_net_srv_voting.h"

typedef struct PyDapChainNetSrvVoteInfo{
    PyObject_HEAD
    dap_chain_net_voting_info_t *info;
}PyDapChainNetSrvVoteInfoObject;

typedef struct PyDapChainNetSrvVoteInfoOption{
    PyObject_HEAD
    dap_chain_net_voting_option_info_t *option;
}PyDapChainNetSrvVoteInfoOptionObject;

PyObject *wrapping_dap_chain_net_srv_vote_get_hash(PyObject *self, void *closure);
PyObject *wrapping_dap_chain_net_srv_vote_get_question(PyObject *self, void *closure);
PyObject *wrapping_dap_chain_net_srv_vote_get_options(PyObject *self, void *closure);
PyObject *wrapping_dap_chain_net_srv_vote_get_expire_datetime(PyObject *self, void *closure);
PyObject *wrapping_dap_chain_net_srv_vote_get_is_delegate_key_required(PyObject *self, void *closure);
PyObject *wrapping_dap_chain_net_srv_vote_get_is_vote_changing_allowed(PyObject *self, void *closure);

extern PyTypeObject DapChainNetSrvVoteInfoObjectType;

PyObject *wrapping_dap_chain_net_srv_vote_option_get_description(PyObject *self, void *closure);
PyObject *wrapping_dap_chain_net_srv_vote_option_get_votes(PyObject *self, void *closure);
PyObject *wrapping_dap_chain_net_srv_vote_option_get_weights(PyObject *self, void *closure);
PyObject *wrapping_dap_chain_net_srv_vote_option_txs(PyObject *self, void *closure);

extern PyTypeObject DapChainNetSrvVoteInfoOptionObjectType;

