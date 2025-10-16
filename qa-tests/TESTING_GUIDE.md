# Cellframe Node QA Testing Guide

## 🏗️ Архитектура тестирования

Профессиональная система тестирования Cellframe Node, построенная по лучшим практикам и стандартам индустрии.

### 📁 Структура проекта

```
qa-tests/
├── framework/                  # Тестовый фреймворк
│   ├── config/                # Конфигурация
│   │   ├── test_config.py     # Централизованная конфигурация
│   │   └── __init__.py
│   ├── utils/                 # Утилиты
│   │   ├── command_executor.py # Выполнение команд с retry
│   │   └── __init__.py
│   ├── pages/                 # Page Objects
│   │   ├── node_cli.py        # CLI интерфейс ноды
│   │   └── __init__.py
│   ├── assertions/            # Кастомные assertions
│   │   ├── node_assertions.py # Специфичные для ноды проверки
│   │   └── __init__.py
│   ├── fixtures/              # Pytest fixtures
│   │   ├── node_fixtures.py   # Фикстуры для ноды
│   │   └── __init__.py
│   └── __init__.py
├── tests/                     # Тесты по категориям
│   ├── smoke/                 # Smoke тесты
│   │   ├── test_node_basic.py # Базовая функциональность
│   │   └── __init__.py
│   ├── integration/           # Интеграционные тесты
│   │   ├── test_network_operations.py # Сетевые операции
│   │   └── __init__.py
│   ├── e2e/                   # End-to-end тесты
│   │   ├── test_node_lifecycle.py # Жизненный цикл ноды
│   │   └── __init__.py
│   └── __init__.py
├── data/                      # Тестовые данные
│   ├── test_data/             # Данные для тестов
│   │   ├── network_test_data.py # Сетевые данные
│   │   └── __init__.py
│   └── expected_results/      # Ожидаемые результаты
├── reports/                   # Отчеты
├── conftest.py               # Глобальная конфигурация pytest
├── pytest.ini               # Конфигурация pytest
└── requirements.txt          # Зависимости
```

## 🎯 Принципы архитектуры

### 1. **Модульность**
- Каждый компонент имеет четкую ответственность
- Легкое переиспользование кода
- Простое добавление новых тестов

### 2. **Конфигурируемость**
- Централизованная конфигурация через `test_config.py`
- Поддержка различных окружений
- Переменные окружения для настройки

### 3. **Page Object Pattern**
- CLI интерфейс инкапсулирован в `NodeCLI` класс
- Высокоуровневые методы для взаимодействия с нодой
- Скрытие деталей реализации

### 4. **Надежность**
- Retry логика для нестабильных операций
- Proper error handling
- Таймауты и лимиты

### 5. **Наблюдаемость**
- Подробное логирование
- Allure отчеты с attachments
- Метрики производительности

## 🚀 Быстрый старт

### Установка зависимостей

```bash
pip install -r requirements.txt
```

### Запуск тестов

```bash
# Все тесты
pytest

# Только smoke тесты
pytest -m smoke

# Только интеграционные тесты
pytest -m integration

# E2E тесты
pytest -m e2e

# Тесты с отчетом Allure
pytest --alluredir=allure-results
allure serve allure-results
```

### Конфигурация

Настройте переменные окружения:

```bash
export CELLFRAME_NODE_DIR="/opt/cellframe-node"
export QA_MAX_MEMORY_MB="1024"
export QA_MAX_CPU_PERCENT="50.0"
export QA_ENVIRONMENT="docker"
export QA_DEBUG="true"
```

## 📋 Категории тестов

### 🔥 Smoke Tests
**Цель**: Быстрая проверка основной функциональности
- Время выполнения: < 2 минут
- Запускаются при каждом коммите
- Критически важные функции

**Примеры**:
- Нода запущена и отвечает
- Версия доступна
- Базовые CLI команды работают

### 🔗 Integration Tests
**Цель**: Проверка взаимодействия компонентов
- Время выполнения: 5-10 минут
- Сетевые операции
- Взаимодействие с внешними системами

**Примеры**:
- Статус сетей
- Подключение к peers
- Производительность команд

### 🌐 End-to-End Tests
**Цель**: Полные пользовательские сценарии
- Время выполнения: 10-30 минут
- Реальные workflow
- Стресс-тестирование

**Примеры**:
- Полный жизненный цикл ноды
- Длительная стабильность
- Ресурсоемкие операции

## 🛠️ Добавление новых тестов

### 1. Smoke тест

```python
import pytest
import allure
from framework import NodeCLI, NodeAssertions

@allure.epic("Cellframe Node")
@allure.feature("New Feature")
@pytest.mark.smoke
@pytest.mark.critical
class TestNewFeature:
    
    @allure.title("New feature works correctly")
    def test_new_feature(self, node_cli: NodeCLI, node_assertions: NodeAssertions):
        # Arrange
        
        # Act
        result = node_cli.execute_custom_command("new_command")
        
        # Assert
        node_assertions.assert_command_success(result)
        node_assertions.assert_output_contains(result, "expected_text")
```

### 2. Интеграционный тест

```python
@pytest.mark.integration
@pytest.mark.network
class TestNetworkIntegration:
    
    def test_network_integration(self, node_cli: NodeCLI, wait_for_networks):
        # Более сложная логика
        networks_status = node_cli.get_all_networks_status()
        
        for network_name, status in networks_status.items():
            # Проверки интеграции
            pass
```

### 3. E2E тест

```python
@pytest.mark.e2e
@pytest.mark.slow
class TestCompleteWorkflow:
    
    def test_complete_workflow(self, isolated_test_environment):
        # Полный сценарий использования
        pass
```

## 🎨 Лучшие практики

### 1. **Именование тестов**
- Используйте описательные имена
- Формат: `test_what_when_then`
- Пример: `test_network_status_when_online_then_returns_valid_data`

### 2. **Структура тестов**
```python
def test_something(self):
    # Arrange - подготовка
    
    # Act - действие
    
    # Assert - проверка
```

### 3. **Использование маркеров**
```python
@pytest.mark.smoke      # Категория
@pytest.mark.critical   # Важность
@pytest.mark.network    # Область
@pytest.mark.slow       # Характеристика
```

### 4. **Allure аннотации**
```python
@allure.epic("Cellframe Node")
@allure.feature("Network Operations")
@allure.story("Network Status")
@allure.title("Network returns valid status")
@allure.description("Detailed test description")
```

### 5. **Фикстуры**
- Используйте подходящий scope
- `session` - для дорогих ресурсов
- `function` - для изоляции тестов
- `class` - для группы связанных тестов

### 6. **Assertions**
- Используйте кастомные assertions из `NodeAssertions`
- Добавляйте информативные сообщения об ошибках
- Проверяйте не только успех, но и производительность

### 7. **Данные**
- Выносите тестовые данные в `data/test_data/`
- Используйте параметризацию для data-driven тестов
- Избегайте хардкода в тестах

## 🔧 Конфигурация и настройка

### Переменные окружения

| Переменная | Описание | По умолчанию |
|------------|----------|--------------|
| `CELLFRAME_NODE_DIR` | Директория ноды | `/opt/cellframe-node` |
| `QA_MAX_MEMORY_MB` | Лимит памяти | `1024` |
| `QA_MAX_CPU_PERCENT` | Лимит CPU | `50.0` |
| `QA_ENVIRONMENT` | Окружение | `docker` |
| `QA_DEBUG` | Режим отладки | `false` |
| `QA_TIMEOUT` | Таймаут тестов | `300` |

### Pytest опции

```bash
# Запуск с дополнительными опциями
pytest --run-slow                    # Включить медленные тесты
pytest --node-required               # Требовать запущенную ноду
pytest --test-category=smoke         # Только smoke тесты
pytest -n auto                      # Параллельное выполнение
pytest --reruns 2                   # Повтор упавших тестов
```

## 📊 Отчетность

### Allure Reports
- Подробные отчеты с историей
- Скриншоты и логи
- Метрики производительности
- Трендовый анализ

### JUnit XML
- Интеграция с CI/CD
- Стандартный формат
- Совместимость с Jenkins, GitLab CI

### Coverage Reports
- Покрытие кода фреймворка
- HTML отчеты
- Интеграция с SonarQube

## 🚨 Troubleshooting

### Частые проблемы

1. **Нода не запущена**
   ```
   Solution: Убедитесь что cellframe-node запущен
   ```

2. **Таймауты тестов**
   ```
   Solution: Увеличьте QA_TIMEOUT или оптимизируйте тесты
   ```

3. **Проблемы с путями**
   ```
   Solution: Проверьте CELLFRAME_NODE_DIR
   ```

4. **Нестабильные тесты**
   ```
   Solution: Используйте retry логику и proper waits
   ```

### Отладка

```bash
# Подробные логи
pytest --log-cli-level=DEBUG

# Остановка на первой ошибке
pytest -x

# Запуск конкретного теста
pytest tests/smoke/test_node_basic.py::TestNodeBasic::test_node_is_running -v
```

## 🔄 CI/CD интеграция

### GitLab CI пример

```yaml
test:
  stage: test
  script:
    - pip install -r requirements.txt
    - pytest -m smoke --junitxml=reports/junit.xml
  artifacts:
    reports:
      junit: reports/junit.xml
    paths:
      - allure-results/
    expire_in: 1 week
```

## 📈 Метрики качества

### Цели покрытия
- **Smoke тесты**: 100% критической функциональности
- **Integration тесты**: 80% API endpoints
- **E2E тесты**: 60% пользовательских сценариев

### SLA производительности
- **Smoke тесты**: < 2 минут
- **Integration тесты**: < 10 минут  
- **E2E тесты**: < 30 минут

### Стабильность
- **Success rate**: > 95%
- **Flaky tests**: < 5%
- **False positives**: < 1%

---

## 🎯 Заключение

Эта архитектура тестирования обеспечивает:

✅ **Профессиональное качество** - следование лучшим практикам индустрии
✅ **Масштабируемость** - легкое добавление новых тестов
✅ **Надежность** - стабильные и информативные тесты
✅ **Эффективность** - быстрая обратная связь разработчикам
✅ **Наблюдаемость** - подробная отчетность и метрики

**Система готова к продуктивному использованию!** 🚀
