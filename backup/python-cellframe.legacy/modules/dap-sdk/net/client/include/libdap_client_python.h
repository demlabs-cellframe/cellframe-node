#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include "dap_client.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct PyDapClient{
    PyObject_HEAD
    dap_client_t *client;
}PyDapClientObject;

int dap_client_init_py();
void dap_client_deinit_py();

//PyObject *dap_client_new_py(PyObject *)
PyObject *dap_client_delete_py(PyObject *self, PyObject *args);

PyObject *dao_client_set_uplink_py(PyObject *self, PyObject *args);
PyObject *dap_client_get_uplink_addr_py(PyObject *self, PyObject *args);
PyObject *dap_client_get_uplink_port_py(PyObject *self, PyObject *args);

PyObject *dap_client_get_key_stream_py(PyObject *self, PyObject *args);
PyObject *dap_client_go_stage_py(PyObject *self, PyObject *args);
PyObject *dap_client_reset_py(PyObject *self, PyObject *args);
PyObject *dap_client_request_enc_py(PyObject *self, PyObject *args);
PyObject *dap_client_request_py(PyObject *self, PyObject *args);
PyObject *dap_client_disconnect_py(PyObject *self, PyObject *args);

PyObject *dap_client_get_stage_str_py(PyObject *self, PyObject *args);
PyObject *dap_client_stage_str_py(PyObject *self, PyObject *args);

PyObject *dap_client_get_stage_status_str_py(PyObject *self, PyObject *args);
PyObject *dap_client_stage_status_str_py(PyObject *self, PyObject *args);
PyObject *dap_client_error_str_py(PyObject *self, PyObject *args);
PyObject *dap_client_get_error_str_py(PyObject *self, PyObject *args);

PyObject *dap_client_get_auth_cookie_py(PyObject *self, PyObject *args);
PyObject *dap_client_get_stream_py(PyObject *self, PyObject *args);
PyObject *dap_client_get_stream_ch_py(PyObject *self, PyObject *args);
PyObject *dap_client_get_stream_id_py(PyObject *self, PyObject *args);
PyObject *dap_client_set_active_channels_py(PyObject *self, PyObject *args);

PyObject *dap_client_get_stage_py(PyObject *self, PyObject *args);
PyObject *dap_client_get_stage_status_py(PyObject *self, PyObject *args);

extern PyTypeObject dapClientObject_dapClientType;

#ifdef __cplusplus
}
#endif

