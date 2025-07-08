#include "wrapping_dap_chain_net_srv_vote_info.h"
#include "wrapping_dap_hash.h"

#define PVT(a) ((PyDapChainNetSrvVoteInfoObject*)a)->info
#define PVT_OPTION(a) ((PyDapChainNetSrvVoteInfoOptionObject*)a)->option

static PyGetSetDef DapChainNetSrvVoteInfoGetSet[] = {
        {"hash", wrapping_dap_chain_net_srv_vote_get_hash, NULL, NULL, NULL},
        {"question", wrapping_dap_chain_net_srv_vote_get_question, NULL, NULL, NULL},
        {"options", wrapping_dap_chain_net_srv_vote_get_options, NULL, NULL, NULL},
        {"expire", wrapping_dap_chain_net_srv_vote_get_expire_datetime, NULL, NULL, NULL},
        {"isDelegateKeyRequired", wrapping_dap_chain_net_srv_vote_get_is_delegate_key_required, NULL, NULL, NULL},
        {"isVoteChangingAllowed", wrapping_dap_chain_net_srv_vote_get_is_vote_changing_allowed, NULL, NULL, NULL},
        {}
};

void DapChainNetSrvVoteInfo_dealloc(PyDapChainNetSrvVoteInfoObject *self) {
    PyTypeObject *tp = Py_TYPE(self);
    dap_chain_net_voting_info_t *l_info = self->info;
    dap_chain_net_voting_info_free(l_info);
    tp->tp_free(self);
}

PyObject *wrapping_dap_chain_net_srv_vote_get_hash(PyObject *self, void *closure) {
    (void)closure;
    PyDapHashFastObject *obj = PyObject_New(PyDapHashFastObject, &DapChainHashFastObjectType);
    obj->hash_fast = DAP_NEW(dap_hash_fast_t);
    memcpy(obj->hash_fast, &PVT(self)->hash, sizeof(dap_hash_fast_t));
    return (PyObject*)obj;
}
PyObject *wrapping_dap_chain_net_srv_vote_get_question(PyObject *self, void *closure) {
    (void)closure;
    dap_chain_net_voting_info_t *l_info = PVT(self);
    if (!PVT(self)->question.question_str)
        Py_RETURN_NONE;
    char *l_str = dap_strup(l_info->question.question_str, l_info->question.question_size);
    PyObject *obj_str = Py_BuildValue("s", l_str);
    DAP_DELETE(l_str);
    return obj_str;
}
PyObject *wrapping_dap_chain_net_srv_vote_get_options(PyObject *self, void *closure) {
    (void)closure;
    Py_ssize_t l_count_option = PVT(self)->options.count_option;
    if (PVT(self)->options.count_option == 0) {
        Py_RETURN_NONE;
    }
    PyObject *obj_list = PyList_New(l_count_option);
    dap_chain_net_voting_option_info_t **l_infs = PVT(self)->options.options;
    for (Py_ssize_t i = l_count_option; i;) {
        PyDapChainNetSrvVoteInfoOptionObject *option  = PyObject_New(PyDapChainNetSrvVoteInfoOptionObject,
                                                                     &DapChainNetSrvVoteInfoOptionObjectType);
        i -= 1;
        dap_chain_net_voting_option_info_t * l_option = l_infs[i];
        option->option = l_option;
        PyList_SetItem(obj_list, i, (PyObject*)option);
    }
    return obj_list;
}
PyObject *wrapping_dap_chain_net_srv_vote_get_expire_datetime(PyObject *self, void *closure) {
    (void)closure;
    PyDateTime_IMPORT;
    PyDapChainNetSrvVoteInfoObject *l_info = (PyDapChainNetSrvVoteInfoObject*)self;
    uint64_t l_ts_expire = l_info->info->expired;
    PyObject *obj_ts_long =  Py_BuildValue("(k)", l_ts_expire);
    PyObject *obj_ts = PyDateTime_FromTimestamp(obj_ts_long);
    return obj_ts;
}
PyObject *wrapping_dap_chain_net_srv_vote_get_is_delegate_key_required(PyObject *self, void *closure) {
    (void)closure;
    bool delegate_key = PVT(self)->is_delegate_key_required;
    if (delegate_key)
        Py_RETURN_TRUE;
    else
        Py_RETURN_FALSE;
}
PyObject *wrapping_dap_chain_net_srv_vote_get_is_vote_changing_allowed(PyObject *self, void *closure) {
    (void)closure;
    bool vote_changing_allowed = PVT(self)->is_changing_allowed;
    if (vote_changing_allowed)
        Py_RETURN_TRUE;
    else
        Py_RETURN_FALSE;
}

PyTypeObject DapChainNetSrvVoteInfoObjectType = DAP_PY_TYPE_OBJECT(
        "CellFrame.Services.VoteInfo",
        sizeof(PyDapChainNetSrvVoteInfoObject),
        "CellFrame.Services.VoteInfo",
        .tp_dealloc = (destructor)DapChainNetSrvVoteInfo_dealloc,
        .tp_getset = DapChainNetSrvVoteInfoGetSet);

static PyGetSetDef DapChainNetSrvVoteInfoOptionGetSet[] = {
        {"description", wrapping_dap_chain_net_srv_vote_option_get_description, NULL, NULL, NULL},
        {"votes", wrapping_dap_chain_net_srv_vote_option_get_votes, NULL, NULL, NULL},
        {"weights", wrapping_dap_chain_net_srv_vote_option_get_weights, NULL, NULL, NULL},
        {"hashTxs", wrapping_dap_chain_net_srv_vote_option_txs, NULL, NULL, NULL},
        {}
};

PyObject *wrapping_dap_chain_net_srv_vote_option_get_description(PyObject *self, void *closure) {
    (void)closure;
    char *l_str = dap_strup(PVT_OPTION(self)->description, PVT_OPTION(self)->description_size);
    PyObject *obj_ret = Py_BuildValue("s",l_str);
    DAP_DELETE(l_str);
    return obj_ret;
}
PyObject *wrapping_dap_chain_net_srv_vote_option_get_votes(PyObject *self, void *closure) {
    (void)closure;
    return Py_BuildValue("k", PVT_OPTION(self)->votes_count);
}
PyObject *wrapping_dap_chain_net_srv_vote_option_get_weights(PyObject *self, void *closure) {
    (void)closure;
    DapMathObject *obj_weights = PyObject_New(DapMathObject, &DapMathObjectType);
    obj_weights->value = PVT_OPTION(self)->weight;
    return (PyObject*)obj_weights;
}

PyObject *wrapping_dap_chain_net_srv_vote_option_txs(PyObject *self, void *closure){
    (void)closure;
    dap_chain_net_voting_option_info_t *l_option = PVT_OPTION(self);
    PyObject *obj_list_tx = PyList_New(l_option->votes_count);
    dap_list_t *l_tmp = l_option->hashes_tx_votes;
    for (size_t i = 0; i < l_option->votes_count && l_tmp; i++) {
        dap_hash_fast_t *l_hf_tx = (dap_hash_fast_t*)l_tmp->data;
        PyDapHashFastObject *obj_hf = PyObject_New(PyDapHashFastObject, &DapChainHashFastObjectType);
        obj_hf->hash_fast = DAP_NEW(dap_chain_hash_fast_t);
        memcpy(obj_hf->hash_fast, l_hf_tx, sizeof(dap_hash_fast_t));
        obj_hf->origin = true;
        PyList_SetItem(obj_list_tx, i, (PyObject*)obj_hf);
        l_tmp = l_tmp->next;
    }
    return obj_list_tx;
}

PyTypeObject DapChainNetSrvVoteInfoOptionObjectType = DAP_PY_TYPE_OBJECT(
        "CellFrame.Services.VoteInfoOption",
        sizeof(PyDapChainNetSrvVoteInfoOptionObject),
        "CellFrame.Services.VoteInfoOption",
        .tp_getset = DapChainNetSrvVoteInfoOptionGetSet);

