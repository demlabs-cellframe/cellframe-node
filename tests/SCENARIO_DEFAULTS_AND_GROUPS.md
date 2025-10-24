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

