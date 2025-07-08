#pragma once

#include "Python.h"
#include "datetime.h"
#include "libdap-python.h"
//#include "frameobject.h"
#include "dap_common.h"
#include "dap_strfuncs.h"

void python_error_in_log_it(const char *a_tag);
#define _PyErr_logIt(a_level, a_tag, ...) _log_it(NULL, 0, a_tag, a_level, ##__VA_ARGS__)
PyObject *python_get_config_item(dap_config_t* a_config, const char *a_section, const char *a_key, PyObject *obj_default);

DAP_STATIC_INLINE uint64_t PyDateTime_to_timestamp_uint64(PyObject *obj_date_time) {
    struct tm l_tm;
    l_tm.tm_sec = PyDateTime_DATE_GET_SECOND(obj_date_time);
    l_tm.tm_min = PyDateTime_DATE_GET_MINUTE(obj_date_time);
    l_tm.tm_hour = PyDateTime_DATE_GET_HOUR(obj_date_time);
    l_tm.tm_mday = PyDateTime_GET_DAY(obj_date_time);
    l_tm.tm_mon = PyDateTime_GET_MONTH(obj_date_time);
    l_tm.tm_year = PyDateTime_GET_YEAR(obj_date_time);
    time_t tmp = mktime(&l_tm);
    return (tmp <= 0) ? 0 : tmp;
}

#define Py_BuildNone Py_BuildValue("")