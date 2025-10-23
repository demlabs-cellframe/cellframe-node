# Cellframe Node Tests

Автоматизированная система тестирования для Cellframe Node на базе YAML сценариев.

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
│   └── integration/       # Интеграционные тесты
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
└── README.md              # Этот файл
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

## 🔧 Общие компоненты

Директория `stage-env/tests/common/` содержит переиспользуемые компоненты:

### Wallets
- `create_wallet.yml` - создание тестового кошелька

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

```yaml
name: Test Name
description: What this test does
tags: [category, feature, priority]
version: "1.0"

network:
  topology: default  # или single_node, network_minimal

includes:
  - common/wallets/create_wallet.yml
  - common/networks/single_node.yml

setup:
  - cli: command here
    node: node1
    expect: success
    save: variable_name
    wait: 3s
    description: "What this step does"

test:
  # CLI Command
  - cli: another command
    node: node1
    expect: success
    contains: "expected output"
    description: "Test step description"
  
  # Python Code
  - python: |
      # Код с доступом к контексту через ctx
      result = ctx.get_variable('variable_name')
      assert 'expected' in result
    save: python_result
    description: "Python computation"
  
  # Bash Script
  - bash: |
      echo "Running on node"
      some_command
    node: node1
    expect: success
    save: bash_result
    description: "Bash script execution"

check:
  # CLI Check
  - cli: status command
    node: node1
    contains: "expected"
    description: "Verify status"
  
  # Python Check
  - python: |
      value = ctx.get_variable('variable_name')
      assert value > 0, "Value must be positive"
    description: "Python assertion"
  
  # Bash Check
  - bash: |
      # Exit 0 = success, Exit 1 = failure
      [ -f /some/file ] && exit 0 || exit 1
    node: node1
    description: "Bash condition check"
```

## 🆕 Расширенные возможности языка сценариев

### Python блоки

Python блоки имеют доступ к контексту выполнения через объект `ctx`:

```yaml
test:
  - python: |
      # Получить значение переменной
      wallet_addr = ctx.get_variable('wallet_addr')
      
      # Установить переменную
      ctx.set_variable('computed_value', wallet_addr.upper())
      
      # Результат можно сохранить
      result = len(wallet_addr)
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

### Bash блоки

Bash скрипты выполняются внутри Docker контейнеров узлов:

```yaml
test:
  - bash: |
      # Полный доступ к shell
      ls -la /opt/cellframe-node/var
      cat /proc/meminfo | grep MemTotal
      echo "Result: OK"
    node: node1
    expect: success
    save: node_info
    description: "Collect node info"

check:
  - bash: |
      # Проверка условия (exit 0 = success)
      if [ -f /opt/cellframe-node/var/run/cellframe-node.pid ]; then
        exit 0
      else
        exit 1
      fi
    node: node1
    description: "Check PID file exists"
```

### Substitution переменных

Во всех блоках доступна подстановка переменных:

```yaml
test:
  - cli: wallet info -w {{wallet_name}} -net stagenet
    node: node1
    save: wallet_info
  
  - python: |
      info = ctx.get_variable('wallet_info')
      # Переменные автоматически подставляются
    description: "Process {{wallet_name}}"
  
  - bash: |
      echo "Working with {{wallet_addr}}"
    node: node1
```

## 🚀 Запуск тестов

### Запуск всех E2E тестов
```bash
cd tests
./stage-env/stage-env --config=stage-env.cfg run-tests e2e/
```

### Запуск конкретного сьюта
```bash
./stage-env/stage-env --config=stage-env.cfg run-tests e2e/wallet/
```

### Запуск функциональных тестов
```bash
./stage-env/stage-env --config=stage-env.cfg run-tests functional/
```

### Запуск с фильтром
```bash
./stage-env/stage-env --config=stage-env.cfg run-tests e2e/ --filter=wallet
```

### Без автоматического старта сети
```bash
./stage-env/stage-env --config=stage-env.cfg run-tests e2e/wallet/ --no-start-network
```

### С сохранением сети после тестов
```bash
./stage-env/stage-env --config=stage-env.cfg run-tests e2e/wallet/ --keep-running
```

## 🏷️ Теги тестов

- `fast` - быстрые тесты (< 30 секунд)
- `slow` - медленные тесты (> 2 минут)
- `critical` - критически важные тесты
- `smoke` - smoke-тесты для быстрой проверки
- `e2e` - end-to-end тесты
- `functional` - функциональные тесты
- `wallet`, `token`, `net`, `node`, `chain`, `mempool` - по компонентам

## 📊 Артефакты

После запуска тестов артефакты сохраняются в:

```
testing/artifacts/
└── run_YYYYMMDD_HHMMSS/
    ├── scenario-logs/           # Логи каждого сценария
    ├── stage-env-logs/          # Логи stage-env
    ├── node-logs/               # Логи узлов
    ├── core-dumps/              # Core dumps (если были)
    ├── stack-traces/            # Stack traces
    ├── health-logs/             # Health check логи
    └── reports/                 # Отчеты
```

## 🔍 Отладка

### Просмотр логов последнего запуска
```bash
ls -t testing/artifacts/ | head -1 | xargs -I {} cat testing/artifacts/{}/scenario-logs/*.log
```

### Запуск с сохранением сети
```bash
./stage-env/stage-env --config=stage-env.cfg run-tests e2e/wallet/ --keep-running
```

Затем можно вручную проверить узлы:
```bash
docker exec cellframe-stage-node-1 cellframe-node-cli wallet list
docker exec cellframe-stage-node-1 bash -c "ls -la /opt/cellframe-node/var"
```

## 💡 Примеры использования

### Пример: Комплексная проверка с Python

```yaml
name: Token Balance Validation
test:
  - cli: token_emit -net stagenet -token TEST -value 1000 -addr {{addr}}
    save: tx_hash
    node: node1
    wait: 3s
  
  - cli: wallet info -w test_wallet -net stagenet
    save: wallet_info
    node: node1
  
  - python: |
      info = ctx.get_variable('wallet_info')
      # Парсим баланс
      import re
      match = re.search(r'balance:\s+(\d+)', info)
      if match:
          balance = int(match.group(1))
          ctx.set_variable('parsed_balance', balance)
    description: "Parse balance from wallet info"

check:
  - python: |
      balance = ctx.get_variable('parsed_balance')
      assert balance == 1000, f"Expected 1000, got {balance}"
    description: "Verify exact balance"
```

### Пример: Bash скрипт для системных проверок

```yaml
name: System Resource Check
test:
  - bash: |
      # Собираем системную информацию
      mem=$(free -m | awk 'NR==2{print $3}')
      disk=$(df -h / | awk 'NR==2{print $5}' | tr -d '%')
      echo "mem=$mem,disk=$disk"
    node: node1
    save: sys_info
    description: "Collect system metrics"

check:
  - bash: |
      # Проверяем что свободно достаточно ресурсов
      mem=$(free -m | awk 'NR==2{print $4}')
      if [ $mem -lt 100 ]; then
        echo "Low memory: ${mem}MB"
        exit 1
      fi
      exit 0
    node: node1
    description: "Verify sufficient memory"
```

## 📚 Документация

- [Stage Environment README](stage-env/README.md) - подробная документация stage-env
- [Scenario Format](stage-env/docs/scenarios.md) - формат YAML сценариев
- [CLI Commands](stage-env/docs/cli.md) - доступные CLI команды

## 🤝 Вклад

При добавлении новых тестов:

1. Выберите правильную категорию (e2e или functional)
2. Создайте/используйте подходящий сьют
3. Пронумеруйте тест (следующий номер)
4. Переиспользуйте common компоненты где возможно
5. Добавьте описательные теги
6. Документируйте каждый шаг через `description`
7. Используйте Python/Bash блоки для сложной логики

## 📞 Поддержка

Вопросы и проблемы: https://github.com/cellframe/cellframe-node/issues
