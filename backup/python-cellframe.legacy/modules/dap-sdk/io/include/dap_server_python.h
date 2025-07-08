#ifndef _DAP_SERVER_PYTHON_
#define _DAP_SERVER_PYTHON_
#include "Python.h"
#include "dap_server.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct PyDapServer {
    PyObject_HEAD
    dap_server_t *t_server;
} PyDapServerObject;

extern PyTypeObject DapServerObjectType;

int py_server_init(uint32_t l_thread_cnt, size_t conn_t);
void py_server_deinit(void);

PyObject *py_server_loop(PyObject *self, PyObject *args);

#ifdef __cplusplus
}
#endif
#endif //_DAP_SERVER_PYTHON_
