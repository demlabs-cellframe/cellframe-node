#include "libdap-python.h"
#include "wrapping_dap_http_folder.h"

static PyMethodDef DapHttpFolderMethods[] = {
        {"add", (PyCFunction)dap_http_folder_add_py, METH_VARARGS | METH_STATIC, ""},
        {}
};

PyTypeObject DapHttpFolder_DapHttpFolderType = DAP_PY_TYPE_OBJECT(
        "CellFrame.DapHttpFolder", sizeof(PyDapHttpFolderObject),
        "Dap http folder object",
        .tp_methods = DapHttpFolderMethods);

PyObject *dap_http_folder_add_py(PyObject *self, PyObject *args){
    PyObject *obj_server;
    const char *url_path;
    const char *local_path;
    if (!PyArg_ParseTuple(args, "Oss", &obj_server, &url_path, &local_path))
        return NULL;
    dap_server_t *l_server = ((PyDapServerObject*)obj_server)->t_server;
    if (l_server) {
        int res = dap_http_folder_add(DAP_HTTP_SERVER(l_server), url_path, local_path);
        return PyLong_FromLong(res);
    } else {
        PyErr_SetString(PyExc_SystemError, "It is not possible to add a handler to a non-existent server. Check the configuration.");
        return NULL;
    }
}
