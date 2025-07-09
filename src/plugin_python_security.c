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

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/stat.h>
#include <sys/resource.h>
#include <signal.h>
#include <errno.h>
#include <pthread.h>
#include <Python.h>
#include <dap_common.h>
#include <dap_config.h>
#include <dap_strfuncs.h>
#include <dap_file_utils.h>
#include "plugin_python_security.h"

#define LOG_TAG "python-security"

// Global security state
static bool s_security_initialized = false;
static python_security_context_t *s_default_context = NULL;
static pthread_mutex_t s_security_mutex = PTHREAD_MUTEX_INITIALIZER;

// Security statistics
static struct {
    uint64_t total_validations;
    uint64_t blocked_attempts;
    uint64_t path_traversal_attempts;
    uint64_t code_violations;
    uint64_t resource_violations;
} s_security_stats = {0};

// Default security policies
const char* PYTHON_SECURITY_DEFAULT_ALLOWED_IMPORTS[] = {
    "sys",
    "os",
    "json",
    "time",
    "datetime",
    "hashlib",
    "hmac",
    "base64",
    "uuid",
    "re",
    "math",
    "random",
    "struct",
    "collections",
    "itertools",
    "functools",
    "cellframe",
    "dap",
    NULL
};

const char* PYTHON_SECURITY_DEFAULT_FORBIDDEN_IMPORTS[] = {
    "subprocess",
    "os.system",
    "eval",
    "exec",
    "compile",
    "__import__",
    "importlib",
    "ctypes",
    "socket",
    "urllib",
    "requests",
    "ftplib",
    "smtplib",
    "telnetlib",
    "multiprocessing",
    "threading",
    "asyncio",
    "_thread",
    "pickle",
    "marshal",
    "shelve",
    "dbm",
    "sqlite3",
    "tempfile",
    "shutil",
    "glob",
    "platform",
    "getpass",
    "pwd",
    "grp",
    "fcntl",
    "termios",
    "tty",
    "pty",
    "pipes",
    "posix",
    "nt",
    "mmap",
    "resource",
    "gc",
    "weakref",
    "imp",
    "zipimport",
    "runpy",
    "code",
    "codeop",
    "py_compile",
    "compileall",
    "dis",
    "inspect",
    "types",
    "site",
    NULL
};

const char* PYTHON_SECURITY_DEFAULT_FORBIDDEN_FUNCTIONS[] = {
    "eval",
    "exec",
    "compile",
    "open",
    "__import__",
    "globals",
    "locals",
    "vars",
    "dir",
    "hasattr",
    "getattr",
    "setattr",
    "delattr",
    "callable",
    "isinstance",
    "issubclass",
    "super",
    "classmethod",
    "staticmethod",
    "property",
    "input",
    "raw_input",
    "reload",
    "execfile",
    NULL
};

// === Internal Functions ===

/**
 * @brief Safe string copy with bounds checking
 */
static int safe_strcpy(char *dest, size_t dest_size, const char *src)
{
    if (!dest || !src || dest_size == 0) {
        return -1;
    }
    
    size_t src_len = strlen(src);
    if (src_len >= dest_size) {
        return -1;
    }
    
    memcpy(dest, src, src_len);
    dest[src_len] = '\0';
    return 0;
}

/**
 * @brief Check if string is in array
 */
static bool is_string_in_array(const char *str, const char **array)
{
    if (!str || !array) {
        return false;
    }
    
    for (size_t i = 0; array[i] != NULL; i++) {
        if (strcmp(str, array[i]) == 0) {
            return true;
        }
    }
    return false;
}

/**
 * @brief Read file content safely
 */
static char* read_file_safe(const char *path, size_t max_size, size_t *out_size)
{
    FILE *file = fopen(path, "rb");
    if (!file) {
        python_security_log_event(L_ERROR, "FILE_READ_ERROR", "Cannot open file: %s", path);
        return NULL;
    }
    
    // Get file size
    fseek(file, 0, SEEK_END);
    long file_size = ftell(file);
    fseek(file, 0, SEEK_SET);
    
    if (file_size < 0 || (size_t)file_size > max_size) {
        python_security_log_event(L_WARNING, "FILE_SIZE_VIOLATION", 
                                 "File too large: %s (%ld bytes, max %zu)", 
                                 path, file_size, max_size);
        fclose(file);
        return NULL;
    }
    
    char *content = DAP_NEW_Z_SIZE(char, file_size + 1);
    if (!content) {
        fclose(file);
        return NULL;
    }
    
    size_t read_size = fread(content, 1, file_size, file);
    fclose(file);
    
    if (read_size != (size_t)file_size) {
        DAP_DELETE(content);
        return NULL;
    }
    
    content[file_size] = '\0';
    if (out_size) {
        *out_size = file_size;
    }
    
    return content;
}

// === Security Initialization ===

int python_security_init(void)
{
    pthread_mutex_lock(&s_security_mutex);
    
    if (s_security_initialized) {
        pthread_mutex_unlock(&s_security_mutex);
        return 0;
    }
    
    log_it(L_INFO, "Initializing Python security subsystem");
    
    // Create default security context
    s_default_context = DAP_NEW_Z(python_security_context_t);
    if (!s_default_context) {
        pthread_mutex_unlock(&s_security_mutex);
        return -1;
    }
    
    // Set default security settings
    s_default_context->enabled = true;
    s_default_context->strict_mode = true;
    s_default_context->max_code_size = PYTHON_SECURITY_MAX_CODE_SIZE;
    s_default_context->max_execution_time_sec = PYTHON_SECURITY_MAX_EXECUTION_TIME;
    s_default_context->max_memory_mb = PYTHON_SECURITY_MAX_MEMORY_MB;
    s_default_context->max_cpu_percent = PYTHON_SECURITY_MAX_CPU_PERCENT;
    
    // Sandbox settings
    s_default_context->enable_sandbox = true;
    s_default_context->allow_file_io = false;
    s_default_context->allow_network_io = false;
    s_default_context->allow_subprocess = false;
    s_default_context->allow_eval_exec = false;
    
    // Monitoring
    s_default_context->enable_monitoring = true;
    s_default_context->log_security_events = true;
    
    s_security_initialized = true;
    pthread_mutex_unlock(&s_security_mutex);
    
    log_it(L_INFO, "Python security subsystem initialized");
    return 0;
}

void python_security_deinit(void)
{
    pthread_mutex_lock(&s_security_mutex);
    
    if (!s_security_initialized) {
        pthread_mutex_unlock(&s_security_mutex);
        return;
    }
    
    log_it(L_INFO, "Deinitializing Python security subsystem");
    
    if (s_default_context) {
        python_security_free_context(s_default_context);
        s_default_context = NULL;
    }
    
    s_security_initialized = false;
    pthread_mutex_unlock(&s_security_mutex);
    
    log_it(L_INFO, "Python security subsystem deinitialized");
}

python_security_context_t* python_security_get_default_context(void)
{
    return s_default_context;
}

void python_security_free_context(python_security_context_t *ctx)
{
    if (!ctx) {
        return;
    }
    
    // Free arrays
    if (ctx->allowed_directories) {
        for (size_t i = 0; i < ctx->allowed_directories_count; i++) {
            DAP_DELETE(ctx->allowed_directories[i]);
        }
        DAP_DELETE(ctx->allowed_directories);
    }
    
    if (ctx->forbidden_paths) {
        for (size_t i = 0; i < ctx->forbidden_paths_count; i++) {
            DAP_DELETE(ctx->forbidden_paths[i]);
        }
        DAP_DELETE(ctx->forbidden_paths);
    }
    
    if (ctx->allowed_imports) {
        for (size_t i = 0; i < ctx->allowed_imports_count; i++) {
            DAP_DELETE(ctx->allowed_imports[i]);
        }
        DAP_DELETE(ctx->allowed_imports);
    }
    
    if (ctx->forbidden_imports) {
        for (size_t i = 0; i < ctx->forbidden_imports_count; i++) {
            DAP_DELETE(ctx->forbidden_imports[i]);
        }
        DAP_DELETE(ctx->forbidden_imports);
    }
    
    if (ctx->forbidden_functions) {
        for (size_t i = 0; i < ctx->forbidden_functions_count; i++) {
            DAP_DELETE(ctx->forbidden_functions[i]);
        }
        DAP_DELETE(ctx->forbidden_functions);
    }
    
    DAP_DELETE(ctx);
}

// === Path Validation ===

python_security_result_t python_security_validate_path(const char *path,
                                                       python_security_context_t *ctx,
                                                       char *sanitized_path,
                                                       size_t sanitized_path_size)
{
    if (!path || !ctx || !sanitized_path || sanitized_path_size == 0) {
        return PYTHON_SECURITY_RESULT_INVALID_PATH;
    }
    
    s_security_stats.total_validations++;
    
    // Check path length
    size_t path_len = strlen(path);
    if (path_len == 0 || path_len >= PYTHON_SECURITY_MAX_PATH_LENGTH) {
        s_security_stats.blocked_attempts++;
        python_security_log_violation("PATH_LENGTH", path, "Path too long or empty");
        return PYTHON_SECURITY_RESULT_INVALID_PATH;
    }
    
    // Check for directory traversal
    if (python_security_is_path_traversal(path)) {
        s_security_stats.path_traversal_attempts++;
        s_security_stats.blocked_attempts++;
        python_security_log_violation("PATH_TRAVERSAL", path, "Directory traversal attempt detected");
        return PYTHON_SECURITY_RESULT_PATH_TRAVERSAL;
    }
    
    // Get canonical path
    char canonical_path[PATH_MAX];
    if (python_security_get_canonical_path(path, canonical_path, sizeof(canonical_path)) != 0) {
        s_security_stats.blocked_attempts++;
        python_security_log_violation("PATH_CANONICAL", path, "Cannot resolve canonical path");
        return PYTHON_SECURITY_RESULT_INVALID_PATH;
    }
    
    // Check if path is allowed
    if (!python_security_is_path_allowed(canonical_path, ctx)) {
        s_security_stats.blocked_attempts++;
        python_security_log_violation("PATH_NOT_ALLOWED", canonical_path, "Path not in allowed directories");
        return PYTHON_SECURITY_RESULT_INVALID_PATH;
    }
    
    // Copy sanitized path
    if (safe_strcpy(sanitized_path, sanitized_path_size, canonical_path) != 0) {
        return PYTHON_SECURITY_RESULT_INVALID_PATH;
    }
    
    return PYTHON_SECURITY_RESULT_OK;
}

bool python_security_is_path_traversal(const char *path)
{
    if (!path) {
        return false;
    }
    
    // Check for obvious traversal patterns
    if (strstr(path, "../") != NULL ||
        strstr(path, "..\\") != NULL ||
        strstr(path, "/..") != NULL ||
        strstr(path, "\\..") != NULL) {
        return true;
    }
    
    // Check for encoded traversal patterns
    if (strstr(path, "%2e%2e") != NULL ||
        strstr(path, "%2E%2E") != NULL ||
        strstr(path, "..%2f") != NULL ||
        strstr(path, "..%2F") != NULL) {
        return true;
    }
    
    // Check for double encoded
    if (strstr(path, "%252e") != NULL ||
        strstr(path, "%252E") != NULL) {
        return true;
    }
    
    return false;
}

int python_security_get_canonical_path(const char *path, char *canonical_path, size_t canonical_path_size)
{
    if (!path || !canonical_path || canonical_path_size == 0) {
        return -1;
    }
    
    char *resolved = realpath(path, NULL);
    if (!resolved) {
        // If file doesn't exist, try to resolve the directory part
        char dir_path[PATH_MAX];
        char file_name[PATH_MAX];
        
        // Split path into directory and filename
        const char *last_slash = strrchr(path, '/');
        if (last_slash) {
            size_t dir_len = last_slash - path;
            if (dir_len >= sizeof(dir_path)) {
                return -1;
            }
            memcpy(dir_path, path, dir_len);
            dir_path[dir_len] = '\0';
            safe_strcpy(file_name, sizeof(file_name), last_slash + 1);
        } else {
            safe_strcpy(dir_path, sizeof(dir_path), ".");
            safe_strcpy(file_name, sizeof(file_name), path);
        }
        
        char *resolved_dir = realpath(dir_path, NULL);
        if (!resolved_dir) {
            return -1;
        }
        
        // Reconstruct path
        int ret = snprintf(canonical_path, canonical_path_size, "%s/%s", resolved_dir, file_name);
        free(resolved_dir);
        
        if (ret < 0 || (size_t)ret >= canonical_path_size) {
            return -1;
        }
        return 0;
    }
    
    size_t resolved_len = strlen(resolved);
    if (resolved_len >= canonical_path_size) {
        free(resolved);
        return -1;
    }
    
    memcpy(canonical_path, resolved, resolved_len + 1);
    free(resolved);
    return 0;
}

bool python_security_is_path_allowed(const char *path, python_security_context_t *ctx)
{
    if (!path || !ctx) {
        return false;
    }
    
    // If no allowed directories specified, allow any path
    if (!ctx->allowed_directories || ctx->allowed_directories_count == 0) {
        return true;
    }
    
    // Check against allowed directories
    for (size_t i = 0; i < ctx->allowed_directories_count; i++) {
        if (strncmp(path, ctx->allowed_directories[i], strlen(ctx->allowed_directories[i])) == 0) {
            return true;
        }
    }
    
    return false;
}

// === Code Validation ===

python_security_result_t python_security_validate_code(const char *code,
                                                       size_t code_size,
                                                       python_security_context_t *ctx)
{
    if (!code || !ctx || code_size == 0) {
        return PYTHON_SECURITY_RESULT_INVALID_SYNTAX;
    }
    
    s_security_stats.total_validations++;
    
    // Check code size
    if (code_size > ctx->max_code_size) {
        s_security_stats.blocked_attempts++;
        python_security_log_violation("CODE_SIZE", NULL, "Code too large: %zu bytes", code_size);
        return PYTHON_SECURITY_RESULT_FILE_TOO_LARGE;
    }
    
    // Validate syntax
    char error_buffer[1024];
    if (!python_security_validate_syntax(code, error_buffer, sizeof(error_buffer))) {
        s_security_stats.code_violations++;
        s_security_stats.blocked_attempts++;
        python_security_log_violation("SYNTAX_ERROR", NULL, "Invalid Python syntax: %s", error_buffer);
        return PYTHON_SECURITY_RESULT_INVALID_SYNTAX;
    }
    
    // Check for forbidden imports
    if (python_security_has_forbidden_imports(code, ctx)) {
        s_security_stats.code_violations++;
        s_security_stats.blocked_attempts++;
        python_security_log_violation("FORBIDDEN_IMPORT", NULL, "Forbidden import detected");
        return PYTHON_SECURITY_RESULT_FORBIDDEN_IMPORT;
    }
    
    // Check for forbidden functions
    if (python_security_has_forbidden_functions(code, ctx)) {
        s_security_stats.code_violations++;
        s_security_stats.blocked_attempts++;
        python_security_log_violation("FORBIDDEN_FUNCTION", NULL, "Forbidden function detected");
        return PYTHON_SECURITY_RESULT_FORBIDDEN_FUNCTION;
    }
    
    return PYTHON_SECURITY_RESULT_OK;
}

bool python_security_has_forbidden_imports(const char *code, python_security_context_t *ctx)
{
    if (!code || !ctx) {
        return false;
    }
    
    // Check against forbidden imports
    for (size_t i = 0; PYTHON_SECURITY_DEFAULT_FORBIDDEN_IMPORTS[i] != NULL; i++) {
        const char *forbidden = PYTHON_SECURITY_DEFAULT_FORBIDDEN_IMPORTS[i];
        
        // Check for "import forbidden_module"
        char import_pattern[256];
        snprintf(import_pattern, sizeof(import_pattern), "import %s", forbidden);
        if (strstr(code, import_pattern) != NULL) {
            return true;
        }
        
        // Check for "from forbidden_module import"
        snprintf(import_pattern, sizeof(import_pattern), "from %s import", forbidden);
        if (strstr(code, import_pattern) != NULL) {
            return true;
        }
    }
    
    return false;
}

bool python_security_has_forbidden_functions(const char *code, python_security_context_t *ctx)
{
    if (!code || !ctx) {
        return false;
    }
    
    // Check against forbidden functions
    for (size_t i = 0; PYTHON_SECURITY_DEFAULT_FORBIDDEN_FUNCTIONS[i] != NULL; i++) {
        const char *forbidden = PYTHON_SECURITY_DEFAULT_FORBIDDEN_FUNCTIONS[i];
        
        // Check for direct function calls
        char call_pattern[256];
        snprintf(call_pattern, sizeof(call_pattern), "%s(", forbidden);
        if (strstr(code, call_pattern) != NULL) {
            return true;
        }
    }
    
    return false;
}

bool python_security_validate_syntax(const char *code, char *error_buffer, size_t error_buffer_size)
{
    if (!code || !error_buffer) {
        return false;
    }
    
    // Compile code to check syntax
    PyObject *compiled = Py_CompileString(code, "<security_check>", Py_file_input);
    if (!compiled) {
        if (PyErr_Occurred()) {
            PyObject *type, *value, *traceback;
            PyErr_Fetch(&type, &value, &traceback);
            
            if (value) {
                PyObject *str = PyObject_Str(value);
                if (str) {
                    const char *error_str = PyUnicode_AsUTF8(str);
                    if (error_str) {
                        safe_strcpy(error_buffer, error_buffer_size, error_str);
                    }
                    Py_DECREF(str);
                }
            }
            
            Py_XDECREF(type);
            Py_XDECREF(value);
            Py_XDECREF(traceback);
        }
        return false;
    }
    
    Py_DECREF(compiled);
    return true;
}

// === Secure Plugin Loading ===

python_security_result_t python_security_load_file_sandboxed(const char *file_path,
                                                             python_security_context_t *ctx)
{
    if (!file_path || !ctx) {
        return PYTHON_SECURITY_RESULT_INVALID_PATH;
    }
    
    python_security_log_event(L_INFO, "SECURE_LOAD", "Loading Python file: %s", file_path);
    
    // Validate path
    char sanitized_path[PATH_MAX];
    python_security_result_t path_result = python_security_validate_path(file_path, ctx, 
                                                                         sanitized_path, sizeof(sanitized_path));
    if (path_result != PYTHON_SECURITY_RESULT_OK) {
        return path_result;
    }
    
    // Read file content
    size_t code_size;
    char *code = read_file_safe(sanitized_path, ctx->max_code_size, &code_size);
    if (!code) {
        return PYTHON_SECURITY_RESULT_FILE_TOO_LARGE;
    }
    
    // Validate code
    python_security_result_t code_result = python_security_validate_code(code, code_size, ctx);
    if (code_result != PYTHON_SECURITY_RESULT_OK) {
        DAP_DELETE(code);
        return code_result;
    }
    
    // Execute in sandbox
    char result_buffer[1024];
    python_security_result_t exec_result = python_security_execute_sandboxed(code, ctx, 
                                                                             result_buffer, sizeof(result_buffer));
    
    DAP_DELETE(code);
    
    if (exec_result == PYTHON_SECURITY_RESULT_OK) {
        python_security_log_event(L_INFO, "SECURE_LOAD_SUCCESS", "Successfully loaded: %s", file_path);
    } else {
        python_security_log_event(L_ERROR, "SECURE_LOAD_FAILED", "Failed to load: %s, error: %s", 
                                 file_path, python_security_result_to_string(exec_result));
    }
    
    return exec_result;
}

python_security_result_t python_security_execute_sandboxed(const char *code,
                                                           python_security_context_t *ctx,
                                                           char *result_buffer,
                                                           size_t result_buffer_size)
{
    if (!code || !ctx) {
        return PYTHON_SECURITY_RESULT_INVALID_SYNTAX;
    }
    
    // Setup sandbox
    if (python_security_setup_sandbox(ctx) != 0) {
        return PYTHON_SECURITY_RESULT_SANDBOX_VIOLATION;
    }
    
    // Start resource monitoring
    void *monitor = python_security_start_monitoring(ctx);
    
    // Execute code
    int exec_result = PyRun_SimpleString(code);
    
    // Check resource limits
    int monitor_result = python_security_stop_monitoring(monitor);
    
    if (monitor_result != 0) {
        if (python_security_are_limits_exceeded(monitor)) {
            s_security_stats.resource_violations++;
            return PYTHON_SECURITY_RESULT_CPU_LIMIT; // Or memory/timeout
        }
    }
    
    if (exec_result != 0) {
        return PYTHON_SECURITY_RESULT_SANDBOX_VIOLATION;
    }
    
    if (result_buffer && result_buffer_size > 0) {
        safe_strcpy(result_buffer, result_buffer_size, "OK");
    }
    
    return PYTHON_SECURITY_RESULT_OK;
}

// === Monitoring Functions ===

typedef struct {
    time_t start_time;
    uint32_t max_execution_time;
    uint32_t max_memory_mb;
    bool limits_exceeded;
} python_security_monitor_t;

void* python_security_start_monitoring(python_security_context_t *ctx)
{
    if (!ctx || !ctx->enable_monitoring) {
        return NULL;
    }
    
    python_security_monitor_t *monitor = DAP_NEW_Z(python_security_monitor_t);
    if (!monitor) {
        return NULL;
    }
    
    monitor->start_time = time(NULL);
    monitor->max_execution_time = ctx->max_execution_time_sec;
    monitor->max_memory_mb = ctx->max_memory_mb;
    monitor->limits_exceeded = false;
    
    return monitor;
}

int python_security_stop_monitoring(void *monitor_handle)
{
    if (!monitor_handle) {
        return 0;
    }
    
    python_security_monitor_t *monitor = (python_security_monitor_t*)monitor_handle;
    
    // Check execution time
    time_t current_time = time(NULL);
    if (current_time - monitor->start_time > monitor->max_execution_time) {
        monitor->limits_exceeded = true;
    }
    
    int result = monitor->limits_exceeded ? -1 : 0;
    DAP_DELETE(monitor);
    return result;
}

bool python_security_are_limits_exceeded(void *monitor_handle)
{
    if (!monitor_handle) {
        return false;
    }
    
    python_security_monitor_t *monitor = (python_security_monitor_t*)monitor_handle;
    return monitor->limits_exceeded;
}

// === Sandbox Setup ===

int python_security_setup_sandbox(python_security_context_t *ctx)
{
    if (!ctx || !ctx->enable_sandbox) {
        return 0;
    }
    
    // Restrict builtins
    PyRun_SimpleString("import builtins");
    
    if (!ctx->allow_eval_exec) {
        PyRun_SimpleString("builtins.eval = None");
        PyRun_SimpleString("builtins.exec = None");
        PyRun_SimpleString("builtins.compile = None");
        PyRun_SimpleString("builtins.__import__ = None");
    }
    
    if (!ctx->allow_file_io) {
        PyRun_SimpleString("builtins.open = None");
    }
    
    return 0;
}

// === Utility Functions ===

const char* python_security_result_to_string(python_security_result_t result)
{
    switch (result) {
        case PYTHON_SECURITY_RESULT_OK: return "OK";
        case PYTHON_SECURITY_RESULT_INVALID_PATH: return "Invalid path";
        case PYTHON_SECURITY_RESULT_PATH_TRAVERSAL: return "Path traversal attempt";
        case PYTHON_SECURITY_RESULT_FILE_TOO_LARGE: return "File too large";
        case PYTHON_SECURITY_RESULT_INVALID_SYNTAX: return "Invalid syntax";
        case PYTHON_SECURITY_RESULT_FORBIDDEN_IMPORT: return "Forbidden import";
        case PYTHON_SECURITY_RESULT_FORBIDDEN_FUNCTION: return "Forbidden function";
        case PYTHON_SECURITY_RESULT_TIMEOUT: return "Execution timeout";
        case PYTHON_SECURITY_RESULT_MEMORY_LIMIT: return "Memory limit exceeded";
        case PYTHON_SECURITY_RESULT_CPU_LIMIT: return "CPU limit exceeded";
        case PYTHON_SECURITY_RESULT_SANDBOX_VIOLATION: return "Sandbox violation";
        default: return "Unknown error";
    }
}

bool python_security_is_enabled(void)
{
    return s_security_initialized && s_default_context && s_default_context->enabled;
}

void python_security_log_event(int level, const char *event_type, const char *message, ...)
{
    if (!s_security_initialized || !s_default_context || !s_default_context->log_security_events) {
        return;
    }
    
    va_list args;
    va_start(args, message);
    
    char formatted_message[2048];
    vsnprintf(formatted_message, sizeof(formatted_message), message, args);
    
    log_it(level, "[SECURITY][%s] %s", event_type, formatted_message);
    
    va_end(args);
}

void python_security_log_violation(const char *violation_type, const char *path, const char *details)
{
    python_security_log_event(L_WARNING, "SECURITY_VIOLATION", 
                              "Type: %s, Path: %s, Details: %s", 
                              violation_type, path ? path : "N/A", details);
}

int python_security_get_stats(char *stats_buffer, size_t stats_buffer_size)
{
    if (!stats_buffer || stats_buffer_size == 0) {
        return -1;
    }
    
    return snprintf(stats_buffer, stats_buffer_size,
                   "Security Statistics:\n"
                   "  Total validations: %lu\n"
                   "  Blocked attempts: %lu\n"
                   "  Path traversal attempts: %lu\n"
                   "  Code violations: %lu\n"
                   "  Resource violations: %lu\n",
                   s_security_stats.total_validations,
                   s_security_stats.blocked_attempts,
                   s_security_stats.path_traversal_attempts,
                   s_security_stats.code_violations,
                   s_security_stats.resource_violations);
} 