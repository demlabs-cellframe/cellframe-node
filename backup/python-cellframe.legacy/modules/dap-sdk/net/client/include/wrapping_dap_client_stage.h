#ifndef _WRAPPING_DAP_CLIENT_STAGE_
#define _WRAPPING_DAP_CLIENT_STAGE_
#include <Python.h>
#include "dap_client.h"

#ifdef __cplusplus
extern "C"{
#endif

typedef struct PyDapClientStage{
    PyObject_HEAD
    dap_client_stage_t stage;
}PyDapClientStageObject;

PyObject *STAGE_BEGIN_PY();
PyObject *STAGE_ENC_INIT_PY();
PyObject *STAGE_STREAM_CTL_PY();
PyObject *STAGE_STREAM_SESSION_PY();
PyObject *STAGE_STREAM_CONNECTED_PY();
PyObject *STAGE_STREAM_STREAMING_PY();
PyObject *STAGE_STREAM_ABORT_PY();

extern PyTypeObject dapClientStageObject_dapClientStageType;

#ifdef __cplusplus
}
#endif

#endif // _WRAPPING_DAP_CLIENT_STAGE_