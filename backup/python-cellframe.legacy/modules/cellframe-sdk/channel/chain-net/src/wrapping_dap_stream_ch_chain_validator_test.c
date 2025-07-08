#include "wrapping_dap_stream_ch_chain_validator_test.h"
#include "wrapping_dap_sign.h"
//#include "wrapping_cry"
#include "dap_common.h"
#define LOG_TAG "wrapping_dap_chain_net_ch"

#define PVT(a) ((dap_chain_ch_validator_test_t*)((PyDapStreamChChainValidatorTestObject*)a)->rnd)

PyObject *wrapping_dap_stream_ch_chain_validator_test_get_version(PyObject *self, void *closure) {
    (void)closure;
    return Py_BuildValue("s", PVT(self)->header.version);
}
PyObject *wrapping_dap_stream_ch_chain_validator_test_get_flags(PyObject *self, void *closure) {
    (void)closure;
    PyObject *obj_dict = PyDict_New();
    bool auto_proc      = PVT(self)->header.flags & A_PROC ? true : false;
    bool order          = PVT(self)->header.flags & F_ORDR ? true : false;
    bool auto_online    = PVT(self)->header.flags & A_ONLN ? true : false;
    bool auto_update    = PVT(self)->header.flags & A_UPDT ? true : false;
    bool data_signed    = PVT(self)->header.flags & D_SIGN ? true : false;
    bool found_cert     = PVT(self)->header.flags & F_CERT ? true : false;
    PyDict_SetItemString(obj_dict, "AUTO_PROC", auto_proc ? Py_True : Py_False);
    PyDict_SetItemString(obj_dict, "ORDER", order ? Py_True : Py_False);
    PyDict_SetItemString(obj_dict, "AUTO_ONLINE", auto_online ? Py_True : Py_False);
    PyDict_SetItemString(obj_dict, "AUTO_UPDATE", auto_update ? Py_True : Py_False);
    PyDict_SetItemString(obj_dict, "DATA_SIGNED", data_signed ? Py_True : Py_False);
    PyDict_SetItemString(obj_dict, "FOUND_CERT", found_cert ? Py_True : Py_False);
    return obj_dict;
}
PyObject *wrapping_dap_stream_ch_chain_validator_test_get_sign_size(PyObject *self, void *closure) {
    (void)closure;
    return Py_BuildValue("I", PVT(self)->header.sign_size);
}
PyObject *wrapping_dap_stream_ch_chain_validator_test_get_sign_correct(PyObject *self, void *closure) {
    (void)closure;
    if(PVT(self)->header.sign_correct)
        Py_RETURN_TRUE;
    else
        Py_RETURN_FALSE;
}
PyObject *wrapping_dap_stream_ch_chain_validator_test_get_overall_correct(PyObject *self, void *closure) {
    (void)closure;
    if (PVT(self)->header.overall_correct)
        Py_RETURN_TRUE;
    else
        Py_RETURN_FALSE;
}
PyObject *wrapping_dap_stream_ch_chain_validator_test_get_signs(PyObject *self, void *closure) {
    (void)closure;
    size_t l_sign_size_max = 0;
    PyObject *obj_sign_list = PyList_New(0);
    while(l_sign_size_max < PVT(self)->header.sign_size) {
        dap_sign_t *l_sign = (dap_sign_t*)((byte_t*)PVT(self)->sign + l_sign_size_max);
        size_t l_sign_size = dap_sign_get_size(l_sign);
        if (l_sign_size > PVT(self)->header.sign_size) {
            log_it(L_ERROR, "Corrupted sign size");
            Py_XDECREF(obj_sign_list);
            Py_RETURN_NONE;
        }
        PyObject *obj_sign = PyDapSignObject_Cretae(l_sign);
        PyList_Append(obj_sign_list, obj_sign);
        Py_XDECREF((PyObject*)obj_sign);
        l_sign_size_max += l_sign_size;
    }
    return obj_sign_list;
}

PyGetSetDef PyDapStreamChChainValidatorTestGetsSets[] = {
        {
            "version",
            (getter)wrapping_dap_stream_ch_chain_validator_test_get_version,
            NULL,
            NULL,
            NULL
        },
        {
            "flags",
            (getter)wrapping_dap_stream_ch_chain_validator_test_get_flags,
            NULL,
            NULL,
            NULL
        },
        {
            "signSize",
            (getter)wrapping_dap_stream_ch_chain_validator_test_get_sign_size,
            NULL,
            NULL,
            NULL
        },
        {
            "signCorrect",
            (getter)wrapping_dap_stream_ch_chain_validator_test_get_sign_correct,
            NULL,
            NULL,
            NULL
        },
        {
            "overallCorrect",
            (getter)wrapping_dap_stream_ch_chain_validator_test_get_overall_correct,
            NULL,
            NULL,
            NULL
        },
        {
            "signs",
            (getter)wrapping_dap_stream_ch_chain_validator_test_get_signs,
            NULL,
            NULL,
            NULL
        },
        {}
};

void PyDapStreamChChainValidatorTestObject_free(PyDapStreamChChainValidatorTestObject *self){
    DAP_DELETE(self->rnd);
    Py_TYPE(self)->tp_free((PyObject*)self);
}

PyTypeObject PyDapStreamChChainValidatorTestObjectType = DAP_PY_TYPE_OBJECT(
        "CellFrame.Services.StreamChChainValidatorTest",
        sizeof(PyDapStreamChChainValidatorTestObject),
        "Stream ch chain validator test info object",
        .tp_dealloc = (destructor)PyDapStreamChChainValidatorTestObject_free,
        .tp_getset = PyDapStreamChChainValidatorTestGetsSets);
