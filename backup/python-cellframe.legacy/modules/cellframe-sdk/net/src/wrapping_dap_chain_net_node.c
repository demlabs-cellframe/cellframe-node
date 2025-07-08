#include "wrapping_dap_chain_net_node.h"
#include "node_address.h"

static PyMethodDef DapChainNetNodeMethods[] = {
        {"aliasFind", dap_chain_node_alias_find_py, METH_VARARGS | METH_STATIC, ""},
        {"aliasRegister", dap_chain_node_alias_register_py, METH_VARARGS | METH_STATIC, ""},
        {"aliasDelete", dap_chain_node_alias_delete_py, METH_VARARGS | METH_STATIC, ""},
        {NULL, NULL, 0, NULL}
};

PyTypeObject DapChainNodeObjectType = DAP_PY_TYPE_OBJECT(
        "CellFrame.ChainNode", sizeof(PyDapChainNodeObject),
        "Chain net node object",
        .tp_methods = DapChainNetNodeMethods);

PyObject *dap_chain_node_alias_find_py(PyObject *self, PyObject *args){
    (void) self;
    PyObject *chain_net;
    const char *alias;
    if (!PyArg_ParseTuple(args, "O|s", &chain_net, &alias))
        return NULL;
    PyObject *obj_node_addr = _PyObject_New(&DapNodeAddrObjectType);
    dap_chain_node_addr_t *l_node_addr = dap_chain_node_alias_find(((PyDapChainNetObject*)chain_net)->chain_net, alias);
    if (l_node_addr) {
        ((PyDapNodeAddrObject*)obj_node_addr)->addr = *l_node_addr;
        DAP_DELETE(l_node_addr);
    }
    return Py_BuildValue("O", obj_node_addr);
}
PyObject *dap_chain_node_alias_register_py(PyObject *self, PyObject *args){
    PyObject *obj_chain_net;
    const char *alias;
    PyObject *obj_node_addr;
    if (!PyArg_ParseTuple(args, "O|s|O", &obj_chain_net, &alias, &obj_node_addr))
        return NULL;
    bool ret = dap_chain_node_alias_register(((PyDapChainNetObject*)obj_chain_net)->chain_net, alias,
                                             &((PyDapNodeAddrObject*)obj_node_addr)->addr);
    if (ret)
        Py_RETURN_TRUE;
    else
        Py_RETURN_FALSE;
}
PyObject *dap_chain_node_alias_delete_py(PyObject *self, PyObject *args){
    PyObject *obj_chain_net;
    const char *alias;
    if (!PyArg_ParseTuple(args, "O|s", &obj_chain_net, &alias))
        return NULL;
    bool ret = dap_chain_node_alias_delete(((PyDapChainNetObject*)obj_chain_net)->chain_net, alias);
    if (ret)
        Py_RETURN_TRUE;
    else
        Py_RETURN_FALSE;
}
