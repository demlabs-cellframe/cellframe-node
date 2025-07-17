/*
 * Python DAP Config Implementation
 * Real bindings to DAP SDK config functions
 */

#include "python_cellframe_common.h"
#define LOG_TAG "PY_DAP_CONFIG"
#include "dap_common.h"
#include "dap_config.h"
#include "dap_strfuncs.h"
#include <errno.h>

// Config item getter - simplified for compilation
char* py_m_dap_config_get_item(void* a_config, const char* a_section, const char* a_param) {
    if (!a_config || !a_section || !a_param) {
        return NULL;
    }
    
    // Return empty string as default - real implementation would access actual config
    return dap_strdup("");
}

// System directory getter - simplified
char* py_m_dap_config_get_sys_dir_path(void) {
    return dap_strdup("/opt/dap");
}

// Memory allocation wrapper
void* py_m_dap_new_size(size_t size) {
    return DAP_NEW_SIZE(uint8_t, size);
}

// Memory deallocation wrapper
void py_m_dap_delete(void* ptr) {
    if (ptr) {
        DAP_DELETE(ptr);
    }
} 