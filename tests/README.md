# CellFrame Node Integration Tests

🧪 **Интеграционные и E2E тесты для CellFrame Node**

## 📋 Описание

Эта папка содержит высокоуровневые тесты для CellFrame Node:
- **Интеграционные тесты**: Проверка взаимодействия компонентов
- **E2E тесты**: Полные сценарии работы пользователя
- **Тесты плагинов**: Загрузка и работа плагинов
- **Тесты API**: Проверка внешних интерфейсов

## 🏗️ Структура

```
tests/
├── unit/                  # Модульные тесты (если нужны)
├── integration/           # Интеграционные тесты
│   ├── test_node_startup.sh      # Запуск и остановка ноды
│   ├── test_binary_plugins.sh    # Загрузка бинарных плагинов
│   ├── test_python_plugins.sh    # Работа Python плагинов
│   └── test_api_endpoints.sh     # Тестирование API
├── e2e/                   # End-to-end тесты
│   ├── test_full_workflow.sh     # Полный рабочий процесс
│   └── test_network_sync.sh      # Синхронизация с сетью
├── fixtures/              # Тестовые данные и конфигурации
│   ├── configs/          # Конфигурационные файлы
│   └── plugins/          # Тестовые плагины
├── helpers/               # Вспомогательные функции
│   ├── test_utils.sh     # Общие функции для тестов
│   └── node_control.sh   # Управление нодой
├── run_tests.sh          # Запуск всех тестов
└── README.md             # Этот файл
```

## 🚀 Запуск тестов

### Все тесты
```bash
cd tests
./run_tests.sh
```

### Отдельные категории
```bash
# Интеграционные тесты
./run_tests.sh integration

# E2E тесты  
./run_tests.sh e2e

# Тесты плагинов
./run_tests.sh plugins
```

### Отдельный тест
```bash
./integration/test_binary_plugins.sh
```

## ⚙️ Требования

- **Bash 4.0+**
- **CellFrame Node** (собранный)
- **curl** для HTTP тестов
- **jq** для обработки JSON
- **timeout** для контроля времени выполнения

## 🛠️ Конфигурация

Тесты используют переменные окружения:

```bash
# Основные настройки
export CELLFRAME_NODE_PATH="/path/to/cellframe-node"
export CELLFRAME_CONFIG_PATH="/path/to/configs"
export TEST_TIMEOUT=30

# Настройки сети
export TEST_NETWORK="testnet"
export TEST_PORT=8079

# Настройки плагинов
export PYTHON_PLUGIN_PATH="/path/to/python-plugin.so"
export PLUGINS_DIR="/path/to/plugins"
```

## 📊 Отчеты

Результаты тестов сохраняются в:
- `test_results.xml` - JUnit формат
- `test_coverage.html` - Покрытие тестами
- `logs/` - Логи выполнения тестов

## 🐛 Отладка

```bash
# Запуск в debug режиме
DEBUG=1 ./run_tests.sh

# Запуск с verbose логами
VERBOSE=1 ./integration/test_binary_plugins.sh

# Оставить ноду запущенной после тестов
KEEP_RUNNING=1 ./run_tests.sh integration
``` 