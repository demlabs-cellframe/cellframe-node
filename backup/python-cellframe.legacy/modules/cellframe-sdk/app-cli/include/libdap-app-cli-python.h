#pragma once

#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include "dap_common.h"
#include "dap_app_cli.h"
#include "dap_strfuncs.h"


typedef struct PyAppCli{
    PyObject_HEAD
}PyAppCliObject;


PyObject* dap_app_cli_main_py(PyObject *self, PyObject *args);

extern PyTypeObject DapAppCliObjectType;
