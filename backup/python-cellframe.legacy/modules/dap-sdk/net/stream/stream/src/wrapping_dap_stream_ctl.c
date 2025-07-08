#include "libdap-python.h"
#include "wrapping_dap_stream_ctl.h"

#define LOG_TAG "wrapping_dap_stream_ctl"

static PyMethodDef DapStreamCtlMethods[] = {
    {"addProcHttp", dap_stream_ctl_add_proc_py, METH_VARARGS | METH_STATIC, ""},
    {}
};

PyTypeObject DapStreamCtlObjectType = DAP_PY_TYPE_OBJECT(
        "DAP.Net.StreamCtl", sizeof(PyDapStreamCtlObject),
        "Dap stream ctl object",
        .tp_methods =DapStreamCtlMethods);


PyObject *dap_stream_ctl_add_proc_py(PyObject *self, PyObject *args){
    PyObject *obj_server;
    const char *STREAM_CTL_URL;
    if (!PyArg_ParseTuple(args, "O|s", &obj_server, &STREAM_CTL_URL))
        return  NULL;
    dap_server_t *l_server = ((PyDapServerObject*)obj_server)->t_server;
    if (l_server)
        dap_stream_ctl_add_proc(DAP_HTTP_SERVER(l_server), STREAM_CTL_URL);
    else {
        PyErr_SetString(PyExc_SystemError, "It is not possible to add a handler to a non-existent server. Check the configuration.");
        return NULL;
    }
    Py_RETURN_NONE;
}

int dap_stream_ctl_init_py(uint32_t size){
    UNUSED(size);
    return dap_stream_ctl_init();
}
