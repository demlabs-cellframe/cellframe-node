#include "libdap-python.h"
#include "wrapping_guuid.h"
#include "node_address.h"
#include "wrapping_dap_global_db_cluster.h"
#include "wrapping_dap_global_db_instance.h"
#include "wrapping_dap_global_db_role.h"
#include "wrapping_dap_cluster_member.h"


static PyMethodDef DapGlobalDBClusterMethods[] = {
    {"byGroup", (PyCFunction)wrapping_dap_global_db_cluster_by_group, METH_VARARGS | METH_STATIC, ""},
    {"memberAdd", (PyCFunction)wrapping_dap_global_db_cluster_member_add, METH_VARARGS, ""},
    {"memberDelete", (PyCFunction)wrapping_dap_global_db_cluster_member_delete, METH_VARARGS, ""},
    {"notifyAdd", (PyCFunction)wrapping_dap_global_db_cluster_notify_add, METH_VARARGS, ""},
    {"AddNetAssociate", (PyCFunction)wrapping_dap_global_db_cluster_add_net_associate, METH_VARARGS, ""},
    {NULL, NULL, 0, NULL}
};

int DapGlobalDBCluster_init(PyGlobalDBClusterObject *self, PyObject *argv, PyObject *kwds){
    const char *kwlist[] = {
        "dbi",
        "goup_name_or_mnemonium",
        "GUID",
        "group_mask",
        "TTL",
        "owner_root_access",
        "defaultRole",
        "clusterRole",
        NULL
    };
    PyObject *dbi;
    const char *mnemonuim;
    PyObject *guid;
    const char *group_mask;
    uint32_t ttl;
    bool owner_root_access;
    PyObject *defaultRole;
    PyObject *clusterRole;
    if (!PyArg_ParseTupleAndKeywords(argv, kwds, "OsOsIpOO", (char **)kwlist, &dbi, &mnemonuim, &guid, &group_mask, &ttl, &owner_root_access, &defaultRole, &clusterRole))
        return -1;
    if (!PyObject_TypeCheck(dbi, &DapGlobalDBInstanceObjectType)){
        PyErr_SetString(PyExc_Exception, "The first argument is incorrect, it should be an instance of the DAP.GlobalDB.Instance class.");
        return -1;
    }
    if (!PyObject_TypeCheck(guid, &PyCryptoGUUIDObjectType)){
        PyErr_SetString(PyExc_Exception, "The third argument is incorrect, it should be an instance of the DAP.Crypto.GUUID class.");
        return -1;
    }
    if (!PyObject_TypeCheck(defaultRole, &DapGlobalDBRoleObjectType)) {
        PyErr_SetString(PyExc_Exception, "The seventh argument is incorrect, it should be an instance of the DAP.GlobalDB.Role class. To get it, use the DAP.GlobalDB.Roles enumeration.");
        return -1;
    }
    if (!PyObject_TypeCheck(clusterRole, &DapClusterRoleObjectType)) {
        PyErr_SetString(PyExc_Exception, "The eighth argument is incorrect, it should be an instance of the DAP.Network.ClusterRole class. To obtain it, use the DAP.Network.ClusterRoles enumeration.");
        return -1;
    }
    self->cluster = dap_global_db_cluster_add(((PyDapGlobalDBInstanceObject*)dbi)->instance, mnemonuim, 
                                                ((PyCryptoGUUIDObject*)guid)->guuid, group_mask, ttl, owner_root_access,
                                                ((PyGlobalDBRoleObject*)defaultRole)->role, ((PyDapClusterRoleObject*)clusterRole)->type);
    if (!self->cluster) {
        char *l_err_str = dap_strdup_printf("Failed to create cluster. Specified cluster group mask %s.", group_mask);
        PyErr_SetString(PyExc_Exception, l_err_str);
        DAP_DELETE(l_err_str);
        return -1;
    }
    return 0;
}

PyObject *wrapping_dap_global_db_cluster_by_group(PyObject *self, PyObject *argv){
    PyObject *obj_instance;
    const char *group;
    if (!PyArg_ParseTuple(argv, "Os", &obj_instance, &group))
        return NULL;
    dap_global_db_instance_t *l_instance = ((PyDapGlobalDBInstanceObject*)self)->instance;
    dap_global_db_cluster_t *l_cluster = dap_global_db_cluster_by_group(l_instance, group);
    PyGlobalDBClusterObject *obj_cluster = PyObject_New(PyGlobalDBClusterObject, &DapGlobalDBClusterObjectType);
    obj_cluster->cluster = l_cluster;
    return (PyObject*)obj_cluster;
}

PyObject *wrapping_dap_global_db_cluster_member_add(PyObject *self, PyObject *argv) {
    dap_global_db_cluster_t *l_cluster = ((PyGlobalDBClusterObject*)self)->cluster;
    PyObject *obj_node_addr, *obj_role;
    if (!PyArg_ParseTuple(argv, "OO", &obj_node_addr, &obj_role)) {
        return NULL;
    }
    if (!PyObject_TypeCheck(obj_node_addr, &DapNodeAddrObjectType)) {
        PyErr_SetString(PyExc_Exception, "The first argument must be an instance of the DAP.Network.StreamNodeAddr object");
        return NULL;
    }
    if (!PyObject_TypeCheck(obj_role, &DapGlobalDBRoleObjectType)) {
        PyErr_SetString(PyExc_Exception, "The second argument must be an instance of the DAP.GlobalDB.ClusterRole object.");
        return NULL;
    }
    dap_cluster_member_t *l_member = dap_global_db_cluster_member_add(l_cluster, 
                                    &((PyDapNodeAddrObject*)obj_node_addr)->addr, 
                                    ((PyGlobalDBRoleObject*)obj_role)->role);
    if (!l_member) {
        Py_RETURN_NONE;
    }
    PyDapClusterMemberObject *obj_member = PyObject_New(PyDapClusterMemberObject, &DapClusterMemberObjectType);
    obj_member->member = l_member;
    return (PyObject*)obj_member;
}

PyObject *wrapping_dap_global_db_cluster_member_delete(PyObject *self, PyObject *argv) {
    PyObject *obj_node_addr = NULL;
    if (!PyArg_ParseTuple(argv, "O", &obj_node_addr)) {
        return NULL;
    }
    if (!PyObject_TypeCheck(obj_node_addr, &DapNodeAddrObjectType)){
        PyErr_SetString(PyExc_Exception, "The first argument must be an instance of the DAP.Network.StreamNodeAddr object");
        return NULL;
    }
    int res = dap_global_db_cluster_member_delete(((PyGlobalDBClusterObject*)self)->cluster, &((PyDapNodeAddrObject*)obj_node_addr)->addr);
    if (res == 0) {
        Py_RETURN_TRUE;
    } else {
        Py_RETURN_FALSE;
    }
}

typedef struct _wrapping_dap_global_db_cluster_notify_callback{
    PyObject *func;
    PyObject *arg;
    dap_store_obj_t *store_obj;
}_wrapping_dap_global_db_cluster_notify_callback_t;

bool _wrapping_dap_global_db_cluster_callback_call_func_python(void *a_arg) {
    if (!a_arg)
        return false;

    _wrapping_dap_global_db_cluster_notify_callback_t *l_callback = (_wrapping_dap_global_db_cluster_notify_callback_t *)a_arg;
    PyGILState_STATE state = PyGILState_Ensure();
    char l_op_code[2];
    l_op_code[0] = dap_store_obj_get_type(l_callback->store_obj);
    l_op_code[1] = '\0';
    PyObject *l_obj_value = NULL;
    if (!l_callback->store_obj->value || !l_callback->store_obj->value_len)
        l_obj_value = Py_None;
    else
        l_obj_value = PyBytes_FromStringAndSize((char *)l_callback->store_obj->value, (Py_ssize_t)l_callback->store_obj->value_len);
    PyObject *argv = Py_BuildValue("sssOO", l_op_code, l_callback->store_obj->group, l_callback->store_obj->key, l_obj_value, l_callback->arg);
    Py_XINCREF(l_callback->func);
    Py_XINCREF(l_callback->arg);
    PyObject_CallObject(l_callback->func, argv);
    Py_DECREF(argv);
    Py_XDECREF(l_callback->func);
    Py_XDECREF(l_callback->arg);
    PyGILState_Release(state);
    dap_store_obj_free_one(l_callback->store_obj);
    return false;
}

void _wrapping_dap_global_db_cluster_func_callback(dap_store_obj_t *a_obj, void *a_arg)
{
    if (!a_arg || !a_obj)
        return;
    
    _wrapping_dap_global_db_cluster_notify_callback_t *l_obj = DAP_NEW(_wrapping_dap_global_db_cluster_notify_callback_t);
    if (!l_obj) 
        return;
    l_obj->store_obj = dap_store_obj_copy(a_obj, 1);
    l_obj->func = ((_wrapping_dap_global_db_cluster_notify_callback_t*)a_arg)->func;
    l_obj->arg = ((_wrapping_dap_global_db_cluster_notify_callback_t*)a_arg)->arg;
    dap_proc_thread_callback_add(NULL, _wrapping_dap_global_db_cluster_callback_call_func_python, l_obj);
}

PyObject *wrapping_dap_global_db_cluster_notify_add(PyObject *self, PyObject *argv){
    PyObject *l_func_callback = NULL;
    PyObject *l_args_callback = NULL;
    if (!PyArg_ParseTuple(argv, "OO", &l_func_callback, &l_args_callback)) {
        return NULL;
    }
    if (!PyCallable_Check(l_func_callback)) {
        PyErr_SetString(PyExc_AttributeError, "Argument must be callable");
        return NULL;
    }
    _wrapping_dap_global_db_cluster_notify_callback_t *l_callback = DAP_NEW(_wrapping_dap_global_db_cluster_notify_callback_t);
    l_callback->func = l_func_callback;
    l_callback->arg = l_args_callback;
    Py_INCREF(l_func_callback);
    Py_INCREF(l_args_callback);
    dap_global_db_cluster_add_notify_callback(((PyGlobalDBClusterObject*)self)->cluster, 
                                              _wrapping_dap_global_db_cluster_func_callback, l_callback);
    Py_RETURN_NONE;
}

PyObject *wrapping_dap_global_db_cluster_add_net_associate(PyObject *self, PyObject *argv){
    dap_cluster_t *l_cluster = ((PyGlobalDBClusterObject*)self)->cluster->links_cluster;
    uint64_t net_link;
    if (!PyArg_ParseTuple(argv, "k", &net_link)){
        return NULL;
    }
    if (!dap_link_manager_add_net_associate(net_link, l_cluster)) {
        Py_RETURN_TRUE;
    } else {
        Py_RETURN_FALSE;
    }
}

PyTypeObject DapGlobalDBClusterObjectType = DAP_PY_TYPE_OBJECT(
        "DAP.GlobalDB.Cluster", sizeof(PyGlobalDBClusterObject),
        "GlobalDB.Cluster object",
        .tp_methods = DapGlobalDBClusterMethods,
        .tp_init = (initproc)DapGlobalDBCluster_init
);
