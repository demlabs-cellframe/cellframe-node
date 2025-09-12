/*
 * DAP SDK Hello World Application Header
 *
 * Application interface definitions
 */

#pragma once

#include "dap_common.h"
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief Initialize the application
 * @param app_name Application name
 * @return 0 on success, -1 on error
 */
int app_init(const char *app_name);

/**
 * @brief Main application processing
 * @return 0 on success, -1 on error
 */
int app_process(void);

/**
 * @brief Cleanup application resources
 */
void app_cleanup(void);

/**
 * @brief Get SDK version
 * @return SDK version string or NULL
 */
const char *app_get_sdk_version(void);

#ifdef __cplusplus
}
#endif



