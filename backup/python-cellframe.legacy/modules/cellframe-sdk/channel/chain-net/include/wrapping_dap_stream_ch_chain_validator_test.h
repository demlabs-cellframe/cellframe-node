#include "Python.h"
#include "dap_chain_net_ch.h"

typedef struct PyDapStreamChChainValidatorTest{
    PyObject_HEAD
    dap_chain_ch_validator_test_t *rnd;
}PyDapStreamChChainValidatorTestObject;

void PyDapStreamChChainValidatorTestObject_free(PyDapStreamChChainValidatorTestObject *self);

PyObject *wrapping_dap_stream_ch_chain_validator_test_get_version(PyObject *self, void *closure);
PyObject *wrapping_dap_stream_ch_chain_validator_test_get_flags(PyObject *self, void *closure);
PyObject *wrapping_dap_stream_ch_chain_validator_test_get_sign_size(PyObject *self, void *closure);
PyObject *wrapping_dap_stream_ch_chain_validator_test_get_sign_correct(PyObject *self, void *closure);
PyObject *wrapping_dap_stream_ch_chain_validator_test_get_overall_correct(PyObject *self, void *closure);
PyObject *wrapping_dap_stream_ch_chain_validator_test_get_signs(PyObject *self, void *closure);

extern PyTypeObject PyDapStreamChChainValidatorTestObjectType;
