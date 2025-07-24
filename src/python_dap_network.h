/*
 * Python DAP Network Coordinator Header
 * Coordinates DAP SDK network subsystems initialization
 */

#ifndef PYTHON_DAP_NETWORK_H
#define PYTHON_DAP_NETWORK_H

#define PY_SSIZE_T_CLEAN
#include <Python.h>

// Network coordination functions
PyObject* dap_network_init_wrapper(PyObject* self, PyObject* args);
PyObject* dap_network_deinit_wrapper(PyObject* self, PyObject* args);
PyObject* dap_network_status_wrapper(PyObject* self, PyObject* args);

// Network subsystem management
PyObject* dap_network_reinit_stream_wrapper(PyObject* self, PyObject* args);
PyObject* dap_network_reinit_client_wrapper(PyObject* self, PyObject* args);
PyObject* dap_network_reinit_http_wrapper(PyObject* self, PyObject* args);

// Combined methods provider
PyMethodDef* py_dap_network_get_methods(void);

#endif // PYTHON_DAP_NETWORK_H 