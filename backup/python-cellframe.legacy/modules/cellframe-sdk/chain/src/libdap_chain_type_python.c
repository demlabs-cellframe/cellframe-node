#include "libdap-python.h"
#include "libdap_chain_type_python.h"


static PyMethodDef DapChainTypeMethods[] = {
        {"CHAIN_TYPE_INVALID", (PyCFunction)CHAIN_TYPE_INVALID_PY, METH_NOARGS|METH_STATIC, ""},
        {"CHAIN_TYPE_TOKEN", (PyCFunction)CHAIN_TYPE_TOKEN_PY, METH_NOARGS|METH_STATIC, ""},
        {"CHAIN_TYPE_EMISSION", (PyCFunction)CHAIN_TYPE_EMISSION_PY, METH_NOARGS|METH_STATIC, ""},
        {"CHAIN_TYPE_TX", (PyCFunction)CHAIN_TYPE_TX_PY, METH_NOARGS|METH_STATIC, ""},
        {"CHAIN_TYPE_CA", (PyCFunction)CHAIN_TYPE_CA_PY, METH_NOARGS|METH_STATIC, ""},
        {"CHAIN_TYPE_SIGNER", (PyCFunction) CHAIN_TYPE_SIGNER_PY, METH_NOARGS|METH_STATIC, ""},
        {"CHAIN_TYPE_DECREE", (PyCFunction)CHAIN_TYPE_DECREE_PY, METH_NOARGS|METH_STATIC, ""},
        {"CHAIN_TYPE_ANCHOR", (PyCFunction)CHAIN_TYPE_ANCHOR_PY, METH_NOARGS|METH_STATIC, ""},
        {}
};

PyTypeObject DapChainTypeObjectType = DAP_PY_TYPE_OBJECT(
        "CellFrame.ChainType", sizeof(PyChainTypeObject),
        "Chain type objects",
        .tp_methods = DapChainTypeMethods);

PyObject *s_chain_type_create(dap_chain_type_t a_type) {
    PyChainTypeObject *obj_type = PyObject_New(PyChainTypeObject, &DapChainTypeObjectType);
    obj_type->chain_type = a_type;
    return (PyObject*)obj_type;
}

PyObject *CHAIN_TYPE_INVALID_PY(__attribute__((unused)) PyObject *self, __attribute__((unused)) PyObject *args)
{
    return s_chain_type_create(CHAIN_TYPE_INVALID);
}
PyObject *CHAIN_TYPE_TOKEN_PY(__attribute__((unused)) PyObject *self, __attribute__((unused)) PyObject *args)
{
    return s_chain_type_create(CHAIN_TYPE_TOKEN);
}
PyObject *CHAIN_TYPE_EMISSION_PY(__attribute__((unused)) PyObject *self, __attribute__((unused)) PyObject *args)
{
    return s_chain_type_create(CHAIN_TYPE_EMISSION);
}
PyObject *CHAIN_TYPE_TX_PY(__attribute__((unused)) PyObject *self, __attribute__((unused)) PyObject *args)
{
    return s_chain_type_create(CHAIN_TYPE_TX);
}
PyObject* CHAIN_TYPE_CA_PY(__attribute__((unused)) PyObject *self, __attribute__((unused)) PyObject *args)
{
    return s_chain_type_create(CHAIN_TYPE_CA);
}
PyObject* CHAIN_TYPE_SIGNER_PY(__attribute__((unused)) PyObject *self, __attribute__((unused)) PyObject *args)
{
    return s_chain_type_create(CHAIN_TYPE_SIGNER);
}
PyObject* CHAIN_TYPE_DECREE_PY(__attribute__((unused)) PyObject *self, __attribute__((unused)) PyObject *args)
{
    return s_chain_type_create(CHAIN_TYPE_DECREE);
}
PyObject* CHAIN_TYPE_ANCHOR_PY(__attribute__((unused)) PyObject *self, __attribute__((unused)) PyObject *args)
{
    return s_chain_type_create(CHAIN_TYPE_ANCHOR);
}
