# End-to-End Tests

E2E тесты для Cellframe Node - полные сценарии использования с комплексными проверками.

## Структура

```
tests/e2e/
├── README.md                           # Эта документация
├── utxo_blocking/                      # UTXO blocking feature
│   ├── arbitrage_bypass.yml           # Арбитраж обходит блокировки
│   └── blocked_utxo_transfer.yml      # Заблокированные UTXO нельзя потратить
└── token_lifecycle/                    # Полный жизненный цикл токена
    └── token_transfer_flow.yml        # Создание, эмиссия, трансфер
```

## Назначение E2E тестов

E2E тесты проверяют **полные пользовательские сценарии**:
- Комплексные flow с множественными шагами
- Взаимодействие разных компонентов системы
- Реальные use-case пользователей
- Интеграция между модулями

## Отличие от функциональных тестов

| E2E Tests | Functional Tests |
|-----------|------------------|
| Полные сценарии | Конкретные команды |
| Множественные компоненты | Отдельные функции |
| User perspective | Developer perspective |
| Медленные, комплексные | Быстрые, изолированные |

## Запуск E2E тестов

```bash
# Все E2E тесты
./tests/run.sh --e2e

# Конкретный тест
./tests/stage-env/stage-env run-tests tests/e2e/utxo_blocking/arbitrage_bypass.yml

# С очисткой окружения
./tests/run.sh --e2e --clean
```

## Написание E2E тестов

### Структура E2E теста

```yaml
name: Feature End-to-End Test
description: Complete user scenario from start to finish
tags: [e2e, feature-name, slow]

includes:
  - ../../common/networks/single_node.yml
  - ../../common/wallets/create_wallet.yml

setup:
  # Подготовка полного окружения
  - cli: подготовка

test:
  # Полный сценарий использования
  - cli: шаг_1
  - cli: шаг_2
  - cli: шаг_3

check:
  # Комплексные проверки результата
  - cli: проверка_1
  - cli: проверка_2
```

### Best Practices для E2E

1. **Тестируйте реальные use-case**
   ```yaml
   name: User Creates and Transfers Token
   # Не "Token API Works"
   ```

2. **Включайте все необходимые шаги**
   ```yaml
   setup:
     - cli: создание_всех_зависимостей
   ```

3. **Используйте общие шаблоны**
   ```yaml
   includes:
     - ../../common/networks/single_node.yml
   ```

4. **Добавляйте wait после каждого значимого действия**
   ```yaml
   - cli: token_emit
     wait: 3s
   ```

5. **Проверяйте конечное состояние**
   ```yaml
   check:
     - cli: проверка_всех_побочных_эффектов
   ```

## UTXO Blocking Feature Tests

Тесты функциональности блокировки UTXO:

### arbitrage_bypass.yml
Проверяет что арбитражные транзакции могут обходить заблокированные UTXO.

**Сценарий:**
1. Создать токен с UTXO_BLOCKING_ENABLED
2. Эмитировать токены
3. Создать UTXO
4. Заблокировать UTXO
5. Обычная транзакция должна fail
6. Арбитражная транзакция должна success

### blocked_utxo_transfer.yml
Проверяет что заблокированные UTXO действительно нельзя потратить.

**Сценарий:**
1. Создать токен с блокировкой
2. Создать несколько UTXO
3. Заблокировать один UTXO
4. Попытка потратить заблокированный - fail
5. Попытка потратить незаблокированный - success

## См. также

- [Common Templates](../common/) - Общие шаблоны
- [Functional Tests](../functional/) - Функциональные тесты
- [Stage-env Documentation](../stage-env/scenarios/) - Документация системы

