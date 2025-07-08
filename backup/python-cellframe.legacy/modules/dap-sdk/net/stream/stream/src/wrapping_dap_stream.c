#include "libdap-python.h"
#include "wrapping_dap_stream.h"

static PyMethodDef DapStreamMethods[] = {
    {"addProcHttp", dap_stream_add_proc_http_py, METH_VARARGS | METH_STATIC, ""},
    {}
};

PyTypeObject DapStreamObjectType = DAP_PY_TYPE_OBJECT(
        "DAP.Net.Stream", sizeof(PyDapStreamObject),
        "Dap stream object",
        .tp_methods = DapStreamMethods);

PyObject *dap_stream_add_proc_http_py(PyObject *self, PyObject *args){
    PyObject *obj_server;
    const char *STREAM_URL;
    if (!PyArg_ParseTuple(args, "O|s", &obj_server, &STREAM_URL))
        return NULL;
    dap_server_t *l_server = ((PyDapServerObject*)obj_server)->t_server;
    if (l_server) {
        dap_stream_add_proc_http(DAP_HTTP_SERVER(l_server), STREAM_URL);
        return PyLong_FromLong(0);
    } else {
        PyErr_SetString(PyExc_SystemError, "It is not possible to add a handler to a non-existent server. Check the configuration.");
        return NULL;
    }
}
