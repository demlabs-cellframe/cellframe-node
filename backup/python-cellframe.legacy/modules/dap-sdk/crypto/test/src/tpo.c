#include "tpo.h"

PyObject *TPO_init(PyObject *self, PyObject *args){
    if (dap_crypto_init() != 0)
            return NULL;
    return PyLong_FromLong(0);
}
PyObject *TPO_deinit(PyObject *self, PyObject *args){
    dap_common_deinit();
    return PyLong_FromLong(0);
}

PyMODINIT_FUNC PyInit_libTPO(void){

    if (PyType_Ready(&dapCrypto_dapCryptoType) < 0 ||
            PyType_Ready(&CryptoKeyTypeObjecy_CryptoKeyTypeObjecyType) < 0 ||
            PyType_Ready(&CryptoDataTypeObjecy_CryptoDataTypeObjecyType) < 0)
               return NULL;

    PyObject *module = PyModule_Create(&TPOModule);
    PyModule_AddObject(module, "Crypto", (PyObject*)&dapCrypto_dapCryptoType);
    PyModule_AddObject(module, "CryptoKeyType", (PyObject*)&CryptoKeyTypeObjecy_CryptoKeyTypeObjecyType);
    PyModule_AddObject(module, "CryptoDataType", (PyObject*)&CryptoDataTypeObjecy_CryptoDataTypeObjecyType);
    return module;
}

