#include "wrapping_dap_crypto_key_types.h"
#include "libdap-python.h"
#include "wrapping_dap_enc_key_type.h"
#include "dap_enc_key.h"

static PyGetSetDef PyCryptoKeyTypesObjectGetSetDef [] = {
        {"IAES", ENC_KEY_TYPE_IAES, NULL, NULL, "Get type is AES"},
        {"OAES", ENC_KEY_TYPE_OAES, NULL, NULL, "Get type is OES"},
        {"BF_CBC", ENC_KEY_TYPE_BF_CBC, NULL, NULL, "Get type is BF CBC"},
        {"BF_OFB", ENC_KEY_TYPE_BF_OFB, NULL, NULL, "Get type is BF OFB"},
        {"GOST_OFB", ENC_KEY_TYPE_GOST_OFB, NULL, NULL, "Get type is GOST OFB"},
        {"KUZN_OFB", ENC_KEY_TYPE_KUZN_OFB, NULL, NULL, "Get type is KUZN OFB"},
        {"SALSA2012", ENC_KEY_TYPE_SALSA2012, NULL, NULL, "Get type is SALSA2012"},
        {"SEED_OFB", ENC_KEY_TYPE_SEED_OFB, NULL, NULL, "Get type is SEED OFB"},
        {"RLWE_NEWHOPE_CPA_KEM", ENC_KEY_TYPE_RLWE_NEWHOPE_CPA_KEM, NULL, NULL, "Get type is RLWE NEWHOPE CPA KEM"},
        {"MSRLN", ENC_KEY_TYPE_MSRLN, NULL, NULL, "Get type is MSRLN"},
        {"RLWE_MSRLN16", ENC_KEY_TYPE_RLWE_MSRLN16, NULL, NULL, "Get type is RLWE MSRLN16"},
        {"RLWE_BCNS15", ENC_KEY_TYPE_RLWE_BCNS15, NULL, NULL, "Get type is RLWE BCNS15"},
        {"LWE_FRODO", ENC_KEY_TYPE_LWE_FRODO, NULL, NULL, "Get type is LWE FRODO"},
        {"CODE_MCBITS", ENC_KEY_TYPE_CODE_MCBITS, NULL, NULL, "Get type is CODE MCBITS"},
        {"NTRU", ENC_KEY_TYPE_NTRU, NULL, NULL, "Get type is NTRU"},
        {"MLWE_KYBER", ENC_KEY_TYPE_MLWE_KYBER, NULL, NULL, "Get type is MLWE KYBER"},
        {"SIG_PICNIC", ENC_KEY_TYPE_SIG_PICNIC, NULL, NULL, "Get type is SIG PICNIC"},
        {"SIG_BLISS", ENC_KEY_TYPE_SIG_BLISS, NULL, NULL, "Get type is SIG BLISS"},
        {"SIG_TESLA", ENC_KEY_TYPE_SIG_TESLA, NULL, NULL, "Get type is SIG TESLA"},
        {"SIG_DILITHIUM", ENC_KEY_TYPE_SIG_DILITHIUM, NULL, NULL, "Get type is SIG DILITHIUM"},
        {"SIG_RINGCT20", ENC_KEY_TYPE_SIG_RINGCT20, NULL, NULL, "Get type is SIG RINGCT20"},
        {"KEM_KYBER512", ENC_KEY_TYPE_KEM_KYBER512, NULL, NULL, "Get type is KEM KYBER512"},
        {"SIG_FALCON", ENC_KEY_TYPE_SIG_FALCON, NULL, NULL, "Get type is SIG FALNCON"},
#ifdef DAP_PQLR
        // QApp PQLR library integration
        {"PQLR_SIG_DILITHIUM", ENC_KEY_TYPE_PQLR_SIG_DILITHIUM, NULL, NULL, "Get type is PQLR SIG DILITHIUM"},
        {"PQLR_SIG_FALCON", ENC_KEY_TYPE_PQLR_SIG_FALCON, NULL, NULL, "Get type is PQLR SIG FALCON"},
        {"PQLR_SIG_SPHINCS", ENC_KEY_TYPE_PQLR_SIG_SPHINCS, NULL, NULL, "Get type is PQLR SIG SPHINCS"},
        {"PQLR_KEM_SABER", ENC_KEY_TYPE_PQLR_KEM_SABER, NULL, NULL, "Get type is PQLR KEM SABER"},
        {"PQLR_KEM_MCELIECE", ENC_KEY_TYPE_PQLR_KEM_MCELIECE, NULL, NULL, "Get type is PQLR KEM MCELICE"},
        {"PQLR_KEM_NEWHOPE", ENC_KEY_TYPE_PQLR_KEM_NEWHOPE, NULL, NULL, "Get type is KEM NEWHOPE"},
#endif
        {"LAST", ENC_KEY_TYPE_LAST, NULL, NULL, "Get type is LAST"},
        {}
};

PyTypeObject DapCryptoKeyTypesObjectType = DAP_PY_TYPE_OBJECT(
        "DAP.Crypto.KeyTypes", sizeof(PyDapCryptoKeyTypesObject),
        "Crypto key types objects",
        .tp_getset = PyCryptoKeyTypesObjectGetSetDef
//        .tp_methods = PyCryptoKeyTypeObjectMethods
);

PyObject *ENC_KEY_TYPE_IAES(PyObject *self, void *closure){
    (void)self;
    (void)closure;
    PyCryptoKeyTypeObject *type = PyObject_New(PyCryptoKeyTypeObject, &DapCryptoKeyTypeObjectType);
    type->type = DAP_ENC_KEY_TYPE_IAES;
    return (PyObject*)type;
}
PyObject *ENC_KEY_TYPE_OAES(PyObject *self, void *closure){
    (void)self;
    (void)closure;
    PyCryptoKeyTypeObject *obj_type = PyObject_New(PyCryptoKeyTypeObject, &DapCryptoKeyTypesObjectType);
    obj_type->type = DAP_ENC_KEY_TYPE_OAES;
    return (PyObject*)obj_type;
}

PyObject *ENC_KEY_TYPE_BF_CBC(PyObject *self, void *closure){
    (void)self;
    (void)closure;
    PyCryptoKeyTypeObject *obj_type = PyObject_New(PyCryptoKeyTypeObject, &DapCryptoKeyTypesObjectType);
    obj_type->type = DAP_ENC_KEY_TYPE_BF_CBC;
    return (PyObject*)obj_type;
}
PyObject *ENC_KEY_TYPE_BF_OFB(PyObject *self, void *closure){
    (void)self;
    (void)closure;
    PyCryptoKeyTypeObject *obj_type = PyObject_New(PyCryptoKeyTypeObject, &DapCryptoKeyTypesObjectType);
    obj_type->type = DAP_ENC_KEY_TYPE_BF_OFB;
    return (PyObject*)obj_type;
}
PyObject *ENC_KEY_TYPE_GOST_OFB(PyObject *self, void *closure){
    (void)self;
    (void)closure;
    PyCryptoKeyTypeObject *obj_type = PyObject_New(PyCryptoKeyTypeObject, &DapCryptoKeyTypesObjectType);
    obj_type->type = DAP_ENC_KEY_TYPE_GOST_OFB;
    return (PyObject*)obj_type;
}
PyObject *ENC_KEY_TYPE_KUZN_OFB(PyObject *self, void *closure){
    (void)self;
    (void)closure;
    PyCryptoKeyTypeObject *obj_type = PyObject_New(PyCryptoKeyTypeObject, &DapCryptoKeyTypesObjectType);
    obj_type->type = DAP_ENC_KEY_TYPE_KUZN_OFB;
    return (PyObject*)obj_type;
}
PyObject *ENC_KEY_TYPE_SALSA2012(PyObject *self, void *closure){
    (void)self;
    (void)closure;
    PyCryptoKeyTypeObject *obj_type = PyObject_New(PyCryptoKeyTypeObject, &DapCryptoKeyTypesObjectType);
    obj_type->type = DAP_ENC_KEY_TYPE_SALSA2012;
    return (PyObject*)obj_type;
}
PyObject *ENC_KEY_TYPE_SEED_OFB(PyObject *self, void *closure){
    (void)self;
    (void)closure;
    PyCryptoKeyTypeObject *obj_type = PyObject_New(PyCryptoKeyTypeObject, &DapCryptoKeyTypesObjectType);
    obj_type->type = DAP_ENC_KEY_TYPE_SEED_OFB;
    return (PyObject*)obj_type;
}
PyObject *ENC_KEY_TYPE_RLWE_NEWHOPE_CPA_KEM(PyObject *self, void *closure){
    (void)self;
    (void)closure;
    PyCryptoKeyTypeObject *obj_type = PyObject_New(PyCryptoKeyTypeObject, &DapCryptoKeyTypesObjectType);
    obj_type->type = DAP_ENC_KEY_TYPE_RLWE_NEWHOPE_CPA_KEM;
    return (PyObject*)obj_type;
}
PyObject *ENC_KEY_TYPE_MSRLN(PyObject *self, void *closure){
    (void)self;
    (void)closure;
    PyCryptoKeyTypeObject *obj_type = PyObject_New(PyCryptoKeyTypeObject, &DapCryptoKeyTypesObjectType);
    obj_type->type = DAP_ENC_KEY_TYPE_MSRLN;
    return (PyObject*)obj_type;
}
PyObject *ENC_KEY_TYPE_RLWE_MSRLN16(PyObject *self, void *closure){
    (void)self;
    (void)closure;
    PyCryptoKeyTypeObject *obj_type = PyObject_New(PyCryptoKeyTypeObject, &DapCryptoKeyTypesObjectType);
    obj_type->type = DAP_ENC_KEY_TYPE_RLWE_MSRLN16;
    return (PyObject*)obj_type;
}
PyObject *ENC_KEY_TYPE_RLWE_BCNS15(PyObject *self, void *closure){
    (void)self;
    (void)closure;
    PyCryptoKeyTypeObject *obj_type = PyObject_New(PyCryptoKeyTypeObject, &DapCryptoKeyTypesObjectType);
    obj_type->type = DAP_ENC_KEY_TYPE_RLWE_BCNS15;
    return (PyObject*)obj_type;
}
PyObject *ENC_KEY_TYPE_LWE_FRODO(PyObject *self, void *closure){
    (void)self;
    (void)closure;
    PyCryptoKeyTypeObject *obj_type = PyObject_New(PyCryptoKeyTypeObject, &DapCryptoKeyTypesObjectType);
    obj_type->type = DAP_ENC_KEY_TYPE_LWE_FRODO;
    return (PyObject*)obj_type;
}
PyObject *ENC_KEY_TYPE_CODE_MCBITS(PyObject *self, void *closure){
    (void)self;
    (void)closure;
    PyCryptoKeyTypeObject *obj_type = PyObject_New(PyCryptoKeyTypeObject, &DapCryptoKeyTypesObjectType);
    obj_type->type = DAP_ENC_KEY_TYPE_CODE_MCBITS;
    return (PyObject*)obj_type;
}
PyObject *ENC_KEY_TYPE_NTRU(PyObject *self, void *closure){
    (void)self;
    (void)closure;
    PyCryptoKeyTypeObject *obj_type = PyObject_New(PyCryptoKeyTypeObject, &DapCryptoKeyTypesObjectType);
    obj_type->type = DAP_ENC_KEY_TYPE_NTRU;
    return (PyObject*)obj_type;
}
PyObject *ENC_KEY_TYPE_MLWE_KYBER(PyObject *self, void *closure){
    (void)self;
    (void)closure;
    PyCryptoKeyTypeObject *obj_type = PyObject_New(PyCryptoKeyTypeObject, &DapCryptoKeyTypesObjectType);
    obj_type->type = DAP_ENC_KEY_TYPE_MLWE_KYBER;
    return (PyObject*)obj_type;
}
PyObject *ENC_KEY_TYPE_SIG_PICNIC(PyObject *self, void *closure){
    (void)self;
    (void)closure;
    PyCryptoKeyTypeObject *obj_type = PyObject_New(PyCryptoKeyTypeObject, &DapCryptoKeyTypesObjectType);
    obj_type->type = DAP_ENC_KEY_TYPE_SIG_PICNIC;
    return (PyObject*)obj_type;
}
PyObject *ENC_KEY_TYPE_SIG_BLISS(PyObject *self, void  *closure){
    (void)self;
    (void)closure;
    PyCryptoKeyTypeObject *obj_type = PyObject_New(PyCryptoKeyTypeObject, &DapCryptoKeyTypesObjectType);
    obj_type->type = DAP_ENC_KEY_TYPE_SIG_BLISS;
    return (PyObject*)obj_type;
}
PyObject *ENC_KEY_TYPE_SIG_TESLA(PyObject *self, void *closure){
    (void)self;
    (void)closure;
    PyCryptoKeyTypeObject *obj_type = PyObject_New(PyCryptoKeyTypeObject, &DapCryptoKeyTypesObjectType);
    obj_type->type = DAP_ENC_KEY_TYPE_SIG_TESLA;
    return (PyObject*)obj_type;
}
PyObject *ENC_KEY_TYPE_SIG_DILITHIUM(PyObject *self, void *closure){
    (void)self;
    (void)closure;
    PyCryptoKeyTypeObject *obj_type = PyObject_New(PyCryptoKeyTypeObject, &DapCryptoKeyTypesObjectType);
    obj_type->type = DAP_ENC_KEY_TYPE_SIG_DILITHIUM;
    return (PyObject*)obj_type;
}
PyObject *ENC_KEY_TYPE_SIG_RINGCT20(PyObject *self, void *closure){
    (void)self;
    (void)closure;
    PyCryptoKeyTypeObject *obj_type = PyObject_New(PyCryptoKeyTypeObject, &DapCryptoKeyTypesObjectType);
    obj_type->type = DAP_ENC_KEY_TYPE_SIG_RINGCT20;
    return (PyObject*)obj_type;
}
PyObject *ENC_KEY_TYPE_KEM_KYBER512(PyObject *self, void *closure){
    (void)self;
    (void)closure;
    PyCryptoKeyTypeObject *obj_type = PyObject_New(PyCryptoKeyTypeObject, &DapCryptoKeyTypesObjectType);
    obj_type->type = DAP_ENC_KEY_TYPE_KEM_KYBER512;
    return (PyObject*)obj_type;
}
PyObject *ENC_KEY_TYPE_SIG_FALCON(PyObject *self, void *closure){
    (void)self;
    (void)closure;
    PyCryptoKeyTypeObject *obj_type = PyObject_New(PyCryptoKeyTypeObject, &DapCryptoKeyTypesObjectType);
    obj_type->type = DAP_ENC_KEY_TYPE_SIG_FALCON;
    return (PyObject*)obj_type;
}
#ifdef DAP_PQLR
// QApp PQLR library integration
PyObject *ENC_KEY_TYPE_PQLR_SIG_DILITHIUM(PyObject *self, void *closure){
    (void)self;
    (void)closure;
    PyCryptoKeyTypeObject *obj_type = PyObject_New(PyCryptoKeyTypeObject, &DapCryptoKeyTypesObjectType);
    obj_type->type = DAP_ENC_KEY_TYPE_PQLR_SIG_DILITHIUM;
    return (PyObject*)obj_type;
}
PyObject *ENC_KEY_TYPE_PQLR_SIG_FALCON(PyObject *self, void *closure){
    (void)self;
    (void)closure;
    PyCryptoKeyTypeObject *obj_type = PyObject_New(PyCryptoKeyTypeObject, &DapCryptoKeyTypesObjectType);
    obj_type->type = DAP_ENC_KEY_TYPE_PQLR_SIG_FALCON;
    return (PyObject*)obj_type;
}
PyObject *ENC_KEY_TYPE_PQLR_SIG_SPHINCS(PyObject *self, void *closure){
    (void)self;
    (void)closure;
    PyCryptoKeyTypeObject *obj_type = PyObject_New(PyCryptoKeyTypeObject, &DapCryptoKeyTypesObjectType);
    obj_type->type = DAP_ENC_KEY_TYPE_PQLR_SIG_SPHINCS;
    return (PyObject*)obj_type;
}
PyObject *ENC_KEY_TYPE_PQLR_KEM_SABER(PyObject *self, void *closure){
    (void)self;
    (void)closure;
    PyCryptoKeyTypeObject *obj_type = PyObject_New(PyCryptoKeyTypeObject, &DapCryptoKeyTypesObjectType);
    obj_type->type = DAP_ENC_KEY_TYPE_PQLR_KEM_SABER;
    return (PyObject*)obj_type;
}
PyObject *ENC_KEY_TYPE_PQLR_KEM_MCELIECE(PyObject *self, void *closure){
    (void)self;
    (void)closure;
    PyCryptoKeyTypeObject *obj_type = PyObject_New(PyCryptoKeyTypeObject, &DapCryptoKeyTypesObjectType);
    obj_type->type = DAP_ENC_KEY_TYPE_PQLR_KEM_MCELIECE;
    return (PyObject*)obj_type;
}
PyObject *ENC_KEY_TYPE_PQLR_KEM_NEWHOPE(PyObject *self, void *closure){
    (void)self;
    (void)closure;
    PyCryptoKeyTypeObject *obj_type = PyObject_New(PyCryptoKeyTypeObject, &DapCryptoKeyTypesObjectType);
    obj_type->type = DAP_ENC_KEY_TYPE_PQLR_KEM_NEWHOPE;
    return (PyObject*)obj_type;
}
#endif
PyObject *ENC_KEY_TYPE_LAST(PyObject *self, void *closure){
    (void)self;
    (void)closure;
    PyCryptoKeyTypeObject *obj_type = PyObject_New(PyCryptoKeyTypeObject, &DapCryptoKeyTypesObjectType);
    obj_type->type = DAP_ENC_KEY_TYPE_LAST;
    return (PyObject*)obj_type;
}
