# Troubleshooting Guide

Руководство по решению проблем при работе с тестовыми сценариями.

## Содержание

- [Проблемы запуска](#проблемы-запуска)
- [Ошибки сценариев](#ошибки-сценариев)
- [Проблемы с сетью](#проблемы-с-сетью)
- [Проблемы производительности](#проблемы-производительности)
- [Отладка](#отладка)

---

## Проблемы запуска

### Ошибка: `scenario file not found`

**Причина:** Неправильный путь к файлу сценария.

**Решение:**
```bash
# Убедитесь что путь относительный к tests/scenarios/
./tests/stage-env/stage-env run-tests tests/scenarios/features/my_test.yml

# Или абсолютный путь
./tests/stage-env/stage-env run-tests /full/path/to/my_test.yml
```

### Ошибка: `python3 not found`

**Причина:** Python не установлен.

**Решение:**
```bash
# Ubuntu/Debian
sudo apt install python3 python3-venv python3-pip

# Fedora/RHEL
sudo dnf install python3

# Проверить установку
python3 --version
```

### Ошибка: `docker not found`

**Причина:** Docker не установлен или не запущен.

**Решение:**
```bash
# Установить Docker
sudo apt install docker.io  # Ubuntu/Debian

# Запустить Docker
sudo systemctl start docker
sudo systemctl enable docker

# Добавить пользователя в группу docker
sudo usermod -aG docker $USER
newgrp docker

# Проверить
docker ps
```

### Ошибка: `venv creation failed`

**Причина:** Проблемы с созданием виртуального окружения.

**Решение:**
```bash
# Удалить старый venv
rm -rf tests/stage-env/.venv

# Пересоздать
./tests/stage-env/stage-env --help  # Автоматически создаст venv

# Или вручную
cd tests/stage-env
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## Ошибки сценариев

### Ошибка: `Invalid YAML syntax`

**Причина:** Синтаксическая ошибка в YAML файле.

**Решение:**
```yaml
# Проверьте отступы (только пробелы, не табы)
name: My Test
description: Test description  # ✓ Правильно
  tags: [test]                 # ✗ Неправильный отступ

# Проверьте кавычки
- cli: wallet new -w "my wallet"  # ✓ С пробелами нужны кавычки
- cli: wallet new -w my_wallet    # ✓ Без пробелов кавычки не нужны

# Проверьте двоеточия
name:My Test   # ✗ Нужен пробел после :
name: My Test  # ✓ Правильно
```

**Валидация:**
```bash
# Проверить синтаксис
./tests/stage-env/stage-env validate tests/scenarios/features/my_test.yml
```

### Ошибка: `Undefined variable: variable_name`

**Причина:** Переменная используется но не определена.

**Решение:**
```yaml
# Вариант 1: Определить в variables
variables:
  wallet_addr: "0x1234..."

# Вариант 2: Сохранить из команды
setup:
  - cli: wallet new -w test
    save: wallet_addr  # Теперь можно использовать {{wallet_addr}}

# Вариант 3: Проверить опечатки
test:
  - cli: transfer -to {{wallet_addr}}  # ✓ Правильно
  - cli: transfer -to {{walet_addr}}   # ✗ Опечатка
```

### Ошибка: `Reference to undefined node: node2`

**Причина:** Обращение к ноде которая не определена в network.

**Решение:**
```yaml
network:
  nodes:
    - name: node1
      role: root
    - name: node2      # Добавить ноду
      role: master

test:
  - cli: wallet list
    node: node2        # Теперь node2 определена
```

### Ошибка: `Schema validation failed`

**Причина:** Данные не соответствуют схеме.

**Решение:**
```yaml
# Проверьте обязательные поля
name: Test Name          # ✓ Обязательно
description: Test desc   # ✓ Обязательно
network:                 # ✓ Обязательно
  topology: minimal
test:                    # ✓ Обязательно хотя бы один шаг
  - cli: version

# Проверьте типы данных
- cli: wallet new
  timeout: 30           # ✓ Число
  timeout: "30"         # ✗ Строка (будет ошибка)

# Проверьте допустимые значения
- cli: test
  expect: success       # ✓ Допустимо
  expect: ok            # ✗ Недопустимо (только success/error/any)
```

---

## Проблемы с сетью

### Ошибка: `docker compose config failed`

**Причина:** Проблемы с docker-compose.yml.

**Решение:**
```bash
# Проверить конфигурацию
cd tests/stage-env
docker compose config

# Пересоздать сеть
./stage-env stop --volumes
./stage-env start --clean
```

### Ошибка: `Port already in use`

**Причина:** Порты заняты другим процессом.

**Решение:**
```bash
# Найти процесс на порту
sudo lsof -i :8080
sudo lsof -i :8545

# Убить процесс
sudo kill -9 <PID>

# Или использовать другую топологию
# (топологии могут использовать разные порты)
```

### Ошибка: `No running services found`

**Причина:** Контейнеры не запущены.

**Решение:**
```bash
# Запустить сеть
./tests/stage-env/stage-env start --wait

# Проверить статус
./tests/stage-env/stage-env status

# Посмотреть логи
docker compose -f tests/stage-env/docker-compose.yml logs
```

### Ошибка: `Connection refused`

**Причина:** Нода не отвечает или ещё не готова.

**Решение:**
```yaml
# Добавить wait после start
setup:
  - wait: 10s  # Дать время на запуск

# Увеличить timeout
test:
  - cli: version
    timeout: 60  # Увеличить до 60 секунд
```

---

## Проблемы производительности

### Тест выполняется очень медленно

**Причина:** Неоптимальные wait времена или топология.

**Решение:**
```yaml
# Уменьшить wait времена
- cli: token_emit
  wait: 3s    # Вместо 10s

# Использовать минимальную топологию для быстрых тестов
includes:
  - common/network_minimal.yml  # 1 нода вместо 4

# Убрать ненужные loop итерации
- loop: 10   # Вместо 1000
  steps:
    - cli: test_command
```

### Таймауты команд

**Причина:** Операция занимает больше времени чем timeout.

**Решение:**
```yaml
# Увеличить timeout для долгих операций
- cli: token_emit -value 1000000000
  timeout: 120  # 2 минуты вместо 30 секунд

# Или разбить на части
- loop: 10
  steps:
    - cli: token_emit -value 100000000
      timeout: 60
```

### Ошибка: `out of memory`

**Причина:** Недостаточно памяти для Docker.

**Решение:**
```bash
# Увеличить память для Docker
# Docker Desktop -> Settings -> Resources -> Memory: 4GB+

# Или уменьшить нагрузку
# Использовать меньше нод
# Уменьшить количество итераций в loop
```

---

## Отладка

### Включить verbose логи

```bash
# Verbose режим
./tests/stage-env/stage-env --verbose run-tests tests/scenarios/features/my_test.yml

# JSON вывод для анализа
./tests/stage-env/stage-env --json run-tests tests/scenarios/features/my_test.yml
```

### Посмотреть логи нод

```bash
# Логи конкретной ноды
./tests/stage-env/stage-env logs node1

# Следить за логами в реальном времени
./tests/stage-env/stage-env logs node1 --follow

# Последние 100 строк
./tests/stage-env/stage-env logs node1 --tail 100
```

### Зайти в контейнер

```bash
# Интерактивная сессия
./tests/stage-env/stage-env exec node1 bash

# Выполнить команду
./tests/stage-env/stage-env exec node1 cellframe-node-cli version
```

### Проверить состояние системы

```bash
# Статус сети
./tests/stage-env/stage-env status

# Docker контейнеры
docker ps

# Docker сети
docker network ls

# Использование ресурсов
docker stats
```

### Сохранить артефакты для анализа

```bash
# Сохранить логи
./tests/stage-env/stage-env logs node1 > node1_logs.txt

# Сохранить состояние
./tests/stage-env/stage-env exec node1 cellframe-node-cli wallet list > wallets.txt
./tests/stage-env/stage-env exec node1 cellframe-node-cli token list > tokens.txt
```

### Пошаговое выполнение

```yaml
# Добавить паузы между шагами
test:
  - cli: step1
  - wait: 30s  # Пауза для ручной проверки
  - cli: step2
  - wait: 30s
  - cli: step3
```

### Изолировать проблему

```yaml
# Минимальный воспроизводимый тест
name: Debug Test
description: Isolated problem reproduction

network:
  topology: minimal
  nodes:
    - name: node1
      role: root

test:
  # Только проблемный шаг
  - cli: проблемная_команда
```

---

## Частые проблемы и решения

### "Transaction failed: insufficient funds"

```yaml
# Проверьте баланс перед трансфером
setup:
  - cli: token_emit -value 10000 -addr {{addr}}
    wait: 3s

check:
  - cli: balance -addr {{addr}}
    contains: "10000"
```

### "UTXO is blocked"

```yaml
# Это ожидаемое поведение при использовании UTXO blocking
# Используйте -arbitrage для bypass:
- cli: tx_create -value 100 -arbitrage
  expect: success
```

### "Certificate not found"

```bash
# Сгенерировать сертификаты
./tests/stage-env/stage-env certs --network stagenet --nodes 4

# Или пересоздать сеть
./tests/stage-env/stage-env stop
./tests/stage-env/stage-env clean
./tests/stage-env/stage-env build
./tests/stage-env/stage-env start
```

### "Node not synchronized"

```yaml
# Добавить wait для синхронизации
setup:
  - wait: 10s  # Дать время на синхронизацию

# Или проверить статус
- cli: net sync
  contains: "synchronized"
```

---

## Получение помощи

### Проверить документацию

1. [Getting Started](GETTING_STARTED.md) - быстрый старт
2. [Reference](REFERENCE.md) - полная справка
3. [Cookbook](COOKBOOK.md) - примеры решений
4. [README](README.md) - обзор системы

### Валидировать сценарий

```bash
# Перед запуском
./tests/stage-env/stage-env validate tests/scenarios/features/my_test.yml
```

### Проверить примеры

```bash
# Посмотреть рабочие примеры
ls tests/scenarios/features/
cat tests/scenarios/features/arbitrage_bypass_test.yml
```

### Собрать диагностическую информацию

```bash
# Версии
python3 --version
docker --version
docker compose version

# Статус системы
./tests/stage-env/stage-env status

# Логи всех нод
for node in node1 node2 node3 node4; do
  echo "=== $node ==="
  ./tests/stage-env/stage-env logs $node --tail 50
done > all_logs.txt
```

### Очистка и перезапуск

```bash
# Полная очистка
./tests/stage-env/stage-env stop --volumes
./tests/stage-env/stage-env clean --all

# Пересборка
./tests/stage-env/stage-env build --clean

# Свежий старт
./tests/stage-env/stage-env start --clean --wait
```

---

## Советы по предотвращению проблем

1. **Всегда валидируйте перед запуском**
   ```bash
   ./tests/stage-env/stage-env validate my_test.yml
   ```

2. **Используйте достаточные wait времена**
   ```yaml
   - cli: token_emit
     wait: 3s  # Не менее 3s для state changes
   ```

3. **Проверяйте результаты команд**
   ```yaml
   - cli: important_command
     expect: success
     contains: "expected_output"
   ```

4. **Переиспользуйте проверенные шаблоны**
   ```yaml
   includes:
     - common/network_minimal.yml
     - common/wallet_setup.yml
   ```

5. **Добавляйте осмысленные теги**
   ```yaml
   tags: [feature, priority, duration]
   ```

6. **Пишите понятные описания**
   ```yaml
   description: What this test does and why
   ```

---

Если проблема не решена, создайте issue с:
- Полным текстом сценария
- Выводом команды с --verbose
- Логами нод
- Версиями софта (python, docker)

