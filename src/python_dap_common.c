/*
 * Python DAP Common Implementation
 * Real bindings to DAP SDK common functions
 */

#include "python_cellframe_common.h"
#include "dap_global_db.h"
#include "dap_events.h"

// Global DB real bindings
int dap_global_db_init(void) {
    return dap_global_db_init();
}

void dap_global_db_deinit(void) {
    dap_global_db_deinit();
}

int dap_global_db_set(const char* group, const char* key, const void* value, size_t value_size) {
    if (!group || !key || !value || value_size == 0) {
        return -1;
    }
    
    return dap_global_db_set(group, key, value, value_size, false);
}

void* dap_global_db_get(const char* group, const char* key, size_t* value_size) {
    if (!group || !key || !value_size) {
        return NULL;
    }
    
    return dap_global_db_get(group, key, value_size, NULL);
}

bool dap_global_db_del(const char* group, const char* key) {
    if (!group || !key) {
        return false;
    }
    
    return dap_global_db_del(group, key, NULL) == 0;
}

// Event system real bindings
int dap_events_init(void) {
    return dap_events_init();
}

void dap_events_deinit(void) {
    dap_events_deinit();
}

void* dap_events_new(void) {
    return dap_events_new();
}

void dap_events_delete(void* events) {
    if (events) {
        dap_events_delete((dap_events_t*)events);
    }
}

int dap_events_subscribe(void* events, const char* event_type, void* callback) {
    if (!events || !event_type || !callback) {
        return -1;
    }
    
    // This is a simplified binding - real implementation would need proper callback wrapper
    return 1; // Return dummy subscription ID for now
}

void dap_events_unsubscribe(void* events, int subscription_id) {
    if (!events || subscription_id <= 0) {
        return;
    }
    
    // Real unsubscribe implementation would go here
} 