#include "libdap-python.h"
#include "dap_plugins_python_app_context.h"

#define LOG_TAG "App conext for python"

dap_plugins_python_app_context_t *s_app_context = NULL;

static PyMethodDef DapAppContextMethods[] = {
    {"getServer", (PyCFunction)dap_plugins_python_app_context_get_server, METH_VARARGS | METH_STATIC, "Get main server from node"},
    {"getHttp", (PyCFunction)dap_plugins_python_app_context_get_http, METH_NOARGS | METH_STATIC, "Get main server from node"},
    {}
};


PyTypeObject DapAppContextObjectType = DAP_PY_TYPE_OBJECT(
        "DAP.AppContext", sizeof(PyDapAppContextObject),
        "Dap App Context object",
        .tp_methods = DapAppContextMethods);

int dap_plugins_python_app_content_init(dap_server_t *a_server){
    s_app_context = DAP_NEW(dap_plugins_python_app_context_t);
    if (!s_app_context) {
        log_it(L_CRITICAL, "Memory allocation error");
        return -1;
    }
    s_app_context->server = a_server;
    return 0;
}

PyObject *dap_plugins_python_app_context_get_server(PyObject *self, PyObject *args){
    (void)self;
    PyObject *l_obj_server;
    if (!PyArg_ParseTuple(args, "O", &l_obj_server)){
        PyErr_SetString(PyExc_TypeError, "No argument provided.");
        return NULL;
    }
    if (!s_app_context->server)
    {
       PyErr_SetString(PyExc_TypeError, "IO server object is null, probably configuration mismatch in [server] section.");
       return NULL;
    }
    ((PyDapServerObject*)l_obj_server)->t_server = s_app_context->server;
    Py_RETURN_NONE;
}
PyObject *dap_plugins_python_app_context_get_http(PyObject *self, PyObject *args){
    (void)self;
    (void)args;
    PyDapHttpObject *l_obj_http = PyObject_NEW(PyDapHttpObject, &DapHttpObjectType);
    l_obj_http->http = DAP_HTTP_SERVER(s_app_context->server);
    return Py_BuildValue("O", l_obj_http);
}
