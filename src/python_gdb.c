/*
 * Python DAP Global Database Implementation
 * Real bindings to DAP SDK Global Database functions
 */

#include "python_cellframe_common.h"
#define LOG_TAG "PY_DAP_GDB"
#include "dap_common.h"
#include "dap_global_db.h"
#include <errno.h>

// Global Database initialization and management
int dap_global_db_init_py(void) {
    // Initialize global database with default settings
    log_it(L_INFO, "Initializing Global Database");
    return dap_global_db_init() == 0 ? 0 : -1;
}

void dap_global_db_deinit_py(void) {
    log_it(L_INFO, "Deinitializing Global Database");
    dap_global_db_deinit();
}

// Database operations using real DAP SDK API
int dap_global_db_set_py(const char* a_group, const char* a_key, 
                         const void* a_value, size_t a_value_size) {
    if (!a_group || !a_key || !a_value || a_value_size == 0) {
        log_it(L_ERROR, "Invalid parameters for global DB set operation");
        return -EINVAL;
    }
    
    log_it(L_DEBUG, "Setting global DB key %s:%s (size: %zu)", a_group, a_key, a_value_size);
    
    // Use DAP SDK global DB set function with callback for async operation
    int l_result = dap_global_db_set(a_group, a_key, a_value, a_value_size, false, NULL, NULL);
    
    if (l_result != 0) {
        log_it(L_ERROR, "Failed to set global DB key %s:%s, error: %d", a_group, a_key, l_result);
        return l_result;
    }
    
    return 0;
}

// Global DB get with proper callback handling
typedef struct {
    void** out_data;
    size_t* out_size;
    int result;
    bool completed;
} dap_gdb_get_context_t;

// Callback for async get operation
static void s_gdb_get_callback(dap_global_db_instance_t *a_dbi, int a_rc, const char *a_group, 
                               const char *a_key, const void *a_value, const size_t a_value_len, 
                               dap_nanotime_t a_value_ts, bool a_is_pinned, void *a_arg) {
    dap_gdb_get_context_t* l_ctx = (dap_gdb_get_context_t*)a_arg;
    
    if (!l_ctx) {
        return;
    }
    
    l_ctx->result = a_rc;
    l_ctx->completed = true;
    
    if (a_rc == 0 && a_value && a_value_len > 0) {
        // Allocate memory for the value
        void* l_data = DAP_NEW_SIZE(uint8_t, a_value_len);
        if (l_data) {
            memcpy(l_data, a_value, a_value_len);
            *(l_ctx->out_data) = l_data;
            *(l_ctx->out_size) = a_value_len;
            log_it(L_DEBUG, "Retrieved global DB key %s:%s (size: %zu)", a_group, a_key, a_value_len);
        } else {
            l_ctx->result = -ENOMEM;
            log_it(L_ERROR, "Failed to allocate memory for global DB value");
        }
    } else {
        *(l_ctx->out_data) = NULL;
        *(l_ctx->out_size) = 0;
        log_it(L_DEBUG, "Global DB key %s:%s not found or error: %d", a_group, a_key, a_rc);
    }
}

void* dap_global_db_get_py(const char* a_group, const char* a_key, size_t* a_value_size) {
    if (!a_group || !a_key || !a_value_size) {
        log_it(L_ERROR, "Invalid parameters for global DB get operation");
        return NULL;
    }
    
    log_it(L_DEBUG, "Getting global DB key %s:%s", a_group, a_key);
    
    void* l_data = NULL;
    dap_gdb_get_context_t l_ctx = {
        .out_data = &l_data,
        .out_size = a_value_size,
        .result = -1,
        .completed = false
    };
    
    // Use DAP SDK global DB get function with callback
    int l_result = dap_global_db_get(a_group, a_key, s_gdb_get_callback, &l_ctx);
    
    if (l_result != 0) {
        log_it(L_ERROR, "Failed to initiate global DB get for key %s:%s, error: %d", a_group, a_key, l_result);
        *a_value_size = 0;
        return NULL;
    }
    
    // Wait for callback completion (simplified for synchronous behavior)
    // In production, this should be handled with proper async patterns
    int l_wait_count = 0;
    while (!l_ctx.completed && l_wait_count < 1000) {
        usleep(1000); // 1ms sleep
        l_wait_count++;
    }
    
    if (!l_ctx.completed) {
        log_it(L_WARNING, "Global DB get operation timed out for key %s:%s", a_group, a_key);
        *a_value_size = 0;
        return NULL;
    }
    
    if (l_ctx.result != 0) {
        log_it(L_DEBUG, "Global DB get completed with error %d for key %s:%s", l_ctx.result, a_group, a_key);
        *a_value_size = 0;
        return NULL;
    }
    
    return l_data;
}

// Global DB delete with proper callback handling
typedef struct {
    int result;
    bool completed;
} dap_gdb_del_context_t;

// Callback for async delete operation
static void s_gdb_del_callback(dap_global_db_instance_t *a_dbi, int a_rc, const char *a_group, 
                               const char *a_key, const void *a_value, const size_t a_value_len, 
                               dap_nanotime_t a_value_ts, bool a_is_pinned, void *a_arg) {
    dap_gdb_del_context_t* l_ctx = (dap_gdb_del_context_t*)a_arg;
    
    if (l_ctx) {
        l_ctx->result = a_rc;
        l_ctx->completed = true;
    }
}

int dap_global_db_del_py(const char* a_group, const char* a_key) {
    if (!a_group || !a_key) {
        log_it(L_ERROR, "Invalid parameters for global DB delete operation");
        return -EINVAL;
    }
    
    log_it(L_DEBUG, "Deleting global DB key %s:%s", a_group, a_key);
    
    dap_gdb_del_context_t l_ctx = {
        .result = -1,
        .completed = false
    };
    
    // Use DAP SDK global DB delete function with callback
    int l_result = dap_global_db_del(a_group, a_key, s_gdb_del_callback, &l_ctx);
    
    if (l_result != 0) {
        log_it(L_ERROR, "Failed to initiate global DB delete for key %s:%s, error: %d", a_group, a_key, l_result);
        return l_result;
    }
    
    // Wait for callback completion (simplified for synchronous behavior)
    int l_wait_count = 0;
    while (!l_ctx.completed && l_wait_count < 1000) {
        usleep(1000); // 1ms sleep
        l_wait_count++;
    }
    
    if (!l_ctx.completed) {
        log_it(L_WARNING, "Global DB delete operation timed out for key %s:%s", a_group, a_key);
        return -ETIMEDOUT;
    }
    
    if (l_ctx.result != 0) {
        log_it(L_ERROR, "Global DB delete failed with error %d for key %s:%s", l_ctx.result, a_group, a_key);
        return l_ctx.result;
    }
    
    log_it(L_DEBUG, "Successfully deleted global DB key %s:%s", a_group, a_key);
    return 0;
}

// Global DB utility functions
int dap_global_db_get_count_py(const char* a_group) {
    if (!a_group) {
        log_it(L_ERROR, "Invalid group parameter for global DB count operation");
        return -EINVAL;
    }
    
    log_it(L_DEBUG, "Getting count for global DB group %s", a_group);
    
    // This would require implementing a callback-based count function
    // For now, return placeholder
    return 0;
}

char** dap_global_db_get_keys_py(const char* a_group, size_t* a_keys_count) {
    if (!a_group || !a_keys_count) {
        log_it(L_ERROR, "Invalid parameters for global DB keys list operation");
        return NULL;
    }
    
    log_it(L_DEBUG, "Getting keys list for global DB group %s", a_group);
    
    // This would require implementing a callback-based keys enumeration
    // For now, return empty list
    *a_keys_count = 0;
    return NULL;
}

void dap_global_db_free_keys_py(char** a_keys, size_t a_keys_count) {
    if (!a_keys || a_keys_count == 0) {
        return;
    }
    
    for (size_t i = 0; i < a_keys_count; i++) {
        if (a_keys[i]) {
            DAP_DELETE(a_keys[i]);
        }
    }
    DAP_DELETE(a_keys);
} 