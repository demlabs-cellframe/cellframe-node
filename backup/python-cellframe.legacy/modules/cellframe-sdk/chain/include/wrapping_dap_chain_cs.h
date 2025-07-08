#ifndef _WRAPPING_DAP_CHAIN_CS_
#define _WRAPPING_DAP_CHAIN_CS_

#include "Python.h"
#include "dap_chain_cs.h"
#include "libdap-chain-python.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct PyDapChainCs{
    PyObject_HEAD
    char *cs_name;
    dap_chain_callback_new_cfg_t callback_new_cfg;
}PyDapChainCsObject;
static PyObject *binded_object_callback_new_cfg = NULL;

PyObject *DapChainCSObject_new(PyTypeObject *type_object, PyObject *args, PyObject *kwds);

int dap_chain_cs_init_py(void);
void dap_chain_cs_deinit_py(void);

PyObject *dap_chain_cs_add_py (PyObject *self, PyObject *args);
PyObject *dap_chain_cs_create_py(PyObject *self, PyObject *args);

PyObject *dap_chain_class_add_py (PyObject *self, PyObject *args);
PyObject *dap_chain_class_create_py(PyObject *self, PyObject *args);

extern PyTypeObject DapChainCsObjectType;

#ifdef __cplusplus
}
#endif

#endif //_WRAPPING_DAP_CHAIN_CS_
