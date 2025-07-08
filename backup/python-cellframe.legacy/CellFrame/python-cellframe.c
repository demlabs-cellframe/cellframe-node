#include "python-cellframe.h"

#define LOG_TAG "python-cellframe"

static bool s_init_crypto = false;
static bool s_init_chain = false;
static bool s_init_app_cli = false;
static bool s_init_stream = false;
static bool s_init_stream_ctl = false;
static bool s_init_http_folder = false;
static bool s_init_http = false;
static bool s_init_http_enc = false;
static bool s_io_core = false;
static bool s_init_mempool = false;

//static bool s_init_http_client_simple = false;
static bool s_init_wallet = false;
static bool s_init_cs_dag = false;
static bool s_init_cs_dag_poa = false;
static bool s_init_cs_dag_pos = false;
static bool s_init_chain_net_srv = false;
static bool s_init_ks = false;

static bool submodules_deint;

PyObject* CellFrame_error = NULL;

static PyMethodDef DapPythonMethods[] = {
    {"init", python_dap_init, METH_VARARGS, "Initialization of the Python Cellframe library."},
    {"deinit", python_dap_deinit, METH_VARARGS, "Deinitialization of the Python Cellframe library."},
    {"setLogLevel", (PyCFunction)dap_set_log_level, METH_VARARGS, "Setting the logging level."},
    {"configGetItem", (PyCFunction)py_m_dap_config_get_item, METH_VARARGS, "Get an item from a configuration."},
    {"configGetSysDir", (PyCFunction)py_m_dap_config_get_sys_dir, METH_VARARGS, "Get config storage dir."},

    {}
};

static char CellFramePythonModuleDoc[] = "CellFrame SDK.Python v"DAP_VERSION" welcomes you!";

static PyModuleDef CellFramePythonModule =    DAP_PY_MODULE(.m_name = "CellFrame",     /* name of module */
                                                            .m_doc = CellFramePythonModuleDoc, /* module documentation, may be NULL */
                                                            .m_size = -1);             /* size of per-interpreter state of the module,
                                                                                    or -1 if the module keeps state in global variables. */

static PyModuleDef DapPythonModule =          DAP_PY_MODULE(.m_name = "DAP",
                                                            .m_doc = "DAP SDK.Python v"DAP_VERSION" welcomes you!",
                                                            .m_size = -1,
                                                            .m_methods = DapPythonMethods);

static PyModuleDef DapCorePythonModule =      DAP_PY_MODULE(.m_name = "DAP.Core",
                                                            .m_size = -1);

static PyModuleDef DapCryptoPythonModule =    DAP_PY_MODULE(.m_name = "DAP.Crypto",
                                                            .m_size = -1);

static PyModuleDef DapNetPythonModule =       DAP_PY_MODULE(.m_name = "DAP.Network",
                                                            .m_size = -1);

static PyModuleDef DapGlobalDBPythonModule =  DAP_PY_MODULE(.m_name = "DAP.GlobalDB",
                                                            .m_size = -1);

static PyModuleDef CellframeChainPythonModule =     DAP_PY_MODULE(.m_name = "Cellframe.Chain",
                                                                  .m_size = -1);

static PyModuleDef CellframeCommonPythonModule =    DAP_PY_MODULE(.m_name = "Cellframe.Common",
                                                                  .m_size = -1);

static PyModuleDef CellframeNetworkPythonModule =   DAP_PY_MODULE(.m_name = "Cellframe.Network",
                                                                  .m_size = -1);

static PyModuleDef CellframeServicesPythonModule =  DAP_PY_MODULE(.m_name = "Cellframe.Services",
                                                                  .m_size = -1);

static PyModuleDef CellframeConsensusPythonModule = DAP_PY_MODULE(.m_name = "Cellframe.Consensus",
                                                                  .m_size = -1);
#ifdef _WIN32

BOOL WINAPI consoleHandler(DWORD dwType){
    if (dwType == CTRL_C_EVENT){
        log_it(L_NOTICE, "Execution terminated. Ctrl+C is pressed");
        deinit_modules();
    }
    return TRUE;
}
#else

void sigfunc(int sig){
    if (sig == SIGINT){
        log_it(L_NOTICE, "Execution terminated. Ctrl+C is pressed");
        dap_events_stop_all();
        deinit_modules();
    }
}
#endif

PyObject *python_cellframe_init(PyObject *self, PyObject *args)
{
    PyObject *cellframeModules = args;
    Py_ssize_t size_list = PyList_Size(cellframeModules);
    for (int i=0; i < size_list;i++) {
        PyObject *value = PyList_GetItem(cellframeModules, i);
        const char *c_value = PyUnicode_AsUTF8(value);
        log_it(L_INFO, "Initializing \"%s\" module ...", c_value);
        if (strcmp(c_value, "Chain") == 0){
            if(dap_chain_init() != 0){
                PyErr_SetString(CellFrame_error, "Failed to initialize \"Chain\" module");
                return NULL;
            }
            if (dap_chain_cs_init() != 0){
                PyErr_SetString(CellFrame_error, "Failed to initialize \"ChainCS\" module");
                return NULL;
            }
        } else if (strcmp(c_value, "Mempool") == 0){
            if (dap_datum_mempool_init() != 0){
                PyErr_SetString(CellFrame_error, "Failed to initialize \"Mempool\" module");
                return NULL;
            }
            s_init_mempool = true;
        } else if (strcmp(c_value, "Wallet") == 0){
            if (dap_chain_wallet_init_py() != 0){
                PyErr_SetString(CellFrame_error, "Failed to initialize \"Wallet\" module");
                return NULL;
            }
            s_init_wallet = true;
        /*        } else if (strcmp(c_value, "ChainCSDag") == 0){
            if (dap_chain_cs_dag_init() != 0)
            {
                PyErr_SetString(CellFrame_error, "Failed to initialize ChainCSDag module. ");
                return NULL;
            }
        } else if (strcmp(c_value, "ChainCSDagPoa") == 0){
            if (dap_chain_cs_dag_poa_init() != 0){
                PyErr_SetString(CellFrame_error, "Failed to initialize ChainCSDagPoa module. ");
                return NULL;
            }
        } else if (strcmp(c_value, "ChainCSDagPos") == 0){
            if (dap_chain_cs_dag_pos_init() != 0){
                PyErr_SetString(CellFrame_error, "Failed to initialize ChainCSDagPos module. ");
                return NULL;
            } */
        } else if (strcmp(c_value, "ChainNetSrv") == 0){
            if (dap_chain_net_srv_init() != 0){
                PyErr_SetString(CellFrame_error, "Failed to initialize \"ChainNetSrv\" module");
                return NULL;
            }
        } else if (strcmp(c_value, "StreamChChainNet") == 0){
            if (dap_chain_net_ch_init() != 0 ){
                PyErr_SetString(CellFrame_error, "Failed to initialize \"StreamChChainNet\" module");
                return NULL;
            }
        }else if (strcmp(c_value, "StreamChChainNetSrv") == 0){
            if (dap_chain_net_ch_init() != 0 ){
                PyErr_SetString(CellFrame_error, "Failed to initialize \"StreamChChainNetSrv\" module");
                return NULL;
            }
        }else if (strcmp(c_value, "EncKS") == 0){
        //            if (dap_enc_ks_init())
        //            if (dap_enc_ks_
        } else if (strcmp(c_value, "GlobalDB") == 0){
            if ( dap_global_db_init() != 0 ) {
                PyErr_SetString(CellFrame_error, "Failed to initialize \"GlobalDB\" module");
                return NULL;
            }
        }else if (strcmp(c_value, "Client") == 0){
            if (dap_client_init() != 0){
                PyErr_SetString(CellFrame_error, "Failed to initialize \"Client\" module");
                return NULL;
            }
        }else if (strcmp(c_value, "Net") == 0){
            if (dap_chain_net_init_py() != 0 ){
                PyErr_SetString(CellFrame_error, "Failed to initialize \"Net\" module");
                return NULL;
            }
        }else if (strcmp(c_value, "AppCliServer") == 0){
            if (dap_chain_node_cli_init(g_config) != 0 ){
                PyErr_SetString(CellFrame_error, "Failed to initialize \"AppCliServer\" module" );
                return NULL;
            }
        }else{
            log_it(L_WARNING,"Unknown module: \"%s\"", c_value);
        }
        log_it(L_INFO, "Initialization of module is completed");
    }
    Py_RETURN_NONE;
}

static int dap_server_core_init(uint32_t l_thread_cnt, size_t conn_t)
{
    int result = dap_server_init();
    if ( result != 0 ) {
        log_it( L_CRITICAL, "Can't initialize \"socket server\" module" );
    }
    dap_events_init(l_thread_cnt, conn_t);
    return result;
}

static void dap_server_core_deinit(void)
{
    dap_server_deinit();
    dap_events_deinit();
}

PyObject *python_dap_init(PyObject *self, PyObject *args)
{
    const char *app_name;
    const char *file_name_log;
    const char *config_dir;
    const char *log_level;
    const char *JSON_str;

    s_init_ks = true;
    submodules_deint = false;

    PyObject *events = NULL;

    #ifdef _WIN32
        SetConsoleCtrlHandler((PHANDLER_ROUTINE)consoleHandler, TRUE);
    #else
        signal(SIGINT, sigfunc);
    #endif

    if (!PyArg_ParseTuple(args, "s", &JSON_str)){
        PyErr_SetString(CellFrame_error, "Argument must be a string");
        return NULL;
    }

    PyObject *JSON_Module = PyImport_ImportModule("json");
    if (JSON_Module == NULL) {
        PyErr_SetString(CellFrame_error, "json module was not imported");
        return NULL;
    }

    PyObject* JSONLoadsFunction = PyObject_GetAttrString(JSON_Module, "loads");
    if (JSONLoadsFunction == NULL) {
        PyErr_SetString(CellFrame_error, "json.loads function was not imported");
        return NULL;
    }

    PyObject* argsInLoadsJSON = PyTuple_Pack(1,PyUnicode_FromString(JSON_str));
    PyObject* result = PyObject_CallObject(JSONLoadsFunction, argsInLoadsJSON);
    if (result == NULL){
        PyErr_SetString(CellFrame_error, "Erron in \"json.loads\" function. Argument must be a JSON format string");
        return NULL;
    }
    PyObject* getModules = PyDict_GetItemString(result, "modules");
    if (getModules == NULL){
        PyErr_SetString(CellFrame_error, "Can't find \"modules\" object in JSON string");
        return NULL;
    }

    // DAP or Core
    PyObject* getDap = PyDict_GetItemString(result, "DAP");

    if (getDap == NULL)
        getDap = PyDict_GetItemString(result, "Core");

    if( getDap == NULL ){
        PyErr_SetString(CellFrame_error, "Can't find \"Core\" or \"DAP\" object in JSON string");
        return NULL;
    }

    /*Parse DAP*/
    PyObject* config_dir_PyObject = PyDict_GetItemString(getDap, "config_dir");
    if (config_dir_PyObject == NULL) {
        PyErr_SetString(CellFrame_error, "Can't find \"config_dir\" key in \"DAP\" object");
        return NULL;
    }
    PyObject* application_name_PyObject = PyDict_GetItemString(getDap, "application_name");
    if (application_name_PyObject == NULL) {
        PyErr_SetString(CellFrame_error, "Can't find \"application_name\" key in \"DAP\" object");
        return NULL;
    }
    PyObject* file_name_log_PyObject = PyDict_GetItemString(getDap, "file_name_log");
    if (file_name_log_PyObject == NULL) {
        PyErr_SetString(CellFrame_error, "Can't find \"file_name_log\" key in \"DAP\" object");
        return NULL;
    }
    PyObject* logLevel_PyObject = PyDict_GetItemString(getDap, "log_level");
    if (logLevel_PyObject == NULL) {
        PyErr_SetString(CellFrame_error, "Can't find \"log_level\" key in \"DAP\" object");
        return NULL;
    }
    app_name = PyUnicode_AsUTF8(application_name_PyObject);
    file_name_log = PyUnicode_AsUTF8(file_name_log_PyObject);
    config_dir = PyUnicode_AsUTF8(config_dir_PyObject);
    log_level = PyUnicode_AsUTF8(logLevel_PyObject);

    if (dap_common_init(app_name, file_name_log) != 0){
        PyErr_SetString(CellFrame_error, "Can't initialize CellFrame SDK library");
        return NULL;
    }
    dap_set_appname(app_name);
    if ( dap_strcmp( log_level, "L_DEBUG" )==0 || dap_strcmp( log_level, "DEBUG" )==0  ){
        dap_log_level_set(L_DEBUG);
    }else if ( dap_strcmp( log_level, "L_INFO" )==0 || dap_strcmp( log_level, "INFO" )==0  ){
        dap_log_level_set(L_INFO);
    }else if ( dap_strcmp( log_level, "L_NOTICE" )==0 || dap_strcmp( log_level, "NOTICE" )==0  ){
        dap_log_level_set(L_NOTICE);
    }else if ( dap_strcmp( log_level, "L_MSG" )==0 || dap_strcmp( log_level, "MSG" )==0  ){
        dap_log_level_set(L_MSG);
    }else if ( dap_strcmp( log_level, "L_DAP" )==0 || dap_strcmp( log_level, "DAP" )==0  ){
        dap_log_level_set(L_DAP);
    }else if ( dap_strcmp( log_level, "L_WARNING" )==0 || dap_strcmp( log_level, "WARNING" )==0  ){
        dap_log_level_set(L_WARNING);
    }else if ( dap_strcmp( log_level, "L_ATT" )==0 || dap_strcmp( log_level, "ATTENTION" )==0  ){
        dap_log_level_set(L_ATT);
    }else if ( dap_strcmp( log_level, "L_ERROR" )==0 || dap_strcmp( log_level, "ERROR" )==0  ){
        dap_log_level_set(L_ERROR);
    }else if ( dap_strcmp( log_level, "L_CRITICAL" )==0 || dap_strcmp( log_level, "CRITICAL" )==0  ){
        dap_log_level_set(L_CRITICAL);
    }
    //Init config
    dap_config_init(config_dir);
    if ((g_config = dap_config_open(app_name) ) == NULL){
        PyErr_SetString(CellFrame_error, "Can't inititialize general configurations");
        return NULL;
    }
    //Init modules
    log_it(L_INFO, "Initializing modules ...");
    if (!PyList_Check(getModules)){
        PyErr_SetString(CellFrame_error, "Can't find an array of module names");
        return NULL;
    }
    Py_ssize_t size_list = PyList_Size(getModules);
    for (int i=0; i < size_list;i++){
        PyObject *value = PyList_GetItem(getModules, i);
        const char *c_value = PyUnicode_AsUTF8(value);
        log_it(L_INFO, "Initializing \"%s\" module ...", c_value);
        if (strcmp(c_value, "Crypto") == 0){            //Init crypto
//            log_it(L_INFO, "Initializing the %s module", c_value);
            s_init_crypto = true;
            if (dap_crypto_init() != 0){
                PyErr_SetString(CellFrame_error, "Failed to initialize \"Crypto\" module");
                return NULL;
            }
            dap_cert_init();
        } else if (strcmp(c_value, "Server") == 0){
            if(dap_server_init() != 0 ){
                PyErr_SetString(CellFrame_error, "Failed to initialize \"Server\" module");
                return NULL;
            }
        }else if (strcmp(c_value, "IO") == 0){
            PyObject* getIOData = PyDict_GetItemString(result, "IO");
            if (getIOData == NULL){
                PyErr_SetString(CellFrame_error, "Failed to initialize \"IO\" module."
                                "Can't find \"IO\" object in JSON string");
                return NULL;
            }
            PyObject* Nl_thread_cnt = PyDict_GetItemString(getIOData, "thread_cnt");
            PyObject* Nl_conn = PyDict_GetItemString(getIOData, "conn");
            if ( (Nl_thread_cnt == NULL || Nl_conn == NULL) || !PyNumber_Check(Nl_thread_cnt) ||
                 !PyNumber_Check(Nl_conn)){
                PyErr_SetString(CellFrame_error, "Failed to initialize \"IO\" module."
                                                 "Values of \"thread_cnt\" and \"conn\" keys aren't numerical or are absent");
                return NULL;
            }
            PyObject *ll_thread_cnt= PyNumber_Long(Nl_thread_cnt);
            PyObject *ll_conn = PyNumber_Long(Nl_conn);
            uint32_t ul_thread_cnt = (uint32_t)PyLong_AsUnsignedLong(ll_thread_cnt);
            size_t ul_conn = PyLong_AsSize_t(ll_conn);
            if(py_server_init(ul_thread_cnt, ul_conn) != 0 ){
                PyErr_SetString(CellFrame_error, "Failed to initialize \"IO\" module");
                return NULL;
            }
            dap_events_init(ul_thread_cnt,0);
            events = _PyObject_New(&DapEventsObjectType);
            dap_events_start();
            s_io_core = true;

        } else if (strcmp(c_value, "Http") == 0){
            if(dap_http_init() != 0){
                PyErr_SetString(CellFrame_error, "Failed to initialize \"Http\" module");
                return NULL;
            }
            s_init_http = true;
        } else if (strcmp(c_value, "HttpSimple") == 0){
            if (dap_http_simple_module_init() != 0){
                PyErr_SetString(CellFrame_error, "Failed to initialize \"HttpSimple\" module");
                return NULL;
            }
        } else if (strcmp(c_value, "EncHttp") == 0){
            if(enc_http_init() != 0){
                PyErr_SetString(CellFrame_error, "Failed to initialize \"EncHttp\" module");
                return NULL;
            }
            s_init_http_enc = true;
        } else if (strcmp(c_value, "HttpFolder") == 0){
            if (dap_http_folder_init() !=0){
                PyErr_SetString(CellFrame_error, "Failed to initialize \"HttpFolder\" module");
                return NULL;
            }
            s_init_http_folder = true;
        } else if (strcmp(c_value, "Stream") == 0){
            PyObject* getStreamData = PyDict_GetItemString(result, "Stream");
            if (getStreamData == NULL){
                PyErr_SetString(CellFrame_error, "Failed to initialize \"Stream\" module."
                                "Can't find \"Stream\" object in JSON string");
                return NULL;
            }
            PyObject *debugDumpStreamHeadersObj = PyDict_GetItemString(getStreamData, "DebugDumpStreamHeaders");
            if (debugDumpStreamHeadersObj == NULL || !PyBool_Check(debugDumpStreamHeadersObj)){
                PyErr_SetString(CellFrame_error, "Failed to initialize \"Stream\" module."
                                                 "Value of \"DebugDumpStreamHeaders\" key isn't boolean");
                return NULL;
            }
            if(dap_stream_init(g_config) != 0){
                PyErr_SetString(CellFrame_error, "Failed to initialize \"Stream\" module");
                return NULL;
            }
            s_init_stream = true;
        } else if (strcmp(c_value, "StreamCtl") == 0){
            if (dap_stream_ctl_init_py(32) != 0){
                PyErr_SetString(CellFrame_error, "Failed to initialize \"StreamCtl\" module");
                return NULL;
            }
            s_init_stream_ctl = true;
        /*
        } else if (strcmp(c_value, "HttpClientSimple") == 0){
            if (dap_http_client_simple_init() != 0){
                PyErr_SetString(CellFrame_error, "Failed to initialize HttpClientSimple module. ");
                return NULL;
            }
            s_init_http_client_simple = true;*/
        }
    }
    python_cellframe_init(NULL, getModules);        // TODO replace it with module init function
    if (events == NULL)
        return PyLong_FromLong(0);
    else {
        Py_INCREF(events);
        return Py_BuildValue("iO", 0, events);
    }
}

PyMODINIT_FUNC PyInit_libDAP()
{
    /* === DAP === */
    if (
        // === Core ===
        PyType_Ready( &DapCoreObjectType ) < 0 ||
        PyType_Ready( &DapLogitObjectType ) < 0 ||
        PyType_Ready( &DapCommonObjectType ) < 0 ||
        PyType_Ready(&DapMathObjectType) < 0 ||
        PyType_Ready( &DapNodeAddrObjectType ) < 0 ||
#ifdef DAP_SUPPORT_PYTHON_PLUGINS
        PyType_Ready( &DapAppContextObjectType) < 0 ||
#endif
        // === Crypto ===
        PyType_Ready( &DapCryptoAlgoObjectType ) < 0 ||
        PyType_Ready( &DapCryptoCertObjectType ) < 0 ||
        PyType_Ready( &DapCryptoKeyTypeObjectType ) < 0 ||
        PyType_Ready( &DapCryptoKeyTypesObjectType ) < 0 ||
        PyType_Ready( &DapCryptoDataTypeObjectType ) < 0 ||
        PyType_Ready( &DapCryproSignTypeObjectType ) < 0 ||
        PyType_Ready( &DapCryptoSignObjectType ) < 0 ||
        PyType_Ready( &DapChainHashFastObjectType ) < 0 ||
        PyType_Ready( &DapPkeyObject_DapPkeyObjectType ) < 0 ||
        PyType_Ready( &PyCryptoGUUIDObjectType) < 0 ||
        // === Network ==
        PyType_Ready( &DapServerObjectType ) < 0 ||
        PyType_Ready( &DapEventsObjectType ) < 0 ||
        PyType_Ready( &DapEventsSocketObjectType ) < 0 ||
        PyType_Ready( &DapHttpCodeObjectType ) < 0 ||
        PyType_Ready( &DapHttpObjectType ) < 0 ||
        PyType_Ready( &DapHttpSimpleObjectType ) < 0 ||
        PyType_Ready( &DapClientHttpObjectType ) < 0 ||
        PyType_Ready( &DapHttpHeaderObjectType ) < 0 ||
        PyType_Ready( &DapEncServerObjectType ) < 0 ||
        PyType_Ready( &DapStreamObjectType ) < 0 ||
        PyType_Ready( &DapStreamCtlObjectType ) < 0 ||
        PyType_Ready( &DapClusterRoleObjectType) < 0 ||
        PyType_Ready( &DapClusterRolesObjectType ) < 0 ||
        PyType_Ready( &DapClusterMemberObjectType ) < 0 ||
        PyType_Ready( &DapJsonRpcRequestObjectType ) < 0 ||
        PyType_Ready( &DapJsonRpcResponseobjectType ) < 0 ||
        // === GlobalDB ==
        PyType_Ready( &DapGlobalDBObjectType ) < 0 ||
        PyType_Ready( &DapGlobalDBContainerObjectType ) < 0 ||
        PyType_Ready( &DapGlobalDBInstanceObjectType ) < 0 ||
        PyType_Ready( &DapGlobalDBRoleObjectType ) < 0 ||
        PyType_Ready( &DapGlobalDBRolesObjectType ) < 0 ||
        PyType_Ready( &DapGlobalDBClusterObjectType ) < 0
        ) {
        log_it(L_CRITICAL,"Not all python type objects are initialized for DAP module");
        return NULL;
    }
    PyObject *coreModule = PyModule_Create(&DapCorePythonModule);
    PyModule_AddObject(coreModule, "logIt", (PyObject *)&DapLogitObjectType);
    PyModule_AddObject(coreModule, "Common", (PyObject*)&DapCommonObjectType);
    PyModule_AddObject(coreModule, "Math", (PyObject *)&DapMathObjectType);
    PyModule_AddObject(coreModule, "NodeAddr", (PyObject*)&DapNodeAddrObjectType);
#ifdef DAP_SUPPORT_PYTHON_PLUGINS
    PyModule_AddObject(coreModule, "AppContext", (PyObject*)&DapAppContextObjectType);
#endif

    PyObject *cryptoModule = PyModule_Create(&DapCryptoPythonModule);
    PyObject *cryptoKeyTypes = PyObject_NEW(PyObject, &DapCryptoKeyTypesObjectType);
    PyModule_AddObject(cryptoModule, "Algo", (PyObject*)&DapCryptoAlgoObjectType);
    PyModule_AddObject(cryptoModule, "Cert", (PyObject*)&DapCryptoCertObjectType);
    PyModule_AddObject(cryptoModule, "Pkey", (PyObject*)&DapPkeyObject_DapPkeyObjectType);
    PyModule_AddObject(cryptoModule, "SignType", (PyObject*)&DapCryproSignTypeObjectType);
    PyModule_AddObject(cryptoModule, "Sign", (PyObject*)&DapCryptoSignObjectType);
    PyModule_AddObject(cryptoModule, "CryptoKeyType", (PyObject*)&DapCryptoKeyTypeObjectType);
    PyModule_AddObject(cryptoModule, "KeyTypes", cryptoKeyTypes);
    PyModule_AddObject(cryptoModule, "CryptoDataType", (PyObject*)&DapCryptoDataTypeObjectType);
    PyModule_AddObject(cryptoModule, "HashFast", (PyObject*)&DapChainHashFastObjectType);
    PyModule_AddObject(cryptoModule, "GUUID", (PyObject*)&PyCryptoGUUIDObjectType);

    PyObject *netModule = PyModule_Create(&DapNetPythonModule);
    PyModule_AddObject(netModule, "Server", (PyObject*)&DapServerObjectType);
    PyModule_AddObject(netModule, "Events", (PyObject*)&DapEventsObjectType);
    PyModule_AddObject(netModule, "EventsSocket", (PyObject*)&DapEventsSocketObjectType);
    PyModule_AddObject(netModule, "Http", (PyObject*)&DapHttpObjectType);
    PyModule_AddObject(netModule, "HttpCode", (PyObject*)&DapHttpCodeObjectType);
    PyModule_AddObject(netModule, "HttpSimple", (PyObject*)&DapHttpSimpleObjectType);
    PyModule_AddObject(netModule, "HttpHeader", (PyObject*)&DapHttpHeaderObjectType);
    PyModule_AddObject(netModule, "ClientHTTP", (PyObject*)&DapClientHttpObjectType);
    PyModule_AddObject(netModule, "EncHttp", (PyObject*)&DapEncServerObjectType);
    PyModule_AddObject(netModule, "Stream", (PyObject*)&DapStreamObjectType);
    PyModule_AddObject(netModule, "StreamCtl", (PyObject*)&DapStreamCtlObjectType);
    PyModule_AddObject(netModule, "JSONRPCRequest", (PyObject*)&DapJsonRpcRequestObjectType);
    PyModule_AddObject(netModule, "JSONRPCResponse", (PyObject*)&DapJsonRpcResponseobjectType);
    PyModule_AddObject(netModule, "Member", (PyObject*)&DapClusterMemberObjectType);
    //Object with roles for network cluster
    PyObject *obj_cluster_roles = PyObject_New(PyObject, &DapClusterRolesObjectType);
    PyModule_AddObject(netModule, "ClusterRoles", obj_cluster_roles);


    PyObject *globalDBModule = PyModule_Create(&DapGlobalDBPythonModule);
    PyModule_AddObject(globalDBModule, "DB", (PyObject*)&DapGlobalDBObjectType);
    PyModule_AddObject(globalDBModule, "Container", (PyObject*)&DapGlobalDBContainerObjectType);
    PyModule_AddObject(globalDBModule, "Instance", (PyObject*)&DapGlobalDBInstanceObjectType);
    PyModule_AddObject(globalDBModule, "Cluster", (PyObject*)&DapGlobalDBClusterObjectType);
    //Object with role for member global DB cluster
    PyObject *globalDBClusterRoles = PyObject_New(PyObject, &DapGlobalDBRolesObjectType);
    PyModule_AddObject(globalDBModule, "MemberRoles", globalDBClusterRoles);

    PyObject *dapModule = PyModule_Create(&DapPythonModule);
    PyModule_AddStringConstant(dapModule, "__author__", "Alexey Stratulat <alexey.stratulat@demlabs.net>");
    PyModule_AddStringConstant(dapModule, "__version__", DAP_VERSION);
    PyModule_AddObject(dapModule, "error", PyErr_NewException("DAP.error", NULL, NULL));
    PyObject *moduleDict = PyImport_GetModuleDict();
    Py_INCREF(coreModule);
    PyModule_AddObject(dapModule, "Core", coreModule);
    PyDict_SetItemString(moduleDict, "DAP.Core", coreModule);
    Py_INCREF(cryptoModule);
    PyModule_AddObject(dapModule, "Crypto", cryptoModule);
    PyDict_SetItemString(moduleDict, "DAP.Crypto", cryptoModule);
    Py_INCREF(netModule);
    PyModule_AddObject(dapModule, "Network", netModule);
    PyDict_SetItemString(moduleDict, "DAP.Network", netModule);
    PyModule_AddObject(dapModule, "GlobalDB", globalDBModule);
    PyDict_SetItemString(moduleDict, "DAP.GlobalDB", globalDBModule);
    Py_INCREF(globalDBModule);
    return dapModule;
}


PyMODINIT_FUNC PyInit_libCellFrame(void)
{
        /* === Cellframe === */
    if (
        // ==== Common ===
        PyType_Ready( &DapAppCliObjectType ) < 0 ||
        // === Chain ===
        PyType_Ready( &DapChainObjectType ) < 0 ||
        PyType_Ready( &DapChainIdObjectType ) < 0 ||
        PyType_Ready( &DapChainTypeObjectType ) < 0 ||
        PyType_Ready( &DapChainAtomIterObjectType ) < 0 ||
        PyType_Ready( &DapChainAtomPtrObjectType ) < 0 ||
        //PyType_Ready( &DapChainCellObjectType ) < 0 ||
        PyType_Ready( &DapChainMempoolObjectType ) < 0 ||
        PyType_Ready( &DapChainCellIdObjectType ) < 0 ||
        PyType_Ready( &DapChainHashSlowKindObjectType ) < 0 ||
        PyType_Ready( &DapChainHashSlowObjectType ) < 0 ||
        PyType_Ready( &DapChainAddrObjectType ) < 0 ||
        PyType_Ready( &DapChainCsObjectType ) < 0 ||
        PyType_Ready( &DapChainLedgerObjectType ) < 0 ||
        PyType_Ready( &DapChainWalletObjectType ) < 0 ||
        // === Chain datum
        /// Common
        PyType_Ready( &DapChainDatumTypeIdObjectType ) < 0 ||
        PyType_Ready( &DapChainDatumObjectType ) < 0 ||
        PyType_Ready( &DapChainDatumDecreeObjectType ) < 0 ||
        PyType_Ready( &DapChainDatumAnchorObjectType ) < 0 ||
        PyType_Ready( &DapChainDatumIterObjectType ) < 0 ||
        /// Token
        PyType_Ready( &DapChainDatumTokenObjectType ) < 0 ||
        PyType_Ready( &DapChainDatumTokenEmissionObjectType ) < 0 ||
        /// Transaction
        PyType_Ready( &DapChainDatumTxObjectType ) < 0 ||
        PyType_Ready( &DapChainTxItemTypeObjectType ) < 0 ||
        PyType_Ready( &DapChainTxTokenExtType ) < 0 ||
        PyType_Ready( &DapChainTxOutCondObjectType ) < 0 ||
        PyType_Ready( &DapChainTxOutCondSubTypeObjectType ) < 0 ||
        PyType_Ready( &DapChainTxOutCondSubTypeSrvPayObjectType ) < 0 ||
        PyType_Ready( &DapChainTxOutCondSubTypeSrvStakePosDelegateObjectType ) < 0 ||
        PyType_Ready( &DapChainTxOutCondSubTypeSrvStakeLockObjectType ) < 0 ||
        PyType_Ready( &DapChainTxOutCondSubTypeSrvStakeLockFlagObjectType ) < 0 ||
        PyType_Ready( &DapChainTxOutCondSubTypeSrvStakeLockFlagListObjectType ) < 0 ||
        PyType_Ready( &DapChainTxOutCondSubTypeSrvXchangeObjectType ) < 0 ||
        PyType_Ready( &DapChainTxInObjectType ) < 0 ||
        PyType_Ready( &DapChainTxInCondObjectType ) < 0 ||
        PyType_Ready( &DapChainTxSigObjectType ) < 0 ||
        PyType_Ready( &DapChainTxOutObjectType ) < 0 ||
        PyType_Ready( &DapChainTxTokenObjectType ) < 0 ||
        PyType_Ready( &DapChainTxPkeyObjectType ) < 0 ||
        PyType_Ready( &DapChainTxReceiptObjectType ) < 0 ||
        PyType_Ready( &DapChainTxOutExtObjectType ) < 0 ||
        PyType_Ready( &DapChainTxTSDObjectType ) < 0 ||
        PyType_Ready( &PyDapChainTXVoteObjectType) < 0 ||
        PyType_Ready( &PyDapChainTxVotingObjectType ) < 0 ||
        PyType_Ready( &DapChainTxOutStdObjectType ) < 0 ||
                // === Chain net ===
        /// Node
        PyType_Ready( &DapChainNodeObjectType ) < 0 ||
        PyType_Ready( &DapChainNodeCliObjectType ) < 0 ||
        PyType_Ready( &DapChainNodeClientObjectType ) < 0 ||
        PyType_Ready( &DapChainNodeInfoObjectType ) < 0 ||
        /// Net
        PyType_Ready( &DapChainNetObjectType ) < 0 ||
        PyType_Ready( &DapChainNetIdObjectType ) < 0 ||
        PyType_Ready( &DapChainNetStateObjectType ) < 0 ||
        /// Srv
        PyType_Ready( &DapChainNetSrvObjectType ) < 0 ||
        PyType_Ready( &DapChainNetSrvClientObjectType ) < 0 ||
        PyType_Ready( &DapChainNetSrvOrderDirectionObjectType ) < 0 ||
        PyType_Ready( &DapChainNetSrvOrderObjectType ) < 0 ||
        PyType_Ready( &DapChainNetSrvUidObjectType ) < 0 ||
        PyType_Ready( &DapChainNetSrvPriceObjectType ) < 0 ||
        PyType_Ready( &DapChainNetSrvPriceUnitUidObjectType ) < 0 ||
        /// Services
        PyType_Ready( &PyDapChainNetSrvStakePosDelegateObjectType ) < 0 ||
        PyType_Ready( &PyDapStreamChChainValidatorTestObjectType ) < 0 ||
        PyType_Ready( &DapChainNetSrvXchangeObjectType ) < 0 ||
        PyType_Ready( &PyDapChainNetSrvXchangeOrderObjectType ) < 0 ||
        PyType_Ready( &PyDapChainNetSrvVoteObjectType ) < 0 ||
        PyType_Ready( &DapChainNetSrvVoteInfoObjectType ) < 0 ||
        PyType_Ready( &DapChainNetSrvVoteInfoOptionObjectType ) < 0 ||
        // === Chain consensuses
        PyType_Ready( &DapChainCsDagPoaObjectType ) < 0 ||
        PyType_Ready(&DapChainCsBlockType) < 0 ||
        PyType_Ready(&DapChainCsDagType) < 0 ||
        PyType_Ready(&DapChainCsDagEventType) < 0 ||
        PyType_Ready(&DapChainCsDagRoundType) < 0 ||
        PyType_Ready(&DapChainCsDagRoundInfoType) < 0
        ) {
        log_it(L_CRITICAL,"Not all python type objects are initialized for CellFrame module");
        return NULL;
    }

    PyObject *chainModule = PyModule_Create(&CellframeChainPythonModule);
    PyModule_AddObject(chainModule, "Chain", (PyObject*)&DapChainObjectType);
    PyModule_AddObject(chainModule, "ChainType", (PyObject*)&DapChainTypeObjectType);
    PyModule_AddObject(chainModule, "ChainAtomIter", (PyObject*)&DapChainAtomIterObjectType);
    PyModule_AddObject(chainModule, "ChainAtomPtr", (PyObject*)&DapChainAtomPtrObjectType);
    //PyModule_AddObject(chainModule, "ChainCell", (PyObject*)&DapChainCellObjectType);
    PyModule_AddObject(chainModule, "ChainID", (PyObject*)&DapChainIdObjectType);
    PyModule_AddObject(chainModule, "ChainCellID", (PyObject*)&DapChainCellIdObjectType);
    PyModule_AddObject(chainModule, "ChainHashSlow", (PyObject*)&DapChainHashSlowObjectType);
    PyModule_AddObject(chainModule, "ChainHashSlowKind", (PyObject*)&DapChainHashSlowKindObjectType);
    PyModule_AddObject(chainModule, "ChainAddr", (PyObject*)&DapChainAddrObjectType);
    PyModule_AddObject(chainModule, "ChainCS", (PyObject*)&DapChainCsObjectType);
    PyModule_AddObject(chainModule, "Wallet", (PyObject*)&DapChainWalletObjectType);
    PyModule_AddObject(chainModule, "Mempool", (PyObject*)&DapChainMempoolObjectType);
    PyModule_AddObject(chainModule, "Ledger", (PyObject*)&DapChainLedgerObjectType);

    PyObject *commonModule = PyModule_Create(&CellframeCommonPythonModule);
    PyModule_AddObject(commonModule, "DatumTypeID", (PyObject*)&DapChainDatumTypeIdObjectType);
    PyModule_AddObject(commonModule, "Datum", (PyObject*)&DapChainDatumObjectType);
    PyModule_AddObject(commonModule, "DatumIter", (PyObject*)&DapChainDatumIterObjectType);
    PyModule_AddObject(commonModule, "DatumToken", (PyObject*)&DapChainDatumTokenObjectType);
    PyModule_AddObject(commonModule, "DatumTokenExt", (PyObject*)&DapChainTxTokenExtType);
    PyModule_AddObject(commonModule, "DatumEmission", (PyObject*)&DapChainDatumTokenEmissionObjectType);
    PyModule_AddObject(commonModule, "DatumDecree", (PyObject*)&DapChainDatumDecreeObjectType);
    PyModule_AddObject(commonModule, "DatumAnchor", (PyObject*)&DapChainDatumAnchorObjectType);
    PyModule_AddObject(commonModule, "TxItemType", (PyObject*)&DapChainTxItemTypeObjectType);
    PyModule_AddObject(commonModule, "DatumTx", (PyObject*)&DapChainDatumTxObjectType);
    PyModule_AddObject(commonModule, "TxOutCond", (PyObject*)&DapChainTxOutCondObjectType);
    PyModule_AddObject(commonModule, "TxOutCondSubtypeSrvPay", (PyObject*)&DapChainTxOutCondSubTypeSrvPayObjectType);
    PyModule_AddObject(commonModule, "TxOutCondSubtypeSrvStakeLock", (PyObject*)&DapChainTxOutCondSubTypeSrvStakeLockObjectType);
    //FLAGS TxOutCondSubtypeSrvStakeLock
    PyObject *obj_tx_out_cond_subtype_srv_stake_lock_flag = PyObject_New(PyObject, &DapChainTxOutCondSubTypeSrvStakeLockFlagListObjectType);
    PyModule_AddObject(commonModule, "TxOutCondSubtypeSrvStakeLockFlags", obj_tx_out_cond_subtype_srv_stake_lock_flag);

    PyModule_AddObject(commonModule, "TxOutCondSubtypeSrvStakePosDelegate", (PyObject*)&DapChainTxOutCondSubTypeSrvStakePosDelegateObjectType);
    PyModule_AddObject(commonModule, "TxOutCondSubtypeSrvXchange", (PyObject*)&DapChainTxOutCondSubTypeSrvXchangeObjectType);
    PyModule_AddObject(commonModule, "TxIn", (PyObject*)&DapChainTxInObjectType);
    PyModule_AddObject(commonModule, "TxInCond", (PyObject*)&DapChainTxInCondObjectType);
    PyModule_AddObject(commonModule, "TxOut", (PyObject*)&DapChainTxOutObjectType);
    PyModule_AddObject(commonModule, "TxPkey", (PyObject*)&DapChainTxPkeyObjectType);
    PyModule_AddObject(commonModule, "TxSig", (PyObject*)&DapChainTxSigObjectType);
    PyModule_AddObject(commonModule, "TxToken", (PyObject*)&DapChainTxTokenObjectType);
    PyModule_AddObject(commonModule, "TxReceipt", (PyObject*)&DapChainTxReceiptObjectType);
    PyModule_AddObject(commonModule, "TxOutExt", (PyObject*)&DapChainTxOutExtObjectType);
    PyModule_AddObject(commonModule, "TxTSD", (PyObject*)&DapChainTxTSDObjectType);
    PyModule_AddObject(commonModule, "TxVote", (PyObject*)&PyDapChainTXVoteObjectType);
    PyModule_AddObject(commonModule, "TxVoting", (PyObject*)&PyDapChainTxVotingObjectType);
    PyModule_AddObject(commonModule, "TxOutStd", (PyObject*)&DapChainTxOutStdObjectType);

    PyObject *netModule = PyModule_Create(&CellframeNetworkPythonModule);
    // === Chain node ===
    PyModule_AddObject(netModule, "Node", (PyObject*)&DapChainNodeObjectType);
    PyModule_AddObject(netModule, "NodeInfo", (PyObject*)&DapChainNodeInfoObjectType);
    PyModule_AddObject(netModule, "NodeClient", (PyObject*)&DapChainNodeClientObjectType);
    // === Chain net ===
    PyModule_AddObject(netModule, "Net", (PyObject*)&DapChainNetObjectType);
    PyModule_AddObject(netModule, "NetID", (PyObject*)&DapChainNetIdObjectType);
    PyModule_AddObject(netModule, "NetState", (PyObject*)&DapChainNetStateObjectType);
    // === Chain net srv ===
    PyModule_AddObject(netModule, "Service", (PyObject*)&DapChainNetSrvObjectType);
    PyModule_AddObject(netModule, "ServiceClient", (PyObject*)&DapChainNetSrvClientObjectType);
    PyModule_AddObject(netModule, "ServicePrice", (PyObject*)&DapChainNetSrvPriceObjectType);
    PyModule_AddObject(netModule, "ServiceOrder", (PyObject*)&DapChainNetSrvOrderObjectType);
    PyModule_AddObject(netModule, "ServiceOrderDirection", (PyObject*)&DapChainNetSrvOrderDirectionObjectType);
    PyModule_AddObject(netModule, "ServiceUID", (PyObject*)&DapChainNetSrvUidObjectType);
    PyModule_AddObject(netModule, "ServicePriceUnitUID", (PyObject*)&DapChainNetSrvPriceUnitUidObjectType);

    PyObject *servicesModule = PyModule_Create(&CellframeServicesPythonModule);
    PyModule_AddObject(servicesModule, "StakePosDelegate", (PyObject*)&PyDapChainNetSrvStakePosDelegateObjectType);
    PyModule_AddObject(servicesModule, "Xchange", (PyObject*)&DapChainNetSrvXchangeObjectType);
    PyModule_AddObject(servicesModule, "StreamChChainValidatorTest", (PyObject*)&PyDapStreamChChainValidatorTestObjectType);
    PyModule_AddObject(servicesModule, "Vote", (PyObject*)&PyDapChainNetSrvVoteObjectType);

    PyObject *csModule = PyModule_Create(&CellframeConsensusPythonModule);
    // === Chain cs dag poa
    PyModule_AddObject(csModule, "DagPoa", (PyObject*)&DapChainCsDagPoaObjectType);
    PyModule_AddObject(csModule, "Block", (PyObject*)&DapChainCsBlockType);
    PyModule_AddObject(csModule, "ChainCSDag", (PyObject*)&DapChainCsDagType);
    PyModule_AddObject(csModule, "DAG", (PyObject*)&DapChainCsDagEventType);
    // TODO PyModule_AddObject(csModule, "None", (PyObject*)&DapNonconsensusObjectType);

    PyObject *cellframeModule = PyModule_Create(&CellFramePythonModule);
    PyModule_AddStringConstant(cellframeModule, "__author__", "Alexey Stratulat <alexey.stratulat@demlabs.net>");
    PyModule_AddStringConstant(cellframeModule, "__version__", DAP_VERSION);
    CellFrame_error = PyErr_NewException("CellFrame.error", NULL, NULL);
    CellFrame_Xchange_error = PyErr_NewException("CellFrame.Service.XchangeError", NULL, NULL);
    DapChainNetSrvVoteError = PyErr_NewException("CellFrame.Service.VoteError", NULL, NULL);
    PyModule_AddObject(cellframeModule, "error", CellFrame_error);
    PyModule_AddObject(cellframeModule, "AppCli", (PyObject*)&DapAppCliObjectType);
    PyModule_AddObject(cellframeModule, "AppCliServer", (PyObject*)&DapChainNodeCliObjectType);
    PyObject *moduleDict = PyImport_GetModuleDict();
    Py_INCREF(chainModule);
    PyModule_AddObject(cellframeModule, "Chain", chainModule);
    PyDict_SetItemString(moduleDict, "CellFrame.Chain", chainModule);
    Py_INCREF(commonModule);
    PyModule_AddObject(cellframeModule, "Common", commonModule);
    PyDict_SetItemString(moduleDict, "CellFrame.Common", commonModule);
    Py_INCREF(netModule);
    PyModule_AddObject(cellframeModule, "Network", netModule);
    PyDict_SetItemString(moduleDict, "CellFrame.Network", netModule);
    Py_INCREF(servicesModule);
    PyModule_AddObject(servicesModule, "VoteError", DapChainNetSrvVoteError);
    PyModule_AddObject(cellframeModule, "Services", servicesModule);
    PyDict_SetItemString(moduleDict, "CellFrame.Services", servicesModule);
    Py_INCREF(csModule);
    PyModule_AddObject(cellframeModule, "Consensus", csModule);
    PyDict_SetItemString(moduleDict, "CellFrame.Consensus", csModule);
    return cellframeModule;
}

void deinit_modules(void){
    if (!submodules_deint){
        log_it(L_NOTICE, "Deintializing modules ...");
        if (s_init_crypto){
            dap_crypto_deinit();
            dap_cert_deinit();
        }
        if (s_init_chain){
            deinit_chain_py();
            dap_chain_cs_deinit_py();
        }
        if (s_init_stream){
            dap_stream_deinit();
        }
        if (s_init_stream_ctl){
            dap_stream_ctl_deinit();
        }
        if (s_init_http_folder){
            dap_http_folder_deinit();
        }
        if (s_init_http){
            dap_http_deinit();
        }
        if (s_io_core){
            py_server_deinit();
        }
        if (s_init_ks){
            dap_enc_ks_deinit();
        }
        dap_config_close(g_config);
        dap_config_deinit();
        dap_common_deinit();
        submodules_deint = true;
        log_it(L_INFO, "Deinitialization of modules is completed");
    }
    if (s_init_wallet){
        dap_chain_wallet_deinit_py();
    }
    dap_config_close(g_config);
    dap_config_deinit();
    dap_common_deinit();
}

PyObject *python_dap_deinit(PyObject *self, PyObject *args){
    deinit_modules();
    return PyLong_FromLong(0);
}

#ifndef DAP_SUPPORT_PYTHON_PLUGINS
int main(int argc, char **argv) {
    wchar_t *program = Py_DecodeLocale(argv[0], NULL);
    if (program == NULL) {
        fprintf(stderr, "Fatal error: cann't decode argv[0]\n");
        exit(1);
    }

    /* Add a built-in module, before Py_Initialize */
    PyImport_AppendInittab("CellFrame", PyInit_libCellFrame);

    /* Pass argv[0] to the Python interpreter */
    Py_SetProgramName(program);

    /* Initialize the Python interpreter.  Required. */
    Py_Initialize();

    /* Optionally import the module; alternatively,
       import can be deferred until the embedded script
       imports it. */
    PyImport_ImportModule(".");

    PyMem_RawFree(program);
    return 0;
}
#endif
