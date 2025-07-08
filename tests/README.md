# CellFrame Node Python Plugin - Tests

Тестовая система для CellFrame Node Python Plugin.

## Структура

```
tests/
├── conftest.py                     # Конфигурация pytest
├── pytest.ini                     # Настройки pytest
├── requirements-test.txt           # Зависимости для тестов
├── run_tests.py                   # Основной test runner
├── README.md                      # Документация
├── 
├── unit/                          # Unit тесты
├── integration/                   # Integration тесты
├── performance/                   # Performance тесты
├── config/                        # Тестовые конфигурации
├── plugin/                        # Тестовые плагины
└── fixtures/                      # Тестовые данные
```

## Использование

### Установка зависимостей
```bash
cd tests/
python run_tests.py --install-deps
```

### Запуск тестов
```bash
# Все тесты
python run_tests.py

# Только unit тесты
python run_tests.py --type unit

# С coverage
python run_tests.py --coverage

# Все проверки
python run_tests.py --all-checks
```

### Прямое использование pytest
```bash
cd tests/
pytest unit/                       # Unit тесты
pytest integration/                # Integration тесты
pytest -m "composer"               # Тесты composer
pytest -v --tb=short              # Подробный вывод
```

## Файлы

- **conftest.py** - Глобальные fixtures и конфигурация
- **pytest.ini** - Настройки pytest, маркеры, coverage
- **requirements-test.txt** - Зависимости для тестирования
- **run_tests.py** - Основной test runner скрипт
- **integration/test_python_api_symbols.py** - Тест символов в бинарке
- **plugin/test_plugin.py** - Тестовый плагин
- **config/etc/cellframe-node.cfg** - Тестовая конфигурация

## Маркеры

- `@pytest.mark.unit` - Unit тесты
- `@pytest.mark.integration` - Integration тесты
- `@pytest.mark.performance` - Performance тесты
- `@pytest.mark.plugin` - Тесты plugin инфраструктуры
- `@pytest.mark.composer` - Тесты transaction composer
- `@pytest.mark.conditional` - Тесты conditional processors
- `@pytest.mark.legacy` - Тесты обратной совместимости
- `@pytest.mark.mock_only` - Тесты только с моками
- `@pytest.mark.slow` - Медленные тесты

## Статус

**Phase 7.1 "Testing & Validation"** - Активная разработка
Версия: 1.0.0
Обновлено: 2024-07-08 