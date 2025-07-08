#include "libdap-python.h"
#include "libdap_crypto_key_python.h"

PyTypeObject PyCryptoKeyObjectType = DAP_PY_TYPE_OBJECT(
        "DAP.Crypto.Key", sizeof(PyCryptoKeyObject),
        "Crypto key objects",
        .tp_dealloc = (destructor)PyCryptoKeyObject_dealloc);

bool PyCryptoKeyObject_check(PyObject *self){
    return PyObject_TypeCheck(self, &PyCryptoKeyObjectType);
}

void PyCryptoKeyObject_dealloc(PyCryptoKeyObject *cryptoObject){
//    dap_enc_key_delete(cryptoObject->key);
    PyTypeObject *l_obj_type = Py_TYPE(cryptoObject);
    if (l_obj_type->tp_free)
        l_obj_type->tp_free(cryptoObject);
//    Py_TYPE((PyObject*)cryptoObject)->tp_free((PyObject*)cryptoObject);
//    Py_TYPE(cryptoObject)->tp_free((PyObject*)cryptoObject);
}
