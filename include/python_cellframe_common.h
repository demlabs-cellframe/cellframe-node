/*
 * Python Cellframe Common Header
 * Function declarations for Python DAP SDK bindings
 */

#ifndef PYTHON_CELLFRAME_COMMON_H
#define PYTHON_CELLFRAME_COMMON_H

#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

// Core DAP functions
int dap_common_init_py(const char* a_console_title, const char* a_log_file_path);
void dap_common_deinit_py(void);

// Config functions
void* dap_config_init_py(const char* a_config_path);
void dap_config_deinit_py(void* a_config);
char* dap_config_get_item_str_py(void* a_config, const char* a_section, const char* a_param);

// System directory functions
char* dap_get_sys_dir_path_py(void);

// Crypto functions
int dap_crypto_init_py(void);
void dap_crypto_deinit_py(void);
int dap_hash_fast_py(const void* a_data, size_t a_data_size, void* a_hash_out);
size_t dap_hash_fast_get_size_py(void);
int dap_hash_fast_compare_py(const void* a_hash1, const void* a_hash2);
int dap_hash_fast_from_str_py(const char* a_hash_str, void* a_hash_out);
char* dap_hash_fast_to_str_py(const void* a_hash);

// Key management functions
void* dap_enc_key_new_generate_py(const char* a_key_type, const char* a_key_name, 
                                   const char* a_seed_str, size_t a_key_size);
void dap_enc_key_delete_py(void* a_key);

// Signature functions
int dap_sign_create_py(void* a_key, const void* a_data, size_t a_data_size, 
                       void** a_signature_out, size_t* a_signature_size_out);
int dap_sign_verify_py(void* a_key, const void* a_data, size_t a_data_size,
                       const void* a_signature, size_t a_signature_size);

// Certificate functions
void* dap_cert_generate_py(const char* a_cert_name, void* a_key);
void dap_cert_delete_py(void* a_cert);
int dap_cert_save_to_folder_py(void* a_cert, const char* a_folder_path);
void* dap_cert_load_from_folder_py(const char* a_folder_path, const char* a_cert_name);

// Network functions
void* dap_client_new_py(void);
void dap_client_delete_py(void* a_client);
int dap_client_connect_to_py(void* a_client, const char* a_addr, uint16_t a_port);
int dap_client_disconnect_py(void* a_client);
size_t dap_client_write_py(void* a_client, const void* a_data, size_t a_data_size);
size_t dap_client_read_py(void* a_client, void* a_buffer, size_t a_buffer_size);
bool dap_client_is_connected_py(void* a_client);

// Server functions
void* dap_server_new_py(void);
void dap_server_delete_py(void* a_server);
int dap_server_listen_py(void* a_server, const char* a_addr, uint16_t a_port);
int dap_server_stop_py(void* a_server);

// Event socket functions
void* dap_events_socket_create_py(int a_socket_domain, int a_socket_type);
void dap_events_socket_delete_py(void* a_events_socket);

// HTTP functions
int dap_http_simple_request_py(const char* a_url_str, void** a_response_data, size_t* a_response_size);
char* dap_http_simple_request_str_py(const char* a_url_str);

// Global database functions (python_gdb.c)
int dap_global_db_init_py(void);
void dap_global_db_deinit_py(void);
int dap_global_db_set_py(const char* a_group, const char* a_key, 
                         const void* a_value, size_t a_value_size);
void* dap_global_db_get_py(const char* a_group, const char* a_key, size_t* a_value_size);
int dap_global_db_del_py(const char* a_group, const char* a_key);
int dap_global_db_get_count_py(const char* a_group);
char** dap_global_db_get_keys_py(const char* a_group, size_t* a_keys_count);
void dap_global_db_free_keys_py(char** a_keys, size_t a_keys_count);

// System functions
uint64_t dap_time_now_py(void);
uint64_t dap_time_from_str_py(const char* a_time_str);
char* dap_time_to_str_py(uint64_t a_timestamp);
int dap_time_sleep_py(uint32_t a_seconds);

// Logging functions
void dap_log_py(int a_level, const char* a_format, const char* a_message);

// Version and system info functions
char* dap_get_version_py(void);

// Memory management functions
void* dap_malloc_py(size_t a_size);
void dap_free_py(void* a_ptr);
void* dap_realloc_py(void* a_ptr, size_t a_size);

// Thread functions
uint32_t dap_get_current_thread_id_py(void);

// File system functions
bool dap_dir_test_py(const char* a_path);
int dap_mkdir_with_parents_py(const char* a_path);
char* dap_path_get_dirname_py(const char* a_path);

#ifdef __cplusplus
}
#endif

#endif /* PYTHON_CELLFRAME_COMMON_H */ 