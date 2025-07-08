# Plugin Dependency Management System

## Overview

The Plugin Dependency Management System provides automatic plugin loading with dependency resolution and file type handler registration for DAP SDK. This system eliminates hardcoded language enums and enables dynamic plugin registration.

## Features

### 🔧 Dynamic Type Registration
- Register plugins as handlers for specific file extensions
- No hardcoded language types
- Runtime registration system

### 📦 Dependency Resolution
- Topological sorting of plugin dependencies
- Circular dependency detection
- Automatic dependency loading

### 🔍 Auto-Discovery
- Automatic detection of plugin files
- Handler identification by file extension
- Auto-loading of required plugins

## Usage Examples

### Python Plugin Registration

```c
// In python-plugin initialization
static int python_plugin_init(dap_config_t *a_config, char **a_error_str)
{
    // Register python-plugin as handler for .py files
    dap_plugin_type_callbacks_t callbacks = {
        .load = python_plugin_load_script,
        .unload = python_plugin_unload_script
    };
    
    int ret = dap_plugin_register_type_handler(".py", "python-plugin", &callbacks, NULL);
    if (ret != 0) {
        *a_error_str = dap_strdup("Failed to register Python file handler");
        return -1;
    }
    
    log_it(L_INFO, "Python plugin registered as .py file handler");
    return 0;
}
```

### Auto-Loading Python Files

```c
// Scan directory for Python plugins
dap_plugin_detection_result_t *results = NULL;
size_t results_count = 0;

int ret = dap_plugin_scan_directory("/path/to/plugins", true, &results, &results_count);
if (ret == 0 && results_count > 0) {
    // Auto-load required handlers
    ret = dap_plugin_auto_load_handlers(results, results_count);
    if (ret == 0) {
        log_it(L_INFO, "Auto-loaded %zu plugin handlers", results_count);
    }
    
    // Clean up
    dap_plugin_detection_results_free(results, results_count);
}
```

### Loading with Dependencies

```c
// Load python-plugin with all its dependencies
int ret = dap_plugin_load_with_dependencies("python-plugin", NULL);
if (ret == 0) {
    log_it(L_INFO, "Python plugin loaded with dependencies");
} else {
    log_it(L_ERROR, "Failed to load python-plugin (code %d)", ret);
}
```

## Architecture

### Key Components

1. **Type Handler Registry**: Hash-based registry for file extension handlers
2. **Dependency Graph**: Topological sorting with cycle detection
3. **Auto-Discovery**: Directory scanning with pattern matching
4. **Integration Layer**: Seamless integration with existing DAP plugin system

### Flow Diagram

```
[Plugin Directory] → [Scanner] → [Detection Results]
                                       ↓
[Type Registry] ← [Handler Registration] ← [Auto-Loader]
       ↓
[Dependency Manager] → [Topological Sort] → [Load Order]
                                                 ↓
[Plugin System] ← [Dependency-Aware Loading] ← [Sorted List]
```

## API Reference

### Core Functions

- `dap_plugin_dependency_manager_init()` - Initialize the system
- `dap_plugin_dependency_manager_deinit()` - Cleanup resources
- `dap_plugin_register_type_handler()` - Register file type handler
- `dap_plugin_find_type_handler()` - Find handler for extension
- `dap_plugin_scan_directory()` - Scan for plugin files
- `dap_plugin_auto_load_handlers()` - Auto-load required handlers
- `dap_plugin_load_with_dependencies()` - Load plugin with dependencies

### Statistics

```c
dap_plugin_load_stats_t stats = dap_plugin_get_load_stats();
log_it(L_INFO, "Loaded: %zu, Dependencies: %zu, Handlers: %zu", 
       stats.total_loaded, stats.dependencies_resolved, stats.handlers_registered);
```

## Integration

The system automatically integrates with the existing DAP plugin architecture:

1. **Initialization**: Called from `dap_plugin_init()`
2. **Dependency Resolution**: Replaces empty `s_solve_dependencies()`
3. **Type System**: Extends existing plugin type callbacks
4. **Memory Management**: Uses DAP SDK memory macros

## Error Handling

All functions return standard DAP error codes:
- `0` - Success
- Negative values - Error codes with specific meanings
- Extensive logging for debugging

## Thread Safety

The system is designed for single-threaded initialization and multi-threaded usage:
- All registration should happen during initialization
- Runtime lookups are thread-safe
- Statistics are atomic

## Performance

- **O(1)** type handler lookups via hash tables
- **O(V + E)** dependency resolution via DFS
- **O(n log n)** directory scanning
- Minimal memory footprint with efficient cleanup

## Example Integration

See `cellframe-node.rc-6.0/plugin/plugin-python/` for a complete example of how to integrate Python plugin with the dependency management system.

## Troubleshooting

### Common Issues

1. **Handler Not Found**: Ensure the handler plugin is properly registered
2. **Circular Dependencies**: Check plugin manifests for circular references
3. **Memory Leaks**: Always call cleanup functions

### Debug Information

```c
dap_plugin_dependency_manager_debug_print();
```

This prints detailed information about registered handlers, statistics, and system state. 