#pragma once
#include <Python.h>
#include "dap_global_db.h"

typedef struct PyDapGlobalDBInstance{
    PyObject_HEAD
    dap_global_db_instance_t *instance;
}PyDapGlobalDBInstanceObject;

extern PyTypeObject DapGlobalDBInstanceObjectType;