#include "libdap-python.h"
#include "dap_events_python.h"

static void PyDapEventsObject_dealloc(PyDapEventsObject *eventsObject);
static PyObject *dap_events_socket_remove_and_delete_py(PyDapEventsObject *self, PyObject *args);
static PyObject *dap_events_socket_kill_socket_py(PyDapEventsObject *self, PyObject *args);
static PyObject *dap_events_start_py(PyDapEventsObject *self,  PyObject *args);
static PyObject *dap_events_wait_py(PyDapEventsObject *self,  PyObject *arg);

static PyMethodDef PyDapEventsObject_methods[] = {
        {"start", (PyCFunction)dap_events_start_py, METH_NOARGS, ""},
        {"wait", (PyCFunction)dap_events_wait_py, METH_NOARGS, ""},
        {"killSocket", (PyCFunction)dap_events_socket_kill_socket_py, METH_VARARGS, ""},
        {"removeAndDeleteSocket", (PyCFunction)dap_events_socket_remove_and_delete_py, METH_VARARGS, ""},
        {}  /* Sentinel */
};

PyTypeObject DapEventsObjectType = DAP_PY_TYPE_OBJECT(
        "DAP.IO.Events", sizeof(PyDapEventsObject),
        "DapEvents objects",
        .tp_dealloc = (destructor)PyDapEventsObject_dealloc,
        .tp_methods = PyDapEventsObject_methods);

static void PyDapEventsObject_dealloc(PyDapEventsObject *eventsObject){
    Py_TYPE(eventsObject)->tp_free((PyObject*)eventsObject);
}

static PyObject *dap_events_socket_remove_and_delete_py(PyDapEventsObject *self, PyObject *args){
    PyObject *in_obj;
    PyObject *in_bool;
    if (!PyArg_ParseTuple(args, "O|O", &in_obj, &in_bool)){
        return NULL;
    }
    bool preserve_inheritor = true;
    if (in_bool == Py_False)
        preserve_inheritor = false;
    UNUSED(preserve_inheritor); // Is it really need for?
    dap_events_socket_remove_and_delete(((PyDapEventsSocketObject*)in_obj)->t_events_socket->worker,
                                           ((PyDapEventsSocketObject*)in_obj)->t_events_socket->uuid);
    return PyLong_FromLong(0);
}

static PyObject *dap_events_socket_kill_socket_py(PyDapEventsObject *self, PyObject *args){
    PyObject *in_obj;
    if (!PyArg_ParseTuple(args, "O", &in_obj)){
        return NULL;
    }
    dap_events_socket_remove_and_delete(((PyDapEventsSocketObject*)in_obj)->t_events_socket->worker,
                                           ((PyDapEventsSocketObject*)in_obj)->t_events_socket->uuid);
    return PyLong_FromLong(0);
}

static PyObject *dap_events_start_py(__attribute__((unused)) PyDapEventsObject *self, __attribute__((unused)) PyObject *args)
{
    int32_t result = dap_events_start();
    return PyLong_FromLong(result);
}

static PyObject *dap_events_wait_py(__attribute__((unused)) PyDapEventsObject *self, __attribute__((unused)) PyObject *args)
{
    int32_t result = dap_events_wait();
    return PyLong_FromLong(result);
}
