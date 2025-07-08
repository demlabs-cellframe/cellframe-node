#include "tpo.h"

PyObject *TPO_init(PyObject *self, PyObject *args){
    const char *app_name, *file_name_log, *config_dir, *s_log_level;
    if (!PyArg_ParseTuple(args, "s|s|s|s", &app_name, &file_name_log, &config_dir, &s_log_level)){
        return NULL;
    }
    if (dap_common_init(app_name, file_name_log) != 0){
        return  NULL;
    }
    dap_config_init(config_dir);
    if ((g_config = dap_config_open(app_name) ) == NULL){
        return NULL;
    }

    if (strcmp(s_log_level, "DEBUG") == 0 ){
        dap_log_level_set(L_DEBUG);
    } else if (strcmp(s_log_level, "INFO") == 0) {
        dap_log_level_set(L_INFO);
    } else if (strcmp(s_log_level, "NOTICE") == 0) {
        dap_log_level_set(L_NOTICE);
    }else if (strcmp(s_log_level, "MESSAGE") == 0) {
        dap_log_level_set(L_MSG);
    }else if (strcmp(s_log_level, "DAP") == 0) {
        dap_log_level_set(L_DAP);
    }else if (strcmp(s_log_level, "WARNING") == 0) {
        dap_log_level_set(L_WARNING);
    }else if (strcmp(s_log_level, "ATT") == 0) {
        dap_log_level_set(L_ATT);
    }else if (strcmp(s_log_level, "ERROR") == 0) {
        dap_log_level_set(L_ERROR);
    } else if (strcmp(s_log_level, "CRITICAL") == 0) {
            dap_log_level_set(L_CRITICAL);
    } else {
      dap_log_level_set(L_DEBUG);
    }
    return PyLong_FromLong(0);
}
PyObject *TPO_deinit(PyObject *self, PyObject *args){
    dap_config_close(g_config);
    dap_config_deinit();
    return PyLong_FromLong(0);
}

PyMODINIT_FUNC PyInit_libTPO(void){

    if (PyType_Ready(&DapObject_DapObjectType) < 0 )
               return NULL;

    PyObject *module = PyModule_Create(&TPOModule);
    PyModule_AddObject(module, "DEBUG", PyLong_FromLong(L_DEBUG));
    PyModule_AddObject(module, "INFO", PyLong_FromLong(L_INFO));
    PyModule_AddObject(module, "NOTICE", PyLong_FromLong(L_NOTICE));
    PyModule_AddObject(module, "MESSAGE", PyLong_FromLong(L_MSG));
    PyModule_AddObject(module, "DAP", PyLong_FromLong(L_DAP));
    PyModule_AddObject(module, "WARNING", PyLong_FromLong(L_WARNING));
    PyModule_AddObject(module, "ATT", PyLong_FromLong(L_ATT));
    PyModule_AddObject(module, "ERROR", PyLong_FromLong(L_ERROR));
    PyModule_AddObject(module, "CRITICAL", PyLong_FromLong(L_CRITICAL));
    return module;
}

