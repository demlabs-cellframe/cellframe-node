#include "math_python.h"
#include "dap_chain_common.h"

PyNumberMethods DapMathNumberMethods = {
        .nb_add = wrapping_math_python_add,
        .nb_subtract = wrapping_math_python_subtract,
        .nb_multiply = wrapping_math_python_multiply,
        .nb_true_divide = wrapping_math_python_true_divide,
        .nb_floor_divide = wrapping_math_python_floor_divmode,
        .nb_remainder = wrapping_math_python_remainder,
        .nb_divmod = wrapping_math_python_divmode,
        .nb_power = wrapping_math_python_power,
        .nb_float = wrapping_math_python_float
};

static PyGetSetDef DapMathGetsSets[] = {
        {"coins", (getter)wrapping_dap_math_get_coins, NULL, NULL, NULL},
        {"balance", (getter)wrapping_dap_math_get_balance, NULL, NULL, NULL},
        {NULL, NULL, NULL, NULL, NULL}
};

static PyMethodDef DapMathMethods[] = {
        {"balance_to_coins", wrapping_dap_chain_balance_to_coins,
         METH_VARARGS | METH_STATIC, "The function calculates the number of coins from the number of datoshi."},
        {"percent", math_python_calc_percent,
         METH_VARARGS, "The function calculates the specified percentage of a number."},
        {NULL, NULL, 0, NULL}
};

PyTypeObject DapMathObjectType = {
        PyVarObject_HEAD_INIT(NULL, 0)
        .tp_name = "DAP.Core.Math",
        .tp_basicsize = sizeof(DapMathObject),
        .tp_as_number = &DapMathNumberMethods,
        .tp_str = math_python_str,
        .tp_richcompare = math_python_richcompare,
        .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
        "Dap math methods",
        .tp_getset = DapMathGetsSets,
        .tp_methods = DapMathMethods,
        .tp_init = math_python_create,
        .tp_new = PyType_GenericNew,
};

int math_python_create(PyObject *self, PyObject *argv, PyObject *kwds){
    const char *kwlist[] = {
            "number",
            NULL
    };
    char *l_number_str;
    if (!PyArg_ParseTupleAndKeywords(argv, kwds, "s", (char**)kwlist, &l_number_str))
        return -1;
    bool l_is_decimal = false;
    for (size_t i = 0; i < dap_strlen(l_number_str); i++){
        if (l_number_str[i] == '.') {
            l_is_decimal = true;
            break;
        }
    }
    ((DapMathObject*)self)->value = l_is_decimal ? dap_chain_balance_coins_scan(l_number_str) : dap_chain_balance_datoshi_scan(l_number_str);
    return 0;
}

PyObject *math_python_str(PyObject *self){
    char *l_balance = dap_chain_balance_datoshi_print(((DapMathObject*)self)->value);
    PyObject *l_obj_balance = Py_BuildValue("s", l_balance);
    DAP_DELETE(l_balance);
    return l_obj_balance;
}

typedef struct pvt_struct_parse_numbers{
    uint256_t n1;
    uint256_t n2;
}pvt_struct_parse_numbers_t;

/**
 * Converts two PyObjects to a special intermediate structure.
 * @param O1 PyObject*
 * @param O2 PyObject*
 * @param result Pointer to a structure in which to put two numbers.
 * @return If successful, it is 0, otherwise any other number.
 */
int pvt_parse_object(PyObject *O1, PyObject *O2, pvt_struct_parse_numbers_t *result){
    uint256_t l_number = {0};
    uint256_t l_number_2 = {0};
    PyObject *obj_number = NULL;
    if (PyObject_TypeCheck(O1, &DapMathObjectType)){
        l_number = ((DapMathObject*)O1)->value;
        obj_number = O2;
    } else {
        l_number = ((DapMathObject*)O2)->value;
        obj_number = O1;
    }
    bool l_parse_numer = false;
    if (PyObject_TypeCheck(obj_number, &DapMathObjectType)){
        l_number_2 = ((DapMathObject*)obj_number)->value;
        l_parse_numer = true;
    }
    if (PyFloat_Check(obj_number) || PyComplex_Check(obj_number)){
        return -1;
    }
    if (PyLong_Check(obj_number)){
        uint64_t l_temp = PyLong_AsLong(obj_number);
        l_number_2 = dap_chain_uint256_from(l_temp);
        l_parse_numer = true;
    }
    if(!l_parse_numer)
        return -2;
    result->n1  = l_number;
    result->n2 = l_number_2;
    return 0;
}

PyObject *wrapping_math_python_add(PyObject *o1, PyObject *o2){
    pvt_struct_parse_numbers_t l_numbers = {0};
    int res = pvt_parse_object(o1, o2, &l_numbers);
    if (res == 0){
        uint256_t l_result = {0};
        if (!SUM_256_256(l_numbers.n1, l_numbers.n2, &l_result)){
            DapMathObject *obj_result = PyObject_New(DapMathObject, &DapMathObjectType);
            obj_result->value = l_result;
            return (PyObject*)obj_result;
        }else{
            PyErr_SetString(PyExc_NotImplementedError, "Failed to add two 256-bit numbers.");
            return NULL;
        }
    }
    else if (res == -1){
        PyErr_SetString(PyExc_AttributeError, "The 256-bit math in SDK does not support operations "
                                                   "on complex numbers and floating point numbers.");
        return NULL;
    }
    else if (res == -2){
        PyErr_SetString(PyExc_AttributeError, "Looks like one of the operands is not a number.");
        return NULL;
    }
    else{
        PyErr_SetString(PyExc_AttributeError, "An error has occurred, the cause cannot be determined");
        return NULL;
    }
}
PyObject *wrapping_math_python_subtract(PyObject *o1, PyObject *o2){
    pvt_struct_parse_numbers_t l_numbers = {0};
    int res = pvt_parse_object(o1, o2, &l_numbers);
    if (res == 0){
        uint256_t l_result = {0};
        if (!SUBTRACT_256_256(l_numbers.n1, l_numbers.n2, &l_result)){
            DapMathObject *obj_result = PyObject_New(DapMathObject, &DapMathObjectType);
            obj_result->value = l_result;
            return (PyObject*)obj_result;
        }else{
            PyErr_SetString(PyExc_NotImplementedError, "Failed to add two 256-bit numbers.");
            return NULL;
        }
    }
    else if (res == -1){
        PyErr_SetString(PyExc_AttributeError, "The 256-bit math in SDK does not support operations "
                                              "on complex numbers and floating point numbers.");
        return NULL;
    }
    else if (res == -2){
        PyErr_SetString(PyExc_AttributeError, "Looks like one of the operands is not a number.");
        return NULL;
    }
    else{
        PyErr_SetString(PyExc_AttributeError, "An error has occurred, the cause cannot be determined");
        return NULL;
    }
}
PyObject *wrapping_math_python_multiply(PyObject *o1, PyObject *o2){
    pvt_struct_parse_numbers_t l_numbers = {0};
    int res = pvt_parse_object(o1, o2, &l_numbers);
    if (res == 0){
        uint256_t l_result = {0};
        if (!MULT_256_256(l_numbers.n1, l_numbers.n2, &l_result)){
            DapMathObject *obj_result = PyObject_New(DapMathObject, &DapMathObjectType);
            obj_result->value = l_result;
            return (PyObject*)obj_result;
        }else{
            PyErr_SetString(PyExc_NotImplementedError, "Failed to add two 256-bit numbers.");
            return NULL;
        }
    }
    else if (res == -1){
        PyErr_SetString(PyExc_AttributeError, "The 256-bit math in SDK does not support operations "
                                              "on complex numbers and floating point numbers.");
        return NULL;
    }
    else if (res == -2){
        PyErr_SetString(PyExc_AttributeError, "Looks like one of the operands is not a number.");
        return NULL;
    }
    else{
        PyErr_SetString(PyExc_AttributeError, "An error has occurred, the cause cannot be determined");
        return NULL;
    }
}
PyObject *wrapping_math_python_true_divide(PyObject *o1, PyObject *o2){
    pvt_struct_parse_numbers_t l_numbers = {0};
    int res = pvt_parse_object(o1, o2, &l_numbers);
    if (res == 0){
        uint256_t l_result = {0};
        DIV_256_COIN(l_numbers.n1, l_numbers.n2, &l_result);
        DapMathObject *obj_result = PyObject_New(DapMathObject, &DapMathObjectType);
        obj_result->value = l_result;
        return (PyObject*)obj_result;
    }
    else if (res == -1){
        PyErr_SetString(PyExc_AttributeError, "The 256-bit math in SDK does not support operations "
                                              "on complex numbers and floating point numbers.");
        return NULL;
    }
    else if (res == -2){
        PyErr_SetString(PyExc_AttributeError, "Looks like one of the operands is not a number.");
        return NULL;
    }
    else{
        PyErr_SetString(PyExc_AttributeError, "An error has occurred, the cause cannot be determined");
        return NULL;
    }
}

PyObject *wrapping_math_python_power(PyObject *o1, PyObject *o2, PyObject *o3){
    uint256_t a = uint256_0, b = uint256_0, res = uint256_0;
    if (o3 != Py_None) {
        PyErr_SetString(PyExc_AttributeError, "The 256-bit math in SDK does not support operations "
                                              "on complex numbers and floating point numbers.");
        return NULL;
    }
    if (!PyObject_TypeCheck(o1, &DapMathObjectType)) {
        PyErr_SetString(PyExc_AttributeError, "The 256-bit math in SDK does not support operations "
                                              "on complex numbers and floating point numbers.");
        return NULL;
    }
    a = ((DapMathObject*)o1)->value;
    if (!PyObject_TypeCheck(o2, &DapMathObjectType)) {
        PyErr_SetString(PyExc_AttributeError, "The 256-bit math in SDK does not support operations "
                                              "on complex numbers and floating point numbers.");
        return NULL;
    }
    b = ((DapMathObject*)o2)->value;
    res = a;
    for (uint256_t i = uint256_1; compare256(i, b) == -1; SUM_256_256(i, uint256_1, &i)){
        MULT_256_256(res, a, &res);
    }
    DapMathObject *obj_math = PyObject_New(DapMathObject, &DapMathObjectType);
    obj_math->value = res;
    return (PyObject*)obj_math;
}

PyObject *wrapping_math_python_remainder(PyObject *o1, PyObject *o2){
    pvt_struct_parse_numbers_t l_numbers = {0};
    int res = pvt_parse_object(o1, o2, &l_numbers);
    if (res == 0){
        uint256_t l_result = {0};
        uint256_t l_ret = uint256_0;
        uint256_t l_remainder = uint256_0;
        divmod_impl_256(l_numbers.n1, l_numbers.n2, &l_ret, &l_remainder);
        DapMathObject *obj_result = PyObject_New(DapMathObject, &DapMathObjectType);
        obj_result->value = l_remainder;
        return (PyObject*)obj_result;
    }
    else if (res == -1){
        PyErr_SetString(PyExc_AttributeError, "The 256-bit math in SDK does not support operations "
                                              "on complex numbers and floating point numbers.");
        return NULL;
    } else {
        PyErr_SetString(PyExc_AttributeError, "Looks like one of the operands is not a number.");
        return NULL;
    }
}

PyObject *wrapping_math_python_floor_divmode(PyObject *o1, PyObject *o2){
    pvt_struct_parse_numbers_t  l_numbers = {0};
    int res = pvt_parse_object(o1, o2, &l_numbers);
    if (res == 0){
        uint256_t l_result = {0};
        uint256_t l_ret = uint256_0;
        uint256_t l_remainder = uint256_0;
        divmod_impl_256(l_numbers.n1, l_numbers.n2, &l_ret, &l_remainder);
        DapMathObject *obj_result = PyObject_New(DapMathObject, &DapMathObjectType);
        obj_result->value = l_ret;
        return (PyObject*)obj_result;
    }
    else if (res == -1){
        PyErr_SetString(PyExc_AttributeError, "The 256-bit math in SDK does not support operations "
                                              "on complex numbers and floating point numbers.");
        return NULL;
    } else {
        PyErr_SetString(PyExc_AttributeError, "Looks like one of the operands is not a number.");
        return NULL;
    }
}


PyObject *wrapping_math_python_divmode(PyObject *o1, PyObject *o2){
    pvt_struct_parse_numbers_t l_numbers = {0};
    int res = pvt_parse_object(o1, o2, &l_numbers);
    if (res == 0){
        uint256_t l_result = {0};
        uint256_t l_ret = uint256_0;
        uint256_t l_remainder = uint256_0;
        divmod_impl_256(l_numbers.n1, l_numbers.n2, &l_ret, &l_remainder);
        DapMathObject *obj_v1 = PyObject_New(DapMathObject, &DapMathObjectType);
        obj_v1->value = l_ret;
        DapMathObject *obj_v2 = PyObject_New(DapMathObject, &DapMathObjectType);
        obj_v2->value = l_remainder;
        return Py_BuildValue("OO", (PyObject*)obj_v1, (PyObject*)obj_v2);
    }
    else if (res == -1){
        PyErr_SetString(PyExc_AttributeError, "The 256-bit math in SDK does not support operations "
                                              "on complex numbers and floating point numbers.");
        return NULL;
    } else {
        PyErr_SetString(PyExc_AttributeError, "Looks like one of the operands is not a number.");
        return NULL;
    }
}

PyObject *wrapping_math_python_float(PyObject *o1){
    uint256_t in = ((DapMathObject*)o1)->value;
    double out = dap_uint256_decimal_to_double(in);
    PyObject *obj_ret = PyFloat_FromDouble(out);
    return obj_ret;
}

PyObject *math_python_richcompare(PyObject *O1, PyObject *O2, int opid){
    pvt_struct_parse_numbers_t l_result = {0};
    int res = pvt_parse_object(O1, O2, &l_result);
    if (res != 0)
        return NULL;
    res = compare256(l_result.n1, l_result.n2);
    switch (opid) {
        case Py_LT: // <
            if (res == -1)
                Py_RETURN_TRUE;
            break;
        case Py_LE: // <=
            if (res != 1)
                Py_RETURN_TRUE;
            break;
        case Py_EQ: // ==
            if (res == 0)
                Py_RETURN_TRUE;
            break;
        case Py_NE: // !=
            if (res != 0)
                Py_RETURN_TRUE;
            break;
        case Py_GT: // >
            if (res == 1)
                Py_RETURN_TRUE;
            break;
        case Py_GE: // >=
            if (res != -1)
                Py_RETURN_TRUE;
            break;
    }
    Py_RETURN_FALSE;
}

PyObject *wrapping_dap_math_get_coins(PyObject *self, void *closure){
    (void)closure;
    char *l_coins = dap_chain_balance_coins_print(((DapMathObject*)self)->value);
    PyObject *l_obj_coins = Py_BuildValue("s", l_coins);
    DAP_DELETE(l_coins);
    return l_obj_coins;
}

PyObject *wrapping_dap_math_get_balance(PyObject *self, void *closure){
    (void)closure;
    char *l_balance = dap_chain_balance_datoshi_print(((DapMathObject*)self)->value);
    PyObject *l_obj_res = Py_BuildValue("s", l_balance);
    DAP_DELETE(l_balance);
    return l_obj_res;
}

PyObject *wrapping_dap_chain_balance_to_coins(PyObject *self, PyObject *args){
    (void)self;
    uint64_t l_balance;
    if(!PyArg_ParseTuple(args, "k", &l_balance)){
        return NULL;
    }
//    dap_chain_uint256_to()
    uint256_t l_balance_256 = dap_chain_uint256_from(l_balance);
    char *l_balance_str = dap_chain_balance_coins_print(l_balance_256);
    PyObject *l_obj_balance = Py_BuildValue("s", l_balance);
    DAP_DELETE(l_balance);
    return l_obj_balance;
}

PyObject *math_python_calc_percent(PyObject *self, PyObject *argv){
    uint256_t l_o1 = ((DapMathObject*)self)->value;
    uint256_t l_o2 = uint256_0;
    uint256_t l_result = uint256_0;
    uint256_t l_base = dap_chain_balance_scan("100");
    PyObject *obj_o2 = NULL;
    if (!PyArg_ParseTuple(argv, "O", obj_o2)){
        return NULL;
    }
    l_o2 = ((DapMathObject*)obj_o2)->value;
    uint256_t t1 = uint256_0;
    DIV_256_COIN(l_o2, l_base, &t1);
    MULT_256_256(l_o1, t1, &l_result);
    DapMathObject *l_obj_result = PyObject_New(DapMathObject, &DapMathObjectType);
    l_obj_result->value = l_result;
    return (PyObject*)l_obj_result;
}
