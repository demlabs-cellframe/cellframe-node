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
#include <Python.h>
#include <dap_common.h>
#include <dap_strfuncs.h>
#include <dap_file_utils.h>
#include "plugin_python_init.h"

#define LOG_TAG "plugin-python-init"

// Global state
static bool s_python_initialized = false;
static char s_last_error[1024] = {0};

/**
 * @brief Set last error message
 * @param format Format string
 * @param ... Arguments
 */
static void set_last_error(const char *format, ...)
{
    va_list args;
    va_start(args, format);
    vsnprintf(s_last_error, sizeof(s_last_error), format, args);
    va_end(args);
}

/**
 * @brief Clear last error message
 */
void python_clear_last_error(void)
{
    memset(s_last_error, 0, sizeof(s_last_error));
}

/**
 * @brief Get last error message
 * @return Last error message or NULL if no error
 */
const char *python_get_last_error(void)
{
    return s_last_error[0] ? s_last_error : NULL;
}

/**
 * @brief Check if Python interpreter is initialized
 * @return true if initialized, false otherwise
 */
bool python_interpreter_is_initialized(void)
{
    return s_python_initialized && Py_IsInitialized();
}

/**
 * @brief Initialize Python interpreter
 * @param python_path Path to Python installation
 * @return 0 on success, negative value on error
 */
int python_interpreter_init(const char *python_path)
{
    if (s_python_initialized) {
        log_it(L_WARNING, "Python interpreter already initialized");
        return 0;
    }
    
    log_it(L_INFO, "Initializing Python interpreter with path: %s", python_path);
    
    // Set Python path
    if (python_path && strlen(python_path) > 0) {
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
                set_last_error("Failed to decode Python path");
                return -1;
            }
            DAP_DELETE(python_home);
        }
    }
    
    // Initialize Python
    Py_Initialize();
    if (!Py_IsInitialized()) {
        log_it(L_ERROR, "Failed to initialize Python interpreter");
        set_last_error("Failed to initialize Python interpreter");
        return -2;
    }
    
    // Initialize thread support
    PyEval_InitThreads();
    
    // Add current directory to Python path
    PyRun_SimpleString("import sys");
    PyRun_SimpleString("sys.path.insert(0, '.')");
    
    // Add python_path to sys.path if specified
    if (python_path && strlen(python_path) > 0) {
        char *path_cmd = dap_strdup_printf("sys.path.insert(0, '%s')", python_path);
        if (path_cmd) {
            PyRun_SimpleString(path_cmd);
            DAP_DELETE(path_cmd);
        }
    }
    
    s_python_initialized = true;
    log_it(L_INFO, "Python interpreter initialized successfully");
    
    return 0;
}

/**
 * @brief Deinitialize Python interpreter
 */
void python_interpreter_deinit(void)
{
    if (!s_python_initialized) {
        log_it(L_WARNING, "Python interpreter was not initialized");
        return;
    }
    
    log_it(L_INFO, "Deinitializing Python interpreter");
    
    // Finalize Python
    if (Py_IsInitialized()) {
        Py_Finalize();
    }
    
    s_python_initialized = false;
    log_it(L_INFO, "Python interpreter deinitialized");
}

/**
 * @brief Initialize CellFrame Python modules
 * @return 0 on success, negative value on error
 */
int python_cellframe_modules_init(void)
{
    if (!python_interpreter_is_initialized()) {
        log_it(L_ERROR, "Python interpreter not initialized");
        set_last_error("Python interpreter not initialized");
        return -1;
    }
    
    log_it(L_INFO, "Initializing CellFrame Python modules");
    
    // Try to import cellframe module
    PyObject *cellframe_module = PyImport_ImportModule("cellframe");
    if (!cellframe_module) {
        if (PyErr_Occurred()) {
            PyErr_Print();
        }
        log_it(L_ERROR, "Failed to import 'cellframe' module");
        set_last_error("Failed to import 'cellframe' module");
        return -2;
    }
    
    // Try to import dap module
    PyObject *dap_module = PyImport_ImportModule("dap");
    if (!dap_module) {
        if (PyErr_Occurred()) {
            PyErr_Print();
        }
        log_it(L_ERROR, "Failed to import 'dap' module");
        set_last_error("Failed to import 'dap' module");
        Py_DECREF(cellframe_module);
        return -3;
    }
    
    // Clean up references
    Py_DECREF(cellframe_module);
    Py_DECREF(dap_module);
    
    log_it(L_INFO, "CellFrame Python modules initialized successfully");
    return 0;
}

/**
 * @brief Deinitialize CellFrame Python modules
 */
void python_cellframe_modules_deinit(void)
{
    if (!python_interpreter_is_initialized()) {
        return;
    }
    
    log_it(L_INFO, "Deinitializing CellFrame Python modules");
    
    // Clear module cache
    PyRun_SimpleString("import sys");
    PyRun_SimpleString("if 'cellframe' in sys.modules: del sys.modules['cellframe']");
    PyRun_SimpleString("if 'dap' in sys.modules: del sys.modules['dap']");
    
    log_it(L_INFO, "CellFrame Python modules deinitialized");
}

/**
 * @brief Load Python plugin from file
 * @param plugin_path Path to plugin file
 * @return 0 on success, negative value on error
 */
int python_plugin_load(const char *plugin_path)
{
    if (!python_interpreter_is_initialized()) {
        log_it(L_ERROR, "Python interpreter not initialized");
        set_last_error("Python interpreter not initialized");
        return -1;
    }
    
    if (!plugin_path || strlen(plugin_path) == 0) {
        log_it(L_ERROR, "Invalid plugin path");
        set_last_error("Invalid plugin path");
        return -2;
    }
    
    log_it(L_INFO, "Loading Python plugin: %s", plugin_path);
    
    // Check if file exists
    struct stat st;
    if (stat(plugin_path, &st) != 0) {
        log_it(L_ERROR, "Plugin file not found: %s", plugin_path);
        set_last_error("Plugin file not found: %s", plugin_path);
        return -3;
    }
    
    // Read and execute plugin file
    FILE *plugin_file = fopen(plugin_path, "r");
    if (!plugin_file) {
        log_it(L_ERROR, "Failed to open plugin file: %s", plugin_path);
        set_last_error("Failed to open plugin file: %s", plugin_path);
        return -4;
    }
    
    if (PyRun_SimpleFile(plugin_file, plugin_path) != 0) {
        if (PyErr_Occurred()) {
            PyErr_Print();
        }
        log_it(L_ERROR, "Failed to execute plugin: %s", plugin_path);
        set_last_error("Failed to execute plugin: %s", plugin_path);
        fclose(plugin_file);
        return -5;
    }
    
    fclose(plugin_file);
    log_it(L_INFO, "Successfully loaded Python plugin: %s", plugin_path);
    
    return 0;
}

/**
 * @brief Load Python plugins from directory
 * @param plugins_dir Directory containing Python plugins
 * @return Number of loaded plugins or negative value on error
 */
int python_plugins_load_from_dir(const char *plugins_dir)
{
    if (!python_interpreter_is_initialized()) {
        log_it(L_ERROR, "Python interpreter not initialized");
        set_last_error("Python interpreter not initialized");
        return -1;
    }
    
    if (!plugins_dir || strlen(plugins_dir) == 0) {
        log_it(L_ERROR, "Invalid plugins directory");
        set_last_error("Invalid plugins directory");
        return -2;
    }
    
    log_it(L_INFO, "Loading Python plugins from directory: %s", plugins_dir);
    
    DIR *dir = opendir(plugins_dir);
    if (!dir) {
        log_it(L_WARNING, "Failed to open plugins directory: %s", plugins_dir);
        return 0; // Not an error, just no plugins to load
    }
    
    int loaded_count = 0;
    struct dirent *entry;
    
    while ((entry = readdir(dir)) != NULL) {
        // Skip hidden files and directories
        if (entry->d_name[0] == '.') {
            continue;
        }
        
        // Only process .py files
        const char *ext = strrchr(entry->d_name, '.');
        if (!ext || strcmp(ext, ".py") != 0) {
            continue;
        }
        
        // Build full path
        char *plugin_path = dap_strdup_printf("%s/%s", plugins_dir, entry->d_name);
        if (!plugin_path) {
            log_it(L_ERROR, "Failed to allocate memory for plugin path");
            continue;
        }
        
        // Load plugin
        if (python_plugin_load(plugin_path) == 0) {
            loaded_count++;
        }
        
        DAP_DELETE(plugin_path);
    }
    
    closedir(dir);
    log_it(L_INFO, "Loaded %d Python plugins from directory: %s", loaded_count, plugins_dir);
    
    return loaded_count;
}

/**
 * @brief Unload specific Python plugin
 * @param plugin_name Name of plugin to unload
 */
void python_plugin_unload(const char *plugin_name)
{
    if (!python_interpreter_is_initialized()) {
        return;
    }
    
    if (!plugin_name || strlen(plugin_name) == 0) {
        log_it(L_ERROR, "Invalid plugin name");
        return;
    }
    
    log_it(L_INFO, "Unloading Python plugin: %s", plugin_name);
    
    // Remove module from sys.modules
    char *unload_cmd = dap_strdup_printf("import sys; "
                                        "if '%s' in sys.modules: del sys.modules['%s']",
                                        plugin_name, plugin_name);
    if (unload_cmd) {
        PyRun_SimpleString(unload_cmd);
        DAP_DELETE(unload_cmd);
    }
    
    log_it(L_INFO, "Python plugin unloaded: %s", plugin_name);
}

/**
 * @brief Unload all Python plugins
 */
void python_plugins_unload_all(void)
{
    if (!python_interpreter_is_initialized()) {
        return;
    }
    
    log_it(L_INFO, "Unloading all Python plugins");
    
    // Clear all user modules (keep only built-in modules)
    PyRun_SimpleString("import sys");
    PyRun_SimpleString("user_modules = [m for m in sys.modules.keys() if not m.startswith('__')]");
    PyRun_SimpleString("for m in user_modules: del sys.modules[m]");
    
    log_it(L_INFO, "All Python plugins unloaded");
} 