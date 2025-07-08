#define PY_SSIZE_T_CLEAN
#include "Python.h"
#include "libdap-crypto-python.h"
#include "libdap_crypto_data_type.h"

#ifdef __cplusplus
extern "C" {
#endif

PyObject *TPO_init(PyObject *self, PyObject *args);
PyObject *TPO_deinit(PyObject *self, PyObject *args);

static PyMethodDef TPOPythonMethods[] = {
        {"init", TPO_init, METH_VARARGS, "Initialization of the python-cellframe interface DAP (Demlabs Application Protocol)"},
        {"deinit", TPO_deinit, METH_VARARGS, "Deinitialization of the python-cellframe interface DAP (Demlabs Application Protocol)"},
//        {"setLogLevel", (PyCFunction)dap_set_log_level, METH_VARARGS, "Setting the logging level"},
//        {"logIt", (PyCFunction)dap_log_it, METH_VARARGS, "The wrapper of the log_it function for the libdap library"},
//        {"logItDebug", (PyCFunction)dap_log_it_debug, METH_VARARGS, "The log_it wrapper for the libdap library displays information with the logging level DEBUG"},
//        {"logItInfo", (PyCFunction)dap_log_it_info, METH_VARARGS, "The log_it wrapper for the libdap library displays information with the logging level INFO"},
//        {"logItNotice", (PyCFunction)dap_log_it_notice, METH_VARARGS, "The log_it wrapper for the libdap library displays information with the logging level NOTICE"},
//        {"logItMessage", (PyCFunction)dap_log_it_message, METH_VARARGS, "The log_it wrapper for the libdap library displays information with the logging level MESSAGE"},
//        {"logItDap", (PyCFunction)dap_log_it_dap, METH_VARARGS, "The log_it wrapper for the libdap library displays information with the logging level DAP"},
//        {"logItWarning", (PyCFunction)dap_log_it_warning, METH_VARARGS, "The log_it wrapper for the libdap library displays information with the logging level WARNING"},
//        {"logItAtt", (PyCFunction)dap_log_it_att, METH_VARARGS, "The log_it wrapper for the libdap library displays information with the logging level ATT"},
//        {"logItError", (PyCFunction)dap_log_it_error, METH_VARARGS, "The log_it wrapper for the libdap library displays information with the logging level ERROR"},
//        {"logItCritical", (PyCFunction)dap_log_it_critical, METH_VARARGS, "The log_it wrapper for the libdap library displays information with the logging level CRITICAL"},
//        {"configGetItem", (PyCFunction)py_m_dap_config_get_item, METH_VARARGS, ""},
//        {"configGetItemDefault", (PyCFunction)py_m_dap_config_get_item_default, METH_VARARGS, ""},
        //{"deinit", dap_io_deinit, METH_NOARGS, "Deinitialization of the DAP (Demlabs Application Protocol) server core library"},
        //{"loop", dap_io_loop, METH_VARARGS, ""},
        //{"listen", dap_io_listen, METH_VARARGS, ""},
        {NULL, NULL, 0, NULL}
};

static struct PyModuleDef TPOModule = {
        PyModuleDef_HEAD_INIT,
        "libTPO",   /* name of module */
        NULL, /* module documentation, may be NULL */
        -1,       /* size of per-interpreter state of the module,
                 or -1 if the module keeps state in global variables. */
        TPOPythonMethods
};

PyMODINIT_FUNC PyInit_libTPO(void);


#ifdef __cplusplus
}
#endif

