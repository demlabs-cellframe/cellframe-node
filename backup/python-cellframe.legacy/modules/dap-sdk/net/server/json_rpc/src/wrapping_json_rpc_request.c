#include "wrapping_json_rpc_request.h"

#define LOG_TAG "wrapping_json_rpc_request"

static PyMethodDef PyDapJSONRPCRequestMethods[] = {
        {"registrationHandler", (PyCFunction)dap_json_rpc_request_reg_handler_py, METH_VARARGS | METH_STATIC, ""},
        {}
};

PyTypeObject DapJsonRpcRequestObjectType = DAP_PY_TYPE_OBJECT(
        "DAP.Net.JSONRPCRequest", sizeof(PyDAPJsonRPCRequestObject),
        "Dap JSON RPC request object",
        .tp_methods = PyDapJSONRPCRequestMethods);

struct _w_json_rpc_handler *handlers = NULL;

void _w_dap_json_rpc_request_handler(dap_json_rpc_params_t *a_params, dap_json_rpc_response_t *a_response, const char *a_method){
    int count_params = a_params->length;
    PyGILState_STATE GILState = PyGILState_Ensure();
    PyDapJSONRPCResponseObject *obj_response = PyObject_NEW(PyDapJSONRPCResponseObject, &DapJsonRpcResponseobjectType);
    obj_response->response = a_response;
    PyObject *obj_params = PyList_New(count_params);
    for (int i=0; i < count_params; i++) {
        bool tmp_bool;
        double tmp_double;
        int tmp_int;
        char *tmp_string;
        PyObject *obj_ptr = NULL;
        switch (a_params->params[i]->type) {
            case TYPE_PARAM_BOOLEAN:
                tmp_bool = *(bool *) a_params->params[i]->value_param;
                obj_ptr = tmp_bool ? Py_True : Py_False;
                break;
            case TYPE_PARAM_DOUBLE:
                tmp_double = *(double *) (a_params->params[i]->value_param);
                obj_ptr = PyLong_FromDouble(tmp_double);
                break;
            case TYPE_PARAM_INTEGER:
                tmp_int = *(int *) a_params->params[i]->value_param;
                obj_ptr = PyLong_FromLong(tmp_int);
                break;
            case TYPE_PARAM_STRING:
                tmp_string = (char *) a_params->params[i]->value_param;
                obj_ptr = PyUnicode_FromString(tmp_string);
                break;
            default: break;
        }
        if (obj_ptr != NULL) {
            PyList_SetItem(obj_params, i, obj_ptr);
        }
    }
    PyObject *args = Py_BuildValue("OO", obj_params, (PyObject*)obj_response);
    Py_XINCREF(args);
    struct _w_json_rpc_handler *func = NULL;
    HASH_FIND_STR(handlers, a_method, func);
    if (func != NULL){
        //Called python func
        PyObject *obj_result = PyObject_CallObject(func->call_func, args);
        python_error_in_log_it(LOG_TAG);
        PyGILState_Release(GILState);
        if (!obj_result){
            log_it(L_ERROR, "Can't call method: %s", a_method);
            // a_response->type = TYPE_RESPONSE_NULL;
            // a_response->error = DAP_NEW(dap_json_rpc_error_t);
            // a_response->error->code_error = 0xF1;
            // a_response->error->msg = "Can't call method";
            Py_XDECREF(args);
            //a_response->error = dap_json_rpc_error_search_by_code(1);
            return;
        }
    } else {
        PyGILState_Release(GILState);
        log_it(L_WARNING, "Can't call method: %s. It isn't in the python function table", a_method);
        a_response->type = TYPE_RESPONSE_NULL;
        // a_response->error = dap_json_rpc_error_search_by_code(1);
    }
    Py_XDECREF(args);
}

PyObject* dap_json_rpc_request_reg_handler_py(PyObject *self, PyObject *args){
    PyObject *obj_func = NULL;
    char *method = NULL;
    if (!PyArg_ParseTuple(args, "sO", &method, &obj_func)) {
        PyErr_SetString(PyExc_ValueError, "Function takes two arguments, a string and a callable");
        return NULL;
    }
    if(!PyCallable_Check(obj_func)){
        PyErr_SetString(PyExc_ValueError, "The second argument must be a callable");
        return NULL;
    }
    if (dap_json_rpc_registration_request_handler(method, _w_dap_json_rpc_request_handler) != 0){
        PyErr_SetString(PyExc_IndexError, "This handler name is already registered");
        return NULL;
    }
    struct _w_json_rpc_handler *handler = DAP_NEW(struct _w_json_rpc_handler);
    if (!handler) {
        log_it(L_CRITICAL, "Memory allocation error");
        return NULL;
    }
    handler->method = dap_strdup(method);
    Py_INCREF(obj_func);
    handler->call_func = obj_func;
    HASH_ADD_STR(handlers, method, handler);
    Py_RETURN_NONE;
}
