#ifndef PYTHON_DAP_H
#define PYTHON_DAP_H

#include <Python.h>
#include <stddef.h>
#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

// Module initialization function
PyMODINIT_FUNC PyInit_python_dap(void);

// Cleanup function
void python_dap_cleanup(void);

// Module constants
#define PYTHON_DAP_VERSION "1.0.0"

// Build mode constants (defined at compile time)
#ifdef PYTHON_DAP_STANDALONE
#define PYTHON_DAP_BUILD_MODE "standalone"
#elif defined(PYTHON_DAP_STATIC)
#define PYTHON_DAP_BUILD_MODE "static"
#ifdef PYTHON_DAP_PLUGIN_MODE
#define PYTHON_DAP_PLUGIN_SUPPORT 1
#else
#define PYTHON_DAP_PLUGIN_SUPPORT 0
#endif
#else
#define PYTHON_DAP_BUILD_MODE "unknown"
#define PYTHON_DAP_PLUGIN_SUPPORT 0
#endif

// All module headers are included in the implementation files
// This header provides the main module interface only

#ifdef __cplusplus
}
#endif

#endif // PYTHON_DAP_H 