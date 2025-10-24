# Cellframe Node Tests

Автоматизированная система тестирования для Cellframe Node на базе YAML сценариев с поддержкой иерархических defaults и группировки.

## 📁 Структура

```
tests/
├── e2e/                    # End-to-End тесты (полные сценарии)
│   ├── wallet/            # Тесты кошельков
│   ├── token/             # Тесты токенов
│   ├── net/               # Тесты сети
│   ├── node/              # Тесты узлов
│   ├── chain/             # Тесты блокчейна
│   ├── mempool/           # Тесты mempool
│   ├── integration/       # Интеграционные тесты
│   └── examples/          # Примеры использования всех возможностей
├── functional/            # Функциональные тесты (отдельные функции)
│   ├── wallet/
│   ├── token/
│   ├── net/
│   ├── node/
│   ├── chain/
│   ├── mempool/
│   └── utxo_blocking/     # Специфичные тесты UTXO блокировки
├── stage-env/             # Окружение для тестирования
│   └── tests/
│       └── common/        # Переиспользуемые компоненты
│           ├── wallets/   # Общие операции с кошельками
│           ├── tokens/    # Общие операции с токенами
│           ├── networks/  # Конфигурации сетей
│           ├── checks/    # Общие проверки
│           ├── setup/     # Общие setup действия
│           ├── transactions/  # Общие операции с транзакциями
│           └── assertions/    # Общие утверждения
├── README.md                              # Этот файл
├── SCENARIO_DEFAULTS_AND_GROUPS.md        # Руководство по defaults и группам
└── run.sh                                 # Скрипт запуска тестов
```

## 🎯 Организация тестов

### Сьюты (Suites)

Каждая директория в `e2e/` и `functional/` представляет собой **тестовый сьют**.

- **Файл сьюта**: `<suite_name>.yml` на уровне директории
  - Содержит описание всего сьюта
  - Не содержит тестов, только метаданные
  
- **Тесты**: Файлы `*.yml` внутри директории сьюта
  - Каждый файл = один тестовый сценарий
  - Нумерация: `001_test_name.yml`, `002_another_test.yml`

### Пример структуры сьюта

```
e2e/wallet/
├── wallet.yml              # Описание сьюта
├── 001_wallet_create.yml   # Тест создания кошелька
├── 002_wallet_address.yml  # Тест получения адреса
└── 003_wallet_multiple.yml # Тест множественных кошельков
```

## 🆕 Новые возможности: Defaults и Группы

### Иерархические Defaults

Система поддерживает 4 уровня defaults с приоритетом наследования:

```
Global → Section → Group → Step
```

**Пример простого использования:**

```yaml
name: Token Emission Test
description: Test emitting tokens to a wallet
tags: [e2e, token, emission]

network:
  topology: default

# Global defaults - применяются ко всем секциям
defaults:
  node: node1
  wait: 3s
  timeout: 60

setup:
  # Наследует node=node1, wait=3s, timeout=60
  - cli: token_decl -net stagenet -token TEST -total 1000000
    description: "Declare token"

test:
  # Также наследует все global defaults
  - cli: token_emit -net stagenet -token TEST -value 1000 -addr {{wallet_addr}}
    save: emit_tx
    description: "Emit tokens"

check:
  # И здесь тоже
  - cli: token info -net stagenet -token TEST
    contains: "TEST"
```

### Группировка шагов

Группируйте связанные операции с локальными defaults:

```yaml
defaults:
  wait: 2s  # Global default

test:
  # Группа 1: Операции на node1
  - group:
      name: "Node1 Operations"
      defaults:
        node: node1
        wait: 5s  # Переопределяет global
      steps:
        - cli: wallet new -w node1_wallet
        - cli: token_decl -net stagenet -token TOKEN1
        - cli: token_emit -net stagenet -token TOKEN1 -value 1000
  
  # Группа 2: Операции на node2
  - group:
      name: "Node2 Operations"
      defaults:
        node: node2
        wait: 3s
      steps:
        - cli: wallet new -w node2_wallet
        - cli: wallet list
```

**Подробнее:** См. [SCENARIO_DEFAULTS_AND_GROUPS.md](SCENARIO_DEFAULTS_AND_GROUPS.md)

## 🔧 Общие компоненты (Common Includes)

Директория `stage-env/tests/common/` содержит переиспользуемые компоненты:

### Wallets
- `create_wallet.yml` - создание тестового кошелька с адресом

### Tokens
- `create_token.yml` - создание токена
- `emit_tokens.yml` - эмиссия токенов

### Networks
- `single_node.yml` - конфигурация одного узла
- `network_minimal.yml` - минимальная сеть (2-3 узла)

### Checks
- `verify_online.yml` - проверка что узел онлайн

### Setup
- `wait_for_sync.yml` - ожидание синхронизации сети

### Transactions
- `create_simple_tx.yml` - создание простой транзакции

### Assertions
- `check_success.yml` - проверка успешности операции

## 📝 Формат тестового сценария

### Минимальный сценарий

```yaml
name: Simple Test
description: Basic test example
tags: [e2e, simple]
version: "1.0"

network:
  topology: default

test:
  - cli: wallet list
    node: node1
```

### Полный сценарий со всеми возможностями

```yaml
name: Full Featured Test
description: Demonstrates all scenario features
tags: [e2e, advanced, example]
version: "1.0"

network:
  topology: default

# Global defaults для всего сценария
defaults:
  node: node1
  wait: 3s
  timeout: 60

# Переиспользуемые компоненты
includes:
  - common/wallets/create_wallet.yml
  - common/networks/single_node.yml

# Setup с section defaults
setup:
  defaults:
    wait: 5s  # Override global для setup
  steps:
    - cli: wallet new -w test_wallet
      description: "Create test wallet"

# Test с группами
test:
  # Простые шаги (используют global defaults)
  - cli: token_decl -net stagenet -token TEST -total 1000000
    save: token_hash
  
  # Группа шагов
  - group:
      name: "Token Operations"
      defaults:
        node: node2  # Override node для группы
        wait: 4s
      steps:
        - cli: token_emit -net stagenet -token TEST -value 1000
        - cli: token info -net stagenet -token TEST
        
        # Вложенная группа
        - group:
            name: "Wallet Checks"
            steps:
              - cli: wallet list
              - cli: wallet info -w test_wallet
  
  # Python блок
  - python: |
      token = ctx.get_variable('token_hash')
      assert len(token) > 0
    description: "Validate token hash"
  
  # Bash блок
  - bash: |
      ls -la /opt/cellframe-node/var
    node: node1
    save: node_files

# Check секция
check:
  # CLI check
  - cli: wallet list
    contains: "test_wallet"
  
  # Python check
  - python: |
      files = ctx.get_variable('node_files')
      assert 'node_addr.txt' in files
  
  # Bash check
  - bash: |
      [ -f /opt/cellframe-node/var/run/cellframe-node.pid ]
    node: node1
```

## 🎨 Расширенные возможности языка

### 1. Python блоки

Python блоки имеют полный доступ к контексту через объект `ctx`:

```yaml
test:
  - python: |
      # Получить переменную
      wallet = ctx.get_variable('wallet_addr')
      
      # Установить переменную
      ctx.set_variable('wallet_upper', wallet.upper())
      
      # Вычисления
      result = len(wallet)
      
      # Результат автоматически сохраняется если указан save:
    save: addr_length
    description: "Compute address length"

check:
  - python: |
      # Проверки с assert
      addr = ctx.get_variable('wallet_addr')
      assert '::' in addr, "Address must contain ::"
      assert len(addr) > 10, "Address too short"
    description: "Validate address format"
```

### 2. Bash блоки

Bash скрипты выполняются внутри Docker контейнеров:

```yaml
test:
  - bash: |
      # Полный shell доступ
      ls -la /opt/cellframe-node/var
      cat /proc/meminfo | grep MemTotal
      echo "Result: OK"
    node: node1
    save: node_info
    description: "Collect node info"

check:
  - bash: |
      # Exit 0 = success, Exit 1 = failure
      if [ -f /opt/cellframe-node/var/run/cellframe-node.pid ]; then
        exit 0
      else
        exit 1
      fi
    node: node1
    description: "Check PID file exists"
```

### 3. Substitution переменных

Переменные доступны везде через `{{variable}}`:

```yaml
test:
  - cli: wallet info -w {{wallet_name}} -net stagenet
    save: info
  
  - python: |
      # Переменные автоматически подставляются в строках
      info = ctx.get_variable('info')
      print(f"Info for {{wallet_name}}: {info}")
  
  - bash: |
      echo "Working with {{wallet_addr}}"
```

### 4. Циклы

```yaml
test:
  - loop: 5
    steps:
      - cli: wallet new -w wallet_{{iteration}}
        node: node1
      - wait: 1s
```

## 🚀 Запуск тестов

### Через run.sh (рекомендуется)

```bash
cd tests

# Запуск всех E2E тестов
./run.sh e2e

# Запуск конкретного сьюта
./run.sh e2e/wallet

# Запуск функциональных тестов
./run.sh functional

# Запуск с фильтром
./run.sh e2e -k "wallet"

# Полная очистка + пересборка + тесты
./run.sh e2e --full
```

### Напрямую через stage-env

```bash
cd tests/stage-env

# Запуск тестов
./stage_env.py run-tests ../e2e/wallet/

# С автозапуском сети
./stage_env.py run-tests ../e2e/wallet/ --start-network

# Без остановки сети после
./stage_env.py run-tests ../e2e/wallet/ --keep-running

# С фильтром
./stage_env.py run-tests ../e2e/ -k "create"
```

## 📊 Артефакты

После запуска тестов артефакты сохраняются в:

```
tests/artifacts/
└── run_tests_YYYYMMDD_HHMMSS/    # Каждый запуск = отдельная папка
    ├── scenario-logs/              # Логи выполнения каждого сценария
    │   ├── scenario_wallet_create_20241024_123456.log
    │   └── scenario_token_emit_20241024_123457.log
    ├── stage-env-logs/             # Логи stage-env
    ├── node-logs/                  # Логи Docker контейнеров нод
    ├── core-dumps/                 # Core dumps (если были)
    ├── health-logs/                # Health check логи
    └── summary.json                # Сводка по запуску
```

### Структура scenario log

```
=== Scenario: Token Emission Test ===
File: /path/to/test.yml
Description: Test emitting tokens
Tags: e2e, token
Started: 20241024_123456
======================================================================

======================================================================
CLI COMMAND
======================================================================
Node: node1
Command: token_decl -net stagenet -token TEST -total 1000000
Description: Declare token
Timeout: 60s
Expected: success

--- Node Response ---
Exit Code: 0

Stdout:
Token TEST declared successfully
Hash: 0x1234...
======================================================================

... (все шаги) ...

======================================================================
=== Results ===
Status: PASSED
Steps: 5/5 passed
Variables saved: 3
  token_hash = 0x1234...
  wallet_addr = 0xABCD...::...
  emit_tx = 0x5678...
```

## 🎯 Best Practices

### 1. Используйте defaults для DRY

❌ **Плохо** (повторения):
```yaml
test:
  - cli: wallet new -w w1
    node: node1
    wait: 3s
  - cli: wallet new -w w2
    node: node1
    wait: 3s
```

✅ **Хорошо** (чисто):
```yaml
defaults:
  node: node1
  wait: 3s
test:
  - cli: wallet new -w w1
  - cli: wallet new -w w2
```

### 2. Группируйте связанные операции

✅ **Хорошо**:
```yaml
test:
  - group:
      name: "Setup Wallets"
      steps:
        - cli: wallet new -w w1
        - cli: wallet new -w w2
  
  - group:
      name: "Create Tokens"
      steps:
        - cli: token_decl ...
        - cli: token_emit ...
```

### 3. Переиспользуйте common includes

✅ **Хорошо**:
```yaml
includes:
  - common/wallets/create_wallet.yml
  - common/tokens/create_token.yml

test:
  # wallet_addr и token уже доступны
  - cli: token_emit ... -addr {{wallet_addr}}
```

### 4. Именуйте группы для отладки

✅ **Хорошо**:
```yaml
- group:
    name: "Prepare Node2"  # Видно в логах
    description: "Setup node2 for cross-node test"
    steps: ...
```

### 5. Используйте description везде

✅ **Хорошо**:
```yaml
- cli: wallet new -w test
  description: "Create test wallet for token operations"
```

## 📚 Дополнительная документация

- **[SCENARIO_DEFAULTS_AND_GROUPS.md](SCENARIO_DEFAULTS_AND_GROUPS.md)** - Полное руководство по defaults и группам
- **[tests/e2e/examples/](e2e/examples/)** - Примеры использования всех возможностей
- **[stage-env/README.md](stage-env/README.md)** - Документация по окружению

## 🔍 Примеры

### Простой тест

```yaml
# tests/e2e/wallet/001_wallet_create.yml
name: Wallet Creation
description: Test wallet creation
tags: [e2e, wallet, basic]

network:
  topology: default

defaults:
  node: node1
  wait: 2s

test:
  - cli: wallet new -w test_wallet
  - cli: wallet list
    contains: "test_wallet"
```

### Сложный multi-node тест

```yaml
# tests/e2e/integration/cross_node_token_transfer.yml
name: Cross-Node Token Transfer
description: Transfer tokens between nodes
tags: [e2e, integration, multi-node]

network:
  topology: default

defaults:
  wait: 3s

includes:
  - common/wallets/create_wallet.yml
  - common/tokens/create_token.yml

test:
  - group:
      name: "Setup Node1"
      defaults:
        node: node1
      steps:
        - cli: wallet new -w node1_wallet
        - cli: token_emit ... -addr {{node1_addr}}
  
  - group:
      name: "Setup Node2"
      defaults:
        node: node2
      steps:
        - cli: wallet new -w node2_wallet
  
  - cli: tx_create ... -from {{node1_addr}} -to {{node2_addr}}
    node: node1
  
  - wait: 10s
  
  - cli: wallet list
    node: node2
    contains: "node2_wallet"
```

## 🐛 Отладка

### Логи

Все детальные логи в `tests/artifacts/run_tests_*/scenario-logs/`

### Ошибки сценариев

При ошибке сценарий показывает:
- Какой шаг упал
- Команда и параметры
- Вывод ноды (stdout/stderr)
- Ожидаемый vs фактический результат

### Сохранение сети после тестов

```bash
./stage_env.py run-tests ../e2e/wallet/ --keep-running

# Затем можно вручную проверить ноды
docker ps
docker exec cellframe-stage-node-1 cellframe-node-cli wallet list
```

## 🤝 Контрибуция

При добавлении новых тестов:

1. **Используйте defaults** - избегайте повторений
2. **Группируйте операции** - структурируйте сложные сценарии
3. **Создавайте includes** - выносите общие операции в `common/`
4. **Добавляйте descriptions** - помогает при отладке
5. **Следуйте структуре сьютов** - один сьют = одна папка
6. **Нумеруйте тесты** - `001_`, `002_`, etc.
7. **Тестируйте локально** перед коммитом

## 📈 Статистика

```bash
# Количество тестов
find e2e/ functional/ -name "*.yml" -not -name "*suite*" | wc -l

# Запуск с coverage (будущее)
./run.sh e2e --coverage
```
