#pragma once

#include <Python.h>
#include "dap_chain_cs_dag.h"

typedef struct PyDapChainCsDagRound{
    PyObject_HEAD
    dap_chain_cs_dag_event_round_item_t *item;
}PyDapChainCsDagRoundObject;

extern PyTypeObject DapChainCsDagRoundType;

typedef struct PyDapChainCsDagRoundInfo{
    PyObject_HEAD
    dap_chain_cs_dag_event_round_info_t info;
}PyDapChainCsDagRoundInfoObject;

extern PyTypeObject DapChainCsDagRoundInfoType;

#define WRAPPING_DAP_CHAIN_CS_DAG_ROUND_NEW PyObject_New(PyDapChainCsDagRoundObject, &DapChainCsDagRoundType)