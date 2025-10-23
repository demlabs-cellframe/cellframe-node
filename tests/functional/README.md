# Functional Tests

Функциональные тесты для конкретных команд и функций Cellframe Node.

## Структура

```
tests/functional/
├── README.md                           # Эта документация
├── utxo_blocking/                      # UTXO blocking commands
│   ├── token_update_utxo_add.yml      # Команда добавления UTXO в blocklist
│   ├── token_update_utxo_remove.yml   # Команда удаления UTXO из blocklist
│   ├── token_update_utxo_clear.yml    # Команда очистки blocklist
│   ├── token_info_history.yml         # Команда просмотра истории блокировок
│   └── tx_create_arbitrage.yml        # Команда создания арбитражной транзакции
└── basic/                              # Базовые команды
    └── version_command.yml             # Команда version
```

## Назначение функциональных тестов

Функциональные тесты проверяют **отдельные команды и функции**:
- Корректность работы конкретной команды
- Валидация параметров
- Обработка ошибок
- Edge cases
- Изолированное тестирование функциональности

## Отличие от E2E тестов

| Functional Tests | E2E Tests |
|------------------|-----------|
| Одна команда/функция | Полный сценарий |
| Изолированное тестирование | Интеграция компонентов |
| Быстрые, простые | Медленные, комплексные |
| Developer perspective | User perspective |

## Запуск функциональных тестов

```bash
# Все функциональные тесты
./tests/run.sh --functional

# Конкретный тест
./tests/stage-env/stage-env run-tests tests/functional/utxo_blocking/token_update_utxo_add.yml

# Группа тестов
./tests/stage-env/stage-env run-tests tests/functional/utxo_blocking/
```

## Написание функциональных тестов

### Структура функционального теста

```yaml
name: Command Name Test
description: Test specific command functionality
tags: [functional, command-name, fast]

includes:
  - ../../common/networks/single_node.yml

setup:
  # Минимальная подготовка
  - cli: минимальная_подготовка

test:
  # Тестируемая команда
  - cli: тестируемая_команда параметры
    expect: expected_result

check:
  # Проверка результата
  - cli: проверка
```

### Best Practices для функциональных тестов

1. **Тестируйте одну команду**
   ```yaml
   name: token_update -utxo_blocked_add Command
   # Не "Token Update Commands" (множественное)
   ```

2. **Минимальная подготовка**
   ```yaml
   setup:
     - cli: только_необходимое
   ```

3. **Фокус на команде**
   ```yaml
   test:
     - cli: конкретная_команда
   ```

4. **Проверяйте прямой результат**
   ```yaml
   check:
     - cli: непосредственная_проверка
   ```

5. **Быстрое выполнение**
   ```yaml
   # Избегайте долгих wait
   wait: 1s  # Минимальное время
   ```

## UTXO Blocking Functional Tests

### token_update_utxo_add.yml
Проверяет команду `token_update -utxo_blocked_add`

**Тестирует:**
- Добавление UTXO в blocklist
- Корректность параметров
- Результат команды

### token_update_utxo_remove.yml
Проверяет команду `token_update -utxo_blocked_remove`

**Тестирует:**
- Удаление UTXO из blocklist
- Проверка что UTXO больше не заблокирован

### token_update_utxo_clear.yml
Проверяет команду `token_update -utxo_blocked_clear`

**Тестирует:**
- Очистка всего blocklist
- Проверка что все UTXO разблокированы

### token_info_history.yml
Проверяет команду `token info -history_limit`

**Тестирует:**
- Просмотр истории блокировок
- Корректность вывода
- Лимит записей

### tx_create_arbitrage.yml
Проверяет команду `tx_create -arbitrage`

**Тестирует:**
- Создание арбитражной транзакции
- Наличие маркера arbitrage
- Обход блокировок

## Паттерны тестирования

### Happy Path
```yaml
test:
  - cli: команда корректные_параметры
    expect: success
```

### Error Handling
```yaml
test:
  - cli: команда неверные_параметры
    expect: error
    contains: "expected error message"
```

### Boundary Conditions
```yaml
test:
  - cli: команда граничное_значение
    expect: success
```

### Edge Cases
```yaml
test:
  - cli: команда редкий_случай
    expect: определенный_результат
```

## См. также

- [Common Templates](../common/) - Общие шаблоны
- [E2E Tests](../e2e/) - End-to-end тесты
- [Stage-env Documentation](../stage-env/scenarios/) - Документация системы

