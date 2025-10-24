# Scenario Language: Defaults and Grouping

## Обзор

Язык сценариев поддерживает иерархическую систему параметров по умолчанию и группировку шагов для более чистого и удобного кода.

## Уровни Defaults

### 1. Global Defaults (Глобальные)

Применяются ко всем секциям (`setup`, `test`, `check`):

```yaml
name: My Scenario
defaults:
  node: node1
  wait: 3s
  timeout: 60
  expect: success

setup:
  - cli: wallet new -w test  # Наследует node=node1, wait=3s, timeout=60
  
test:
  - cli: token_decl -net stagenet -token TEST  # Тоже наследует
```

### 2. Section Defaults (На уровне секции)

Переопределяют глобальные для конкретной секции:

```yaml
defaults:
  node: node1
  wait: 2s

setup:
  defaults:
    wait: 5s  # Переопределяет глобальное для setup
  
  steps:
    - cli: wallet new -w test  # node=node1, wait=5s
    
test:
  defaults:
    node: node2  # Переопределяет node для test
  
  steps:
    - cli: wallet list  # node=node2, wait=2s (глобальное)
```

### 3. Group Defaults (Групповые)

Применяются только к шагам внутри группы:

```yaml
test:
  defaults:
    node: node1
  
  steps:
    - group:
        name: "Node2 Operations"
        defaults:
          node: node2
          wait: 4s
        
        steps:
          - cli: wallet list  # node=node2, wait=4s
          - cli: token info   # node=node2, wait=4s
    
    - cli: net get status  # node=node1 (section default)
```

### 4. Step Level (Уровень шага)

Всегда имеет наивысший приоритет:

```yaml
defaults:
  node: node1
  wait: 3s

test:
  - cli: wallet list  # node=node1, wait=3s
  
  - cli: wallet list
    node: node2      # Переопределяет node
    wait: 1s         # Переопределяет wait
```

## Приоритет наследования

```
Step > Group > Section > Global > Hardcoded Default
```

**Пример:**
```yaml
defaults:
  node: node1   # Global
  wait: 2s      # Global

test:
  defaults:
    wait: 3s    # Section (переопределяет Global wait)
  
  steps:
    - group:
        defaults:
          node: node2  # Group (переопределяет Global node)
          wait: 4s     # Group (переопределяет Section wait)
        
        steps:
          - cli: wallet list  # node=node2, wait=4s
          
          - cli: token info
            wait: 1s          # Step (переопределяет Group wait)
                              # node=node2 (Group)
```

**Итог:**
- Первый CLI: `node=node2` (Group), `wait=4s` (Group)
- Второй CLI: `node=node2` (Group), `wait=1s` (Step)

## Группировка шагов

### Простая группа

```yaml
test:
  - group:
      name: "Setup Wallets"
      description: "Create test wallets"
      defaults:
        wait: 2s
      
      steps:
        - cli: wallet new -w wallet1
        - cli: wallet new -w wallet2
        - cli: wallet new -w wallet3
```

### Вложенные группы

```yaml
test:
  - group:
      name: "Multi-node Operations"
      defaults:
        wait: 3s
      
      steps:
        - group:
            name: "Node1 Tasks"
            defaults:
              node: node1
            steps:
              - cli: wallet list
              - cli: token info
        
        - group:
            name: "Node2 Tasks"
            defaults:
              node: node2
            steps:
              - cli: wallet list
              - cli: token info
```

### Группы для организации кода

Используйте группы для:
- **Логического разделения:** Группировка связанных операций
- **Читаемости:** Наглядная структура сценария
- **Переиспользования defaults:** Избежать повторения параметров
- **Отладки:** Логи показывают вход/выход из групп

## Параметры Defaults

### Поддерживаемые параметры

```yaml
defaults:
  node: node1       # Нода для выполнения CLI/RPC команд
  wait: 3s          # Задержка после каждого шага
  expect: success   # Ожидаемый результат (success/error)
  timeout: 60       # Таймаут команды в секундах
```

### Применяются к:

**Steps:**
- `CLIStep` - все параметры
- `RPCStep` - все параметры
- `BashStep` - все параметры
- `WaitStep` - не применяются
- `PythonStep` - не применяются

**Checks:**
- `CLICheck` - `node`, `timeout`
- `RPCCheck` - `node`, `timeout`
- `BashCheck` - `node`, `timeout`
- `PythonCheck` - не применяются

## Обратная совместимость

Старый формат (список шагов) по-прежнему работает:

```yaml
# Старый формат - OK
setup:
  - cli: wallet new -w test
    node: node1
    wait: 3s

# Новый формат - тоже OK
setup:
  defaults:
    node: node1
    wait: 3s
  steps:
    - cli: wallet new -w test
```

## Примеры использования

### До (много повторений):

```yaml
test:
  - cli: wallet new -w wallet1
    node: node1
    wait: 3s
  
  - cli: wallet new -w wallet2
    node: node1
    wait: 3s
  
  - cli: wallet list
    node: node1
    wait: 3s
```

### После (чисто и ясно):

```yaml
defaults:
  node: node1
  wait: 3s

test:
  - cli: wallet new -w wallet1
  - cli: wallet new -w wallet2
  - cli: wallet list
```

**Результат:** 55% меньше кода, легче читать и поддерживать!

### Многоузловой сценарий:

```yaml
defaults:
  wait: 2s

test:
  - group:
      name: "Prepare Node1"
      defaults:
        node: node1
      steps:
        - cli: wallet new -w node1_wallet
        - cli: token_decl -net stagenet -token TEST1
  
  - group:
      name: "Prepare Node2"
      defaults:
        node: node2
      steps:
        - cli: wallet new -w node2_wallet
        - cli: token_decl -net stagenet -token TEST2
  
  # Cross-node interaction
  - cli: net -net stagenet link list
    node: node1
```

## Реальные примеры оптимизации

### Пример 1: Token Emission Test

**До (37 строк):**
```yaml
name: Token Emission Test
description: Test emitting tokens
tags: [e2e, token]

network:
  topology: default

includes:
  - common/networks/single_node.yml
  - common/wallets/create_wallet.yml

setup:
  - cli: token_decl -net stagenet -token EMITTEST -total 1000000
    node: node1
    wait: 3s
    description: "Declare EMITTEST token"

test:
  - cli: token_emit -net stagenet -token EMITTEST -value 10000 -addr {{wallet_addr}}
    node: node1
    save: emit_tx
    wait: 3s
    description: "Emit tokens to wallet"

check:
  - cli: token info -net stagenet -token EMITTEST -history_limit 10
    node: node1
    contains: "EMITTEST"
    description: "Token history contains emission"
```

**После (24 строки - экономия 35%):**
```yaml
name: Token Emission Test
description: Test emitting tokens
tags: [e2e, token]

network:
  topology: default

includes:
  - common/networks/single_node.yml
  - common/wallets/create_wallet.yml

defaults:
  node: node1
  wait: 3s

setup:
  - cli: token_decl -net stagenet -token EMITTEST -total 1000000
    description: "Declare EMITTEST token"

test:
  - cli: token_emit -net stagenet -token EMITTEST -value 10000 -addr {{wallet_addr}}
    save: emit_tx
    description: "Emit tokens"

check:
  - cli: token info -net stagenet -token EMITTEST -history_limit 10
    contains: "EMITTEST"
```

### Пример 2: UTXO Blocking Test

**До (62 строки):**
```yaml
setup:
  - cli: token_decl -net stagenet -token ADDTEST -total 1000000 -flags UTXO_BLOCKING_ENABLED
    save: token
    node: node1
    expect: success
    wait: 3s
    description: "Create ADDTEST token"
  
  - cli: token_emit -net stagenet -token ADDTEST -value 1000 -addr {{wallet_addr}}
    save: emission
    node: node1
    expect: success
    wait: 3s
    description: "Emit tokens"
  
  - cli: tx_create -net stagenet -token ADDTEST -from_emission {{emission}} -value 500
    save: utxo
    node: node1
    expect: success
    wait: 3s
    description: "Create UTXO"

test:
  - cli: token_update -net stagenet -token ADDTEST -utxo_blocked_add {{utxo}}:0
    node: node1
    expect: success
    wait: 3s
    description: "Add UTXO to blocklist"
```

**После (42 строки - экономия 32%):**
```yaml
defaults:
  node: node1
  wait: 3s

setup:
  - cli: token_decl -net stagenet -token ADDTEST -total 1000000 -flags UTXO_BLOCKING_ENABLED
    save: token
    description: "Create ADDTEST token"
  
  - cli: token_emit -net stagenet -token ADDTEST -value 1000 -addr {{wallet_addr}}
    save: emission
    description: "Emit tokens"
  
  - cli: tx_create -net stagenet -token ADDTEST -from_emission {{emission}} -value 500
    save: utxo
    description: "Create UTXO"

test:
  - cli: token_update -net stagenet -token ADDTEST -utxo_blocked_add {{utxo}}:0
    description: "Add UTXO to blocklist"
```

### Пример 3: Multi-node Integration Test

**До (без групп - трудно читать):**
```yaml
test:
  - cli: wallet new -w node1_wallet
    node: node1
    wait: 3s
  - cli: token_decl -net stagenet -token TOKEN1 -total 1000000
    node: node1
    wait: 3s
  - cli: token_emit -net stagenet -token TOKEN1 -value 1000 -addr {{node1_addr}}
    node: node1
    wait: 5s
  - cli: wallet new -w node2_wallet
    node: node2
    wait: 3s
  - cli: token_decl -net stagenet -token TOKEN2 -total 1000000
    node: node2
    wait: 3s
  - cli: tx_create -from {{node1_addr}} -to {{node2_addr}} -value 100
    node: node1
    wait: 10s
```

**После (с группами - структура ясна):**
```yaml
defaults:
  wait: 3s

test:
  - group:
      name: "Setup Node1"
      description: "Prepare token and wallet on node1"
      defaults:
        node: node1
      steps:
        - cli: wallet new -w node1_wallet
        - cli: token_decl -net stagenet -token TOKEN1 -total 1000000
        - cli: token_emit -net stagenet -token TOKEN1 -value 1000 -addr {{node1_addr}}
          wait: 5s  # Longer wait for emission
  
  - group:
      name: "Setup Node2"
      description: "Prepare token and wallet on node2"
      defaults:
        node: node2
      steps:
        - cli: wallet new -w node2_wallet
        - cli: token_decl -net stagenet -token TOKEN2 -total 1000000
  
  - cli: tx_create -from {{node1_addr}} -to {{node2_addr}} -value 100
    node: node1
    wait: 10s
    description: "Cross-node transfer"
```

### Пример 4: Компактный Wallet Test Suite

**До (3 файла × 40 строк = 120 строк):**
```yaml
# 001_wallet_create.yml
test:
  - cli: wallet new -w test_wallet_default
    node: node1
    wait: 2s
  - cli: wallet list
    node: node1

# 002_wallet_address.yml  
test:
  - cli: wallet new -w test_addr_wallet
    node: node1
    wait: 2s
  - cli: wallet info -w test_addr_wallet -net stagenet
    node: node1
    save: wallet_info

# 003_wallet_multiple.yml
test:
  - cli: wallet new -w multi_wallet_1
    node: node1
    wait: 2s
  - cli: wallet new -w multi_wallet_2
    node: node1
    wait: 2s
  - cli: wallet new -w multi_wallet_3
    node: node1
    wait: 2s
```

**После (3 файла × 20 строк = 60 строк - экономия 50%):**
```yaml
# Каждый файл теперь:
defaults:
  node: node1
  wait: 2s

test:
  - cli: wallet new -w test_wallet_default
  - cli: wallet list
```

## Best Practices

1. **Используйте глобальные defaults** для общих параметров (node, wait)
2. **Группируйте связанные операции** для читаемости
3. **Переопределяйте только нужное** - не дублируйте defaults
4. **Именуйте группы** - помогает при отладке по логам
5. **Не злоупотребляйте вложенностью** - максимум 2-3 уровня

## Отладка

При выполнении группы в логах видно:

```
[info] Entering group: Node1 Operations
[info] Step 1/3: CLIStep
[debug] Executing CLI: wallet new -w test on node1
[info] Step 2/3: CLIStep
...
[info] Exited group: Node1 Operations
```

Это помогает понять в какой группе произошла ошибка.

## См. также

- `tests/e2e/examples/test_defaults_and_groups.yml` - полный пример
- `tests/e2e/token/002_token_emit.yml` - простое использование defaults

