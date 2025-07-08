#include "wrapping_dap_chain_datum_tx.h"
#include "dap_chain_datum_tx_sig.h"

#include "dap_chain_wallet_python.h"

/* DAP chain tx iter type */

static PyMethodDef PyDapChainTxItemTypeObjectMethods[] ={
        {"TX_ITEM_TYPE_IN", (PyCFunction)TX_ITEM_TYPE_IN_PY, METH_NOARGS | METH_STATIC, ""},
        {"TX_ITEM_TYPE_OUT", (PyCFunction)TX_ITEM_TYPE_OUT_PY, METH_NOARGS | METH_STATIC, ""},
        {"TX_ITEM_TYPE_PKEY", (PyCFunction)TX_ITEM_TYPE_PKEY_PY, METH_NOARGS | METH_STATIC, ""},
        {"TX_ITEM_TYPE_SIG", (PyCFunction)TX_ITEM_TYPE_SIG_PY, METH_NOARGS | METH_STATIC, ""},
        {"TX_ITEM_TYPE_IN_EMS", (PyCFunction)TX_ITEM_TYPE_IN_EMS_PY, METH_NOARGS | METH_STATIC, ""},
        {"TX_ITEM_TYPE_IN_COND", (PyCFunction)TX_ITEM_TYPE_IN_COND_PY, METH_NOARGS | METH_STATIC, ""},
        {"TX_ITEM_TYPE_OUT_COND", (PyCFunction)TX_ITEM_TYPE_OUT_COND_PY, METH_NOARGS | METH_STATIC, ""},
        {"TX_ITEM_TYPE_RECEIPT", (PyCFunction)TX_ITEM_TYPE_RECEIPT_PY, METH_NOARGS | METH_STATIC, ""},
        {"TX_ITEM_TYPE_RECEIPT_OLD", (PyCFunction)TX_ITEM_TYPE_RECEIPT_OLD_PY, METH_NOARGS | METH_STATIC, ""},
        {"TX_ITEM_TYPE_TSD", (PyCFunction)TX_ITEM_TYPE_TSD_PY, METH_NOARGS | METH_STATIC, ""},
        {}
};

PyTypeObject DapChainTxItemTypeObjectType = DAP_PY_TYPE_OBJECT(
        "CellFrame.Chain.TxItemType", sizeof(PyDapChainTxItemTypeObject),
        "Chain tx item type object",
        .tp_methods = PyDapChainTxItemTypeObjectMethods);

PyObject *TX_ITEM_TYPE_IN_PY(__attribute__((unused)) PyObject *self, __attribute__((unused)) PyObject *args)
{
    return PyLong_FromLong(TX_ITEM_TYPE_IN);
}
PyObject *TX_ITEM_TYPE_OUT_PY(__attribute__((unused)) PyObject *self, __attribute__((unused)) PyObject *args)
{
        return PyLong_FromLong(TX_ITEM_TYPE_OUT);
}
PyObject *TX_ITEM_TYPE_PKEY_PY(__attribute__((unused)) PyObject *self, __attribute__((unused)) PyObject *args)
{
        return PyLong_FromLong(TX_ITEM_TYPE_PKEY);
}
PyObject *TX_ITEM_TYPE_SIG_PY(__attribute__((unused)) PyObject *self, __attribute__((unused)) PyObject *args)
{
        return PyLong_FromLong(TX_ITEM_TYPE_SIG);
}
PyObject *TX_ITEM_TYPE_IN_EMS_PY(__attribute__((unused)) PyObject *self, __attribute__((unused)) PyObject *args)
{
        return PyLong_FromLong(TX_ITEM_TYPE_IN_EMS);
}
PyObject *TX_ITEM_TYPE_IN_COND_PY(__attribute__((unused)) PyObject *self, __attribute__((unused)) PyObject *args)
{
        return PyLong_FromLong(TX_ITEM_TYPE_IN_COND);
}
PyObject *TX_ITEM_TYPE_OUT_COND_PY(__attribute__((unused)) PyObject *self, __attribute__((unused)) PyObject *args)
{
        return PyLong_FromLong(TX_ITEM_TYPE_OUT_COND);
}
PyObject *TX_ITEM_TYPE_RECEIPT_PY(__attribute__((unused)) PyObject *self, __attribute__((unused)) PyObject *args)
{
        return PyLong_FromLong(TX_ITEM_TYPE_RECEIPT);
}
PyObject *TX_ITEM_TYPE_RECEIPT_OLD_PY(__attribute__((unused)) PyObject *self, __attribute__((unused)) PyObject *args)
{
        return PyLong_FromLong(TX_ITEM_TYPE_RECEIPT);
}
PyObject *TX_ITEM_TYPE_TSD_PY(__attribute__((unused)) PyObject *self, __attribute__((unused)) PyObject *args)
{
    return PyLong_FromLong(TX_ITEM_TYPE_TSD);
}

/* -------------------------------------- */

/* DAP chain datum tx */
static PyGetSetDef PyDaoChainDatumTxObjectGetsSets[] = {
        {"hash", (getter) wrapping_dap_chain_datum_tx_get_hash, NULL, NULL, NULL},
        {"dateCreated", (getter) wrapping_dap_chain_datum_tx_get_tsCreated, NULL, NULL, NULL},
        {}
};

static PyMethodDef PyDapChainDatumTxObjectMethods[] ={
        {"getSize", (PyCFunction)dap_chain_datum_tx_get_size_py, METH_VARARGS, ""},
        {"addItem", (PyCFunction)dap_chain_datum_tx_add_item_py, METH_VARARGS, ""},
        {"addInItem", (PyCFunction)dap_chain_datum_tx_add_in_item_py, METH_VARARGS, ""},
        {"addInCondItem", (PyCFunction)dap_chain_datum_tx_add_in_cond_item_py, METH_VARARGS, ""},
        {"addOutItem", (PyCFunction)dap_chain_datum_tx_add_out_item_py, METH_VARARGS, ""},
        {"addOutCond", (PyCFunction)dap_chain_datum_tx_add_out_cond_item_py, METH_VARARGS, ""},
        {"addSignItem", (PyCFunction)dap_chain_datum_tx_add_sign_item_py, METH_VARARGS, ""},
        {"appendSignItem", (PyCFunction)dap_chain_datum_tx_append_sign_item_py, METH_VARARGS, ""},
        {"verifySign", (PyCFunction)dap_chain_datum_tx_verify_sign_py, METH_VARARGS, ""},
        {"getItems", (PyCFunction)wrapping_dap_chain_datum_tx_get_items, METH_NOARGS, ""},
        {}
};

PyTypeObject DapChainDatumTxObjectType = {
        .ob_base = PyVarObject_HEAD_INIT(NULL, 0)
        .tp_name = "CellFrame.Common.DatumTx",
        .tp_basicsize = sizeof(PyDapChainDatumTxObject),
        .tp_doc = "Chain datum tx object",
        .tp_methods = PyDapChainDatumTxObjectMethods,
        .tp_getset = PyDaoChainDatumTxObjectGetsSets,
        .tp_new = PyDapChainDatumTxObject_create,
        .tp_dealloc = (destructor) PyDapChainDatumTxObject_delete
};

bool DapChainDatumTx_Check(PyObject *self){
    return PyObject_TypeCheck(self, &DapChainDatumTxObjectType);
}

PyObject *PyDapChainDatumTxObject_create(PyTypeObject *type_object, PyObject *args, PyObject *kwds){
    PyDapChainDatumTxObject *obj = (PyDapChainDatumTxObject*)PyType_GenericNew(type_object, args, kwds);
    obj->datum_tx = dap_chain_datum_tx_create();
    obj->original = true;
    return (PyObject *)obj;
}
void PyDapChainDatumTxObject_delete(PyDapChainDatumTxObject* datumTx){
    if (!datumTx->original) {
        dap_chain_datum_tx_delete(datumTx->datum_tx);
    }
    Py_TYPE(datumTx)->tp_free((PyObject*)datumTx);
}

PyObject *dap_chain_datum_tx_get_size_py(PyObject *self, PyObject *args){
    (void)args;
    size_t size = dap_chain_datum_tx_get_size(((PyDapChainDatumTxObject*)self)->datum_tx);
    return PyLong_FromSize_t(size);
}
PyObject *dap_chain_datum_tx_add_item_py(PyObject *self, PyObject *args){
    PyObject *obj_item;
    if (!PyArg_ParseTuple(args, "O", &obj_item))
        return NULL;
    void *l_item = NULL;
    if (PyObject_TypeCheck(obj_item, &DapChainTxInObjectType)) {
        l_item = ((PyDapChainTXInObject*)obj_item)->tx_in;
    } else if (PyObject_TypeCheck(obj_item, &DapChainTxInCondObjectType)) {
        l_item = ((PyDapChainTXInCondObject*)obj_item)->tx_in_cond;
    } else if (PyObject_TypeCheck(obj_item, &DapChainTxOutObjectType)) {
        l_item = ((PyDapChainTXOutObject*)obj_item)->tx_out;
    } else if (PyObject_TypeCheck(obj_item, &DapChainTxOutCondSubTypeSrvPayObjectType)) {
        l_item = ((PyDapChainTxOutCondObject*)obj_item)->out_cond;
    } else if (PyObject_TypeCheck(obj_item, &DapChainTxOutCondSubTypeSrvStakePosDelegateObjectType)) {
        l_item = ((PyDapChainTxOutCondObject*)obj_item)->out_cond;
    } else if (PyObject_TypeCheck(obj_item, &DapChainTxOutCondSubTypeSrvStakeLockObjectType)) {
        l_item = ((PyDapChainTxOutCondObject*)obj_item)->out_cond;
    } else if (PyObject_TypeCheck(obj_item, &DapChainTxOutCondSubTypeSrvXchangeObjectType)) {
        l_item = ((PyDapChainTxOutCondObject*)obj_item)->out_cond;
    } else if (PyObject_TypeCheck(obj_item, &DapChainTxOutExtObjectType)) {
        l_item = ((PyDapChainTXOutExtObject*)obj_item)->out_ext;
    } else if (PyObject_TypeCheck(obj_item, &DapChainTxReceiptObjectType)) {
        l_item = ((PyDapChainTXReceiptObject*)obj_item)->tx_receipt;
    } else if (PyObject_TypeCheck(obj_item, &DapChainTxReceiptOldObjectType)) {
        l_item = ((PyDapChainTXReceiptOldObject*)obj_item)->tx_receipt;
    } else if (PyObject_TypeCheck(obj_item, &DapChainTxTokenObjectType)) {
        l_item = ((PyDapChainTxTokenObject*)obj_item)->token;
    } else {
        PyErr_SetString(PyExc_Exception, "The addItem function is passed an object that is not supported for adding to the transaction.");
        return NULL;
    }
    int res = dap_chain_datum_tx_add_item(&(((PyDapChainDatumTxObject*)self)->datum_tx), l_item);
    if (res == 1)
        Py_RETURN_TRUE;
    else
        Py_RETURN_FALSE;
}

PyObject *dap_chain_datum_tx_sign_py(PyObject *self, PyObject *args){
    PyObject *obj;
    if (!PyArg_ParseTuple(args, "O", &obj))
        return NULL;
    dap_enc_key_t *l_enc_key = NULL;
    int res = 0;
    if (PyCryptoKeyObject_check(obj)) {
        res = dap_chain_datum_tx_add_sign_item(&((PyDapChainDatumTxObject*)self)->datum_tx, ((PyCryptoKeyObject*)obj)->key);
    } else if (PyDapChainWalletObject_Check(obj)) {
        dap_enc_key_t *l_key = dap_chain_wallet_get_key(((PyDapChainWalletObject*)obj)->wallet, 0);
        res = dap_chain_datum_tx_add_sign_item(&((PyDapChainDatumTxObject*)self)->datum_tx, l_key);
    } else if (PyDapCryptoCertObject_Check(obj)) {
        res = dap_chain_datum_tx_add_sign_item(&((PyDapChainDatumTxObject*)self)->datum_tx, ((PyCryptoCertObject*)obj)->cert->enc_key);
    } else {
        PyErr_SetString(PyExc_Exception, "An invalid object type was passed. The sign function accepts an "
                                         "instance with DAP.Crypto.Key or CellFrame.Chain.Wallet.");
        return NULL;
    }
    if (res == 1)
        Py_RETURN_TRUE;
    else
        Py_RETURN_FALSE;
}

PyObject *dap_chain_datum_tx_add_out_item_py(PyObject *self, PyObject *args){
    PyObject *in_addr;
    uint256_t value;
    if (!PyArg_ParseTuple(args, "O|k", &in_addr, &value))
        return NULL;
    int res = dap_chain_datum_tx_add_out_item(&(((PyDapChainDatumTxObject*)self)->datum_tx),
                                              ((PyDapChainAddrObject*)in_addr)->addr,
                                              value);
    return PyLong_FromLong(res);
}


PyObject *dap_chain_datum_tx_add_out_cond_item_py(PyObject *self, PyObject *args){
    PyObject *obj_key;
    PyObject *obj_srv_uid;
    uint256_t value;
    uint256_t value_max_per_unit;
    PyObject *obj_srv_price_unit_uid;
    PyObject *obj_cond_bytes;
    Py_ssize_t cond_size;
    if (!PyArg_ParseTuple(args, "O|O|k|k|O|O|n", &obj_key, &obj_srv_uid, &value, &value_max_per_unit,
                          &obj_srv_price_unit_uid, &obj_cond_bytes, &cond_size))
        return NULL;
    void *cond = (void*)PyBytes_AsString(obj_cond_bytes);
    int res = dap_chain_datum_tx_add_out_cond_item(&(((PyDapChainDatumTxObject*)self)->datum_tx),
                                                   ((PyDapPkeyObject*)obj_key)->pkey,
                                                   ((PyDapChainNetSrvUIDObject*)obj_srv_uid)->net_srv_uid,
                                                   value, value_max_per_unit,
                                                   ((PyDapChainNetSrvPriceUnitUIDObject*)obj_srv_price_unit_uid)->price_unit_uid,
                                                   cond, (size_t)cond_size);
    return PyLong_FromLong(res);
}

PyObject *dap_chain_datum_tx_add_in_item_py(PyObject *self, PyObject *args){
    PyObject *in_obj_hash_fast;
    uint32_t in_tx_out_pref_idx;
    if (!PyArg_ParseTuple(args, "O|I", &in_obj_hash_fast, &in_tx_out_pref_idx))
        return NULL;
    int res = dap_chain_datum_tx_add_in_item(&(((PyDapChainDatumTxObject*)self)->datum_tx),
                                             ((PyDapHashFastObject*)in_obj_hash_fast)->hash_fast,
                                             in_tx_out_pref_idx);
    return PyLong_FromLong(res);
}

PyObject *dap_chain_datum_tx_add_in_cond_item_py(PyObject *self, PyObject *args){
    PyObject *in_chain_hash_fast;
    unsigned int in_tx_out_prev_idx;
    unsigned int in_receipt_idx;
    if (!PyArg_ParseTuple(args, "O|I|I", &in_chain_hash_fast, &in_tx_out_prev_idx, &in_receipt_idx))
        return NULL;
    int res = dap_chain_datum_tx_add_in_cond_item(&(((PyDapChainDatumTxObject*)self)->datum_tx),
                                                  ((PyDapHashFastObject*)in_chain_hash_fast)->hash_fast,
                                                  in_tx_out_prev_idx,
                                                  in_receipt_idx);
    return PyLong_FromLong(res);
}


PyObject *dap_chain_datum_tx_add_sign_item_py(PyObject *self, PyObject *args){
    PyObject *obj_key;
    if (!PyArg_ParseTuple(args, "O", &obj_key))
        return NULL;
    int res = dap_chain_datum_tx_add_sign_item(&(((PyDapChainDatumTxObject*)self)->datum_tx),
                                               ((PyCryptoKeyObject*)obj_key)->key);
    return PyLong_FromLong(res);
}

PyObject *dap_chain_datum_tx_append_sign_item_py(PyObject *self, PyObject *args){
    PyDapSignObject *obj_sign;
    if (!PyArg_ParseTuple(args, "O", &obj_sign))
        return NULL;
    
    dap_chain_tx_sig_t *l_sign = dap_chain_tx_sig_create(obj_sign->sign);
    if (!l_sign) Py_RETURN_FALSE;

    if(dap_chain_datum_tx_add_item(&((PyDapChainDatumTxObject*)self)->datum_tx, l_sign))
        Py_RETURN_TRUE;
    
    Py_RETURN_FALSE;
}


PyObject *dap_chain_datum_tx_verify_sign_py(PyObject *self, PyObject *args){
    (void)args;
    int res = dap_chain_datum_tx_verify_sign(((PyDapChainDatumTxObject*)self)->datum_tx, 0);
    return PyLong_FromLong(res);
}

PyObject *wrapping_dap_chain_datum_tx_get_hash(PyObject *self, void* closure){
    (void)closure;
    PyDapHashFastObject *obj_hash_fast = PyObject_New(PyDapHashFastObject, &DapChainHashFastObjectType);
    obj_hash_fast->hash_fast = DAP_NEW(dap_chain_hash_fast_t);
    dap_hash_fast(((PyDapChainDatumTxObject*)self)->datum_tx,
                  dap_chain_datum_tx_get_size(((PyDapChainDatumTxObject*)self)->datum_tx),
                  obj_hash_fast->hash_fast);
    obj_hash_fast->origin = true;
    return  (PyObject*)obj_hash_fast;
}
PyObject *wrapping_dap_chain_datum_tx_get_tsCreated(PyObject *self, void* closure){
    (void)closure;
    PyObject *obj_ts_float = PyLong_FromLong(((PyDapChainDatumTxObject*)self)->datum_tx->header.ts_created);
    PyObject *obj_ts = Py_BuildValue("(O)", obj_ts_float);
    PyDateTime_IMPORT;
    PyObject *obj_dt = PyDateTime_FromTimestamp(obj_ts);
    return obj_dt;
}

PyObject *wrapping_dap_chain_datum_tx_get_items(PyObject *self, PyObject *args){
    (void)args;
    uint32_t l_tx_items_count = 0;
    uint32_t l_tx_items_size = ((PyDapChainDatumTxObject*)self)->datum_tx->header.tx_items_size;
    PyObject *obj_list = PyList_New(0);
    uint64_t l_out_idx = 0;
    dap_hash_fast_t l_tx_hf;
    dap_hash_fast(((PyDapChainDatumTxObject*)self)->datum_tx,
                  dap_chain_datum_tx_get_size(((PyDapChainDatumTxObject*)self)->datum_tx),
                  &l_tx_hf);
    while(l_tx_items_count < l_tx_items_size){
        uint8_t *item = ((PyDapChainDatumTxObject*)self)->datum_tx->tx_items + l_tx_items_count;
        size_t l_tx_item_size = dap_chain_datum_item_tx_get_size(item, 0);
        if (l_tx_item_size == 0) {
            Py_DECREF(obj_list);       
            PyObject *empty_list = PyList_New(0);
            return empty_list;
        }
        PyObject *obj_tx_item = NULL;
        switch (*item) {
            case TX_ITEM_TYPE_IN:
                obj_tx_item = (PyObject*)PyObject_New(PyDapChainTXInObject, &DapChainTxInObjectType);
                ((PyDapChainTXInObject*)obj_tx_item)->tx_in = ((dap_chain_tx_in_t*)item);
                break;
            case TX_ITEM_TYPE_OUT:
                obj_tx_item = (PyObject*)PyObject_New(PyDapChainTXOutObject, &DapChainTxOutObjectType);
                ((PyDapChainTXOutObject*)obj_tx_item)->tx_out = ((dap_chain_tx_out_t*)item);
                ((PyDapChainTXOutObject*)obj_tx_item)->tx_hash = DAP_NEW(dap_hash_fast_t);
                memcpy(((PyDapChainTXOutObject*)obj_tx_item)->tx_hash, &l_tx_hf, sizeof(dap_hash_fast_t));
                ((PyDapChainTXOutObject*)obj_tx_item)->idx = l_out_idx;
                l_out_idx++;
                break;
            case TX_ITEM_TYPE_IN_EMS:
                obj_tx_item = (PyObject*)PyObject_New(PyDapChainTxTokenObject, &DapChainTxTokenObjectType);
                ((PyDapChainTxTokenObject*)obj_tx_item)->token = (dap_chain_tx_in_ems_t*)item;
                break;
            case TX_ITEM_TYPE_SIG:
                obj_tx_item = (PyObject*)PyObject_New(PyDapChainTXSigObject, &DapChainTxSigObjectType);
                ((PyDapChainTXSigObject*)obj_tx_item)->tx_sig = (dap_chain_tx_sig_t*)item;
                break;
            case TX_ITEM_TYPE_RECEIPT:
                obj_tx_item = (PyObject*)PyObject_New(PyDapChainTXReceiptObject, &DapChainTxReceiptObjectType);
                ((PyDapChainTXReceiptObject*)obj_tx_item)->tx_receipt = (dap_chain_datum_tx_receipt_t*)item;
                break;
            case TX_ITEM_TYPE_RECEIPT_OLD:
                obj_tx_item = (PyObject*)PyObject_New(PyDapChainTXReceiptOldObject, &DapChainTxReceiptOldObjectType);
                ((PyDapChainTXReceiptOldObject*)obj_tx_item)->tx_receipt = (dap_chain_datum_tx_receipt_old_t*)item;
                break;
            case TX_ITEM_TYPE_PKEY:
                obj_tx_item = (PyObject*)PyObject_New(PyDapChainTXPkeyObject, &DapChainTxPkeyObjectType);
                ((PyDapChainTXPkeyObject*)obj_tx_item)->tx_pkey = ((dap_chain_tx_pkey_t*)item);
                break;
            case TX_ITEM_TYPE_IN_COND:
                obj_tx_item = (PyObject*)PyObject_New(PyDapChainTXInCondObject, &DapChainTxInCondObjectType);
                ((PyDapChainTXInCondObject*)obj_tx_item)->tx_in_cond = (dap_chain_tx_in_cond_t*)item;
                break;
            case TX_ITEM_TYPE_OUT_COND:
                switch (((dap_chain_tx_out_cond_t*)item)->header.subtype) {
                    case DAP_CHAIN_TX_OUT_COND_SUBTYPE_SRV_PAY:
                        obj_tx_item = (PyObject*)PyObject_New(PyDapChainTxOutCondObject, &DapChainTxOutCondSubTypeSrvPayObjectType);
                        ((PyDapChainTxOutCondObject*)obj_tx_item)->out_cond = ((dap_chain_tx_out_cond_t*)item);
                        break;
                    case DAP_CHAIN_TX_OUT_COND_SUBTYPE_SRV_STAKE_LOCK:
                        obj_tx_item = (PyObject*)PyObject_New(PyDapChainTxOutCondObject, &DapChainTxOutCondSubTypeSrvStakeLockObjectType);
                        ((PyDapChainTxOutCondObject*)obj_tx_item)->out_cond = ((dap_chain_tx_out_cond_t*)item);
                        break;
                    case DAP_CHAIN_TX_OUT_COND_SUBTYPE_SRV_STAKE_POS_DELEGATE:
                        obj_tx_item = (PyObject*)PyObject_New(PyDapChainTxOutCondObject, &DapChainTxOutCondSubTypeSrvStakePosDelegateObjectType);
                        ((PyDapChainTxOutCondObject*)obj_tx_item)->out_cond = ((dap_chain_tx_out_cond_t*)item);
                        break;
                    case DAP_CHAIN_TX_OUT_COND_SUBTYPE_SRV_XCHANGE:
                        obj_tx_item = (PyObject*)PyObject_New(PyDapChainTxOutCondObject, &DapChainTxOutCondSubTypeSrvXchangeObjectType);
                        ((PyDapChainTxOutCondObject*)obj_tx_item)->out_cond = ((dap_chain_tx_out_cond_t*)item);
                        break;
                    default:
                        obj_tx_item = (PyObject*)PyObject_New(PyDapChainTxOutCondObject, &DapChainTxOutCondObjectType);
                        ((PyDapChainTxOutCondObject*)obj_tx_item)->out_cond = ((dap_chain_tx_out_cond_t*)item);
                }
                dap_hash_fast_t *l_tx_hash_out = DAP_NEW(dap_hash_fast_t);
                memcpy(l_tx_hash_out, &l_tx_hf, sizeof(dap_hash_fast_t));
                ((PyDapChainTxOutCondObject*)obj_tx_item)->tx_hash = l_tx_hash_out;
                ((PyDapChainTxOutCondObject*)obj_tx_item)->idx = l_out_idx;
                l_out_idx++;
                break;
            case TX_ITEM_TYPE_OUT_EXT:
                obj_tx_item = (PyObject*)PyObject_New(PyDapChainTXOutExtObject, &DapChainTxOutExtObjectType);
                ((PyDapChainTXOutExtObject*)obj_tx_item)->out_ext = (dap_chain_tx_out_ext_t*)item;
                ((PyDapChainTXOutExtObject*)obj_tx_item)->tx_hash = l_tx_hf;
                ((PyDapChainTXOutExtObject*)obj_tx_item)->idx = l_out_idx;
                l_out_idx++;
                break;
            case TX_ITEM_TYPE_OUT_STD: {
                PyDapChainTXOutStdObject *obj_out = PyObject_New(PyDapChainTXOutStdObject, &DapChainTxOutStdObjectType);
                obj_out->out = (dap_chain_tx_out_std_t *)item;
                obj_out->tx_hash = l_tx_hf;
                obj_out->idx = l_out_idx++;
                obj_tx_item = (PyObject *)obj_out;
            } break;
            case TX_ITEM_TYPE_TSD:
                obj_tx_item = (PyObject*)PyObject_New(PyDapChainTxTSDObject, &DapChainTxTSDObjectType);
                ((PyDapChainTxTSDObject*)obj_tx_item)->tsd = (dap_chain_tx_tsd_t*)item;
                break;
            case TX_ITEM_TYPE_VOTE:
                obj_tx_item = (PyObject*) PyObject_New(PyDapChainTXVoteObject, &PyDapChainTXVoteObjectType);
                ((PyDapChainTXVoteObject*)obj_tx_item)->vote = (dap_chain_tx_vote_t*)item;
                break;
            case TX_ITEM_TYPE_VOTING:
                obj_tx_item = (PyObject*)PyObject_New(PyDapChainTXVotingObject, &PyDapChainTxVotingObjectType);
                ((PyDapChainTXVotingObject*)obj_tx_item)->voting = dap_chain_datum_tx_voting_parse_tsd(((PyDapChainDatumTxObject*)self)->datum_tx);
                break;
            default:
                obj_tx_item = Py_None;
                break;
        }
        PyList_Append(obj_list, obj_tx_item);
        if (obj_tx_item != Py_None)
            Py_XDECREF(obj_tx_item);
        l_tx_items_count += l_tx_item_size;
    }
    return obj_list;
}

/* -------------------------------------- */
