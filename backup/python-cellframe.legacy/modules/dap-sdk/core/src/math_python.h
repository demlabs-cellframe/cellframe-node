/*
 * Authors:
 * Alexey V. Stratulat <alexey.stratulat@demlabs.net>
 * DeM Labs Inc.   https://demlabs.net
 * CellFrame       https://cellframe.net
 * Sources         https://gitlab.demlabs.net/cellframe
 * Copyright  (c) 2022
 * All rights reserved.

 This file is part of DAP (Distributed Applications Platform) the open source project

    DAP (Distributed Applications Platform) is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    DAP is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with any DAP based project.  If not, see <http://www.gnu.org/licenses/>.
*/
#pragma once

#include <Python.h>
#include "dap_common.h"
#include "dap_math_ops.h"

typedef struct DapMath{
    PyObject_HEAD
    uint256_t value;
}DapMathObject;

int math_python_create(PyObject *self, PyObject *argv, PyObject *kwds);
PyObject *math_python_calc_percent(PyObject *self, PyObject *argv);
PyObject *math_python_str(PyObject *self);

PyObject *wrapping_math_python_add(PyObject *o1, PyObject *o2);
PyObject *wrapping_math_python_subtract(PyObject *o1, PyObject *o2);
PyObject *wrapping_math_python_multiply(PyObject *o1, PyObject *o2);
PyObject *wrapping_math_python_true_divide(PyObject *o1, PyObject *o2);
PyObject *wrapping_math_python_power(PyObject *o1, PyObject *o2, PyObject *o3);
PyObject *wrapping_math_python_floor_divmode(PyObject *o1, PyObject *o2);
PyObject *wrapping_math_python_remainder(PyObject *o1, PyObject *o2);
PyObject *wrapping_math_python_divmode(PyObject *o1, PyObject *o2);
PyObject *wrapping_math_python_float(PyObject *o1);
PyObject *math_python_richcompare(PyObject *O1, PyObject *O2, int opid);

PyObject *wrapping_dap_chain_balance_to_coins(PyObject *self, PyObject *args);
PyObject *wrapping_dap_math_get_coins(PyObject *self, void *closure);
PyObject *wrapping_dap_math_get_balance(PyObject *self, void *closure);

extern PyTypeObject DapMathObjectType;

DAP_STATIC_INLINE bool DapMathObject_Check(PyObject *obj_math){
    return PyObject_TypeCheck(obj_math, &DapMathObjectType);
}
