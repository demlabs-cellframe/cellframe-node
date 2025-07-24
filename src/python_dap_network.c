/*
 * Python DAP Network Coordinator
 * Initializes and coordinates DAP SDK network subsystems
 * Imports and provides unified interface for network modules
 */

#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include "python_dap.h"
#include "python_dap_stream.h"
#include "python_dap_http.h"
#include "dap_common.h"
#include "dap_config.h"
#include "dap_stream.h"
#include "dap_stream_ctl.h"
#include "dap_stream_worker.h"
#include "dap_client.h"
#include "dap_http_server.h"

// External config reference
extern dap_config_t *g_config;

// Network subsystem initialization status
static bool s_network_initialized = false;
static bool s_stream_initialized = false;
static bool s_client_initialized = false;
static bool s_http_initialized = false;

// Network Module Initialization Functions

PyObject* dap_network_init_wrapper(PyObject* self, PyObject* args) {
    if (!PyArg_ParseTuple(args, "")) {
        return NULL;
    }
    
    if (s_network_initialized) {
        return PyLong_FromLong(0); // Already initialized
    }
    
    int result = 0;
    
    // Initialize stream subsystem
    if (!s_stream_initialized) {
        if (g_config) {
            result = dap_stream_init(g_config);
            if (result == 0) {
                result = dap_stream_ctl_init();
                if (result == 0) {
                    result = dap_stream_worker_init();
                    s_stream_initialized = (result == 0);
                }
            }
        }
    }
    
    // Initialize client subsystem  
    if (!s_client_initialized && result == 0) {
        result = dap_client_init();
        s_client_initialized = (result == 0);
    }
    
    // Initialize HTTP subsystem
    if (!s_http_initialized && result == 0) {
        result = dap_http_init();
        s_http_initialized = (result == 0);
    }
    
    s_network_initialized = (result == 0);
    
    return PyLong_FromLong(result);
}

PyObject* dap_network_deinit_wrapper(PyObject* self, PyObject* args) {
    if (!PyArg_ParseTuple(args, "")) {
        return NULL;
    }
    
    if (!s_network_initialized) {
        Py_RETURN_NONE; // Not initialized
    }
    
    // Deinitialize in reverse order
    if (s_http_initialized) {
        dap_http_deinit();
        s_http_initialized = false;
    }
    
    if (s_client_initialized) {
        dap_client_deinit();
        s_client_initialized = false;
    }
    
    if (s_stream_initialized) {
        dap_stream_worker_deinit();
        dap_stream_ctl_deinit();
        dap_stream_deinit();
        s_stream_initialized = false;
    }
    
    s_network_initialized = false;
    
    Py_RETURN_NONE;
}

PyObject* dap_network_status_wrapper(PyObject* self, PyObject* args) {
    if (!PyArg_ParseTuple(args, "")) {
        return NULL;
    }
    
    PyObject* status_dict = PyDict_New();
    if (!status_dict) {
        return NULL;
    }
    
    PyDict_SetItemString(status_dict, "network_initialized", 
                        s_network_initialized ? Py_True : Py_False);
    PyDict_SetItemString(status_dict, "stream_initialized", 
                        s_stream_initialized ? Py_True : Py_False);
    PyDict_SetItemString(status_dict, "client_initialized", 
                        s_client_initialized ? Py_True : Py_False);
    PyDict_SetItemString(status_dict, "http_initialized", 
                        s_http_initialized ? Py_True : Py_False);
    
    return status_dict;
}

// Network subsystem management
PyObject* dap_network_reinit_stream_wrapper(PyObject* self, PyObject* args) {
    if (!PyArg_ParseTuple(args, "")) {
        return NULL;
    }
    
    if (s_stream_initialized) {
        dap_stream_worker_deinit();
        dap_stream_ctl_deinit();
        dap_stream_deinit();
        s_stream_initialized = false;
    }
    
    int result = 0;
    if (g_config) {
        result = dap_stream_init(g_config);
        if (result == 0) {
            result = dap_stream_ctl_init();
            if (result == 0) {
                result = dap_stream_worker_init();
                s_stream_initialized = (result == 0);
            }
        }
    }
    
    return PyLong_FromLong(result);
}

PyObject* dap_network_reinit_client_wrapper(PyObject* self, PyObject* args) {
    if (!PyArg_ParseTuple(args, "")) {
        return NULL;
    }
    
    if (s_client_initialized) {
        dap_client_deinit();
        s_client_initialized = false;
    }
    
    int result = dap_client_init();
    s_client_initialized = (result == 0);
    
    return PyLong_FromLong(result);
}

PyObject* dap_network_reinit_http_wrapper(PyObject* self, PyObject* args) {
    if (!PyArg_ParseTuple(args, "")) {
        return NULL;
    }
    
    if (s_http_initialized) {
        dap_http_deinit();
        s_http_initialized = false;
    }
    
    int result = dap_http_init();
    s_http_initialized = (result == 0);
    
    return PyLong_FromLong(result);
}

// Combine all network module methods
PyMethodDef* py_dap_network_get_methods() {
    static PyMethodDef combined_methods[256]; // Static array for combined methods
    int method_count = 0;
    
    // Add network coordination methods
    PyMethodDef network_methods[] = {
        {"dap_network_init", dap_network_init_wrapper, METH_VARARGS, "Initialize all network subsystems"},
        {"dap_network_deinit", dap_network_deinit_wrapper, METH_VARARGS, "Deinitialize all network subsystems"},
        {"dap_network_status", dap_network_status_wrapper, METH_VARARGS, "Get network subsystems status"},
        {"dap_network_reinit_stream", dap_network_reinit_stream_wrapper, METH_VARARGS, "Reinitialize stream subsystem"},
        {"dap_network_reinit_client", dap_network_reinit_client_wrapper, METH_VARARGS, "Reinitialize client subsystem"},
        {"dap_network_reinit_http", dap_network_reinit_http_wrapper, METH_VARARGS, "Reinitialize HTTP subsystem"},
        {NULL, NULL, 0, NULL}
    };
    
    // Copy network methods
    for (int i = 0; network_methods[i].ml_name != NULL && method_count < 250; i++) {
        combined_methods[method_count++] = network_methods[i];
    }
    
    // Add stream methods
    PyMethodDef* stream_methods = dap_stream_methods;
    for (int i = 0; stream_methods[i].ml_name != NULL && method_count < 250; i++) {
        combined_methods[method_count++] = stream_methods[i];
    }
    
    // Add HTTP methods
    PyMethodDef* http_methods = dap_http_methods;
    for (int i = 0; http_methods[i].ml_name != NULL && method_count < 250; i++) {
        combined_methods[method_count++] = http_methods[i];
    }
    
    // Terminate array
    combined_methods[method_count] = (PyMethodDef){NULL, NULL, 0, NULL};
    
    return combined_methods;
} 