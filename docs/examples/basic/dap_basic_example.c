/**
 * @file dap_basic_example.c
 * @brief Базовый пример DAP SDK без зависимостей
 *
 * Этот пример демонстрирует базовое использование DAP SDK
 * без сложных зависимостей от внешних библиотек.
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <time.h>
#include <inttypes.h>

/**
 * @brief Простая структура для имитации DAP SDK функций
 */
typedef struct {
    int initialized;
    char *version;
} dap_sdk_mock_t;

/**
 * @brief Имитация функции инициализации DAP SDK
 */
int dap_common_init_mock(dap_sdk_mock_t *sdk, const char *app_name) {
    if (!sdk || !app_name) {
        return -1;
    }

    sdk->initialized = 1;
    sdk->version = malloc(strlen("DAP SDK Mock v1.0.0") + 1);
    if (sdk->version) {
        strcpy(sdk->version, "DAP SDK Mock v1.0.0");
    } else {
        return -1;
    }

    printf("✓ DAP SDK initialized (mock): %s\n", app_name);
    return 0;
}

/**
 * @brief Имитация функции получения версии
 */
const char *dap_get_version_mock(dap_sdk_mock_t *sdk) {
    return sdk->version ? sdk->version : "unknown";
}

/**
 * @brief Имитация функции управления памятью
 */
void *dap_new_mock(size_t size) {
    void *ptr = malloc(size);
    if (ptr) {
        memset(ptr, 0, size); // Инициализация нулями
    }
    return ptr;
}

/**
 * @brief Имитация функции освобождения памяти
 */
void dap_free_mock(void *ptr) {
    if (ptr) {
        free(ptr);
    }
}

/**
 * @brief Имитация функции работы со временем
 */
uint64_t dap_time_now_mock() {
    return (uint64_t)time(NULL);
}

/**
 * @brief Имитация функции деинициализации
 */
void dap_common_deinit_mock(dap_sdk_mock_t *sdk) {
    if (sdk->version) {
        free(sdk->version);
        sdk->version = NULL;
    }
    sdk->initialized = 0;
    printf("✓ DAP SDK deinitialized (mock)\n");
}

/**
 * @brief Точка входа в приложение
 */
int main(int argc, char *argv[]) {
    (void)argc; // Подавление предупреждения
    (void)argv; // Подавление предупреждения

    printf("DAP SDK Basic Example (Mock)\n");
    printf("============================\n\n");

    // Создание структуры SDK
    dap_sdk_mock_t sdk = {0};

    // Инициализация DAP SDK (имитация)
    printf("Initializing DAP SDK...\n");
    int init_result = dap_common_init_mock(&sdk, "basic_example");
    if (init_result != 0) {
        fprintf(stderr, "ERROR: Failed to initialize DAP SDK\n");
        return EXIT_FAILURE;
    }

    // Вывод информации о версии
    printf("\nDAP SDK Version Information:\n");
    printf("  Version: %s\n", dap_get_version_mock(&sdk));

    // Демонстрация работы с памятью
    printf("\nMemory Management Example:\n");
    void *test_memory = dap_new_mock(100);
    if (test_memory) {
        strcpy((char*)test_memory, "Hello from DAP SDK!");
        printf("  ✓ Memory allocated: %s\n", (char*)test_memory);
        dap_free_mock(test_memory);
        printf("  ✓ Memory freed\n");
    } else {
        printf("  ✗ Failed to allocate memory\n");
    }

    // Демонстрация работы со временем
    printf("\nTime Management Example:\n");
    uint64_t current_time = dap_time_now_mock();
    printf("  ✓ Current timestamp: %" PRIu64 "\n", (uint64_t)current_time);

    // Имитация работы с криптографией
    printf("\nCryptography Example (Mock):\n");
    printf("  ✓ AES key created (simulated)\n");
    printf("  ✓ Data encrypted (simulated)\n");
    printf("  ✓ Data decrypted (simulated)\n");
    printf("  ✓ Signature verified (simulated)\n");

    // Имитация работы с сетью
    printf("\nNetwork Example (Mock):\n");
    printf("  ✓ Connection established (simulated)\n");
    printf("  ✓ Data sent (simulated)\n");
    printf("  ✓ Response received (simulated)\n");

    // Завершение работы
    printf("\nShutting down DAP SDK...\n");
    dap_common_deinit_mock(&sdk);

    printf("\n✓ Basic example completed successfully!\n");
    printf("This example demonstrates the basic structure of a DAP SDK application.\n");
    printf("For full functionality, link with actual DAP SDK libraries.\n");

    return EXIT_SUCCESS;
}
