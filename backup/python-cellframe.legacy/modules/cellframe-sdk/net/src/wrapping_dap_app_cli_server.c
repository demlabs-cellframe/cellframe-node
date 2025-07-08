#include "wrapping_dap_app_cli_server.h"

#define LOG_TAG "wrapping_dap_app_cli_server"

static PyMethodDef DapChainNodeCliMethods[] = {
        {"cmdItemCreate", dap_chain_node_cli_cmd_item_create_py, METH_VARARGS| METH_STATIC, ""},
        {"setReplyText", dap_chain_node_cli_set_reply_text_py, METH_VARARGS| METH_STATIC, ""},
        {"cli_exec_str", dap_chain_node_cli_cmd_exec_str, METH_VARARGS| METH_STATIC, ""},
        {}
};

PyTypeObject DapChainNodeCliObjectType = {
        .ob_base = PyVarObject_HEAD_INIT(NULL, 0)
        .tp_name = "CellFrame.AppCliServer",
        .tp_basicsize = sizeof(PyDapAppCliServerObject),
        .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
        "Chain net node cli object",
        .tp_methods = DapChainNodeCliMethods,
        .tp_new = DapChainNodeCliObject_new
};

int dap_chain_node_cli_init_py(dap_config_t *g_config){
    log_it(L_DEBUG, "Initializing application client server.");
    dap_chain_node_cli_init(g_config);
    l_str_reply_list = NULL;
    l_element_py_func_list = NULL;
    return 0;
}
void dap_chain_node_cli_delete_py(void){
    element_py_func_del_all();
    elements_str_reply_delete_all();
    dap_chain_node_cli_delete();
}

size_t elements_str_reply_add(char **a_str_reply)
{
    size_t max_index = 0;
    element_str_reply_t *el;
    LL_FOREACH(l_str_reply_list, el){
        if (max_index  < el->id)
            max_index = el->id;
    }
    size_t new_index = max_index+1;
    element_str_reply_t *new_el = DAP_NEW(element_str_reply_t);
    if (!new_el) {
        return 0;
    }
    new_el->str_reply = a_str_reply;
    new_el->id = new_index;
    LL_APPEND(l_str_reply_list, new_el);
    return new_index;
}
int elements_str_reply_cmp_by_id(element_str_reply_t *e1, element_str_reply_t *e2){
    if (e1->id == e2->id)
        return 0;
    else
        return 1;
}
char** elements_str_reply_get_by_id(size_t id){
    element_str_reply_t *el, *tmp;
    tmp = DAP_NEW(element_str_reply_t);
    if (!tmp) {
        return NULL;
    }
    tmp->id = id;
    LL_SEARCH(l_str_reply_list, el, tmp, elements_str_reply_cmp_by_id);
    DAP_FREE(tmp);
    if (el)
        return el->str_reply;
    return NULL;
}
void elements_str_reply_delete(size_t id){
     element_str_reply_t *el, *tmp;
     LL_FOREACH_SAFE(l_str_reply_list, el, tmp){
         if (id == el->id){
             LL_DELETE(l_str_reply_list, el);
             DAP_FREE(el);
         }
     }
}
void elements_str_reply_delete_all(){
    element_str_reply_t *el, *tmp;
    LL_FOREACH_SAFE(l_str_reply_list, el, tmp){
        LL_DELETE(l_str_reply_list, el);
        DAP_FREE(el);
    }
}

void element_py_func_add(const char *name, PyObject *func){
    element_py_func_t *el = DAP_NEW(element_py_func_t);
    if (!el) {
        return;
    }
    el->name = dap_strdup(name);
    el->func = func;
    Py_XINCREF(el->func);
    LL_APPEND(l_element_py_func_list, el);
}
int element_py_func_cmp_by_name(element_py_func_t *e1, element_py_func_t *e2){
    return dap_strcmp(e1->name, e2->name);
}
PyObject *element_py_func_get(char *name){
    element_py_func_t *el, *like;
    like = DAP_NEW(element_py_func_t);
    if (!like) {
        return NULL;
    }
    like->name = name;
    LL_SEARCH(l_element_py_func_list, el, like,  element_py_func_cmp_by_name);
    DAP_FREE(like);
    return el->func;
}
void element_py_func_del_by_name(char *name){
    element_py_func_t *el, *like;
    like = DAP_NEW(element_py_func_t);
    if (!like) {
        return;
    }
    like->name = name;
    LL_SEARCH(l_element_py_func_list, el, like,  element_py_func_cmp_by_name);
    DAP_FREE(like);
    LL_DELETE(l_element_py_func_list, el);
    Py_XDECREF(el->func);
    DAP_FREE(el);
}
void element_py_func_del_all(){
    element_py_func_t *el, *tmp;
    LL_FOREACH_SAFE(l_element_py_func_list, el, tmp){
        LL_DELETE(l_element_py_func_list, el);
        Py_XDECREF(el->func);
        DAP_FREE(el);
    }
}

static int wrapping_cmdfunc(int argc, char **argv, void **a_str_reply, int a_version)
{
    PyGILState_STATE l_state = PyGILState_Ensure();
    size_t id_str_replay = elements_str_reply_add((char **)a_str_reply);
    PyObject *obj_argv = stringToPyList(argc, argv);
    PyObject *obj_id_str_replay = PyLong_FromSize_t(id_str_replay);
    PyObject *arglist = Py_BuildValue("OO", obj_argv, obj_id_str_replay);
    Py_XINCREF(arglist);
    PyObject *binden_obj_cmdfunc = element_py_func_get(argv[0]);
    PyObject *result = PyObject_CallObject(binden_obj_cmdfunc, arglist);
    if (!result){
        log_it(L_DEBUG, "Function can't be called");
        python_error_in_log_it(LOG_TAG);
    }
    Py_XDECREF(arglist);
    Py_XDECREF(obj_argv);
    PyGILState_Release(l_state);
    elements_str_reply_delete(id_str_replay);
    return 0;
}

PyObject *DapChainNodeCliObject_new(PyTypeObject *type_object, PyObject *args, PyObject *kwds){
    PyDapAppCliServerObject *obj = (PyDapAppCliServerObject*)PyType_GenericNew(type_object, args, kwds);
    obj->func = wrapping_cmdfunc;
    return (PyObject *)obj;
}

PyObject *dap_chain_node_cli_cmd_item_create_py(PyObject *a_self, PyObject *a_args){
    (void) a_self;
    const char *name, *doc, *doc_ex;
    PyObject *obj_cmdfunc;
    if (!PyArg_ParseTuple(a_args, "s|O|s|s", &name, &obj_cmdfunc, &doc, &doc_ex)){
            return NULL;
    }else {
        if (!PyCallable_Check(obj_cmdfunc)){
            PyErr_SetString(PyExc_TypeError, "The second argumnet must be a callable");
            return NULL;
        }
    }
    element_py_func_add(name, obj_cmdfunc);
    dap_cli_server_cmd_add(name, wrapping_cmdfunc, doc, dap_chain_node_cli_cmd_id_from_str(name), doc_ex);
    return PyLong_FromLong(0);
}

PyObject *dap_chain_node_cli_set_reply_text_py(PyObject *self, PyObject *args){
    (void) self;
    PyObject *obj_id_str_reply;
    const char *str_reply_text;
    if (!PyArg_ParseTuple(args, "sO", &str_reply_text, &obj_id_str_reply))
        return NULL;
    size_t id_str_reply = PyLong_AsSize_t(obj_id_str_reply);
    dap_cli_server_cmd_set_reply_text((void **)elements_str_reply_get_by_id(id_str_reply), "%s", str_reply_text);
    return PyLong_FromLong(0);
}

char **PyListToString(PyObject *list){
    Py_ssize_t size = PyList_Size(list);
    char **result = DAP_NEW_SIZE(char*, size);
    for (Py_ssize_t i=0; i<size;i++){
        PyObject *element = PyList_GetItem(list, i);
        result[i] = dap_strdup(PyUnicode_AsUTF8(element));
    }
    return result;
}

PyObject *stringToPyList(int argc, char **list){
    PyObject *obj_list = PyList_New(argc);
    for (int i=0; i < argc; ++i){
        PyList_SetItem(obj_list, i, PyUnicode_FromString(list[i]));
    }
    return obj_list;
}

PyObject *dap_chain_node_cli_cmd_exec_str(PyObject *a_self, PyObject *a_args){
    
    const char *full_cmd;
    int l_version = 1;
    
    if (!PyArg_ParseTuple(a_args, "si", &full_cmd, &l_version))
        return NULL;

    char **l_argv = dap_strsplit(full_cmd, " ", -1);
    size_t l_argc = dap_str_countv(l_argv);
    
    char *cmd_name = l_argv[0];

    dap_cli_cmd_t *l_cmd = dap_cli_server_cmd_find(cmd_name);
    char *l_append_cmd = NULL;
    char *l_ncmd = NULL;

    if (!l_cmd)
        l_cmd = dap_cli_server_cmd_find_by_alias(cmd_name, &l_append_cmd, &l_ncmd);

    if(!l_cmd) {
        PyErr_SetString(PyExc_TypeError, "No such command found!");
        return NULL;
    }

    if(!l_argv) {
        PyErr_SetString(PyExc_TypeError, "Can't make parameters from string!");
        return NULL;
    }

    if(l_cmd->overrides.log_cmd_call)
        l_cmd->overrides.log_cmd_call(full_cmd);
      
    char *str_reply = NULL;

    if( !l_cmd->func)
    {
        PyErr_SetString(PyExc_TypeError, "No function for command, but registration present");
        return NULL;
    } 

    if (l_cmd->arg_func) {
        l_cmd->func_ex(l_argc, l_argv, l_cmd->arg_func, (void **)&str_reply, l_version);
    } else {
        l_cmd->func(l_argc, l_argv, (void **)&str_reply, l_version);
    }     
    
    dap_strfreev(l_argv);

    return Py_BuildValue("s", str_reply);
}
