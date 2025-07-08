#pragma once

#include <Python.h>
#include "dap_config.h"
#include "dap_enc_key.h"
#include "dap_stream_ctl.h"
#include "dap_server_python.h"
#include "dap_http_server.h"
#include "dap_enc_http.h"

typedef struct PyDapStreamCtl{
    PyObject_HEAD
}PyDapStreamCtlObject;

PyObject *dap_stream_ctl_add_proc_py(PyObject *self, PyObject *args);
int dap_stream_ctl_init_py(uint32_t size);

extern PyTypeObject DapStreamCtlObjectType;

