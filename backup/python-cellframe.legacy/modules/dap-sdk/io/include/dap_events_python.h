#pragma once

#include "Python.h"
#include "dap_events.h"
#include "dap_events_socket_python.h"


#ifdef __cplusplus
extern "C" {
#endif

typedef struct PyDapEvents{
    PyObject_HEAD
}PyDapEventsObject;

extern PyTypeObject DapEventsObjectType;

#ifdef __cplusplus
}
#endif
