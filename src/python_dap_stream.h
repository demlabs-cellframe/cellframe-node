/*
 * Python DAP Stream Module Header
 * Stream and channel function wrappers around DAP SDK
 */

#ifndef PYTHON_DAP_STREAM_H
#define PYTHON_DAP_STREAM_H

#define PY_SSIZE_T_CLEAN
#include <Python.h>

// Stream management functions
PyObject* dap_stream_init_wrapper(PyObject* self, PyObject* args);
PyObject* dap_stream_deinit_wrapper(PyObject* self, PyObject* args);

// Stream instance functions  
PyObject* dap_stream_new_wrapper(PyObject* self, PyObject* args);
PyObject* dap_stream_delete_wrapper(PyObject* self, PyObject* args);
PyObject* dap_stream_open_wrapper(PyObject* self, PyObject* args);
PyObject* dap_stream_close_wrapper(PyObject* self, PyObject* args);
PyObject* dap_stream_write_wrapper(PyObject* self, PyObject* args);
PyObject* dap_stream_read_wrapper(PyObject* self, PyObject* args);
PyObject* dap_stream_get_id_wrapper(PyObject* self, PyObject* args);
PyObject* dap_stream_set_callback_wrapper(PyObject* self, PyObject* args);
PyObject* dap_stream_get_remote_addr_wrapper(PyObject* self, PyObject* args);
PyObject* dap_stream_get_remote_port_wrapper(PyObject* self, PyObject* args);
PyObject* dap_stream_get_all_wrapper(PyObject* self, PyObject* args);

// Stream channel functions
PyObject* dap_stream_ch_new_wrapper(PyObject* self, PyObject* args);
PyObject* dap_stream_ch_delete_wrapper(PyObject* self, PyObject* args);
PyObject* dap_stream_ch_set_ready_to_read_wrapper(PyObject* self, PyObject* args);
PyObject* dap_stream_ch_set_ready_to_write_wrapper(PyObject* self, PyObject* args);
PyObject* dap_stream_ch_write_wrapper(PyObject* self, PyObject* args);
PyObject* dap_stream_ch_read_wrapper(PyObject* self, PyObject* args);

// Stream channel packet functions
PyObject* dap_stream_ch_pkt_write_wrapper(PyObject* self, PyObject* args);
PyObject* dap_stream_ch_pkt_send_wrapper(PyObject* self, PyObject* args);

// Stream channel processor functions
PyObject* dap_stream_ch_proc_add_wrapper(PyObject* self, PyObject* args);
PyObject* dap_stream_ch_proc_find_wrapper(PyObject* self, PyObject* args);

// Stream channel notifier functions
PyObject* dap_stream_ch_add_notifier_wrapper(PyObject* self, PyObject* args);
PyObject* dap_stream_ch_del_notifier_wrapper(PyObject* self, PyObject* args);

// Stream worker functions
PyObject* dap_stream_worker_new_wrapper(PyObject* self, PyObject* args);
PyObject* dap_stream_worker_delete_wrapper(PyObject* self, PyObject* args);
PyObject* dap_stream_worker_add_stream_wrapper(PyObject* self, PyObject* args);
PyObject* dap_stream_worker_remove_stream_wrapper(PyObject* self, PyObject* args);
PyObject* dap_stream_worker_get_count_wrapper(PyObject* self, PyObject* args);
PyObject* dap_stream_worker_get_stats_wrapper(PyObject* self, PyObject* args);

// Method definitions array for Python module
extern PyMethodDef dap_stream_methods[];

#endif // PYTHON_DAP_STREAM_H 