#include "libdap-python.h"
#include "wrapping_dap_enc_key_type.h"


PyTypeObject DapCryptoKeyTypeObjectType = DAP_PY_TYPE_OBJECT(
        "DAP.Crypto.KeyType", sizeof(PyCryptoKeyTypeObject),
        "Crypto keys type objects",
        .tp_str = CryptoKeyType_toStr,
        .tp_richcompare = CryptoKeyType_richcompare);

PyObject *CryptoKeyType_toStr(PyObject *self){
    dap_enc_key_type_t l_type = ((PyCryptoKeyTypeObject*)self)->type;
    return Py_BuildValue("s", dap_enc_get_type_name(l_type));
}

PyObject *CryptoKeyType_richcompare(PyObject *self, PyObject *other, int op){
    if (!PyObject_TypeCheck(other, &DapCryptoKeyTypeObjectType)){
        PyErr_SetString(PyExc_AttributeError, "The object with which the comparison is made must be of type KeyType.");
        return NULL;
    }
    if (op == Py_EQ){
        if (((PyCryptoKeyTypeObject*)self)->type == (((PyCryptoKeyTypeObject*)other)->type))
            Py_RETURN_TRUE;
        else
            Py_RETURN_FALSE;
    }
    else if (op == Py_NE) {
        if (((PyCryptoKeyTypeObject*)self)->type != (((PyCryptoKeyTypeObject*)other)->type))
            Py_RETURN_TRUE;
        else
            Py_RETURN_FALSE;
    } else {
        return PyExc_NotImplementedError;
    }
}
