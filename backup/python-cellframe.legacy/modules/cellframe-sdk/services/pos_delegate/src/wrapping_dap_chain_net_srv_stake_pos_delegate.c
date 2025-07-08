#include "wrapping_dap_chain_net_srv_stake_pos_delegate.h"
#include "libdap_chain_net_python.h"
#include "wrapping_dap_hash.h"
#include "wrapping_dap_stream_ch_chain_validator_test.h"
#include "dap_chain_net_srv_stake_pos_delegate.h"

int DapChainNetSrvStakePosDelegateObject_init(PyObject *self, PyObject *args, PyObject *kwds){
    const char *kwlist[] = {
            "net",
            NULL
    };
    PyObject* obj_net;
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "O", (char**)kwlist, &obj_net))
        return -1;
    ((PyDapChainNetSrvStakePosDelegateObject*)self)->net = ((PyDapChainNetObject*)obj_net)->chain_net;
    return 0;
}

PyObject *wrapping_dap_chain_net_srv_stake_check_validator(PyObject *self, PyObject *argv){
    (void)self;
    PyObject *obj_tx_hash;
    uint16_t time_connect;
    uint16_t time_response;
    if (!PyArg_ParseTuple(argv, "OHH", &obj_tx_hash, &time_connect, &time_response)) {
        return NULL;
    }
    if (!PyDapHashFast_Check((PyDapHashFastObject*)obj_tx_hash)) {
        PyErr_SetString(PyExc_AttributeError, "");
        return NULL;
    }
    dap_chain_ch_validator_test_t l_out = {0};
    bool res = dap_chain_net_srv_stake_check_validator(
            ((PyDapChainNetSrvStakePosDelegateObject *)self)->net,
            ((PyDapHashFastObject*)obj_tx_hash)->hash_fast,
            &l_out, time_connect, time_response);
    if (res)
        Py_RETURN_TRUE;
    else
        Py_RETURN_FALSE;
}

PyObject *wrapping_dap_chain_net_srv_stake_check_validator_full_info(PyObject *self, PyObject *argv){
    (void)self;
    PyObject *obj_tx_hash;
    uint16_t time_connect;
    uint16_t time_response;
    if (!PyArg_ParseTuple(argv, "OHH", &obj_tx_hash, &time_connect, &time_response)) {
        return NULL;
    }
    if (!PyDapHashFast_Check((PyDapHashFastObject*)obj_tx_hash)) {
        PyErr_SetString(PyExc_AttributeError, "");
        return NULL;
    }
    dap_chain_ch_validator_test_t l_out = {0};
    dap_chain_net_srv_stake_check_validator(
            ((PyDapChainNetSrvStakePosDelegateObject *)self)->net,
            ((PyDapHashFastObject*)obj_tx_hash)->hash_fast,
            &l_out, time_connect, time_response);
    PyDapStreamChChainValidatorTestObject *obj_rnd = PyObject_New(PyDapStreamChChainValidatorTestObject, &PyDapStreamChChainValidatorTestObjectType);
    obj_rnd->rnd = DAP_NEW_Z_SIZE(dap_chain_ch_validator_test_t, sizeof(dap_chain_ch_validator_test_t) + l_out.header.sign_size);
    memcpy(obj_rnd->rnd, &l_out, sizeof(dap_chain_ch_validator_test_t) + l_out.header.sign_size);
    return (PyObject*)obj_rnd;
}

PyObject *wrapping_dap_chain_net_srv_stake_get_count_validator(PyObject *self, void *closure) {
    (void)closure;
    size_t l_in_active_validators = 0;
    size_t l_total_validator = dap_chain_net_srv_stake_get_total_keys(
            ((PyDapChainNetSrvStakePosDelegateObject *)self)->net->pub.id, &l_in_active_validators);
    return Py_BuildValue("nn", l_total_validator, l_in_active_validators);
}

PyObject *wrapping_dap_chain_net_srv_stake_get_total_weight(PyObject *self, void *closure) {
    (void)closure;
    uint256_t total_weight = dap_chain_net_srv_stake_get_total_weight(
            ((PyDapChainNetSrvStakePosDelegateObject *)self)->net->pub.id, NULL);
    DapMathObject *obj_weight = PyObject_New(DapMathObject, &DapMathObjectType);
    obj_weight->value = total_weight;
    return (PyObject*)obj_weight;
}

static PyGetSetDef PyDapChainNetSrvStakePosDelegateGetsSets[] = {
        {"CountValidators", (getter)wrapping_dap_chain_net_srv_stake_get_count_validator, NULL, "", NULL},
        {"TotalWeight", (getter) wrapping_dap_chain_net_srv_stake_get_total_weight, NULL, "", NULL},
        {}
};

static PyMethodDef PyDapChainNetSrvStakePosDelegateMethods[] = {
        {
            "checkValidator",
            wrapping_dap_chain_net_srv_stake_check_validator,
            METH_VARARGS,
            ""
        },
        {
            "checkValidatorFullInfo",
            wrapping_dap_chain_net_srv_stake_check_validator_full_info,
            METH_VARARGS,
            ""
        },
        {}
};

PyTypeObject PyDapChainNetSrvStakePosDelegateObjectType = DAP_PY_TYPE_OBJECT(
            "CellFrame.Services.StakePosDelegate",
            sizeof(PyDapChainNetSrvStakePosDelegateObject),
            "CellFrame.Services.StakePosDelegate object",
            .tp_getset = PyDapChainNetSrvStakePosDelegateGetsSets,
            .tp_methods = PyDapChainNetSrvStakePosDelegateMethods,
            .tp_init = DapChainNetSrvStakePosDelegateObject_init
        );
