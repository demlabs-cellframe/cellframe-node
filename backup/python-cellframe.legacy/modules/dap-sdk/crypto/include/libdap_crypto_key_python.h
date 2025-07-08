#ifndef LIBDAP_CRYPTO_KEY_PYTHON_H_
#define LIBDAP_CRYPTO_KEY_PYTHON_H_

#include "Python.h"
#include "dap_enc_key.h"
#ifdef __cplusplus
extern "C" {
#endif

typedef struct PyCryptoKey{
    PyObject_HEAD
    dap_enc_key_t *key;
}PyCryptoKeyObject;

bool PyCryptoKeyObject_check(PyObject *self);
void PyCryptoKeyObject_dealloc(PyCryptoKeyObject *cryptoObject);

extern PyTypeObject PyCryptoKeyObjectType;

#ifdef __cplusplus
}
#endif

#endif //LIBDAP_CRYPTO_KEY_PYTHON_H_
