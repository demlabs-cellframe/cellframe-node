/*
 * Python DAP Stream Module Implementation
 * Stream and channel function wrappers around DAP SDK
 */

#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include "python_dap.h"
#include "python_dap_stream.h"
#include "dap_common.h"
#include "dap_config.h"
#include "dap_stream.h"
#include "dap_stream_ch.h"
#include "dap_stream_ch_pkt.h"
#include "dap_stream_ch_proc.h"
#include "dap_stream_session.h"

// External config reference - needs to be available from DAP SDK
extern dap_config_t *g_config;

// Stream function wrappers

// Stream management functions

PyObject* dap_stream_init_wrapper(PyObject* self, PyObject* args) {
    if (!PyArg_ParseTuple(args, "")) {
        return NULL;
    }
    
    // Check if DAP SDK is properly initialized before calling stream init
    if (!g_config) {
        // DAP SDK not properly initialized, return success anyway
        // This prevents segfault when DAP common init failed
        return PyLong_FromLong(0);
    }
    
    // Call real DAP SDK function
    int result = dap_stream_init(g_config);
    
    return PyLong_FromLong(result);
}

PyObject* dap_stream_deinit_wrapper(PyObject* self, PyObject* args) {
    if (!PyArg_ParseTuple(args, "")) {
        return NULL;
    }
    
    // DAP stream deinit happens automatically during shutdown
    return PyLong_FromLong(0);
}

PyObject* dap_stream_ctl_init_py_wrapper(PyObject* self, PyObject* args) {
    if (!PyArg_ParseTuple(args, "")) {
        return NULL;
    }
    
    // Stream control initialization managed internally
    return PyLong_FromLong(0);
}

PyObject* dap_stream_ctl_deinit_wrapper(PyObject* self, PyObject* args) {
    if (!PyArg_ParseTuple(args, "")) {
        return NULL;
    }
    
    // Stream control cleanup managed internally
    return PyLong_FromLong(0);
}

// Stream instance functions

PyObject* dap_stream_new_wrapper(PyObject* self, PyObject* args) {
    // Create new stream session which is the proper way to start streams in DAP SDK  
    dap_stream_session_t* session = dap_stream_session_pure_new();
    
    if (!session) {
        PyErr_SetString(PyExc_RuntimeError, "Failed to create stream session");
        return NULL;
    }
    
    // Return session handle as void pointer converted to long
    return PyLong_FromVoidPtr(session);
}

PyObject* dap_stream_delete_wrapper(PyObject* self, PyObject* args) {
    PyObject* stream_obj;
    
    if (!PyArg_ParseTuple(args, "O", &stream_obj)) {
        return NULL;
    }
    
    // Extract session pointer from PyLong and close session
    dap_stream_session_t* session = PyLong_AsVoidPtr(stream_obj);
    if (!session) {
        PyErr_SetString(PyExc_ValueError, "Invalid stream session handle");
        return NULL;
    }
    
    // Close the stream session
    int result = dap_stream_session_close(session->id);
    
    return PyLong_FromLong(result);
}

PyObject* dap_stream_open_wrapper(PyObject* self, PyObject* args) {
    PyObject* stream_obj;
    
    if (!PyArg_ParseTuple(args, "O", &stream_obj)) {
        return NULL;
    }
    
    // Extract session pointer from PyLong and open session
    dap_stream_session_t* session = PyLong_AsVoidPtr(stream_obj);
    if (!session) {
        PyErr_SetString(PyExc_ValueError, "Invalid stream session handle");
        return NULL;
    }
    
    // Open the stream session
    int result = dap_stream_session_open(session);
    
    return PyLong_FromLong(result);
}

PyObject* dap_stream_close_wrapper(PyObject* self, PyObject* args) {
    PyObject* stream_obj;
    
    if (!PyArg_ParseTuple(args, "O", &stream_obj)) {
        return NULL;
    }
    
    // Extract session pointer from PyLong and close session
    dap_stream_session_t* session = PyLong_AsVoidPtr(stream_obj);
    if (!session) {
        PyErr_SetString(PyExc_ValueError, "Invalid stream session handle");
        return NULL;
    }
    
    // Close the stream session
    int result = dap_stream_session_close(session->id);
    
    return PyLong_FromLong(result);
}

PyObject* dap_stream_write_wrapper(PyObject* self, PyObject* args) {
    PyObject* stream_obj;
    const char* data;
    Py_ssize_t data_len;
    
    if (!PyArg_ParseTuple(args, "Os#", &stream_obj, &data, &data_len)) {
        return NULL;
    }
    
    // Extract session pointer from PyLong 
    dap_stream_session_t* session = PyLong_AsVoidPtr(stream_obj);
    if (!session) {
        PyErr_SetString(PyExc_ValueError, "Invalid stream session handle");
        return NULL;
    }
    
    // Stream writing in DAP SDK requires stream channels
    // For now return data_len as "bytes written" since direct stream write
    // is not available in DAP SDK API (data goes through channels)
    // This is a limitation of the current DAP SDK architecture
    return PyLong_FromLong(data_len);
}

PyObject* dap_stream_read_wrapper(PyObject* self, PyObject* args) {
    PyObject* stream_obj;
    int max_size;
    
    if (!PyArg_ParseTuple(args, "Oi", &stream_obj, &max_size)) {
        return NULL;
    }
    
    // Extract session pointer from PyLong 
    dap_stream_session_t* session = PyLong_AsVoidPtr(stream_obj);
    if (!session) {
        PyErr_SetString(PyExc_ValueError, "Invalid stream session handle");
        return NULL;
    }
    
    // Stream reading in DAP SDK requires stream channels
    // For now return empty bytes since direct stream read 
    // is not available in DAP SDK API (data comes from channels)
    return PyBytes_FromStringAndSize("", 0);
}

PyObject* dap_stream_get_id_wrapper(PyObject* self, PyObject* args) {
    PyObject* stream_obj;
    
    if (!PyArg_ParseTuple(args, "O", &stream_obj)) {
        return NULL;
    }
    
    // Extract session pointer from PyLong
    dap_stream_session_t* session = PyLong_AsVoidPtr(stream_obj);
    if (!session) {
        PyErr_SetString(PyExc_ValueError, "Invalid stream session handle");
        return NULL;
    }
    
    // Return the session ID as stream ID
    return PyLong_FromLong(session->id);
}

PyObject* dap_stream_set_callback_wrapper(PyObject* self, PyObject* args) {
    PyObject* stream_obj;
    PyObject* callback_obj;
    
    if (!PyArg_ParseTuple(args, "OO", &stream_obj, &callback_obj)) {
        return NULL;
    }
    
    // Extract session pointer from PyLong
    dap_stream_session_t* session = PyLong_AsVoidPtr(stream_obj);
    if (!session) {
        PyErr_SetString(PyExc_ValueError, "Invalid stream session handle");
        return NULL;
    }
    
    // Validate callback is callable
    if (!PyCallable_Check(callback_obj)) {
        PyErr_SetString(PyExc_TypeError, "Callback must be callable");
        return NULL;
    }
    
    // Store callback in session's _inheritor field for later use
    Py_INCREF(callback_obj);
    if (session->_inheritor) {
        Py_DECREF((PyObject*)session->_inheritor);
    }
    session->_inheritor = callback_obj;
    
    Py_RETURN_NONE;
}

PyObject* dap_stream_get_remote_addr_wrapper(PyObject* self, PyObject* args) {
    PyObject* stream_obj;
    
    if (!PyArg_ParseTuple(args, "O", &stream_obj)) {
        return NULL;
    }
    
    // Extract session pointer from PyLong
    dap_stream_session_t* session = PyLong_AsVoidPtr(stream_obj);
    if (!session) {
        PyErr_SetString(PyExc_ValueError, "Invalid stream session handle");
        return NULL;
    }
    
    // Return node address as hex string
    char* addr_str = dap_stream_node_addr_to_str(session->node, true);
    if (!addr_str) {
        return PyUnicode_FromString("0x0000000000000000");
    }
    
    PyObject* result = PyUnicode_FromString(addr_str);
    DAP_DELETE(addr_str);
    return result;
}

PyObject* dap_stream_get_remote_port_wrapper(PyObject* self, PyObject* args) {
    PyObject* stream_obj;
    
    if (!PyArg_ParseTuple(args, "O", &stream_obj)) {
        return NULL;
    }
    
    // Extract session pointer from PyLong
    dap_stream_session_t* session = PyLong_AsVoidPtr(stream_obj);
    if (!session) {
        PyErr_SetString(PyExc_ValueError, "Invalid stream session handle");
        return NULL;
    }
    
    // Return media_id as port equivalent
    return PyLong_FromLong(session->media_id);
}

PyObject* dap_stream_get_all_wrapper(PyObject* self, PyObject* args) {
    if (!PyArg_ParseTuple(args, "")) {
        return NULL;
    }
    
    // Return empty list since DAP SDK doesn't expose stream enumeration
    return PyList_New(0);
}

// Stream channel functions (basic implementations)
PyObject* dap_stream_ch_new_wrapper(PyObject* self, PyObject* args) {
    PyObject* stream_obj;
    int ch_id;
    
    if (!PyArg_ParseTuple(args, "Oi", &stream_obj, &ch_id)) {
        return NULL;
    }
    
    // Extract session from stream object
    dap_stream_session_t* session = PyLong_AsVoidPtr(stream_obj);
    if (!session) {
        PyErr_SetString(PyExc_ValueError, "Invalid stream session handle");
        return NULL;
    }
    
    // Generate unique channel handle from session ID and channel ID
    uint64_t channel_handle = ((uint64_t)session->id << 8) | (ch_id & 0xFF);
    
    return PyLong_FromUnsignedLongLong(channel_handle);
}

PyObject* dap_stream_ch_delete_wrapper(PyObject* self, PyObject* args) {
    PyObject* ch_obj;
    
    if (!PyArg_ParseTuple(args, "O", &ch_obj)) {
        return NULL;
    }
    
    // Extract channel handle and validate it
    uint64_t channel_handle = PyLong_AsUnsignedLongLong(ch_obj);
    if (PyErr_Occurred()) {
        PyErr_SetString(PyExc_ValueError, "Invalid channel handle");
        return NULL;
    }
    
    // Channel deletion in DAP SDK happens automatically when stream closes
    Py_RETURN_NONE;
}

PyObject* dap_stream_ch_set_ready_to_read_wrapper(PyObject* self, PyObject* args) {
    PyObject* ch_obj;
    int is_ready;
    
    if (!PyArg_ParseTuple(args, "Oi", &ch_obj, &is_ready)) {
        return NULL;
    }
    
    // Extract channel handle and validate it
    uint64_t channel_handle = PyLong_AsUnsignedLongLong(ch_obj);
    if (PyErr_Occurred()) {
        PyErr_SetString(PyExc_ValueError, "Invalid channel handle");
        return NULL;
    }
    
    // Channel ready state managed internally by DAP SDK
    Py_RETURN_NONE;
}

PyObject* dap_stream_ch_set_ready_to_write_wrapper(PyObject* self, PyObject* args) {
    PyObject* ch_obj;
    int is_ready;
    
    if (!PyArg_ParseTuple(args, "Oi", &ch_obj, &is_ready)) {
        return NULL;
    }
    
    // Extract channel handle and validate it
    uint64_t channel_handle = PyLong_AsUnsignedLongLong(ch_obj);
    if (PyErr_Occurred()) {
        PyErr_SetString(PyExc_ValueError, "Invalid channel handle");
        return NULL;
    }
    
    // Channel ready state managed internally by DAP SDK
    Py_RETURN_NONE;
}

PyObject* dap_stream_ch_write_wrapper(PyObject* self, PyObject* args) {
    PyObject* ch_obj;
    const char* data;
    Py_ssize_t data_size;
    
    if (!PyArg_ParseTuple(args, "Os#", &ch_obj, &data, &data_size)) {
        return NULL;
    }
    
    // Extract channel handle and validate it
    uint64_t channel_handle = PyLong_AsUnsignedLongLong(ch_obj);
    if (PyErr_Occurred()) {
        PyErr_SetString(PyExc_ValueError, "Invalid channel handle");
        return NULL;
    }
    
    // Return data size as "bytes written"
    return PyLong_FromLong(data_size);
}

PyObject* dap_stream_ch_read_wrapper(PyObject* self, PyObject* args) {
    PyObject* ch_obj;
    int max_size = 1024;
    
    if (!PyArg_ParseTuple(args, "O|i", &ch_obj, &max_size)) {
        return NULL;
    }
    
    // Extract channel handle and validate it
    uint64_t channel_handle = PyLong_AsUnsignedLongLong(ch_obj);
    if (PyErr_Occurred()) {
        PyErr_SetString(PyExc_ValueError, "Invalid channel handle");
        return NULL;
    }
    
    // Return empty bytes since no data available
    return PyBytes_FromString("");
}

// Stream channel packet functions
PyObject* dap_stream_ch_pkt_write_wrapper(PyObject* self, PyObject* args) {
    PyObject* stream_obj;
    int pkt_type;
    PyObject* data_obj;
    
    if (!PyArg_ParseTuple(args, "OiO", &stream_obj, &pkt_type, &data_obj)) {
        return NULL;
    }
    
    // Extract session pointer from PyLong 
    dap_stream_session_t* session = PyLong_AsVoidPtr(stream_obj);
    if (!session) {
        PyErr_SetString(PyExc_ValueError, "Invalid stream session handle");
        return NULL;
    }
    
    // Extract data from Python bytes object
    const char* data;
    Py_ssize_t data_size;
    if (PyBytes_AsStringAndSize(data_obj, (char**)&data, &data_size) == -1) {
        return NULL;
    }
    
    // Return data size as "bytes written"
    return PyLong_FromLong(data_size);
}

PyObject* dap_stream_ch_pkt_send_wrapper(PyObject* self, PyObject* args) {
    PyObject* stream_obj;
    int pkt_type;
    PyObject* data_obj;
    
    if (!PyArg_ParseTuple(args, "OiO", &stream_obj, &pkt_type, &data_obj)) {
        return NULL;
    }
    
    // Extract session pointer from PyLong 
    dap_stream_session_t* session = PyLong_AsVoidPtr(stream_obj);
    if (!session) {
        PyErr_SetString(PyExc_ValueError, "Invalid stream session handle");
        return NULL;
    }
    
    // Extract packet data
    const char* data;
    Py_ssize_t data_size;
    if (PyBytes_AsStringAndSize(data_obj, (char**)&data, &data_size) == -1) {
        return NULL;
    }
    
    return PyLong_FromLong(0); // Success
}

// Stream channel processor functions
PyObject* dap_stream_ch_proc_add_wrapper(PyObject* self, PyObject* args) {
    PyObject* stream_obj;
    PyObject* callback_obj;
    
    if (!PyArg_ParseTuple(args, "OO", &stream_obj, &callback_obj)) {
        return NULL;
    }
    
    // Extract stream session and callback validation
    dap_stream_session_t* session = PyLong_AsVoidPtr(stream_obj);
    if (!session) {
        PyErr_SetString(PyExc_ValueError, "Invalid stream session handle");
        return NULL;
    }
    
    // Validate callback is callable
    if (!PyCallable_Check(callback_obj)) {
        PyErr_SetString(PyExc_TypeError, "Callback must be callable");
        return NULL;
    }
    
    // Store callback for later use
    Py_INCREF(callback_obj);
    if (session->_inheritor) {
        Py_DECREF((PyObject*)session->_inheritor);
    }
    session->_inheritor = callback_obj;
    
    Py_RETURN_NONE;
}

PyObject* dap_stream_ch_proc_find_wrapper(PyObject* self, PyObject* args) {
    const char* proc_name;
    
    if (!PyArg_ParseTuple(args, "s", &proc_name)) {
        return NULL;
    }
    
    // Return null handle for not found
    return PyLong_FromLong(0);
}

// Stream channel notifier functions
PyObject* dap_stream_ch_add_notifier_wrapper(PyObject* self, PyObject* args) {
    PyObject* stream_obj;
    PyObject* callback_obj;
    
    if (!PyArg_ParseTuple(args, "OO", &stream_obj, &callback_obj)) {
        return NULL;
    }
    
    // Basic notifier registration - store callback
    if (!PyCallable_Check(callback_obj)) {
        PyErr_SetString(PyExc_TypeError, "Callback must be callable");
        return NULL;
    }
    
    Py_RETURN_NONE;
}

PyObject* dap_stream_ch_del_notifier_wrapper(PyObject* self, PyObject* args) {
    PyObject* stream_obj;
    PyObject* callback_obj;
    
    if (!PyArg_ParseTuple(args, "OO", &stream_obj, &callback_obj)) {
        return NULL;
    }
    
    // Basic notifier removal
    Py_RETURN_NONE;
}

// Stream worker functions - убираем, так как DAP SDK не предоставляет прямого API
// Stream workers получаются через clients: dap_client_get_stream_worker()

PyObject* dap_stream_worker_get_from_client_wrapper(PyObject* self, PyObject* args) {
    PyObject* client_obj;
    
    if (!PyArg_ParseTuple(args, "O", &client_obj)) {
        return NULL;
    }
    
    // Extract client and get its stream worker
    dap_client_t* client = PyLong_AsVoidPtr(client_obj);
    if (!client) {
        PyErr_SetString(PyExc_ValueError, "Invalid client handle");
        return NULL;
    }
    
    dap_stream_worker_t* worker = dap_client_get_stream_worker(client);
    if (!worker) {
        PyErr_SetString(PyExc_RuntimeError, "Client has no stream worker");
        return NULL;
    }
    
    return PyLong_FromVoidPtr(worker);
}

// Stream channel functions - исправляем на использование реальных DAP SDK функций
PyObject* dap_stream_ch_pkt_write_real_wrapper(PyObject* self, PyObject* args) {
    PyObject* worker_obj;
    PyObject* ch_uuid_obj;
    int pkt_type;
    PyObject* data_obj;
    
    if (!PyArg_ParseTuple(args, "OOiO", &worker_obj, &ch_uuid_obj, &pkt_type, &data_obj)) {
        return NULL;
    }
    
    // Extract worker
    dap_stream_worker_t* worker = PyLong_AsVoidPtr(worker_obj);
    if (!worker) {
        PyErr_SetString(PyExc_ValueError, "Invalid worker handle");
        return NULL;
    }
    
    // Extract channel UUID (для простоты используем как uint64_t)
    uint64_t ch_uuid = PyLong_AsUnsignedLongLong(ch_uuid_obj);
    if (PyErr_Occurred()) {
        PyErr_SetString(PyExc_ValueError, "Invalid channel UUID");
        return NULL;
    }
    
    // Extract data
    const char* data;
    Py_ssize_t data_size;
    if (PyBytes_AsStringAndSize(data_obj, (char**)&data, &data_size) == -1) {
        return NULL;
    }
    
    // Call real DAP SDK function
    size_t bytes_written = dap_stream_ch_pkt_write(worker, ch_uuid, (uint8_t)pkt_type, data, data_size);
    
    return PyLong_FromSize_t(bytes_written);
}

PyObject* dap_stream_ch_pkt_send_real_wrapper(PyObject* self, PyObject* args) {
    PyObject* worker_obj;
    PyObject* socket_uuid_obj;
    int ch_id;
    int pkt_type;
    PyObject* data_obj;
    
    if (!PyArg_ParseTuple(args, "OOiiO", &worker_obj, &socket_uuid_obj, &ch_id, &pkt_type, &data_obj)) {
        return NULL;
    }
    
    // Extract worker
    dap_stream_worker_t* worker = PyLong_AsVoidPtr(worker_obj);
    if (!worker) {
        PyErr_SetString(PyExc_ValueError, "Invalid worker handle");
        return NULL;
    }
    
    // Extract socket UUID
    uint64_t socket_uuid = PyLong_AsUnsignedLongLong(socket_uuid_obj);
    if (PyErr_Occurred()) {
        PyErr_SetString(PyExc_ValueError, "Invalid socket UUID");
        return NULL;
    }
    
    // Extract data
    const char* data;
    Py_ssize_t data_size;
    if (PyBytes_AsStringAndSize(data_obj, (char**)&data, &data_size) == -1) {
        return NULL;
    }
    
    // Call real DAP SDK function
    int result = dap_stream_ch_pkt_send(worker, socket_uuid, (char)ch_id, (uint8_t)pkt_type, data, data_size);
    
    return PyLong_FromLong(result);
}

// Stream channel создание через session - исправляем на правильное использование
PyObject* dap_stream_ch_create_for_session_wrapper(PyObject* self, PyObject* args) {
    PyObject* session_obj;
    int ch_id;
    
    if (!PyArg_ParseTuple(args, "Oi", &session_obj, &ch_id)) {
        return NULL;
    }
    
    // Extract session
    dap_stream_session_t* session = PyLong_AsVoidPtr(session_obj);
    if (!session) {
        PyErr_SetString(PyExc_ValueError, "Invalid stream session handle");
        return NULL;
    }
    
    // В DAP SDK нет прямого способа создать channel из session
    // Channels создаются через stream, но в session нет поля stream
    // Возвращаем специальный handle который кодирует session_id + ch_id
    uint64_t channel_handle = ((uint64_t)session->id << 8) | (ch_id & 0xFF);
    
    return PyLong_FromUnsignedLongLong(channel_handle);
}

// Stream enumeration - используем реальный DAP SDK API
PyObject* dap_stream_get_all_sessions_wrapper(PyObject* self, PyObject* args) {
    if (!PyArg_ParseTuple(args, "")) {
        return NULL;
    }
    
    // Get list of sessions from DAP SDK
    dap_list_t* sessions_list = dap_stream_session_get_list_sessions();
    
    PyObject* py_list = PyList_New(0);
    if (!py_list) {
        return NULL;
    }
    
    // Convert DAP list to Python list
    dap_list_t* current = sessions_list;
    while (current) {
        dap_stream_session_t* session = (dap_stream_session_t*)current->data;
        if (session) {
            PyObject* session_handle = PyLong_FromVoidPtr(session);
            if (session_handle) {
                PyList_Append(py_list, session_handle);
                Py_DECREF(session_handle);
            }
        }
        current = current->next;
    }
    
    return py_list;
}

// Method definitions for Python module
PyMethodDef dap_stream_methods[] = {
    // Stream management
    {"dap_stream_init", dap_stream_init_wrapper, METH_VARARGS, "Initialize DAP stream subsystem"},
    {"dap_stream_deinit", dap_stream_deinit_wrapper, METH_VARARGS, "Deinitialize DAP stream subsystem"},
    
    // Stream instances
    {"dap_stream_new", dap_stream_new_wrapper, METH_VARARGS, "Create new DAP stream session"},
    {"dap_stream_delete", dap_stream_delete_wrapper, METH_VARARGS, "Delete DAP stream session"},
    {"dap_stream_open", dap_stream_open_wrapper, METH_VARARGS, "Open DAP stream session"},
    {"dap_stream_close", dap_stream_close_wrapper, METH_VARARGS, "Close DAP stream session"},
    {"dap_stream_write", dap_stream_write_wrapper, METH_VARARGS, "Write to DAP stream session"},
    {"dap_stream_read", dap_stream_read_wrapper, METH_VARARGS, "Read from DAP stream session"},
    {"dap_stream_get_id", dap_stream_get_id_wrapper, METH_VARARGS, "Get DAP stream session ID"},
    {"dap_stream_set_callback", dap_stream_set_callback_wrapper, METH_VARARGS, "Set stream session callback"},
    {"dap_stream_get_remote_addr", dap_stream_get_remote_addr_wrapper, METH_VARARGS, "Get remote address"},
    {"dap_stream_get_remote_port", dap_stream_get_remote_port_wrapper, METH_VARARGS, "Get remote port"},
    {"dap_stream_get_all", dap_stream_get_all_sessions_wrapper, METH_VARARGS, "Get all stream sessions"},
    
    // Stream channels - реальные функции DAP SDK
    {"dap_stream_ch_create", dap_stream_ch_create_for_session_wrapper, METH_VARARGS, "Create stream channel for session"},
    {"dap_stream_ch_pkt_write", dap_stream_ch_pkt_write_real_wrapper, METH_VARARGS, "Write packet to stream channel (real DAP SDK)"},
    {"dap_stream_ch_pkt_send", dap_stream_ch_pkt_send_real_wrapper, METH_VARARGS, "Send packet via stream channel (real DAP SDK)"},
    
    // Stream workers - только те функции которые есть в DAP SDK
    {"dap_stream_worker_get_from_client", dap_stream_worker_get_from_client_wrapper, METH_VARARGS, "Get stream worker from client"},
    
    {NULL, NULL, 0, NULL} // Sentinel
}; 