#pragma once
#include <Python.h>
#include "dap_global_db_cluster.h"

typedef struct PyGlobalDBRole{
    PyObject_HEAD
    dap_global_db_role_t role;
}PyGlobalDBRoleObject;

extern PyTypeObject DapGlobalDBRoleObjectType;

struct PyGlobalDBRoleEnum{
    PyObject_HEAD
};

PyObject *ROLE_NOBODY(PyObject *self, void *closure);
PyObject *ROLE_GUEST(PyObject *self, void *closure);
PyObject *ROLE_USER(PyObject *self, void *closure);
PyObject *ROLE_ROOT(PyObject *self, void *closure);
PyObject *ROLE_DEFAULT(PyObject *self, void *closure);
PyObject *ROLE_INVALID(PyObject *self, void *closure);

extern PyTypeObject DapGlobalDBRolesObjectType;