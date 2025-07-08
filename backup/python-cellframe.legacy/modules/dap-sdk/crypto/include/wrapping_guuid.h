#pragma once
#include <Python.h>
#include "dap_guuid.h"

typedef struct PyCryptoGUUID{
    PyObject_HEAD
    dap_guuid_t guuid;
} PyCryptoGUUIDObject;

PyObject *wrapping_guuid_compose(PyObject *self, PyObject *argv);
PyObject *wrapping_guuid_generate(PyObject *self, PyObject *argv);

extern PyTypeObject PyCryptoGUUIDObjectType;