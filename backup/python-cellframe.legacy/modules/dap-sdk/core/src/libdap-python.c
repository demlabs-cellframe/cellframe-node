#include "libdap-python.h"
#include "python-cellframe_common.h"

#define LOG_TAG "libdap-python"

static PyMethodDef DapCoreMethods[] = {
        {NULL, NULL, 0, NULL}
};

PyTypeObject DapCoreObjectType = DAP_PY_TYPE_OBJECT(
        "DAP.Core", sizeof(PyDapObject),
        "Dap objects",
        .tp_methods = DapCoreMethods);

static PyMethodDef DapCommonMethods[] = {
        {"execWithRes", (PyCFunction)dap_exec_with_ret, METH_VARARGS | METH_STATIC, ""},
        {}
};

PyTypeObject DapCommonObjectType = DAP_PY_TYPE_OBJECT(
        "Dap.Common", sizeof(PyDapObject),
        "Dap common methods",
        .tp_methods = DapCommonMethods);

PyObject* dap_exec_with_ret(PyObject* self, PyObject *args){
    (void)self;
    char *str;
    if (!PyArg_ParseTuple(args, "s", &str)){
        return NULL;
    }
    char *l_ret = exec_with_ret_multistring(str);
    PyObject *l_res_obj = Py_BuildValue("s", l_ret);
    DAP_DELETE(l_ret);
    return l_res_obj;
}

static PyMethodDef DapLogitMethods[] = {
    {"debug", (PyCFunction)dap_log_it_debug, METH_VARARGS | METH_STATIC, "Log a message with the DEBUG level."},
    {"info", (PyCFunction)dap_log_it_info, METH_VARARGS | METH_STATIC, "Log a message with the INFO level."},
    {"notice", (PyCFunction)dap_log_it_notice, METH_VARARGS | METH_STATIC, "Log a message with the NOTICE level."},
    {"message", (PyCFunction)dap_log_it_message, METH_VARARGS | METH_STATIC, "Log a message with the MESSAGE level."},
    {"dap", (PyCFunction)dap_log_it_dap, METH_VARARGS | METH_STATIC, "Log a message with the DAP level."},
    {"warning", (PyCFunction)dap_log_it_warning, METH_VARARGS | METH_STATIC, "Log a message with the WARNING level."},
    {"att", (PyCFunction)dap_log_it_att, METH_VARARGS | METH_STATIC, "Log a message with the ATT level."},
    {"error", (PyCFunction)dap_log_it_error, METH_VARARGS | METH_STATIC, "Log a message with the ERROR level."},
    {"critical", (PyCFunction)dap_log_it_critical, METH_VARARGS | METH_STATIC, "Log a message with the CRITICAL level."},
    {}
};

PyTypeObject DapLogitObjectType = DAP_PY_TYPE_OBJECT(
        "Dap.logIt", sizeof(PyDapObject),
        "Dap LogIt methods",
        .tp_methods = DapLogitMethods);

PyObject *dap_set_log_level(PyObject *self, PyObject *args){
    short int new_log_level;
    if (!PyArg_ParseTuple(args, "h", &new_log_level))
        return NULL;
    if (new_log_level < 0 || new_log_level > 10 ) {
        return PyLong_FromLong(-1);
    } else {
        dap_log_level_set(new_log_level);
        return PyLong_FromLong(0);
    }
}

PyObject* dap_log_it(PyObject* self, PyObject* args){
    short int log_level;
    const char* string_output;
    const char* string_name_plugin = NULL;
    if (!PyArg_ParseTuple(args, "hs|s", &log_level, &string_output, &string_name_plugin))
        return NULL;
    if (log_level < 0 || log_level > 10 ) {
        return PyLong_FromLong(-1);
    } else {
        if (string_name_plugin){
            log_it(log_level, "[plugin: %s] %s", string_name_plugin, string_output);
        } else {
            log_it(log_level, "%s", string_output);
        }
        return PyLong_FromLong(0);
    }
}

PyObject* dap_log_it_debug(PyObject* self, PyObject* args){
    const char* string_output;
    const char* string_name_plugin = NULL;
    if (!PyArg_ParseTuple(args, "s|s", &string_output, &string_name_plugin)){
        return NULL;
    }
    if (string_name_plugin) {
        log_it(L_DEBUG, "[plugin: %s] %s", string_name_plugin, string_output);
    } else {
        log_it(L_DEBUG, "%s", string_output);
    }
    return PyLong_FromLong(0);
}
PyObject* dap_log_it_info(PyObject* self, PyObject* args){
    const char* string_output;
    const char* string_name_plugin = NULL;
    if (!PyArg_ParseTuple(args, "s|s", &string_output, &string_name_plugin)){
        return NULL;
    }
    if (string_name_plugin) {
        log_it(L_INFO, "[plugin: %s] %s", string_name_plugin, string_output);
    } else {
        log_it(L_INFO, "%s", string_output);
    }
    return PyLong_FromLong(0);
}
PyObject* dap_log_it_notice(PyObject* self, PyObject* args){
    const char* string_output;
    const char* string_name_plugin = NULL;
    if (!PyArg_ParseTuple(args, "s|s", &string_output, &string_name_plugin)){
        return NULL;
    }
    if (string_name_plugin) {
        log_it(L_NOTICE, "[plugin: %s] %s", string_name_plugin, string_output);
    } else {
        log_it(L_NOTICE, "%s", string_output);
    }
    return PyLong_FromLong(0);
}
PyObject* dap_log_it_message(PyObject* self, PyObject* args){
    const char* string_output;
    const char* string_name_plugin = NULL;
    if (!PyArg_ParseTuple(args, "s|s", &string_output, &string_name_plugin)){
        return NULL;
    }
    if (string_name_plugin) {
        log_it(L_MSG, "[plugin: %s] %s", string_name_plugin, string_output);
    } else {
        log_it(L_MSG, "%s", string_output);
    }
    return PyLong_FromLong(0);
}
PyObject* dap_log_it_dap(PyObject* self, PyObject* args){
    const char* string_output;
    const char* string_name_plugin = NULL;
    if (!PyArg_ParseTuple(args, "s|s", &string_output, &string_name_plugin)){
        return NULL;
    }
    if (string_name_plugin) {
        log_it(L_DAP, "[plugin: %s] %s", string_name_plugin, string_output);
    } else {
        log_it(L_DAP, "%s", string_output);
    }
    return PyLong_FromLong(0);
}
PyObject* dap_log_it_warning(PyObject* self, PyObject* args){
    const char* string_output;
    const char* string_name_plugin = NULL;
    if (!PyArg_ParseTuple(args, "s|s", &string_output, &string_name_plugin)){
        return NULL;
    }
    if (string_name_plugin) {
        log_it(L_WARNING, "[plugin: %s] %s", string_output, string_name_plugin);
    } else {
        log_it(L_WARNING, "%s", string_output);
    }
    return PyLong_FromLong(0);
}
PyObject* dap_log_it_att(PyObject* self, PyObject* args){
    const char* string_output;
    const char* string_name_plugin = NULL;
    if (!PyArg_ParseTuple(args, "s|s", &string_output, &string_name_plugin)){
        return NULL;
    }
    if (string_name_plugin) {
        log_it(L_ATT, "[plugin: %s] %s", string_output, string_name_plugin);
    } else {
        log_it(L_ATT, "%s", string_output);
    }
    return PyLong_FromLong(0);
}
PyObject* dap_log_it_error(PyObject* self, PyObject* args){
    const char* string_output;
    const char* string_name_plugin = NULL;
    if (!PyArg_ParseTuple(args, "s|s", &string_output, &string_name_plugin)){
        return NULL;
    }
    if (string_name_plugin) {
        log_it(L_ERROR, "[plugin: %s] %s", string_output, string_name_plugin);
    } else {
        log_it(L_ERROR, "%s", string_output);
    }
    return PyLong_FromLong(0);
}
PyObject* dap_log_it_critical(PyObject* self, PyObject* args){
    const char* string_output;
    const char* string_name_plugin = NULL;
    if (!PyArg_ParseTuple(args, "s|s", &string_output, &string_name_plugin)){
        return NULL;
    }
    if (string_name_plugin) {
        log_it(L_CRITICAL, "[plugin: %s] %s", string_output, string_name_plugin);
    } else {
        log_it(L_CRITICAL, "%s", string_output);
    }
    return PyLong_FromLong(0);
}

PyObject* py_m_dap_config_get_item(PyObject *self, PyObject *args){
    const char *section_path;
    const char *item_name;
    PyObject *obj_def = NULL;
    if (!PyArg_ParseTuple(args, "ss|O", &section_path, &item_name, &obj_def))
        return NULL;
    return python_get_config_item(g_config, section_path, item_name, obj_def);
}

PyObject* py_m_dap_config_get_sys_dir(PyObject *self, PyObject *args){
   
    return Py_BuildValue("s", g_sys_dir_path);
}

PyObject *dapListToPyList(dap_list_t *list) {
    ssize_t len = dap_list_length(list), i = 0;
    PyObject *pylist = PyList_New(len);
    dap_list_t *el;
    DL_FOREACH(list, el) {
        PyList_SetItem(pylist, i, PyBytes_FromString((const char*)el->data));
    }
    return pylist;
}

dap_list_t *pyListToDapList(PyObject *list) {
    PyObject *iter, *item;
    if (!(iter = PyObject_GetIter(list))) {
        // Empty list :c
        return NULL;
    }
    dap_list_t *dap_list = NULL;
    while ((item = PyIter_Next(iter))) {
        dap_list = dap_list_append(dap_list, PyBytes_AsString(item));
        Py_DECREF(item);
    }
    Py_DECREF(iter);
    return dap_list;
}
