#include "wrapping_dap_chain_datum_anchor.h"
#include <datetime.h>
#include "wrapping_cert.h"
#include "wrapping_dap_sign.h"

#define PVT(a)((PyDapChainDatumAnchorObject*)a)

PyObject *wrapping_dap_chain_datum_anchor_get_ts_created(PyObject *self, void *closure){
    (void)closure;
    PyDateTime_IMPORT;
    PyObject *obj_ts_float = PyLong_FromLong(PVT(self)->anchor->header.ts_created);
    PyObject *obj_ts = Py_BuildValue("(O)", obj_ts_float);
    PyObject *obj_dt = PyDateTime_FromTimestamp(obj_ts);
    Py_DECREF(obj_ts_float);
    return obj_dt;
}

PyObject *wrapping_dap_chain_datum_anchor_get_decree_hash(PyObject *self, void *closure){
    (void)closure;
    size_t l_tsd_total_size = PVT(self)->anchor->header.data_size;
    if (l_tsd_total_size == 0)
        Py_RETURN_NONE;
    for (size_t l_offset = 0; l_offset < l_tsd_total_size;) {
        dap_tsd_t *l_tsd = (dap_tsd_t*)(((byte_t*)PVT(self)->anchor->data_n_sign) + l_offset);
        size_t l_tsd_size = dap_tsd_size(l_tsd);
        if (l_tsd_size + l_offset > l_tsd_total_size)
            break;
        l_offset += l_tsd_size;
        if (l_tsd->type == DAP_CHAIN_DATUM_ANCHOR_TSD_TYPE_DECREE_HASH) {
            dap_hash_fast_t *l_hf = _dap_tsd_get_object(l_tsd, dap_hash_fast_t);
            PyDapHashFastObject *l_obj_hf = PyObject_New(PyDapHashFastObject, &DapChainHashFastObjectType);
            l_obj_hf->hash_fast = DAP_NEW(dap_hash_fast_t);
            if (!l_obj_hf->hash_fast) {
                Py_DECREF(l_obj_hf);
                return NULL;
            }
            memcpy(l_obj_hf->hash_fast, l_hf, sizeof(dap_hash_fast_t));
            return (PyObject*)l_obj_hf;
        }
    }
    Py_RETURN_NONE;
}

PyObject *wrapping_dap_chain_datum_anchor_get_tsd(PyObject *self, void *closure) {
    (void)closure;
    size_t l_tsd_total_size = PVT(self)->anchor->header.data_size;
    if (l_tsd_total_size == 0)
        Py_RETURN_NONE;
    PyObject *obj_list = PyList_New(0);
    for (size_t l_offset = 0; l_offset < l_tsd_total_size;) {
        dap_tsd_t *l_tsd = (dap_tsd_t*)(((byte_t*)PVT(self)->anchor->data_n_sign) + l_offset);
        size_t l_tsd_size = dap_tsd_size(l_tsd);
        if (l_tsd_size + l_offset > l_tsd_total_size)
            break;
        l_offset += l_tsd_size;
        PyObject *obj_type = PyLong_FromLong(l_tsd->type);
        PyObject *obj_value = PyBytes_FromStringAndSize((char*)l_tsd->data, l_tsd->size);
        PyObject *obj_dict = PyDict_New();
        PyDict_SetItemString(obj_dict, "type", obj_type);
        PyDict_SetItemString(obj_dict, "value", obj_value);
        PyList_Append(obj_list, obj_dict);
        Py_DECREF(obj_dict);
    }
    return (PyObject*)obj_list;
}

PyObject *wrapping_dap_chain_datum_anchor_get_sign(PyObject *self, void *closure) {
    (void)closure;
    size_t l_signs_size = PVT(self)->anchor->header.signs_size;
    dap_sign_t *l_signs = (dap_sign_t*)((byte_t*)(PVT(self)->anchor->data_n_sign) + PVT(self)->anchor->header.data_size);
    if (l_signs_size == 0)
        Py_RETURN_NONE;
    PyObject *obj_list = PyList_New(0);
    for (size_t l_offset = 0; l_offset < l_signs_size; ) {
        dap_sign_t *l_sign = (dap_sign_t*)((byte_t*)l_signs + l_offset);
        size_t l_sign_size = dap_sign_get_size(l_sign);
        PyObject *obj_sign = PyDapSignObject_Cretae(l_sign);
        PyList_Append(obj_list, obj_sign);
        Py_DECREF(obj_sign);
        l_offset += l_sign_size;
    }
    return obj_list;
}

PyObject *wrapping_dap_chain_datum_anchor_get_hash(PyObject *self, void *closure){
    (void)closure;
    dap_chain_datum_anchor_t *l_anchor = ((PyDapChainDatumAnchorObject*)self)->anchor;
    dap_hash_fast_t *l_hf = DAP_NEW(dap_hash_fast_t);
    dap_hash_fast(l_anchor, dap_chain_datum_anchor_get_size(((PyDapChainDatumAnchorObject*)self)->anchor), l_hf);
    PyDapHashFastObject *obj_hf = PyObject_New(PyDapHashFastObject, &DapChainHashFastObjectType);
    obj_hf->hash_fast = l_hf;
    return (PyObject*)obj_hf;
}

static PyGetSetDef DapChainDatumAnchorGetSet[] = {
        {"hash", (getter)wrapping_dap_chain_datum_anchor_get_hash, NULL, NULL,NULL},
        {"created", (getter)wrapping_dap_chain_datum_anchor_get_ts_created, NULL, NULL, NULL},
        {"TSD", (getter)wrapping_dap_chain_datum_anchor_get_tsd, NULL, NULL, NULL},
        {"signs", (getter)wrapping_dap_chain_datum_anchor_get_sign, NULL, NULL, NULL},
        {"decreeHash", (getter)wrapping_dap_chain_datum_anchor_get_decree_hash, NULL, NULL, NULL},
        {}
};

static PyMethodDef DapChainDatumAnchorMethods[] = {{}};

PyObject * DapChainDatumAnchorObject_create(PyTypeObject *type_object, PyObject *args, PyObject *kwds) {
    (void)type_object;
    (void)kwds;
    PyObject *obj_tsd_list;
    PyObject *obj_cert;
    if (!PyArg_ParseTuple(args, "OO", &obj_tsd_list, &obj_cert)) {
        return NULL;
    }
    if (!PyObject_TypeCheck(obj_cert, &DapCryptoCertObjectType)) {
        PyErr_SetString(PyExc_AttributeError, "The second argument to the constructor was not correctly "
                                              "passed, the second argument must be DAP.Crypto.Cert");
        return NULL;
    }
    if (!PyList_Check(obj_tsd_list)) {
        PyErr_SetString(PyExc_AttributeError, "The first argument to the constructor was not correctly "
                                              "passed, the third argument must be a list.");
        return NULL;
    }
    //Parse TSD
    dap_list_t *l_tsd_list = NULL;
    PyObject* l_iter = PyObject_GetIter(obj_tsd_list);
    if (l_iter == NULL) {
        PyErr_SetString(PyExc_AttributeError, "Passed as the first argument, the list contains no elements.");
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
    //Creating datum anchor
    dap_chain_datum_anchor_t *l_anchor = DAP_NEW_Z_SIZE(dap_chain_datum_anchor_t, sizeof(dap_chain_datum_anchor_t) + l_total_tsd_size);
    if (!l_anchor) {
        PyErr_SetString(PyExc_RuntimeError, "Anchor creation failed");
        return NULL;
    }
    l_anchor->anchor_version = 1;
    l_anchor->header.ts_created = dap_time_now();
    l_anchor->header.data_size = l_total_tsd_size;
    l_anchor->header.signs_size = 0;

    size_t l_data_tsd_offset = 0;
    for ( dap_list_t* l_tsd_list_iter=dap_list_first(l_tsd_list); l_tsd_list_iter; l_tsd_list_iter=l_tsd_list_iter->next){
        dap_tsd_t * l_b_tsd = (dap_tsd_t *) l_tsd_list_iter->data;
        size_t l_tsd_size = dap_tsd_size(l_b_tsd);
        memcpy((byte_t*)l_anchor->data_n_sign + l_data_tsd_offset, l_b_tsd, l_tsd_size);
        l_data_tsd_offset += l_tsd_size;
    }
    dap_list_free_full(l_tsd_list, NULL);

    dap_sign_t *l_sign = dap_cert_sign(((PyCryptoCertObject*)obj_cert)->cert, l_anchor,
                                       sizeof(dap_chain_datum_anchor_t) + l_anchor->header.data_size);

    if (l_sign) {
        size_t l_sign_size = dap_sign_get_size(l_sign);
        l_anchor = DAP_REALLOC(l_anchor, sizeof(dap_chain_datum_anchor_t) + l_anchor->header.data_size + l_sign_size);
        if (!l_anchor) {
            DAP_DELETE(l_sign);
            PyErr_SetString(PyExc_RuntimeError, "Anchor resizing failed");
            return NULL;
        }
        memcpy(l_anchor->data_n_sign + l_total_tsd_size, l_sign, l_sign_size);
        l_anchor->header.signs_size = l_sign_size;
        DAP_DELETE(l_sign);
    } else {
        DAP_DELETE(l_anchor);
        PyErr_SetString(PyExc_RuntimeError, "Anchor signing failed");
        return NULL;
    }

    PyDapChainDatumAnchorObject *obj_anchor = PyObject_New(PyDapChainDatumAnchorObject, &DapChainDatumAnchorObjectType);
    PVT(obj_anchor)->anchor = l_anchor;

    return (PyObject*)obj_anchor;
}

PyTypeObject DapChainDatumAnchorObjectType = {
        .ob_base = PyVarObject_HEAD_INIT(NULL, 0)
        .tp_name = "CellFrame.Common.DatumAnchor",
        .tp_basicsize = sizeof(PyDapChainDatumAnchorObject),
        .tp_doc = "Chain datum type anchor object",
        .tp_getset = DapChainDatumAnchorGetSet,
        .tp_methods = DapChainDatumAnchorMethods,
        .tp_new = DapChainDatumAnchorObject_create
};

bool DapChainDatumAnchor_Check(PyObject *self) {
    return PyObject_TypeCheck(self, &DapChainDatumAnchorObjectType);
}
