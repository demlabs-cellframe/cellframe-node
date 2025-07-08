#include "libdap-python.h"
#include "libdap_crypto_data_type.h"

PyObject *get_ENC_DATA_TYPE_RAW(){
    return PyLong_FromLong(DAP_ENC_DATA_TYPE_RAW);
}
PyObject *get_ENC_DATA_TYPE_B64(){
    return PyLong_FromLong(DAP_ENC_DATA_TYPE_B64);
}
PyObject *get_ENC_DATA_TYPE_B64_URLSAFE(){
    return PyLong_FromLong(DAP_ENC_DATA_TYPE_B64_URLSAFE);
}

static PyMethodDef PyCryptoDataTypeObjectMethods[] = {
        {"DAP_ENC_DATA_TYPE_RAW", (PyCFunction)get_ENC_DATA_TYPE_RAW, METH_NOARGS | METH_STATIC, ""},
        {"DAP_ENC_DATA_TYPE_B64", (PyCFunction)get_ENC_DATA_TYPE_B64, METH_NOARGS | METH_STATIC, ""},
        {"DAP_ENC_DATA_TYPE_B64_URLSAFE", (PyCFunction)get_ENC_DATA_TYPE_B64_URLSAFE, METH_NOARGS | METH_STATIC, ""},
        {}
};

PyTypeObject DapCryptoDataTypeObjectType = DAP_PY_TYPE_OBJECT(
        "DAP.Crypto.DataType", sizeof(PyCryptoDataTypeObjecy),
        "Crypto data type objects",
        .tp_methods = PyCryptoDataTypeObjectMethods);
