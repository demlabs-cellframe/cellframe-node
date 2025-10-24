# Unit Tests for Stage-Env Components

## Структура

```
unit/
├── __init__.py
├── conftest.py              # Pytest fixtures и конфигурация
├── fixtures/                # Тестовые данные
│   ├── cli_help_main.txt   # Основной help вывод
│   └── cli_help_token_decl.txt  # Help для конкретной команды
├── test_cli_parser.py       # Тесты CLI парсера
└── test_scenario_executor.py # Тесты executor'а
```

## Запуск тестов

```bash
# Все unit тесты
cd tests/stage-env
pytest tests/unit/ -v

# Конкретный файл
pytest tests/unit/test_cli_parser.py -v

# Конкретный тест
pytest tests/unit/test_cli_parser.py::TestCLICommandParser::test_extract_commands_from_main_help -v
```

## Покрытие

### test_cli_parser.py
- ✅ Извлечение команд из main help
- ✅ Извлечение опций из command help
- ✅ Применение defaults к командам
- ✅ Проверка дубликатов
- ✅ Игнорирование неподдерживаемых опций
- ✅ Кэширование (загрузка и сохранение)
- ✅ Валидация пустого кэша

### test_scenario_executor.py
- ✅ Детектирование YAML ошибок
- ✅ Детектирование успешных ответов
- ✅ Извлечение hash из YAML
- ✅ Regex fallback для hash
- ✅ Применение defaults (hierarchical merge)
- ✅ Datum monitor integration (invalid hash rejection)

## Fixtures

### CLI Help Outputs
- `cli_help_main.txt` - реальный вывод `cellframe-node-cli help`
- `cli_help_token_decl.txt` - реальный вывод `help token_decl`

### YAML Responses
- `sample_yaml_error` - типичная ошибка от CLI
- `sample_yaml_success` - успешный ответ с hash

## Mocking

Unit тесты используют:
- `unittest.mock` для Docker API
- Fixture файлы вместо реальных контейнеров
- Изолированные тесты без внешних зависимостей

## CI/CD Integration

Добавить в `.gitlab-ci.yml`:
```yaml
unit-tests:
  stage: test
  script:
    - cd tests/stage-env
    - pip install pytest pytest-asyncio pyyaml
    - pytest tests/unit/ -v --junit-xml=junit.xml
  artifacts:
    reports:
      junit: tests/stage-env/junit.xml
```

