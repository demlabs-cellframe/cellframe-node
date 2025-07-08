#ifndef _WRAPPING_DAP_STREAM_
#define _WRAPPING_DAP_STREAM_

#include <Python.h>
#include "dap_stream.h"
#include "dap_server_python.h"
#include "dap_http_server.h"
#include "dap_enc_http.h"

typedef struct PyDapStream{
    PyObject_HEAD
}PyDapStreamObject;

PyObject *dap_stream_add_proc_http_py(PyObject *self, PyObject *args);

extern PyTypeObject DapStreamObjectType;

#endif // _WRAPPING_DAP_STREAM_
