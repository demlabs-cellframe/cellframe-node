# Test Scenarios Cookbook

Готовые рецепты для типовых задач тестирования Cellframe Node.

## Содержание

- [Wallet Operations](#wallet-operations)
- [Token Management](#token-management)
- [Transactions](#transactions)
- [Network Operations](#network-operations)
- [Advanced Patterns](#advanced-patterns)

---

## Wallet Operations

### Создать кошелёк и сохранить адрес

```yaml
- cli: wallet new -w my_wallet
  save: wallet_addr
  wait: 1s
```

### Создать несколько кошельков

```yaml
- loop: 5
  steps:
    - cli: wallet new -w wallet{{iteration}}
      save: addr{{iteration}}
```

### Проверить существование кошелька

```yaml
check:
  - cli: wallet list
    contains: my_wallet
```

### Экспортировать приватный ключ

```yaml
- cli: wallet export -w my_wallet
  save: private_key
```

---

## Token Management

### Декларировать токен

```yaml
- cli: token_decl -net stagenet -token MYTOKEN -total 1000000
  save: token_hash
  wait: 3s
```

### Декларировать с флагами

```yaml
- cli: token_decl -token TEST -total 1000000 -flags UTXO_BLOCKING_ENABLED
  save: token_hash
  wait: 3s
```

### Эмитировать токены

```yaml
- cli: token_emit -token MYTOKEN -value 100000 -addr {{wallet_addr}}
  save: emission_tx
  wait: 3s
```

### Получить информацию о токене

```yaml
- cli: token info -token MYTOKEN
  contains: {{token_hash}}
```

### Обновить токен

```yaml
- cli: token_update -token MYTOKEN -set_flags ALL_SENDER_FROZEN
  wait: 3s
```

### Заблокировать UTXO

```yaml
- cli: token_update -token MYTOKEN -utxo_blocked_add {{tx_hash}}:0
  wait: 3s
```

---

## Transactions

### Простой трансфер

```yaml
- cli: transfer -token TEST -to {{recipient_addr}} -value 1000
  save: tx_hash
  wait: 3s
```

### Создать транзакцию из эмиссии

```yaml
- cli: tx_create -token TEST -from_emission {{emission_tx}} -value 500
  save: tx_hash
  wait: 3s
```

### Арбитражная транзакция

```yaml
- cli: tx_create -token TEST -value 100 -arbitrage
  save: arb_tx
  expect: success
```

### Проверить историю транзакций

```yaml
check:
  - cli: tx_history -tx {{tx_hash}}
    contains: {{tx_hash}}
```

### Массовая рассылка

```yaml
- loop: 100
  steps:
    - cli: transfer -token TEST -to {{recipient{{i}}}} -value {{amount}}
      wait: 500ms
```

---

## Network Operations

### Проверить статус сети

```yaml
- cli: net status
  expect: success
```

### Получить список нод

```yaml
- cli: net list
  save: nodes_list
```

### Проверить синхронизацию

```yaml
check:
  - cli: net sync
    contains: "synchronized"
```

### Получить информацию о блоке

```yaml
- rpc: eth_blockNumber
  save: block_num
```

---

## Advanced Patterns

### Последовательное создание и трансфер

```yaml
name: Sequential Token Transfer
includes:
  - common/network_minimal.yml

setup:
  - cli: wallet new -w sender
    save: sender_addr
  - cli: wallet new -w receiver
    save: receiver_addr
  - cli: token_decl -token TEST -total 1000000
    save: token
    wait: 3s
  - cli: token_emit -token TEST -value 100000 -addr {{sender_addr}}
    wait: 3s

test:
  - cli: transfer -token TEST -from {{sender_addr}} -to {{receiver_addr}} -value 50000
    save: tx
    wait: 3s

check:
  - cli: balance -addr {{sender_addr}} -token TEST
    contains: "50000"
  - cli: balance -addr {{receiver_addr}} -token TEST
    contains: "50000"
```

### Тест с ожидаемой ошибкой

```yaml
name: Block UTXO Transfer Test
setup:
  - cli: token_decl -token BLOCK -total 1000000 -flags UTXO_BLOCKING_ENABLED
    wait: 3s
  - cli: token_emit -token BLOCK -value 1000 -addr {{addr}}
    save: emission
    wait: 3s
  - cli: tx_create -token BLOCK -from_emission {{emission}} -value 100
    save: tx
    wait: 3s
  - cli: token_update -token BLOCK -utxo_blocked_add {{tx}}:0
    wait: 3s

test:
  # Обычная транзакция должна fail
  - cli: tx_create -token BLOCK -value 50
    expect: error
    contains: "UTXO is blocked"
```

### Условное выполнение через переменные

```yaml
variables:
  should_transfer: true
  transfer_amount: 1000

test:
  - cli: balance -addr {{wallet_addr}}
    save: balance
  
  # Трансфер только если баланс достаточный
  - cli: transfer -value {{transfer_amount}}
    node: node1
    # В реальности нужна поддержка условий в executor
```

### Параллельное тестирование на нескольких нодах

```yaml
network:
  topology: default
  nodes:
    - name: node1
      role: root
    - name: node2
      role: master
    - name: node3
      role: master

test:
  # Выполнить на node1
  - cli: wallet new -w wallet1
    node: node1
    save: addr1
  
  # Выполнить на node2
  - cli: wallet new -w wallet2
    node: node2
    save: addr2
  
  # Проверить репликацию
  - wait: 5s
  
  - cli: wallet list
    node: node3
    contains: wallet1
```

### Стресс-тест

```yaml
name: Token Transfer Stress Test
tags: [stress, slow]

setup:
  - cli: token_decl -token STRESS -total 100000000
    wait: 3s
  - cli: token_emit -token STRESS -value 100000000 -addr {{sender}}
    wait: 3s

test:
  - loop: 1000
    steps:
      - cli: transfer -token STRESS -to {{receiver}} -value {{i + 1}}
        timeout: 60

check:
  - cli: tx_history -limit 1000
    contains: STRESS
```

### Тест времени жизни (timelock)

```yaml
test:
  - cli: tx_create -token TEST -value 1000 -timelock +1h
    save: locked_tx
    wait: 3s
  
  # Попытка использовать сразу - должна fail
  - cli: tx_create -from {{locked_tx}} -value 500
    expect: error
    contains: "timelock"
```

### Мульти-подпись

```yaml
setup:
  - cli: wallet new -w wallet1
    save: addr1
  - cli: wallet new -w wallet2
    save: addr2
  - cli: wallet new -w wallet3
    save: addr3
  
  - cli: token_decl -token MULTISIG -total 1000000 -signs_required 2
    save: token
    wait: 3s

test:
  - cli: token_update -token MULTISIG -add_owner {{addr2}}
    wait: 3s
  - cli: token_update -token MULTISIG -add_owner {{addr3}}
    wait: 3s
```

---

## Полезные паттерны

### Шаблон: Prepare-Act-Assert

```yaml
# Prepare (setup)
setup:
  - cli: создание_ресурсов

# Act (test)
test:
  - cli: выполнение_действия

# Assert (check)
check:
  - cli: проверка_результата
```

### Шаблон: Given-When-Then

```yaml
name: Given-When-Then Pattern
description: BDD-style test

# Given: начальное состояние
setup:
  - cli: wallet new -w test
    save: addr

# When: действие
test:
  - cli: transfer -value 1000 -to {{addr}}
    save: tx

# Then: ожидаемый результат
check:
  - cli: balance -addr {{addr}}
    contains: "1000"
```

### Шаблон: Setup-Teardown

```yaml
# Setup
setup:
  - cli: создание_временных_ресурсов
    save: temp_resource

# Test
test:
  - cli: использование_ресурсов

# Teardown (через cleanup команды если поддерживается)
# или автоматическая очистка через stage-env stop --volumes
```

---

## Советы по производительности

### Минимизировать wait времена

```yaml
# Плохо: слишком долго
- cli: token_emit
  wait: 10s

# Хорошо: оптимальное время
- cli: token_emit
  wait: 3s
```

### Группировать операции

```yaml
# Плохо: много мелких шагов
- cli: wallet new -w w1
  wait: 1s
- cli: wallet new -w w2
  wait: 1s

# Хорошо: batch операции
- loop: 2
  steps:
    - cli: wallet new -w w{{iteration}}
```

### Использовать правильные топологии

```yaml
# Для быстрых тестов
network:
  topology: minimal  # 1 нода

# Для полных тестов
network:
  topology: default  # 4 ноды
```

---

## Debugging рецепты

### Вывести все переменные

```yaml
test:
  - cli: echo "Wallet: {{wallet_addr}}"
  - cli: echo "Token: {{token_hash}}"
  - cli: echo "TX: {{tx_hash}}"
```

### Добавить точки останова

```yaml
test:
  - cli: some_command
  - wait: 30s  # Пауза для ручной проверки
  - cli: next_command
```

### Сохранить все результаты

```yaml
test:
  - cli: wallet list
    save: all_wallets
  - cli: token list
    save: all_tokens
  - cli: tx_history
    save: all_transactions
```

---

Для большего количества примеров смотрите:
- `tests/scenarios/features/` - готовые тесты
- [Getting Started](GETTING_STARTED.md) - базовые примеры
- [Reference](REFERENCE.md) - полная справка

