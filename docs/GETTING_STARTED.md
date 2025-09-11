# 🚀 CellFrame DAP SDK - Руководство по началу работы

## Введение

Добро пожаловать в **CellFrame DAP SDK** - мощную платформу для создания децентрализованных приложений! Это руководство поможет вам быстро начать разработку с использованием нашего SDK.

## 📋 Что такое CellFrame DAP SDK?

**CellFrame DAP SDK** - это комплексная платформа для разработки:

- ✅ **Блокчейн-приложений** с поддержкой множественных консенсусов
- ✅ **Децентрализованных сетей** с P2P коммуникациями
- ✅ **Криптографических решений** постквантовой безопасности
- ✅ **Масштабируемых систем** с высокой производительностью

## 🛠️ Быстрый старт

### 1. Системные требования

#### Минимальные требования:
- **ОС:** Linux (Ubuntu 18.04+), macOS (10.15+), Windows (10+)
- **Процессор:** 2-core CPU с поддержкой AVX2
- **Память:** 4 GB RAM
- **Диск:** 10 GB свободного места
- **Компилятор:** GCC 7+ / Clang 6+ / MSVC 2019+

#### Рекомендуемые требования:
- **ОС:** Ubuntu 20.04 LTS или новее
- **Процессор:** 4-core CPU с AVX2
- **Память:** 8 GB RAM
- **Диск:** SSD с 50 GB свободного места

### 2. Установка зависимостей

#### Ubuntu/Debian:
```bash
# Обновление системы
sudo apt update && sudo apt upgrade

# Основные зависимости
sudo apt install -y build-essential cmake git pkg-config

# Библиотеки для криптографии
sudo apt install -y libssl-dev libgmp-dev libsodium-dev

# Библиотеки для сетевых функций
sudo apt install -y libcurl4-openssl-dev libmicrohttpd-dev

# Библиотеки для баз данных
sudo apt install -y liblmdb-dev sqlite3 libsqlite3-dev

# Инструменты разработки
sudo apt install -y valgrind gdb clang-format
```

#### macOS:
```bash
# Установка Homebrew (если не установлен)
# /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Основные зависимости
brew install cmake pkg-config openssl gmp libsodium curl libmicrohttpd lmdb sqlite

# Инструменты разработки
brew install valgrind gdb clang-format
```

#### Windows:
```powershell
# Используйте vcpkg для управления зависимостями
# git clone https://github.com/Microsoft/vcpkg.git
# cd vcpkg && .\bootstrap-vcpkg.bat

# Установка зависимостей
.\vcpkg install --triplet=x64-windows openssl gmp libsodium curl libmicrohttpd lmdb sqlite3
```

### 3. Получение исходного кода

```bash
# Клонирование репозитория
git clone https://github.com/cellframe/libdap.git
cd libdap

# Переключение на стабильную ветку
git checkout master

# Инициализация подмодулей (если есть)
git submodule update --init --recursive
```

### 4. Сборка проекта

#### Стандартная сборка:

```bash
# Создание директории сборки
mkdir build && cd build

# Конфигурация CMake
cmake .. -DCMAKE_BUILD_TYPE=Release \
         -DDAP_BUILD_TESTS=ON \
         -DDAP_BUILD_EXAMPLES=ON \
         -DDAP_WITH_PYTHON=ON

# Сборка проекта
make -j$(nproc)

# Установка (опционально)
sudo make install
```

#### Сборка с отладочной информацией:

```bash
# Для разработки и отладки
mkdir build_debug && cd build_debug

cmake .. -DCMAKE_BUILD_TYPE=Debug \
         -DDAP_BUILD_TESTS=ON \
         -DDAP_BUILD_EXAMPLES=ON \
         -DDAP_WITH_PYTHON=ON \
         -DCMAKE_EXPORT_COMPILE_COMMANDS=ON

make -j$(nproc)
```

#### Кросс-компиляция для Raspberry Pi:

```bash
# Установка toolchain
sudo apt install -y gcc-arm-linux-gnueabihf g++-arm-linux-gnueabihf

# Сборка для ARM
mkdir build_arm && cd build_arm

cmake .. -DCMAKE_TOOLCHAIN_FILE=../cmake/Toolchain-rpi.cmake \
         -DCMAKE_BUILD_TYPE=Release

make -j$(nproc)
```

## 🏗️ Архитектура SDK

### Основные компоненты

```
CellFrame DAP SDK
├── DAP SDK Core          # Базовые функции и утилиты
├── DAP SDK Crypto        # Криптографические алгоритмы
├── DAP SDK Net           # Сетевая коммуникация
├── DAP SDK IO            # Асинхронный ввод/вывод
├── DAP SDK Global DB     # Распределенная база данных
├── CellFrame SDK         # Блокчейн-специфичные компоненты
│   ├── Chain            # Управление цепочками блоков
│   ├── Consensus        # Алгоритмы консенсуса
│   ├── Mempool          # Пул транзакций
│   └── Services         # Блокчейн-сервисы
└── Tools & Examples      # Инструменты и примеры
```

### Модульная архитектура

SDK построен по модульному принципу, что позволяет:

- **Гибкость:** Использовать только необходимые компоненты
- **Расширяемость:** Добавлять новые модули без изменения ядра
- **Изоляция:** Независимая разработка и тестирование модулей

## 💡 Первый пример - "Hello World"

### Создание простого приложения

1. **Создайте новый проект:**

```bash
mkdir my_first_dap_app
cd my_first_dap_app

# Создайте структуру проекта
mkdir src include cmake

# Создайте файлы
touch CMakeLists.txt
touch src/main.c
touch include/app.h
```

2. **Настройте CMakeLists.txt:**

```cmake
cmake_minimum_required(VERSION 3.10)
project(MyFirstDapApp C)

# Поиск DAP SDK
find_package(DAP REQUIRED)

# Создание исполняемого файла
add_executable(${PROJECT_NAME}
    src/main.c
)

# Подключение DAP SDK
target_link_libraries(${PROJECT_NAME}
    dap_core
    dap_crypto
    dap_net
)

# Настройка путей включения
target_include_directories(${PROJECT_NAME} PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/include
    ${DAP_INCLUDE_DIRS}
)
```

3. **Реализуйте основное приложение:**

```c
// include/app.h
#pragma once

#include "dap_common.h"

int app_init(void);
void app_deinit(void);
void app_run(void);

// src/main.c
#include "app.h"
#include <stdio.h>

int main(int argc, char *argv[]) {
    printf("🚀 Starting My First DAP Application...\n");

    // Инициализация приложения
    if (app_init() != 0) {
        fprintf(stderr, "❌ Failed to initialize application\n");
        return 1;
    }

    // Запуск основного цикла
    app_run();

    // Деинициализация
    app_deinit();

    printf("✅ Application finished successfully!\n");
    return 0;
}

int app_init(void) {
    // Инициализация DAP SDK компонентов
    if (dap_common_init("my_app") != 0) {
        return -1;
    }

    printf("✅ Application initialized\n");
    return 0;
}

void app_deinit(void) {
    // Очистка ресурсов
    dap_common_deinit();
    printf("✅ Application deinitialized\n");
}

void app_run(void) {
    // Основная логика приложения
    printf("🎯 Application is running!\n");
    printf("📚 DAP SDK Version: %s\n", dap_get_version());

    // Здесь будет ваша бизнес-логика
    // ...

    sleep(2); // Имитация работы
}
```

4. **Соберите и запустите:**

```bash
# Сборка
mkdir build && cd build
cmake ..
make

# Запуск
./MyFirstDapApp
```

**Ожидаемый вывод:**
```
🚀 Starting My First DAP Application...
✅ Application initialized
🎯 Application is running!
📚 DAP SDK Version: 2.3.0
✅ Application deinitialized
✅ Application finished successfully!
```

## 🔧 Следующие шаги

### 1. Изучите основные концепции

- **[Архитектура SDK](docs/architecture.md)** - Общее понимание системы
- **[Криптография](docs/modules/crypto.md)** - Работа с ключами и шифрованием
- **[Сетевое взаимодействие](docs/modules/net.md)** - P2P коммуникации

### 2. Освойте ключевые модули

- **[Core модуль](docs/modules/core.md)** - Базовые функции
- **[Chain модуль](docs/modules/chain.md)** - Работа с блокчейном
- **[Compose модуль](docs/modules/compose.md)** - Создание транзакций

### 3. Практические примеры

- **[Примеры приложений](docs/examples/)** - Готовые приложения
- **[Туториалы](docs/tutorials/)** - Пошаговые руководства
- **[Кейс-стади](docs/case-studies/)** - Реальные применения

## 🆘 Получение помощи

### Документация

- **[Полная документация](docs/)** - Детальное описание всех компонентов
- **[API Reference](docs/api/)** - Справка по функциям и структурам
- **[Руководства](docs/guides/)** - Специализированные руководства

### Сообщество

- **GitHub Issues** - Сообщения об ошибках и запросы на улучшения
- **GitHub Discussions** - Обсуждение идей и вопросов
- **Telegram чат** - Общение с сообществом разработчиков

### Техническая поддержка

```bash
# Получение информации о версии
./dap-cli --version

# Проверка конфигурации
./dap-cli config check

# Логи и диагностика
./dap-cli debug info
```

## 🎯 Что дальше?

### Для новичков:
1. **Изучите примеры** в директории `examples/`
2. **Пройдите туториалы** по основным концепциям
3. **Создайте свое первое приложение** на базе примеров

### Для опытных разработчиков:
1. **Изучите продвинутые возможности** SDK
2. **Освойте разработку плагинов** для расширения функциональности
3. **Участвуйте в развитии** проекта, внося свой вклад

### Для команд:
1. **Организуйте процесс разработки** с использованием наших инструментов
2. **Настройте CI/CD** для автоматического тестирования
3. **Интегрируйте SDK** в существующие проекты

---

**Готовы начать? Переходите к [следующему разделу](docs/tutorials/basic-concepts.md) для изучения основных концепций!** 🚀

**Если у вас возникли вопросы, не стесняйтесь обращаться в наше сообщество!** 💬

