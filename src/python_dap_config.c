/*
 * Python DAP Config Implementation
 */

#include "python_cellframe_common.h"
#include "dap_config.h"

// Config functions
int dap_config_init(void) {
    return dap_config_init();
}

void dap_config_deinit(void) {
    dap_config_deinit();
}

void* dap_config_open(const char* path) {
    return dap_config_open(path);
}

void dap_config_close(void* config) {
    if (config) {
        dap_config_close((dap_config_t*)config);
    }
}

const char* dap_config_get_item_str(void* config, const char* section, const char* key, const char* default_value) {
    if (!config || !section || !key) {
        return default_value;
    }
    return dap_config_get_item_str((dap_config_t*)config, section, key);
}

int dap_config_get_item_int(void* config, const char* section, const char* key, int default_value) {
    if (!config || !section || !key) {
        return default_value;
    }
    return dap_config_get_item_int32((dap_config_t*)config, section, key);
}

bool dap_config_get_item_bool(void* config, const char* section, const char* key, bool default_value) {
    if (!config || !section || !key) {
        return default_value;
    }
    return dap_config_get_item_bool((dap_config_t*)config, section, key);
}

bool dap_config_set_item_str(void* config, const char* section, const char* key, const char* value) {
    if (!config || !section || !key || !value) {
        return false;
    }
    return dap_config_set_item_str((dap_config_t*)config, section, key, value) == 0;
}

bool dap_config_set_item_int(void* config, const char* section, const char* key, int value) {
    if (!config || !section || !key) {
        return false;
    }
    return dap_config_set_item_int32((dap_config_t*)config, section, key, value) == 0;
}

bool dap_config_set_item_bool(void* config, const char* section, const char* key, bool value) {
    if (!config || !section || !key) {
        return false;
    }
    return dap_config_set_item_bool((dap_config_t*)config, section, key, value) == 0;
}

const char* dap_config_get_sys_dir(void) {
    return dap_config_get_sys_dir();
}

const char* py_m_dap_config_get_item(const char* section, const char* key, const char* default_value) {
    if (!section || !key) {
        return default_value;
    }
    return dap_config_get_item_str_default(dap_config_default(), section, key, default_value);
}

const char* py_m_dap_config_get_sys_dir(void) {
    return dap_config_get_sys_dir();
} 