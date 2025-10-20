# Getting Started with Test Scenarios

Добро пожаловать в систему тестирования Cellframe Node! Это руководство поможет QA инженерам быстро начать писать тесты.

## Что такое Test Scenarios?

Test Scenarios - это YAML файлы, описывающие что нужно протестировать. Вам не нужно знать программирование - достаточно описать последовательность действий и ожидаемые результаты.

### Пример простого теста

```yaml
name: Проверка создания кошелька
description: Убедиться что кошелёк создаётся успешно

network:
  topology: minimal
  nodes:
    - name: node1
      role: root

test:
  - cli: wallet new -w my_wallet
    save: wallet_addr
  
  - cli: wallet list
    contains: my_wallet

check:
  - cli: wallet info -w my_wallet
    contains: {{wallet_addr}}
```

Этот тест:
1. Создаёт кошелёк `my_wallet`
2. Сохраняет адрес в переменную `wallet_addr`
3. Проверяет что кошелёк появился в списке
4. Проверяет информацию о кошельке

## Установка и запуск

### Шаг 1: Подготовка окружения

```bash
cd /path/to/cellframe-node

# Убедитесь что stage-env готов
./tests/stage-env/stage-env --help
```

### Шаг 2: Создание теста

Создайте файл `tests/scenarios/features/my_test.yml`:

```yaml
name: Мой первый тест
description: Описание что тестируем
tags: [basic]

includes:
  - common/network_minimal.yml  # Переиспользуем готовую сеть

test:
  - cli: version
    expect: success
```

### Шаг 3: Запуск теста

```bash
# Запустить все тесты
./tests/run.sh --e2e

# Запустить конкретный тест
./tests/stage-env/stage-env run-tests tests/scenarios/features/my_test.yml
```

## Основные концепции

### 1. Структура теста

Каждый тест состоит из секций:

```yaml
# Метаданные (обязательно)
name: Название теста
description: Что тестируем
tags: [категория, приоритет]

# Переиспользуемые конфиги (опционально)
includes:
  - common/network_minimal.yml

# Подготовка (опционально)
setup:
  - cli: подготовительная команда

# Основной тест (обязательно)
test:
  - cli: тестируемая команда

# Проверки (рекомендуется)
check:
  - cli: проверочная команда
```

### 2. CLI команды

Выполняют команды cellframe-node-cli:

```yaml
- cli: wallet new -w test_wallet
  save: wallet_addr     # Сохранить результат в переменную
  wait: 3s              # Подождать 3 секунды
  expect: success       # Ожидаем успех
  contains: "Created"   # Проверить что вывод содержит текст
```

### 3. Переменные

Используйте `{{имя_переменной}}` для подстановки значений:

```yaml
setup:
  - cli: wallet new -w wallet1
    save: addr1  # Сохраняем адрес

test:
  - cli: transfer -to {{addr1}} -value 100  # Используем адрес
```

### 4. Проверки

Убедитесь что результат соответствует ожиданиям:

```yaml
check:
  # Проверить что вывод содержит текст
  - cli: wallet list
    contains: my_wallet
  
  # Проверить что текста НЕТ в выводе
  - cli: token info -token TEST
    not_contains: error
  
  # Точное совпадение
  - cli: net status
    equals: connected
```

### 5. Переиспользование (includes)

Не повторяйте себя - используйте готовые шаблоны:

```yaml
includes:
  - common/network_minimal.yml  # Одна нода
  - common/network_full.yml     # 4 ноды
  - common/wallet_setup.yml     # Готовый кошелёк
```

## Типовые задачи

### Создать кошелёк

```yaml
- cli: wallet new -w my_wallet
  save: wallet_addr
  wait: 1s
```

### Создать токен

```yaml
- cli: token_decl -net stagenet -token TEST -total 1000000
  save: token_hash
  wait: 3s
```

### Эмитировать токены

```yaml
- cli: token_emit -token TEST -value 10000 -addr {{wallet_addr}}
  save: emission_tx
  wait: 3s
```

### Создать транзакцию

```yaml
- cli: tx_create -token TEST -value 100 -to {{recipient_addr}}
  save: tx_hash
  expect: success
  wait: 3s
```

### Проверить баланс

```yaml
check:
  - cli: balance -addr {{wallet_addr}} -token TEST
    contains: "10000"
```

### Подождать

```yaml
- wait: 5s    # 5 секунд
- wait: 100ms # 100 миллисекунд
- wait: 2m    # 2 минуты
```

### Повторить действие

```yaml
- loop: 10
  steps:
    - cli: tx_create -value {{i * 100}}
    - wait: 1s
```

## Готовые шаблоны

### Минимальная сеть

```yaml
includes:
  - common/network_minimal.yml
```

Даёт вам:
- `node1` - корневая нода с ролью validator

### Полная сеть

```yaml
includes:
  - common/network_full.yml
```

Даёт вам:
- `node1` - root validator
- `node2` - master validator
- `node3` - master validator
- `node4` - full node

### Готовый кошелёк

```yaml
includes:
  - common/wallet_setup.yml
```

Даёт вам:
- `test_wallet` - созданный кошелёк
- `{{wallet_addr}}` - адрес кошелька

## Примеры тестов

### Пример 1: Простой тест версии

```yaml
name: Version Check
description: Verify node version command works

includes:
  - common/network_minimal.yml

test:
  - cli: version
    expect: success
    contains: "Cellframe"
```

### Пример 2: Тест создания токена

```yaml
name: Token Creation Test
description: Create token and verify it exists

includes:
  - common/network_minimal.yml

setup:
  - cli: wallet new -w creator
    save: creator_addr

test:
  - cli: token_decl -token MYTOKEN -total 1000000
    save: token_hash
    wait: 3s

check:
  - cli: token list
    contains: MYTOKEN
  
  - cli: token info -token MYTOKEN
    contains: {{token_hash}}
```

### Пример 3: Тест трансфера

```yaml
name: Token Transfer Test
description: Transfer tokens between wallets

includes:
  - common/network_minimal.yml

setup:
  - cli: wallet new -w wallet1
    save: addr1
  - cli: wallet new -w wallet2
    save: addr2
  - cli: token_decl -token TRF -total 1000000
    save: token
    wait: 3s
  - cli: token_emit -token TRF -value 10000 -addr {{addr1}}
    wait: 3s

test:
  - cli: transfer -token TRF -to {{addr2}} -value 5000
    expect: success
    wait: 3s

check:
  - cli: balance -addr {{addr1}} -token TRF
    contains: "5000"
  
  - cli: balance -addr {{addr2}} -token TRF
    contains: "5000"
```

## Советы и рекомендации

### ✅ DO (Делайте так)

1. **Используйте понятные имена**
   ```yaml
   name: Token Transfer Between Wallets
   ```

2. **Добавляйте wait после изменений**
   ```yaml
   - cli: token_emit -value 1000
     wait: 3s  # Даём время на обработку
   ```

3. **Проверяйте результаты**
   ```yaml
   check:
     - cli: verification_command
   ```

4. **Используйте переменные**
   ```yaml
   - cli: wallet new -w test
     save: addr
   - cli: transfer -to {{addr}}
   ```

5. **Переиспользуйте шаблоны**
   ```yaml
   includes:
     - common/network_minimal.yml
   ```

### ❌ DON'T (Не делайте так)

1. **Не копируйте код**
   ```yaml
   # Плохо: дублирование
   - cli: wallet new -w wallet1
   - cli: wallet new -w wallet2
   
   # Хорошо: цикл
   - loop: 2
     steps:
       - cli: wallet new -w wallet{{i}}
   ```

2. **Не забывайте wait**
   ```yaml
   # Плохо: сразу после эмиссии
   - cli: token_emit -value 1000
   - cli: balance  # Может быть ещё не готов
   
   # Хорошо: с паузой
   - cli: token_emit -value 1000
     wait: 3s
   - cli: balance
   ```

3. **Не игнорируйте ошибки**
   ```yaml
   # Плохо: нет проверки
   - cli: transfer -value 1000
   
   # Хорошо: проверяем результат
   - cli: transfer -value 1000
     expect: success
   ```

## Что дальше?

1. **Изучите примеры**: `tests/scenarios/features/`
2. **Попробуйте шаблоны**: `tests/scenarios/common/`
3. **Читайте справку**: `tests/scenarios/README.md`
4. **Смотрите рецепты**: `tests/scenarios/COOKBOOK.md`

## Помощь

### Проверить синтаксис

```bash
# Валидация без запуска
./tests/stage-env/stage-env validate tests/scenarios/features/my_test.yml
```

### Запустить с отладкой

```bash
# Verbose режим
./tests/stage-env/stage-env --verbose run-tests tests/scenarios/features/my_test.yml
```

### Часто задаваемые вопросы

**Q: Как узнать доступные CLI команды?**
```bash
docker exec node1 cellframe-node-cli help
```

**Q: Как проверить что тест работает?**
```bash
./tests/stage-env/stage-env run-tests tests/scenarios/features/my_test.yml
```

**Q: Где смотреть логи при ошибках?**
```bash
./tests/stage-env/stage-env logs node1
```

**Q: Как быстро перезапустить тест?**
```bash
# С очисткой окружения
./tests/run.sh --e2e --clean
```

## Готовы начать!

Создайте свой первый тест в `tests/scenarios/features/` и запустите его!

Удачи! 🚀

