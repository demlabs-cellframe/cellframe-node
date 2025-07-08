#pragma once
#include <Python.h>
#include "dap_global_db_cluster.h"
#include "wrapping_dap_global_db_instance.h"
#include "wrapping_dap_global_db_role.h"
#include "wrapping_dap_stream_cluster_role.h"

typedef struct PyGlobalDBCluster{
    PyObject_HEAD
    dap_global_db_cluster_t *cluster;
} PyGlobalDBClusterObject;

void PyGloabDBCluster_Delete(PyGlobalDBClusterObject *self);

PyObject *wrapping_dap_global_db_cluster_by_group(PyObject *self, PyObject *argv);
PyObject *wrapping_dap_global_db_cluster_broadcust(PyObject *self, PyObject *argv);
PyObject *wrapping_dap_global_db_cluster_member_delete(PyObject *self, PyObject *argv);
PyObject *wrapping_dap_global_db_cluster_member_add(PyObject *self, PyObject *argv);
//cluster_notyfy
PyObject *wrapping_dap_global_db_cluster_notify_add(PyObject *self, PyObject *argv);
PyObject *wrapping_dap_global_db_cluster_add_net_associate(PyObject *self, PyObject *argv);

extern PyTypeObject DapGlobalDBClusterObjectType;