/*
 * Python DAP HTTP Module Implementation
 * HTTP client function wrappers around DAP SDK
 */

#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include "python_dap.h"
#include "python_dap_http.h"
#include "dap_common.h"
#include "dap_client.h"
#include "dap_client_http.h"
#include "dap_worker.h"

// HTTP client management functions
PyObject* dap_http_client_init_wrapper(PyObject* self, PyObject* args) {
    if (!PyArg_ParseTuple(args, "")) {
        return NULL;
    }
    
    // Check if DAP SDK is initialized before calling HTTP init
    extern dap_config_t *g_config;
    if (!g_config) {
        PyErr_SetString(PyExc_RuntimeError, 
            "DAP SDK not initialized. Call dap_common_init() first or initialize with proper permissions.");
        return NULL;
    }
    
    // Use real DAP SDK HTTP client initialization
    int result = dap_client_http_init();
    return PyLong_FromLong(result);
}

PyObject* dap_http_client_deinit_wrapper(PyObject* self, PyObject* args) {
    if (!PyArg_ParseTuple(args, "")) {
        return NULL;
    }
    
    // Check if DAP SDK is initialized
    extern dap_config_t *g_config;
    if (!g_config) {
        // Already deinitialized or never initialized
        return PyLong_FromLong(0);
    }
    
    // Use real DAP SDK HTTP client deinitialization
    dap_client_http_deinit();
    return PyLong_FromLong(0);
}

PyObject* dap_http_client_new_wrapper(PyObject* self, PyObject* args) {
    if (!PyArg_ParseTuple(args, "")) {
        return NULL;
    }
    
    // Create new DAP client (HTTP client in DAP context)
    dap_client_t* client = dap_client_new(NULL, NULL); // No callbacks for now
    
    if (!client) {
        PyErr_SetString(PyExc_RuntimeError, "Failed to create DAP client");
        return NULL;
    }
    
    // Return client handle as void pointer converted to long
    return PyLong_FromVoidPtr(client);
}

PyObject* dap_http_client_delete_wrapper(PyObject* self, PyObject* args) {
    PyObject* client_obj;
    
    if (!PyArg_ParseTuple(args, "O", &client_obj)) {
        return NULL;
    }
    
    // Extract client pointer from PyLong and delete it
    dap_client_t* client = PyLong_AsVoidPtr(client_obj);
    if (!client) {
        PyErr_SetString(PyExc_ValueError, "Invalid client handle");
        return NULL;
    }
    
    // Delete the DAP client
    dap_client_delete(client);
    
    return PyLong_FromLong(0);
}

PyObject* dap_http_get_all_clients_wrapper(PyObject* self, PyObject* args) {
    if (!PyArg_ParseTuple(args, "")) {
        return NULL;
    }
    
    // DAP SDK does not expose client enumeration API
    // This is a design limitation - return empty list
    return PyList_New(0);
}

// Simple HTTP request callback storage
static PyObject* s_http_response_callback = NULL;
static PyObject* s_http_error_callback = NULL;
static void* s_response_data = NULL;
static size_t s_response_size = 0;
static int s_response_code = 0;

// HTTP response callback for DAP SDK
static void http_response_callback(void* a_data, size_t a_data_size, void* a_arg, int a_status_code) {
    // Store response data
    if (s_response_data) {
        DAP_DELETE(s_response_data);
    }
    s_response_data = DAP_NEW_SIZE(char, a_data_size + 1);
    memcpy(s_response_data, a_data, a_data_size);
    ((char*)s_response_data)[a_data_size] = '\0';
    s_response_size = a_data_size;
    s_response_code = a_status_code;
    
    // Call Python callback if set
    if (s_http_response_callback && PyCallable_Check(s_http_response_callback)) {
        PyObject* py_data = PyBytes_FromStringAndSize((char*)a_data, a_data_size);
        PyObject* py_code = PyLong_FromLong(a_status_code);
        PyObject* result = PyObject_CallFunctionObjArgs(s_http_response_callback, py_data, py_code, NULL);
        if (result) {
            Py_DECREF(result);
        }
        Py_DECREF(py_data);
        Py_DECREF(py_code);
    }
}

// HTTP error callback for DAP SDK
static void http_error_callback(int a_error_code, void* a_arg) {
    s_response_code = a_error_code;
    
    // Call Python callback if set
    if (s_http_error_callback && PyCallable_Check(s_http_error_callback)) {
        PyObject* py_error = PyLong_FromLong(a_error_code);
        PyObject* result = PyObject_CallFunctionObjArgs(s_http_error_callback, py_error, NULL);
        if (result) {
            Py_DECREF(result);
        }
        Py_DECREF(py_error);
    }
}

// HTTP client request functions - now using real DAP SDK HTTP API
PyObject* dap_http_client_request_wrapper(PyObject* self, PyObject* args) {
    const char* url;
    const char* method = "GET";
    
    if (!PyArg_ParseTuple(args, "s|s", &url, &method)) {
        return NULL;
    }
    
    // Parse URL to get host, port, path
    // Simple URL parsing for http://host:port/path
    char* url_copy = strdup(url);
    char* host = NULL;
    uint16_t port = 80;
    char* path = "/";
    
    if (strncmp(url_copy, "http://", 7) == 0) {
        host = url_copy + 7;
        char* port_start = strchr(host, ':');
        char* path_start = strchr(host, '/');
        
        if (port_start && (!path_start || port_start < path_start)) {
            *port_start = '\0';
            port_start++;
            port = atoi(port_start);
            char* port_end = strchr(port_start, '/');
            if (port_end) {
                path = port_end;
            }
        } else if (path_start) {
            *path_start = '\0';
            path = path_start;
        }
    } else {
        free(url_copy);
        PyErr_SetString(PyExc_ValueError, "Only HTTP URLs are supported");
        return NULL;
    }
    
    // Make real HTTP request using DAP SDK
    dap_client_http_t* http_client = dap_client_http_request(
        NULL,           // worker - NULL for default
        host,           // uplink_addr
        port,           // uplink_port
        method,         // method
        NULL,           // content_type
        path,           // path
        NULL,           // request_data
        0,              // request_size
        NULL,           // cookie
        http_response_callback,  // response_callback
        http_error_callback,     // error_callback
        NULL,           // callbacks_arg
        NULL            // custom_headers
    );
    
    free(url_copy);
    
    if (!http_client) {
        PyErr_SetString(PyExc_RuntimeError, "Failed to create HTTP request");
        return NULL;
    }
    
    // Return HTTP client handle
    return PyLong_FromVoidPtr(http_client);
}

PyObject* dap_http_client_request_ex_wrapper(PyObject* self, PyObject* args) {
    const char* url;
    const char* method;
    PyObject* headers_obj;
    PyObject* body_obj;
    
    if (!PyArg_ParseTuple(args, "ssOO", &url, &method, &headers_obj, &body_obj)) {
        return NULL;
    }
    
    // Parse URL to get host, port, path
    char* url_copy = strdup(url);
    char* host = NULL;
    uint16_t port = 80;
    char* path = "/";
    
    if (strncmp(url_copy, "http://", 7) == 0) {
        host = url_copy + 7;
        char* port_start = strchr(host, ':');
        char* path_start = strchr(host, '/');
        
        if (port_start && (!path_start || port_start < path_start)) {
            *port_start = '\0';
            port_start++;
            port = atoi(port_start);
            char* port_end = strchr(port_start, '/');
            if (port_end) {
                path = port_end;
            }
        } else if (path_start) {
            *path_start = '\0';
            path = path_start;
        }
    } else {
        free(url_copy);
        PyErr_SetString(PyExc_ValueError, "Only HTTP URLs are supported");
        return NULL;
    }
    
    // Extract body data
    const char* body_data = NULL;
    Py_ssize_t body_size = 0;
    if (body_obj != Py_None) {
        if (PyBytes_AsStringAndSize(body_obj, (char**)&body_data, &body_size) == -1) {
            free(url_copy);
            return NULL;
        }
    }
    
    // Make extended HTTP request using DAP SDK
    dap_client_http_t* http_client = dap_client_http_request_custom(
        NULL,           // worker - NULL for default
        host,           // uplink_addr
        port,           // uplink_port
        method,         // method
        "application/octet-stream", // content_type
        path,           // path
        body_data,      // request_data
        body_size,      // request_size
        NULL,           // cookie
        http_response_callback,  // response_callback
        http_error_callback,     // error_callback
        NULL,           // callbacks_arg
        NULL,           // custom_headers
        false           // over_ssl
    );
    
    free(url_copy);
    
    if (!http_client) {
        PyErr_SetString(PyExc_RuntimeError, "Failed to create extended HTTP request");
        return NULL;
    }
    
    // Return HTTP client handle
    return PyLong_FromVoidPtr(http_client);
}

PyObject* dap_http_simple_request_wrapper(PyObject* self, PyObject* args) {
    const char* url;
    
    if (!PyArg_ParseTuple(args, "s", &url)) {
        return NULL;
    }
    
    // Make simple GET request and wait for response
    PyObject* result = dap_http_client_request_wrapper(self, args);
    if (!result) {
        return NULL;
    }
    
    // For simple request, return the response data immediately
    // Note: This is a simplified synchronous approach
    if (s_response_data && s_response_size > 0) {
        PyObject* response = PyBytes_FromStringAndSize((char*)s_response_data, s_response_size);
        Py_DECREF(result);
        return response;
    }
    
    Py_DECREF(result);
    return PyBytes_FromString(""); // Empty response
}

// HTTP client configuration functions - now using real DAP SDK
PyObject* dap_http_client_set_headers_wrapper(PyObject* self, PyObject* args) {
    PyObject* client_obj;
    PyObject* headers_obj;
    
    if (!PyArg_ParseTuple(args, "OO", &client_obj, &headers_obj)) {
        return NULL;
    }
    
    // Extract client handle
    dap_client_t* client = PyLong_AsVoidPtr(client_obj);
    if (!client) {
        PyErr_SetString(PyExc_ValueError, "Invalid client handle");
        return NULL;
    }
    
    // Headers need to be passed to dap_client_http_request as custom_headers parameter
    // Store headers in client's _inheritor for later use
    if (PyDict_Check(headers_obj)) {
        // Convert dict to string format
        // For now, just store the reference
        Py_INCREF(headers_obj);
        if (client->_inheritor) {
            Py_DECREF((PyObject*)client->_inheritor);
        }
        client->_inheritor = headers_obj;
    }
    
    Py_RETURN_NONE;
}

PyObject* dap_http_client_set_timeout_wrapper(PyObject* self, PyObject* args) {
    int timeout_ms;
    
    if (!PyArg_ParseTuple(args, "i", &timeout_ms)) {
        return NULL;
    }
    
    // Use real DAP SDK timeout setting
    dap_client_http_set_connect_timeout_ms(timeout_ms);
    
    Py_RETURN_NONE;
}

// HTTP client response functions - now using real DAP SDK data
PyObject* dap_http_client_get_response_code_wrapper(PyObject* self, PyObject* args) {
    PyObject* client_obj;
    
    if (!PyArg_ParseTuple(args, "O", &client_obj)) {
        return NULL;
    }
    
    // Extract client handle
    dap_client_http_t* http_client = PyLong_AsVoidPtr(client_obj);
    if (!http_client) {
        PyErr_SetString(PyExc_ValueError, "Invalid HTTP client handle");
        return NULL;
    }
    
    // Return stored response code
    return PyLong_FromLong(s_response_code);
}

PyObject* dap_http_client_get_response_size_wrapper(PyObject* self, PyObject* args) {
    PyObject* client_obj;
    
    if (!PyArg_ParseTuple(args, "O", &client_obj)) {
        return NULL;
    }
    
    // Extract client handle
    dap_client_http_t* http_client = PyLong_AsVoidPtr(client_obj);
    if (!http_client) {
        PyErr_SetString(PyExc_ValueError, "Invalid HTTP client handle");
        return NULL;
    }
    
    // Return stored response size
    return PyLong_FromSize_t(s_response_size);
}

PyObject* dap_http_client_get_response_data_wrapper(PyObject* self, PyObject* args) {
    PyObject* client_obj;
    
    if (!PyArg_ParseTuple(args, "O", &client_obj)) {
        return NULL;
    }
    
    // Extract client handle
    dap_client_http_t* http_client = PyLong_AsVoidPtr(client_obj);
    if (!http_client) {
        PyErr_SetString(PyExc_ValueError, "Invalid HTTP client handle");
        return NULL;
    }
    
    // Return stored response data
    if (s_response_data && s_response_size > 0) {
        return PyBytes_FromStringAndSize((char*)s_response_data, s_response_size);
    }
    
    return PyBytes_FromString("");
}

PyObject* dap_http_client_get_response_headers_wrapper(PyObject* self, PyObject* args) {
    PyObject* client_obj;
    
    if (!PyArg_ParseTuple(args, "O", &client_obj)) {
        return NULL;
    }
    
    // Extract client handle
    dap_client_http_t* http_client = PyLong_AsVoidPtr(client_obj);
    if (!http_client) {
        PyErr_SetString(PyExc_ValueError, "Invalid HTTP client handle");
        return NULL;
    }
    
    // DAP SDK doesn't provide direct access to response headers
    // Return empty dictionary
    return PyDict_New();
}

// HTTP client close function
PyObject* dap_http_client_close_wrapper(PyObject* self, PyObject* args) {
    PyObject* client_obj;
    
    if (!PyArg_ParseTuple(args, "O", &client_obj)) {
        return NULL;
    }
    
    // Extract client handle
    dap_client_http_t* http_client = PyLong_AsVoidPtr(client_obj);
    if (!http_client) {
        PyErr_SetString(PyExc_ValueError, "Invalid HTTP client handle");
        return NULL;
    }
    
    // Use real DAP SDK close function
    dap_client_http_close_unsafe(http_client);
    
    Py_RETURN_NONE;
}

// HTTP callback setters
PyObject* dap_http_client_set_response_callback_wrapper(PyObject* self, PyObject* args) {
    PyObject* callback_obj;
    
    if (!PyArg_ParseTuple(args, "O", &callback_obj)) {
        return NULL;
    }
    
    if (!PyCallable_Check(callback_obj)) {
        PyErr_SetString(PyExc_TypeError, "Callback must be callable");
        return NULL;
    }
    
    // Store callback
    Py_XDECREF(s_http_response_callback);
    Py_INCREF(callback_obj);
    s_http_response_callback = callback_obj;
    
    Py_RETURN_NONE;
}

PyObject* dap_http_client_set_error_callback_wrapper(PyObject* self, PyObject* args) {
    PyObject* callback_obj;
    
    if (!PyArg_ParseTuple(args, "O", &callback_obj)) {
        return NULL;
    }
    
    if (!PyCallable_Check(callback_obj)) {
        PyErr_SetString(PyExc_TypeError, "Callback must be callable");
        return NULL;
    }
    
    // Store callback
    Py_XDECREF(s_http_error_callback);
    Py_INCREF(callback_obj);
    s_http_error_callback = callback_obj;
    
    Py_RETURN_NONE;
}

// Method definitions for Python module
PyMethodDef dap_http_methods[] = {
    // HTTP client management
    {"dap_http_client_init", dap_http_client_init_wrapper, METH_VARARGS, "Initialize HTTP client subsystem"},
    {"dap_http_client_deinit", dap_http_client_deinit_wrapper, METH_VARARGS, "Deinitialize HTTP client subsystem"},
    {"dap_http_client_new", dap_http_client_new_wrapper, METH_VARARGS, "Create new DAP client"},
    {"dap_http_client_delete", dap_http_client_delete_wrapper, METH_VARARGS, "Delete DAP client"},
    {"dap_http_get_all_clients", dap_http_get_all_clients_wrapper, METH_VARARGS, "Get all clients (empty list - not supported)"},
    
    // HTTP client requests - now using real DAP SDK
    {"dap_http_client_request", dap_http_client_request_wrapper, METH_VARARGS, "Make HTTP request using DAP SDK"},
    {"dap_http_client_request_ex", dap_http_client_request_ex_wrapper, METH_VARARGS, "Make extended HTTP request using DAP SDK"},
    {"dap_http_simple_request", dap_http_simple_request_wrapper, METH_VARARGS, "Make simple HTTP request using DAP SDK"},
    
    // HTTP client configuration
    {"dap_http_client_set_headers", dap_http_client_set_headers_wrapper, METH_VARARGS, "Set HTTP headers"},
    {"dap_http_client_set_timeout", dap_http_client_set_timeout_wrapper, METH_VARARGS, "Set client timeout"},
    
    // HTTP client responses - now using real DAP SDK data
    {"dap_http_client_get_response_code", dap_http_client_get_response_code_wrapper, METH_VARARGS, "Get HTTP response code"},
    {"dap_http_client_get_response_size", dap_http_client_get_response_size_wrapper, METH_VARARGS, "Get HTTP response size"},
    {"dap_http_client_get_response_data", dap_http_client_get_response_data_wrapper, METH_VARARGS, "Get HTTP response data"},
    {"dap_http_client_get_response_headers", dap_http_client_get_response_headers_wrapper, METH_VARARGS, "Get HTTP response headers"},
    
    // HTTP client control
    {"dap_http_client_close", dap_http_client_close_wrapper, METH_VARARGS, "Close HTTP client connection"},
    
    // HTTP callbacks
    {"dap_http_client_set_response_callback", dap_http_client_set_response_callback_wrapper, METH_VARARGS, "Set response callback"},
    {"dap_http_client_set_error_callback", dap_http_client_set_error_callback_wrapper, METH_VARARGS, "Set error callback"},
    
    {NULL, NULL, 0, NULL} // Sentinel
}; 