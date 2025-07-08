#include "wrapping_dap_mempool.h"
#include "dap_chain_wallet_python.h"
#include "python-cellframe_common.h"
#include "dap_chain_wallet_shared.h"
#include "dap_chain_datum_tx_items.h"
#include "dap_list.h"

#define LOG_TAG "python-mempool"

static PyMethodDef  DapMempoolMethods[] = {
        {"proc", dap_chain_mempool_proc_py, METH_VARARGS | METH_STATIC, ""},
        {"emissionPlace", wrapping_dap_mempool_emission_place, METH_VARARGS | METH_STATIC, ""},
        {"transactionPlace", wrapping_dap_mempool_transaction_place, METH_VARARGS | METH_STATIC, ""},
        
        {"emissionGet", dap_chain_mempool_emission_get_py, METH_VARARGS | METH_STATIC, ""},
        {"emissionExtract", dap_chain_mempool_datum_emission_extract_py, METH_VARARGS | METH_STATIC, ""},
        {"datumExtract", dap_chain_mempool_datum_extract_py, METH_VARARGS | METH_STATIC, ""},
        {"datumGet", dap_chain_mempool_datum_get_py, METH_VARARGS | METH_STATIC, ""},
        {"txCreate", dap_chain_mempool_tx_create_py, METH_VARARGS | METH_STATIC, ""},
        {"baseTxCreate", dap_chain_mempool_base_tx_create_py, METH_VARARGS | METH_STATIC, ""},
        {"txCreateCond", dap_chain_mempool_tx_create_cond_py, METH_VARARGS | METH_STATIC, ""},
        {"txCreateCondInput", dap_chain_mempool_tx_create_cond_input_py, METH_VARARGS | METH_STATIC, ""},
        {"remove", dap_chain_mempool_remove_py, METH_VARARGS | METH_STATIC, ""},
        {"list", dap_chain_mempool_list_py, METH_VARARGS | METH_STATIC, ""},
        {"addDatum", dap_chain_mempool_add_datum_py, METH_VARARGS | METH_STATIC, ""},
        {"txCreateMultisignWithdraw", dap_chain_mempool_tx_create_multisign_withdraw_py, METH_VARARGS | METH_STATIC, ""},
        {NULL,NULL,0,NULL}
};

PyTypeObject DapChainMempoolObjectType = DAP_PY_TYPE_OBJECT(
        "CellFrame.DapMempool", sizeof(PyDapMempoolObject),
        "Dap mempool object",
        .tp_methods = DapMempoolMethods);

PyObject *wrapping_dap_mempool_emission_place(PyObject *self, PyObject *args){
    (void)self;
    PyDapChainObject *obj_chain;
    PyDapChainDatumTokenEmissionObject *obj_emission;
    if (!PyArg_ParseTuple(args, "OO", &obj_chain, &obj_emission)){
        return NULL;
    }
    if (!PyDapChain_Check(obj_chain)){
        PyErr_SetString(PyExc_AttributeError, "The second argument was incorrectly passed to this "
                                              "function, the first argument must be an object of type "
                                              "CellFrame.Chain.Chain.");
        return NULL;
    }
    if (!PyDapChainDatumTokenEmissionObject_check((PyObject*)obj_emission)){
        PyErr_SetString(PyExc_AttributeError, "The second argument was incorrectly passed"
                                              " to this function, the second argument must be an object of "
                                              "type ChainDatumTokenEmission. ");
        return NULL;
    }
    size_t l_emission_size = dap_chain_datum_emission_get_size((uint8_t*)(obj_emission->token_emission));
    dap_chain_datum_t *l_datum = dap_chain_datum_create(
            DAP_CHAIN_DATUM_TOKEN_EMISSION,
            obj_emission->token_emission, l_emission_size);
    char *l_str = dap_chain_mempool_datum_add(l_datum, obj_chain->chain_t, "hex");
    if (l_str == NULL){
        Py_RETURN_NONE;
    }
    PyObject *l_str_obj = Py_BuildValue("s", l_str);
    DAP_DELETE(l_str);
    return l_str_obj;
}

PyObject *wrapping_dap_mempool_transaction_place(PyObject *self, PyObject *args){
    (void)self;
    PyDapChainObject *obj_chain;
    PyDapChainDatumTxObject *obj_tx;
    if (!PyArg_ParseTuple(args, "OO", &obj_chain, &obj_tx)){
        return NULL;
    }
    if (!PyDapChain_Check(obj_chain)){
        PyErr_SetString(PyExc_AttributeError, "The first argument was incorrectly passed to this "
                                              "function, the first argument must be an object of type "
                                              "CellFrame.Chain.Chain.");
        return NULL;
    }
    if (!DapChainDatumTx_Check((PyObject*)obj_tx)){
        PyErr_SetString(PyExc_AttributeError, "The second argument was incorrectly passed"
                                              " to this function, the second argument must be an object of "
                                              "type ChainDatumTx. ");
        return NULL;
    }

    size_t l_tx_size = dap_chain_datum_tx_get_size(obj_tx->datum_tx);
    dap_chain_datum_t *l_datum = dap_chain_datum_create(
            DAP_CHAIN_DATUM_TX,
            obj_tx->datum_tx, l_tx_size);

    char *l_str = dap_chain_mempool_datum_add(l_datum, obj_chain->chain_t, "hex");
    
    if (l_str == NULL){
        Py_RETURN_NONE;
    }
    
    PyObject *l_str_obj = Py_BuildValue("s", l_str);
    DAP_DELETE(l_str);
    return l_str_obj;
    
    Py_RETURN_NONE;
}

PyObject *dap_chain_mempool_emission_get_py(PyObject *self, PyObject * args){
    PyDapChainObject *obj_chain;
    char *l_emission_hash;
    if (!PyArg_ParseTuple(args, "Os", &obj_chain, &l_emission_hash)){
        return NULL;
    }
    if (!PyDapChain_Check(obj_chain)){
        PyErr_SetString(PyExc_AttributeError, "The first argument passed to the wrong function, the first"
                                              " argument must be an object of type Chain.");
        return NULL;
    }
    dap_chain_datum_token_emission_t *l_token = dap_chain_mempool_emission_get(
            obj_chain->chain_t, l_emission_hash);
    if (l_token == NULL){
        Py_RETURN_NONE;
    }
    PyDapChainDatumTokenEmissionObject *l_emi = PyObject_New(PyDapChainDatumTokenEmissionObject,
                                                             &DapChainDatumTokenEmissionObjectType);
    l_emi->token_emission = l_token;
    l_emi->token_size = dap_chain_datum_emission_get_size((uint8_t*)l_token);
    l_emi->copy = true;
    return (PyObject*)l_emi;
}

PyObject* dap_chain_mempool_datum_emission_extract_py(PyObject *self, PyObject *args){
    (void)self;
    PyDapChainObject *obj_chain;
    PyObject *obj_bytes;
    if (!PyArg_ParseTuple(args, "OO", &obj_chain, &obj_bytes)){
        return NULL;
    }
    if (!PyDapChain_Check(obj_chain)){
        PyErr_SetString(PyExc_AttributeError, "The first argument was not correctly passed to "
                                              "this function. The first argument must be an instance of an object of type Chain.");
        return NULL;
    }
    if (!PyBytes_Check(obj_bytes)){
        PyErr_SetString(PyExc_AttributeError, "The second argument of the function was passed incorrectly,"
                                              " this function takes an instance of an object of the bytes type as the "
                                              "second argument.");
        return NULL;
    }
    void *l_bytes = PyBytes_AsString(obj_bytes);
    size_t l_bytes_size = PyBytes_Size(obj_bytes);
    dap_chain_datum_token_emission_t *l_emi = dap_chain_mempool_datum_emission_extract(
            obj_chain->chain_t, l_bytes, l_bytes_size);
    if (l_emi == NULL){
        Py_RETURN_NONE;
    }
    PyDapChainDatumTokenEmissionObject *l_obj_emi = PyObject_New(PyDapChainDatumTokenEmissionObject,
                                                                 &DapChainDatumTokenEmissionObjectType);
    l_obj_emi->token_emission = l_emi;
    l_obj_emi->token_size = dap_chain_datum_emission_get_size((byte_t*)l_emi);
    l_obj_emi->copy = true;
    return (PyObject*)l_obj_emi;
}

PyObject *dap_chain_mempool_proc_py(PyObject *self, PyObject *args) {
    UNUSED(self);
    PyDapChainObject *obj_chain = NULL;
    char *l_hash_str = NULL;
    if (!PyArg_ParseTuple(args, "sO", &l_hash_str, &obj_chain)) {
        return NULL;
    }
    if (!PyDapChain_Check(obj_chain)) {
        char *l_str = "The second function argument is invalid, it must be an "
                                              "instance of an object of type CellFrame.Chain.Chain ";
        PyErr_SetString(PyExc_AttributeError, l_str);
        log_it(L_ERROR, "%s", l_str);
        return NULL;
    }
    dap_chain_t *l_chain = obj_chain->chain_t;
    dap_chain_net_t *l_net = dap_chain_net_by_id(l_chain->net_id);
    // If full or light it doesnt work
    if(dap_chain_net_get_role(l_net).enums>= NODE_ROLE_FULL){
        char *l_str = dap_strdup_printf("Need master node role or higher for network %s to process this command", l_net->pub.name);
        PyErr_SetString(PyExc_RuntimeError, l_str);
        log_it(L_ERROR, "%s", l_str);
        DAP_DELETE(l_str);
        return NULL;
    }

    char *l_gdb_group_mempool = NULL;
    l_gdb_group_mempool = dap_chain_mempool_group_new(l_chain);

    size_t l_datum_size = 0;
    dap_chain_datum_t *l_datum = (dap_chain_datum_t*) dap_global_db_get_sync(l_gdb_group_mempool,l_hash_str,
                                                              &l_datum_size, NULL, NULL);
    if (!l_datum){
        char *l_str = dap_strdup_printf("Failed to get data from chain %s on network %s using hash %s",
                                                                l_chain->name, l_net->pub.name, l_hash_str);
        PyErr_SetString(PyExc_AttributeError, l_str);
        return NULL;
        log_it(L_ERROR, "%s", l_str);
        DAP_DELETE(l_str);
        DAP_DELETE(l_gdb_group_mempool);
        return NULL;
    }
    size_t l_datum_size2 = l_datum ? dap_chain_datum_size(l_datum) : 0;
    if (l_datum_size != l_datum_size2) {
        char *l_str = dap_strdup_printf("Error! Corrupted datum %s, size by datum headers is %zu when in mempool is only %zu bytes",
                                       l_hash_str, l_datum_size2, l_datum_size);
        PyErr_SetString(PyExc_RuntimeError, l_str);
        log_it(L_ERROR, "%s", l_str);
        DAP_DELETE(l_str);
        DAP_DELETE(l_gdb_group_mempool);
        return NULL;
    }

    if (dap_chain_node_mempool_process(l_chain, l_datum, l_hash_str, NULL)) {
        bool res_del_mempool = dap_global_db_del(l_gdb_group_mempool, l_hash_str, NULL, NULL);
        if (res_del_mempool) {
            char *l_str = dap_strdup_printf("Warning! Can't delete datum with hash: %s from mempool!", l_hash_str);
            PyErr_SetString(PyExc_Warning, l_str);
            DAP_DELETE(l_str);
            return NULL;
        }
    }
    DAP_DELETE(l_gdb_group_mempool);
    Py_RETURN_NONE;
}

PyObject *dap_chain_mempool_base_tx_create_py(PyObject *self, PyObject *args){
    (void)self;
    PyDapChainObject *obj_chain, *obj_emi_chain;
    PyDapHashFastObject *obj_emi_hash;
    DapMathObject *obj_emission_value;
    char *l_ticker;
    PyDapChainAddrObject *obj_addr_to;
    PyObject *obj_wallet_or_cert;
    dap_enc_key_t *l_priv_key = NULL;
    DapMathObject *obj_value_fee;
    if (!PyArg_ParseTuple(args, "OOOOsOOO", &obj_chain, &obj_emi_hash, &obj_emi_chain, &obj_emission_value,
                          &l_ticker, &obj_addr_to, &obj_value_fee, &obj_wallet_or_cert)) {
        return NULL;
    }
    if (!PyDapChain_Check(obj_chain)){
        PyErr_SetString(PyExc_AttributeError, "The first argument was not correctly passed to "
                                              "this function. The first argument must be an instance of an object of type Chain. ");
        return NULL;
    }
    if (!PyDapHashFast_Check(obj_emi_hash)){
        PyErr_SetString(PyExc_AttributeError, "The second argument was not correctly passed to this "
                                              "function. The second argument must be an instance of a HashFast object"
                                              " containing the hash of the emission.");
        return NULL;
    }
    if (!PyDapChain_Check(obj_emi_chain)){
        PyErr_SetString(PyExc_AttributeError, "The third argument was not correctly passed to this "
                                              "function. The third argument must be an instance of an object of type "
                                              "Chain that contains the emission. ");
        return NULL;
    }
    if (!PyDapChainAddrObject_Check(obj_addr_to)){
        PyErr_SetString(PyExc_AttributeError, "The sixth argument was not correctly passed to this "
                                              "function. The sixth argument should be an instance of an object of type "
                                              "ChainAddr , which indicates which wallet address the underlying "
                                              "transaction should be made to. ");
        return NULL;
    }
    if (!PyObject_TypeCheck(obj_value_fee, &DapMathObjectType)) {
        PyErr_SetString(PyExc_AttributeError, "The seventh argument was not correctly passed to this "
                                              "function. The seventh argument must be an instance of an object of type "
                                              "DAP.Math that contains the fee for the underlying transaction.");
        return NULL;
    }
    
    if (PyDapChainWalletObject_Check(obj_wallet_or_cert)) 
        l_priv_key = dap_chain_wallet_get_key(((PyDapChainWalletObject*)obj_wallet_or_cert)->wallet, 0);
    else  if (PyDapCryptoCertObject_Check(obj_wallet_or_cert)) 
        l_priv_key = ((PyCryptoCertObject*)obj_wallet_or_cert)->cert->enc_key;
    else
    {
            PyErr_SetString(PyExc_AttributeError, "The eighth argument was passed incorrectly: "
                                                  "The eighth argument should be DapChainWallet or CryptoCert");
            return NULL;
    }
    
    uint256_t l_value_fee = ((DapMathObject*)obj_value_fee)->value;
    char *l_tx_hash_str = dap_chain_mempool_base_tx_create(
            obj_chain->chain_t, obj_emi_hash->hash_fast,
            obj_emi_chain->chain_t->id, obj_emission_value->value, l_ticker,
            obj_addr_to->addr, l_priv_key, "hex", l_value_fee);

    if (l_tx_hash_str == NULL)
        Py_RETURN_NONE;
    PyDapHashFastObject *l_obj_hf = PyObject_New(PyDapHashFastObject, &DapChainHashFastObjectType);
    l_obj_hf->hash_fast = DAP_NEW(dap_hash_fast_t);
    dap_chain_hash_fast_from_str(l_tx_hash_str, l_obj_hf->hash_fast);
    l_obj_hf->origin = true;
    DAP_DELETE(l_tx_hash_str);
    return (PyObject*)l_obj_hf;
}

#define DAP_LIST_SAPPEND(X, Y) X = dap_list_append(X,Y)


uint256_t *dap_chain_balance_from_pyobj(PyObject *obj, size_t *o_count) {
    log_it(L_NOTICE, "dap_chain_balance_from_pyobj");
    uint256_t *res = NULL;
    if (PyList_Check(obj)) {
        log_it(L_NOTICE, "dap_chain_balance_from_pyobj list");
        Py_ssize_t l_pos = 0;
        PyObject *l_item;
        *o_count = PyList_Size(obj);
        res = DAP_NEW_Z_COUNT(uint256_t, *o_count);
        if (!res) {
            PyErr_SetString(PyExc_MemoryError, "Memory allocation error");
            return NULL;
        }

        size_t l_pos_valid = 0;
        PyObject *iter;
        PyObject *item;
        if ((iter = PyObject_GetIter(obj)) == NULL) {
            PyErr_SetString(PyExc_TypeError, "List is Empty.");
            return NULL;
        }
        while ((item = PyIter_Next(iter)) != NULL) {
         
            if (!PyUnicode_Check(item)) {
                PyErr_SetString(PyExc_TypeError, "List must contain only string values");
                DAP_DELETE(res);
                return NULL;        
            }
            const char *l_str_value = PyUnicode_AsUTF8(item);
            *(res + l_pos_valid++) = dap_chain_balance_scan(l_str_value);
        }
    }
    else {
        if (!PyUnicode_Check(obj)) {
            PyErr_SetString(PyExc_TypeError, "Argument should be string type");
            return NULL;
        }
        res = DAP_NEW(uint256_t);
        if (!res) {
            PyErr_SetString(PyExc_MemoryError, "Memory allocation error");
            return NULL;
        }
        *res = dap_chain_balance_scan(PyBytes_AsString(obj));
        *o_count = 1;
    }
    return res;
}   


dap_chain_addr_t *dap_chain_addr_from_pyobj(PyObject *obj, size_t *o_count) {

    dap_chain_addr_t *res = NULL;

    if (PyList_Check(obj)) {
        Py_ssize_t l_pos = 0;
        *o_count = PyList_Size(obj);

        res = DAP_NEW_Z_COUNT(dap_chain_addr_t, *o_count);
    
        if (!res) {
            PyErr_SetString(PyExc_MemoryError, "Memory allocation error");
            return NULL;
        }
        size_t l_pos_valid = 0;

        PyObject *iter;
        PyDapChainAddrObject *item;
        if ((iter = PyObject_GetIter(obj)) == NULL) {
            PyErr_SetString(PyExc_TypeError, "List is Empty.");
            return NULL;
        }
        while ((item = (PyDapChainAddrObject *)PyIter_Next(iter)) != NULL) {
            if (!PyDapChainAddrObject_Check(item)) {
                PyErr_SetString(PyExc_TypeError, "List must contain only DapChainAddr objects");
                DAP_DELETE(res);
                return NULL;
            }
            *(res + l_pos_valid++) = *(item->addr);
            
        }

        if (l_pos_valid != (*o_count)) {
            PyErr_SetString(PyExc_ValueError, "Not DapChainAddr objects in list");
            DAP_DELETE(res);
            return NULL;
        }          
    }
    else {
        PyDapChainAddrObject *l_addr_obj = (PyDapChainAddrObject *)obj;
        if (!PyDapChainAddrObject_Check(l_addr_obj)) {
            PyErr_SetString(PyExc_TypeError, "Argument should be DapChainAddr type");
            return NULL;
        }
        *res = *(l_addr_obj->addr);
        *o_count = 1;
    }
    return res;
}   

PyObject *dap_chain_mempool_tx_create_multisign_withdraw_py(PyObject *self, PyObject *args) {

    PyDapChainNetObject *obj_net;
    PyDapHashFastObject * transaction_hash;
    PyObject *obj_addr_to;
    PyObject *value;
    char * fee;
    PyCryptoKeyObject *obj_key_from;
    PyObject *tsd;
    if (!PyArg_ParseTuple(args, "OOOOsOO", &obj_net, &transaction_hash, &obj_addr_to, &value, &fee, &obj_key_from, &tsd)){
        PyErr_SetString(PyExc_AttributeError, "Function takes exactly six arguments.");
        return NULL;
    }   

    if (!PyDapChainNet_Check(obj_net)){
        PyErr_SetString(PyExc_AttributeError, "The first argument was not correctly passed to "
                                              "this function. The first argument must be an instance of an object of type Net. ");
        return NULL;
    }

    if (!PyDapHashFast_Check(transaction_hash)){
        PyErr_SetString(PyExc_AttributeError, "Invalid second argument passed. The second argument must "
                                              "be an instance of an object of type DapHash. ");
        return NULL;
    }

    size_t l_value_count = 0;
    uint256_t *l_value_256 = dap_chain_balance_from_pyobj(value, &l_value_count);
    uint256_t l_value_fee_256 = dap_chain_balance_scan(fee);


    if (!dap_ledger_tx_find_by_hash(obj_net->chain_net->pub.ledger, transaction_hash->hash_fast)) {
        PyErr_SetString(PyExc_AttributeError, "Tx with provided hash not found");
        return NULL;
    }
    
    size_t l_addr_count = 0;
    dap_enc_key_t *l_enc_key =obj_key_from->key;
    dap_chain_addr_t *l_addr = dap_chain_addr_from_pyobj(obj_addr_to, &l_addr_count);
    dap_list_t *tsd_items = NULL;

    if (l_addr_count != l_value_count) {
        PyErr_SetString(PyExc_ValueError, "Number of addresses must match number of values");
        return NULL;
    }

    PyObject *tsdkey, *tsdvalue;
    Py_ssize_t pos = 0;
    
    while (PyDict_Next(tsd, &pos, &tsdkey, &tsdvalue))
    {
        dap_chain_tx_tsd_t *tsd_item = dap_chain_datum_tx_item_tsd_create(PyBytes_AsString(tsdvalue), PyLong_AsLong(tsdkey), PyBytes_Size(tsdvalue));
        if (!tsd_item) 
        {
            log_it(L_ERROR, "Can't add tsd");
            return NULL;
        }
        
        DAP_LIST_SAPPEND(tsd_items, tsd_item);
    } 

    dap_chain_datum_tx_t *l_tx = dap_chain_wallet_shared_taking_tx_create(NULL, obj_net->chain_net, l_enc_key, l_addr, l_value_256, l_addr_count,
                                                                                  l_value_fee_256, transaction_hash->hash_fast, tsd_items);
    
    if (!l_tx) {
        PyErr_SetString(PyExc_AttributeError, "Failed to create tx datum");
        return NULL;
    }
    size_t l_tx_size = dap_chain_datum_tx_get_size(l_tx);

    // Pack transaction into the datum
    dap_chain_t * l_chain = dap_chain_net_get_chain_by_name(obj_net->chain_net, "main");
    dap_chain_datum_t * l_datum_tx = dap_chain_datum_create(DAP_CHAIN_DATUM_TX, l_tx, l_tx_size);
    dap_chain_datum_tx_delete(l_tx);

    char *l_ret = dap_chain_mempool_datum_add(l_datum_tx, l_chain, "hex");;
    DAP_DELETE(l_datum_tx);

    PyDapHashFastObject *l_obj_hf = PyObject_New(PyDapHashFastObject, &DapChainHashFastObjectType);
    l_obj_hf->hash_fast = DAP_NEW(dap_hash_fast_t);
    dap_chain_hash_fast_from_str(l_ret, l_obj_hf->hash_fast);
    l_obj_hf->origin = true;
    
    return (PyObject*)l_obj_hf;
}

PyObject *dap_chain_mempool_tx_create_py(PyObject *self, PyObject *args){
    (void)self;
    PyObject *obj_chain;
    PyObject *obj_key_from;
    PyObject *obj_addr_from;
    PyObject *obj_addr_to;
    char *l_token_ticker;
    PyObject *l_value;
    char * l_value_fee;
    if (!PyArg_ParseTuple(args, "OOOOsOs", &obj_chain, &obj_key_from, &obj_addr_from, &obj_addr_to,
                          &l_token_ticker, &l_value, &l_value_fee)){
        return NULL;
    }
    dap_chain_t *l_chain = ((PyDapChainObject*)obj_chain)->chain_t;
    dap_enc_key_t *l_key_from = ((PyCryptoKeyObject*)obj_key_from)->key;

    size_t addr_from_count = 0;
    dap_chain_addr_t *l_addr_from = dap_chain_addr_from_pyobj(obj_addr_from, &addr_from_count); //can be array
    
    size_t addr_to_count = 0;
    const dap_chain_addr_t *l_addr_to = dap_chain_addr_from_pyobj(obj_addr_to, &addr_to_count);
    
    size_t l_value_count = 0;
    uint256_t *l_value_256 = dap_chain_balance_from_pyobj(l_value, &l_value_count);

    if (!l_addr_to || !l_value_256) {
        return NULL; //error already set
    }

    if (l_value_count != addr_to_count) {
        PyErr_SetString(PyExc_ValueError, "Number of values must match number of addresses");
        return NULL;
    }

    uint256_t l_value_fee_256 = dap_chain_balance_scan(l_value_fee);
    
    char *l_tx_hash_str = dap_chain_mempool_tx_create(l_chain, l_key_from,
                                                    l_addr_from, &l_addr_to,
                                                    l_token_ticker,
                                                    l_value_256, l_value_fee_256, "hex", l_value_count, 0);
    if (l_tx_hash_str == NULL)
        Py_RETURN_NONE;
    PyDapHashFastObject *l_obj_hf = PyObject_New(PyDapHashFastObject, &DapChainHashFastObjectType);
    l_obj_hf->hash_fast = DAP_NEW(dap_hash_fast_t);
    dap_chain_hash_fast_from_str(l_tx_hash_str, l_obj_hf->hash_fast);
    DAP_DELETE(l_tx_hash_str);
    l_obj_hf->origin = true;
    return (PyObject*)l_obj_hf;
}

PyObject *dap_chain_mempool_tx_create_cond_py(PyObject *self, PyObject *args){
    (void)self;
    PyDapChainNetObject *obj_net;
    PyObject* obj_key_from;
    PyObject* obj_key_cond;
    char *l_token_ticker;
    char* l_value;
    char* l_value_per_unit_max;
    PyObject *obj_unit;
    PyObject *obj_srv_uid;
    char* l_fee;
    PyObject *obj_cond;
    if (!PyArg_ParseTuple(args, "OOOsssOOsO", &obj_net, &obj_key_from, &obj_key_cond, &l_token_ticker, &l_value,
                          &l_value_per_unit_max, &obj_unit, &obj_srv_uid, &l_fee, &obj_cond)){
        PyErr_SetString(PyExc_AttributeError, "Function takes exactly ten arguments.");
        return NULL;
    }
    if (!PyDapChainNet_Check(obj_net)){
        PyErr_SetString(PyExc_AttributeError, "Invalid first argument passed. The first argument must "
                                              "be an instance of an object of type ChainNet. ");
        return NULL;
    }
    void *l_bytes_cond = PyBytes_AsString(obj_cond);
    size_t l_bytes_cond_size = PyBytes_Size(obj_cond);
    uint256_t l_value_256 = dap_chain_balance_scan(l_value);
    uint256_t l_value_per_unit_max_256 = dap_chain_balance_scan(l_value_per_unit_max);
    uint256_t l_fee_256  = dap_chain_balance_scan(l_fee);
    char *l_tx_hash_str = dap_chain_mempool_tx_create_cond(
            obj_net->chain_net,
            ((PyCryptoKeyObject*)obj_key_from)->key,
            ((PyDapPkeyObject *)obj_key_cond)->pkey,
            l_token_ticker,
            l_value_256,
            l_value_per_unit_max_256,
            ((PyDapChainNetSrvPriceUnitUIDObject*)obj_unit)->price_unit_uid,
            ((PyDapChainNetSrvUIDObject*)obj_srv_uid)->net_srv_uid,
            l_fee_256,
            l_bytes_cond,
            l_bytes_cond_size,
            "hex"
    );
    if (!l_tx_hash_str)
        Py_RETURN_NONE;
    PyDapHashFastObject *l_obj_hf = PyObject_New(PyDapHashFastObject, &DapChainHashFastObjectType);
    l_obj_hf->hash_fast = DAP_NEW(dap_hash_fast_t);
    dap_chain_hash_fast_from_str(l_tx_hash_str, l_obj_hf->hash_fast);
    DAP_DELETE(l_tx_hash_str);
    l_obj_hf->origin = true;
    return (PyObject*)l_obj_hf;
}

PyObject *dap_chain_mempool_tx_create_cond_input_py(PyObject *self, PyObject *args){
    (void)self;
    PyDapChainNetObject *obj_net;
    PyDapHashFastObject *obj_tx_prev_hash;
    PyObject *obj_addr_to;
    PyObject *obj_key_tx_sign;
    PyObject *obj_receipt;
    if (!PyArg_ParseTuple(args, "OOOOO", &obj_net, &obj_tx_prev_hash, &obj_addr_to, &obj_key_tx_sign, &obj_receipt)){
        PyErr_SetString(PyExc_AttributeError, "Function takes exactly five arguments.");
        return NULL;
    }
    if (!PyDapChainNet_Check(obj_net)) {
        PyErr_SetString(PyExc_AttributeError, "Invalid first argument passed. The first argument must "
                                              "be an instance of an object of type ChainNet. ");
        return NULL;
    }
    if (!PyDapHashFast_Check(obj_tx_prev_hash)){
        PyErr_SetString(PyExc_AttributeError, "Invalid second argument passed. The first argument must "
                                              "be an instance of an object of type ChainNet. ");
        return NULL;
    }
    if (!PyDapSignObject_Check(obj_key_tx_sign)){
        PyErr_SetString(PyExc_AttributeError, "Invalid fourth argument passed. The first argument must "
                                              "be an instance of an object of type DapSign.");
        return NULL;
    }
    char *l_tx_hash_str = dap_chain_mempool_tx_create_cond_input(
            obj_net->chain_net,
            obj_tx_prev_hash->hash_fast,
            PY_DAP_CHAIN_ADDR(obj_addr_to),
            ((PyCryptoKeyObject*)obj_key_tx_sign)->key,
            ((PyDapChainTXReceiptObject*)obj_receipt)->tx_receipt,
            "hex", NULL);
    if (!l_tx_hash_str)
        Py_RETURN_NONE;
    PyDapHashFastObject *l_obj_hf = PyObject_New(PyDapHashFastObject, &DapChainHashFastObjectType);
    l_obj_hf->hash_fast = DAP_NEW(dap_hash_fast_t);
    dap_chain_hash_fast_from_str(l_tx_hash_str, l_obj_hf->hash_fast);
    DAP_DELETE(l_tx_hash_str);
    l_obj_hf->origin = true;
    return (PyObject*)l_obj_hf;
}

PyObject *dap_chain_mempool_remove_py(PyObject *self, PyObject *args){
    PyDapChainObject *obj_chain;
    char *l_str_hash = NULL;
    if (!PyArg_ParseTuple(args, "Os", &obj_chain, &l_str_hash)){
        return NULL;
    }
    if (!PyDapChain_Check(obj_chain)){
        PyErr_SetString(PyExc_AttributeError, "The first argument was not correctly passed to "
                                              "the function, the first argument must be an instance of an object of "
                                              "type Chain.");
        return NULL;
    }
    if (!obj_chain->chain_t){
        PyErr_SetString(PyExc_AttributeError, "The passed chain arguments are corrupted.");
        return NULL;
    }
    char *l_gdb_group_mempool = dap_chain_mempool_group_new(obj_chain->chain_t);
    if (!dap_global_db_del(l_gdb_group_mempool, l_str_hash, NULL, NULL)) {
        DAP_DELETE(l_gdb_group_mempool);
        Py_RETURN_TRUE;
    } else {
        DAP_DELETE(l_gdb_group_mempool);
        Py_RETURN_FALSE;
    }
}

PyObject* pvt_dap_chain_mempool_list(dap_chain_t *a_chain){
    PyObject *obj_dict = PyDict_New();
    char * l_gdb_group_mempool = dap_chain_mempool_group_new(a_chain);
    if (l_gdb_group_mempool){
        size_t l_objs_size = 0;
        dap_global_db_obj_t * l_objs = dap_global_db_get_all_sync(l_gdb_group_mempool, &l_objs_size);
        for (size_t i = 0; i < l_objs_size; i++){

        
            dap_chain_datum_t * l_datum =  DAP_NEW_SIZE(dap_chain_datum_t, l_objs[i].value_len);
            memcpy(l_datum, l_objs[i].value, l_objs[i].value_len);

            PyDapChainDatumObject *obj_datum = PyObject_New(PyDapChainDatumObject, &DapChainDatumObjectType);
            obj_datum->datum = l_datum;
            obj_datum->origin = true;
            PyDict_SetItemString(obj_dict, l_objs[i].key, (PyObject*)obj_datum);
            Py_XDECREF((PyObject*)obj_datum);
        }
        dap_global_db_objs_delete(l_objs, l_objs_size);
    }
    DAP_FREE(l_gdb_group_mempool);
    return obj_dict;
}

PyObject *dap_chain_mempool_list_py(PyObject *self, PyObject *args){
    (void)self;
    PyDapChainNetObject *obj_net;
    PyDapChainObject *obj_chain = NULL;
    if (!PyArg_ParseTuple(args, "O|O", &obj_net, &obj_chain)){
        return NULL;
    }
    if (!PyDapChainNet_Check(obj_net)){
        PyErr_SetString(PyExc_AttributeError, "The first argument was passed to the function incorrectly,"
                                              " the first argument must be an instance of an object of type ChainNet.");
        return NULL;
    }
    if (!obj_chain){
        dap_chain_t *l_chain_tmp;
        PyObject *obj_dict = PyDict_New();
        DL_FOREACH(obj_net->chain_net->pub.chains, l_chain_tmp){
            PyObject *obj_list_datum_from_chain = pvt_dap_chain_mempool_list(l_chain_tmp);
            Py_ssize_t l_pos = 0;
            PyObject *l_key, *l_value;
            while(PyDict_Next(obj_list_datum_from_chain, &l_pos, &l_key, &l_value)){
                PyDict_SetItem(obj_dict, l_key, l_value);
                Py_DECREF(l_value);
            }
        }
        return obj_dict;
    }else{
        if (!PyDapChain_Check(obj_chain)){
            PyErr_SetString(PyExc_AttributeError, "The second argument was passed to the function incorrectly, the "
                                                  "second argument must be an instance of an object of type Chain.");
            return NULL;
        }
        PyObject *obj_dict = pvt_dap_chain_mempool_list(obj_chain->chain_t);
        return obj_dict;
    }
}

PyObject *dap_chain_mempool_add_datum_py(PyObject *self, PyObject *args){
    (void)self;
    PyObject *obj_data;
    PyDapChainObject *obj_chain;
    if (!PyArg_ParseTuple(args, "OO", &obj_chain, &obj_data)){
        return NULL;
    }
    if (!PyDapChain_Check(obj_chain)){
        PyErr_SetString(PyExc_AttributeError, "The first argument was not passed correctly. "
                                              "The first argument must be instance of an object of type Chain.");
        return NULL;
    }
    dap_chain_datum_t *l_datum = NULL;
    if (DapChainDatumDecree_Check(obj_data)) {
        size_t l_data_size = dap_chain_datum_decree_get_size(((PyDapChainDatumDecreeObject*)obj_data)->decree);
        l_datum = DAP_NEW_Z_SIZE(dap_chain_datum_t, sizeof(dap_chain_datum_t) + l_data_size);
        l_datum->header.version_id = DAP_CHAIN_DATUM_VERSION;
        l_datum->header.ts_create = dap_time_now();
        l_datum->header.data_size = l_data_size;
        l_datum->header.type_id = DAP_CHAIN_DATUM_DECREE;
        memcpy(l_datum->data, ((PyDapChainDatumDecreeObject*)obj_data)->decree, l_data_size);
    }
    else if (DapChainDatumAnchor_Check(obj_data)) {
        size_t l_data_size = dap_chain_datum_anchor_get_size(((PyDapChainDatumAnchorObject*)obj_data)->anchor);
        l_datum = DAP_NEW_Z_SIZE(dap_chain_datum_t, sizeof(dap_chain_datum_t) + l_data_size);
        l_datum->header.version_id = DAP_CHAIN_DATUM_VERSION;
        l_datum->header.ts_create = dap_time_now();
        l_datum->header.data_size = l_data_size;
        l_datum->header.type_id = DAP_CHAIN_DATUM_ANCHOR;
        memcpy(l_datum->data, ((PyDapChainDatumAnchorObject*)obj_data)->anchor, l_data_size);
    }
    else if (DapChainDatumTx_Check(obj_data)) {
        size_t l_tx_size = dap_chain_datum_tx_get_size(((PyDapChainDatumTxObject*)obj_data)->datum_tx);
        l_datum = dap_chain_datum_create(DAP_CHAIN_DATUM_TX, ((PyDapChainDatumTxObject*)obj_data)->datum_tx, l_tx_size);
    }
    else if (PyDapChainDatum_Check(obj_data)) {
        l_datum = ((PyDapChainDatumObject*)obj_data)->datum;
        ((PyDapChainDatumObject*)obj_data)->origin = false;
    } else {
        PyErr_SetString(PyExc_AttributeError, "The second argument was not passed correctly. "
                                              "The second argument must be instance of an object of type"
                                              " Datum, DatumDecree, DatumAnchor.");
        return NULL;
    }
    char *l_str = dap_chain_mempool_datum_add(l_datum, obj_chain->chain_t, "hex");
    if (!l_str)
        return Py_BuildNone;
    PyObject *l_obj_ret = Py_BuildValue("s", l_str);
    DAP_DELETE(l_str);
    return l_obj_ret;
}


PyObject *dap_chain_mempool_datum_extract_py(PyObject *self, PyObject *args)
{
    (void)self;
    
    PyObject *obj_bytes;
    if (!PyArg_ParseTuple(args, "O", &obj_bytes)){
        return NULL;
    }
    
    if (!PyBytes_Check(obj_bytes)){
        PyErr_SetString(PyExc_AttributeError, "The first argument of the function was passed incorrectly,"
                                              " this function takes an instance of an object of the bytes type as the "
                                              "first argument.");
        return NULL;
    }
    void *l_bytes = PyBytes_AsString(obj_bytes);
    size_t l_bytes_size = PyBytes_Size(obj_bytes);
    
    dap_chain_datum_t * l_datum =  DAP_NEW_SIZE(dap_chain_datum_t, l_bytes_size);
    memcpy(l_datum, l_bytes, l_bytes_size);

    PyDapChainDatumObject *obj_datum = PyObject_New(PyDapChainDatumObject, &DapChainDatumObjectType);
    obj_datum->datum = l_datum;
    obj_datum->origin = true;
    
    return (PyObject *)obj_datum;
}

PyObject *dap_chain_mempool_datum_get_py(PyObject *self, PyObject *args)
{
      PyDapChainObject *obj_chain;
    char *l_emission_hash;
    if (!PyArg_ParseTuple(args, "Os", &obj_chain, &l_emission_hash)){
        return NULL;
    }
    if (!PyDapChain_Check(obj_chain)){
        PyErr_SetString(PyExc_AttributeError, "The first argument passed to the wrong function, the first"
                                              " argument must be an object of type Chain.");
        return NULL;
    }
    dap_chain_datum_t *l_datum = dap_chain_mempool_datum_get(
            obj_chain->chain_t, l_emission_hash);
    if (l_datum == NULL){
        Py_RETURN_NONE;
    }
    PyDapChainDatumObject *l_pydatum = PyObject_New(PyDapChainDatumObject,
                                                             &DapChainDatumObjectType);
    l_pydatum->datum = l_datum;
    l_pydatum->origin = true;
    return (PyObject*)l_pydatum;
}
