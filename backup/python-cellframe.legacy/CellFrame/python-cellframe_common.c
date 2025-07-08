#include <Python.h>
#if PY_MAJOR_VERSION > 3 || (PY_MAJOR_VERSION == 3 && PY_MINOR_VERSION > 11)
#include <pytypedefs.h>
#endif
#include <patchlevel.h>
#include <frameobject.h>

#include "python-cellframe_common.h"

char* _PyErr_get_stacktrace(PyObject *a_obj){
    if (!a_obj){
        return "No stack trace";
    }
    PyTracebackObject *l_traceback = (PyTracebackObject*)a_obj;
    char  *s = "\tStack trace:\n";
    size_t cnt = 0;
    while (l_traceback != NULL)  {
        const char *l_name, *l_file;
#if PY_MAJOR_VERSION == 3 && PY_MINOR_VERSION < 10
        l_name = l_file = "unknown";
#else
        PyCodeObject *l_code = PyFrame_GetCode(l_traceback->tb_frame);
        l_name = PyUnicode_AsUTF8(l_code->co_name);
        l_file = PyUnicode_AsUTF8(l_code->co_filename);
#endif
        int l_lineo = l_traceback->tb_lineno;
        s = dap_strdup_printf("%s\t\t(%zu) File \"%s\", line %d, in %s\n", s, cnt, l_file, l_lineo, l_name);
        l_traceback = l_traceback->tb_next;
        cnt++;
    }
    return s;
}

void python_error_in_log_it(const char *a_tag){
    PyObject *type, *value, *trackback;

    PyErr_Fetch(&type, &value, &trackback);
    PyErr_NormalizeException(&type, &value, &trackback);

    PyObject* str_exc_value = PyObject_Repr(value);
    PyObject* exect_value_str = PyUnicode_AsEncodedString(str_exc_value, "utf-8", "strict");

    const char *l_str_value = PyBytes_AS_STRING(exect_value_str);

    _PyErr_logIt(L_ERROR, a_tag, "An exception occurred while executing a Python script.\n"
                    "\t%s\n%s", l_str_value ? l_str_value : "(null)",
                    trackback ? _PyErr_get_stacktrace(trackback) : "(null)");

    PyErr_Restore(type, value, trackback);
}

PyObject *python_get_config_item(dap_config_t* a_config, const char *a_section, const char *a_key, PyObject *obj_default) {
    dap_config_item_type_t l_type_item = dap_config_get_item_type(
            a_config, a_section, a_key);
    switch (l_type_item) {
        case DAP_CONFIG_ITEM_UNKNOWN: {
            if (obj_default != NULL) {
                return obj_default;
            }
            PyErr_SetString(PyExc_ValueError, "Value can't be obtained. Either no such section or a key is missing in section");
            return NULL;
        }
        case DAP_CONFIG_ITEM_ARRAY: {
            uint16_t l_values_count = 0;
            const char **l_values = dap_config_get_array_str(a_config, a_section, a_key, &l_values_count);
            PyObject *obj_list = PyList_New(l_values_count);
            for (uint16_t i = 0; i < l_values_count; i++) {
                const char *l_value = l_values[i];
                PyObject *obj_unicode = PyUnicode_FromString(l_value);
                PyList_SetItem(obj_list, i, obj_unicode);
            }
            return obj_list;
        }
        case DAP_CONFIG_ITEM_BOOL: {
            if (dap_config_get_item_bool(a_config, a_section, a_key))
                Py_RETURN_TRUE;
            else
                Py_RETURN_FALSE;
        }
        case DAP_CONFIG_ITEM_DECIMAL: {
            int64_t res = dap_config_get_item_int64(a_config, a_section, a_key);
            return Py_BuildValue("L", res);
        }
        case DAP_CONFIG_ITEM_STRING: {
            const char *res = dap_config_get_item_str(a_config, a_section, a_key);
            return Py_BuildValue("s", res);
        }
        default:;
    }
    Py_RETURN_NONE;
}
