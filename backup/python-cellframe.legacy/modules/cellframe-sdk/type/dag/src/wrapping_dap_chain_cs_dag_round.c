#include "libdap-python.h"
#include "wrapping_dap_chain_cs_dag_round.h"
#include "wrapping_dap_chain_cs_dag_event.h"

#define ROUND(a) ((PyDapChainCsDagRoundObject*)a)->item
#define INFO(a) ((PyDapChainCsDagRoundInfoObject*)a)->info

PyObject *wrapping_dap_chain_cs_dag_round_get_info(PyObject *self, void *closure) {
    (void)closure;
    PyDapChainCsDagRoundInfoObject *obj_info = PyObject_NEW(PyDapChainCsDagRoundInfoObject, &DapChainCsDagRoundInfoType);
    obj_info->info = ROUND(self)->round_info;
    return (PyObject*)obj_info;
}
PyObject *wrapping_dap_chain_cs_dag_round_get_event(PyObject *self, void *closure) {
    (void)closure;
    PyDapChainCsDagEventObject *obj_event = PyObject_New(PyDapChainCsDagEventObject, &DapChainCsDagEventType);
    obj_event->event = (dap_chain_cs_dag_event_t*)ROUND(self)->event_n_signs;
    obj_event->event_size = ROUND(self)->event_size;
    return (PyObject*)obj_event;
}


PyObject *wrapping_dap_chain_cs_dag_round_get_signs(PyObject *self, void *closure) {
    (void)closure;
    PyObject *list_signs = PyList_New(0);
    size_t l_offset = ROUND(self)->event_size;
    while (l_offset < ROUND(self)->data_size) {
        dap_sign_t *l_sign = (dap_sign_t*)((byte_t*)ROUND(self)->event_n_signs+l_offset);
        size_t l_sign_size = dap_sign_get_size(l_sign);
        PyDapSignObject *l_obj_sign = PyObject_New(PyDapSignObject, &DapCryptoSignObjectType);
        l_obj_sign->sign = DAP_NEW_SIZE(dap_sign_t, l_sign_size);
        memcpy(l_obj_sign->sign, l_sign, l_sign_size);
        PyList_Append(list_signs, (PyObject*)l_obj_sign);
        Py_XDECREF(l_obj_sign);
        l_offset += l_sign_size;
    }
    return list_signs;
}

void DapChainCsDagRound_free(PyDapChainCsDagRoundObject *self) {
    DAP_DELETE(self->item);
    Py_TYPE(self)->tp_free((PyObject*)self);
}

PyGetSetDef DapChainCsDagRoundGetSetDef[] = {
        {"info", (getter) wrapping_dap_chain_cs_dag_round_get_info, NULL, "", NULL},
        {"event", (getter) wrapping_dap_chain_cs_dag_round_get_event, NULL, "", NULL},
        {"signs", (getter) wrapping_dap_chain_cs_dag_round_get_signs, NULL, "", NULL},
        {}
};

PyTypeObject DapChainCsDagRoundType = DAP_PY_TYPE_OBJECT(
        "CellFrame.Consensus.DagRound",sizeof(PyDapChainCsDagRoundObject),
        "Chain cs dag event objects",
        .tp_getset = DapChainCsDagRoundGetSetDef);

PyObject *wrapping_dap_chain_cs_dag_round_info_get_reject_count(PyObject *self, void *closure) {
    (void)closure;
    return Py_BuildValue("H", INFO(self).reject_count);
}
PyObject *wrapping_dap_chain_cs_dag_round_info_get_ts_update(PyObject *self, void *closure) {
    (void)closure;
    PyDateTime_IMPORT;
    dap_nanotime_t l_ts_expire = INFO(self).ts_update;
    PyObject *obj_ts_long =  Py_BuildValue("(k)", l_ts_expire);
    PyObject *obj_ts = PyDateTime_FromTimestamp(obj_ts_long);
    return obj_ts;
}
PyObject *wrapping_dap_chain_cs_dag_round_info_get_datum_hash(PyObject *self, void *closure) {
    (void)closure;
    PyDapHashFastObject *obj_hf = PyObject_New(PyDapHashFastObject, &DapChainHashFastObjectType);
    obj_hf->origin = true;
    obj_hf->hash_fast = DAP_NEW(dap_chain_hash_fast_t);
    memcpy(obj_hf->hash_fast, &INFO(self).datum_hash, sizeof(dap_chain_hash_fast_t));
    return (PyObject*)obj_hf;
}

PyGetSetDef DapChainCsDagRoundInfoGetSetDef[] = {
        {"reject_count", (getter) wrapping_dap_chain_cs_dag_round_info_get_reject_count, NULL, "", NULL},
        {"ts_update", (getter) wrapping_dap_chain_cs_dag_round_info_get_ts_update, NULL, "", NULL},
        {"datum_hash", (getter) wrapping_dap_chain_cs_dag_round_info_get_datum_hash, NULL, "", NULL},
        {}
};

PyTypeObject DapChainCsDagRoundInfoType = DAP_PY_TYPE_OBJECT(
        "CellFrame.Consensus.DagRoundInfo",sizeof(PyDapChainCsDagRoundInfoObject),
        "Chain cs dag round info objects",
        .tp_getset = DapChainCsDagRoundInfoGetSetDef
);