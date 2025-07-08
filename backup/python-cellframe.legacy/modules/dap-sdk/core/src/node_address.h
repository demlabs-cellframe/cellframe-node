#pragma once
#include <Python.h>
#include "dap_common.h"

typedef struct PyDapNodeAddr
{
    PyObject_HEAD
    dap_stream_node_addr_t addr;
}PyDapNodeAddrObject;

extern PyTypeObject DapNodeAddrObjectType;

DAP_STATIC_INLINE bool PyDapNodeAddrObject_Check(PyObject *self) {
    return PyObject_TypeCheck(self, &DapNodeAddrObjectType);
}
