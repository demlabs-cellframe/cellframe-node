# 🔍 Руководство по отладке и профилированию CellFrame DAP SDK

Это всеобъемлющее руководство по отладке, профилированию и оптимизации приложений, созданных с использованием CellFrame DAP SDK.

## 📋 Содержание

- [Быстрый старт в отладке](#быстрый-старт-в-отладке)
- [Настройка среды разработки](#настройка-среды-разработки)
- [Отладка с GDB](#отладка-с-gdb)
- [Санитайзеры памяти](#санитайзеры-памяти)
- [Профилирование производительности](#профилирование-производительности)
- [Анализ потребления памяти](#анализ-потребления-памяти)
- [Отладка сетевых проблем](#отладка-сетевых-проблем)
- [Дебаг многопоточных приложений](#дебаг-многопоточных-приложений)
- [Логирование и трассировка](#логирование-и-трассировка)
- [Инструменты анализа кода](#инструменты-анализа-кода)
- [Отладка в production](#отладка-в-production)

## 🚀 Быстрый старт в отладке

### 1. Сборка в режиме отладки

```bash
# Создание debug сборки
mkdir build_debug && cd build_debug
cmake .. -DCMAKE_BUILD_TYPE=Debug \
         -DDAP_BUILD_TESTS=ON \
         -DCMAKE_EXPORT_COMPILE_COMMANDS=ON
make -j$(nproc)
```

### 2. Запуск с базовой отладкой

```bash
# Запуск с gdb
gdb --args ./my_app --debug

# В gdb
(gdb) break main
(gdb) run
(gdb) print "Application started"
```

### 3. Проверка базовой функциональности

```c
// Добавьте в начало main()
#ifdef DEBUG
    printf("🐛 Debug mode enabled\n");
    printf("📍 PID: %d\n", getpid());
    printf("📂 CWD: %s\n", getcwd(NULL, 0));
#endif
```

## 🛠️ Настройка среды разработки

### Установка инструментов отладки

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y gdb valgrind kcachegrind \
                   perf-tools-unstable \
                   clang-tools \
                   cppcheck \
                   flawfinder \
                   strace \
                   ltrace

# macOS
brew install gdb valgrind llvm \
             perf gperftools \
             cppcheck flawfinder

# Инструменты для анализа покрытия
sudo apt install -y lcov gcovr
```

### Конфигурация CMake для отладки

```cmake
# В CMakeLists.txt добавьте:
option(ENABLE_DEBUG "Enable debug build" OFF)
option(ENABLE_ASAN "Enable Address Sanitizer" OFF)
option(ENABLE_TSAN "Enable Thread Sanitizer" OFF)
option(ENABLE_UBSAN "Enable Undefined Behavior Sanitizer" OFF)

if(ENABLE_DEBUG)
    set(CMAKE_BUILD_TYPE Debug)
    add_definitions(-DDEBUG)
    set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
endif()

if(ENABLE_ASAN)
    set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -fsanitize=address -fno-omit-frame-pointer")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fsanitize=address -fno-omit-frame-pointer")
endif()

if(ENABLE_TSAN)
    set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -fsanitize=thread")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fsanitize=thread")
endif()

if(ENABLE_UBSAN)
    set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -fsanitize=undefined")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fsanitize=undefined")
endif()
```

### Сборка с отладкой

```bash
# Сборка с различными режимами
mkdir build_asan && cd build_asan
cmake .. -DENABLE_DEBUG=ON -DENABLE_ASAN=ON
make -j$(nproc)

# Или для многопоточной отладки
mkdir build_tsan && cd build_tsan
cmake .. -DENABLE_DEBUG=ON -DENABLE_TSAN=ON
make -j$(nproc)
```

## 🐛 Отладка с GDB

### Основные команды GDB

```bash
# Запуск программы
gdb ./my_app
gdb --args ./my_app arg1 arg2

# Основные команды внутри gdb
(gdb) break main                    # Точка останова на main
(gdb) break my_function             # Точка останова на функции
(gdb) break my_file.c:42           # Точка останова на строке
(gdb) run                          # Запуск программы
(gdb) continue                     # Продолжение выполнения
(gdb) next                         # Следующая строка (без входа в функции)
(gdb) step                         # Следующая строка (с входом в функции)
(gdb) finish                       # Выход из текущей функции
(gdb) print variable               # Вывод значения переменной
(gdb) print *pointer               # Разыменование указателя
(gdb) backtrace                    # Стек вызовов
(gdb) frame N                      # Переход к кадру стека
(gdb) info locals                  # Локальные переменные
(gdb) info args                    # Аргументы функции
```

### Расширенная отладка

```bash
# Условные точки останова
(gdb) break my_function if x > 10

# Точки останова с командами
(gdb) break my_function
(gdb) commands
    printf "Function called with arg: %d\n", arg
    continue
end

# Watchpoints - отслеживание изменения переменных
(gdb) watch my_variable
(gdb) rwatch my_variable    # Только чтение
(gdb) awatch my_variable    # Чтение и запись

# Обработка сигналов
(gdb) handle SIGSEGV stop   # Останавливаться на segmentation fault
(gdb) handle SIGPIPE nostop # Игнорировать broken pipe

# Работа с потоками
(gdb) info threads          # Список потоков
(gdb) thread 2              # Переключение на поток 2
(gdb) thread apply all bt   # Стек вызовов всех потоков
```

### Отладка DAP SDK компонентов

```bash
# Отладка инициализации SDK
(gdb) break dap_common_init
(gdb) run

# Отладка сетевых операций
(gdb) break dap_client_connect
(gdb) break dap_stream_ch_packet_write

# Отладка работы с памятью
(gdb) break malloc
(gdb) break free
```

### Скрипты GDB

Создайте файл `.gdbinit` для автоматизации:

```gdb
# .gdbinit
set pagination off
set print pretty on
set print array on
set print array-indexes on

# Автоматическая загрузка символов
set auto-load safe-path /

# Пользовательские команды
define dap_debug
    printf "=== DAP SDK Debug Info ===\n"
    print dap_common_initialized
    print g_dap_log_level
end

# Автоматические точки останова для распространенных ошибок
break abort
break exit
catch throw
```

## 🧠 Санитайзеры памяти

### Address Sanitizer (ASan)

```bash
# Сборка с ASan
mkdir build_asan && cd build_asan
cmake .. -DENABLE_DEBUG=ON -DENABLE_ASAN=ON
make

# Запуск с ASan
./my_app

# Пример вывода ASan:
# =================================================================
# ==12345==ERROR: AddressSanitizer: heap-buffer-overflow
# WRITE of size 4 at 0x7f8b0c05a014
#     #0 0x55c5e8b4c2a1 in my_function (/path/to/my_app+0x12a1)
#     #1 0x55c5e8b4c345 in main (/path/to/my_app+0x1345)
# =================================================================
```

### Thread Sanitizer (TSan)

```bash
# Сборка с TSan
mkdir build_tsan && cd build_tsan
cmake .. -DENABLE_DEBUG=ON -DENABLE_TSAN=ON
make

# Запуск с TSan
./my_app

# Пример вывода TSan:
# ==================
# WARNING: ThreadSanitizer: data race
#   Write of size 8 at 0x7f8b0c05a000 by thread T1:
#     #0 my_write_function (/path/to/my_app+0x12a1)
#   Previous read of size 8 at 0x7f8b0c05a000 by thread T2:
#     #0 my_read_function (/path/to/my_app+0x1345)
# ==================
```

### Undefined Behavior Sanitizer (UBSan)

```bash
# Сборка с UBSan
mkdir build_ubsan && cd build_ubsan
cmake .. -DENABLE_DEBUG=ON -DENABLE_UBSAN=ON
make

# Запуск с UBSan
./my_app

# Пример вывода UBSan:
# runtime error: signed integer overflow: 2147483647 + 1 cannot be represented in type 'int'
```

### Leak Sanitizer (LSan)

```bash
# Сборка с LSan (включен в ASan)
mkdir build_lsan && cd build_lsan
cmake .. -DENABLE_DEBUG=ON -DENABLE_ASAN=ON
make

# Запуск с LSan
LSAN_OPTIONS=suppressions=lsan_suppressions.txt ./my_app

# Файл lsan_suppressions.txt
# leak:libdap.so
# leak:*alloc
```

## 📊 Профилирование производительности

### Perf - системный профилировщик

```bash
# Запись профиля
perf record -g ./my_app

# Анализ профиля
perf report

# Статистика по событиям
perf stat ./my_app

# Трассировка системных вызовов
perf trace ./my_app

# Анализ кэша
perf stat -e cache-misses ./my_app
```

### Callgrind - профилирование вызовов функций

```bash
# Запуск с callgrind
valgrind --tool=callgrind ./my_app

# Анализ результатов
callgrind_annotate callgrind.out.*

# Визуализация (требует kcachegrind)
kcachegrind callgrind.out.*
```

### Massif - анализ кучи

```bash
# Анализ использования кучи
valgrind --tool=massif ./my_app

# Визуализация
ms_print massif.out.*
```

### Бенчмаркинг DAP SDK

```c
// benchmark_dap.h
#pragma once

#include "dap_time.h"

// Простой бенчмарк
#define BENCHMARK_START(name) \
    dap_nanotime_t name##_start = dap_nanotime_now()

#define BENCHMARK_END(name) \
    do { \
        dap_nanotime_t name##_end = dap_nanotime_now(); \
        double name##_elapsed = (name##_end - name##_start) / 1000000.0; \
        printf("BENCHMARK %s: %.3f ms\n", #name, name##_elapsed); \
    } while(0)

// Детальный бенчмарк
typedef struct benchmark_result {
    const char *name;
    double min_time;
    double max_time;
    double avg_time;
    size_t iterations;
} benchmark_result_t;

benchmark_result_t *benchmark_run(const char *name,
                                 void (*func)(void),
                                 size_t iterations);
```

## 🧵 Дебаг многопоточных приложений

### Отладка race conditions

```c
// Добавьте отладочные метки
static pthread_mutex_t debug_mutex = PTHREAD_MUTEX_INITIALIZER;
static __thread int thread_id = 0;

void debug_thread_enter(const char *func_name) {
    pthread_mutex_lock(&debug_mutex);
    printf("Thread %d entering %s\n", thread_id, func_name);
    pthread_mutex_unlock(&debug_mutex);
}

void debug_thread_exit(const char *func_name) {
    pthread_mutex_lock(&debug_mutex);
    printf("Thread %d exiting %s\n", thread_id, func_name);
    pthread_mutex_unlock(&debug_mutex);
}
```

### Helgrind - обнаружение race conditions

```bash
# Запуск с helgrind
valgrind --tool=helgrind ./my_app

# Пример вывода:
# ==12345== ----------------------------------------------------------------
# ==12345== Possible data race during read of size 4 at 0x7f8b0c05a000
# ==12345== by thread #1
# ==12345== by thread #2
# ==12345== ----------------------------------------------------------------
```

### Отладка deadlock'ов

```c
// Детектор deadlock'ов
static pthread_mutex_t mutex1 = PTHREAD_MUTEX_INITIALIZER;
static pthread_mutex_t mutex2 = PTHREAD_MUTEX_INITIALIZER;

void safe_lock_debug(pthread_mutex_t *mutex, const char *name) {
    printf("Thread %ld trying to lock %s\n", pthread_self(), name);
    int result = pthread_mutex_lock(mutex);
    if (result == 0) {
        printf("Thread %ld locked %s\n", pthread_self(), name);
    } else {
        printf("Thread %ld failed to lock %s: %s\n",
               pthread_self(), name, strerror(result));
    }
}
```

## 🌐 Отладка сетевых проблем

### Wireshark для анализа трафика

```bash
# Захват трафика на интерфейсе
sudo wireshark

# Фильтры для DAP протокола
# tcp port 8081
# http contains "cellframe"

# Захват в файл для анализа
tcpdump -i eth0 -w capture.pcap tcp port 8081
```

### Отладка HTTP соединений

```bash
# Трассировка системных вызовов сети
strace -e trace=network ./my_app

# Отладка DNS
strace -e trace=getaddrinfo ./my_app

# Мониторинг открытых соединений
netstat -tlnp | grep :8081
ss -tlnp | grep :8081
```

### DAP SDK сетевой дебаг

```c
// Включение сетевого дебага
extern int g_dap_net_debug_more;
g_dap_net_debug_more = 1;

// Отладка клиентских соединений
dap_client_debug_enable(true);

// Отладка серверных соединений
dap_server_debug_enable(true);
```

## 📝 Логирование и трассировка

### Уровни логирования DAP SDK

```c
// Установка уровня логирования
dap_log_set_level(L_DEBUG);

// Логирование с уровнями
DAP_LOG_DEBUG("Debug message: %s", debug_info);
DAP_LOG_INFO("Info message: %d", value);
DAP_LOG_WARNING("Warning message");
DAP_LOG_ERROR("Error message: %s", error_str);
```

### Создание трассировочного лога

```c
// Трассировка функций
#define TRACE_ENTER() \
    DAP_LOG_DEBUG("ENTER: %s:%d %s", __FILE__, __LINE__, __FUNCTION__)

#define TRACE_EXIT() \
    DAP_LOG_DEBUG("EXIT: %s:%d %s", __FILE__, __LINE__, __FUNCTION__)

void my_function() {
    TRACE_ENTER();

    // Код функции

    TRACE_EXIT();
}
```

### Структурированное логирование

```c
// JSON логирование
typedef struct log_entry {
    const char *timestamp;
    const char *level;
    const char *component;
    const char *message;
    const char *function;
    int line;
    const char *thread_id;
} log_entry_t;

void log_structured(log_entry_t *entry) {
    printf("{\"timestamp\":\"%s\",\"level\":\"%s\",\"component\":\"%s\","
           "\"message\":\"%s\",\"function\":\"%s\",\"line\":%d,"
           "\"thread_id\":\"%s\"}\n",
           entry->timestamp, entry->level, entry->component,
           entry->message, entry->function, entry->line,
           entry->thread_id);
}
```

## 🔧 Инструменты анализа кода

### Cppcheck - статический анализ

```bash
# Базовый анализ
cppcheck --enable=all --std=c99 src/

# Детальный анализ с подавлением предупреждений
cppcheck --enable=all --std=c99 --suppress=unusedFunction src/

# Анализ с правилами MISRA C
cppcheck --enable=all --std=c99 --addon=misra_c_2012 src/

# Генерация XML отчета
cppcheck --enable=all --std=c99 --xml src/ 2> cppcheck_results.xml
```

### Flawfinder - поиск уязвимостей

```bash
# Поиск потенциальных уязвимостей
flawfinder src/

# Детальный анализ
flawfinder -D -c src/

# С фокусом на определенные типы уязвимостей
flawfinder --inputs src/  # Фокус на input функциях
```

### Clang Static Analyzer

```bash
# Анализ с clang
scan-build make

# Детальный анализ
scan-build -v make

# С пользовательскими чекерами
scan-build --use-analyzer=/usr/bin/clang make
```

### Coverage анализ

```bash
# Сборка с покрытием
mkdir build_coverage && cd build_coverage
cmake .. -DCMAKE_BUILD_TYPE=Debug -DENABLE_COVERAGE=ON
make

# Запуск тестов
make test

# Генерация отчета о покрытии
lcov --capture --directory . --output-file coverage.info
genhtml coverage.info --output-directory coverage_report

# Просмотр результатов
firefox coverage_report/index.html
```

## 🚀 Отладка в production

### Core dumps

```bash
# Включение core dumps
ulimit -c unlimited

# Настройка пути для core dumps
echo "core.%e.%p.%t" > /proc/sys/kernel/core_pattern

# Анализ core dump
gdb ./my_app core.my_app.1234.1640995200

# В gdb
(gdb) bt           # Стек вызовов
(gdb) info threads # Потоки
(gdb) print var    # Переменные
```

### Remote debugging

```bash
# На production сервере
gdbserver :9090 ./my_app

# На локальной машине
gdb ./my_app
(gdb) target remote production-server:9090
(gdb) continue
```

### Logging в production

```c
// Production-ready логирование
typedef struct prod_logger {
    FILE *log_file;
    pthread_mutex_t mutex;
    bool async_mode;
    int max_file_size;
    int max_files;
} prod_logger_t;

// Асинхронное логирование для production
void prod_log_async(prod_logger_t *logger, const char *level,
                   const char *format, ...) {
    // Буферизация и асинхронная запись
    va_list args;
    va_start(args, format);

    char *buffer = malloc(4096);
    vsnprintf(buffer, 4096, format, args);

    // Добавление в очередь для асинхронной записи
    log_queue_add(logger, level, buffer);

    va_end(args);
}
```

### Monitoring и alerting

```c
// Health check endpoints
void health_check_handler(dap_http_client_t *client, void *arg) {
    // Проверка состояния компонентов
    bool db_ok = check_database_connection();
    bool network_ok = check_network_connectivity();
    bool memory_ok = check_memory_usage();

    if (db_ok && network_ok && memory_ok) {
        client->out_status = 200;
        client->out_body = (uint8_t *)strdup("OK");
    } else {
        client->out_status = 503;
        client->out_body = (uint8_t *)strdup("Service Unavailable");
    }
}

// Metrics collection
typedef struct app_metrics {
    uint64_t requests_total;
    uint64_t requests_failed;
    uint64_t response_time_sum;
    uint64_t active_connections;
    // ... другие метрики
} app_metrics_t;

// Экспорт метрик в Prometheus формате
void export_prometheus_metrics(app_metrics_t *metrics) {
    printf("# HELP requests_total Total number of requests\n");
    printf("# TYPE requests_total counter\n");
    printf("requests_total %llu\n", metrics->requests_total);

    printf("# HELP response_time_avg Average response time\n");
    printf("# TYPE response_time_avg gauge\n");
    printf("response_time_avg %.2f\n",
           (double)metrics->response_time_sum / metrics->requests_total);
}
```

## 🐛 Распространенные проблемы и решения

### Проблема: Segmentation Fault

```bash
# Анализ с valgrind
valgrind --tool=memcheck --leak-check=full ./my_app

# Отладка с gdb
gdb ./my_app
(gdb) run
(gdb) bt  # Показать стек вызовов при падении
```

### Проблема: Memory Leaks

```bash
# Поиск утечек
valgrind --tool=memcheck --leak-check=full --show-leak-kinds=all ./my_app

# Трекинг аллокаций
valgrind --tool=massif ./my_app
ms_print massif.out.*
```

### Проблема: Deadlocks

```bash
# Обнаружение deadlock'ов
valgrind --tool=helgrind ./my_app

# Анализ с gdb
gdb ./my_app
(gdb) info threads
(gdb) thread apply all bt
```

### Проблема: Performance Degradation

```bash
# Профилирование CPU
perf record -g ./my_app
perf report

# Профилирование памяти
valgrind --tool=massif ./my_app

# Системный мониторинг
vmstat 1
iostat 1
```

## 📚 Полезные ссылки

### Официальная документация
- [GDB Manual](https://sourceware.org/gdb/current/onlinedocs/gdb/)
- [Valgrind Manual](https://valgrind.org/docs/manual/manual.html)
- [Perf Manual](https://perf.wiki.kernel.org/index.php/Main_Page)

### Инструменты
- [Cppcheck](http://cppcheck.sourceforge.net/)
- [Flawfinder](https://dwheeler.com/flawfinder/)
- [Clang Static Analyzer](https://clang-analyzer.llvm.org/)

### Сообщество
- [Stack Overflow - C Debugging](https://stackoverflow.com/questions/tagged/c+debugging)
- [Reddit - C Programming](https://www.reddit.com/r/C_Programming/)

## 🎯 Лучшие практики отладки

### 1. Профилактика
```c
// Всегда проверяйте возвращаемые значения
int result = some_function();
if (result != SUCCESS) {
    DAP_LOG_ERROR("Function failed: %d", result);
    return result;
}

// Используйте assert в debug сборках
assert(ptr != NULL);
assert(value >= 0);
```

### 2. Структурированное логирование
```c
// Логируйте входы/выходы функций
DAP_LOG_DEBUG("Enter function: param=%d", param);

// Логируйте важные состояния
DAP_LOG_INFO("Processing %zu items", item_count);

// Логируйте ошибки с контекстом
DAP_LOG_ERROR("Database connection failed: %s (errno=%d)",
              strerror(errno), errno);
```

### 3. Автоматизированное тестирование
```c
// Unit тесты для всех функций
void test_my_function() {
    // Arrange
    int input = 42;
    int expected = 84;

    // Act
    int result = my_function(input);

    // Assert
    dap_assert(result == expected, "Function should double input");
}
```

### 4. CI/CD интеграция
```yaml
# .github/workflows/debug.yml
name: Debug Build
on: [push, pull_request]

jobs:
  debug:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Setup
      run: sudo apt install -y valgrind cppcheck
    - name: Build Debug
      run: |
        mkdir build && cd build
        cmake .. -DENABLE_DEBUG=ON -DENABLE_ASAN=ON
        make -j$(nproc)
    - name: Run Tests with Sanitizers
      run: |
        cd build
        ctest --output-on-failure
    - name: Static Analysis
      run: cppcheck --enable=all --std=c99 src/
```

---

## 🎉 Заключение

Эффективная отладка и профилирование - ключ к созданию надежных и высокопроизводительных приложений на CellFrame DAP SDK. Используйте комбинацию инструментов и следуйте лучшим практикам для достижения наилучших результатов.

**🐛 Помните:** "Лучший способ найти баг - это иметь хорошую систему отладки!"

**📞 Нужна помощь?** Обратитесь в [техническую поддержку](https://cellframe.net/support) или наше [сообщество разработчиков](https://t.me/cellframe_dev).
