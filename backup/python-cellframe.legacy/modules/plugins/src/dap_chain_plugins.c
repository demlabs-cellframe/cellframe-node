#include "dap_config.h"
#include "dap_plugin.h"
#include "dap_common.h"
#include "dap_file_utils.h"
#include "python-cellframe.h"
#include "dap_chain_plugins.h"

#undef LOG_TAG
#define LOG_TAG "dap_chain_plugins"

static bool s_debug_more = false;

PyObject *s_sys_path = NULL;
const char *s_plugins_root_path = NULL;

PyThreadState *s_thread_state;

typedef struct _dap_chain_plugins_module{
    PyObject *module;
    char *name;
    struct _dap_chain_plugins_module *next;
}_dap_chain_plugins_module_t;

_dap_chain_plugins_module_t *_s_modules = NULL;

static int s_dap_chain_plugins_load(dap_plugin_manifest_t * a_manifest, void ** a_pvt_data, char ** a_error_str );
static int s_dap_chain_plugins_unload(dap_plugin_manifest_t * a_manifest, void * a_pvt_data, char ** a_error_str );
static void s_plugins_load_plugin_initialization(void* a_module);
static void s_plugins_load_plugin_uninitialization(void* a_module);

const char *pycfhelpers_path = "/opt/cellframe-node/python/lib/"PYTHON_VERSION"/site-packages/pycfhelpers";
const char *pycftools_path = "/opt/cellframe-node/python/lib/"PYTHON_VERSION"/site-packages/pycftools";
const char *plugins_path = "/opt/cellframe-node/var/lib/plugins/";
char *strings[]={"DAP", "CellFrame", NULL};

wchar_t *s_get_full_path(const char *a_prefix, const char *a_path)
{
    char *l_full_char_path = dap_strjoin("", a_prefix, "/", a_path, NULL);
    size_t l_len = strlen(l_full_char_path) + 1;
    wchar_t *l_ret = DAP_NEW_Z_SIZE(wchar_t, l_len * sizeof(wchar_t));
    mbstowcs(l_ret, l_full_char_path, l_len);
    DAP_DELETE(l_full_char_path);
    return l_ret;
}

int dap_chain_plugins_init(dap_config_t *a_config)
{
    if (!dap_config_get_item_bool_default(a_config, "plugins", "py_load", false))
        return -1;

    dap_plugin_type_callbacks_t l_callbacks={};
    l_callbacks.load = s_dap_chain_plugins_load;
    l_callbacks.unload = s_dap_chain_plugins_unload;
    dap_plugin_type_create("python",&l_callbacks);

    s_debug_more = dap_config_get_item_bool_default(a_config, "plugins", "debug_more", s_debug_more);

    const char *l_default_path_plugins = dap_strjoin(NULL, g_sys_dir_path, "/var/plugins/", NULL);
    const char *l_plugins_root_path = dap_config_get_item_str_path_default(a_config, "plugins", "py_path",
                                                        l_default_path_plugins);
    s_plugins_root_path = dap_strjoin("", l_plugins_root_path, "/", NULL);
    DAP_DELETE(l_default_path_plugins);

    log_it(L_INFO, "Start initialization of python (%s) plugins. Path plugins: %s", PYTHON_VERSION, s_plugins_root_path);
    if (!dap_dir_test(s_plugins_root_path)){
        log_it(L_ERROR, "Can't find \"%s\" directory", s_plugins_root_path);
        return -1;
    }
    PyImport_AppendInittab("DAP", PyInit_libDAP);
    PyImport_AppendInittab("CellFrame", PyInit_libCellFrame);

    PyStatus l_status;
    PyPreConfig l_preconfig;
    PyConfig l_config;
#ifdef DAP_BUILD_WITH_PYTHON_ENV
    PyPreConfig_InitIsolatedConfig(&l_preconfig);
    l_preconfig.utf8_mode = 1;

    #if DAP_OS_DARWIN
    char *pypath  = "/Applications/CellframeNode.app/Contents/Frameworks/";
    #else
    char *pypath  = g_sys_dir_path;
    #endif

    PyConfig_InitIsolatedConfig(&l_config);
    l_config.module_search_paths_set = 1;
    wchar_t *l_path = s_get_full_path(pypath, "python/lib/" PYTHON_VERSION);
    l_status = PyWideStringList_Append(&l_config.module_search_paths, l_path);
    DAP_DELETE(l_path);
    if (PyStatus_Exception(l_status))
        goto excpt;
    l_path = s_get_full_path(pypath, "python/lib/" PYTHON_VERSION "/lib-dynload");
    l_status = PyWideStringList_Append(&l_config.module_search_paths, l_path);
    DAP_DELETE(l_path);
    if (PyStatus_Exception(l_status))
        goto excpt;
    l_path = s_get_full_path(pypath, "python/lib/" PYTHON_VERSION "/site-packages");
    l_status = PyWideStringList_Append(&l_config.module_search_paths, l_path);
    DAP_DELETE(l_path);
    if (PyStatus_Exception(l_status))
        goto excpt;

    l_path = s_get_full_path(pypath, "python");
    l_status = PyConfig_SetString(&l_config, &l_config.base_exec_prefix, l_path);
    if (PyStatus_Exception(l_status)) {
        DAP_DELETE(l_path);
        goto excpt;
    }
    l_status = PyConfig_SetString(&l_config, &l_config.base_prefix, l_path);
    if (PyStatus_Exception(l_status)) {
        DAP_DELETE(l_path);
        goto excpt;
    }
    l_status = PyConfig_SetString(&l_config, &l_config.exec_prefix, l_path);
    if (PyStatus_Exception(l_status)) {
        DAP_DELETE(l_path);
        goto excpt;
    }
    l_status = PyConfig_SetString(&l_config, &l_config.prefix, l_path);
    DAP_DELETE(l_path);
    if (PyStatus_Exception(l_status))
        goto excpt;

    l_path = s_get_full_path(pypath, "python/bin/" PYTHON_VERSION);
    l_status = PyConfig_SetString(&l_config, &l_config.executable, l_path);
    DAP_DELETE(l_path);
    if (PyStatus_Exception(l_status))
        goto excpt;
#else
    PyPreConfig_InitPythonConfig(&l_preconfig);
    PyConfig_InitPythonConfig(&l_config);
#endif

    l_status = Py_PreInitialize(&l_preconfig);
    if (PyStatus_Exception(l_status))
        Py_ExitStatusException(l_status);

#ifdef DAP_OS_WINDOWS
    wchar_t l_progam_name[] = L"python";
#else
    wchar_t l_program_name[] = L"python3";
#endif
    l_status = PyConfig_SetString(&l_config, &l_config.program_name, l_program_name);
    if (PyStatus_Exception(l_status))
        goto excpt;

    l_status = Py_InitializeFromConfig(&l_config);

excpt:
    PyConfig_Clear(&l_config);
    if (PyStatus_Exception(l_status))
        Py_ExitStatusException(l_status);


    Py_Initialize();
    char py_path[1024];
    wchar_t *py_wpath = Py_GetPythonHome();
    if (!py_wpath)
        py_wpath = Py_GetPrefix();
    if (!py_wpath)
        py_wpath = Py_GetExecPrefix();
    wcstombs(py_path, py_wpath, 1024);
    log_it(L_NOTICE, "Python interpreter initialized from %s with version %s",
                                py_path, Py_GetVersion());

    PyObject *l_sys_module = PyImport_ImportModule("sys");
    s_sys_path = PyObject_GetAttrString(l_sys_module, "path");

    if (s_debug_more) {
        PyRun_SimpleString("import tracemalloc\n"
                           "tracemalloc.start(10)\n");
        PyRun_SimpleString("import sys\n"
                           "for attr in dir(sys):\n"
                               "\tprint(\"sys.%s = %r\" % (attr, getattr(sys, attr)))\n");
    }

    return 0;
}

void dap_chain_plugins_save_thread(dap_config_t *a_config)
{
    if (dap_config_get_item_bool_default(a_config, "plugins", "py_load", false))
        s_thread_state = PyEval_SaveThread();
}

static int s_dap_chain_plugins_load(dap_plugin_manifest_t * a_manifest, void ** a_pvt_data, char ** a_error_str ){
    log_it(L_NOTICE, "Loading plugins");
    dap_plugin_manifest_t *l_manifest = a_manifest;
    void *l_pvt_data = NULL;
    if (l_manifest == NULL){
        return -100;
    }

    if (*l_manifest->name == 0){
        log_it(L_ERROR, "Can't load a plugin, file not found");
        return -101;
    }
    log_it(L_NOTICE, "Check dependencies for plugin: %s", l_manifest->name);

    PyGILState_STATE l_gil_state;
    l_gil_state = PyGILState_Ensure();
    char * module_path = dap_strjoin("", s_plugins_root_path, l_manifest->name, "/", NULL);
    l_pvt_data = dap_chain_plugins_load_plugin_importing(module_path, l_manifest->name);
    DAP_DEL_Z(module_path);

    if (!l_pvt_data){
        PyGILState_Release(l_gil_state);
        return -102;
    }

    *a_pvt_data = l_pvt_data;
    s_plugins_load_plugin_initialization(l_pvt_data);
    PyGILState_Release(l_gil_state);
    return 0;

}

static int s_dap_chain_plugins_unload(dap_plugin_manifest_t * a_manifest, void * a_pvt_data, char ** a_error_str )
{
    log_it(L_NOTICE, "Unloading plugins");
    dap_plugin_manifest_t *l_manifest = a_manifest;
    void *l_pvt_data = a_pvt_data;
    if (l_manifest == NULL)
        return -100;
    if (*l_manifest->name == 0){
        log_it(L_ERROR, "Can't load a plugin, file not found");
        return -101;
    }
    PyGILState_STATE l_gil_state;
    l_gil_state = PyGILState_Ensure();
    s_plugins_load_plugin_uninitialization(l_pvt_data);
    PyGILState_Release(l_gil_state);
    return 0;
}


void* dap_chain_plugins_load_plugin_importing(const char *a_dir_path, const char *a_name) {
    log_it(L_NOTICE, "Import \"%s\" module from \"%s\" directory", a_name, a_dir_path);

    PyObject *l_obj_dir_path = PyUnicode_FromString(a_dir_path);
    PyList_Append(s_sys_path, l_obj_dir_path);
    Py_XDECREF(l_obj_dir_path);

    PyObject *l_module_name = PyUnicode_FromString(a_name);

    // Trying to get an already loaded module
    PyObject *l_ext_module = PyImport_GetModule(l_module_name);
    PyObject *l_module = NULL;

    if (l_ext_module) {
        // The module has already been imported, remove it from sys.modules
        log_it(L_NOTICE, "Module \"%s\" is already imported, reloading...", a_name);
        if (PyDict_DelItem(PyImport_GetModuleDict(), l_module_name) < 0) {
            python_error_in_log_it(LOG_TAG);
            log_it(L_ERROR, "Failed to remove module \"%s\" from sys.modules", a_name);
        } else {
            log_it(L_NOTICE, "Module \"%s\" removed from sys.modules", a_name);
        }
        Py_DECREF(l_ext_module);

        // Get the list of keys in sys.modules
        PyObject *modules_dict = PyImport_GetModuleDict();
        PyObject *modules_keys = PyDict_Keys(modules_dict);
        Py_ssize_t num_modules = PyList_Size(modules_keys);

        // Reload each module except for those in system paths or DAP and CellFrame related ones
        for (Py_ssize_t i = 0; i < num_modules; ++i) {
            PyObject *module_name = PyList_GetItem(modules_keys, i);
            const char *module_name_str = PyUnicode_AsUTF8(module_name);

            // Skip system modules
            int j = 0;
            bool sysmodule = false;
            while (strings[j]) {
                if (dap_strstr_len(module_name_str, strlen(module_name_str), strings[j]) != NULL) {
                    sysmodule = true;
                    break;
                }
                j++;
            }
            if (sysmodule) continue;

            // Get the module
            PyObject *module = PyImport_GetModule(module_name);
            if (!module) {
                continue;
            }

            // Get the file path of the module
            PyObject *module_file_attr = PyObject_GetAttrString(module, "__file__");
            if (!module_file_attr) {
                Py_DECREF(module);
                continue;
            }
            const char *module_file_path = PyUnicode_AsUTF8(module_file_attr);

            // Check if the module is in the site-packages or plugins path
            if (dap_strstr_len(module_file_path, strlen(module_file_path), pycfhelpers_path) != NULL ||
                dap_strstr_len(module_file_path, strlen(module_file_path), pycftools_path) != NULL ||
                dap_strstr_len(module_file_path, strlen(module_file_path), plugins_path) != NULL) {
                log_it(L_NOTICE, "Reloading module \"%s\" from \"%s\"...", module_name_str, module_file_path);
                if (PyImport_ReloadModule(module) == NULL) {
                    log_it(L_WARNING, "Failed to reload module \"%s\"", module_name_str);
                    PyErr_Clear();
                }
            }

            Py_DECREF(module_file_attr);
            Py_DECREF(module);
        }
        Py_DECREF(modules_keys);
    }

    // Import the module
    l_module = PyImport_ImportModule(a_name);
    if (!l_module) {
        python_error_in_log_it(LOG_TAG);
        log_it(L_ERROR, "Failed to import module \"%s\"", a_name);
    }

    Py_DECREF(l_module_name);

    if (!l_module) {
        return NULL;
    }

    _dap_chain_plugins_module_t *module = DAP_NEW(_dap_chain_plugins_module_t);
    if (!module) {
        python_error_in_log_it(LOG_TAG);
        PyErr_Clear();
        return NULL;
    }
    module->module = l_module;
    module->name = dap_strdup(a_name);
    Py_INCREF(l_module);
    return module;
}

static void s_plugins_load_plugin_initialization(void* a_module){
    if (!a_module)
        return;
    _dap_chain_plugins_module_t  *l_container = (_dap_chain_plugins_module_t  *)a_module;
    PyObject *l_func_init = PyObject_GetAttrString(l_container->module, "init");
    PyObject *l_func_deinit = PyObject_GetAttrString(l_container->module, "deinit");
    PyObject *l_res_int = NULL;
    PyErr_Clear();
    if (PyCallable_Check(l_func_init)) {
        PyObject *l_void_tuple = PyTuple_New(0);
        PyGILState_STATE l_gil_state;
        l_gil_state = PyGILState_Ensure();
        l_res_int = PyObject_CallObject(l_func_init, l_void_tuple);
        PyGILState_Release(l_gil_state);
        if (l_res_int && PyLong_Check(l_res_int)) {
            if (PyLong_AsInt(l_res_int) == 0) {
                Py_INCREF(l_container->module);
            } else {
                python_error_in_log_it(LOG_TAG);
                log_it(L_ERROR, "Can't initialize \"%s\" plugin. Code error: %i", l_container->name,
                       PyLong_AsInt(l_res_int));
            }
        } else {
            python_error_in_log_it(LOG_TAG);
            log_it(L_ERROR, "The 'init' function of \"%s\" plugin didn't return an integer value", l_container->name);
        }
        Py_XDECREF(l_res_int);
        Py_XDECREF(l_void_tuple);
    } else {
        log_it(L_ERROR, "Can't find 'init' function of \"%s\" plugin", l_container->name);
    }
    if (l_func_deinit == NULL || !PyCallable_Check(l_func_deinit)){
        log_it(L_WARNING, "Can't find 'deinit' function of \"%s\" plugin", l_container->name);
    }
}

static void s_plugins_load_plugin_uninitialization(void* a_module){
    if (!a_module)
        return;
    _dap_chain_plugins_module_t  *l_container = (_dap_chain_plugins_module_t  *)a_module;
    PyObject *l_func_deinit = PyObject_GetAttrString(l_container->module, "deinit");
    PyObject *l_res_int = NULL;
    PyErr_Clear();
    if (PyCallable_Check(l_func_deinit)) {
        PyObject *l_void_tuple = PyTuple_New(0);
        PyGILState_STATE l_gil_state;
        l_gil_state = PyGILState_Ensure();
        l_res_int = PyObject_CallObject(l_func_deinit, l_void_tuple);
        PyGILState_Release(l_gil_state);
        if (l_res_int && PyLong_Check(l_res_int)) {
            if (PyLong_AsInt(l_res_int) == 0) {
                //                dap_chain_plugins_list_add(l_container->module, l_container->name);
                Py_INCREF(l_container->module);
            } else {
                python_error_in_log_it(LOG_TAG);
                log_it(L_ERROR, "Can't deinitialize \"%s\" plugin. Code error: %i", l_container->name,
                       PyLong_AsInt(l_res_int));
            }
        } else {
            python_error_in_log_it(LOG_TAG);
            log_it(L_ERROR, "The 'deinit' function of \"%s\" plugin didn't return an integer value", l_container->name);
        }
        Py_XDECREF(l_res_int);
        Py_XDECREF(l_void_tuple);
    } else {
        log_it(L_ERROR, "Can't find 'deinit' function of \"%s\" plugin", l_container->name);
    }
}

void dap_chain_plugins_load_plugin(const char *a_dir_path, const char *a_name){
    log_it(L_NOTICE, "Loading \"%s\" plugin directory %s", a_name, a_dir_path);
    PyErr_Clear();

    PyObject *l_obj_dir_path = PyUnicode_FromString(a_dir_path);
    PyList_Append(s_sys_path, l_obj_dir_path);
    Py_XDECREF(l_obj_dir_path);
    PyObject *l_module = PyImport_ImportModule(a_name);
    python_error_in_log_it(LOG_TAG);
    PyObject *l_func_init = PyObject_GetAttrString(l_module, "init");
    PyObject *l_func_deinit = PyObject_GetAttrString(l_module, "deinit");
    PyObject *l_res_int = NULL;
    PyErr_Clear();
    if (l_func_init != NULL && PyCallable_Check(l_func_init)){
        PyObject *l_void_tuple = PyTuple_New(0);
        l_res_int = PyObject_CallObject(l_func_init, l_void_tuple);
        if (l_res_int && PyLong_Check(l_res_int)){
            if (PyLong_AsInt(l_res_int) != 0){
                python_error_in_log_it(LOG_TAG);
                log_it(L_ERROR, "Can't initialize \"%s\" plugin. Code error: %i", a_name, PyLong_AsInt(l_res_int));
            }
        } else {
            python_error_in_log_it(LOG_TAG);
            log_it(L_ERROR, "The 'init' function of \"%s\" plugin didn't return an integer value", a_name);
        }
        Py_XDECREF(l_res_int);
        Py_XDECREF(l_void_tuple);
    }else {
        log_it(L_ERROR, "Can't find 'init' function of \"%s\" plugin", a_name);
    }
    if (l_func_deinit == NULL || !PyCallable_Check(l_func_deinit)){
        log_it(L_WARNING, "Can't find 'deinit' function of \"%s\" plugin", a_name);
    }
}
