#include "libdap-python.h"
#include "wrapping_dap_chain_atom_ptr.h"

static PyMethodDef DapChainAtomPtrMethods[] = {
        {}
};

PyTypeObject DapChainAtomPtrObjectType = DAP_PY_TYPE_OBJECT(
        "CellFrame.ChainAtomPtr", sizeof(PyChainAtomObject),
        "Chain atom ptr objects",
        .tp_methods = DapChainAtomPtrMethods);
