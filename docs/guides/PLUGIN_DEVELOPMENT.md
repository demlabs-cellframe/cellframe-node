# 🔌 Руководство по разработке плагинов CellFrame DAP SDK

## Введение

Плагины в CellFrame DAP SDK предоставляют мощный механизм для расширения функциональности системы без изменения основного кода. Это руководство поможет вам создать свой первый плагин и освоить продвинутые техники разработки.

## 🎯 Что такое плагины?

**Плагины** - это динамически загружаемые модули, которые:

- ✅ **Расширяют функциональность** без изменения ядра
- ✅ **Загружаются во время выполнения** (hot-plugging)
- ✅ **Изолированы** от основного приложения
- ✅ **Могут быть обновлены** без перезапуска системы
- ✅ **Обеспечивают модульность** и гибкость архитектуры

## 🏗️ Архитектура плагинов

### Основные компоненты

```
Plugin System
├── Plugin Manager          # Управление жизненным циклом
├── Plugin Manifest         # Метаданные плагина
├── Plugin Loader           # Загрузка и выгрузка
├── Type System            # Типизация плагинов
├── Dependency Resolver    # Разрешение зависимостей
└── Security Framework     # Безопасность и изоляция
```

### Типы плагинов

1. **Модульные плагины** - расширяют базовую функциональность
2. **Сервисные плагины** - предоставляют сервисы приложению
3. **Драйверные плагины** - интерфейсы к внешним системам
4. **UI плагины** - расширяют пользовательский интерфейс
5. **Интеграционные плагины** - связывают с внешними сервисами

## 🚀 Создание первого плагина

### 1. Настройка структуры проекта

```bash
# Создание директории плагина
mkdir my_first_plugin
cd my_first_plugin

# Создание структуры
mkdir src include cmake tests docs

# Основные файлы
touch CMakeLists.txt
touch manifest.json
touch src/plugin.c
touch include/plugin.h
touch README.md
```

### 2. Создание манифеста плагина

```json
// manifest.json
{
  "name": "my_first_plugin",
  "version": "1.0.0",
  "author": "Your Name",
  "description": "My first CellFrame DAP SDK plugin",
  "type": "module",
  "dependencies": ["core", "net"],
  "permissions": ["network", "storage"],
  "entry_point": "my_plugin_init",
  "unload_function": "my_plugin_deinit",
  "config_schema": {
    "properties": {
      "debug_mode": {
        "type": "boolean",
        "default": false
      },
      "max_connections": {
        "type": "integer",
        "minimum": 1,
        "maximum": 1000,
        "default": 100
      }
    }
  }
}
```

### 3. Реализация основного кода плагина

```c
// include/plugin.h
#pragma once

#include "dap_plugin.h"
#include "dap_config.h"

#ifdef __cplusplus
extern "C" {
#endif

// Структура данных плагина
typedef struct my_plugin_data {
    bool debug_mode;
    int max_connections;
    void *custom_data;
    // ... другие поля
} my_plugin_data_t;

// Экспортируемые функции
int my_plugin_init(dap_plugin_manifest_t *manifest,
                   void **pvt_data,
                   char **error_str);

int my_plugin_deinit(dap_plugin_manifest_t *manifest,
                     void *pvt_data,
                     char **error_str);

// Вспомогательные функции
void my_plugin_process_data(my_plugin_data_t *data, const void *input, size_t size);
void my_plugin_log_debug(my_plugin_data_t *data, const char *message);

#ifdef __cplusplus
}
#endif
```

```c
// src/plugin.c
#include "plugin.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// Callback загрузки плагина
int my_plugin_init(dap_plugin_manifest_t *manifest,
                   void **pvt_data,
                   char **error_str) {

    printf("🚀 Initializing My First Plugin v%s\n", manifest->version);

    // Выделение памяти для данных плагина
    my_plugin_data_t *data = calloc(1, sizeof(my_plugin_data_t));
    if (!data) {
        *error_str = strdup("Failed to allocate plugin data");
        return -1;
    }

    // Загрузка конфигурации
    if (manifest->config) {
        data->debug_mode = dap_config_get_bool(manifest->config,
                                               "debug_mode", false);
        data->max_connections = dap_config_get_int(manifest->config,
                                                   "max_connections", 100);
    }

    // Инициализация внутренних структур
    data->custom_data = my_plugin_create_custom_data();
    if (!data->custom_data) {
        free(data);
        *error_str = strdup("Failed to initialize custom data");
        return -1;
    }

    *pvt_data = data;

    if (data->debug_mode) {
        printf("🐛 Debug mode enabled\n");
    }

    printf("✅ Plugin initialized successfully\n");
    return 0;
}

// Callback выгрузки плагина
int my_plugin_deinit(dap_plugin_manifest_t *manifest,
                     void *pvt_data,
                     char **error_str) {

    printf("🛑 Deinitializing My First Plugin\n");

    if (!pvt_data) {
        return 0; // Нечего очищать
    }

    my_plugin_data_t *data = (my_plugin_data_t *)pvt_data;

    // Очистка ресурсов
    if (data->custom_data) {
        my_plugin_destroy_custom_data(data->custom_data);
    }

    free(data);

    printf("✅ Plugin deinitialized successfully\n");
    return 0;
}

// Вспомогательная функция обработки данных
void my_plugin_process_data(my_plugin_data_t *data,
                           const void *input,
                           size_t size) {

    if (data->debug_mode) {
        printf("📦 Processing %zu bytes of data\n", size);
    }

    // Здесь ваша логика обработки данных
    // ...

    if (data->debug_mode) {
        printf("✅ Data processing completed\n");
    }
}

// Вспомогательная функция логирования
void my_plugin_log_debug(my_plugin_data_t *data, const char *message) {
    if (data->debug_mode) {
        printf("🐛 [PLUGIN DEBUG] %s\n", message);
    }
}

// Внутренняя функция создания данных
static void *my_plugin_create_custom_data() {
    // Создание внутренних структур
    return calloc(1, sizeof(int)); // Пример
}

// Внутренняя функция уничтожения данных
static void my_plugin_destroy_custom_data(void *data) {
    free(data);
}
```

### 4. Настройка сборки с CMake

```cmake
# CMakeLists.txt
cmake_minimum_required(VERSION 3.10)
project(my_first_plugin C)

# Поиск DAP SDK
find_package(DAP REQUIRED)

# Создание shared library
add_library(${PROJECT_NAME} SHARED
    src/plugin.c
)

# Подключение заголовочных файлов
target_include_directories(${PROJECT_NAME} PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/include
    ${DAP_INCLUDE_DIRS}
)

# Подключение библиотек DAP SDK
target_link_libraries(${PROJECT_NAME}
    dap_core
    dap_plugin
    dap_config
    # ... другие необходимые библиотеки
)

# Настройки компиляции
target_compile_options(${PROJECT_NAME} PRIVATE
    -Wall
    -Wextra
    -Wpedantic
    -fPIC
)

# Установка плагина
install(TARGETS ${PROJECT_NAME}
    LIBRARY DESTINATION lib/dap/plugins
)

# Установка манифеста
install(FILES manifest.json
    DESTINATION share/dap/plugins/${PROJECT_NAME}
)
```

### 5. Создание файла сборки

```bash
#!/bin/bash
# build.sh

# Создание директории сборки
mkdir -p build
cd build

# Конфигурация и сборка
cmake .. -DCMAKE_BUILD_TYPE=Release
make -j$(nproc)

# Установка (опционально)
# sudo make install

echo "Plugin built successfully!"
```

## 🔧 Продвинутые возможности

### Работа с событиями

```c
// Регистрация обработчика событий
typedef void (*event_callback_t)(const char *event_type, void *event_data);

int my_plugin_register_event_handler(my_plugin_data_t *data) {
    // Регистрация callback для сетевых событий
    return dap_events_subscribe("network_packet_received",
                               my_network_event_handler,
                               data);
}

void my_network_event_handler(const char *event_type, void *event_data) {
    my_plugin_data_t *data = (my_plugin_data_t *)event_data;

    if (strcmp(event_type, "network_packet_received") == 0) {
        // Обработка сетевого пакета
        my_plugin_process_network_packet(data, event_data);
    }
}
```

### Работа с базой данных

```c
// Сохранение данных в Global DB
int my_plugin_save_data(my_plugin_data_t *data, const char *key, const void *value, size_t size) {
    return dap_global_db_set_sync("my_plugin_data", key, value, size, true);
}

// Загрузка данных из Global DB
void *my_plugin_load_data(my_plugin_data_t *data, const char *key, size_t *size) {
    return dap_global_db_get_sync("my_plugin_data", key, size, NULL, NULL);
}
```

### Создание RPC интерфейса

```c
// Регистрация RPC методов
int my_plugin_register_rpc_methods(my_plugin_data_t *data) {
    // Регистрация метода получения статуса
    dap_json_rpc_register_method("plugin.getStatus",
                                my_rpc_get_status,
                                data);

    // Регистрация метода настройки
    dap_json_rpc_register_method("plugin.configure",
                                my_rpc_configure,
                                data);

    return 0;
}

// RPC обработчик статуса
void my_rpc_get_status(dap_json_rpc_params_t *params,
                      dap_json_rpc_response_t *response,
                      const char *method) {

    my_plugin_data_t *data = (my_plugin_data_t *)params->user_data;

    // Создание ответа
    json_object *result = json_object_new_object();
    json_object_object_add(result, "status", json_object_new_string("active"));
    json_object_object_add(result, "version", json_object_new_string("1.0.0"));
    json_object_object_add(result, "connections", json_object_new_int(data->max_connections));

    response->result = result;
    response->error_code = 0;
}
```

### Многопоточность и синхронизация

```c
// Потокобезопасная структура данных
typedef struct thread_safe_data {
    int value;
    pthread_mutex_t mutex;
} thread_safe_data_t;

// Инициализация
int init_thread_safe_data(thread_safe_data_t *data) {
    data->value = 0;
    return pthread_mutex_init(&data->mutex, NULL);
}

// Потокобезопасный доступ
void set_value_thread_safe(thread_safe_data_t *data, int new_value) {
    pthread_mutex_lock(&data->mutex);
    data->value = new_value;
    pthread_mutex_unlock(&data->mutex);
}

int get_value_thread_safe(thread_safe_data_t *data) {
    pthread_mutex_lock(&data->mutex);
    int value = data->value;
    pthread_mutex_unlock(&data->mutex);
    return value;
}
```

## 📋 Лучшие практики разработки плагинов

### 1. Обработка ошибок

```c
// Правильная обработка ошибок
int my_plugin_operation(my_plugin_data_t *data) {
    if (!data) {
        return MY_PLUGIN_ERROR_INVALID_DATA;
    }

    // Попытка выполнения операции
    int result = perform_operation(data);
    if (result != 0) {
        my_plugin_log_error(data, "Operation failed");
        return MY_PLUGIN_ERROR_OPERATION_FAILED;
    }

    return MY_PLUGIN_SUCCESS;
}
```

### 2. Управление памятью

```c
// RAII паттерн для ресурсов
typedef struct resource_guard {
    void *resource;
    void (*cleanup)(void *);
} resource_guard_t;

void resource_guard_init(resource_guard_t *guard,
                        void *resource,
                        void (*cleanup)(void *)) {
    guard->resource = resource;
    guard->cleanup = cleanup;
}

void resource_guard_cleanup(resource_guard_t *guard) {
    if (guard->resource && guard->cleanup) {
        guard->cleanup(guard->resource);
        guard->resource = NULL;
    }
}

// Использование
void my_plugin_safe_operation(my_plugin_data_t *data) {
    void *temp_resource = allocate_resource();
    resource_guard_t guard;
    resource_guard_init(&guard, temp_resource, free_resource);

    // Работа с ресурсом
    if (use_resource(temp_resource) != 0) {
        // Ошибка - ресурс будет автоматически очищен
        return;
    }

    // Явная очистка при успехе
    resource_guard_cleanup(&guard);
}
```

### 3. Логирование

```c
// Структурированное логирование
typedef enum {
    LOG_LEVEL_DEBUG,
    LOG_LEVEL_INFO,
    LOG_LEVEL_WARNING,
    LOG_LEVEL_ERROR
} log_level_t;

void my_plugin_log(my_plugin_data_t *data, log_level_t level,
                  const char *format, ...) {

    if (!data->debug_mode && level == LOG_LEVEL_DEBUG) {
        return; // Пропуск отладочных сообщений
    }

    va_list args;
    va_start(args, format);

    // Форматирование сообщения с меткой времени
    time_t now = time(NULL);
    char timestamp[32];
    strftime(timestamp, sizeof(timestamp), "%Y-%m-%d %H:%M:%S", localtime(&now));

    fprintf(stderr, "[%s] [PLUGIN] ", timestamp);

    switch (level) {
        case LOG_LEVEL_DEBUG:   fprintf(stderr, "[DEBUG] "); break;
        case LOG_LEVEL_INFO:    fprintf(stderr, "[INFO] "); break;
        case LOG_LEVEL_WARNING: fprintf(stderr, "[WARN] "); break;
        case LOG_LEVEL_ERROR:   fprintf(stderr, "[ERROR] "); break;
    }

    vfprintf(stderr, format, args);
    fprintf(stderr, "\n");

    va_end(args);
}
```

### 4. Конфигурация

```c
// Гибкая система конфигурации
typedef struct plugin_config {
    bool debug_mode;
    int max_connections;
    char *log_file;
    int log_level;
    // ... другие параметры
} plugin_config_t;

// Загрузка конфигурации с валидацией
int load_plugin_config(dap_config_t *config, plugin_config_t *plugin_config) {
    // Загрузка с значениями по умолчанию
    plugin_config->debug_mode = dap_config_get_bool(config, "debug_mode", false);
    plugin_config->max_connections = dap_config_get_int(config, "max_connections", 100);

    // Загрузка строковых значений
    const char *log_file = dap_config_get_string(config, "log_file", NULL);
    if (log_file) {
        plugin_config->log_file = strdup(log_file);
    }

    // Валидация значений
    if (plugin_config->max_connections < 1 || plugin_config->max_connections > 10000) {
        return -1; // Недопустимое значение
    }

    return 0;
}
```

## 🧪 Тестирование плагинов

### Unit-тесты

```c
// test_plugin.c
#include "plugin.h"
#include "dap_test.h"

// Тест инициализации
void test_plugin_init() {
    my_plugin_data_t *data = NULL;
    char *error = NULL;

    // Создание mock манифеста
    dap_plugin_manifest_t manifest = {
        .name = "test_plugin",
        .version = "1.0.0"
    };

    int result = my_plugin_init(&manifest, (void **)&data, &error);
    dap_assert(result == 0, "Plugin initialization should succeed");
    dap_assert(data != NULL, "Plugin data should be allocated");

    // Очистка
    if (data) {
        my_plugin_deinit(&manifest, data, &error);
    }
    if (error) free(error);
}

// Тест обработки данных
void test_data_processing() {
    my_plugin_data_t data = {.debug_mode = true};
    const char *test_input = "Hello, Plugin!";
    const size_t input_size = strlen(test_input);

    // Этот тест проверяет, что функция не падает
    my_plugin_process_data(&data, test_input, input_size);
    dap_pass_msg("Data processing test passed");
}

int main() {
    dap_print_module_name("Plugin Tests");

    test_plugin_init();
    test_data_processing();

    return 0;
}
```

### Интеграционные тесты

```bash
#!/bin/bash
# test_integration.sh

echo "Running plugin integration tests..."

# Загрузка плагина
./dap-cli plugin load my_first_plugin

# Проверка статуса
status=$(./dap-cli plugin status my_first_plugin)
if [ "$status" != "loaded" ]; then
    echo "Plugin failed to load"
    exit 1
fi

# Тестирование функциональности
./dap-cli plugin test my_first_plugin

# Выгрузка плагина
./dap-cli plugin unload my_first_plugin

echo "Integration tests passed!"
```

## 📦 Упаковка и распространение

### Создание пакета плагина

```bash
#!/bin/bash
# package_plugin.sh

PLUGIN_NAME="my_first_plugin"
VERSION="1.0.0"

# Создание директории пакета
mkdir -p package/${PLUGIN_NAME}-${VERSION}

# Копирование файлов
cp build/lib${PLUGIN_NAME}.so package/${PLUGIN_NAME}-${VERSION}/
cp manifest.json package/${PLUGIN_NAME}-${VERSION}/
cp README.md package/${PLUGIN_NAME}-${VERSION}/
cp -r docs package/${PLUGIN_NAME}-${VERSION}/

# Создание архива
cd package
tar -czf ${PLUGIN_NAME}-${VERSION}.tar.gz ${PLUGIN_NAME}-${VERSION}

echo "Plugin package created: ${PLUGIN_NAME}-${VERSION}.tar.gz"
```

### Структура пакета

```
my_first_plugin-1.0.0/
├── libmy_first_plugin.so     # Бинарная библиотека
├── manifest.json            # Манифест плагина
├── README.md                # Документация
├── docs/                    # Дополнительная документация
│   ├── api.md
│   ├── examples.md
│   └── changelog.md
└── config/                  # Конфигурационные файлы
    └── default.cfg
```

## 🔒 Безопасность плагинов

### Аудит кода

```bash
# Статический анализ кода
cppcheck --enable=all --std=c99 src/

# Поиск уязвимостей
flawfinder src/

# Проверка на утечки памяти
valgrind --leak-check=full ./test_plugin
```

### Безопасная загрузка

```c
// Проверка целостности плагина
int verify_plugin_signature(const char *plugin_path,
                           const char *signature_path) {

    // Загрузка подписи
    dap_sign_t *signature = dap_sign_load_from_file(signature_path);
    if (!signature) {
        return -1;
    }

    // Вычисление хэша плагина
    dap_hash_fast_t plugin_hash;
    if (dap_hash_file(plugin_path, &plugin_hash) != 0) {
        dap_sign_free(signature);
        return -1;
    }

    // Верификация подписи
    int result = dap_sign_verify(signature, &plugin_hash, sizeof(plugin_hash));

    dap_sign_free(signature);
    return result;
}
```

### Изоляция ресурсов

```c
// Ограничение ресурсов плагина
typedef struct resource_limits {
    size_t max_memory;        // Максимальный объем памяти
    size_t max_cpu_time;      // Максимальное CPU время
    size_t max_file_descriptors; // Максимум файловых дескрипторов
    size_t max_threads;       // Максимум потоков
} resource_limits_t;

int enforce_resource_limits(pid_t plugin_pid, resource_limits_t *limits) {
    // Установка лимитов через cgroups или другие механизмы
    // ...
    return 0;
}
```

## 🎯 Расширенные сценарии

### Плагин для кастомного консенсуса

```c
// Регистрация нового алгоритма консенсуса
int consensus_plugin_init(dap_plugin_manifest_t *manifest,
                         void **pvt_data, char **error_str) {

    consensus_plugin_data_t *data = calloc(1, sizeof(consensus_plugin_data_t));

    // Регистрация алгоритма
    int result = dap_consensus_register_algorithm(
        "my_custom_consensus",
        my_consensus_init,
        my_consensus_process_block,
        my_consensus_validate,
        data
    );

    if (result != 0) {
        *error_str = strdup("Failed to register consensus algorithm");
        free(data);
        return -1;
    }

    *pvt_data = data;
    return 0;
}
```

### Плагин для внешней интеграции

```c
// Интеграция с внешним сервисом
int integration_plugin_init(dap_plugin_manifest_t *manifest,
                           void **pvt_data, char **error_str) {

    integration_data_t *data = calloc(1, sizeof(integration_data_t));

    // Инициализация HTTP клиента
    data->http_client = dap_http_client_init();
    if (!data->http_client) {
        *error_str = strdup("Failed to initialize HTTP client");
        free(data);
        return -1;
    }

    // Регистрация webhook обработчика
    dap_http_server_add_proc(data->http_server, "/webhook",
                             webhook_handler, data, NULL, NULL, NULL);

    *pvt_data = data;
    return 0;
}
```

## 🔧 Отладка и профилирование

### Отладка плагинов

```bash
# Запуск с отладчиком
gdb --args ./dap-node --plugin my_first_plugin --debug

# Внутри gdb
(gdb) break my_plugin_init
(gdb) run
(gdb) print *data
```

### Профилирование производительности

```bash
# Профилирование с perf
perf record -g ./dap-node --plugin my_first_plugin
perf report

# Анализ потребления памяти
valgrind --tool=massif ./dap-node --plugin my_first_plugin
ms_print massif.out.*
```

## 📚 Дополнительные ресурсы

### Примеры плагинов
- **[Базовый плагин](examples/plugins/basic/)** - Простой шаблон
- **[Сетевой плагин](examples/plugins/network/)** - Работа с сетью
- **[Крипто плагин](examples/plugins/crypto/)** - Криптографические функции
- **[Сервисный плагин](examples/plugins/service/)** - Предоставление сервисов

### Документация
- **[Plugin API](api/plugin/)** - Полная спецификация API
- **[Manifest Format](specs/manifest-format.md)** - Формат манифеста
- **[Security Guidelines](security/plugin-security.md)** - Руководство по безопасности

## 🚀 Следующие шаги

1. **Изучите существующие плагины** в директории examples
2. **Создайте свой первый плагин** используя этот шаблон
3. **Протестируйте плагин** в изолированной среде
4. **Опубликуйте плагин** в репозитории сообщества
5. **Участвуйте в развитии** экосистемы плагинов

---

**💡 Помните:** Плагины позволяют расширять функциональность DAP SDK без изменения ядра, обеспечивая модульность и гибкость системы.

**🔗 Полезные ссылки:**
- [Plugin Examples](examples/plugins/)
- [Plugin API Documentation](api/plugin/)
- [Community Plugins](https://github.com/cellframe/dap-plugins)

**🎯 Готовы создать свой плагин? Начните с [базового шаблона](examples/plugins/basic/)!**
