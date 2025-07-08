#include "wrapping_dap_chain_tx_receipt.h"
#include "wrapping_cert.h"

#define LOG_TAG "wrapping_dap_chain_tx_receipt"

int PyDapChainTxReceipt_init(PyDapChainTXReceiptObject *self, PyObject *argv, PyObject *kwds);

static PyGetSetDef DapChainTxReceiptGetSetDefs[] = {
        {"size", (getter)wrapping_dap_chain_tx_receipt_get_size, NULL, NULL, NULL},
        {"extSize", (getter)wrapping_dap_chain_tx_receipt_get_ext_size, NULL, NULL, NULL},
        {"units", (getter)wrapping_dap_chain_tx_receipt_get_units, NULL, NULL, NULL},
        {"uid", (getter)wrapping_dap_chain_tx_receipt_get_uid, NULL, NULL, NULL},
        {"unitsType", (getter)wrapping_dap_chain_tx_receipt_get_units_type, NULL, NULL, NULL},
        {"value", (getter)wrapping_dap_chain_tx_receipt_get_value, NULL, NULL, NULL},
        {"provider", (getter)wrapping_dap_chain_tx_receipt_get_sig_provider, NULL, NULL, NULL},
        {"client", (getter)wrapping_dap_chain_tx_receipt_get_sig_client, NULL, NULL, NULL},
        {}
};

static PyMethodDef DapChainTxReceiptMethods[] = {
        {"sign", (PyCFunction)wrapping_dap_chain_tx_receipt_sign, METH_VARARGS, ""},
        {}
};

PyTypeObject DapChainTxReceiptObjectType = DAP_PY_TYPE_OBJECT(
        "CellFrame.ChainTxReceipt", sizeof(PyDapChainTXReceiptObject),
        "Chain tx item receipt object",
        .tp_methods = DapChainTxReceiptMethods,
        .tp_getset = DapChainTxReceiptGetSetDefs,
        .tp_init = (initproc)PyDapChainTxReceipt_init);

PyTypeObject DapChainTxReceiptOldObjectType = DAP_PY_TYPE_OBJECT(
        "CellFrame.ChainTxReceiptOld", sizeof(PyDapChainTXReceiptOldObject),
        "Chain tx item receipt old object",
        .tp_methods = DapChainTxReceiptMethods,
        .tp_getset = DapChainTxReceiptGetSetDefs,
        .tp_init = (initproc)PyDapChainTxReceipt_init);

PyObject *wrapping_dap_chain_tx_receipt_get_size(PyObject *self, void *closure){
    (void)closure;
    dap_chain_datum_tx_receipt_t *l_receipt = ((PyDapChainTXReceiptObject*)self)->tx_receipt;
    if (l_receipt->receipt_info.version < 2){
        dap_chain_datum_tx_receipt_old_t *l_receipt_old = (dap_chain_datum_tx_receipt_old_t*)l_receipt;
        return Py_BuildValue("H", l_receipt_old->size);
    } else {
        return Py_BuildValue("H", l_receipt->size);
    }
}
PyObject *wrapping_dap_chain_tx_receipt_get_ext_size(PyObject *self, void *closure){
    (void)closure;
    dap_chain_datum_tx_receipt_t *l_receipt = ((PyDapChainTXReceiptObject*)self)->tx_receipt;
    if (l_receipt->receipt_info.version < 2){
        dap_chain_datum_tx_receipt_old_t *l_receipt_old = (dap_chain_datum_tx_receipt_old_t*)l_receipt;
        return Py_BuildValue("H", l_receipt_old->exts_size);
    } else {
        return Py_BuildValue("H", l_receipt->exts_size);
    }
}
PyObject *wrapping_dap_chain_tx_receipt_get_units(PyObject *self, void *closure){
    (void)closure;
    dap_chain_datum_tx_receipt_t *l_receipt = ((PyDapChainTXReceiptObject*)self)->tx_receipt;
    if (l_receipt->receipt_info.version < 2){
        dap_chain_datum_tx_receipt_old_t *l_receipt_old = (dap_chain_datum_tx_receipt_old_t*)l_receipt;
        return Py_BuildValue("k", l_receipt_old->receipt_info.units);
    } else {
        return Py_BuildValue("k", l_receipt->receipt_info.units);
    }
}
PyObject *wrapping_dap_chain_tx_receipt_get_uid(PyObject *self, void *closure){
    (void)closure;
    dap_chain_datum_tx_receipt_t *l_receipt = ((PyDapChainTXReceiptObject*)self)->tx_receipt;
    if (l_receipt->receipt_info.version < 2){
        dap_chain_datum_tx_receipt_old_t *l_receipt_old = (dap_chain_datum_tx_receipt_old_t*)l_receipt;
        return Py_BuildValue("k", l_receipt_old->receipt_info.srv_uid.uint64);
    } else {
        return Py_BuildValue("k", l_receipt->receipt_info.srv_uid.uint64);
    }
}
PyObject *wrapping_dap_chain_tx_receipt_get_units_type(PyObject *self, void *closure){
    (void)closure;
    dap_chain_datum_tx_receipt_t *l_receipt = ((PyDapChainTXReceiptObject*)self)->tx_receipt;
    if (l_receipt->receipt_info.version < 2){
        dap_chain_datum_tx_receipt_old_t *l_receipt_old = (dap_chain_datum_tx_receipt_old_t*)l_receipt;
        return Py_BuildValue("s", dap_chain_srv_unit_enum_to_str(l_receipt_old->receipt_info.units_type.enm));
    } else {
        return Py_BuildValue("s", dap_chain_srv_unit_enum_to_str(l_receipt->receipt_info.units_type.enm));
    }
}
PyObject *wrapping_dap_chain_tx_receipt_get_value(PyObject *self, void *closure){
    (void)closure;
    dap_chain_datum_tx_receipt_t *l_receipt = ((PyDapChainTXReceiptObject*)self)->tx_receipt;
    if (l_receipt->receipt_info.version < 2){
        dap_chain_datum_tx_receipt_old_t *l_receipt_old = (dap_chain_datum_tx_receipt_old_t*)l_receipt;
        return Py_BuildValue("k", l_receipt_old->receipt_info.value_datoshi);
    } else {
        return Py_BuildValue("k", l_receipt->receipt_info.value_datoshi);
    }
}

PyObject *wrapping_dap_chain_tx_receipt_get_sig_provider(PyObject *self, void *closure){
    UNUSED(closure);
    dap_chain_datum_tx_receipt_t *l_receipt = ((PyDapChainTXReceiptObject*)self)->tx_receipt;
    if (l_receipt->receipt_info.version < 2){
        dap_chain_datum_tx_receipt_old_t *l_receipt_old = (dap_chain_datum_tx_receipt_old_t*)l_receipt;
        uint64_t l_signs_size = l_receipt_old->size - l_receipt_old->exts_size;
        if (l_signs_size) {
            dap_sign_t *l_sign = (dap_sign_t *)&l_receipt_old->exts_n_signs[l_receipt_old->exts_size];
            if ( dap_sign_verify_size(l_sign, l_signs_size) )
                Py_RETURN_NONE;
            PyObject  *obj_sign_provider = PyDapSignObject_Cretae(l_sign);
            return (PyObject *)obj_sign_provider;
        }
    } else {
        uint64_t l_signs_size = l_receipt->size - l_receipt->exts_size;
        if (l_signs_size) {
            dap_sign_t *l_sign = (dap_sign_t *)&l_receipt->exts_n_signs[l_receipt->exts_size];
            if ( dap_sign_verify_size(l_sign, l_signs_size) )
                Py_RETURN_NONE;
            PyObject  *obj_sign_provider = PyDapSignObject_Cretae(l_sign);
            return (PyObject *)obj_sign_provider;
        }
    }
    Py_RETURN_NONE;
}

PyObject *wrapping_dap_chain_tx_receipt_get_sig_client(PyObject *self, void *closure){
    UNUSED(closure);
    dap_chain_datum_tx_receipt_t *l_receipt = ((PyDapChainTXReceiptObject*)self)->tx_receipt;
    if (l_receipt->receipt_info.version < 2){
        dap_chain_datum_tx_receipt_old_t *l_receipt_old = (dap_chain_datum_tx_receipt_old_t*)l_receipt;
        uint64_t l_signs_size = l_receipt_old->size - l_receipt_old->exts_size;
        if (l_signs_size) {
            dap_sign_t *l_sign = (dap_sign_t *)&l_receipt_old->exts_n_signs[l_receipt_old->exts_size];
            if ( dap_sign_verify_size(l_sign, l_signs_size) )
                Py_RETURN_NONE;
            size_t l_sign_size = dap_sign_get_size(l_sign);
            if (l_receipt_old->exts_size + l_sign_size >= l_receipt_old->size)
                Py_RETURN_NONE;
            l_sign = (dap_sign_t *)&l_receipt_old->exts_n_signs[l_receipt_old->exts_size + l_sign_size];
            if ( dap_sign_verify_size(l_sign, l_signs_size - l_sign_size) )
                Py_RETURN_NONE;
            PyObject *obj_sign_client = PyDapSignObject_Cretae(l_sign);
            return obj_sign_client;
        }
    } else {
        uint64_t l_signs_size = l_receipt->size - l_receipt->exts_size;
        if (l_signs_size) {
            dap_sign_t *l_sign = (dap_sign_t *)&l_receipt->exts_n_signs[l_receipt->exts_size];
            if ( dap_sign_verify_size(l_sign, l_signs_size) )
                Py_RETURN_NONE;
            size_t l_sign_size = dap_sign_get_size(l_sign);
            if (l_receipt->exts_size + l_sign_size >= l_receipt->size)
                Py_RETURN_NONE;
            l_sign = (dap_sign_t *)&l_receipt->exts_n_signs[l_receipt->exts_size + l_sign_size];
            if ( dap_sign_verify_size(l_sign, l_signs_size - l_sign_size) )
                Py_RETURN_NONE;
            PyObject *obj_sign_client = PyDapSignObject_Cretae(l_sign);
            return obj_sign_client;
        }
    }
    Py_RETURN_NONE;
}

PyObject *wrapping_dap_chain_tx_receipt_sign(PyObject *self, PyObject *sign) {
    PyCryptoCertObject *obj_cert;
    if (!PyArg_ParseTuple(sign, "O", &obj_cert)) {
        log_it(L_ERROR, "Certificate for receipt signing not provided");
        Py_RETURN_NONE;
    }
    if (!PyObject_TypeCheck(obj_cert, &DapCryptoCertObjectType)) {
        log_it(L_ERROR, "Certificate for receipt signing has invalid object type");
        Py_RETURN_NONE;
    }
    if (!obj_cert->cert || !obj_cert->cert->enc_key) {
        log_it(L_ERROR, "Certificate for receipt signing has no cert object or private key");
        Py_RETURN_NONE;
    }
    dap_chain_datum_tx_receipt_t *l_receipt = ((PyDapChainTXReceiptObject*)self)->tx_receipt;
    if (l_receipt->receipt_info.version < 2){
        log_it(L_ERROR, "Receipt version < 2 is deprecated.");
        Py_RETURN_NONE;
    }
    ((PyDapChainTXReceiptObject*)self)->tx_receipt = dap_chain_datum_tx_receipt_sign_add(l_receipt, obj_cert->cert->enc_key);
    return self;
}

int PyDapChainTxReceipt_init(PyDapChainTXReceiptObject *self, PyObject *argv, PyObject *kwds) {
    const char *kwlist[] = {
        "srv_uid",
        "units_type",
        "units",
        "value",
        "ext",
        "prev_tx_hash",
        NULL
    };
    PyObject *obj_srv_uid;
    PyObject *obj_units_type;
    uint64_t l_units;
    PyObject *obj_value;
    PyObject *obj_ext = NULL;
    PyObject *obj_prev_tx_hash = NULL;
    if (!PyArg_ParseTupleAndKeywords(argv, kwds, "OOKO|OO", (char **) kwlist, &obj_srv_uid, &obj_units_type, &l_units,
                                     &obj_value, &obj_ext, &obj_prev_tx_hash))
        return -1;
    if (!PyDapChainNetSrvUid_Check((PyDapChainNetSrvUIDObject*)obj_srv_uid)) {
        PyErr_SetString(PyExc_Exception, "The first argument is passed incorrectly, it should be an object of "
                                         "type CellFrame.Network.ServiceUID");
        return -1;
    }
    if (!PyDapChainNetSrvPriceUnitUidObject_Check(obj_units_type)) {
        PyErr_SetString(PyExc_Exception, "The second argument is passed incorrectly, it should be an object of "
                                         "type CellFrame.Network.ServicePriceUnitUID");
        return -1;
    }
    if (!DapMathObject_Check(obj_value)) {
        PyErr_SetString(PyExc_Exception, "The fourth argument is passed incorrectly, it should be an object of "
                                         "type DAP.Core.Math");
        return -1;
    }
    if (obj_prev_tx_hash) {
        PyErr_SetString(PyExc_Exception, "The sixth argument is passed incorrectly, it should be an object of "
                                            "type DAP.Core.HashFast.");
        return -1;
    }
    void *l_bytes = NULL;
    size_t l_bytes_size = 0;
    if (obj_ext) {
        if (!PyBytes_Check(obj_ext)) {
            PyErr_SetString(PyExc_Exception, "The fifth argument is passed incorrectly, it should be an object of "
                                             "type Bytes.");
            return -1;
        }
        l_bytes = PyBytes_AsString(obj_ext);
        l_bytes_size = PyBytes_Size(obj_ext);
    }
    self->tx_receipt = dap_chain_datum_tx_receipt_create(((PyDapChainNetSrvUIDObject*)obj_srv_uid)->net_srv_uid,
                                                         ((PyDapChainNetSrvPriceUnitUIDObject*)obj_units_type)->price_unit_uid,
                                                         l_units, ((DapMathObject*)obj_value)->value, l_bytes, l_bytes_size, ((PyDapHashFastObject*)obj_prev_tx_hash)->hash_fast);
    return 0;
}
