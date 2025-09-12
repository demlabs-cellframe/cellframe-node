/*
 * DAP SDK Hello World Application Implementation
 */

#include "app.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

// Static variable to store SDK version
static char sdk_version[32] = {0};

int app_init(const char *app_name) {
    printf("🚀 Initializing application: %s\n", app_name);

    // Initialize DAP SDK common module
    if (dap_common_init(app_name) != 0) {
        fprintf(stderr, "❌ Failed to initialize DAP SDK\n");
        return -1;
    }

    // Get SDK version
    const char *version = dap_get_version();
    if (version) {
        strncpy(sdk_version, version, sizeof(sdk_version) - 1);
        printf("📚 DAP SDK Version: %s\n", sdk_version);
    } else {
        fprintf(stderr, "⚠️  Failed to get SDK version\n");
        strcpy(sdk_version, "unknown");
    }

    printf("🎯 Application is running!\n");
    return 0;
}

int app_process(void) {
    // Simulate application processing
    static int counter = 0;

    // Log every 10 iterations
    if (counter % 10 == 0) {
        printf("🔄 Processing iteration: %d\n", counter);

        // Simulate memory usage (in real app this would be actual monitoring)
        printf("📊 Memory usage: %d KB\n", 1024 + (counter % 100));
    }

    counter++;
    return 0;
}

void app_cleanup(void) {
    printf("🛑 Shutting down gracefully...\n");

    // Cleanup DAP SDK modules
    dap_config_deinit();
    dap_common_deinit();

    printf("✅ Cleanup completed\n");
}

const char *app_get_sdk_version(void) {
    return sdk_version;
}



