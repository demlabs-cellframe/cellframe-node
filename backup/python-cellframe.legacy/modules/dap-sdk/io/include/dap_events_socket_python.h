#pragma once

#include "Python.h"
#include "dap_events_socket.h"
#include "dap_events_python.h"
#include "dap_common.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct PyDapEventsSocket{
    PyObject_HEAD
    dap_events_socket_t *t_events_socket;
}PyDapEventsSocketObject;

PyObject *dap_events_socket_create_after_py(PyDapEventsSocketObject *self, PyObject *args);

PyObject *dap_events_socket_set_readable_py(PyDapEventsSocketObject *self, PyObject *args);
PyObject *dap_events_socket_set_writable_py(PyDapEventsSocketObject *self, PyObject *args);

PyObject *dap_events_socket_write_py(PyDapEventsSocketObject *self, PyObject *args);
PyObject *dap_events_socket_write_f_py(PyDapEventsSocketObject *self, PyObject *args);
PyObject *dap_events_socket_read_py(PyDapEventsSocketObject *self, PyObject *args);

PyObject *dap_events_socket_delete_py(PyDapEventsSocketObject *self, PyObject *args);// Removes the client from the list

PyObject *dap_events_socket_shrink_buf_in_py(PyDapEventsSocketObject *self, PyObject *args);

extern PyTypeObject DapEventsSocketObjectType;

#ifdef __cplusplus
}
#endif
