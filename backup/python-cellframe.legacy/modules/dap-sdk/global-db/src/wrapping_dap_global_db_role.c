#include "wrapping_dap_global_db_role.h"
#include "libdap-python.h"

#define PVT(a) ((PyGlobalDBRoleObject*)a)->role

PyObject *DapGlobalDBRoleObject_compare(PyObject *self, PyObject *other, int op) {
    if (!PyObject_TypeCheck(other, &DapGlobalDBRolesObjectType)) {
        Py_RETURN_FALSE;
    }
    switch (op) {
        case Py_EQ:
            if (PVT(self) == PVT(other))
                Py_RETURN_TRUE;
            else
                Py_RETURN_FALSE;
            break;
        case Py_NE:
            if (PVT(self) != PVT(other))
                Py_RETURN_TRUE;
            else
                Py_RETURN_FALSE;
            break;
        default:
            Py_RETURN_FALSE;
    }
}

PyTypeObject DapGlobalDBRoleObjectType = DAP_PY_TYPE_OBJECT("DAP.GlobalDB.ClusterRole", sizeof(PyGlobalDBRoleObject),
                                                            "Object with role member in global db cluster",
                                                            .tp_richcompare = DapGlobalDBRoleObject_compare);

static PyGetSetDef DapGlobalDBRolesGetsSets[] = {
    {"NOBODY", (getter)ROLE_NOBODY, NULL, "", NULL},
    {"GUEST", (getter)ROLE_GUEST, NULL, "", NULL},
    {"USER", (getter)ROLE_USER, NULL, "", NULL},
    {"ROOT", (getter)ROLE_ROOT, NULL, "", NULL},
    {"DEFAULT", (getter)ROLE_DEFAULT, NULL, "", NULL},
    {"INVALID", (getter)ROLE_INVALID, NULL, "", NULL},
    {}
};

PyObject *ROLE_NOBODY(PyObject *self, void *closure){
    (void)closure;
    PyGlobalDBRoleObject *obj_role = PyObject_New(PyGlobalDBRoleObject, &DapGlobalDBRoleObjectType);
    obj_role->role = DAP_GDB_MEMBER_ROLE_NOBODY;
    return (PyObject*)obj_role;
}
PyObject *ROLE_GUEST(PyObject *self, void *closure){
    (void)closure;
    PyGlobalDBRoleObject *obj_role = PyObject_New(PyGlobalDBRoleObject, &DapGlobalDBRoleObjectType);
    obj_role->role = DAP_GDB_MEMBER_ROLE_GUEST;
    return (PyObject*)obj_role;
}
PyObject *ROLE_USER(PyObject *self, void *closure){
    (void)closure;
    PyGlobalDBRoleObject *obj_role = PyObject_New(PyGlobalDBRoleObject, &DapGlobalDBRoleObjectType);
    obj_role->role = DAP_GDB_MEMBER_ROLE_USER;
    return (PyObject*)obj_role;
}
PyObject *ROLE_ROOT(PyObject *self, void *closure){
    (void)closure;
    PyGlobalDBRoleObject *obj_role = PyObject_New(PyGlobalDBRoleObject, &DapGlobalDBRoleObjectType);
    obj_role->role = DAP_GDB_MEMBER_ROLE_ROOT;
    return (PyObject*)obj_role;
}
PyObject *ROLE_DEFAULT(PyObject *self, void *closure){
    (void)closure;
    PyGlobalDBRoleObject *obj_role = PyObject_New(PyGlobalDBRoleObject, &DapGlobalDBRoleObjectType);
    obj_role->role = DAP_GDB_MEMBER_ROLE_DEFAULT;
    return (PyObject*)obj_role;
}
PyObject *ROLE_INVALID(PyObject *self, void *closure){
    (void)closure;
    PyGlobalDBRoleObject *obj_role = PyObject_New(PyGlobalDBRoleObject, &DapGlobalDBRoleObjectType);
    obj_role->role = DAP_GDB_MEMBER_ROLE_INVALID;
    return (PyObject*)obj_role;
}

PyTypeObject DapGlobalDBRolesObjectType = DAP_PY_TYPE_OBJECT("DAP.GlobalDB.RoleEnums", sizeof(struct PyGlobalDBRoleEnum),
                                                          "Enum with role gloalDB cluster",
                                                          .tp_getset = DapGlobalDBRolesGetsSets);
