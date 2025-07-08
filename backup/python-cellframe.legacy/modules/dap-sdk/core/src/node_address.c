#include "node_address.h"
#include "libdap-python.h"
#include "dap_strfuncs.h"

PyObject* PyDapNodeAddrObject_str(PyObject* self) {
    char *ret = dap_strdup_printf(NODE_ADDR_FP_STR, NODE_ADDR_FP_ARGS_S(((PyDapNodeAddrObject*) self)->addr));
    PyObject *l_obj = Py_BuildValue("s", ret);
    DAP_FREE(ret);
    return l_obj;
}

int PyDapNodeAddr_Init(PyDapNodeAddrObject *self, PyObject *args, PyObject *kwds) {
    const char *in_addr_str;
    char *kwords[] = {
        "address",
        NULL
    };
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "s", kwords, &in_addr_str))
        return -1;
    if (!dap_stream_node_addr_from_str(&self->addr, in_addr_str)) {
        return 0;
    }
    char *l_err = dap_strdup_printf("Failed to convert %s to NodeAddr, please check the recording format.", in_addr_str);
    PyErr_SetString(PyExc_Exception, l_err);
    DAP_DELETE(l_err);
    return -1;
}

PyTypeObject DapNodeAddrObjectType = DAP_PY_TYPE_OBJECT("DAP.Core.NodeAddr", sizeof(PyDapNodeAddrObject),
                                                          "Stream node addr object", 
                                                          .tp_str = PyDapNodeAddrObject_str,
                                                          .tp_init = (initproc)PyDapNodeAddr_Init);