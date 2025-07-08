/**
 * @file plugin_dependency_manager.h
 * @brief Plugin Dependency Management System
 * @details Автоматическая загрузка плагинов с управлением зависимостями
 * 
 * Система обеспечивает:
 * - Автоматическую загрузку python-plugin при обнаружении Python плагинов
 * - Построение графа зависимостей из plugin manifest
 * - Топологическую сортировку для правильного порядка загрузки
 * - Валидацию циклических зависимостей
 * 
 * @author Dmitriy Gerasimov
 * @date 2025-01-08
 */

#ifndef PLUGIN_DEPENDENCY_MANAGER_H
#define PLUGIN_DEPENDENCY_MANAGER_H

#include <stdint.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <json-c/json.h>

#ifdef __cplusplus
extern "C" {
#endif

// Forward declarations
typedef struct dap_plugin_manifest dap_plugin_manifest_t;
typedef struct dap_plugin_dependency dap_plugin_dependency_t;
typedef struct dap_plugin_dependency_graph dap_plugin_dependency_graph_t;
typedef struct dap_plugin_loader_context dap_plugin_loader_context_t;

/**
 * @brief Plugin types enumeration
 */
typedef enum {
    DAP_PLUGIN_TYPE_UNKNOWN = 0,
    DAP_PLUGIN_TYPE_BINARY,     // .so/.dll/.dylib
    DAP_PLUGIN_TYPE_PYTHON,     // .py
    DAP_PLUGIN_TYPE_JAVASCRIPT, // .js
    DAP_PLUGIN_TYPE_LUA,        // .lua
    DAP_PLUGIN_TYPE_WASM,       // .wasm
    DAP_PLUGIN_TYPE_MAX
} dap_plugin_type_t;

/**
 * @brief Plugin status enumeration
 */
typedef enum {
    DAP_PLUGIN_STATUS_UNKNOWN = 0,
    DAP_PLUGIN_STATUS_DISCOVERED,
    DAP_PLUGIN_STATUS_LOADING,
    DAP_PLUGIN_STATUS_LOADED,
    DAP_PLUGIN_STATUS_FAILED,
    DAP_PLUGIN_STATUS_UNLOADED,
    DAP_PLUGIN_STATUS_MAX
} dap_plugin_status_t;

/**
 * @brief Plugin dependency structure
 */
typedef struct dap_plugin_dependency {
    char *name;                 // Dependency name
    char *version;              // Required version (>=1.0.0)
    dap_plugin_type_t type;     // Dependency type
    bool required;              // Is dependency required
    bool auto_load;             // Should be loaded automatically
    char *load_path;            // Path to dependency
    
    struct dap_plugin_dependency *next;
} dap_plugin_dependency_t;

/**
 * @brief Plugin manifest structure
 */
typedef struct dap_plugin_manifest {
    char *name;                     // Plugin name
    char *version;                  // Plugin version
    char *description;              // Plugin description
    dap_plugin_type_t type;         // Plugin type
    char *entry_point;              // Entry point file/function
    char *manifest_path;            // Path to manifest file
    char *plugin_path;              // Path to plugin file
    
    // Runtime information
    struct {
        char *language;             // Runtime language
        char *interpreter;          // Interpreter path
        char *environment;          // Environment requirements
    } runtime;
    
    // Dependencies
    dap_plugin_dependency_t *dependencies;
    uint32_t dependency_count;
    
    // Metadata
    struct {
        char *author;
        char *license;
        char *homepage;
        uint64_t created_at;
        uint64_t updated_at;
    } metadata;
    
    // Status
    dap_plugin_status_t status;
    void *handle;                   // Plugin handle (for loaded plugins)
    
    struct dap_plugin_manifest *next;
} dap_plugin_manifest_t;

/**
 * @brief Plugin dependency graph node
 */
typedef struct dap_plugin_graph_node {
    dap_plugin_manifest_t *manifest;
    uint32_t in_degree;             // Number of incoming edges
    uint32_t out_degree;            // Number of outgoing edges
    struct dap_plugin_graph_node **dependencies;  // Outgoing edges
    struct dap_plugin_graph_node **dependents;    // Incoming edges
    bool visited;                   // For traversal algorithms
    uint32_t load_order;            // Order in which to load
    
    struct dap_plugin_graph_node *next;
} dap_plugin_graph_node_t;

/**
 * @brief Plugin dependency graph
 */
typedef struct dap_plugin_dependency_graph {
    dap_plugin_graph_node_t *nodes;
    uint32_t node_count;
    uint32_t edge_count;
    bool has_cycles;                // Cycle detection result
    dap_plugin_graph_node_t **sorted_nodes;  // Topologically sorted nodes
    uint32_t sorted_count;
} dap_plugin_dependency_graph_t;

/**
 * @brief Plugin loader context
 */
typedef struct dap_plugin_loader_context {
    dap_plugin_manifest_t *manifests;          // All discovered manifests
    dap_plugin_dependency_graph_t *graph;      // Dependency graph
    
    // Configuration
    char *plugins_dir;                          // Plugin directory
    char *python_plugin_path;                  // Path to python-plugin
    bool auto_load_python_plugin;              // Auto-load python-plugin
    bool strict_dependency_checking;           // Strict dependency validation
    
    // Runtime state
    uint32_t loaded_plugins_count;
    uint32_t failed_plugins_count;
    dap_plugin_manifest_t *deferred_plugins;   // Plugins waiting for dependencies
    
    // Callbacks
    int (*on_plugin_loaded)(dap_plugin_manifest_t *manifest);
    int (*on_plugin_failed)(dap_plugin_manifest_t *manifest, const char *error);
    int (*on_dependency_resolved)(dap_plugin_manifest_t *plugin, dap_plugin_dependency_t *dep);
    
    // Statistics
    struct {
        uint32_t total_plugins;
        uint32_t successful_loads;
        uint32_t failed_loads;
        uint32_t auto_loaded_python_plugins;
        uint64_t total_load_time_ms;
    } stats;
} dap_plugin_loader_context_t;

// === Core Functions ===

/**
 * @brief Initialize plugin dependency manager
 * @param plugins_dir Directory containing plugins
 * @param python_plugin_path Path to python-plugin binary
 * @return Plugin loader context or NULL on error
 */
dap_plugin_loader_context_t* dap_plugin_dependency_manager_init(const char *plugins_dir, 
                                                                const char *python_plugin_path);

/**
 * @brief Cleanup plugin dependency manager
 * @param ctx Plugin loader context
 */
void dap_plugin_dependency_manager_deinit(dap_plugin_loader_context_t *ctx);

/**
 * @brief Discover all plugins in directory
 * @param ctx Plugin loader context
 * @return Number of discovered plugins or -1 on error
 */
int dap_plugin_dependency_manager_discover(dap_plugin_loader_context_t *ctx);

/**
 * @brief Build dependency graph from manifests
 * @param ctx Plugin loader context
 * @return 0 on success, -1 on error
 */
int dap_plugin_dependency_manager_build_graph(dap_plugin_loader_context_t *ctx);

/**
 * @brief Load plugins in dependency order
 * @param ctx Plugin loader context
 * @return Number of successfully loaded plugins or -1 on error
 */
int dap_plugin_dependency_manager_load_all(dap_plugin_loader_context_t *ctx);

// === Manifest Functions ===

/**
 * @brief Load plugin manifest from file
 * @param manifest_path Path to manifest file
 * @return Plugin manifest or NULL on error
 */
dap_plugin_manifest_t* dap_plugin_manifest_load(const char *manifest_path);

/**
 * @brief Create manifest from Python plugin file
 * @param plugin_path Path to Python plugin file
 * @return Plugin manifest or NULL on error
 */
dap_plugin_manifest_t* dap_plugin_manifest_create_from_python(const char *plugin_path);

/**
 * @brief Free plugin manifest
 * @param manifest Plugin manifest to free
 */
void dap_plugin_manifest_free(dap_plugin_manifest_t *manifest);

/**
 * @brief Check if plugin type needs python-plugin
 * @param type Plugin type
 * @return true if needs python-plugin, false otherwise
 */
bool dap_plugin_type_needs_python_plugin(dap_plugin_type_t type);

// === Dependency Graph Functions ===

/**
 * @brief Create dependency graph
 * @return Empty dependency graph or NULL on error
 */
dap_plugin_dependency_graph_t* dap_plugin_dependency_graph_create(void);

/**
 * @brief Add plugin to dependency graph
 * @param graph Dependency graph
 * @param manifest Plugin manifest
 * @return 0 on success, -1 on error
 */
int dap_plugin_dependency_graph_add_plugin(dap_plugin_dependency_graph_t *graph, 
                                          dap_plugin_manifest_t *manifest);

/**
 * @brief Perform topological sort
 * @param graph Dependency graph
 * @return 0 on success, -1 on error (cycles detected)
 */
int dap_plugin_dependency_graph_topological_sort(dap_plugin_dependency_graph_t *graph);

/**
 * @brief Check for cycles in dependency graph
 * @param graph Dependency graph
 * @return true if cycles exist, false otherwise
 */
bool dap_plugin_dependency_graph_has_cycles(dap_plugin_dependency_graph_t *graph);

/**
 * @brief Free dependency graph
 * @param graph Dependency graph to free
 */
void dap_plugin_dependency_graph_free(dap_plugin_dependency_graph_t *graph);

// === Auto-loader Functions ===

/**
 * @brief Auto-load python-plugin if needed
 * @param ctx Plugin loader context
 * @param for_plugin Plugin that needs python-plugin
 * @return 0 on success, -1 on error
 */
int dap_plugin_auto_load_python_plugin(dap_plugin_loader_context_t *ctx, 
                                      dap_plugin_manifest_t *for_plugin);

/**
 * @brief Check if python-plugin is already loaded
 * @param ctx Plugin loader context
 * @return true if loaded, false otherwise
 */
bool dap_plugin_is_python_plugin_loaded(dap_plugin_loader_context_t *ctx);

/**
 * @brief Load single plugin
 * @param ctx Plugin loader context
 * @param manifest Plugin manifest
 * @return 0 on success, -1 on error
 */
int dap_plugin_load_single(dap_plugin_loader_context_t *ctx, dap_plugin_manifest_t *manifest);

// === Utility Functions ===

/**
 * @brief Get plugin type from file extension
 * @param file_path Path to plugin file
 * @return Plugin type
 */
dap_plugin_type_t dap_plugin_get_type_from_file(const char *file_path);

/**
 * @brief Get plugin type string
 * @param type Plugin type
 * @return Type string
 */
const char* dap_plugin_type_to_string(dap_plugin_type_t type);

/**
 * @brief Get plugin status string
 * @param status Plugin status
 * @return Status string
 */
const char* dap_plugin_status_to_string(dap_plugin_status_t status);

/**
 * @brief Print dependency graph (for debugging)
 * @param graph Dependency graph
 */
void dap_plugin_dependency_graph_print(dap_plugin_dependency_graph_t *graph);

/**
 * @brief Get plugin statistics
 * @param ctx Plugin loader context
 * @return Statistics structure
 */
const char* dap_plugin_dependency_manager_get_stats(dap_plugin_loader_context_t *ctx);

// === Plugin Type Registry Functions ===

/**
 * @brief Plugin type handler function
 * @param manifest Plugin manifest
 * @param ctx Plugin loader context
 * @return 0 on success, -1 on error
 */
typedef int (*dap_plugin_type_handler_t)(dap_plugin_manifest_t *manifest, 
                                        dap_plugin_loader_context_t *ctx);

/**
 * @brief Register plugin type handler
 * @param type Plugin type
 * @param handler Handler function
 * @return 0 on success, -1 on error
 */
int dap_plugin_register_type_handler(dap_plugin_type_t type, dap_plugin_type_handler_t handler);

/**
 * @brief Get plugin type handler
 * @param type Plugin type
 * @return Handler function or NULL if not found
 */
dap_plugin_type_handler_t dap_plugin_get_type_handler(dap_plugin_type_t type);

/**
 * @brief Initialize plugin type registry
 * @return 0 on success, -1 on error
 */
int dap_plugin_type_registry_init(void);

/**
 * @brief Cleanup plugin type registry
 */
void dap_plugin_type_registry_deinit(void);

#ifdef __cplusplus
}
#endif

#endif // PLUGIN_DEPENDENCY_MANAGER_H 