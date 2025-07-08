#include "Python.h"

typedef struct PyDapChainNetSrvVote{
	PyObject_HEAD
}PyDapChainNetSrvVoteObject;

static PyObject *DapChainNetSrvVoteError;

PyObject *wrapping_dap_chain_net_srv_vote_create(PyObject *self, PyObject *args);
PyObject *wrapping_dap_chain_net_srv_vote_list(PyObject *self, PyObject *args);
PyObject *wrapping_dap_chain_net_srv_vote(PyObject *self, PyObject *args);

extern PyTypeObject PyDapChainNetSrvVoteObjectType;

