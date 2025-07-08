#include "wrapping_dap_chain_datum_tx_voting.h"
#include "libdap-python.h"
#include "wrapping_dap_hash.h"
#include "datetime.h"

//Voting
#define PVT_VOTING(a) ((PyDapChainTXVotingObject*)a)->voting

PyGetSetDef PyDapChainTxVotingGetSetDef[] = {
        {"question", wrapping_dap_chain_tx_voting_get_question, NULL, NULL, NULL},
        {"answers", wrapping_dap_chain_tx_voting_get_answers, NULL, NULL, NULL},
        {"maxCountVote", wrapping_dap_chain_tx_voting_get_max_count, NULL, NULL, NULL},
        {"expire", wrapping_dap_chain_tx_voting_get_expire, NULL, NULL, NULL},
        {"isDelegateKeyRequired", wrapping_dap_chain_tx_voting_get_is_delegate_key_required, NULL, NULL, NULL},
        {"isVoteChangingAllowed", wrapping_dap_chain_tx_voting_get_is_vote_changing_allowed, NULL, NULL, NULL},
        {}
};

PyObject *wrapping_dap_chain_tx_voting_get_question(PyObject *self, void *closure){
    (void)closure;
    return Py_BuildValue("s", PVT_VOTING(self)->question);
}
PyObject *wrapping_dap_chain_tx_voting_get_answers(PyObject *self, void *closure){
    (void)closure;
    size_t l_option_count = dap_list_length(PVT_VOTING(self)->options);
    PyObject *obj_list = PyList_New(l_option_count);
    for (uint64_t i = l_option_count; --i;) {
        char *l_data = dap_list_nth_data(PVT_VOTING(self)->options, i);
        PyObject *obj_str = Py_BuildValue("s", l_data);
        PyList_SetItem(obj_list, i, obj_str);
    }
    return obj_list;
}
PyObject *wrapping_dap_chain_tx_voting_get_max_count(PyObject *self, void *closure){
    (void)closure;
    return Py_BuildValue("k", PVT_VOTING(self)->votes_max_count);
}
PyObject *wrapping_dap_chain_tx_voting_get_expire(PyObject *self, void *closure){
    (void)closure;
    if (PVT_VOTING(self)->voting_expire) {
        PyDateTime_IMPORT;
        PyObject *obj_ts_long =  Py_BuildValue("(k)", PVT_VOTING(self)->voting_expire);
        PyObject *obj_ts = PyDateTime_FromTimestamp(obj_ts_long);
        return obj_ts;
    }
    Py_RETURN_NONE;
}
PyObject *wrapping_dap_chain_tx_voting_get_is_delegate_key_required(PyObject *self, void *closure){
    (void)closure;
    if (PVT_VOTING(self)->delegate_key_required)
        Py_RETURN_TRUE;
    else
        Py_RETURN_FALSE;
}
PyObject *wrapping_dap_chain_tx_voting_get_is_vote_changing_allowed(PyObject *self, void *closure){
    (void)closure;
    if (PVT_VOTING(self)->vote_changing_allowed)
        Py_RETURN_TRUE;
    else
        Py_RETURN_FALSE;
}

PyTypeObject PyDapChainTxVotingObjectType = DAP_PY_TYPE_OBJECT(
        "CellFrame.Common.TxVoting",
        sizeof(PyDapChainTXVotingObject),
        "Wrapping item voting for transaction",
        .tp_getset = PyDapChainTxVotingGetSetDef);

//Vote

PyGetSetDef PyDapChainTxVoteGetSetDef[] = {
        {"hash", (getter) wrapping_dap_chain_tx_vote_get_hash, NULL, NULL, NULL},
        {"answerIdx", (getter) wrapping_dap_chain_tx_vote_get_answer_idx, NULL, NULL, NULL},
        {}
};

PyObject *wrapping_dap_chain_tx_vote_get_hash(PyObject *self, void *closure){
    (void)closure;
    PyDapHashFastObject *obj_hf = PyObject_New(PyDapHashFastObject, &DapHashFastObjectType);
    obj_hf->hash_fast = DAP_NEW(dap_hash_fast_t);
    memcpy(obj_hf->hash_fast, &((PyDapChainTXVoteObject*)self)->vote->voting_hash, sizeof(dap_hash_fast_t));
    obj_hf->origin = true;
    return (PyObject*)obj_hf;
}

PyObject *wrapping_dap_chain_tx_vote_get_answer_idx(PyObject *self, void *closure){
    (void)closure;
    return Py_BuildValue("k", ((PyDapChainTXVoteObject*)self)->vote->answer_idx);
}

PyTypeObject PyDapChainTXVoteObjectType = DAP_PY_TYPE_OBJECT(
        "CellFrame.Chain.TxVote",
        sizeof(PyDapChainTXVoteObject), "Wrapping item vote for transaction",
        .tp_getset = PyDapChainTxVoteGetSetDef);
