#include "wrapping_dap_client_http.h"
#include "python-cellframe_common.h"
#include "dap_string.h"
#include "http_status_code.h"

static PyMethodDef DapClientHttp_Methods[] = {
    {"getTimeout", (PyCFunction)wrapping_dap_client_http_get_connect_timeout_ms, METH_NOARGS | METH_STATIC, ""},
    {NULL, NULL, 0, NULL}
};

void PyDapClientHttp_deinit(PyDapClientHttpObject *self) {}

typedef struct _s_callback{
    PyObject *obj_callable_response;
    PyObject *obj_callable_error;
    PyObject *obj_argv;
}_s_callback_t;

void _wrapping_response_callback_call(void *a_response, size_t a_response_size, void *a_callback_arg,
                                      http_status_code_t a_http_code) {
    _s_callback_t *lcb = (_s_callback_t*)a_callback_arg;
    PyGILState_STATE gstate;
    gstate = PyGILState_Ensure();
    PyObject *obj_bytes = PyBytes_FromStringAndSize(a_response, a_response_size);
    PyObject *argv = Py_BuildValue("OOI", obj_bytes, lcb->obj_argv, a_http_code);
    Py_INCREF(lcb->obj_argv);
    Py_INCREF(lcb->obj_callable_response);
    PyObject *result = PyObject_CallObject(lcb->obj_callable_response, argv);
    if (!result){
        python_error_in_log_it("wrapping_dap_client_http");
    }
    Py_XDECREF(lcb->obj_callable_response);
    Py_XDECREF(lcb->obj_argv);
    Py_XDECREF(argv);
    Py_XDECREF(result);
    Py_XDECREF(obj_bytes);
    PyGILState_Release(gstate);
}
void _wrapping_response_callback_err(int a_err_code, void *a_callback_arg) {
    _s_callback_t *lcb = (_s_callback_t*)a_callback_arg;
    PyObject *obj_argv = Py_BuildValue("iO", a_err_code, lcb->obj_argv);
    Py_INCREF(lcb->obj_argv);
    Py_INCREF(lcb->obj_callable_error);
    PyObject *result = PyObject_CallObject(lcb->obj_callable_error, obj_argv);
    if (!result){
        python_error_in_log_it("wrapping_dap_client_http");
    }
    Py_XDECREF(result);
    Py_XDECREF(obj_argv);
    Py_XDECREF(lcb->obj_argv);
    Py_XDECREF(lcb->obj_callable_error);
}

int PyDapClientHttp_create(PyObject *self, PyObject *argv, PyObject *kwds)
{
    const char *kwlist[] = {
        "uplink_addr",
        "uplink_port",
        "method",
        "request_content_type",
        "path",
        "request",
        "cookie",
        "response_callback",
        "error_callback",
        "callback_args",
        "custom_headers",
        "over_ssl",
        NULL
    };
    // PyObject *obj_worker;
    const char *uplink_addr;
    uint16_t uplink_port;
    const char *method;
    const char *request_content_type;
    const char *path;
    PyObject *request;
    const char *cookie;
    PyObject *response_callback;
    PyObject *error_callback;
    PyObject *callback_args;
    PyObject *custom_headers;
    PyObject *over_ssl;
    if (!PyArg_ParseTupleAndKeywords(argv, kwds, "sHsssOsOOOOO", (char **)kwlist, &uplink_addr, &uplink_port, &method,
                                     &request_content_type, &path, &request, &cookie, &response_callback, &error_callback,
                                     &callback_args, &custom_headers, &over_ssl)){
        return -1;
    }
    //TODO: Check the obj_worker is wapping dap_worker_t 
    if (!PyCallable_Check(response_callback)) {
        PyErr_SetString(PyExc_BaseException, "The eighth argument is not set correctly, it should be a callback function that will be called after receiving a response to the request.");
        return -1;
    }
    if (!PyCallable_Check(error_callback)) {
        PyErr_SetString(PyExc_BaseException, "The ninth argument is not set correctly, it should be a callback function that will be called after an error occurs.");
        return -1;
    }
    if (!PyList_Check(custom_headers)) {
        PyErr_SetString(PyExc_BaseException, "The eleventh argument is not set correctly, it should be an instance of the List object.");
        return -1;
    }
    if (!PyBool_Check(over_ssl)) {
        PyErr_SetString(PyExc_BaseException, "The twelfth argument is not set correctly, it should be an instance of a bool object.");
        return -1;
    }
    char *l_bytes = NULL;
    Py_ssize_t l_bytes_size = 0;
    if (request != Py_None) {
        if (PyBytes_Check(request)){
            if (PyBytes_AsStringAndSize(request, &l_bytes, &l_bytes_size) == -1) {
                return -1;
            }
        } else {
            PyErr_SetString(PyExc_BaseException, "The sixth argument is not set correctly, it should be an instance of the Bytes or None object.");
            return -1;
        }
    }
    
    dap_string_t *l_str = dap_string_new(NULL);
    size_t l_custom_headers_size = PyList_GET_SIZE(custom_headers);
    for (size_t i = 0; i < l_custom_headers_size; i++) {
        PyObject *obj_el = PyList_GetItem(custom_headers, i);
        if (!PyUnicode_Check(obj_el)) {
            PyErr_SetString(PyExc_BaseException, "The eleventh argument must be a list of strings whose list contains another element.");
            dap_string_free(l_str, true);
            return -1;
        }
        dap_string_append_printf(l_str, "%s\r\n", PyUnicode_AsUTF8(obj_el));
    }
    _s_callback_t *l_callback_w_args  = DAP_NEW(_s_callback_t);
    l_callback_w_args->obj_callable_response = response_callback;
    l_callback_w_args->obj_callable_error = error_callback;
    l_callback_w_args->obj_argv = callback_args;
    Py_INCREF(l_callback_w_args->obj_callable_response);
    Py_INCREF(l_callback_w_args->obj_callable_error);
    Py_INCREF(l_callback_w_args->obj_argv);
    ((PyDapClientHttpObject *)self)->client_http = dap_client_http_request_custom(
                NULL, uplink_addr, uplink_port, method, request_content_type, path, l_bytes, l_bytes_size,
                dap_strdup(cookie), _wrapping_response_callback_call, _wrapping_response_callback_err, l_callback_w_args,
                l_str->str, (over_ssl == Py_True) ? true : false);
    dap_string_free(l_str, true);
    return 0;
}

PyObject *wrapping_dap_client_http_get_connect_timeout_ms(PyObject *self, PyObject *argv) {
    (void)self;
    (void)argv;
    uint64_t l_timeout = dap_client_http_get_connect_timeout_ms();
    return Py_BuildValue("K", l_timeout);
}

void PyDapClientHttp_dealloc(PyDapClientHttpObject *self){
    // dap_client_http_close_unsafe(self->client_http);
    Py_TYPE(self)->tp_free((PyObject*)self);
}

PyTypeObject DapClientHttpObjectType = DAP_PY_TYPE_OBJECT("DAP.Network.ClientHttp",
                                                           sizeof(PyDapClientHttpObject),
                                                           "Client for connect http server",
                                                           .tp_init = PyDapClientHttp_create,
                                                           .tp_dealloc = (destructor)PyDapClientHttp_dealloc);
