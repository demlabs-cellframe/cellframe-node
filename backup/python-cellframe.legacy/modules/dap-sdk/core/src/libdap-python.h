#pragma once
#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include "dap_config.h"
#include "dap_common.h"
#include "dap_list.h"

#define DAP_PY_MODULE(...) ((PyModuleDef) {.m_base = PyModuleDef_HEAD_INIT, ##__VA_ARGS__})
#define DAP_PY_TYPE_OBJECT(name, size, doc, ...) ((PyTypeObject) {                  \
                            .ob_base = {PyObject_HEAD_INIT(NULL) 0},                \
                            .tp_name = name,                                        \
                            .tp_basicsize = size,                                   \
                            .tp_doc = doc,                                          \
                            .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,   \
                            .tp_new = PyType_GenericNew,                            \
                            ##__VA_ARGS__})

typedef struct PyDap{
    PyObject_HEAD
}PyDapObject;

extern PyTypeObject DapCoreObjectType;
extern PyTypeObject DapLogitObjectType;
extern PyTypeObject DapCommonObjectType;

PyObject* dap_exec_with_ret(PyObject* self, PyObject *args);

PyObject *dap_set_log_level(PyObject *self, PyObject *args);

PyObject* dap_log_it(PyObject* self, PyObject* args);

PyObject* dap_log_it_debug(PyObject* self, PyObject* args);
PyObject* dap_log_it_info(PyObject* self, PyObject* args);
PyObject* dap_log_it_notice(PyObject* self, PyObject* args);
PyObject* dap_log_it_message(PyObject* self, PyObject* args);
PyObject* dap_log_it_dap(PyObject* self, PyObject* args);
PyObject* dap_log_it_warning(PyObject* self, PyObject* args);
PyObject* dap_log_it_att(PyObject* self, PyObject* args);
PyObject* dap_log_it_error(PyObject* self, PyObject* args);
PyObject* dap_log_it_critical(PyObject* self, PyObject* args);

PyObject* py_m_dap_config_get_item(PyObject *self, PyObject *args);

PyObject* py_m_dap_config_get_sys_dir(PyObject *self, PyObject *args);

PyObject *dapListToPyList(dap_list_t *list);

dap_list_t *pyListToDapList(PyObject *list);

