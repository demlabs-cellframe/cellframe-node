# Test Scenarios Reference

Полная справка по всем возможностям системы тестовых сценариев.

## Оглавление

- [Структура сценария](#структура-сценария)
- [Метаданные](#метаданные)
- [Конфигурация сети](#конфигурация-сети)
- [Установка пакетов](#установка-пакетов)
- [Размещение файлов](#размещение-файлов)
- [Шаги теста](#шаги-теста)
- [Проверки](#проверки)
- [Переменные](#переменные)
- [Includes](#includes)

---

## Структура сценария

Полная структура YAML файла сценария:

```yaml
# === МЕТАДАННЫЕ (обязательно) ===
name: string                    # Название сценария
description: string             # Описание что тестируем
author: string                  # Автор (опционально)
tags: [string, ...]            # Теги для категоризации
version: string                 # Версия сценария (default: "1.0")

# === INCLUDES (опционально) ===
includes:
  - path/to/template.yml       # Переиспользуемые конфиги

# === КОНФИГУРАЦИЯ СЕТИ (обязательно) ===
network:
  topology: string              # Имя топологии
  nodes: [...]                  # Список нод

# === УСТАНОВКА ПАКЕТОВ (опционально) ===
packages:
  - node: string | [string]     # Ноды для установки
    apt: [string]               # APT пакеты
  - node: string | [string]
    local: string               # Локальный .deb файл
  - node: string | [string]
    url: string                 # URL для скачивания
    checksum: string            # SHA256 checksum

# === РАЗМЕЩЕНИЕ ФАЙЛОВ (опционально) ===
files:
  - node: string | [string]     # Целевые ноды
    src: string                 # Исходный файл на хосте
    dst: string                 # Путь в ноде
    mode: string                # Права доступа
  - node: string | [string]
    content: string             # Inline контент
    dst: string
    mode: string

# === ПРЕДУСТАНОВЛЕННЫЕ ПЕРЕМЕННЫЕ (опционально) ===
variables:
  key: value                    # Глобальные переменные

# === ПОДГОТОВКА (опционально) ===
setup:
  - [test_step]                 # Шаги подготовки

# === ОСНОВНОЙ ТЕСТ (обязательно) ===
test:
  - [test_step]                 # Тестовые шаги

# === ПРОВЕРКИ (рекомендуется) ===
check:
  - [check_spec]                # Assertions
```

---

## Метаданные

### name (обязательно)
Название сценария. Должно быть понятным и описательным.

```yaml
name: Token Transfer Test
```

### description (обязательно)
Подробное описание что тестирует сценарий.

```yaml
description: Verifies that tokens can be transferred between wallets
```

### author (опционально)
Имя автора сценария.

```yaml
author: QA Team
```

### tags (опционально)
Список тегов для категоризации и фильтрации.

```yaml
tags: [tokens, transfer, critical, fast]
```

Рекомендуемые категории тегов:
- **Функция**: `tokens`, `wallet`, `consensus`, `network`
- **Приоритет**: `critical`, `high`, `medium`, `low`
- **Длительность**: `fast` (<1min), `medium` (1-5min), `slow` (>5min)
- **Тип**: `smoke`, `regression`, `integration`, `e2e`

### version (опционально)
Версия сценария. По умолчанию `"1.0"`.

```yaml
version: "2.1"
```

---

## Конфигурация сети

### network.topology
Имя топологии сети. Определяет базовую конфигурацию нод.

```yaml
network:
  topology: minimal     # Одна нода
  # или
  topology: default     # 4 ноды (3 validator + 1 full)
  # или
  topology: custom      # Кастомная топология
```

Доступные топологии:
- `minimal` - 1 root validator
- `default` - 4 ноды (3 validators + 1 full)

### network.nodes
Список нод в сети.

```yaml
network:
  nodes:
    - name: node1           # Уникальное имя ноды
      role: root            # Роль в сети
      validator: true       # Является ли валидатором
      ip: 172.20.0.10      # IP адрес (опционально)
```

**Роли нод:**
- `root` - корневая нода
- `master` - мастер нода
- `full` - полная нода
- `light` - лёгкая нода
- `archive` - архивная нода

**Пример конфигурации:**

```yaml
network:
  topology: default
  nodes:
    - name: node1
      role: root
      validator: true
    
    - name: node2
      role: master
      validator: true
    
    - name: node3
      role: full
      validator: false
```

---

## Установка пакетов

Позволяет устанавливать пакеты в ноды перед выполнением теста.

### APT пакеты

```yaml
packages:
  - node: node1              # Одна нода
    apt:
      - curl
      - jq
      - net-tools
  
  - node: [node1, node2]     # Несколько нод
    apt: [vim, htop]
```

### Локальные пакеты

```yaml
packages:
  - node: node1
    local: ../build/cellframe-node_*.deb     # Glob поддерживается
  
  - node: [node1, node2, node3]
    local: /tmp/custom-plugin.deb
```

### Пакеты по URL

```yaml
packages:
  - node: node1
    url: https://example.com/package.deb
    checksum: sha256:abc123...    # Опционально для проверки
```

---

## Размещение файлов

Копирование файлов с хоста в ноды или создание файлов с inline контентом.

### Копирование с хоста

```yaml
files:
  - node: node1
    src: configs/custom.cfg
    dst: /opt/cellframe-node/etc/custom.cfg
    mode: "0644"                    # Права доступа (опционально)
  
  - node: [node1, node2]
    src: scripts/init.sh
    dst: /usr/local/bin/init.sh
    mode: "0755"
```

### Inline контент

```yaml
files:
  - node: node1
    content: |
      [network]
      name=testnet
      enabled=true
    dst: /opt/cellframe-node/etc/testnet.cfg
  
  - node: node1
    content: "wallet_addr={{wallet_addr}}"    # С переменными
    dst: /tmp/test_vars.conf
```

---

## Шаги теста

### CLI Step

Выполнение команды cellframe-node-cli.

```yaml
- cli: wallet new -w my_wallet        # Команда (обязательно)
  node: node1                          # Нода для выполнения (default: node1)
  save: wallet_addr                    # Сохранить результат в переменную
  wait: 3s                             # Подождать после выполнения
  expect: success                      # Ожидаемый результат (success/error/any)
  contains: "Created"                  # Проверить наличие текста
  timeout: 30                          # Таймаут в секундах (default: 30)
```

**Параметры:**
- `cli` (string, обязательно) - команда для выполнения
- `node` (string, default: "node1") - имя ноды
- `save` (string, опционально) - имя переменной для сохранения результата
- `wait` (string, опционально) - время ожидания (формат: "5s", "100ms", "2m")
- `expect` (enum, default: "success") - ожидаемый результат
  - `success` - команда должна завершиться успешно (exit code 0)
  - `error` - команда должна завершиться с ошибкой (exit code != 0)
  - `any` - любой результат допустим
- `contains` (string, опционально) - подстрока которая должна быть в выводе
- `timeout` (int, default: 30) - таймаут выполнения в секундах

**Примеры:**

```yaml
# Простая команда
- cli: version

# С сохранением результата
- cli: wallet new -w test
  save: addr

# С проверкой вывода
- cli: wallet list
  contains: test

# Ожидание ошибки
- cli: transfer -value 999999999
  expect: error
  contains: insufficient funds

# С таймаутом и ожиданием
- cli: token_emit -token TEST -value 1000000
  timeout: 60
  wait: 5s
```

### RPC Step

Выполнение JSON-RPC вызова.

```yaml
- rpc: eth_blockNumber              # Метод (обязательно)
  params: []                         # Параметры (default: [])
  node: node1                        # Нода (default: node1)
  save: block_num                    # Сохранить результат
  wait: 1s                           # Подождать после вызова
  expect: success                    # Ожидаемый результат
  timeout: 30                        # Таймаут (default: 30)
```

**Параметры:**
- `rpc` (string, обязательно) - имя JSON-RPC метода
- `params` (list, default: []) - параметры метода
- `node` (string, default: "node1") - имя ноды
- `save` (string, опционально) - переменная для сохранения результата
- `wait` (string, опционально) - время ожидания
- `expect` (enum, default: "success") - ожидаемый результат
- `timeout` (int, default: 30) - таймаут в секундах

**Примеры:**

```yaml
# Простой вызов
- rpc: net_version
  params: []

# С параметрами
- rpc: eth_getBalance
  params: ["0x1234...", "latest"]
  save: balance

# С переменными
- rpc: eth_getTransactionReceipt
  params: ["{{tx_hash}}"]
  save: receipt
```

### Wait Step

Пауза между шагами.

```yaml
- wait: 5s      # 5 секунд
- wait: 100ms   # 100 миллисекунд
- wait: 2m      # 2 минуты
```

**Форматы времени:**
- `s` - секунды
- `ms` - миллисекунды
- `m` - минуты

### Loop Step

Повторение шагов несколько раз.

```yaml
- loop: 10                          # Количество итераций (обязательно)
  steps:                            # Шаги для повторения (обязательно)
    - cli: tx_create -value {{i * 100}}
    - wait: 1s
```

**Доступные переменные в цикле:**
- `{{i}}` - индекс итерации (0-based): 0, 1, 2, ...
- `{{iteration}}` - номер итерации (1-based): 1, 2, 3, ...

**Примеры:**

```yaml
# Создать 10 кошельков
- loop: 10
  steps:
    - cli: wallet new -w wallet{{iteration}}
      save: addr{{iteration}}

# Массовая рассылка
- loop: 100
  steps:
    - cli: transfer -to {{recipient}} -value {{i + 1}}
      wait: 500ms
```

---

## Проверки

### CLI Check

Проверка вывода CLI команды.

```yaml
- cli: wallet list                   # Команда (обязательно)
  node: node1                        # Нода (default: node1)
  contains: my_wallet                # Должно содержать текст
  not_contains: error                # НЕ должно содержать текст
  equals: "Balance: 1000"            # Точное совпадение
  timeout: 30                        # Таймаут (default: 30)
```

**Параметры:**
- `cli` (string, обязательно) - команда для выполнения
- `node` (string, default: "node1") - имя ноды
- `contains` (string, опционально) - подстрока которая должна присутствовать
- `not_contains` (string, опционально) - подстрока которой НЕ должно быть
- `equals` (string, опционально) - точное совпадение всего вывода
- `timeout` (int, default: 30) - таймаут в секундах

**Примеры:**

```yaml
check:
  # Проверить наличие
  - cli: wallet list
    contains: test_wallet
  
  # Проверить отсутствие
  - cli: token info -token TEST
    not_contains: error
  
  # Точное совпадение
  - cli: net status
    equals: connected
  
  # С переменными
  - cli: balance -addr {{wallet_addr}}
    contains: "{{expected_balance}}"
```

### RPC Check

Проверка результата JSON-RPC вызова.

```yaml
- rpc: eth_blockNumber              # Метод (обязательно)
  params: []                         # Параметры (default: [])
  node: node1                        # Нода (default: node1)
  result_contains: "0x"              # Результат должен содержать
  result_equals: "0x1"               # Результат должен равняться
  timeout: 30                        # Таймаут (default: 30)
```

**Параметры:**
- `rpc` (string, обязательно) - имя метода
- `params` (list, default: []) - параметры
- `node` (string, default: "node1") - имя ноды
- `result_contains` (any, опционально) - значение должно содержаться в результате
- `result_equals` (any, опционально) - результат должен точно совпадать
- `timeout` (int, default: 30) - таймаут

**Примеры:**

```yaml
check:
  # Проверить формат
  - rpc: net_version
    result_contains: "1"
  
  # Точное значение
  - rpc: eth_chainId
    result_equals: "0x1"
  
  # С переменными
  - rpc: eth_getTransactionReceipt
    params: ["{{tx_hash}}"]
    result_contains: status
```

---

## Переменные

### Определение переменных

Переменные можно определить в секции `variables`:

```yaml
variables:
  token_name: MYTOKEN
  initial_supply: 1000000
  test_value: 100
```

### Сохранение из шагов

Результаты команд можно сохранять в переменные:

```yaml
setup:
  - cli: wallet new -w test
    save: wallet_addr        # Сохранить вывод в wallet_addr
  
  - cli: token_decl -token TEST
    save: token_hash         # Сохранить в token_hash
```

### Использование переменных

Используйте синтаксис `{{имя_переменной}}`:

```yaml
test:
  - cli: transfer -to {{wallet_addr}} -value {{test_value}}
  
  - cli: token info -token {{token_name}}
    contains: {{token_hash}}
```

### Специальные переменные в циклах

В `loop` доступны:
- `{{i}}` - индекс (0, 1, 2, ...)
- `{{iteration}}` - номер (1, 2, 3, ...)

```yaml
- loop: 5
  steps:
    - cli: wallet new -w wallet{{i}}      # wallet0, wallet1, ...
    - cli: echo "Iteration {{iteration}}" # Iteration 1, 2, ...
```

---

## Includes

Переиспользование конфигураций из других файлов.

### Базовый синтаксис

```yaml
includes:
  - common/network_minimal.yml
  - common/wallet_setup.yml
  - my_test/custom_config.yml
```

### Порядок объединения

1. Сначала загружаются все `includes` (в порядке указания)
2. Затем применяется основной файл сценария
3. Основной файл **перезаписывает** значения из includes

### Правила слияния

- **Словари** (dict) - рекурсивно объединяются
- **Списки** (list) - конкатенируются
- **Скаляры** - основной файл перезаписывает include

**Пример:**

`common/base.yml`:
```yaml
network:
  topology: minimal

setup:
  - cli: version
```

`my_test.yml`:
```yaml
includes:
  - common/base.yml

network:
  nodes:
    - name: node1
      role: root

setup:
  - cli: wallet new -w test    # Добавится к setup из base.yml
```

**Результат:**
```yaml
network:
  topology: minimal              # Из base.yml
  nodes:                         # Из my_test.yml
    - name: node1
      role: root

setup:
  - cli: version                 # Из base.yml
  - cli: wallet new -w test      # Из my_test.yml
```

### Относительные пути

Пути в `includes` относительны к директории сценария:

```
tests/scenarios/
  common/
    network_minimal.yml
  features/
    subfolder/
      my_test.yml
```

В `my_test.yml`:
```yaml
includes:
  - ../../common/network_minimal.yml    # Относительный путь
```

---

## Примеры полных сценариев

### Минимальный тест

```yaml
name: Basic Version Check
description: Verify node responds to version command
tags: [smoke, fast]

network:
  topology: minimal
  nodes:
    - name: node1
      role: root

test:
  - cli: version
    expect: success
```

### Тест с подготовкой

```yaml
name: Token Creation and Emission
description: Create token and emit initial supply
tags: [tokens, critical]

includes:
  - common/network_minimal.yml
  - common/wallet_setup.yml

setup:
  - cli: token_decl -token TEST -total 1000000
    save: token_hash
    wait: 3s

test:
  - cli: token_emit -token TEST -value 1000000 -addr {{wallet_addr}}
    save: emission_tx
    expect: success
    wait: 3s

check:
  - cli: token list
    contains: TEST
  
  - cli: balance -addr {{wallet_addr}} -token TEST
    contains: "1000000"
```

### Комплексный тест

```yaml
name: Multi-Wallet Token Transfer
description: Test token transfers between multiple wallets
author: QA Team
tags: [tokens, transfer, integration, medium]
version: "1.0"

includes:
  - common/network_full.yml

variables:
  token_name: TRANSFER_TEST
  total_supply: 10000000
  wallets_count: 5

setup:
  # Create wallets
  - loop: {{wallets_count}}
    steps:
      - cli: wallet new -w wallet{{iteration}}
        save: addr{{iteration}}
  
  # Create token
  - cli: token_decl -token {{token_name}} -total {{total_supply}}
    save: token_hash
    wait: 3s
  
  # Emit to first wallet
  - cli: token_emit -token {{token_name}} -value {{total_supply}} -addr {{addr1}}
    wait: 3s

test:
  # Distribute tokens
  - loop: 4
    steps:
      - cli: transfer -token {{token_name}} -from {{addr1}} -to {{addr{{i+2}}}} -value 1000000
        wait: 2s

check:
  # Verify balances
  - cli: balance -addr {{addr1}} -token {{token_name}}
    contains: "6000000"
  
  - loop: 4
    steps:
      - cli: balance -addr {{addr{{i+2}}}} -token {{token_name}}
        contains: "1000000"
```

---

## Валидация сценариев

Проверить сценарий перед запуском:

```bash
./tests/stage-env/stage-env validate tests/scenarios/features/my_test.yml
```

Валидатор проверяет:
- ✅ Синтаксис YAML
- ✅ Соответствие схеме
- ✅ Определение всех используемых переменных
- ✅ Ссылки на существующие ноды
- ✅ Корректность значений timeout
- ✅ Best practices

---

## См. также

- [Getting Started](GETTING_STARTED.md) - Быстрый старт
- [README](README.md) - Основная документация
- [Cookbook](COOKBOOK.md) - Рецепты для типовых задач

