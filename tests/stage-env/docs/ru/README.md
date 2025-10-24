# Stage Environment - Cellframe Node Testing Infrastructure

**Автономная система для E2E тестирования блокчейн приложений**

Stage Environment - это полнофункциональная инфраструктура для запуска и тестирования Cellframe Node в изолированной Docker среде. Система полностью автономна, легко портируется и не требует глубоких знаний программирования для написания тестов.

## 🎯 Возможности

- ✅ **YAML-сценарии** - пишите тесты на декларативном языке без программирования
- ✅ **Автоматизация** - сборка, запуск, тестирование, сбор артефактов
- ✅ **Docker-изоляция** - каждый тест в чистом окружении
- ✅ **Гибкие топологии** - от 1 ноды до сложных сетей
- ✅ **Artifacts & Reports** - автоматический сбор логов, core dumps, генерация PDF отчетов
- ✅ **Rich CLI** - красивый интерфейс с цветным выводом и progress bars

## 🚀 Быстрый старт

### Минимальный пример

```bash
# 1. Запуск тестовой сети (автоматически установит зависимости)
cd tests
./stage-env/stage-env start

# 2. Проверка статуса
./stage-env/stage-env status

# 3. Запуск тестов
./stage-env/stage-env run-tests scenarios/

# 4. Остановка
./stage-env/stage-env stop
```

### Запуск через run.sh

```bash
# Полный цикл: сборка + тесты + отчеты
cd tests
./run.sh --e2e

# Результаты в testing/artifacts/e2e_*/reports/
```

## 📖 Документация

### Для QA инженеров

- **[Tutorial](scenarios/Tutorial.md)** - Пошаговое обучение языку сценариев (8 уроков)
- **[Cookbook](scenarios/Cookbook.md)** - Готовые рецепты для типовых задач (50 рецептов)
- **[Glossary](scenarios/Glossary.md)** - Полный справочник языка (все команды и параметры)

## 📁 Структура проекта

```
stage-env/
├── stage-env                # Bash wrapper (точка входа)
├── stage_env.py             # Python CLI (Typer)
├── stage-env.cfg            # Конфигурация (в tests/)
│
├── src/                     # Python модули
│   ├── config/              # Управление конфигурацией
│   ├── docker/              # Docker Compose интеграция
│   ├── network/             # Топологии и сеть
│   ├── build/               # Сборка артефактов
│   ├── certs/               # Генерация сертификатов
│   ├── scenarios/           # Парсинг и выполнение сценариев
│   └── utils/               # Логирование, отчеты, артефакты
│
├── config/                  # Конфигурационные файлы
│   ├── topologies/          # Шаблоны сетевых топологий
│   └── templates/           # Jinja2 шаблоны конфигов
│       ├── base/            # Базовые конфиги нод
│       └── chains/          # Конфиги блокчейнов
│
├── scenarios/               # YAML тест-сценарии
│   ├── common/              # Переиспользуемые шаблоны
│   ├── features/            # Feature-specific тесты
│   └── suites/              # Тестовые сьюты
│
└── docs/                    # Документация
    ├── en/                  # English documentation
    └── ru/                  # Русская документация
```

## 🎨 Основные команды

```bash
# === Управление сетью ===
stage-env start                    # Запустить сеть
stage-env start --no-wait          # Запуск без ожидания ONLINE
stage-env start --topology default # Запуск с конкретной топологией
stage-env start --clean            # Очистить данные перед запуском
stage-env start --rebuild          # Пересобрать Docker образы перед запуском
stage-env stop                     # Остановить сеть
stage-env stop --volumes           # Остановить и удалить volumes
stage-env restart                  # Перезапустить всю сеть
stage-env restart node-1           # Перезапустить конкретную ноду
stage-env status                   # Показать статус всех нод

# === Тестирование ===
stage-env run-tests scenarios/                    # Запустить тесты из директории
stage-env run-tests scenarios/test.yml            # Запустить конкретный сценарий
stage-env run-tests scenarios/ --filter token     # Фильтр по названию
stage-env run-tests scenarios/ --no-start-network # Не запускать сеть
stage-env run-tests scenarios/ --keep-running     # Не останавливать после тестов

# === Мониторинг ===
stage-env logs node-1               # Показать логи ноды (последние 100 строк)
stage-env logs node-1 --tail 500    # Показать последние 500 строк
stage-env logs node-1 --follow      # Follow логи в реальном времени
stage-env exec node-1 "ls -la"      # Выполнить команду в контейнере ноды

# === Артефакты и отчеты ===
stage-env collect-artifacts e2e --exit-code=0         # Собрать артефакты E2E тестов
stage-env collect-artifacts functional --exit-code=1  # Собрать артефакты функциональных тестов

# === Сборка ===
stage-env build                 # Собрать Cellframe Node (Debug)
stage-env build --release       # Собрать Release версию
stage-env build --clean         # Чистая сборка (удалить build/)
stage-env build --jobs 8        # Параллельная сборка (8 потоков)

# === Сертификаты ===
stage-env certs                                    # Сгенерировать сертификаты (default: 4 ноды, 3 валидатора)
stage-env certs --nodes 7 --validators 5           # Для 7 нод с 5 валидаторами
stage-env certs --network stagenet                 # Для конкретной сети
stage-env certs --force                            # Пересоздать существующие

# === Очистка ===
stage-env clean --all          # Очистить всё (build + certs + cache)
stage-env clean --build        # Очистить только build артефакты
stage-env clean --certs        # Очистить только сертификаты

# === Глобальные опции ===
stage-env --verbose start      # Детальные логи
stage-env --json start         # JSON вывод логов
stage-env --config path.cfg start  # Использовать другой конфиг
```

## 📝 Написание тестов

### Простой тест

```yaml
# scenarios/my_test.yml
name: My First Test
description: Check wallet creation

includes:
  - common/network_minimal.yml

test:
  - cli: wallet new -w test_wallet
    save: wallet_addr
  
  - cli: wallet list
    contains: test_wallet

check:
  - cli: wallet info -w test_wallet
    contains: {{wallet_addr}}
```

### Запуск теста

```bash
./stage-env/stage-env run-tests scenarios/my_test.yml
```

### Готовые шаблоны

- `common/network_minimal.yml` - 1 нода (root validator)
- `common/network_full.yml` - 4 ноды (3 validators + 1 full node)
- `common/wallet_setup.yml` - Готовый кошелёк с адресом
- `common/network_dynamic_addition.yml` - Динамическое добавление нод

## 🔧 Конфигурация

Основная конфигурация находится в `tests/stage-env.cfg`:

```ini
# === Сеть ===
[network]
name = stagenet                    # Имя сети
network_id = 0x1234                # Network ID
consensus_type = esbocs            # Тип консенсуса (esbocs/pos/poa)

# === Топология ===
[topology]
root_nodes_count = 3               # Количество root нод
master_nodes_count = 3             # Количество master нод
full_nodes_count = 1               # Количество full нод

# === Сборка ===
[build]
build_type = debug                 # debug или release
cellframe_version = latest         # Версия Cellframe Node

# === Сетевые настройки ===
[network_settings]
base_rpc_port = 8545               # Базовый порт RPC
base_p2p_port = 31337              # Базовый порт P2P
base_http_port = 8079              # Базовый порт HTTP
node_port = 8079                   # Порт для внешних подключений
subnet = 172.20.0.0/16             # Docker subnet

# === Консенсус ===
[consensus]
min_validators = 2                 # Минимум валидаторов
new_round_delay = 45               # Задержка между раундами
collecting_level = 10.0            # Уровень сбора голосов
auth_certs_prefix = stagenet.master # Префикс сертификатов

# === Балансировщик ===
[balancer]
enabled = true                     # Включить балансировщик
type = http                        # Тип балансировщика (http)
uri = f0intlt4eyl03htogu           # URI балансировщика
max_links_response = 10            # Макс. количество ссылок в ответе
request_delay = 20                 # Задержка между запросами

# === Функции ===
[features]
monitoring = false                 # Мониторинг
tests = false                      # Тестовый режим
crash_artifacts = true             # Сбор артефактов при крашах

# === Пути ===
[paths]
cache_dir = ../testing/cache       # Директория кэша
artifacts_dir = ../testing/artifacts # Директория артефактов

# === Логирование ===
[logging]
log_dir = ../testing/logs          # Директория логов
log_level = info                   # Уровень логирования (debug/info/warning/error)
scenario_logs = true               # Логировать выполнение сценариев
retain_days = 7                    # Хранить логи N дней

# === Артефакты ===
[artifacts]
collect_node_logs = true           # Собирать логи нод
collect_health_logs = true         # Собирать health check логи
collect_crash_dumps = true         # Собирать core dumps
retain_days = 30                   # Хранить артефакты N дней

# === Таймауты (в секундах) ===
[timeouts]
startup = 600                      # Таймаут запуска сети
health_check = 600                 # Таймаут health check
command = 30                       # Таймаут выполнения команд

# === Источник ноды ===
[node_source]
type = local                       # local/url/repository
local_path = ../test_build/cellframe-node.deb  # Путь к локальному .deb
# url = https://...                # URL для загрузки
# repository_url = https://...     # Git репозиторий для сборки
```

## 🎯 Интеграция в свой проект

### Пример run.sh

```bash
#!/bin/bash
set -euo pipefail

STAGE_ENV="./stage-env/stage-env"
STAGE_ENV_CONFIG="./stage-env.cfg"

# Сборка (опционально)
# cmake -B build && make -C build

# Запуск сети
"$STAGE_ENV" --config="$STAGE_ENV_CONFIG" start

# Запуск тестов
"$STAGE_ENV" --config="$STAGE_ENV_CONFIG" run-tests scenarios/

# Сбор артефактов
"$STAGE_ENV" --config="$STAGE_ENV_CONFIG" collect-artifacts e2e --exit-code=$?

# Остановка
"$STAGE_ENV" --config="$STAGE_ENV_CONFIG" stop
```

### Настройка топологии

Топология сети настраивается через секцию `[topology]` в `stage-env.cfg`:

```ini
[topology]
root_nodes_count = 3     # Root ноды (seed nodes, bootstrap)
master_nodes_count = 3   # Master ноды (validators)
full_nodes_count = 1     # Full ноды (без валидации)
```

Или используйте готовые топологии:

```bash
./stage-env start --topology default  # По умолчанию (из конфига: 3 root + 3 master + 1 full = 7 нод)
./stage-env start --topology minimal  # 1 root нода для быстрых тестов
```

**Примечание:** Фактическое количество нод зависит от конфигурации в `[topology]` секции `stage-env.cfg`.

## 📊 Артефакты и отчеты

После каждого прогона в `testing/artifacts/<run_id>/`:

```
e2e_20251023_150000/
├── reports/
│   ├── report.md            # Markdown отчет
│   └── report.pdf           # PDF отчет (pandoc)
├── stage-env-logs/          # Логи stage-env
├── node-logs/               # Логи Docker контейнеров
├── core-dumps/              # Core dumps (если были)
├── health-logs/             # Health check логи
└── summary.json             # JSON сводка
```

## 🔍 Troubleshooting

### Проблемы с Docker

```bash
# Проверка Docker
docker ps
docker-compose version

# Перезапуск Docker
sudo systemctl restart docker
```

### Проблемы с портами

```bash
# Проверка занятых портов
ss -tlnp | grep 8079

# Остановка всех контейнеров
./stage-env stop --volumes
```

### Проблемы с Python

```bash
# Пересоздать venv
rm -rf .venv
./stage-env --help  # Создаст venv заново
```

### Логи для отладки

```bash
# Verbose режим
./stage-env --verbose start

# Логи конкретной ноды
./stage-env logs node-1 --tail 100

# Статус всех нод
./stage-env status
```

## 📚 Подробная документация

### Для QA инженеров

- **[Tutorial](scenarios/Tutorial.md)** - 8 уроков с упражнениями для изучения языка сценариев
- **[Cookbook](scenarios/Cookbook.md)** - 50 готовых рецептов для типовых задач
- **[Glossary](scenarios/Glossary.md)** - Полный справочник: все команды, параметры, примеры

### Готовые примеры

- `scenarios/common/` - Переиспользуемые шаблоны (network_minimal.yml, network_full.yml)
- `scenarios/features/` - Реальные тесты функциональности
- `scenarios/suites/` - Наборы тестов для комплексной проверки

## 🤝 Участие в разработке

1. Форк репозитория
2. Создайте feature branch (`git checkout -b feature/amazing-feature`)
3. Commit изменений (`git commit -m 'Add amazing feature'`)
4. Push в branch (`git push origin feature/amazing-feature`)
5. Создайте Pull Request

## 📜 Лицензия

См. LICENSE в корне проекта.

## 🔗 Ссылки

- [Cellframe Node](https://github.com/demlabs-cellframe/cellframe-node)
- [DAP SDK](https://github.com/demlabs-cellframe/dap-sdk)
- [Python Cellframe](https://github.com/demlabs-cellframe/python-cellframe)


---

**Язык:** Русский | [English](../en/README.md)
