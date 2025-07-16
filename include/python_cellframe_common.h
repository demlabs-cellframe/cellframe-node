#ifndef PYTHON_CELLFRAME_COMMON_H
#define PYTHON_CELLFRAME_COMMON_H

/*
 * Python CellFrame Common Library
 * 
 * C functions for Python DAP SDK integration
 * Provides direct interface between Python and DAP SDK
 */

#include <stddef.h>
#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

// Core DAP functions
int dap_common_init(void);
void dap_common_deinit(void);

// Memory management functions
void* dap_malloc(size_t size);
void dap_free(void* ptr);
void* dap_calloc(size_t num, size_t size);
void* dap_realloc(void* ptr, size_t size);

// Config functions
int dap_config_init(void);
void dap_config_deinit(void);
void* dap_config_open(const char* path);
void dap_config_close(void* config);
const char* dap_config_get_item_str(void* config, const char* section, const char* key, const char* default_value);
int dap_config_get_item_int(void* config, const char* section, const char* key, int default_value);
bool dap_config_get_item_bool(void* config, const char* section, const char* key, bool default_value);
bool dap_config_set_item_str(void* config, const char* section, const char* key, const char* value);
bool dap_config_set_item_int(void* config, const char* section, const char* key, int value);
bool dap_config_set_item_bool(void* config, const char* section, const char* key, bool value);
const char* dap_config_get_sys_dir(void);
const char* py_m_dap_config_get_item(const char* section, const char* key, const char* default_value);
const char* py_m_dap_config_get_sys_dir(void);

// Crypto functions
int dap_crypto_init(void);
void dap_crypto_deinit(void);
void* dap_crypto_key_create(const char* type);
void dap_crypto_key_destroy(void* key);
int dap_crypto_key_sign(void* key, const void* data, size_t data_size, void* signature, size_t* signature_size);
bool dap_crypto_key_verify(void* key, const void* data, size_t data_size, const void* signature, size_t signature_size);

// Hash functions - return allocated memory that Python manages
void* dap_hash_fast_py(const void* data, size_t size);
void* dap_hash_slow_py(const void* data, size_t size);
size_t dap_hash_fast_get_size(void);

// Network functions
int dap_network_init(void);
void dap_network_deinit(void);
void* dap_client_new(void);
void dap_client_delete(void* client);
int dap_client_connect_to(void* client, const char* addr, int port);
void dap_client_disconnect(void* client);
int dap_client_write(void* client, const void* data, size_t size);
int dap_client_read(void* client, void* buffer, size_t size);

// Server functions
void* dap_server_new(void);
void dap_server_delete(void* server);
int dap_server_listen(void* server, const char* addr, int port);
void dap_server_stop(void* server);

// System functions
const char* exec_with_ret_multistring(const char* command);

// Time functions
uint64_t dap_time_now(void);
const char* dap_time_to_str_rfc822(uint64_t timestamp);

// Logging functions
void dap_log_level_set(int level);
void dap_log_set_external_output(int output_type, void* callback);
void dap_log_set_format(int format);

// Global DB functions
int dap_global_db_init(void);
void dap_global_db_deinit(void);
int dap_global_db_set(const char* group, const char* key, const void* value, size_t value_size);
void* dap_global_db_get(const char* group, const char* key, size_t* value_size);
bool dap_global_db_del(const char* group, const char* key);

// Event functions
int dap_events_init(void);
void dap_events_deinit(void);
void* dap_events_new(void);
void dap_events_delete(void* events);
int dap_events_subscribe(void* events, const char* event_type, void* callback);
void dap_events_unsubscribe(void* events, int subscription_id);
int dap_events_emit(void* events, const char* event_type, const void* data, size_t data_size);

#ifdef __cplusplus
}
#endif

#endif // PYTHON_CELLFRAME_COMMON_H 