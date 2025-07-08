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

#ifdef __cplusplus
extern "C" {
#endif

// Plugin information structure
typedef struct plugin_info {
    const char *name;
    const char *version;
    const char *description;
    int (*init_func)(void);
    void (*deinit_func)(void);
} plugin_info_t;

// Python interpreter management
int python_interpreter_init(const char *python_path);
void python_interpreter_deinit(void);
bool python_interpreter_is_initialized(void);

// CellFrame Python modules management
int python_cellframe_modules_init(void);
void python_cellframe_modules_deinit(void);

// Python plugins management
int python_plugins_load_from_dir(const char *plugins_dir);
void python_plugins_unload_all(void);
int python_plugin_load(const char *plugin_path);
void python_plugin_unload(const char *plugin_name);

// Plugin utility functions
const char *python_get_last_error(void);
void python_clear_last_error(void);

// Plugin main functions
int plugin_python_init(void);
void plugin_python_deinit(void);
plugin_info_t *plugin_get_info(void);

#ifdef __cplusplus
}
#endif 