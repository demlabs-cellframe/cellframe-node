#pragma once

#include <Python.h>
#include "dap_config.h"
#include "dap_chain_node_cli.h"
#include "dap_chain_node_cli_cmd.h"
#include "wrapping_dap_chain_common.h"
#include "wrapping_dap_chain_net_node.h"
#include "utlist.h"
#include "python-cellframe_common.h"

typedef struct PyDapAppCliServer{
    PyObject_HEAD
    dap_cli_server_cmd_callback_t func;
}PyDapAppCliServerObject;

typedef struct element_str_reply{
    char **str_reply;
    size_t id;
    struct element_str_reply *next;
}element_str_reply_t;

static element_str_reply_t *l_str_reply_list;
size_t elements_str_reply_add(char **a_str_reply);
int elements_str_reply_cmp_by_id(element_str_reply_t *e1, element_str_reply_t *e2);
char** elements_str_reply_get_by_id(size_t id);
void elements_str_reply_delete(size_t id);
void elements_str_reply_delete_all();

typedef struct element_py_func{
    char *name;
    PyObject *func;
    struct element_py_func *next;
}element_py_func_t;

static element_py_func_t *l_element_py_func_list;

void element_py_func_add(const char *name, PyObject *func);
int element_py_func_cmp_by_name(element_py_func_t *e1, element_py_func_t *e2);
PyObject *element_py_func_get(char *name);
void element_py_func_del_by_name(char *name);
void element_py_func_del_all();


//static PyObject *binded_object_cmdfunc = NULL;
//static char** l_str_reply = NULL;

int dap_chain_node_cli_init_py(dap_config_t *g_config);
void dap_chain_node_cli_delete_py(void);

PyObject *DapChainNodeCliObject_new(PyTypeObject *type_object, PyObject *args, PyObject *kwds);

PyObject *dap_chain_node_cli_cmd_item_create_py(PyObject *a_self, PyObject *a_args);
PyObject *dap_chain_node_cli_set_reply_text_py(PyObject *self, PyObject *args);

PyObject *dap_chain_node_cli_cmd_exec_str(PyObject *self, PyObject *args);

extern PyTypeObject DapChainNodeCliObjectType;

char **PyListToString(PyObject *list);
//PyObject *stringToPyList(char **list);
PyObject *stringToPyList(int argc, char **list);
