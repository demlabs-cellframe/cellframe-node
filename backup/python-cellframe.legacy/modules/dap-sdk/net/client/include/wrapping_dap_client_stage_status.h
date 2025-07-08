#ifndef _WRAPPING_DAP_CLIENT_STAGE_STATUS_
#define _WRAPPING_DAP_CLIENT_STAGE_STATUS_

#include <Python.h>
#include "dap_client.h"

#ifdef __cplusplus
extern "C"{
#endif

typedef struct PyDapClientStageStatus{
    PyObject_HEAD
    dap_client_stage_status_t stage_status;
}PyDapClientStageStatusObject;

PyObject *STAGE_STATUS_NONE_PY();
// Enc init stage
PyObject *STAGE_STATUS_IN_PROGRESS_PY();
PyObject *STAGE_STATUS_COMPLETE_PY();
PyObject *STAGE_STATUS_ERROR_PY();
PyObject *STAGE_STATUS_DONE_PY();

extern PyTypeObject dapClientStageStatusObject_dapClientStageStatusType;

#ifdef  __cplusplus
}
#endif

#endif //_WRAPPING_DAP_CLIENT_STAGE_STATUS_
