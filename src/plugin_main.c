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
#include <dap_common.h>
#include <dap_config.h>
#include <dap_strfuncs.h>
#include <dap_file_utils.h>
#include "plugin_python_init.h"

#define LOG_TAG "plugin-python"

// Plugin metadata
static const char *s_plugin_name = "cellframe-node-plugin-python";
static const char *s_plugin_version = "1.0.0";
static const char *s_plugin_description = "Python plugins support for CellFrame Node";

// Configuration section name
static const char *s_config_section = "python";

// Plugin initialization state
static bool s_plugin_initialized = false;

/**
 * @brief Plugin initialization function
 * This function is called when the plugin is loaded by CellFrame Node
 * @return 0 on success, negative value on error
 */
int plugin_python_init(void)
{
    log_it(L_NOTICE, "Initializing CellFrame Node Python Plugin v%s", s_plugin_version);
    
    // Check if already initialized
    if (s_plugin_initialized) {
        log_it(L_WARNING, "Python plugin already initialized");
        return -1;
    }
    
    // Read configuration
    bool l_enabled = dap_config_get_item_bool_default(s_config_section, "enabled", true);
    if (!l_enabled) {
        log_it(L_INFO, "Python plugin is disabled in configuration");
        return 0;
    }
    
    // Get plugins path
    const char *l_plugins_path = dap_config_get_item_str_default(s_config_section, "plugins_path", 
                                                                "/opt/cellframe-node/var/lib/plugins");
    if (!l_plugins_path) {
        log_it(L_ERROR, "Failed to get plugins path from configuration");
        return -2;
    }
    
    // Get Python path
    const char *l_python_path = dap_config_get_item_str_default(s_config_section, "python_path", 
                                                               "/opt/cellframe-node/python");
    if (!l_python_path) {
        log_it(L_ERROR, "Failed to get Python path from configuration");
        return -3;
    }
    
    log_it(L_INFO, "Python plugin configuration:");
    log_it(L_INFO, "  Plugins path: %s", l_plugins_path);
    log_it(L_INFO, "  Python path: %s", l_python_path);
    
    // Create plugins directory if it doesn't exist
    if (dap_dir_test(l_plugins_path) != 0) {
        if (dap_mkdir_with_parents(l_plugins_path) != 0) {
            log_it(L_ERROR, "Failed to create plugins directory: %s", l_plugins_path);
            return -4;
        }
        log_it(L_INFO, "Created plugins directory: %s", l_plugins_path);
    }
    
    // Initialize Python interpreter
    int l_python_init_result = python_interpreter_init(l_python_path);
    if (l_python_init_result != 0) {
        log_it(L_ERROR, "Failed to initialize Python interpreter (code: %d)", l_python_init_result);
        return -5;
    }
    
    // Initialize CellFrame Python modules
    int l_cellframe_init_result = python_cellframe_modules_init();
    if (l_cellframe_init_result != 0) {
        log_it(L_ERROR, "Failed to initialize CellFrame Python modules (code: %d)", l_cellframe_init_result);
        python_interpreter_deinit();
        return -6;
    }
    
    // Load Python plugins from directory
    int l_plugins_loaded = python_plugins_load_from_dir(l_plugins_path);
    if (l_plugins_loaded < 0) {
        log_it(L_ERROR, "Failed to load Python plugins from directory: %s", l_plugins_path);
        python_cellframe_modules_deinit();
        python_interpreter_deinit();
        return -7;
    }
    
    log_it(L_INFO, "Successfully loaded %d Python plugins", l_plugins_loaded);
    
    s_plugin_initialized = true;
    log_it(L_NOTICE, "CellFrame Node Python Plugin initialized successfully");
    
    return 0;
}

/**
 * @brief Plugin deinitialization function
 * This function is called when the plugin is unloaded by CellFrame Node
 */
void plugin_python_deinit(void)
{
    log_it(L_NOTICE, "Deinitializing CellFrame Node Python Plugin");
    
    if (!s_plugin_initialized) {
        log_it(L_WARNING, "Python plugin was not initialized");
        return;
    }
    
    // Unload Python plugins
    python_plugins_unload_all();
    
    // Deinitialize CellFrame Python modules
    python_cellframe_modules_deinit();
    
    // Deinitialize Python interpreter
    python_interpreter_deinit();
    
    s_plugin_initialized = false;
    log_it(L_NOTICE, "CellFrame Node Python Plugin deinitialized");
}

/**
 * @brief Get plugin information
 * @return Plugin information structure
 */
plugin_info_t *plugin_get_info(void)
{
    static plugin_info_t s_plugin_info = {
        .name = s_plugin_name,
        .version = s_plugin_version,
        .description = s_plugin_description,
        .init_func = plugin_python_init,
        .deinit_func = plugin_python_deinit
    };
    
    return &s_plugin_info;
}

/**
 * @brief Plugin entry point
 * This function is called when the plugin shared library is loaded
 * @return 0 on success, negative value on error
 */
int plugin_init(void)
{
    log_it(L_DEBUG, "Python plugin entry point called");
    return plugin_python_init();
}

/**
 * @brief Plugin exit point
 * This function is called when the plugin shared library is unloaded
 */
void plugin_deinit(void)
{
    log_it(L_DEBUG, "Python plugin exit point called");
    plugin_python_deinit();
} 