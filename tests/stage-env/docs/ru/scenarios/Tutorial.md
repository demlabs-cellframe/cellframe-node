# Test Scenarios Tutorial

**Пошаговое руководство по написанию тест-сценариев для Cellframe Node**

Добро пожаловать! Это руководство научит вас писать автоматизированные тесты без программирования. Мы начнём с азов и постепенно перейдём к сложным сценариям.

## 📚 Содержание

1. [Введение](#введение)
2. [Урок 1: Первый тест](#урок-1-первый-тест)
3. [Урок 2: Переменные и сохранение результатов](#урок-2-переменные-и-сохранение-результатов)
4. [Урок 3: Проверки результатов](#урок-3-проверки-результатов)
5. [Урок 4: Переиспользование шаблонов](#урок-4-переиспользование-шаблонов)
6. [Урок 5: Работа с токенами](#урок-5-работа-с-токенами)
7. [Урок 6: Циклы и повторения](#урок-6-циклы-и-повторения)
8. [Урок 7: Сложные сценарии](#урок-7-сложные-сценарии)
9. [Урок 8: Лучшие практики](#урок-8-лучшие-практики)

---

## Введение

### Что такое тест-сценарий?

Тест-сценарий - это YAML файл, который описывает:
- **Что тестируем** - название и описание
- **Какую сеть используем** - топология нод
- **Какие действия выполняем** - команды CLI
- **Какой результат ожидаем** - проверки

### Пример минимального сценария

```yaml
name: Проверка версии
description: Убедиться что нода отвечает на команду version

network:
  topology: minimal
  nodes:
    - name: node1
      role: root

test:
  - cli: version
    expect: success
```

Этот сценарий:
1. Создаёт 1 ноду (`minimal` топология)
2. Выполняет команду `version`
3. Ожидает успешное выполнение

### Как запустить?

```bash
# Сохраните сценарий в scenarios/my_test.yml
./tests/stage-env/stage-env run-tests scenarios/my_test.yml
```

---

## Урок 1: Первый тест

Давайте создадим полноценный тест с нуля.

### Задача
Создать кошелёк и проверить, что он появился в списке.

### Решение

Создайте файл `scenarios/lesson1_wallet.yml`:

```yaml
# === МЕТАДАННЫЕ ===
name: Lesson 1 - Wallet Creation
description: Learn how to create a wallet and verify it exists
tags: [tutorial, lesson1, basic]

# === КОНФИГУРАЦИЯ СЕТИ ===
network:
  topology: minimal        # Используем 1 ноду
  nodes:
    - name: node1
      role: root
      validator: true

# === ТЕСТ ===
test:
  # Шаг 1: Создаём кошелёк
  - cli: wallet new -w my_first_wallet
    expect: success
    wait: 1s              # Подождём 1 секунду

  # Шаг 2: Проверяем что он создался
  - cli: wallet list
    contains: my_first_wallet
```

### Запуск

```bash
./tests/stage-env/stage-env run-tests scenarios/lesson1_wallet.yml
```

### Что происходит?

1. **stage-env** создаёт Docker контейнер с нодой
2. Нода запускается и переходит в состояние `ONLINE`
3. Выполняется команда `wallet new -w my_first_wallet`
4. Система ждёт 1 секунду
5. Выполняется команда `wallet list`
6. Проверяется что вывод содержит `my_first_wallet`

### ✅ Упражнение 1

Создайте тест который:
1. Создаёт кошелёк с именем `exercise1_wallet`
2. Создаёт второй кошелёк с именем `exercise1_wallet2`
3. Проверяет что оба кошелька в списке

<details>
<summary>Показать решение</summary>

```yaml
name: Exercise 1 - Two Wallets
description: Create two wallets

network:
  topology: minimal
  nodes:
    - name: node1
      role: root

test:
  - cli: wallet new -w exercise1_wallet
    wait: 1s
  
  - cli: wallet new -w exercise1_wallet2
    wait: 1s
  
  - cli: wallet list
    contains: exercise1_wallet
  
  - cli: wallet list
    contains: exercise1_wallet2
```
</details>

---

## Урок 2: Переменные и сохранение результатов

### Задача
Создать кошелёк, сохранить его адрес и использовать в следующей команде.

### Зачем нужны переменные?

Команды часто возвращают результаты (адреса, хэши), которые нужно использовать дальше:

```yaml
# ❌ Плохо: копируем адрес вручную
- cli: wallet new -w wallet1
  # Вывод: 0xABC123...
- cli: balance -addr 0xABC123...  # Нужно вручную скопировать

# ✅ Хорошо: сохраняем в переменную
- cli: wallet new -w wallet1
  save: wallet_addr              # Сохраняем вывод
- cli: balance -addr {{wallet_addr}}  # Используем переменную
```

### Решение

```yaml
name: Lesson 2 - Variables
description: Learn to save and use variables
tags: [tutorial, lesson2]

network:
  topology: minimal
  nodes:
    - name: node1
      role: root

test:
  # Шаг 1: Создаём кошелёк и сохраняем адрес
  - cli: wallet new -w lesson2_wallet
    save: my_wallet_address      # ← Сохраняем в переменную
    wait: 1s

  # Шаг 2: Проверяем адрес (используем переменную)
  - cli: wallet info -w lesson2_wallet
    contains: {{my_wallet_address}}  # ← Используем переменную
```

### Синтаксис переменных

- **Сохранить**: `save: имя_переменной`
- **Использовать**: `{{имя_переменной}}`

### Предопределённые переменные

Можно задать переменные заранее:

```yaml
variables:
  token_name: MYTOKEN
  initial_supply: 1000000

test:
  - cli: token_decl -token {{token_name}} -total_supply {{initial_supply}} -decimals 18 -signs_total 1 -signs_emission 1 -certs owner -net stagenet -chain zerochain
```

### ✅ Упражнение 2

Создайте тест который:
1. Создаёт кошелёк `sender`
2. Создаёт кошелёк `receiver`
3. Сохраняет адреса обоих кошельков
4. Выводит оба адреса с помощью команды `echo`

<details>
<summary>Показать решение</summary>

```yaml
name: Exercise 2 - Two Addresses
description: Save two wallet addresses

network:
  topology: minimal
  nodes:
    - name: node1
      role: root

test:
  - cli: wallet new -w sender
    save: sender_addr
    wait: 1s
  
  - cli: wallet new -w receiver
    save: receiver_addr
    wait: 1s
  
  - cli: echo "Sender: {{sender_addr}}"
  - cli: echo "Receiver: {{receiver_addr}}"
```
</details>

---

## Урок 3: Проверки результатов

### Задача
Научиться проверять корректность результатов.

### Виды проверок

#### 1. Проверка содержания (`contains`)

```yaml
- cli: wallet list
  contains: my_wallet  # Вывод должен содержать "my_wallet"
```

#### 2. Проверка отсутствия (`not_contains`)

```yaml
- cli: token info -token TEST
  not_contains: error  # Вывод НЕ должен содержать "error"
```

#### 3. Точное совпадение (`equals`)

```yaml
- cli: net status
  equals: connected  # Вывод должен точно равняться "connected"
```

### Секция `check`

Лучшая практика - выносить проверки в отдельную секцию:

```yaml
setup:
  - cli: подготовка...

test:
  - cli: выполнение действия...

check:
  - cli: проверка результата...
```

### Решение

```yaml
name: Lesson 3 - Checks
description: Learn different check types
tags: [tutorial, lesson3]

network:
  topology: minimal
  nodes:
    - name: node1
      role: root

# Подготовка
setup:
  - cli: wallet new -w check_wallet
    save: wallet_addr
    wait: 1s

# Тест
test:
  - cli: wallet info -w check_wallet
    expect: success

# Проверки
check:
  # Проверка 1: кошелёк в списке
  - cli: wallet list
    contains: check_wallet
  
  # Проверка 2: информация содержит адрес
  - cli: wallet info -w check_wallet
    contains: {{wallet_addr}}
  
  # Проверка 3: нет ошибок
  - cli: wallet info -w check_wallet
    not_contains: error
```

### ✅ Упражнение 3

Создайте тест который:
1. Создаёт токен `TEST` с supply 1000000
2. Проверяет что токен появился в списке (`token list`)
3. Проверяет что информация о токене не содержит слово "error"

<details>
<summary>Показать решение</summary>

```yaml
name: Exercise 3 - Token Checks
description: Create token and verify it

network:
  topology: minimal
  nodes:
    - name: node1
      role: root

setup:
  - cli: token_decl -token TEST -total_supply 1000000 -decimals 18 -signs_total 1 -signs_emission 1 -certs owner -net stagenet -chain zerochain
    save: token_hash
    wait: 3s

check:
  - cli: token list
    contains: TEST
  
  - cli: token info -token TEST
    not_contains: error
```
</details>

---

## Урок 4: Переиспользование шаблонов

### Задача
Научиться использовать готовые конфигурации.

### Зачем нужны шаблоны?

Вместо того чтобы каждый раз писать:

```yaml
network:
  topology: minimal
  nodes:
    - name: node1
      role: root
      validator: true
```

Можно просто написать:

```yaml
includes:
  - common/network_minimal.yml
```

### Готовые шаблоны

#### `common/network_minimal.yml`
- 1 нода
- Роль: root validator

#### `common/network_full.yml`
- 7 нод (3 validators + 4 full nodes)
- Полная топология для комплексных тестов

#### `common/wallet_setup.yml`
- Создаёт кошелёк `test_wallet`
- Экспортирует переменную `{{wallet_addr}}`

### Решение

```yaml
name: Lesson 4 - Templates
description: Learn to use includes
tags: [tutorial, lesson4]

# === ПЕРЕИСПОЛЬЗУЕМ ГОТОВЫЕ ШАБЛОНЫ ===
includes:
  - common/network_minimal.yml     # Минимальная сеть
  - common/wallet_setup.yml         # Готовый кошелёк

# Теперь у нас есть:
# - node1 (из network_minimal.yml)
# - test_wallet (из wallet_setup.yml)
# - {{wallet_addr}} (из wallet_setup.yml)

test:
  # Используем готовый кошелёк
  - cli: wallet info -w test_wallet
    contains: {{wallet_addr}}
  
  - cli: wallet list
    contains: test_wallet
```

### Комбинирование шаблонов

```yaml
includes:
  - common/network_full.yml   # 7 нод
  - common/wallet_setup.yml   # Кошелёк

test:
  # Теперь можем использовать несколько нод
  - cli: wallet list
    node: node-1
  
  - cli: wallet list
    node: node-2
```

### ✅ Упражнение 4

Создайте тест который:
1. Использует `common/network_minimal.yml`
2. Использует `common/wallet_setup.yml`
3. Создаёт токен `EXERCISE4`
4. Проверяет что и кошелёк, и токен существуют

<details>
<summary>Показать решение</summary>

```yaml
name: Exercise 4 - Combined Templates
description: Use multiple templates

includes:
  - common/network_minimal.yml
  - common/wallet_setup.yml

setup:
  - cli: token_decl -token EXERCISE4 -total_supply 1000000 -decimals 18 -signs_total 1 -signs_emission 1 -certs owner -net stagenet -chain zerochain
    wait: 3s

check:
  - cli: wallet list
    contains: test_wallet
  
  - cli: token list
    contains: EXERCISE4
```
</details>

---

## Урок 5: Работа с токенами

### Задача
Создать токен, эмитировать его, и проверить баланс.

### Жизненный цикл токена

1. **Декларация** - создание токена
2. **Эмиссия** - выпуск токенов на адрес
3. **Трансфер** - передача между кошельками

### Решение

```yaml
name: Lesson 5 - Tokens
description: Learn token operations
tags: [tutorial, lesson5, tokens]

includes:
  - common/network_minimal.yml
  - common/wallet_setup.yml

setup:
  # Шаг 1: Создаём второй кошелёк
  - cli: wallet new -w receiver_wallet
    save: receiver_addr
    wait: 1s

test:
  # Шаг 2: Декларируем токен
  - cli: token_decl -token LESSON5 -total_supply 1000000 -decimals 18 -signs_total 1 -signs_emission 1 -certs owner -net stagenet -chain zerochain
    save: token_hash
    wait: 3s
  
  # Шаг 3: Эмитируем токены на первый кошелёк
  - cli: token_emit -token LESSON5 -emission_value 100000 -addr {{wallet_addr}} -net stagenet -certs owner
    save: emission_tx
    wait: 3s
  
  # Шаг 4: Переводим часть токенов на второй кошелёк
  - cli: transfer -token LESSON5 -to {{receiver_addr}} -value 50000
    expect: success
    wait: 3s

check:
  # Проверяем балансы
  - cli: balance -addr {{wallet_addr}} -token LESSON5
    contains: "50000"
  
  - cli: balance -addr {{receiver_addr}} -token LESSON5
    contains: "50000"
```

### Важные детали

#### Wait после изменений

```yaml
- cli: token_emit -token TEST -emission_value 1000 -addr {{addr}} -net stagenet -certs owner
  wait: 3s  # ← ОБЯЗАТЕЛЬНО! Даём время на обработку
```

Без `wait` следующая команда может не увидеть изменения.

#### Сохранение хэшей

```yaml
- cli: token_decl -token TEST -total_supply 1000000 -decimals 18 -signs_total 1 -signs_emission 1 -certs owner -net stagenet -chain zerochain
  save: token_hash  # Сохраняем хэш для использования
```

### ✅ Упражнение 5

Создайте тест который:
1. Создаёт 3 кошелька
2. Создаёт токен `EX5TOKEN`
3. Эмитирует 90000 токенов на первый кошелёк
4. Переводит по 30000 на второй и третий кошельки
5. Проверяет что балансы корректны (30000 на каждом)

<details>
<summary>Показать решение</summary>

```yaml
name: Exercise 5 - Token Distribution
description: Distribute tokens across 3 wallets

includes:
  - common/network_minimal.yml

setup:
  - cli: wallet new -w wallet1
    save: addr1
    wait: 1s
  - cli: wallet new -w wallet2
    save: addr2
    wait: 1s
  - cli: wallet new -w wallet3
    save: addr3
    wait: 1s
  
  - cli: token_decl -token EX5TOKEN -total_supply 1000000 -decimals 18 -signs_total 1 -signs_emission 1 -certs owner -net stagenet -chain zerochain
    wait: 3s
  
  - cli: token_emit -token EX5TOKEN -emission_value 90000 -addr {{addr1}} -net stagenet -certs owner
    wait: 3s

test:
  - cli: transfer -token EX5TOKEN -to {{addr2}} -value 30000
    wait: 3s
  - cli: transfer -token EX5TOKEN -to {{addr3}} -value 30000
    wait: 3s

check:
  - cli: balance -addr {{addr1}} -token EX5TOKEN
    contains: "30000"
  - cli: balance -addr {{addr2}} -token EX5TOKEN
    contains: "30000"
  - cli: balance -addr {{addr3}} -token EX5TOKEN
    contains: "30000"
```
</details>

---

## Урок 6: Циклы и повторения

### Задача
Создать 10 кошельков без дублирования кода.

### Цикл `loop`

```yaml
- loop: 10           # Повторить 10 раз
  steps:
    - cli: wallet new -w wallet{{i}}  # {{i}} = 0,1,2...9
```

### Доступные переменные

- `{{i}}` - индекс (0-based): 0, 1, 2, ...
- `{{iteration}}` - номер (1-based): 1, 2, 3, ...

### Решение

```yaml
name: Lesson 6 - Loops
description: Learn to use loops
tags: [tutorial, lesson6]

includes:
  - common/network_minimal.yml

test:
  # Создать 10 кошельков
  - loop: 10
    steps:
      - cli: wallet new -w wallet{{iteration}}
        save: addr{{iteration}}
        wait: 500ms

check:
  # Проверить что все созданы
  - cli: wallet list
    contains: wallet1
  - cli: wallet list
    contains: wallet10
```

### Сложные циклы

```yaml
# Создать 100 транзакций
- loop: 100
  steps:
    - cli: transfer -to {{recipient}} -value {{i + 1}}
      wait: 100ms

# Массовая эмиссия
- loop: 5
  steps:
    - cli: token_emit -token TEST -value {{i * 1000}} -addr {{addr{{i}}}}
      wait: 2s
```

### ✅ Упражнение 6

Создайте тест который:
1. Создаёт 5 кошельков (wallet1, wallet2, ..., wallet5)
2. Создаёт токен LOOP_TOKEN
3. Эмитирует 50000 токенов на wallet1
4. В цикле переводит по 10000 токенов на остальные 4 кошелька
5. Проверяет балансы

<details>
<summary>Показать решение</summary>

```yaml
name: Exercise 6 - Loop Distribution
description: Use loops to distribute tokens

includes:
  - common/network_minimal.yml

setup:
  - loop: 5
    steps:
      - cli: wallet new -w wallet{{iteration}}
        save: addr{{iteration}}
        wait: 500ms
  
  - cli: token_decl -token LOOP_TOKEN -total_supply 1000000 -decimals 18 -signs_total 1 -signs_emission 1 -certs owner -net stagenet -chain zerochain
    wait: 3s
  
  - cli: token_emit -token LOOP_TOKEN -emission_value 50000 -addr {{addr1}} -net stagenet -certs owner
    wait: 3s

test:
  - loop: 4
    steps:
      - cli: transfer -token LOOP_TOKEN -to {{addr{{i+2}}}} -value 10000
        wait: 2s

check:
  - cli: balance -addr {{addr1}} -token LOOP_TOKEN
    contains: "10000"
  - loop: 4
    steps:
      - cli: balance -addr {{addr{{i+2}}}} -token LOOP_TOKEN
        contains: "10000"
```
</details>

---

## Урок 7: Сложные сценарии

### Задача
Комбинировать все изученные техники в реальном тесте.

### Сценарий: Stress Test

Создадим стресс-тест системы токенов.

```yaml
name: Lesson 7 - Complex Scenario
description: Stress test for token system
tags: [tutorial, lesson7, stress]

includes:
  - common/network_full.yml  # Используем полную сеть

variables:
  token_name: STRESS_TOKEN
  total_supply: 10000000
  wallets_count: 20
  transfers_count: 100

setup:
  # Создать множество кошельков
  - loop: {{wallets_count}}
    steps:
      - cli: wallet new -w stress_wallet{{iteration}}
        node: node-{{(i % 3) + 1}}  # Распределяем по нодам
        save: stress_addr{{iteration}}
        wait: 200ms
  
  # Создать токен
  - cli: token_decl -token {{token_name}} -total_supply {{total_supply}} -decimals 18 -signs_total 1 -signs_emission 1 -certs owner -net stagenet -chain zerochain
    node: node-1
    save: token_hash
    wait: 3s
  
  # Эмитировать на первый кошелёк
  - cli: token_emit -token {{token_name}} -emission_value {{total_supply}} -addr {{stress_addr1}} -net stagenet -certs owner
    node: node-1
    wait: 3s

test:
  # Массовая рассылка токенов
  - loop: {{transfers_count}}
    steps:
      - cli: transfer -token {{token_name}} -to {{stress_addr{{(i % wallets_count) + 1}}}} -value {{i + 1}}
        node: node-{{(i % 3) + 1}}
        timeout: 60
        wait: 100ms

check:
  # Проверить что транзакции прошли
  - cli: tx_history -limit {{transfers_count}}
    node: node-1
    contains: {{token_name}}
  
  # Проверить несколько случайных балансов
  - cli: balance -addr {{stress_addr5}} -token {{token_name}}
    node: node-2
  
  - cli: balance -addr {{stress_addr10}} -token {{token_name}}
    node: node-3
```

### Техники из примера

1. **Переменные** - централизованная конфигурация
2. **Циклы** - массовые операции
3. **Несколько нод** - распределение нагрузки
4. **Математика** - вычисления в шаблонах (`{{(i % 3) + 1}}`)
5. **Таймауты** - защита от зависания

### ✅ Итоговое упражнение

Создайте полноценный тест который:
1. Использует полную сеть (7 нод)
2. Создаёт 10 кошельков
3. Создаёт 3 разных токена
4. Распределяет каждый токен на 3 кошелька
5. Делает по 5 трансферов каждого токена между кошельками
6. Проверяет итоговые балансы

---

## Урок 8: Лучшие практики

### 1. Структура теста

```yaml
# ✅ Хорошая структура
name: Clear and descriptive name
description: Detailed description of what we test
tags: [feature, priority, duration]

includes:
  - common/network_minimal.yml

variables:
  key: value

setup:
  - cli: preparation

test:
  - cli: action

check:
  - cli: verification
```

### 2. Именование

```yaml
# ❌ Плохо
name: test1
- cli: wallet new -w w1
  save: a1

# ✅ Хорошо
name: Token Transfer Between Wallets Test
- cli: wallet new -w sender_wallet
  save: sender_address
```

### 3. Комментарии

```yaml
test:
  # === PHASE 1: Token Creation ===
  - cli: token_decl -token TEST -total_supply 1000000 -decimals 18 -signs_total 1 -signs_emission 1 -certs owner -net stagenet -chain zerochain
    save: token_hash
    wait: 3s
  
  # === PHASE 2: Distribution ===
  - loop: 10
    steps:
      - cli: token_emit ...  # Emit to each wallet
```

### 4. Wait Times

```yaml
# ❌ Слишком долго
- cli: token_emit
  wait: 30s  # Слишком много

# ❌ Слишком быстро
- cli: token_emit
  # wait отсутствует - может не успеть

# ✅ Оптимально
- cli: token_emit
  wait: 3s  # Достаточно для обработки
```

### 5. Проверки

```yaml
# ❌ Нет проверок
test:
  - cli: transfer -value 1000

# ✅ С проверками
test:
  - cli: transfer -value 1000
    expect: success
    wait: 3s

check:
  - cli: balance
    contains: "1000"
```

### 6. Обработка ошибок

```yaml
# Тест ожидаемой ошибки
test:
  - cli: transfer -value 999999999  # Недостаточно средств
    expect: error
    contains: insufficient funds
```

### 7. Переиспользование

```yaml
# ❌ Дублирование
- cli: wallet new -w w1
- cli: wallet new -w w2
- cli: wallet new -w w3

# ✅ Цикл
- loop: 3
  steps:
    - cli: wallet new -w w{{iteration}}
```

### 8. Документирование

```yaml
name: Clear Test Name
description: |
  This test verifies that:
  1. Tokens can be created
  2. Tokens can be emitted
  3. Tokens can be transferred
  4. Balances are updated correctly
  
  Prerequisites:
  - Network must be online
  - At least 2 nodes required
  
  Expected duration: ~30 seconds
tags: [tokens, transfer, critical, fast]
author: QA Team
version: "2.0"
```

---

## 🎓 Поздравляем!

Вы прошли весь туториал! Теперь вы умеете:

- ✅ Писать базовые тесты
- ✅ Использовать переменные
- ✅ Проверять результаты
- ✅ Переиспользовать шаблоны
- ✅ Работать с токенами
- ✅ Использовать циклы
- ✅ Создавать сложные сценарии
- ✅ Следовать best practices

### Что дальше?

1. **[Cookbook](Cookbook.md)** - Готовые рецепты для типовых задач
2. **[Glossary](Glossary.md)** - Полный справочник языка
3. **Практика** - Создавайте свои тесты в `scenarios/features/`

### Полезные ссылки

- `scenarios/common/` - Готовые шаблоны
- `scenarios/features/` - Примеры реальных тестов
- `./stage-env --help` - Справка по CLI

Удачи в тестировании! 🚀



---

**Язык:** Русский | [English](../../en/scenarios/Tutorial.md)
