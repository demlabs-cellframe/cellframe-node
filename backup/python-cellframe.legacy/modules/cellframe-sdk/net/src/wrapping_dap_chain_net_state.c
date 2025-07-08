#include "libdap-python.h"
#include "wrapping_dap_chain_net_state.h"

static PyMethodDef PyDapChainNetStateMethods[] = {
        {"NET_STATE_OFFLINE", (PyCFunction)NET_STATE_OFFLINE_PY, METH_NOARGS | METH_STATIC, ""},
        {"NET_STATE_LINKS_PREPARE", (PyCFunction)NET_STATE_LINKS_PREPARE_PY, METH_NOARGS | METH_STATIC, ""},
        {"NET_STATE_LINKS_CONNECTING", (PyCFunction)NET_STATE_LINKS_CONNECTING_PY, METH_NOARGS | METH_STATIC, ""},
        {"NET_STATE_LINKS_ESTABLISHED", (PyCFunction)NET_STATE_LINKS_ESTABLISHED_PY, METH_NOARGS | METH_STATIC, ""},
        {"NET_STATE_SYNC_CHAINS", (PyCFunction)NET_STATE_SYNC_CHAINS_PY, METH_NOARGS | METH_STATIC, ""},
        {NULL, NULL, 0, NULL}
};

PyTypeObject DapChainNetStateObjectType = DAP_PY_TYPE_OBJECT(
        "CellFrame.ChainNetState", sizeof(PyDapChainNetStateObject),
        "Chain net staties object",
        .tp_methods = PyDapChainNetStateMethods);

PyObject *NET_STATE_OFFLINE_PY(){
    PyObject *obj = _PyObject_New(&DapChainNetStateObjectType);
    ((PyDapChainNetStateObject*)obj)->state = NET_STATE_OFFLINE;
    return Py_BuildValue("O", obj);
}
PyObject *NET_STATE_LINKS_PREPARE_PY(){
    PyObject *obj = _PyObject_New(&DapChainNetStateObjectType);
    ((PyDapChainNetStateObject*)obj)->state = NET_STATE_LINKS_PREPARE;
    return Py_BuildValue("O", obj);
}
PyObject *NET_STATE_LINKS_CONNECTING_PY(){
    PyObject *obj = _PyObject_New(&DapChainNetStateObjectType);
    ((PyDapChainNetStateObject*)obj)->state = NET_STATE_LINKS_CONNECTING;
    return Py_BuildValue("O", obj);
}
PyObject *NET_STATE_LINKS_ESTABLISHED_PY(){
    PyObject *obj = _PyObject_New(&DapChainNetStateObjectType);
    ((PyDapChainNetStateObject*)obj)->state = NET_STATE_LINKS_ESTABLISHED;
    return Py_BuildValue("O", obj);
}
PyObject *NET_STATE_ONLINE_PY(){
    PyObject *obj = _PyObject_New(&DapChainNetStateObjectType);
    ((PyDapChainNetStateObject*)obj)->state = NET_STATE_ONLINE;
    return Py_BuildValue("O", obj);
}
PyObject *NET_STATE_SYNC_CHAINS_PY(){
    PyObject *obj = _PyObject_New(&DapChainNetStateObjectType);
    ((PyDapChainNetStateObject*)obj)->state = NET_STATE_SYNC_CHAINS;
    return Py_BuildValue("O", obj);
}
