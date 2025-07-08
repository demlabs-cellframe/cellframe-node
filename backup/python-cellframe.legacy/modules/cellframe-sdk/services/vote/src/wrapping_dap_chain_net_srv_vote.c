#include "wrapping_dap_chain_net_srv_vote.h"
#include "dap_chain_net_srv_voting.h"
#include "dap_chain_net.h"
#include "math_python.h"
#include "datetime.h"
#include "dap_chain_wallet_python.h"
#include "libdap_chain_net_python.h"
#include "wrapping_dap_chain_net_srv_vote_info.h"

PyMethodDef DapChainNetSrvVoteMethods[] = {
        {"create", (PyCFunction)wrapping_dap_chain_net_srv_vote_create, METH_VARARGS | METH_STATIC, ""},
        {"vote", (PyCFunction)wrapping_dap_chain_net_srv_vote, METH_VARARGS | METH_STATIC, ""},
        {"list", (PyCFunction)wrapping_dap_chain_net_srv_vote_list, METH_VARARGS | METH_STATIC, ""},
        {NULL, NULL, 0, NULL}
};

PyObject *wrapping_dap_chain_net_srv_vote_create(PyObject *self, PyObject *args) {
    const char *question, *token = NULL;
    PyObject *obj_list_option;
    PyObject *obj_expire_option = NULL;
    unsigned long max_vote = 0;
    DapMathObject *fee;
    PyObject *obj_delegate_key_required = NULL;
    PyObject *obj_vote_changing_allowed = NULL;
    PyObject *obj_wallet;
    PyObject *obj_net;
    if (!PyArg_ParseTuple(args, "sOOOO|kOOOs", &question, &obj_list_option, &fee, &obj_wallet, &obj_net, &max_vote,
                          &obj_expire_option, &obj_vote_changing_allowed, &obj_delegate_key_required, &token))
        return NULL;
    if (!PyList_Check(obj_list_option)) {
        PyErr_SetString(DapChainNetSrvVoteError, "The second argument is incorrect. There should be a list of options.");
        return NULL;
    }
    if (!PyObject_TypeCheck(fee, &DapMathObjectType)) {
        PyErr_SetString(DapChainNetSrvVoteError, "The third argument is incorrect. There must be an instance of the "
                                                 "DapMath object.");
        return NULL;
    }
    if (!PyDapChainWalletObject_Check(obj_wallet)) {
        PyErr_SetString(DapChainNetSrvVoteError, "The fourth argument is incorrect. There must be an instance of the "
                                                 "Wallet object.");
        return NULL;
    }
    if (!PyDapChainNet_Check((PyDapChainNetObject*)obj_net)) {
        PyErr_SetString(DapChainNetSrvVoteError, "The fifth argument is incorrect. There must be an instance of the "
                                                 "CellFrame.Network.Net object.");
        return NULL;
    }
    dap_time_t l_time_expire_option = 0;
    if (obj_expire_option) {
        if (!PyDateTime_Check(obj_expire_option)) {
            PyErr_SetString(DapChainNetSrvVoteError,
                            "The sixth argument is incorrect. There must be an instance of the "
                            "DateTime object.");
            return NULL;
        }
        struct tm l_tm;
        l_tm.tm_sec = PyDateTime_DATE_GET_SECOND(obj_expire_option);
        l_tm.tm_min = PyDateTime_DATE_GET_MINUTE(obj_expire_option);
        l_tm.tm_hour = PyDateTime_DATE_GET_HOUR(obj_expire_option);
        l_tm.tm_mday = PyDateTime_GET_DAY(obj_expire_option);
        l_tm.tm_mon = PyDateTime_GET_MONTH(obj_expire_option);
        l_tm.tm_year = PyDateTime_GET_YEAR(obj_expire_option);
        time_t tmp = mktime(&l_tm);
        l_time_expire_option = (tmp <= 0) ? 0 : tmp;
    }
    if (obj_delegate_key_required) {
        if (PyBool_Check(obj_delegate_key_required)) {
            PyErr_SetString(DapChainNetSrvVoteError,
                            "The seventh argument is incorrect. There must be an instance of a "
                            "Boolean object.");
            return NULL;
        }
    }
    if (obj_vote_changing_allowed) {
        if (PyBool_Check(obj_vote_changing_allowed)) {
            PyErr_SetString(DapChainNetSrvVoteError, "The eighth argument is incorrect. There must be an instance of a "
                                                     "Boolean object.");
            return NULL;
        }
    }
    dap_list_t *l_option = NULL;
    for (int i = 0; i < PyList_Size(obj_list_option); i++) {
        PyObject *el = PyList_GetItem(obj_list_option, i);
        if (!PyUnicode_Check(el)) {
            dap_list_free(l_option);
            PyErr_SetString(DapChainNetSrvVoteError, "The list passed as the second argument does not contain a string.");
            return NULL;
        }
        Py_ssize_t l_value_size = 0;
        const char *value = PyUnicode_AsUTF8AndSize(el, &l_value_size);
        char *l_value = DAP_NEW_Z_SIZE(char, l_value_size);
        memcpy(l_value, value, sizeof(char) * l_value_size);
        l_option = dap_list_append(l_option, l_value);
    }
    dap_list_free(l_option);
    bool l_delegated_key_required = (obj_delegate_key_required == Py_True) ? true : false;
    bool l_vote_changing_allowed = (obj_vote_changing_allowed == Py_True) ? true : false;
    char *l_hash_ret;
    int res = dap_chain_net_srv_voting_create(question, l_option, obj_expire_option ? l_time_expire_option : 0, max_vote,
                              ((DapMathObject*)fee)->value, l_delegated_key_required, l_vote_changing_allowed,
                              ((PyDapChainWalletObject*)obj_wallet)->wallet, ((PyDapChainNetObject*)obj_net)->chain_net,
                              token, "hex", &l_hash_ret);
    switch (res) {
        case DAP_CHAIN_NET_VOTE_CREATE_OK: {
            PyObject *obj_ret = Py_BuildValue("s", l_hash_ret);
            DAP_DELETE(l_hash_ret);
            return obj_ret;
        } break;
        case DAP_CHAIN_NET_VOTE_CREATE_LENGTH_QUESTION_OVERSIZE_MAX: {
            char *l_ret = dap_strdup_printf("The question must contain no more than %d characters",
                                            DAP_CHAIN_DATUM_TX_VOTING_QUESTION_MAX_LENGTH);
            PyErr_SetString(DapChainNetSrvVoteError, l_ret);
            DAP_DELETE(l_ret);
            return NULL;
        } break;
        case DAP_CHAIN_NET_VOTE_CREATE_COUNT_OPTION_OVERSIZE_MAX: {
            char *l_ret = dap_strdup_printf("The voting can contain no more than %d options",
                                            DAP_CHAIN_DATUM_TX_VOTING_OPTION_MAX_COUNT);
            PyErr_SetString(DapChainNetSrvVoteError, l_ret);
            DAP_DELETE(l_ret);
            return NULL;
        } break;
        case DAP_CHAIN_NET_VOTE_CREATE_FEE_IS_ZERO: {
            PyErr_SetString(DapChainNetSrvVoteError, "The commission amount must be greater than zero");
            return NULL;
        } break;
        case DAP_CHAIN_NET_VOTE_CREATE_SOURCE_ADDRESS_IS_INVALID: {
            PyErr_SetString(DapChainNetSrvVoteError, "Failed to get address from wallet.");
            return NULL;
        } break;
        case DAP_CHAIN_NET_VOTE_CREATE_NOT_ENOUGH_FUNDS_TO_TRANSFER: {
            PyErr_SetString(DapChainNetSrvVoteError, "Not enough funds to transfer");
            return NULL;
        } break;
        case DAP_CHAIN_NET_VOTE_CREATE_MAX_COUNT_OPTION_EXCEEDED: {
            char *l_ret = dap_strdup_printf("The option must contain no more than %d characters",
                                            DAP_CHAIN_DATUM_TX_VOTING_OPTION_MAX_LENGTH);
            PyErr_SetString(DapChainNetSrvVoteError, l_ret);
            DAP_DELETE(l_ret);
            return NULL;
        } break;
        case DAP_CHAIN_NET_VOTE_CREATE_CAN_NOT_OPTION_TSD_ITEM: {
            PyErr_SetString(DapChainNetSrvVoteError, "Can't create option tsd item.");
            return NULL;
        } break;
        case DAP_CHAIN_NET_VOTE_CREATE_INPUT_TIME_MORE_CURRENT_TIME: {
            PyErr_SetString(DapChainNetSrvVoteError, "Can't create voting with expired time");
            return NULL;
        } break;
        case DAP_CHAIN_NET_VOTE_CREATE_CAN_NOT_CREATE_TSD_EXPIRE_TIME: {
            PyErr_SetString(DapChainNetSrvVoteError, "Can't create expired tsd item.");
            return NULL;
        } break;
        case DAP_CHAIN_NET_VOTE_CREATE_CAN_NOT_CREATE_TSD_DELEGATE_KEY: {
            PyErr_SetString(DapChainNetSrvVoteError, "Can't create delegated key req tsd item.");
            return NULL;
        } break;
        case DAP_CHAIN_NET_VOTE_CREATE_CAN_NOT_ADD_NET_FEE_OUT: {
            PyErr_SetString(DapChainNetSrvVoteError, "Can't add net fee out.");
            return NULL;
        } break;
        case DAP_CHAIN_NET_VOTE_CREATE_CAN_NOT_ADD_OUT_WITH_VALUE_BACK: {
            PyErr_SetString(DapChainNetSrvVoteError, "Can't add out with value back");
            return NULL;
        } break;
        case DAP_CHAIN_NET_VOTE_CREATE_CAN_NOT_SIGNED_TX: {
            PyErr_SetString(DapChainNetSrvVoteError, "Can not sign transaction");
            return NULL;
        } break;
        case DAP_CHAIN_NET_VOTE_CREATE_CAN_NOT_POOL_DATUM_IN_MEMPOOL: {
            PyErr_SetString(DapChainNetSrvVoteError, "Can not pool transaction in mempool");
            return NULL;
        } break;
        default: {
            char *l_ret = dap_strdup_printf("Unknown error. Code: %d", res);
            PyErr_SetString(DapChainNetSrvVoteError, l_ret);
            DAP_DELETE(l_ret);
            return NULL;
        }
    }
}

PyObject *wrapping_dap_chain_net_srv_vote_list(PyObject *self, PyObject *argv) {
    PyObject *obj_net;
    if (!PyArg_ParseTuple(argv, "O", &obj_net)) {
        return NULL;
    }
    if (!PyDapChainNet_Check((PyDapChainNetObject*)obj_net)) {
        return NULL;
    }

    dap_list_t *l_list = dap_chain_net_voting_list(((PyDapChainNetObject*)obj_net)->chain_net);
    if (!l_list) {
        Py_RETURN_NONE;
    }
    size_t l_list_count = dap_list_length(l_list);
    dap_list_t *l_ptr = l_list;
    PyObject *obj_list = PyList_New((Py_ssize_t)l_list_count);
    for (size_t i = 0; i < l_list_count; i++) {
        PyDapChainNetSrvVoteInfoObject *obj = PyObject_New(PyDapChainNetSrvVoteInfoObject, &DapChainNetSrvVoteInfoObjectType);
        obj->info = (dap_chain_net_voting_info_t*)l_ptr->data;
        PyList_SetItem(obj_list, (Py_ssize_t)i, (PyObject*)obj);
        l_ptr = l_ptr->next;
    }
    return obj_list;
}

PyObject *wrapping_dap_chain_net_srv_vote(PyObject *self, PyObject *args){
    (void)self;
    PyObject *obj_cert = NULL;
    PyObject *obj_fee;
    PyObject *obj_wallet;
    PyObject *obj_vote;
    unsigned long option_index;
    PyObject *obj_net;
    if (!PyArg_ParseTuple(args, "OkOOO|O", &obj_vote, &option_index, &obj_fee, &obj_wallet, &obj_net, &obj_cert))
        return NULL;
    if (!PyDapHashFast_Check((PyDapHashFastObject*)obj_vote) && !PyObject_TypeCheck(obj_vote, &DapChainNetSrvVoteInfoObjectType)) {
        PyErr_SetString(DapChainNetSrvVoteError, "The first argument is incorrect. "
                                                 "The first argument must be an object of type HashFast or VoteInfo.");
        return NULL;
    }
    if (!PyObject_TypeCheck(obj_fee, &DapMathObjectType)) {
        PyErr_SetString(DapChainNetSrvVoteError, "The third argument is incorrect. "
                                                 "The third argument must be an object of type DapMath.");
        return NULL;
    }
    if (!PyDapChainWalletObject_Check(obj_wallet)) {
        PyErr_SetString(DapChainNetSrvVoteError, "The fourth argument is incorrect. "
                                                 "The fourth argument must be an object of type Wallet.");
        return NULL;
    }
    if (!PyDapChainNet_Check((PyDapChainNetObject*)obj_net)) {
        PyErr_SetString(DapChainNetSrvVoteError, "The fifth argument is incorrect. "
                                                 "The fifth argument must be an object of type Net.");
        return NULL;
    }
    if (obj_cert && !PyDapCryptoCertObject_Check(obj_cert)) {
        PyErr_SetString(DapChainNetSrvVoteError, "The sixth argument is incorrect. "
                                                 "The sixth argument must be an object of type Cert.");
        return NULL;
    }
    dap_cert_t *l_cert = obj_cert ? ((PyCryptoCertObject*)obj_cert)->cert : NULL;
    dap_hash_fast_t *l_hf;
    if (PyDapHashFast_Check((PyDapHashFastObject*)obj_vote)) {
        l_hf = ((PyDapHashFastObject*)obj_vote)->hash_fast;
    } else {
        l_hf = &((PyDapChainNetSrvVoteInfoObject*)obj_vote)->info->hash;
    }
    char *l_hash_ret = NULL;
    int res = dap_chain_net_srv_vote_create(l_cert, ((DapMathObject*)obj_fee)->value,
                                        ((PyDapChainWalletObject*)obj_wallet)->wallet, l_hf, option_index,
                                        ((PyDapChainNetObject*)obj_net)->chain_net, "hex", &l_hash_ret);
    switch (res) {
        case DAP_CHAIN_NET_VOTE_VOTING_OK: {
            PyObject *obj_ret = Py_BuildValue("s", l_hash_ret);
            DAP_DELETE(l_hash_ret);
            return obj_ret;
        }
        case DAP_CHAIN_NET_VOTE_VOTING_CAN_NOT_FIND_VOTE: {
            PyErr_SetString(DapChainNetSrvVoteError, "Can't find voting");
            return NULL;
        }
        case DAP_CHAIN_NET_VOTE_VOTING_THIS_VOTING_HAVE_MAX_VALUE_VOTES: {
            PyErr_SetString(DapChainNetSrvVoteError, "This voting already received the required number of votes.");
            return NULL;
        }
        case DAP_CHAIN_NET_VOTE_VOTING_ALREADY_EXPIRED: {
            PyErr_SetString(DapChainNetSrvVoteError, "This voting already expired.");
            return NULL;
        }
        case DAP_CHAIN_NET_VOTE_VOTING_NO_KEY_FOUND_IN_CERT: {
            const char *l_cert_name = ((PyCryptoCertObject *) obj_cert)->cert->name;
            char *l_ret_err = dap_strdup_printf("Can't serialize public key of certificate \"%s\"", l_cert_name);
            PyErr_SetString(DapChainNetSrvVoteError, l_ret_err);
            DAP_DELETE(l_ret_err);
            return NULL;
        }
        case DAP_CHAIN_NET_VOTE_VOTING_KEY_IS_NOT_DELEGATED: {
            PyErr_SetString(DapChainNetSrvVoteError, "Your key is not delegated.");
            return NULL;
        }
        case DAP_CHAIN_NET_VOTE_VOTING_DOES_NOT_ALLOW_CHANGE_YOUR_VOTE: {
            PyErr_SetString(DapChainNetSrvVoteError, "The voting doesn't allow change your vote.");
            return NULL;
        }
        case DAP_CHAIN_NET_VOTE_VOTING_SOURCE_ADDRESS_INVALID: {
            PyErr_SetString(DapChainNetSrvVoteError, "source address is invalid");
            return NULL;
        }
        case DAP_CHAIN_NET_VOTE_VOTING_NOT_ENOUGH_FUNDS_TO_TRANSFER: {
            PyErr_SetString(DapChainNetSrvVoteError, "Not enough funds to transfer");
            return NULL;
        }
        case DAP_CHAIN_NET_VOTE_VOTING_UNSPENT_UTX0_FOR_PARTICIPATION_THIS_VOTING: {
            PyErr_SetString(DapChainNetSrvVoteError, "You have not unspent UTXO for participation in this voting.");
            return NULL;
        }
        case DAP_CHAIN_NET_VOTE_VOTING_INVALID_OPTION_INDEX: {
            PyErr_SetString(DapChainNetSrvVoteError, "Invalid option index.");
            return NULL;
        }
        case DAP_CHAIN_NET_VOTE_VOTING_CAN_NOT_CREATE_VOTE_ITEM: {
            PyErr_SetString(DapChainNetSrvVoteError, "Can't create vote item.");
            return NULL;
        }
        case DAP_CHAIN_NET_VOTE_VOTING_CAN_NOT_CREATE_TSD_TX_COND_ITEM: {
            PyErr_SetString(DapChainNetSrvVoteError, "Can't create tsd tx cond item.");
            return NULL;
        }
        case DAP_CHAIN_NET_VOTE_VOTING_CAN_NOT_ADD_NET_FEE_OUT: {
            PyErr_SetString(DapChainNetSrvVoteError, "Can't add net fee out.");
            return NULL;
        }
        case DAP_CHAIN_NET_VOTE_VOTING_CAN_NOT_ADD_OUT_WITH_VALUE_BACK: {
            PyErr_SetString(DapChainNetSrvVoteError, "Can't add out with value back");
            return NULL;
        }
        case DAP_CHAIN_NET_VOTE_VOTING_CAN_NOT_SIGN_TX: {
            PyErr_SetString(DapChainNetSrvVoteError, "Can't sign tx");
            return NULL;
        }
        case DAP_CHAIN_NET_VOTE_VOTING_CAN_NOT_POOL_IN_MEMPOOL: {
            PyErr_SetString(DapChainNetSrvVoteError, "Can't add datum to mempool");
            return NULL;
        }
        default: {
            char *l_ret_err = dap_strdup_printf("Undefined error code: %d", res);
            PyErr_SetString(DapChainNetSrvVoteError, l_ret_err);
            DAP_DELETE(l_ret_err);
            return NULL;
        }
    }
}

PyTypeObject PyDapChainNetSrvVoteObjectType = DAP_PY_TYPE_OBJECT(
        "CellFrame.Services.Vote",
        sizeof(PyDapChainNetSrvVoteObject),
        "CellFrame.Service.Vote",
        .tp_methods = DapChainNetSrvVoteMethods);

