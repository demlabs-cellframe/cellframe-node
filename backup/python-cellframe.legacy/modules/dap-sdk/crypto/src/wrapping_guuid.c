#include "wrapping_guuid.h"
#include "libdap-python.h"

static PyMethodDef PyCryptoGUUID_Methods[] = {
    {"generate", wrapping_guuid_generate, METH_NOARGS | METH_STATIC, ""},
    {"compose", wrapping_guuid_compose, METH_VARARGS | METH_STATIC, ""},
    {NULL, NULL, 0, NULL}
};

int PyCryptoGUUID_init(PyCryptoGUUIDObject *self, PyObject *argv, PyObject *kwds){
    const char *in_str_hex;
    char *kwords[] = {
        "hex",
        NULL
    };
    if (!PyArg_ParseTupleAndKeywords(argv, kwds, "s", kwords, &in_str_hex))
        return -1;
    bool success = false;
    self->guuid = dap_guuid_from_hex_str(in_str_hex, &success);
    if (!success)
    {
        PyErr_SetString(PyExc_SystemError, "Can't parse guuid from string");
        return -2;
    }
    return 0;
}

PyObject *wrapping_guuid_compose(PyObject *self, PyObject *argv){
    (void)self;
    uint64_t net_id = 0;
    uint64_t service_id = 0;
    
    if (!PyArg_ParseTuple(argv, "KK", &net_id, &service_id)) {
        return NULL;
    }
    PyCryptoGUUIDObject *obj_guuid = PyObject_New(PyCryptoGUUIDObject, &PyCryptoGUUIDObjectType);
    obj_guuid->guuid = dap_guuid_compose(net_id, service_id);
    return (PyObject*)obj_guuid;
}

PyObject *wrapping_guuid_generate(PyObject *self, PyObject *argv){
    (void)self;
    PyCryptoGUUIDObject *obj = PyObject_New(PyCryptoGUUIDObject, &PyCryptoGUUIDObjectType);
    obj->guuid = dap_guuid_new();
    return (PyObject*)obj;
}

PyObject *PyCryptoGUUID_toStr(PyCryptoGUUIDObject *self){
    const char *l_str = dap_guuid_to_hex_str(self->guuid);
    return Py_BuildValue("s", l_str);
}

PyObject *PyCryptoGUUID_compare(PyCryptoGUUIDObject *self, PyObject *other, int op) {
    if (!PyObject_TypeCheck(other, &PyCryptoGUUIDObjectType)){
        Py_RETURN_FALSE;
    }
    switch (op)
    {
    case Py_EQ:
        if (EQUAL_128(self->guuid.raw, ((PyCryptoGUUIDObject*)other)->guuid.raw))
            Py_RETURN_TRUE;
        else 
            Py_RETURN_FALSE;
        
    case Py_NE:
        if (!EQUAL_128(self->guuid.raw, ((PyCryptoGUUIDObject*)other)->guuid.raw))
            Py_RETURN_TRUE;
        else 
            Py_RETURN_FALSE;
    default:
        Py_RETURN_FALSE;
    }
}

PyTypeObject PyCryptoGUUIDObjectType = DAP_PY_TYPE_OBJECT("DAP.Crypto.GUUID", sizeof(PyCryptoGUUIDObject),
                                                          "GUUID for using dap-sdk and cellframe-sdk",
                                                          .tp_str = (reprfunc)PyCryptoGUUID_toStr,
                                                          .tp_methods = PyCryptoGUUID_Methods,
                                                          .tp_richcompare = (richcmpfunc)PyCryptoGUUID_compare,
                                                          .tp_init = (initproc)PyCryptoGUUID_init);
