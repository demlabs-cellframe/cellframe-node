#pragma once
#include <Python.h>
#include "dap_stream_cluster.h"

typedef struct PyDapClusterMember{
    PyObject_HEAD
    dap_cluster_member_t *member;
}PyDapClusterMemberObject;

extern PyTypeObject DapClusterMemberObjectType;