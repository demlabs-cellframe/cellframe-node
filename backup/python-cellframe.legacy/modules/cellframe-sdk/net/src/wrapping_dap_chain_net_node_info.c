#include "wrapping_dap_chain_net_node_info.h"
#include "node_address.h"

static PyMethodDef DapChainNetNodeInfoMethods[] = {
        {"save", dap_chain_node_info_save_py, METH_VARARGS, ""},
        {"read", dap_chain_node_info_read_py, METH_VARARGS | METH_STATIC, ""},
        {NULL, NULL, 0, NULL}
};

PyTypeObject DapChainNodeInfoObjectType = DAP_PY_TYPE_OBJECT(
        "CellFrame.ChainNodeInfo", sizeof(PyDapChainNodeInfoObject),
        "Chain net node info object",
        .tp_methods = DapChainNetNodeInfoMethods);

PyObject *dap_chain_node_info_save_py(PyObject *self, PyObject *args){
   PyObject *obj_net;
   if (!PyArg_ParseTuple(args, "O", &obj_net))
       return NULL;
   int res = dap_chain_node_info_save(((PyDapChainNetObject*)obj_net)->chain_net, ((PyDapChainNodeInfoObject*)self)->node_info);
   return PyLong_FromLong(res);
}

PyObject *dap_chain_node_info_read_py(PyObject *self, PyObject *args){
    PyObject *obj_net;
    PyObject *obj_node_addr;
    if (!PyArg_ParseTuple(args, "O|O", &obj_net, &obj_node_addr))
        return  NULL;
    PyObject *obj_node_info = _PyObject_New(&DapChainNodeInfoObjectType);
    ((PyDapChainNodeInfoObject*)obj_node_info)->node_info = dap_chain_node_info_read(((PyDapChainNetObject*)obj_net)->chain_net,
                                                                                     &((PyDapNodeAddrObject*)obj_node_addr)->addr);
    return Py_BuildValue("O", &obj_node_info);
}
