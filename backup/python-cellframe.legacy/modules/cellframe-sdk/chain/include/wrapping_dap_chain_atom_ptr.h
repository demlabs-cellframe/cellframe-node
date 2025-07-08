#pragma once

#include <Python.h>
#include "dap_chain.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct PyChainAtom{
    PyObject_HEAD
    dap_chain_atom_ptr_t atom;
    size_t atom_size;
}PyChainAtomObject;

extern PyTypeObject DapChainAtomPtrObjectType;

bool PyDapChainAtomPtr_Check(PyObject *obj);

#ifdef __cplusplus
}
#endif
