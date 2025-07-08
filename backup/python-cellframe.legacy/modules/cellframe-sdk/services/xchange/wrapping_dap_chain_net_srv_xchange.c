#include "wrapping_dap_chain_net_srv_xchange.h"
#include "wrapping_dap_chain_net_srv_xchange_price.h"
#include "dap_chain_net_srv_xchange.h"
#include "dap_chain_wallet_python.h"
#include "libdap_chain_net_python.h"
#include "libdap-python.h"

PyMethodDef DapChainNetSrvXchangeMethods[] = {
        {
                "getOrders",
                wrapping_dap_chain_net_srv_xchange_get_orders,
                METH_VARARGS | METH_STATIC,
                        "The function receives a list of prices for exchange; if there are no prices, then an empty list is returned."},
        {
                "createOrder",
                wrapping_dap_chain_net_srv_xchange_create,
                METH_VARARGS | METH_STATIC,
                        "The function creates a base transaction and an exchange order."
        },
        {NULL, NULL, 0, NULL}
};

PyObject *wrapping_dap_chain_net_srv_xchange_get_orders(PyObject *self, PyObject *argv){
    (void)self;
    PyObject *obj_net;
    if (!PyArg_ParseTuple(argv, "O", &obj_net)) {
        return NULL;
    }
    dap_list_t *l_list_prices = dap_chain_net_srv_xchange_get_prices(((PyDapChainNetObject*)obj_net)->chain_net);
    size_t l_list_prices_count = dap_list_length(l_list_prices);
    dap_list_t *tmp = l_list_prices;
    PyObject *obj_list_price = PyList_New((Py_ssize_t)l_list_prices_count);
    for (size_t i = 0; i < l_list_prices_count; i++){
        dap_chain_net_srv_xchange_price_t *l_price = (dap_chain_net_srv_xchange_price_t*)tmp->data;
        PyDapChainNetSrvXchangeOrderObject *l_obj_price = PyObject_New(PyDapChainNetSrvXchangeOrderObject,
                                                                       &PyDapChainNetSrvXchangeOrderObjectType);
        l_obj_price->price = DAP_NEW(dap_chain_net_srv_xchange_price_t);
        memcpy(l_obj_price->price, l_price, sizeof(dap_chain_net_srv_xchange_price_t));
        PyList_Append(obj_list_price, (PyObject*)l_obj_price);
        Py_XDECREF(l_obj_price);
        tmp = tmp->next;
    }
    dap_list_free(l_list_prices);
    return obj_list_price;
}

PyObject *wrapping_dap_chain_net_srv_xchange_create(PyObject *self, PyObject *argv) {
    (void)self;
    PyObject *obj_net;
    const char *l_token_sell;
    const char *l_token_buy;
    PyObject *obj_value_sell;
    PyObject *obj_rate;
    PyObject *obj_fee;
    PyObject *obj_wallet;
    if (!PyArg_ParseTuple(argv, "OssOOOO", &obj_net, &l_token_sell, &l_token_buy, &obj_value_sell, &obj_rate, &obj_fee,
                          &obj_wallet)) {
        PyErr_SetString(PyExc_AttributeError, "Cant parse args");
        return NULL;
    }
    if (!PyDapChainNet_Check((PyDapChainNetObject *)obj_net)) {
        PyErr_SetString(PyExc_AttributeError, "The first parameter to the function passed an incorrect "
                                              "argument. This must be an instance of the dapchain net class.");
        return NULL;
    }
    if (!DapMathObject_Check(obj_value_sell)) {
        PyErr_SetString(PyExc_AttributeError, "The forth argument was passed incorrectly. This must be "
                                              "an instance of an object of type Math.");
        return NULL;
    }
    if (!DapMathObject_Check(obj_rate)) {
        PyErr_SetString(PyExc_AttributeError, "The fifth argument was passed incorrectly. This must be "
                                              "an instance of an object of type Math.");
        return NULL;
    }
    if (!DapMathObject_Check(obj_fee)) {
        PyErr_SetString(PyExc_AttributeError, "The sixth parameter to the function passed an incorrect "
                                              "argument. This must be an instance of the Wallet class.");
        return NULL;
    }
    if (!PyDapChainWalletObject_Check(obj_wallet)) {
        PyErr_SetString(PyExc_AttributeError, "The seventh parameter to the function passed an incorrect "
                                              "argument. This must be an instance of the Wallet class.");
        return NULL;
    }
    dap_chain_net_t *l_net  = ((PyDapChainNetObject*)obj_net)->chain_net;
    uint256_t l_value_sell  = ((DapMathObject*)obj_value_sell)->value;
    uint256_t l_rate        = ((DapMathObject*)obj_rate)->value;
    uint256_t l_fee         = ((DapMathObject*)obj_fee)->value;
    dap_chain_wallet_t *l_wallet = ((PyDapChainWalletObject*)obj_wallet)->wallet;
    char *l_hash_ret = NULL;
    int l_ret_code = dap_chain_net_srv_xchange_create(l_net, l_token_buy, l_token_sell, l_value_sell, l_rate, l_fee,
                                                      l_wallet, &l_hash_ret);
    switch (l_ret_code) {
        case XCHANGE_CREATE_ERROR_OK:{
            PyObject *l_obj_ret = Py_BuildValue("s", l_hash_ret);
            DAP_FREE(l_hash_ret);
            return l_obj_ret;
        }
        case XCHANGE_CREATE_ERROR_INVALID_ARGUMENT:{
            PyErr_SetString(CellFrame_Xchange_error, "One of the input arguments is not set correctly.");
            return NULL;
        }
        case XCHANGE_CREATE_ERROR_TOKEN_TICKER_SELL_IS_NOT_FOUND_LEDGER:{
            char *l_ret = dap_strdup_printf("The token ticker '%s', which is intended for sale, "
                                            "was not found in the ledger.", l_token_sell);
            PyErr_SetString(CellFrame_Xchange_error, l_ret);
            DAP_DELETE(l_ret);
            return NULL;
        }
        case XCHANGE_CREATE_ERROR_TOKEN_TICKER_BUY_IS_NOT_FOUND_LEDGER:{
            char *l_ret = dap_strdup_printf("The token ticker '%s', which is intended for buy, "
                                            "was not found in the ledger.", l_token_buy);
            PyErr_SetString(CellFrame_Xchange_error, l_ret);
            DAP_DELETE(l_ret);
            return NULL;
        }
        case XCHANGE_CREATE_ERROR_RATE_IS_ZERO:{
            PyErr_SetString(CellFrame_Xchange_error, "Rate is zero");
            return NULL;
        }
        case XCHANGE_CREATE_ERROR_FEE_IS_ZERO:{
            PyErr_SetString(CellFrame_Xchange_error, "Fee is zero");
            return NULL;
        }
        case XCHANGE_CREATE_ERROR_VALUE_SELL_IS_ZERO: {
            PyErr_SetString(CellFrame_Xchange_error, "Value sell is zero");
            return NULL;
        }
        case XCHANGE_CREATE_ERROR_INTEGER_OVERFLOW_WITH_SUM_OF_VALUE_AND_FEE:{
            PyErr_SetString(CellFrame_Xchange_error, "An overflow occurred when adding the transaction "
                                                     "value and commission.");
            return NULL;
        }
        case XCHANGE_CREATE_ERROR_NOT_ENOUGH_CASH_FOR_FEE_IN_SPECIFIED_WALLET:{
            PyErr_SetString(CellFrame_Xchange_error, "There are not enough token funds in the wallet to "
                                                     "create an fee.");
            return NULL;
        }
        case XCHANGE_CREATE_ERROR_NOT_ENOUGH_CASH_IN_SPECIFIED_WALLET:{
            PyErr_SetString(CellFrame_Xchange_error, "There are not enough token funds in the wallet to "
                                                     "create an exchange order.");
            return NULL;
        }
        case XCHANGE_CREATE_ERROR_MEMORY_ALLOCATED:{
            PyErr_SetString(CellFrame_Xchange_error, "Memory allocated");
            return NULL;
        }
        case XCHANGE_CREATE_ERROR_CAN_NOT_COMPOSE_THE_CONDITIONAL_TRANSACTION: {
            PyErr_SetString(CellFrame_Xchange_error, "Failed to create conditional exchange transaction.");
            return NULL;
        }
        case XCHANGE_CREATE_ERROR_CAN_NOT_PUT_TRANSACTION_TO_MEMPOOL: {
            PyErr_SetString(CellFrame_Xchange_error, "The created conditional exchange transaction "
                                                     "could not be posted to the mempool.");
            return NULL;
        }
        default: {
            char *l_ret = dap_strdup_printf("An error occurred with an unknown code: %d.", l_ret_code);
            PyErr_SetString(CellFrame_Xchange_error, l_ret);
            DAP_DELETE(l_ret);
            return NULL;
        }
    }
}


PyTypeObject DapChainNetSrvXchangeObjectType = DAP_PY_TYPE_OBJECT(
        "CellFrame.Service.Xchange",
        sizeof(PyDapChainNetSrvXchangeObject), "Object for work service xchange",
        .tp_methods = DapChainNetSrvXchangeMethods);
