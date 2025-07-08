#include "libdap-python.h"
#include "wrapping_dap_client_stage.h"

static PyMethodDef DapClientStageMethods[] = {
        {"STAGE_BEGIN", (PyCFunction)STAGE_BEGIN_PY, METH_NOARGS | METH_STATIC, ""},
        {"STAGE_ENC_INIT", (PyCFunction)STAGE_ENC_INIT_PY, METH_NOARGS | METH_STATIC, ""},
        {"STAGE_STREAM_CTL", (PyCFunction)STAGE_STREAM_CTL_PY, METH_NOARGS | METH_STATIC, ""},
        {"STAGE_STREAM_SESSION", (PyCFunction)STAGE_STREAM_SESSION_PY, METH_NOARGS | METH_STATIC, ""},
        {"STAGE_STREAM_CONNECTED", (PyCFunction)STAGE_STREAM_CONNECTED_PY, METH_NOARGS | METH_STATIC, ""},
        {"STAGE_STREAM_STREAMING", (PyCFunction)STAGE_STREAM_STREAMING_PY, METH_NOARGS | METH_STATIC, ""},
        {}
};

PyTypeObject dapClientStageObject_dapClientStageType = DAP_PY_TYPE_OBJECT(
        "CellFrame.ClientStage", sizeof(PyDapClientStageObject),
        "Client stage objects",
        .tp_methods = DapClientStageMethods);

PyObject *STAGE_BEGIN_PY(){
    PyDapClientStageObject *obj_stage = (PyDapClientStageObject*)_PyObject_New(&dapClientStageObject_dapClientStageType);
    obj_stage->stage = STAGE_BEGIN;
    return (PyObject *)obj_stage;
}
PyObject *STAGE_ENC_INIT_PY(){
    PyDapClientStageObject *obj_stage = (PyDapClientStageObject*)_PyObject_New(&dapClientStageObject_dapClientStageType);
    obj_stage->stage = STAGE_ENC_INIT;
    return (PyObject *)obj_stage;
}
PyObject *STAGE_STREAM_CTL_PY(){
    PyDapClientStageObject *obj_stage = (PyDapClientStageObject*)_PyObject_New(&dapClientStageObject_dapClientStageType);
    obj_stage->stage = STAGE_STREAM_CTL;
    return (PyObject *)obj_stage;
}
PyObject *STAGE_STREAM_SESSION_PY(){
    PyDapClientStageObject *obj_stage = (PyDapClientStageObject*)_PyObject_New(&dapClientStageObject_dapClientStageType);
    obj_stage->stage = STAGE_STREAM_SESSION;
    return (PyObject *)obj_stage;
}
PyObject *STAGE_STREAM_CONNECTED_PY(){
    PyDapClientStageObject *obj_stage = (PyDapClientStageObject*)_PyObject_New(&dapClientStageObject_dapClientStageType);
    obj_stage->stage = STAGE_STREAM_CONNECTED;
    return (PyObject *)obj_stage;
}
PyObject *STAGE_STREAM_STREAMING_PY(){
    PyDapClientStageObject *obj_stage = (PyDapClientStageObject*)_PyObject_New(&dapClientStageObject_dapClientStageType);
    obj_stage->stage = STAGE_STREAM_STREAMING;
    return (PyObject *)obj_stage;
}
