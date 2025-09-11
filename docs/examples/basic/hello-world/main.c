/*
 * DAP SDK Hello World Example
 *
 * This example demonstrates basic DAP SDK initialization,
 * logging, and graceful shutdown.
 */

#include <stdio.h>
#include <stdlib.h>
#include <signal.h>
#include <unistd.h>
#include <string.h>

// DAP SDK headers
#include "dap_common.h"
#include "dap_config.h"

#define DAP_CONFIG_FILE "hello_world.conf"

// Global variables for signal handling
volatile sig_atomic_t g_shutdown_requested = 0;

// Signal handler
void signal_handler(int signum) {
    g_shutdown_requested = 1;
    printf("\n🛑 Shutdown signal received...\n");
}

/**
 * @brief Initialize the application
 * @param app_name Application name
 * @return 0 on success, -1 on error
 */
int app_init(const char *app_name) {
    printf("🚀 Initializing DAP SDK application: %s\n", app_name);

    // Initialize DAP common module
    if (dap_common_init(app_name) != 0) {
        fprintf(stderr, "❌ Failed to initialize DAP SDK common module\n");
        return -1;
    }

    // Load configuration if available
    if (dap_config_init(DAP_CONFIG_FILE) != 0) {
        printf("⚠️  Configuration file not found, using defaults\n");
    }

    printf("✅ DAP SDK initialized successfully\n");
    return 0;
}

/**
 * @brief Main application processing loop
 * @return 0 on success, -1 on error
 */
int app_process(void) {
    static int counter = 0;

    // Simulate some processing
    if (counter % 10 == 0) {
        printf("🔄 Processing iteration: %d\n", counter);

        // Get SDK version
        const char *version = dap_get_version();
        if (version) {
            printf("📚 DAP SDK Version: %s\n", version);
        } else {
            printf("⚠️  Could not retrieve SDK version\n");
        }

        // Simulate memory usage (in a real app this would be actual monitoring)
        printf("📊 Memory usage: %d KB\n", 1024 + (counter % 100));
    }

    counter++;

    // Simulate some work
    usleep(100000); // 100ms delay

    return 0;
}

/**
 * @brief Cleanup application resources
 */
void app_cleanup(void) {
    printf("🛑 Shutting down gracefully...\n");

    // Cleanup DAP modules
    dap_config_deinit();
    dap_common_deinit();

    printf("✅ Cleanup completed\n");
}

/**
 * @brief Get SDK version
 * @return SDK version string
 */
const char *app_get_sdk_version(void) {
    return dap_get_version();
}

/**
 * @brief Main entry point
 */
int main(int argc, char *argv[]) {
    const char *app_name = (argc > 1) ? argv[1] : "hello_world_app";

    printf("🚀 Starting Hello World Application...\n");

    // Register signal handlers
    signal(SIGINT, signal_handler);
    signal(SIGTERM, signal_handler);

    // Initialize application
    if (app_init(app_name) != 0) {
        fprintf(stderr, "❌ Failed to initialize application\n");
        return EXIT_FAILURE;
    }

    // Main processing loop
    while (!g_shutdown_requested) {
        if (app_process() != 0) {
            fprintf(stderr, "❌ Application processing failed\n");
            break;
        }
    }

    // Cleanup
    app_cleanup();
    printf("✅ Application finished successfully!\n");

    return EXIT_SUCCESS;
}
