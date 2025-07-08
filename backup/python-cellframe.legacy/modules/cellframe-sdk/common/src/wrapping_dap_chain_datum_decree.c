#include "wrapping_dap_chain_datum_decree.h"
#include "libdap-python.h"
#include "datetime.h"
#include "wrapping_dap_sign.h"
#include "libdap_chain_net_python.h"
#include "wrapping_cert.h"
#include "dap_chain_net_srv_stake_pos_delegate.h"

#define PVT(a)((PyDapChainDatumDecreeObject*)a)

PyObject* wrapping_dap_chain_datum_decree_get_ts_created(PyObject *self, void* closure) {
    (void)closure;
    PyDateTime_IMPORT;
    PyObject *obj_ts_float = PyLong_FromLong(PVT(self)->decree->header.ts_created);
    PyObject *obj_ts = Py_BuildValue("(O)", obj_ts_float);
    PyObject *obj_dt = PyDateTime_FromTimestamp(obj_ts);
    return obj_dt;
}
PyObject* wrapping_dap_chain_datum_decree_get_type(PyObject *self, void* closure){
    (void)closure;
    return Py_BuildValue("H", PVT(self)->decree->header.type);
}
PyObject* wrapping_dap_chain_datum_decree_get_type_str(PyObject *self, void* closure){
    (void)closure;
    switch(PVT(self)->decree->header.type){
        case DAP_CHAIN_DATUM_DECREE_TYPE_COMMON:
            return Py_BuildValue("s", "DAP_CHAIN_DATUM_DECREE_TYPE_COMMON");
        case DAP_CHAIN_DATUM_DECREE_TYPE_SERVICE:
            return Py_BuildValue("s", "DAP_CHAIN_DATUM_DECREE_TYPE_SERVICE");
    }
    return Py_BuildValue("s", "UNKNOWN");
}
PyObject* wrapping_dap_chain_datum_decree_get_subtype(PyObject *self, void* closure){
    (void)closure;
    return Py_BuildValue("H", PVT(self)->decree->header.sub_type);
}
PyObject* wrapping_dap_chain_datum_decree_get_subtype_str(PyObject *self, void* closure){
    (void)closure;
    return Py_BuildValue("s", dap_chain_datum_decree_subtype_to_str(PVT(self)->decree->header.sub_type));
}

PyObject* wrapping_dap_chain_datum_decree_get_tsd(PyObject *self, void* closure) {
    (void)closure;
    size_t l_tsd_total_size = PVT(self)->decree->header.data_size;
    if (l_tsd_total_size == 0)
        Py_RETURN_NONE;
    PyObject *obj_list = PyList_New(0);
    for (size_t l_offset = 0; l_offset < l_tsd_total_size;) {
        dap_tsd_t *l_tsd = (dap_tsd_t*)(((byte_t*)PVT(self)->decree->data_n_signs) + l_offset);
        size_t l_tsd_size = dap_tsd_size(l_tsd);
        if (l_tsd_size + l_offset > l_tsd_total_size)
            break;
        l_offset += l_tsd_size;
        PyObject *obj_type = PyLong_FromLong(l_tsd->type);
        PyObject *obj_value = NULL;
        obj_value = PyBytes_FromStringAndSize((char*)l_tsd->data, (Py_ssize_t)l_tsd->size);
        PyObject *obj_dict = PyDict_New();
        PyDict_SetItemString(obj_dict, "type", obj_type);
        PyDict_SetItemString(obj_dict, "value", obj_value);
        PyList_Append(obj_list, obj_dict);
        Py_DECREF(obj_dict);
    }
    return (PyObject*)obj_list;
}

PyObject* wrapping_dap_chain_datum_decree_get_signs(PyObject *self, void* closure) {
    (void)closure;
    size_t l_signs_size = 0;
    dap_sign_t *l_signs = dap_chain_datum_decree_get_signs(PVT(self)->decree, &l_signs_size);
    if (l_signs_size == 0)
        Py_RETURN_NONE;
    PyObject *obj_list = PyList_New(0);
    for (size_t l_offset = 0; l_offset < l_signs_size; ) {
        dap_sign_t *l_sign = (dap_sign_t*)((byte_t*)l_signs + l_offset);
        size_t l_sign_size = dap_sign_get_size(l_sign );
        PyObject *obj_sign = PyDapSignObject_Cretae(l_sign);
        PyList_Append(obj_list, obj_sign);
        Py_DECREF(obj_sign);
        l_offset += l_sign_size;
    }
    return obj_list;
}
PyObject* wrapping_dap_chain_datum_decree_get_hash(PyObject *self, void* closure){
    (void)closure;
    dap_chain_datum_decree_t *l_decree = ((PyDapChainDatumDecreeObject*)self)->decree;
    dap_hash_fast_t *l_hf = DAP_NEW(dap_hash_fast_t);
    dap_hash_fast(l_decree, dap_chain_datum_decree_get_size(l_decree), l_hf);
    PyDapHashFastObject *obj_hf = PyObject_New(PyDapHashFastObject, &DapChainHashFastObjectType);
    obj_hf->hash_fast = l_hf;
    return (PyObject*)obj_hf;
}

PyGetSetDef  DapChainDatumDecreeGetSet[] = {
        {"hash", (getter)wrapping_dap_chain_datum_decree_get_hash, NULL, NULL, NULL},
        {"tsCreated", (getter)wrapping_dap_chain_datum_decree_get_ts_created, NULL, NULL, NULL},
        {"type", (getter)wrapping_dap_chain_datum_decree_get_type, NULL, NULL, NULL},
        {"typeStr", (getter)wrapping_dap_chain_datum_decree_get_type_str, NULL, NULL, NULL},
        {"subtype", (getter)wrapping_dap_chain_datum_decree_get_subtype, NULL, NULL, NULL},
        {"subtypeStr", (getter)wrapping_dap_chain_datum_decree_get_subtype_str, NULL, NULL, NULL},
        {"signs", (getter)wrapping_dap_chain_datum_decree_get_signs, NULL, NULL, NULL},
        {"TSD", (getter)wrapping_dap_chain_datum_decree_get_tsd, NULL, NULL, NULL},
        {}
};

PyObject *wrapping_dap_chain_datum_decree_add_sign(PyObject *self, PyObject *args) {
    PyObject *obj_cert;
    if (!PyArg_ParseTuple(args, "O", &obj_cert)) {
        return NULL;
    }
    if (!PyObject_TypeCheck(obj_cert, &DapCryptoCertObjectType)) {
        PyErr_SetString(PyExc_AttributeError, "The first argument was not passed to the function "
                                              "correctly. The second argument must be of type DAP.Crypto.Cert.");
        return NULL;
    }

    size_t l_cur_sign_offset = PVT(self)->decree->header.data_size + PVT(self)->decree->header.signs_size;
    size_t l_total_signs_size = PVT(self)->decree->header.signs_size;

    dap_sign_t *l_sign = dap_cert_sign(((PyCryptoCertObject*)obj_cert)->cert, PVT(self)->decree,
                                       sizeof(dap_chain_datum_decree_t) + PVT(self)->decree->header.data_size);
    if (l_sign) {
        size_t l_sign_size = dap_sign_get_size(l_sign);
        PVT(self)->decree = DAP_REALLOC(PVT(self)->decree, sizeof(dap_chain_datum_decree_t) + l_cur_sign_offset + l_sign_size);
        memcpy((byte_t*)PVT(self)->decree->data_n_signs + l_cur_sign_offset, l_sign, l_sign_size);
        l_total_signs_size += l_sign_size;
        PVT(self)->decree->header.signs_size = l_total_signs_size;
        DAP_DELETE(l_sign);
    } else {
        PyErr_SetString(PyExc_RuntimeError, "Decree signing failed");
        return NULL;
    }
    Py_RETURN_NONE;
}

PyObject *wrapping_dap_chain_datum_decree_create_approve(PyObject *self, PyObject *args) {
    (void)self;
    PyObject *obj_net;
    PyObject *obj_tx_hash;
    PyObject *obj_cert;
    if (!PyArg_ParseTuple(args, "OOO", &obj_net, &obj_tx_hash, &obj_cert)) {
        return NULL;
    }
    if (!PyDapChainNet_Check((PyDapChainNetObject*)obj_net)) {
        PyErr_SetString(PyExc_AttributeError, "The first argument was not correctly passed to the "
                                              "function call. It must be a Net object.");
        return NULL;
    }
    if (!PyDapHashFast_Check((PyDapHashFastObject*)obj_tx_hash)) {
        PyErr_SetString(PyExc_AttributeError, "The second argument was not correctly passed to the "
                                              "function call. It must be a HashFast object.");
        return NULL;
    }
    if (!PyObject_TypeCheck(obj_cert, &DapCryptoCertObjectType)) {
        PyErr_SetString(PyExc_AttributeError, "The third argument was incorrectly passed to the function"
                                              " call. It must be a Cert object.");
        return NULL;
    }
    dap_chain_datum_decree_t *l_decree = dap_chain_net_srv_stake_decree_approve(
            ((PyDapChainNetObject*)obj_net)->chain_net,
            ((PyDapHashFastObject*)obj_tx_hash)->hash_fast,
            ((PyCryptoCertObject*)obj_cert)->cert);
    if (!l_decree) {
        PyErr_SetString(PyExc_RuntimeError, "It was not possible to create an approval directive, see "
                                            "the node logs for the reasons for the error.");
        return NULL;
    }
    PyDapChainDatumDecreeObject *obj_decree = PyObject_New(PyDapChainDatumDecreeObject, &DapChainDatumDecreeObjectType);
    obj_decree->decree = l_decree;
    return (PyObject*)obj_decree;
}

PyObject *wrapping_dap_chain_datum_decree_create_anchor(PyObject *self, PyObject *args) {
    PyObject *obj_net;
    PyObject *obj_cert;
    PyObject *obj_chain = NULL;
    if (!PyArg_ParseTuple(args, "OO|O", &obj_net, &obj_cert, &obj_chain)) {
        return NULL;
    }
    if (!PyDapChainNet_Check((PyDapChainNetObject*)obj_net)) {
        PyErr_SetString(PyExc_AttributeError, "The first argument is incorrect, it must be an object "
                                              "of type Net.");
        return NULL;
    }
    dap_chain_net_t *l_net = ((PyDapChainNetObject*)obj_net)->chain_net;
    dap_chain_t *l_chain;
    if (!PyObject_TypeCheck(obj_cert, &DapCryptoCertObjectType)) {
        PyErr_SetString(PyExc_AttributeError, "The second argument is incorrect, it must be an "
                                              "object of type Crypto.");
        return NULL;
    }
    if (obj_chain) {
        if (!PyDapChain_Check((PyDapChainObject*)obj_chain)) {
            PyErr_SetString(PyExc_AttributeError, "The third argument is incorrect, it must be an "
                                                  "object of type Chain.");
            return NULL;
        }
        if (((PyDapChainObject*)obj_chain)->chain_t != dap_chain_net_get_chain_by_chain_type(l_net,
                                                                                             CHAIN_TYPE_ANCHOR)) {
            char *l_err_str = dap_strdup_printf("Chain %s don't support decree.",
                                                ((PyDapChainObject*)obj_chain)->chain_t->name);
            PyErr_SetString(PyExc_AttributeError, l_err_str);
            DAP_DELETE(l_err_str);
            return NULL;
        }
        l_chain = ((PyDapChainObject*)obj_chain)->chain_t;
    } else {
        l_chain = dap_chain_net_get_chain_by_chain_type(l_net, CHAIN_TYPE_ANCHOR);
        if (!l_chain) {
            char *l_err_str = dap_strdup_printf("Network %s does not support Decree.", l_net->pub.name);
            PyErr_SetString(PyExc_AttributeError, l_err_str);
            DAP_DELETE(l_err_str);
            return NULL;
        }
    }
    dap_hash_fast_t l_decree_hash = {0};
    dap_hash_fast(PVT(self)->decree, dap_chain_datum_decree_get_size(PVT(self)->decree), &l_decree_hash);
    dap_tsd_t *l_tsd_decree_hash = dap_tsd_create(DAP_CHAIN_DATUM_ANCHOR_TSD_TYPE_DECREE_HASH,
                                                  &l_decree_hash, sizeof(dap_hash_fast_t));
    if (!l_tsd_decree_hash) {
        PyErr_SetString(PyExc_RuntimeError, "Anchor creation failed. Memory allocation fail.");
        return NULL;
    }

    dap_chain_datum_anchor_t *l_anchor = DAP_NEW_Z_SIZE(dap_chain_datum_anchor_t, sizeof(dap_chain_datum_anchor_t) +
                                            dap_tsd_size(l_tsd_decree_hash));
    if (!l_anchor) {
        PyErr_SetString(PyExc_RuntimeError, "Anchor creation failed. Memory allocation fail.");
        return NULL;
    }
    l_anchor->header.data_size = dap_tsd_size(l_tsd_decree_hash);
    l_anchor->header.ts_created = dap_time_now();
    memcpy(l_anchor->data_n_sign, l_tsd_decree_hash, dap_tsd_size(l_tsd_decree_hash));

    DAP_DEL_Z(l_tsd_decree_hash);
    dap_sign_t *l_sign = dap_cert_sign(((PyCryptoCertObject*)obj_cert)->cert, l_anchor,
                                       sizeof(dap_chain_datum_anchor_t)+l_anchor->header.data_size);
    if (l_sign) {
        size_t l_sign_size = dap_sign_get_size(l_sign);
        l_anchor = DAP_REALLOC(l_anchor, sizeof(dap_chain_datum_anchor_t)+l_anchor->header.data_size+l_sign_size);
        memcpy(l_anchor->data_n_sign + l_anchor->header.data_size, l_sign, l_sign_size);
        l_anchor->header.signs_size = l_sign_size;
        DAP_DELETE(l_sign);
    } else {
        PyErr_SetString(PyExc_RuntimeError, "Can't sign created anchor.");
        DAP_DELETE(l_anchor);
        return NULL;
    }

    PyDapChainDatumAnchorObject *obj_anchor = PyObject_New(PyDapChainDatumAnchorObject, &DapChainDatumAnchorObjectType);
    obj_anchor->anchor = l_anchor;
    return (PyObject*)obj_anchor;
}

PyObject *wrapping_decree_sign_check(PyObject *self, PyObject *args){
    (void)args;
    dap_chain_datum_decree_t *l_decree = ((PyDapChainDatumDecreeObject*)self)->decree;
    // Get pkeys sign from decree datum

    size_t l_signs_size = 0;
    //multiple signs reading from datum
    dap_sign_t *l_signs_block = dap_chain_datum_decree_get_signs(l_decree, &l_signs_size);
//    if (!l_signs_size || !l_signs_block)
//    {
//        log_it(L_WARNING,"Decree data sign not found");
//        return -100;
//    }

    // Find unique pkeys in pkeys set from previous step and check that number of signs > min
    size_t l_num_of_unique_signs = 0;
    dap_sign_t **l_unique_signs = dap_sign_get_unique_signs(l_signs_block, l_signs_size, &l_num_of_unique_signs);

    uint16_t l_min_signs = 1;//a_net->pub.decree->min_num_of_owners;
//    if (l_num_of_unique_signs < l_min_signs) {
//        log_it(L_WARNING, "Not enough unique signatures, get %zu from %hu", l_num_of_unique_signs, l_min_signs);
//        return -106;
//    }

    // Verify all keys and its signatures
    uint16_t l_signs_size_for_current_sign = 0, l_signs_verify_counter = 0, l_signs_not_verify_counter = 0;
    l_decree->header.signs_size = 0;
    size_t l_verify_data_size = l_decree->header.data_size + sizeof(dap_chain_datum_decree_t);

    for(size_t i = 0; i < l_num_of_unique_signs; i++)
    {
        size_t l_sign_max_size = dap_sign_get_size(l_unique_signs[i]);
//        if (s_verify_pkey(l_unique_signs[i], a_net))
//        {
            // 3. verify sign
            if(!dap_sign_verify_all(l_unique_signs[i], l_sign_max_size, l_decree, l_verify_data_size))
            {
                l_signs_verify_counter++;
            } else {
                l_signs_not_verify_counter++;
            }
//        } else {
//            dap_hash_fast_t l_sign_hash = {0};
//            dap_hash_fast(l_unique_signs[i], l_sign_max_size, &l_sign_hash);
//            char *l_sign_hash_str = dap_hash_fast_to_str_new(&l_sign_hash);
//            log_it(L_WARNING, "Signature [%zu] %s failed public key verification.", i, l_sign_hash_str);
//            DAP_DELETE(l_sign_hash_str);
//        }
        // Each sign change the sign_size field by adding its size after signing. So we need to change this field in header for each sign.
        l_signs_size_for_current_sign += l_sign_max_size;
        l_decree->header.signs_size = l_signs_size_for_current_sign;
    }

    l_decree->header.signs_size = l_signs_size;

//    DAP_DELETE(l_signs_arr);
    DAP_DELETE(l_unique_signs);

    PyObject* obj_dict = PyDict_New();
    PyDict_SetItemString(obj_dict, "VERIFY", Py_BuildValue("I", l_signs_verify_counter));
    PyDict_SetItemString(obj_dict, "NOVERIFY", Py_BuildValue("I", l_signs_not_verify_counter));
    return obj_dict;
}

PyMethodDef DapChainDatumDecreeMethods[] = {
        {
                "addSign",
                wrapping_dap_chain_datum_decree_add_sign,
                METH_VARARGS,
                "Adding a signature for the decree datum."
            },
        {
                "createApprove",
                wrapping_dap_chain_datum_decree_create_approve,
                METH_VARARGS | METH_STATIC,
                "Creates a steak approval decree."
            },
        {
                "createAnchor",
                wrapping_dap_chain_datum_decree_create_anchor,
                METH_VARARGS,
                "The function creates an anchor for the decree."
            },
        {
            "signCheck",
            wrapping_decree_sign_check,
            METH_NOARGS,
            ""
            },
        {}
};

PyObject *PyDapChainDatumDecreeObject_new(PyTypeObject *type_object, PyObject *args, PyObject *kwds) {
    (void)type_object;
    (void)kwds;
    PyObject *obj_net;
    PyObject *obj_tsd_list;
    const char *l_subtype_str;
    PyObject *obj_cert;
    if (!PyArg_ParseTuple(args, "OOsO", &obj_net, &obj_cert, &l_subtype_str, &obj_tsd_list)) {
        return NULL;
    }
    if (!PyObject_TypeCheck(obj_net, &DapChainNetObjectType)) {
        PyErr_SetString(PyExc_AttributeError, "The first argument to the constructor was not correctly "
                                              "passed, the first argument must be CellFrame.NetworkChain");
        return NULL;
    }
    if (!PyObject_TypeCheck(obj_cert, &DapCryptoCertObjectType)) {
        PyErr_SetString(PyExc_AttributeError, "The second argument to the constructor was not correctly "
                                              "passed, the second argument must be DAP.Crypto.Cert");
        return NULL;
    }
    if (!PyList_Check(obj_tsd_list)) {
        PyErr_SetString(PyExc_AttributeError, "The third argument to the constructor was not correctly "
                                              "passed, the third argument must be a list.");
        return NULL;
    }
    //Get subtype
    uint16_t l_subtype = 0;
    if (strcmp(l_subtype_str, "DAP_CHAIN_DATUM_DECREE_COMMON_SUBTYPE_FEE") == 0 ) {
        l_subtype = DAP_CHAIN_DATUM_DECREE_COMMON_SUBTYPE_FEE;
    } else if (strcmp(l_subtype_str, "DAP_CHAIN_DATUM_DECREE_COMMON_SUBTYPE_OWNERS") == 0) {
        l_subtype = DAP_CHAIN_DATUM_DECREE_COMMON_SUBTYPE_OWNERS;
    } else if (strcmp(l_subtype_str, "DAP_CHAIN_DATUM_DECREE_COMMON_SUBTYPE_OWNERS_MIN") == 0) {
        l_subtype = DAP_CHAIN_DATUM_DECREE_COMMON_SUBTYPE_OWNERS_MIN;
    } else if (strcmp(l_subtype_str, "DAP_CHAIN_DATUM_DECREE_COMMON_SUBTYPE_STAKE_APPROVE") == 0) {
        l_subtype = DAP_CHAIN_DATUM_DECREE_COMMON_SUBTYPE_STAKE_APPROVE;
    } else if (strcmp(l_subtype_str, "DAP_CHAIN_DATUM_DECREE_COMMON_SUBTYPE_STAKE_INVALIDATE") == 0) {
        l_subtype = DAP_CHAIN_DATUM_DECREE_COMMON_SUBTYPE_STAKE_INVALIDATE;
    } else if (strcmp(l_subtype_str, "DAP_CHAIN_DATUM_DECREE_COMMON_SUBTYPE_STAKE_MIN_VALUE") == 0) {
        l_subtype = DAP_CHAIN_DATUM_DECREE_COMMON_SUBTYPE_STAKE_MIN_VALUE;
    } else if (strcmp(l_subtype_str, "DAP_CHAIN_DATUM_DECREE_COMMON_SUBTYPE_STAKE_MIN_VALIDATORS_COUNT") == 0) {
        l_subtype = DAP_CHAIN_DATUM_DECREE_COMMON_SUBTYPE_STAKE_MIN_VALIDATORS_COUNT;
    } else {
        char *l_err_str = dap_strdup_printf("An unsupported %s subtype was passed as the third argument. Supported delegation token subtypes:\n"
                                            "\tDAP_CHAIN_DATUM_DECREE_COMMON_SUBTYPE_FEE\n"
                                            "\tDAP_CHAIN_DATUM_DECREE_COMMON_SUBTYPE_OWNERS\n"
                                            "\tDAP_CHAIN_DATUM_DECREE_COMMON_SUBTYPE_OWNERS_MIN\n"
                                            "\tDAP_CHAIN_DATUM_DECREE_COMMON_SUBTYPE_TON_SIGNERS_MIN\n"
                                            "\tDAP_CHAIN_DATUM_DECREE_COMMON_SUBTYPE_STAKE_APPROVE\n"
                                            "\tDAP_CHAIN_DATUM_DECREE_COMMON_SUBTYPE_STAKE_INVALIDATE\n"
                                            "\tDAP_CHAIN_DATUM_DECREE_COMMON_SUBTYPE_STAKE_MIN_VALUE\n"
                                            "\tDAP_CHAIN_DATUM_DECREE_COMMON_SUBTYPE_STAKE_MIN_VALIDATORS_COUNT", l_subtype_str);
        PyErr_SetString(PyExc_AttributeError, l_err_str);
        DAP_DELETE(l_err_str);
        return NULL;
    }
    //Parsing TSD List
    dap_list_t *l_tsd_list = NULL;
    PyObject* l_iter = PyObject_GetIter(obj_tsd_list);
    if (l_iter == NULL) {
        PyErr_SetString(PyExc_AttributeError, "Passed as the fourth argument, the list contains no elements.");
        return NULL;
    }
    PyObject *l_item = NULL;
    size_t l_el_count = 0;
    size_t l_total_tsd_size = 0;
    while((l_item = PyIter_Next(l_iter)) != NULL){
        l_el_count++;
        if (!PyDict_Check(l_item)) {
            char *l_err_str = dap_strdup_printf("Leaf parsing error, element number: %zu is not a dictionary.", l_el_count);
            PyErr_SetString(PyExc_AttributeError, l_err_str);
            DAP_DELETE(l_err_str);
            return NULL;
        }
        PyObject *l_obj_type = PyDict_GetItemString(l_item, "type");
        if (!PyLong_Check(l_obj_type)) {
            char *l_err_str = dap_strdup_printf("The dictionary obtained from the list under the %zu element "
                                                "does not contain an object with the key type or this object is not "
                                                "a number.", l_el_count);
            PyErr_SetString(PyExc_AttributeError, l_err_str);
            DAP_DELETE(l_err_str);
            return NULL;
        }
        PyObject *l_obj_value = PyDict_GetItemString(l_item, "value");
        if (!PyBytes_Check(l_obj_value)) {
            char *l_err_str = dap_strdup_printf("The dictionary obtained from the list under the %zu element "
                                                "does not contain an object with the key type or this object is not "
                                                "a bytes.", l_el_count);
            PyErr_SetString(PyExc_AttributeError, l_err_str);
            DAP_DELETE(l_err_str);
            return NULL;
        }
        unsigned long l_type = PyLong_AsUnsignedLong(l_obj_type);
        size_t l_value_size = PyBytes_Size(l_obj_value);
        void *l_value = PyBytes_AsString(l_obj_value);
        dap_tsd_t *l_tsd = dap_tsd_create(l_type, l_value, l_value_size);
        l_total_tsd_size += dap_tsd_size(l_tsd);
        l_tsd_list = dap_list_append(l_tsd_list, l_tsd);
    }
    //Creating datum decree
    dap_chain_datum_decree_t *l_decree = DAP_NEW_Z_SIZE(dap_chain_datum_decree_t, sizeof(dap_chain_datum_decree_t) + l_total_tsd_size);
    if (!l_decree) {
        PyErr_SetString(PyExc_RuntimeError, "Decree creation failed");
        return NULL;
    }
    l_decree->decree_version = DAP_CHAIN_DATUM_DECREE_VERSION;
    l_decree->header.ts_created = dap_time_now();
    l_decree->header.type = DAP_CHAIN_DATUM_DECREE_TYPE_COMMON;
    l_decree->header.common_decree_params.net_id = ((PyDapChainNetObject*)obj_net)->chain_net->pub.id;
    l_decree->header.common_decree_params.chain_id = dap_chain_net_get_default_chain_by_chain_type(
            ((PyDapChainNetObject*)obj_net)->chain_net, CHAIN_TYPE_DECREE)->id;
    l_decree->header.common_decree_params.cell_id = *dap_chain_net_get_cur_cell(((PyDapChainNetObject*)obj_net)->chain_net);
    l_decree->header.sub_type = l_subtype;
    l_decree->header.data_size = l_total_tsd_size;
    l_decree->header.signs_size = 0;

    size_t l_data_tsd_offset = 0;
    for ( dap_list_t* l_iter=dap_list_first(l_tsd_list); l_iter; l_iter=l_iter->next){
        dap_tsd_t * l_b_tsd = (dap_tsd_t *) l_iter->data;
        size_t l_tsd_size = dap_tsd_size(l_b_tsd);
        memcpy((byte_t*)l_decree->data_n_signs + l_data_tsd_offset, l_b_tsd, l_tsd_size);
        l_data_tsd_offset += l_tsd_size;
    }
    dap_list_free_full(l_tsd_list, NULL);

    dap_sign_t * l_sign = dap_cert_sign(((PyCryptoCertObject*)obj_cert)->cert,  l_decree,
                                        sizeof(dap_chain_datum_decree_t) + l_decree->header.data_size);

    if (l_sign) {
        size_t l_sign_size = dap_sign_get_size(l_sign);
        l_decree = DAP_REALLOC(l_decree, sizeof(dap_chain_datum_decree_t) + l_total_tsd_size + l_sign_size);
        if (!l_decree) {
            DAP_DELETE(l_sign);
            PyErr_SetString(PyExc_RuntimeError, "Decree resize failed");
            return NULL;
        }
        memcpy((byte_t*)l_decree->data_n_signs + l_total_tsd_size, l_sign, l_sign_size);
        l_decree->header.signs_size = l_sign_size;
        DAP_DELETE(l_sign);
    } else {
        DAP_DELETE(l_decree);
        PyErr_SetString(PyExc_RuntimeError, "Decree signing failed");
        return NULL;
    }

    PyDapChainDatumDecreeObject *obj_self = PyObject_New(PyDapChainDatumDecreeObject, &DapChainDatumDecreeObjectType);
    obj_self->decree = l_decree;
    return (PyObject*)obj_self;
}

void DapChainDatumDecree_free(PyDapChainDatumDecreeObject *self){
    DAP_DELETE(PVT(self)->decree);
    Py_TYPE(self)->tp_free((PyObject*)self);
}

PyTypeObject DapChainDatumDecreeObjectType = {
        .ob_base = PyVarObject_HEAD_INIT(NULL, 0)
        .tp_name = "CellFrame.Common.DatumDecree",
        .tp_basicsize = sizeof(PyDapChainDatumDecreeObject),
        .tp_dealloc = (destructor)DapChainDatumDecree_free,
        .tp_doc = "Chain datum type decree object",
        .tp_getset = DapChainDatumDecreeGetSet,
        .tp_methods = DapChainDatumDecreeMethods,
        .tp_new = PyDapChainDatumDecreeObject_new
};

bool DapChainDatumDecree_Check(PyObject *self){
    return PyObject_TypeCheck(self, &DapChainDatumDecreeObjectType);
}
