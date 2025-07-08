#include "wrapping_dap_global_db_instance.h"
#include "libdap-python.h"

int DapGlobalDBInstance_Init(PyDapGlobalDBInstanceObject *self, PyObject *args, PyObject *kwds) {
    (void)args;
    (void)kwds;
    self->instance = dap_global_db_instance_get_default();
    return 0;
}

PyTypeObject DapGlobalDBInstanceObjectType = DAP_PY_TYPE_OBJECT(
    "DAP.GlobalDB.Instance", sizeof(PyDapGlobalDBInstanceObject),
    "GlobalDB instance class",
    .tp_init = (initproc)DapGlobalDBInstance_Init
);