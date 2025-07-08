#include "Python.h"
#include "dap_chain_cs_dag_poa.h"
#include "libdap-chain-python.h"
#include "wrapping_dap_chain_cs_dag_event.h"

typedef struct PyDapChainCsDagPoa{
    PyObject_HEAD
}PyDapChainCsDagPoaObject;

PyObject* wrapping_dap_chain_cs_dag_poa_presign_callback_set(PyObject *self, PyObject *args);

extern PyTypeObject DapChainCsDagPoaObjectType;
