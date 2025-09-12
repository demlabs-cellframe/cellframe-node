# 🌟 Hello World - Ваш первый проект на CellFrame DAP SDK

Это простейший пример использования CellFrame DAP SDK. Он демонстрирует базовую инициализацию SDK, логирование и graceful shutdown.

## 🎯 Что делает этот пример

- ✅ Инициализирует DAP SDK
- ✅ Выводит информацию о версии SDK
- ✅ Демонстрирует базовое логирование
- ✅ Показывает правильный способ завершения работы

## 📁 Структура проекта

```
hello-world/
├── CMakeLists.txt     # Конфигурация сборки
├── src/
│   └── main.c        # Основной код приложения
├── include/
│   └── app.h         # Заголовочный файл
├── tests/
│   └── test_app.c    # Тесты
├── docs/
│   └── api.md        # Документация API
└── README.md         # Эта документация
```

## 🚀 Быстрый старт

### Сборка и запуск

```bash
# Переход в директорию примера
cd examples/basic/hello-world

# Создание директории сборки
mkdir build && cd build

# Конфигурация проекта
cmake .. -DCMAKE_BUILD_TYPE=Release

# Сборка
make

# Запуск
./hello-world
```

**Ожидаемый вывод:**
```
🚀 Starting Hello World Application...
✅ DAP SDK initialized successfully
📚 DAP SDK Version: 2.3.0
🎯 Application is running!
📊 Memory usage: 1024 KB
🛑 Shutting down gracefully...
✅ Application finished successfully!
```

## 📝 Исходный код

### Основной файл (src/main.c)

```c
#include "app.h"
#include <stdio.h>
#include <stdlib.h>
#include <signal.h>

// Глобальная переменная для обработки сигналов
volatile sig_atomic_t g_shutdown_requested = 0;

// Обработчик сигналов
void signal_handler(int signum) {
    g_shutdown_requested = 1;
    printf("\n🛑 Shutdown signal received...\n");
}

int main(int argc, char *argv[]) {
    printf("🚀 Starting Hello World Application...\n");

    // Регистрация обработчиков сигналов
    signal(SIGINT, signal_handler);
    signal(SIGTERM, signal_handler);

    // Инициализация приложения
    if (app_init("hello_world_app") != 0) {
        fprintf(stderr, "❌ Failed to initialize application\n");
        return EXIT_FAILURE;
    }

    printf("✅ DAP SDK initialized successfully\n");

    // Основной цикл приложения
    while (!g_shutdown_requested) {
        if (app_process() != 0) {
            fprintf(stderr, "❌ Application processing failed\n");
            break;
        }

        // Небольшая задержка для снижения нагрузки на CPU
        usleep(100000); // 100ms
    }

    // Завершение работы
    app_cleanup();
    printf("✅ Application finished successfully!\n");

    return EXIT_SUCCESS;
}
```

### Заголовочный файл (include/app.h)

```c
#pragma once

#include "dap_common.h"
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief Инициализация приложения
 * @param app_name Имя приложения
 * @return 0 при успехе, -1 при ошибке
 */
int app_init(const char *app_name);

/**
 * @brief Основная обработка приложения
 * @return 0 при успехе, -1 при ошибке
 */
int app_process(void);

/**
 * @brief Очистка ресурсов приложения
 */
void app_cleanup(void);

/**
 * @brief Получение информации о версии SDK
 * @return Строка с версией
 */
const char *app_get_sdk_version(void);

#ifdef __cplusplus
}
#endif
```

### Реализация (src/app.c)

```c
#include "app.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

// Статическая переменная для хранения версии
static char sdk_version[32] = {0};

int app_init(const char *app_name) {
    // Инициализация DAP SDK
    if (dap_common_init(app_name) != 0) {
        fprintf(stderr, "❌ Failed to initialize DAP SDK\n");
        return -1;
    }

    // Получение версии SDK
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
    // Имитация работы приложения
    static int counter = 0;

    // Вывод информации каждые 10 итераций
    if (counter % 10 == 0) {
        printf("🔄 Processing iteration: %d\n", counter);

        // Получение информации о памяти (пример)
        // В реальном приложении здесь была бы бизнес-логика
        printf("📊 Memory usage: %d KB\n", 1024 + (counter % 100));
    }

    counter++;
    return 0;
}

void app_cleanup(void) {
    printf("🛑 Shutting down gracefully...\n");

    // Очистка ресурсов DAP SDK
    dap_common_deinit();

    printf("✅ Cleanup completed\n");
}

const char *app_get_sdk_version(void) {
    return sdk_version;
}
```

## 🛠️ Конфигурация сборки

### CMakeLists.txt

```cmake
cmake_minimum_required(VERSION 3.10)
project(hello-world C)

# Поиск DAP SDK
find_package(DAP REQUIRED)

# Создание исполняемого файла
add_executable(${PROJECT_NAME}
    src/main.c
    src/app.c
)

# Подключение заголовочных файлов
target_include_directories(${PROJECT_NAME} PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/include
    ${DAP_INCLUDE_DIRS}
)

# Подключение библиотек DAP SDK
target_link_libraries(${PROJECT_NAME}
    dap_core
    dap_common
)

# Настройки компиляции
target_compile_options(${PROJECT_NAME} PRIVATE
    -Wall
    -Wextra
    -Wpedantic
    -O2
)

# Установка
install(TARGETS ${PROJECT_NAME}
    RUNTIME DESTINATION bin
)
```

## 🧪 Тестирование

### Базовые тесты

```c
// tests/test_app.c
#include "app.h"
#include "dap_test.h"

void test_app_init() {
    // Тест успешной инициализации
    int result = app_init("test_app");
    dap_assert(result == 0, "Application initialization should succeed");

    // Тест получения версии
    const char *version = app_get_sdk_version();
    dap_assert(version != NULL, "SDK version should be available");
    dap_assert(strlen(version) > 0, "SDK version should not be empty");

    // Очистка
    app_cleanup();
}

void test_app_process() {
    // Инициализация для тестирования
    app_init("test_app");

    // Тест обработки
    int result = app_process();
    dap_assert(result == 0, "Application processing should succeed");

    // Очистка
    app_cleanup();
}

int main() {
    dap_print_module_name("Hello World Tests");

    test_app_init();
    test_app_process();

    return 0;
}
```

### Запуск тестов

```bash
# Сборка и запуск тестов
cd build
make test_app
./test_app
```

## 🔧 Расширение функциональности

### Добавление логирования

```c
// В app.h добавить:
void app_log_info(const char *message);
void app_log_error(const char *message);

// В app.c добавить:
#include <stdarg.h>

void app_log_info(const char *message) {
    printf("ℹ️  [INFO] %s\n", message);
}

void app_log_error(const char *message) {
    fprintf(stderr, "❌ [ERROR] %s\n", message);
}
```

### Добавление конфигурации

```c
// В app.h добавить:
typedef struct {
    bool debug_mode;
    int log_level;
    char *config_file;
} app_config_t;

int app_load_config(app_config_t *config, const char *filename);

// В app.c добавить:
int app_load_config(app_config_t *config, const char *filename) {
    // Загрузка конфигурации из файла
    // (упрощенная реализация)
    config->debug_mode = true;
    config->log_level = 2;
    config->config_file = strdup(filename);
    return 0;
}
```

### Добавление многопоточности

```c
// В app.h добавить:
#include <pthread.h>

typedef struct {
    pthread_t thread;
    bool running;
    void *user_data;
} app_worker_t;

int app_start_worker(app_worker_t *worker);
void app_stop_worker(app_worker_t *worker);

// В app.c добавить:
void *worker_thread(void *arg) {
    app_worker_t *worker = (app_worker_t *)arg;

    while (worker->running) {
        // Работа потока
        app_process();
        usleep(10000); // 10ms
    }

    return NULL;
}

int app_start_worker(app_worker_t *worker) {
    worker->running = true;

    if (pthread_create(&worker->thread, NULL, worker_thread, worker) != 0) {
        return -1;
    }

    return 0;
}

void app_stop_worker(app_worker_t *worker) {
    worker->running = false;
    pthread_join(worker->thread, NULL);
}
```

## 📊 Профилирование

### Измерение производительности

```bash
# Сборка с отладочной информацией
cmake .. -DCMAKE_BUILD_TYPE=Debug -DCMAKE_EXPORT_COMPILE_COMMANDS=ON

# Профилирование с perf
perf record -g ./hello-world
perf report

# Анализ покрытия кода
gcovr -r .. .
```

### Мониторинг ресурсов

```c
// В app.c добавить функцию мониторинга
#include <sys/resource.h>

void app_print_resource_usage() {
    struct rusage usage;

    if (getrusage(RUSAGE_SELF, &usage) == 0) {
        printf("📊 Resource Usage:\n");
        printf("  User CPU time: %ld.%06ld sec\n",
               usage.ru_utime.tv_sec, usage.ru_utime.tv_usec);
        printf("  System CPU time: %ld.%06ld sec\n",
               usage.ru_stime.tv_sec, usage.ru_stime.tv_usec);
        printf("  Memory usage: %ld KB\n", usage.ru_maxrss);
    }
}
```

## 🔍 Отладка

### Запуск с отладчиком

```bash
# Сборка в режиме отладки
cmake .. -DCMAKE_BUILD_TYPE=Debug

# Запуск с gdb
gdb ./hello-world
(gdb) break main
(gdb) run
(gdb) print app_name
```

### Добавление отладочного вывода

```c
// В app.h добавить:
#ifdef DEBUG
#define APP_DEBUG(...) printf("🐛 [DEBUG] " __VA_ARGS__)
#else
#define APP_DEBUG(...)
#endif

// В коде использовать:
APP_DEBUG("Initializing with app_name: %s\n", app_name);
```

## 📚 Дополнительные материалы

### Следующие шаги изучения

1. **[Basic Wallet](../basic-wallet/)** - Управление кошельком
2. **[Simple Transaction](../simple-transaction/)** - Работа с транзакциями
3. **[Network Client](../network-client/)** - Сетевое взаимодействие

### Рекомендуемая литература

- [Архитектура DAP SDK](../../../architecture.md)
- [Руководство по API](../../../api/dap-sdk/core/)
- [Лучшие практики](../../../guides/best-practices.md)

## ❓ Вопросы и ответы

### Почему приложение завершается с кодом 1?
Убедитесь, что DAP SDK правильно установлен и все зависимости разрешены.

### Как изменить уровень логирования?
Используйте переменную окружения `DAP_LOG_LEVEL`:
```bash
export DAP_LOG_LEVEL=DEBUG
./hello-world
```

### Можно ли использовать этот пример в production?
Этот пример предназначен для обучения. Для production используйте более сложные примеры с обработкой ошибок и мониторингом.

## 🤝 Вклад в развитие

### Сообщение об ошибках
- Создайте issue на [GitHub](https://github.com/cellframe/libdap/issues)
- Опишите проблему детально
- Приложите логи и шаги воспроизведения

### Предложения по улучшению
- Fork репозиторий
- Создайте feature branch
- Внесите изменения
- Создайте Pull Request

---

## 🎯 Заключение

Этот пример демонстрирует основы работы с CellFrame DAP SDK:

- ✅ **Простая структура** - легко понять и модифицировать
- ✅ **Базовые концепции** - инициализация, обработка, завершение
- ✅ **Лучшие практики** - обработка сигналов, очистка ресурсов
- ✅ **Расширяемость** - легко добавить новую функциональность

**🚀 Теперь вы готовы создавать свои приложения на DAP SDK!**

**Следующий шаг: [Basic Wallet](../basic-wallet/) - управление криптовалютой**


