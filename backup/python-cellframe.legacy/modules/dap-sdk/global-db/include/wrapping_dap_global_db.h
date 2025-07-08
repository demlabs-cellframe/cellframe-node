#pragma once

#include "Python.h"
#include "dap_global_db.h"
#include "wrapping_dap_global_db_obj.h"
#include "dap_strfuncs.h"

typedef struct PyDapGlobalDB{
    PyObject_HEAD
}PyDapGlobalDBObject;

PyObject *wrapping_dap_global_db_gr_get(PyObject *self, PyObject *args);
PyObject *wrapping_dap_global_db_gr_set(PyObject *self, PyObject *args);
PyObject *wrapping_dap_global_db_gr_set_sync(PyObject *self, PyObject *args);
PyObject *wrapping_dap_global_db_gr_del(PyObject *self, PyObject *args);
PyObject *wrapping_dap_global_db_gr_pin(PyObject *self, PyObject *args);
PyObject *wrapping_dap_global_db_gr_unpin(PyObject *self, PyObject *args);
PyObject *wrapping_dap_global_db_gr_load(PyObject *self, PyObject *args);

extern PyTypeObject DapGlobalDBObjectType;
