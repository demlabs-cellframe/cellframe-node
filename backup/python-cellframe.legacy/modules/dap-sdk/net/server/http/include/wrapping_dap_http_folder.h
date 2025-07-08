#ifndef _WRAPPING_DAP_HTTP_FOLDER_
#define _WRAPPING_DAP_HTTP_FOLDER_

#include <Python.h>
#include "dap_http_folder.h"
#include "dap_http_server.h"
#include "dap_enc_http.h"
#include "dap_server_python.h"

typedef struct PyDapHttpFolder{
    PyObject_HEAD
}PyDapHttpFolderObject;

PyObject *dap_http_folder_add_py(PyObject *self, PyObject *args);

extern PyTypeObject DapHttpFolder_DapHttpFolderType;


#endif // _WRAPPING_DAP_HTTP_FOLDER_
