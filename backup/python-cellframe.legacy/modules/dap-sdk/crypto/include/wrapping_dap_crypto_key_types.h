#pragma once
#include "Python.h"

typedef struct PyDapCryptoKeyTypes{
    PyObject_HEAD
}PyDapCryptoKeyTypesObject;

PyObject *ENC_KEY_TYPE_IAES(PyObject *self, void *closure);
PyObject *ENC_KEY_TYPE_OAES(PyObject *self, void *closure);
PyObject *ENC_KEY_TYPE_BF_CBC(PyObject *self, void *closure);
PyObject *ENC_KEY_TYPE_BF_OFB(PyObject *self, void *closure);
PyObject *ENC_KEY_TYPE_GOST_OFB(PyObject *self, void *closure);
PyObject *ENC_KEY_TYPE_KUZN_OFB(PyObject *self, void *closure);
PyObject *ENC_KEY_TYPE_SALSA2012(PyObject *self, void *closure);
PyObject *ENC_KEY_TYPE_SEED_OFB(PyObject *self, void *closure);
PyObject *ENC_KEY_TYPE_RLWE_NEWHOPE_CPA_KEM(PyObject *self, void *closure);
PyObject *ENC_KEY_TYPE_MSRLN(PyObject *self, void *closure);
PyObject *ENC_KEY_TYPE_RLWE_MSRLN16(PyObject *self, void *closure);
PyObject *ENC_KEY_TYPE_RLWE_BCNS15(PyObject *self, void *closure);
PyObject *ENC_KEY_TYPE_LWE_FRODO(PyObject *self, void *closure);
PyObject *ENC_KEY_TYPE_CODE_MCBITS(PyObject *self, void *closure);
PyObject *ENC_KEY_TYPE_NTRU(PyObject *self, void *closure);
PyObject *ENC_KEY_TYPE_MLWE_KYBER(PyObject *self, void *closure);
PyObject *ENC_KEY_TYPE_SIG_PICNIC(PyObject *self, void *closure);
PyObject *ENC_KEY_TYPE_SIG_BLISS(PyObject *self, void  *closure);
PyObject *ENC_KEY_TYPE_SIG_TESLA(PyObject *self, void *closure);
PyObject *ENC_KEY_TYPE_SIG_DILITHIUM(PyObject *self, void *closure);
PyObject *ENC_KEY_TYPE_SIG_RINGCT20(PyObject *self, void *closure);
PyObject *ENC_KEY_TYPE_KEM_KYBER512(PyObject *self, void *closure);
PyObject *ENC_KEY_TYPE_SIG_FALCON(PyObject *self, void *closure);
#ifdef DAP_PQLR
// QApp PQLR library integration
PyObject *ENC_KEY_TYPE_PQLR_SIG_DILITHIUM(PyObject *self, void *closure);
PyObject *ENC_KEY_TYPE_PQLR_SIG_FALCON(PyObject *self, void *closure);
PyObject *ENC_KEY_TYPE_PQLR_SIG_SPHINCS(PyObject *self, void *closure);
PyObject *ENC_KEY_TYPE_PQLR_KEM_SABER(PyObject *self, void *closure);
PyObject *ENC_KEY_TYPE_PQLR_KEM_MCELIECE(PyObject *self, void *closure);
PyObject *ENC_KEY_TYPE_PQLR_KEM_NEWHOPE(PyObject *self, void *closure);
#endif
PyObject *ENC_KEY_TYPE_LAST(PyObject *self, void *closure);

//PyObject *ENC_KEY_TYPE_NULL(PyObject *self, void *closure);


/*
#ifdef DAP_PQLR
    // QApp PQLR library integration

    DAP_ENC_KEY_TYPE_LAST = DAP_ENC_KEY_TYPE_PQLR_KEM_NEWHOPE,
#else
    DAP_ENC_KEY_TYPE_LAST = DAP_ENC_KEY_TYPE_SIG_FALCON,
#endif
 */

extern PyTypeObject DapCryptoKeyTypesObjectType;
