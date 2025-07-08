#include "libdap-python.h"
#include "wrapping_dap_client_stage_status.h"

static PyMethodDef DapClientStageStatusMethods[] = {
        {"STAGE_STATUS_NONE", STAGE_STATUS_NONE_PY, METH_NOARGS, ""},
        // Enc init stage
        {"STAGE_STATUS_IN_PROGRESS", STAGE_STATUS_IN_PROGRESS_PY, METH_NOARGS | METH_STATIC, ""},
        {"STAGE_STATUS_COMPLETE", STAGE_STATUS_COMPLETE_PY, METH_NOARGS | METH_STATIC, ""},
        {"STAGE_STATUS_ERROR", STAGE_STATUS_ERROR_PY, METH_NOARGS | METH_STATIC, ""},
        {"STAGE_STATUS_DONE", STAGE_STATUS_DONE_PY, METH_NOARGS | METH_STATIC, ""},
        {}
};

PyTypeObject dapClientStageStatusObject_dapClientStageStatusType = DAP_PY_TYPE_OBJECT(
        "CellFrame.ClientStageStatus", sizeof(PyDapClientStageStatusObject),
        "Client stage status objects",
        .tp_methods = DapClientStageStatusMethods);

PyObject *STAGE_STATUS_NONE_PY(){
    PyDapClientStageStatusObject *obj_stage_status = (PyDapClientStageStatusObject*)_PyObject_New(
            &dapClientStageStatusObject_dapClientStageStatusType);
    obj_stage_status->stage_status = STAGE_STATUS_NONE;
    return (PyObject *)obj_stage_status;
}
// Enc init stage
PyObject *STAGE_STATUS_IN_PROGRESS_PY(){
    PyDapClientStageStatusObject *obj_stage_status = (PyDapClientStageStatusObject*)_PyObject_New(
            &dapClientStageStatusObject_dapClientStageStatusType);
    obj_stage_status->stage_status = STAGE_STATUS_IN_PROGRESS;
    return (PyObject *)obj_stage_status;
}
PyObject *STAGE_STATUS_COMPLETE_PY(){
    PyDapClientStageStatusObject *obj_stage_status = (PyDapClientStageStatusObject*)_PyObject_New(
            &dapClientStageStatusObject_dapClientStageStatusType);
    obj_stage_status->stage_status = STAGE_STATUS_COMPLETE;
    return (PyObject *)obj_stage_status;
}
PyObject *STAGE_STATUS_ERROR_PY(){
    PyDapClientStageStatusObject *obj_stage_status = (PyDapClientStageStatusObject*)_PyObject_New(
            &dapClientStageStatusObject_dapClientStageStatusType);
    obj_stage_status->stage_status = STAGE_STATUS_ERROR;
    return (PyObject *)obj_stage_status;
}
PyObject *STAGE_STATUS_DONE_PY(){
    PyDapClientStageStatusObject *obj_stage_status = (PyDapClientStageStatusObject*)_PyObject_New(
            &dapClientStageStatusObject_dapClientStageStatusType);
    obj_stage_status->stage_status = STAGE_STATUS_DONE;
    return (PyObject *)obj_stage_status;
}
