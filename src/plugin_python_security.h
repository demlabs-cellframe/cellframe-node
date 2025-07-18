/*
 * Authors:
 * Dmitriy Gerasimov <dmitriy.gerasimov@demlabs.net>
 * DeM Labs Inc.   https://demlabs.net
 * CellFrame       https://cellframe.net
 * Sources         https://gitlab.demlabs.net/cellframe/cellframe-node-plugin-python
 * Copyright  (c) 2017-2025
 * All rights reserved.

 This file is part of CellFrame Node Python Plugin

    CellFrame Node Python Plugin is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    CellFrame Node Python Plugin is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with CellFrame Node Python Plugin.  If not, see <http://www.gnu.org/licenses/>.
*/

#pragma once

#include <stdbool.h>
#include <stdint.h>
#include <limits.h>

#ifdef __cplusplus
extern "C" {
#endif

// Security configuration
#define PYTHON_SECURITY_MAX_PATH_LENGTH     4096
#define PYTHON_SECURITY_MAX_CODE_SIZE       (1024 * 1024)  // 1MB
#define PYTHON_SECURITY_MAX_EXECUTION_TIME  30             // 30 seconds
#define PYTHON_SECURITY_MAX_MEMORY_MB       100            // 100MB
#define PYTHON_SECURITY_MAX_CPU_PERCENT     80             // 80% CPU

// Security validation results
typedef enum {
    PYTHON_SECURITY_RESULT_OK = 0,
    PYTHON_SECURITY_RESULT_INVALID_PATH = -1,
    PYTHON_SECURITY_RESULT_PATH_TRAVERSAL = -2,
    PYTHON_SECURITY_RESULT_FILE_TOO_LARGE = -3,
    PYTHON_SECURITY_RESULT_INVALID_SYNTAX = -4,
    PYTHON_SECURITY_RESULT_FORBIDDEN_IMPORT = -5,
    PYTHON_SECURITY_RESULT_FORBIDDEN_FUNCTION = -6,
    PYTHON_SECURITY_RESULT_TIMEOUT = -7,
    PYTHON_SECURITY_RESULT_MEMORY_LIMIT = -8,
    PYTHON_SECURITY_RESULT_CPU_LIMIT = -9,
    PYTHON_SECURITY_RESULT_SANDBOX_VIOLATION = -10
} python_security_result_t;

// Security context
typedef struct python_security_context {
    bool enabled;
    bool strict_mode;
    
    // Path validation
    char **allowed_directories;
    size_t allowed_directories_count;
    char **forbidden_paths;
    size_t forbidden_paths_count;
    
    // Code validation
    char **allowed_imports;
    size_t allowed_imports_count;
    char **forbidden_imports;
    size_t forbidden_imports_count;
    char **forbidden_functions;
    size_t forbidden_functions_count;
    
    // Resource limits
    uint64_t max_code_size;
    uint32_t max_execution_time_sec;
    uint32_t max_memory_mb;
    uint32_t max_cpu_percent;
    
    // Sandbox settings
    bool enable_sandbox;
    bool allow_file_io;
    bool allow_network_io;
    bool allow_subprocess;
    bool allow_eval_exec;
    
    // Monitoring
    bool enable_monitoring;
    bool log_security_events;
    
} python_security_context_t;

// === Security Initialization ===

/**
 * @brief Initialize Python security subsystem
 * @return 0 on success, negative on error
 */
int python_security_init(void);

/**
 * @brief Cleanup Python security subsystem
 */
void python_security_deinit(void);

/**
 * @brief Get default security context
 * @return Default security context
 */
python_security_context_t* python_security_get_default_context(void);

/**
 * @brief Create security context from configuration
 * @param config_section Configuration section name
 * @return Security context or NULL on error
 */
python_security_context_t* python_security_create_context_from_config(const char *config_section);

/**
 * @brief Free security context
 * @param ctx Security context to free
 */
void python_security_free_context(python_security_context_t *ctx);

// === Path Validation ===

/**
 * @brief Validate and sanitize file path
 * @param path File path to validate
 * @param ctx Security context
 * @param sanitized_path Buffer for sanitized path
 * @param sanitized_path_size Size of sanitized path buffer
 * @return python_security_result_t
 */
python_security_result_t python_security_validate_path(const char *path,
                                                       python_security_context_t *ctx,
                                                       char *sanitized_path,
                                                       size_t sanitized_path_size);

/**
 * @brief Check for directory traversal attack
 * @param path File path to check
 * @return true if path contains traversal attempt
 */
bool python_security_is_path_traversal(const char *path);

/**
 * @brief Get canonical path (resolve symlinks, etc.)
 * @param path Input path
 * @param canonical_path Buffer for canonical path
 * @param canonical_path_size Size of buffer
 * @return 0 on success, negative on error
 */
int python_security_get_canonical_path(const char *path, char *canonical_path, size_t canonical_path_size);

/**
 * @brief Check if path is within allowed directories
 * @param path Path to check
 * @param ctx Security context
 * @return true if path is allowed
 */
bool python_security_is_path_allowed(const char *path, python_security_context_t *ctx);

// === Code Validation ===

/**
 * @brief Validate Python code for security
 * @param code Python code to validate
 * @param code_size Size of code
 * @param ctx Security context
 * @return python_security_result_t
 */
python_security_result_t python_security_validate_code(const char *code,
                                                       size_t code_size,
                                                       python_security_context_t *ctx);

/**
 * @brief Check for forbidden imports in code
 * @param code Python code to check
 * @param ctx Security context
 * @return true if forbidden imports found
 */
bool python_security_has_forbidden_imports(const char *code, python_security_context_t *ctx);

/**
 * @brief Check for forbidden functions in code
 * @param code Python code to check
 * @param ctx Security context
 * @return true if forbidden functions found
 */
bool python_security_has_forbidden_functions(const char *code, python_security_context_t *ctx);

/**
 * @brief Validate Python syntax
 * @param code Python code to validate
 * @param error_buffer Buffer for error message
 * @param error_buffer_size Size of error buffer
 * @return true if syntax is valid
 */
bool python_security_validate_syntax(const char *code, char *error_buffer, size_t error_buffer_size);

// === Sandboxing ===

/**
 * @brief Setup Python sandbox environment
 * @param ctx Security context
 * @return 0 on success, negative on error
 */
int python_security_setup_sandbox(python_security_context_t *ctx);

/**
 * @brief Execute Python code in sandbox
 * @param code Python code to execute
 * @param ctx Security context
 * @param result_buffer Buffer for execution result
 * @param result_buffer_size Size of result buffer
 * @return python_security_result_t
 */
python_security_result_t python_security_execute_sandboxed(const char *code,
                                                           python_security_context_t *ctx,
                                                           char *result_buffer,
                                                           size_t result_buffer_size);

/**
 * @brief Load Python file in sandbox
 * @param file_path Path to Python file
 * @param ctx Security context
 * @return python_security_result_t
 */
python_security_result_t python_security_load_file_sandboxed(const char *file_path,
                                                             python_security_context_t *ctx);

// === Resource Monitoring ===

/**
 * @brief Start resource monitoring for Python execution
 * @param ctx Security context
 * @return Monitor handle or NULL on error
 */
void* python_security_start_monitoring(python_security_context_t *ctx);

/**
 * @brief Stop resource monitoring
 * @param monitor_handle Monitor handle from start_monitoring
 * @return 0 on success, negative if limits exceeded
 */
int python_security_stop_monitoring(void *monitor_handle);

/**
 * @brief Check if resource limits are exceeded
 * @param monitor_handle Monitor handle
 * @return true if limits exceeded
 */
bool python_security_are_limits_exceeded(void *monitor_handle);

// === Audit Logging ===

/**
 * @brief Log security event
 * @param level Log level
 * @param event_type Event type
 * @param message Event message
 * @param ... Format arguments
 */
void python_security_log_event(int level, const char *event_type, const char *message, ...);

/**
 * @brief Log security violation
 * @param violation_type Type of violation
 * @param path File path (if applicable)
 * @param details Additional details
 */
void python_security_log_violation(const char *violation_type, const char *path, const char *details);

// === Configuration ===

/**
 * @brief Load security configuration from file
 * @param config_file Path to configuration file
 * @return Security context or NULL on error
 */
python_security_context_t* python_security_load_config(const char *config_file);

/**
 * @brief Save security configuration to file
 * @param ctx Security context
 * @param config_file Path to configuration file
 * @return 0 on success, negative on error
 */
int python_security_save_config(python_security_context_t *ctx, const char *config_file);

// === Utility Functions ===

/**
 * @brief Get security result string
 * @param result Security result code
 * @return Human-readable string
 */
const char* python_security_result_to_string(python_security_result_t result);

/**
 * @brief Check if security is enabled
 * @return true if security subsystem is enabled
 */
bool python_security_is_enabled(void);

/**
 * @brief Get security statistics
 * @param stats_buffer Buffer for statistics
 * @param stats_buffer_size Size of buffer
 * @return 0 on success, negative on error
 */
int python_security_get_stats(char *stats_buffer, size_t stats_buffer_size);

// === Default Security Policies ===

// Default allowed imports (whitelist)
extern const char* PYTHON_SECURITY_DEFAULT_ALLOWED_IMPORTS[];

// Default forbidden imports (blacklist)
extern const char* PYTHON_SECURITY_DEFAULT_FORBIDDEN_IMPORTS[];

// Default forbidden functions (blacklist)
extern const char* PYTHON_SECURITY_DEFAULT_FORBIDDEN_FUNCTIONS[];

#ifdef __cplusplus
}
#endif 