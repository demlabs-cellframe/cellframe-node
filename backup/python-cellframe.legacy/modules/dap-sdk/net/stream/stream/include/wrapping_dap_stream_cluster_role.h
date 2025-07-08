#pragma once
#include <Python.h>
#include "dap_stream_cluster.h"

typedef struct PyDapClusterRole {
    PyObject_HEAD
    dap_cluster_type_t type;
} PyDapClusterRoleObject;

extern PyTypeObject DapClusterRoleObjectType;

typedef struct PyDapClusterRoles {
    PyObject_HEAD
} PyDapClusterRolesObject;

PyObject *WR_CLUSTER_ROLE_INVALID(PyObject *self, void *closure);
PyObject *WR_CLUSTER_ROLE_EMBEDDED(PyObject *self, void *closure);
PyObject *WR_CLUSTER_ROLE_AUTONOMIC(PyObject *self, void *closure);
PyObject *WR_CLUSTER_ROLE_ISOLATED(PyObject *self, void *closure);
PyObject *WR_CLUSTER_ROLE_VIRTUAL(PyObject *self, void *closure);
    
extern PyTypeObject DapClusterRolesObjectType;