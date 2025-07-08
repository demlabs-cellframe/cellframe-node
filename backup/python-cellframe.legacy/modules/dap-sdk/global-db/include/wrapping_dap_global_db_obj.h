#pragma once

#include "Python.h"
#include "dap_global_db.h"

typedef struct PyDapGlobalDBObj{
    PyObject_HEAD
    dap_global_db_obj_t obj;
}PyDapGlobalDBContainerObject;


//Attributes
PyObject *wrapping_dap_global_db_obj_get_id(PyObject *self, void *closure);
PyObject *wrapping_dap_global_db_obj_get_key(PyObject *self, void *closure);
PyObject *wrapping_dap_global_db_obj_get_value(PyObject *self, void *closure);

extern PyTypeObject DapGlobalDBContainerObjectType;
