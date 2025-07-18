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
#include <dirent.h>
#include <sys/stat.h>
#include <limits.h>
#include <errno.h>
#include <Python.h>
#include <dap_common.h>
#include <dap_strfuncs.h>
#include <dap_file_utils.h>
#include <dap_config.h>
#include "plugin_python_init.h"
#include "plugin_python_security.h"

#define LOG_TAG "plugin-python-init-secure"

// Global state
static bool s_python_initialized = false;
static bool s_security_enabled = true;
static char s_last_error[2048] = {0};  // Increased buffer size
static python_security_context_t *s_security_context = NULL;

/**
 * @brief Set last error message safely
 * @param format Format string
 * @param ... Arguments
 */
static void set_last_error_secure(const char *format, ...)
{
    if (!format) {
        return;
    }
    
    va_list args;
    va_start(args, format);
    
    // Use vsnprintf for bounds checking
    int result = vsnprintf(s_last_error, sizeof(s_last_error) - 1, format, args);
    va_end(args);
    
    // Ensure null termination
    if (result > 0 && (size_t)result < sizeof(s_last_error)) {
        s_last_error[result] = '\0';
    } else {
        s_last_error[sizeof(s_last_error) - 1] = '\0';
    }
    
    // Log security event if it's a security-related error
    if (strstr(format, "security") || strstr(format, "violation") || strstr(format, "forbidden")) {
        python_security_log_event(L_WARNING, "SECURITY_ERROR", "%s", s_last_error);
    }
}

/**
 * @brief Validate configuration parameter securely
 * @param value Configuration value to validate
 * @param param_name Parameter name for logging
 * @return true if valid, false otherwise
 */
static bool validate_config_parameter(const char *value, const char *param_name)
{
    if (!value || !param_name) {
        return false;
    }
    
    size_t value_len = strlen(value);
    
    // Check for null or empty values
    if (value_len == 0) {
        set_last_error_secure("Configuration parameter '%s' is empty", param_name);
        return false;
    }
    
    // Check for maximum length
    if (value_len >= PATH_MAX) {
        set_last_error_secure("Configuration parameter '%s' is too long (%zu bytes)", param_name, value_len);
        python_security_log_violation("CONFIG_PARAM_TOO_LONG", param_name, "Parameter exceeds maximum length");
        return false;
    }
    
    // Check for potential injection characters
    if (strstr(value, "../") || strstr(value, "..\\") ||
        strstr(value, ";") || strstr(value, "|") ||
        strstr(value, "&") || strstr(value, "`") ||
        strstr(value, "$") || strstr(value, "$(")) {
        set_last_error_secure("Configuration parameter '%s' contains suspicious characters", param_name);
        python_security_log_violation("CONFIG_INJECTION_ATTEMPT", param_name, value);
        return false;
    }
    
    return true;
}

/**
 * @brief Validate directory path securely
 * @param path Directory path to validate
 * @param param_name Parameter name for logging
 * @return true if valid, false otherwise
 */
static bool validate_directory_path(const char *path, const char *param_name)
{
    if (!validate_config_parameter(path, param_name)) {
        return false;
    }
    
    // Get canonical path to prevent directory traversal
    char canonical_path[PATH_MAX];
    if (python_security_get_canonical_path(path, canonical_path, sizeof(canonical_path)) != 0) {
        set_last_error_secure("Cannot resolve canonical path for '%s': %s", param_name, path);
        return false;
    }
    
    // Check if directory exists or can be created
    struct stat st;
    if (stat(canonical_path, &st) == 0) {
        // Directory exists, check if it's actually a directory
        if (!S_ISDIR(st.st_mode)) {
            set_last_error_secure("Path '%s' exists but is not a directory", canonical_path);
            return false;
        }
        
        // Check permissions
        if (access(canonical_path, R_OK | W_OK) != 0) {
            set_last_error_secure("Insufficient permissions for directory '%s'", canonical_path);
            return false;
        }
    } else {
        // Directory doesn't exist, check if parent exists and is writable
        char parent_path[PATH_MAX];
        char *last_slash = strrchr(canonical_path, '/');
        if (last_slash) {
            size_t parent_len = last_slash - canonical_path;
            if (parent_len >= sizeof(parent_path)) {
                set_last_error_secure("Parent path too long for '%s'", canonical_path);
                return false;
            }
            memcpy(parent_path, canonical_path, parent_len);
            parent_path[parent_len] = '\0';
            
            if (access(parent_path, W_OK) != 0) {
                set_last_error_secure("Cannot create directory '%s': parent not writable", canonical_path);
                return false;
            }
        }
    }
    
    return true;
}

/**
 * @brief Initialize Python interpreter securely
 * @param python_path Path to Python installation
 * @return 0 on success, negative value on error
 */
int python_interpreter_init_secure(const char *python_path)
{
    if (s_python_initialized) {
        log_it(L_WARNING, "Python interpreter already initialized");
        return 0;
    }
    
    log_it(L_INFO, "Initializing Python interpreter securely");
    
    // Initialize security subsystem first
    if (python_security_init() != 0) {
        set_last_error_secure("Failed to initialize Python security subsystem");
        return -1;
    }
    
    s_security_context = python_security_get_default_context();
    if (!s_security_context) {
        set_last_error_secure("Failed to get security context");
        python_security_deinit();
        return -2;
    }
    
    // Validate python_path if provided
    if (python_path && strlen(python_path) > 0) {
        if (!validate_directory_path(python_path, "python_path")) {
            python_security_deinit();
            return -3;
        }
        
        char *python_home = dap_strdup(python_path);
        if (python_home) {
            wchar_t *wide_path = Py_DecodeLocale(python_home, NULL);
            if (wide_path) {
                Py_SetPythonHome(wide_path);
                log_it(L_DEBUG, "Set Python home to: %s", python_home);
                PyMem_RawFree(wide_path);
            } else {
                log_it(L_ERROR, "Failed to decode Python path: %s", python_home);
                DAP_DELETE(python_home);
                set_last_error_secure("Failed to decode Python path");
                python_security_deinit();
                return -4;
            }
            DAP_DELETE(python_home);
        }
    }
    
    // Initialize Python
    Py_Initialize();
    if (!Py_IsInitialized()) {
        log_it(L_ERROR, "Failed to initialize Python interpreter");
        set_last_error_secure("Failed to initialize Python interpreter");
        python_security_deinit();
        return -5;
    }
    
    // Initialize thread support
    PyEval_InitThreads();
    
    // Setup Python path securely
    PyRun_SimpleString("import sys");
    
    // Only add current directory if security allows it
    if (s_security_context->allow_file_io) {
        PyRun_SimpleString("sys.path.insert(0, '.')");
    }
    
    // Add python_path to sys.path if specified and validated
    if (python_path && strlen(python_path) > 0) {
        // Use parameterized approach to prevent injection
        PyObject *sys_path = PySys_GetObject("path");
        if (sys_path) {
            PyObject *path_str = PyUnicode_FromString(python_path);
            if (path_str) {
                PyList_Insert(sys_path, 0, path_str);
                Py_DECREF(path_str);
            }
        }
    }
    
    // Setup security sandbox
    if (python_security_setup_sandbox(s_security_context) != 0) {
        log_it(L_ERROR, "Failed to setup Python security sandbox");
        Py_Finalize();
        python_security_deinit();
        return -6;
    }
    
    s_python_initialized = true;
    log_it(L_INFO, "Python interpreter initialized securely");
    
    return 0;
}

/**
 * @brief Load Python plugin securely
 * @param plugin_path Path to plugin file
 * @return 0 on success, negative value on error
 */
int python_plugin_load_secure(const char *plugin_path)
{
    if (!python_interpreter_is_initialized()) {
        log_it(L_ERROR, "Python interpreter not initialized");
        set_last_error_secure("Python interpreter not initialized");
        return -1;
    }
    
    if (!plugin_path || strlen(plugin_path) == 0) {
        log_it(L_ERROR, "Invalid plugin path");
        set_last_error_secure("Invalid plugin path");
        return -2;
    }
    
    log_it(L_INFO, "Loading Python plugin securely: %s", plugin_path);
    
    // Validate plugin path using security subsystem
    char sanitized_path[PATH_MAX];
    python_security_result_t path_result = python_security_validate_path(plugin_path, s_security_context,
                                                                         sanitized_path, sizeof(sanitized_path));
    if (path_result != PYTHON_SECURITY_RESULT_OK) {
        const char *error_msg = python_security_result_to_string(path_result);
        log_it(L_ERROR, "Plugin path validation failed: %s", error_msg);
        set_last_error_secure("Plugin path validation failed: %s", error_msg);
        return -3;
    }
    
    // Check if file exists and is readable
    if (access(sanitized_path, R_OK) != 0) {
        log_it(L_ERROR, "Plugin file not accessible: %s", sanitized_path);
        set_last_error_secure("Plugin file not accessible: %s", sanitized_path);
        return -4;
    }
    
    // Check file size
    struct stat st;
    if (stat(sanitized_path, &st) != 0) {
        log_it(L_ERROR, "Cannot stat plugin file: %s", sanitized_path);
        set_last_error_secure("Cannot stat plugin file: %s", sanitized_path);
        return -5;
    }
    
    if ((size_t)st.st_size > s_security_context->max_code_size) {
        log_it(L_ERROR, "Plugin file too large: %s (%ld bytes, max %lu)", 
               sanitized_path, st.st_size, s_security_context->max_code_size);
        set_last_error_secure("Plugin file too large: %s (%ld bytes, max %lu)", 
                              sanitized_path, st.st_size, s_security_context->max_code_size);
        python_security_log_violation("FILE_TOO_LARGE", sanitized_path, "Plugin file exceeds size limit");
        return -6;
    }
    
    // Load plugin using secure sandboxed execution
    python_security_result_t load_result = python_security_load_file_sandboxed(sanitized_path, s_security_context);
    if (load_result != PYTHON_SECURITY_RESULT_OK) {
        const char *error_msg = python_security_result_to_string(load_result);
        log_it(L_ERROR, "Failed to load plugin securely: %s", error_msg);
        set_last_error_secure("Failed to load plugin securely: %s", error_msg);
        return -7;
    }
    
    log_it(L_INFO, "Successfully loaded Python plugin securely: %s", sanitized_path);
    python_security_log_event(L_INFO, "PLUGIN_LOADED", "Plugin loaded successfully: %s", sanitized_path);
    
    return 0;
}

/**
 * @brief Load Python plugins from directory securely
 * @param plugins_dir Directory containing Python plugins
 * @return Number of loaded plugins or negative value on error
 */
int python_plugins_load_from_dir_secure(const char *plugins_dir)
{
    if (!python_interpreter_is_initialized()) {
        log_it(L_ERROR, "Python interpreter not initialized");
        set_last_error_secure("Python interpreter not initialized");
        return -1;
    }
    
    if (!plugins_dir || strlen(plugins_dir) == 0) {
        log_it(L_ERROR, "Invalid plugins directory");
        set_last_error_secure("Invalid plugins directory");
        return -2;
    }
    
    // Validate plugins directory
    if (!validate_directory_path(plugins_dir, "plugins_dir")) {
        return -3;
    }
    
    log_it(L_INFO, "Loading Python plugins from directory securely: %s", plugins_dir);
    
    DIR *dir = opendir(plugins_dir);
    if (!dir) {
        log_it(L_WARNING, "Failed to open plugins directory: %s (errno: %d)", plugins_dir, errno);
        return 0; // Not an error, just no plugins to load
    }
    
    int loaded_count = 0;
    int failed_count = 0;
    struct dirent *entry;
    
    while ((entry = readdir(dir)) != NULL) {
        // Skip hidden files and directories
        if (entry->d_name[0] == '.') {
            continue;
        }
        
        // Check for directory traversal in filename
        if (python_security_is_path_traversal(entry->d_name)) {
            log_it(L_WARNING, "Skipping suspicious filename: %s", entry->d_name);
            python_security_log_violation("FILENAME_TRAVERSAL", entry->d_name, "Suspicious filename detected");
            failed_count++;
            continue;
        }
        
        // Only process .py files
        const char *ext = strrchr(entry->d_name, '.');
        if (!ext || strcmp(ext, ".py") != 0) {
            continue;
        }
        
        // Validate filename length
        size_t filename_len = strlen(entry->d_name);
        if (filename_len == 0 || filename_len >= NAME_MAX) {
            log_it(L_WARNING, "Skipping invalid filename: %s", entry->d_name);
            failed_count++;
            continue;
        }
        
        // Build full path safely
        char plugin_path[PATH_MAX];
        int path_result = snprintf(plugin_path, sizeof(plugin_path), "%s/%s", plugins_dir, entry->d_name);
        if (path_result < 0 || (size_t)path_result >= sizeof(plugin_path)) {
            log_it(L_ERROR, "Plugin path too long: %s/%s", plugins_dir, entry->d_name);
            failed_count++;
            continue;
        }
        
        // Load plugin securely
        if (python_plugin_load_secure(plugin_path) == 0) {
            loaded_count++;
        } else {
            failed_count++;
        }
    }
    
    closedir(dir);
    
    log_it(L_INFO, "Plugin loading completed: %d successful, %d failed from directory: %s", 
           loaded_count, failed_count, plugins_dir);
    
    if (failed_count > 0) {
        python_security_log_event(L_WARNING, "PLUGIN_LOAD_FAILURES", 
                                 "Failed to load %d plugins from %s", failed_count, plugins_dir);
    }
    
    return loaded_count;
}

/**
 * @brief Get last error message
 * @return Last error message or NULL if no error
 */
const char *python_get_last_error_secure(void)
{
    return s_last_error[0] ? s_last_error : NULL;
}

/**
 * @brief Clear last error message
 */
void python_clear_last_error_secure(void)
{
    memset(s_last_error, 0, sizeof(s_last_error));
}

/**
 * @brief Check if security is enabled
 * @return true if security is enabled
 */
bool python_security_is_enabled_secure(void)
{
    return s_security_enabled && python_security_is_enabled();
}

/**
 * @brief Enable or disable security
 * @param enabled Security enabled state
 */
void python_security_set_enabled_secure(bool enabled)
{
    s_security_enabled = enabled;
    log_it(L_INFO, "Python security %s", enabled ? "enabled" : "disabled");
    
    if (!enabled) {
        python_security_log_event(L_WARNING, "SECURITY_DISABLED", "Python security has been disabled");
    }
}

/**
 * @brief Get security statistics
 * @return Security statistics string or NULL on error
 */
char* python_get_security_stats_secure(void)
{
    if (!python_security_is_enabled()) {
        return NULL;
    }
    
    char *stats_buffer = DAP_NEW_Z_SIZE(char, 2048);
    if (!stats_buffer) {
        return NULL;
    }
    
    if (python_security_get_stats(stats_buffer, 2048) < 0) {
        DAP_DELETE(stats_buffer);
        return NULL;
    }
    
    return stats_buffer;
}

/**
 * @brief Deinitialize Python interpreter securely
 */
void python_interpreter_deinit_secure(void)
{
    if (!s_python_initialized) {
        log_it(L_WARNING, "Python interpreter was not initialized");
        return;
    }
    
    log_it(L_INFO, "Deinitializing Python interpreter securely");
    
    // Finalize Python
    if (Py_IsInitialized()) {
        Py_Finalize();
    }
    
    // Cleanup security subsystem
    python_security_deinit();
    s_security_context = NULL;
    
    s_python_initialized = false;
    log_it(L_INFO, "Python interpreter deinitialized securely");
} 