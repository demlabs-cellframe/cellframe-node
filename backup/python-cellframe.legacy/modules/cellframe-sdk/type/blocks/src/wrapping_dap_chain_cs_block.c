#include "wrapping_dap_chain_cs_block.h"
#include "dap_chain_cs_blocks.h"

#define LOG_TAG "CS blocks wrapper"

static PyGetSetDef DapChainCsBlockGetsSetsDef[] = {
        {"hash", (getter)wrapping_dap_chain_block_get_hash, NULL, NULL, NULL},
        {"version", (getter)wrapping_dap_chain_block_get_version, NULL, NULL, NULL},
        {"cellId", (getter)wrapping_dap_chain_block_get_cell_id, NULL, NULL, NULL},
        {"chainId", (getter)wrapping_dap_chain_block_get_chain_id, NULL, NULL, NULL},
        {"created", (getter)wrapping_dap_chain_block_get_ts_created, NULL, NULL, NULL},
        {"metaData", (getter)wrapping_dap_chain_block_get_meta_data, NULL, NULL, NULL},
        {"datums", (getter)wrapping_dap_chain_block_get_datums, NULL, NULL, NULL},
        {"signs", (getter)wrapping_dap_chain_block_get_signs, NULL, NULL, NULL},
//        {"blockCache", (getter)wrapping_dap_chain_block_get_block_cache, NULL, NULL, NULL},
        {}
};

static PyMethodDef DapChainCsBlockMethods[] = {
        {"fromAtom", dap_chain_cs_block_get_atom, METH_VARARGS | METH_STATIC, ""},
        {"ledgerRetCode", wrapping_dap_chain_block_get_ledger_ret_code, METH_VARARGS | METH_STATIC, ""},
        {"byTxHash", wrapping_dap_chain_block_get_block_from_hash, METH_VARARGS | METH_STATIC, ""},
        {"getBlockSignersRewards", wrapping_dap_chain_cs_block_get_block_signers_rewards, METH_VARARGS, ""},
        {}
};

PyTypeObject DapChainCsBlockType = DAP_PY_TYPE_OBJECT(
        "CellFrame.Consensus.ChainCSBlock", sizeof(PyDapChainCSBlockObject),
        "Chain cs block objects",
        .tp_methods = DapChainCsBlockMethods,
        .tp_getset = DapChainCsBlockGetsSetsDef);

PyObject *wrapping_dap_chain_block_get_version(PyObject *self, void *closure){
    (void)closure;
    return Py_BuildValue("i", ((PyDapChainCSBlockObject*)self)->block->hdr.version);
}
PyObject *wrapping_dap_chain_block_get_cell_id(PyObject *self, void *closure){
    (void)closure;
    PyDapChainCellIDObject *obj_cell_id = PyObject_New(PyDapChainCellIDObject, &DapChainCellIdObjectType);
    obj_cell_id->cell_id = ((PyDapChainCSBlockObject*)self)->block->hdr.cell_id;
    return (PyObject*)obj_cell_id;
}
PyObject *wrapping_dap_chain_block_get_chain_id(PyObject *self, void *closure){
    (void)closure;
    PyDapChainIDObject *obj_chain_id = PyObject_New(PyDapChainIDObject, &DapChainIdObjectType);
    obj_chain_id->chain_id = &((PyDapChainCSBlockObject*)self)->block->hdr.chain_id;
    return (PyObject*)obj_chain_id;
}
PyObject *wrapping_dap_chain_block_get_ts_created(PyObject *self, void *closure){
    (void)closure;
    PyDateTime_IMPORT;
    PyObject *l_obj_long_ts = PyLong_FromLong((long)((PyDapChainCSBlockObject*)self)->block->hdr.ts_created);
    PyObject *l_obj_tuple = Py_BuildValue("(O)", l_obj_long_ts);
    PyObject *l_obj_dateTime = PyDateTime_FromTimestamp(l_obj_tuple);
    Py_XDECREF(l_obj_tuple);
    return l_obj_dateTime;
}
PyObject *wrapping_dap_chain_block_get_meta_data(PyObject *self, void *closure){
    (void)closure;
    dap_chain_hash_fast_t l_block_prev_hash = {0};
    dap_chain_hash_fast_t l_block_anchor_hash = {0};
    dap_chain_hash_fast_t l_merkle = {0};
    dap_chain_hash_fast_t *l_block_links = NULL;
    size_t l_block_links_count = 0;
    bool l_is_genesis = false;
    uint64_t l_nonce = {0}, l_nonce2 = {0};
    dap_chain_block_meta_extract(
            ((PyDapChainCSBlockObject*)self)->block, ((PyDapChainCSBlockObject*)self)->block_size,
            &l_block_prev_hash, &l_block_anchor_hash,
            &l_merkle, &l_block_links,
            &l_block_links_count, &l_is_genesis, &l_nonce, &l_nonce2, NULL);
    PyObject *obj_dict = PyDict_New();
    PyDapHashFastObject *l_obj_prev_hash = PyObject_New(PyDapHashFastObject, &DapChainHashFastObjectType);
    l_obj_prev_hash->hash_fast = DAP_NEW(dap_chain_hash_fast_t);
    if (!l_obj_prev_hash->hash_fast) {
        log_it(L_CRITICAL, "Memory allocation error");
        return NULL;
    }

    memcpy(l_obj_prev_hash->hash_fast, &l_block_prev_hash, sizeof(dap_chain_hash_fast_t));
    l_obj_prev_hash->origin = true;
    PyDict_SetItemString(obj_dict, "blockPrevHash", (PyObject*)l_obj_prev_hash);
    PyDapHashFastObject *l_obj_anchor_hash = PyObject_New(PyDapHashFastObject, &DapChainHashFastObjectType);
    l_obj_anchor_hash->hash_fast = DAP_NEW(dap_chain_hash_fast_t);
    if (!l_obj_anchor_hash->hash_fast) {
        log_it(L_CRITICAL, "Memory allocation error");
        DAP_DEL_Z(l_obj_prev_hash->hash_fast);
        return NULL;
    }

    memcpy(l_obj_anchor_hash->hash_fast, &l_block_anchor_hash, sizeof(dap_chain_hash_fast_t));
    l_obj_anchor_hash->origin = true;
    PyDict_SetItemString(obj_dict, "blockAnchorHash", (PyObject*)l_obj_anchor_hash);
    PyDapHashFastObject *l_obj_merkle = PyObject_New(PyDapHashFastObject, &DapChainHashFastObjectType);
    l_obj_merkle->hash_fast = DAP_NEW(dap_chain_hash_fast_t);
    if (!l_obj_merkle->hash_fast) {
        log_it(L_CRITICAL, "Memory allocation error");
        DAP_DEL_Z(l_obj_anchor_hash->hash_fast);
        DAP_DEL_Z(l_obj_prev_hash->hash_fast);
        return NULL;
    }

    memcpy(l_obj_merkle->hash_fast, &l_merkle, sizeof(dap_chain_hash_fast_t));
    l_obj_merkle->origin = true;
    PyDict_SetItemString(obj_dict, "merkle", (PyObject*)l_obj_merkle);
    // Get List links
    PyObject *obj_block_links = PyList_New((Py_ssize_t)l_block_links_count);
    for (size_t i = 0; i < l_block_links_count; i++){
        PyDapHashFastObject *obj_hf = PyObject_New(PyDapHashFastObject, &DapChainHashFastObjectType);
        obj_hf->hash_fast = DAP_NEW(dap_chain_hash_fast_t);
        if (!obj_hf->hash_fast) {
            log_it(L_CRITICAL, "Memory allocation error");
            DAP_DEL_Z(l_obj_merkle->hash_fast);
            DAP_DEL_Z(l_obj_anchor_hash->hash_fast);
            DAP_DEL_Z(l_obj_prev_hash->hash_fast);
            return NULL;
        }

        memcpy(obj_hf->hash_fast, &l_block_links[i], sizeof(dap_chain_hash_fast_t));
        obj_hf->origin = true;
        PyList_SetItem(obj_block_links, i, (PyObject*)obj_hf);
//        obj_hf->hash_fast = &(l_block_links[i]);
    }
    PyDict_SetItemString(obj_dict, "links", obj_block_links);
    if (l_is_genesis){
        PyDict_SetItemString(obj_dict, "isGenesis", Py_True);
    } else {
        PyDict_SetItemString(obj_dict, "isGenesis", Py_False);
    }
    PyObject *obj_nonce = Py_BuildValue("k", l_nonce);
    PyDict_SetItemString(obj_dict, "nonce", obj_nonce);
    PyObject *obj_nonce2 = Py_BuildValue("k", l_nonce2);
    PyDict_SetItemString(obj_dict, "nonce2", obj_nonce2);
    return obj_dict;
}
PyObject *wrapping_dap_chain_block_get_datums(PyObject *self, void *closure){
    (void)closure;
    size_t l_count = 0;
    dap_chain_datum_t **l_datums = dap_chain_block_get_datums(
            ((PyDapChainCSBlockObject*)self)->block,
            ((PyDapChainCSBlockObject*)self)->block_size, &l_count);
    if (l_count == 0){
        Py_RETURN_NONE;
    }
    PyObject *obj_datums = PyList_New(l_count);
    for (size_t i = 0; i < l_count; i++) {
        PyDapChainDatumObject *obj_datum = PyObject_New(PyDapChainDatumObject, &DapChainDatumObjectType);
        obj_datum->datum = l_datums[i];
        obj_datum->origin = false;
        PyList_SetItem(obj_datums, (Py_ssize_t) i, (PyObject *)obj_datum);
    }
    DAP_DELETE(l_datums);
    return obj_datums;
}
PyObject *wrapping_dap_chain_block_get_signs(PyObject *self, void *closure){
    (void)closure;
    size_t l_count = dap_chain_block_get_signs_count(((PyDapChainCSBlockObject*)self)->block,
                                                     ((PyDapChainCSBlockObject*)self)->block_size);
    PyObject *obj_list = PyList_New((Py_ssize_t)l_count);
    for (size_t i =0; i < l_count; i++){
        dap_sign_t *l_sign = dap_chain_block_sign_get(((PyDapChainCSBlockObject*)self)->block,
                                                     ((PyDapChainCSBlockObject*)self)->block_size, i);
        if (l_sign) {
            PyObject *obj_sign = PyDapSignObject_Cretae(l_sign);
            PyList_SetItem(obj_list, (Py_ssize_t)i, obj_sign);
        } else {
            PyList_SetItem(obj_list, (Py_ssize_t)i, Py_None);
            Py_IncRef(Py_None);
        }
    }
    return obj_list;
}

PyObject *wrapping_dap_chain_block_get_hash(PyObject *self, void *closure){
    (void)closure;
    PyDapHashFastObject *obj_hf = PyObject_New(PyDapHashFastObject, &DapChainHashFastObjectType);
    obj_hf->hash_fast = DAP_NEW(dap_chain_hash_fast_t);
    dap_hash_fast(((PyDapChainCSBlockObject*)self)->block,
                  ((PyDapChainCSBlockObject*)self)->block_size, obj_hf->hash_fast);
    obj_hf->origin = true;
    return (PyObject*)obj_hf;
}

PyObject* dap_chain_cs_block_get_atom(PyObject *self, PyObject *args){
    (void)self;
    PyObject *obj_atom_ptr;
    if (!PyArg_ParseTuple(args, "O", &obj_atom_ptr)){
        return NULL;
    }
    PyDapChainCSBlockObject *obj_block = PyObject_New(PyDapChainCSBlockObject, &DapChainCsBlockType);
    obj_block->block = (dap_chain_block_t *)((PyChainAtomObject*)obj_atom_ptr)->atom;
    obj_block->block_size =  ((PyChainAtomObject*)obj_atom_ptr)->atom_size;

    return (PyObject*)obj_block;
}

PyObject *wrapping_dap_chain_block_get_ledger_ret_code(PyObject *self, PyObject *argv){
    PyDapChainObject *chain;
    PyDapHashFastObject *obj_datum_hash;
    if (!PyArg_ParseTuple(argv, "OO", &chain, &obj_datum_hash)) {
        return NULL;
    }
    if (!PyDapChain_Check(chain)) {
        PyErr_SetString(PyExc_AttributeError, "The first argument is set incorrectly, it must be a "
                                              "network chain.");
        return NULL;
    }
    if (!PyDapHashFast_Check(obj_datum_hash)) {
        PyErr_SetString(PyExc_AttributeError, "The second argument is set incorrectly and must be an "
                                              "instance of a DapHashFast object.");
        return NULL;
    }
    int l_ledger_ret_code = 0;
    chain->chain_t->callback_datum_find_by_hash(chain->chain_t, obj_datum_hash->hash_fast, NULL, &l_ledger_ret_code);
    if (l_ledger_ret_code == -1) {
        Py_RETURN_NONE;
    } else {
        return Py_BuildValue("I", l_ledger_ret_code);
    }
}

PyObject *wrapping_dap_chain_block_get_block_from_hash(PyObject *self, PyObject *argv){
    (void)self;
    PyDapHashFastObject  *obj_datum_hash;
    PyDapChainObject  *obj_chain;
    if (!PyArg_ParseTuple(argv, "OO", &obj_chain, &obj_datum_hash)) {
        return NULL;
    }
    if (!PyDapChain_Check(obj_chain)) {
        PyErr_SetString(PyExc_AttributeError, "The first argument is set incorrectly, it must be a "
                                              "network chain.");
        return NULL;
    }
    if (!PyDapHashFast_Check(obj_datum_hash)) {
        PyErr_SetString(PyExc_AttributeError, "The second argument is set incorrectly and must be an "
                                              "instance of a DapHashFast object.");
        return NULL;
    }
    size_t l_block_size = 0;
    dap_chain_block_t *l_blocks = (dap_chain_block_t *)obj_chain->chain_t->callback_block_find_by_tx_hash(obj_chain->chain_t, obj_datum_hash->hash_fast, &l_block_size);
    if (!l_blocks || l_block_size == 0) {
        Py_RETURN_NONE;
    }
    PyDapChainCSBlockObject *obj_block = PyObject_NEW(PyDapChainCSBlockObject, &DapChainCsBlockType);
    obj_block->block = l_blocks;
    obj_block->block_size = l_block_size;
    return (PyObject*)obj_block;
}

PyObject *wrapping_dap_chain_cs_block_get_block_signers_rewards(PyObject *self, PyObject *args){
    
    PyDapChainObject *obj_chain = NULL;

    if (!PyArg_ParseTuple(args, "O", &obj_chain)){
        return NULL;
    }
    if (!PyDapChain_Check(obj_chain)) {
        PyErr_SetString(PyExc_Exception, "The first argument must be an instance of the DAP.Chain object");
        return NULL;
    }

    dap_hash_fast_t l_block_hash = {0}; 
    dap_hash_fast(
        ((PyDapChainCSBlockObject*)self)->block,
        ((PyDapChainCSBlockObject*)self)->block_size, 
        &l_block_hash);

    dap_chain_block_t *l_block = ((PyDapChainCSBlockObject*)self)->block;
    size_t l_block_size = ((PyDapChainCSBlockObject*)self)->block_size;

    PyObject *obj_rewards_list = PyList_New(0);
    size_t l_signs_count = dap_chain_block_get_signs_count(l_block, l_block_size);
    for (size_t i = 0; i < l_signs_count; i++) {
        dap_sign_t *l_sign = dap_chain_block_sign_get(l_block, l_block_size, i);
        dap_pkey_t *l_pkey = dap_pkey_get_from_sign(l_sign);
        if (!l_pkey) {
            log_it(L_ERROR, "Can't get pkey from sign");
            continue;
        }
        dap_hash_fast_t l_pkey_hash = {};
        if (dap_sign_get_pkey_hash(l_sign, &l_pkey_hash) == false) {
            log_it(L_ERROR, "Can't get pkey hash from sign");
            continue;
        }
        uint256_t l_value_reward = obj_chain->chain_t->callback_calc_reward(obj_chain->chain_t, &l_block_hash, l_pkey);

        PyDapHashFastObject *obj_pkey_hash = PyObject_New(PyDapHashFastObject, &DapChainHashFastObjectType);
        if (!obj_pkey_hash) {
            Py_DECREF(obj_rewards_list);
            return NULL;
        }
        obj_pkey_hash->hash_fast = DAP_NEW(dap_chain_hash_fast_t);
        memcpy(obj_pkey_hash->hash_fast, &l_pkey_hash, sizeof(dap_chain_hash_fast_t));
        obj_pkey_hash->origin = true;

        DapMathObject *obj_reward = PyObject_New(DapMathObject, &DapMathObjectType);
        obj_reward->value = l_value_reward;

        char hex_key[DAP_CHAIN_HASH_FAST_STR_LEN + 1] = {0};
        dap_chain_hash_fast_to_str(&l_pkey_hash, hex_key, sizeof(hex_key));

        PyObject *py_key = PyUnicode_FromString(hex_key);
        if (!py_key) {
            Py_DECREF(obj_reward);
            Py_DECREF(obj_rewards_list);
            return NULL;
        }
        
        PyObject *entry = PyDict_New();
        if (PyDict_SetItem(entry, py_key, (PyObject*)obj_reward) < 0) {
            Py_DECREF(entry);
            Py_DECREF(py_key);
            Py_DECREF(obj_reward);
            Py_DECREF(obj_rewards_list);
            return NULL;
        }

        Py_DECREF(py_key);
        Py_DECREF(obj_reward);

        if (PyList_Append(obj_rewards_list, entry) < 0) {
            Py_DECREF(entry);
            Py_DECREF(obj_rewards_list);
            return NULL;
        }
        Py_DECREF(entry);
    }

    return obj_rewards_list;
}