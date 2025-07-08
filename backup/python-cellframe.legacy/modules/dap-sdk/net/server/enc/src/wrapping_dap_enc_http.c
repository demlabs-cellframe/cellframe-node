#include "libdap-python.h"
#include "wrapping_dap_enc_http.h"

static PyMethodDef PyDapEncServerMethods[] = {
        {"requestDecode", enc_http_request_decode_py, METH_VARARGS | METH_STATIC, ""},
        {"isNull", enc_http_is_null_py, METH_NOARGS, ""},
        {"reply", enc_http_reply_py, METH_VARARGS, ""},
        {"replyEncode", enc_http_reply_encode_py, METH_VARARGS, ""},
        {"addProc", enc_http_add_proc_py, METH_VARARGS | METH_STATIC, ""},
        {}
};

static PyGetSetDef PyDapEncServerGetSet[] = {
        {"action", (getter)enc_http_get_action_py, NULL, "Return action request", NULL},
        {"request", (getter)enc_http_get_request_py, NULL, "Return request in view bytes", NULL},
        {"urlPath", (getter)enc_http_get_url_path_py, NULL, "Return request in view bytes", NULL},
        {"query", (getter)enc_http_get_in_query_py, NULL, "Return request in view bytes", NULL},
        {}
};

PyTypeObject DapEncServerObjectType = DAP_PY_TYPE_OBJECT(
        "DAP.Net.EncHttp", sizeof(PyDapEncServerObject),
        "Dap enc server object",
        .tp_dealloc = (destructor)enc_http_delegate_delete_py,
        .tp_methods = PyDapEncServerMethods,
        .tp_getset = PyDapEncServerGetSet);

PyObject *enc_http_reply_py(PyObject *self, PyObject *args){
    PyObject *l_obj_bytes;
    if (!PyArg_ParseTuple(args, "O", &l_obj_bytes)){
        return NULL;
    }
    size_t l_bytes_size = (size_t)PyBytes_Size(l_obj_bytes);
    void *l_bytes = PyBytes_AsString(l_obj_bytes);
    size_t l_len = enc_http_reply(((PyDapEncServerObject*)self)->enc_http_delegate, l_bytes, l_bytes_size);
    return PyLong_FromLong(l_len);
}

PyObject *enc_http_request_decode_py(PyObject *self, PyObject *args){
    (void)self;
    PyObject *obj_sh;
    if (!PyArg_ParseTuple(args, "O", &obj_sh)){
        return NULL;
    }
    PyDapEncServerObject *obj_enc_delegate = PyObject_NEW(PyDapEncServerObject, &DapEncServerObjectType);
    obj_enc_delegate->enc_http_delegate = enc_http_request_decode(((PyDapHttpSimpleObject*)obj_sh)->sh);
    return Py_BuildValue("O", obj_enc_delegate);
}

PyObject *enc_http_is_null_py(PyObject *self, PyObject *args){
    (void)args;
    if (((PyDapEncServerObject*)self)->enc_http_delegate)
        Py_RETURN_FALSE;
    else
        Py_RETURN_TRUE;
}

PyObject *enc_http_reply_encode_py(PyObject *self, PyObject *args){
    PyObject *l_obj_sh;
    if (!PyArg_ParseTuple(args, "O", &l_obj_sh)){
        return NULL;
    }
    enc_http_reply_encode(((PyDapHttpSimpleObject*)l_obj_sh)->sh, ((PyDapEncServerObject*)self)->enc_http_delegate);
    Py_RETURN_NONE;
}

void enc_http_delegate_delete_py(PyObject *self){
    PyTypeObject *tp = Py_TYPE(self);
    if (((PyDapEncServerObject*)self)->enc_http_delegate){
        enc_http_delegate_delete(((PyDapEncServerObject*)self)->enc_http_delegate);
    }
    tp->tp_free(self);
    Py_DECREF(self);
}

PyObject *enc_http_add_proc_py(PyObject *self, PyObject *args){
    (void)self;
    PyObject *obj_server;
    const char *HTTP_URL;
    if (!PyArg_ParseTuple(args, "O|s", &obj_server, &HTTP_URL))
        return NULL;
    dap_server_t *l_server = ((PyDapServerObject*) obj_server)->t_server;
    if (l_server) {
        enc_http_add_proc(DAP_HTTP_SERVER(l_server), HTTP_URL);
    } else {
        PyErr_SetString(PyExc_SystemError, "It is not possible to add a handler to a non-existent server. Check the configuration.");
        return NULL;
    }
    return PyLong_FromLong(0);
}

PyObject *enc_http_get_action_py(PyDapEncServerObject *self, void *clouser){
    (void)clouser;
    return Py_BuildValue("s", self->enc_http_delegate->action);
}

PyObject *enc_http_get_request_py(PyDapEncServerObject *self, void *clouser){
    (void)clouser;
    if (self->enc_http_delegate->request){
        return PyBytes_FromString(self->enc_http_delegate->request);
    }else{
        Py_RETURN_NONE;
    }
}

PyObject *enc_http_get_url_path_py(PyDapEncServerObject *self, void *clouser){
    (void)clouser;
    return  Py_BuildValue("s", self->enc_http_delegate->url_path);
}
PyObject *enc_http_get_in_query_py(PyDapEncServerObject *self, void *clouser){
    (void)clouser;
    return  Py_BuildValue("s", self->enc_http_delegate->in_query);
}
