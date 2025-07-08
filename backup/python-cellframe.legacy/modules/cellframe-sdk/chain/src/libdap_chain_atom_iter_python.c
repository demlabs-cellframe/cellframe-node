#include "libdap-python.h"
#include "libdap_chain_atom_iter_python.h"

static PyMethodDef DapChainAtomIterMethods[] = {
        {}
};

PyTypeObject DapChainAtomIterObjectType = DAP_PY_TYPE_OBJECT(
        "CellFrame.ChainAtomIter", sizeof(PyChainAtomIterObject),
        "Chain atom iter objects",
        .tp_methods = DapChainAtomIterMethods);

bool PyDapChainAtomIter_Check(PyObject *obj){
    return PyObject_TypeCheck(obj, &DapChainAtomIterObjectType);
}
