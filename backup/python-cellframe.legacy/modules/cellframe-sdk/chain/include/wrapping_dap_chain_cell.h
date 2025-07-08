#ifndef _WRAPPING_DAP_CHAIN_CELL_
#define _WRAPPING_DAP_CHAIN_CELL_
#include "Python.h"
#include "dap_chain_cell.h"
#include "libdap-chain-python.h"

#ifdef __cplusplus
extern "C" {
#endif

int init(void);

/* DAP chain cell */
typedef struct PyDapChainCell{
    PyObject_HEAD
    dap_chain_cell_t *cell;
}PyDapChainCellObject;

/* void DapChainCellObject_delete(PyDapChainCellObject* object);
PyObject *DapChainCellObject_create(PyTypeObject *type_object, PyObject *args, PyObject *kwds);

PyObject *dap_chain_cell_load_py(PyObject *self, PyObject *args);
PyObject *dap_chain_cell_file_update_py(PyObject *self, PyObject *args);
PyObject *dap_chain_cell_file_append_py(PyObject *self, PyObject *args);

extern PyTypeObject DapChainCellObjectType;

static bool PyDapChainCell_Check(PyObject *self){
    return PyObject_TypeCheck(self, &DapChainCellObjectType);
}
*/
#ifdef __cplusplus
}
#endif

#endif //_WRAPPING_DAP_CHAIN_CELL_
