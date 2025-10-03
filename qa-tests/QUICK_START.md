# Quick Start Guide - Cellframe Node QA Testing

## TL;DR

Быстрое тестирование ноды в Docker:

```bash
cd /home/nick/Projects/Demlabs/cellframe-node/qa-tests

# Build container
docker build -f Dockerfile.qa -t cellframe-node-qa .

# Run tests
docker run --rm --privileged \
  --tmpfs /run \
  --tmpfs /run/lock \
  -v /sys/fs/cgroup:/sys/fs/cgroup:ro \
  cellframe-node-qa
```

## Что это делает?

1. ✅ Устанавливает cellframe-node из репозитория
2. ✅ Проверяет все файлы и конфигурации
3. ✅ Запускает сервис
4. ✅ Проверяет подключение к сетям (Backbone, KelVPN)
5. ✅ Тестирует CLI команды
6. ✅ Проверяет Python окружение
7. ✅ Анализирует логи и ресурсы
8. ✅ Выдает полный отчет

## Результаты

### ✅ Успех (Exit code: 0)
```
===========================================================
  TEST RESULTS SUMMARY
===========================================================

Total tests:  45
Passed:       45
Failed:       0

✓ ALL TESTS PASSED
```

### ❌ Ошибки (Exit code: 1)
```
===========================================================
  TEST RESULTS SUMMARY
===========================================================

Total tests:  45
Passed:       42
Failed:       3

✗ SOME TESTS FAILED
```

## Что проверяется?

### Основные проверки:
- [x] Установка пакета
- [x] Структура файлов
- [x] Конфигурационные файлы
- [x] Systemd сервис
- [x] Процесс ноды
- [x] CLI команды
- [x] Сети (Backbone, KelVPN)
- [x] Синхронизация
- [x] Кошельки
- [x] Python окружение
- [x] Использование ресурсов
- [x] Логирование

### Детальная спецификация
См. `QA_SPECIFICATION_LINUX.md` - полная документация со всеми деталями.

## Использование в CI/CD

### GitHub Actions

```yaml
name: QA Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - run: cd qa-tests && docker build -f Dockerfile.qa -t qa .
      - run: docker run --rm --privileged qa
```

### GitLab CI

```yaml
qa-tests:
  stage: test
  image: docker:latest
  services: [docker:dind]
  script:
    - cd qa-tests
    - docker build -f Dockerfile.qa -t qa .
    - docker run --rm --privileged qa
```

## Мониторинг в production

Health check каждые 5 минут:

```bash
# Копируем скрипт
sudo cp health-check.sh /opt/cellframe-node/bin/

# Добавляем в cron
echo "*/5 * * * * /opt/cellframe-node/bin/health-check.sh" | sudo crontab -
```

## Отладка проблем

### Нода не запускается

```bash
# Проверить логи
sudo tail -100 /opt/cellframe-node/var/log/cellframe-node.log

# Статус сервиса
sudo systemctl status cellframe-node

# Проверить конфиг
sudo /opt/cellframe-node/bin/cellframe-node-config -e net_list all
```

### Сети не синхронизируются

```bash
# Статус сетей
sudo /opt/cellframe-node/bin/cellframe-node-cli net list

# Backbone статус
sudo /opt/cellframe-node/bin/cellframe-node-cli net -net Backbone get status

# Принудительная синхронизация
sudo /opt/cellframe-node/bin/cellframe-node-cli net -net Backbone sync all
```

### Высокое использование ресурсов

```bash
# Проверить память
ps aux | grep cellframe-node

# Проверить CPU
top -p $(pgrep cellframe-node)

# Перезапустить
sudo systemctl restart cellframe-node
```

## Что делать с результатами?

### Все тесты прошли ✅
- Нода работает корректно
- Можно использовать в production
- Релиз готов

### Есть ошибки ❌
1. Посмотреть детали ошибок в выводе
2. Проверить логи: `/opt/cellframe-node/var/log/cellframe-node.log`
3. Исправить проблемы
4. Запустить тесты снова

### Есть предупреждения ⚠️
- Нода работает, но есть нюансы
- Оценить критичность
- Возможно требуется больше времени на синхронизацию

## Временные рамки

| Этап | Время | Примечание |
|------|-------|------------|
| Build Docker | 2-5 мин | Зависит от скорости интернета |
| Установка пакета | 1-2 мин | Загрузка и установка |
| Запуск ноды | 30-60 сек | Инициализация |
| Синхронизация | 15-30 мин | Первый запуск |
| Тесты | 5-10 мин | Без учета синхронизации |
| **Итого** | **20-50 мин** | Полный цикл |

## Ускорение тестов

Для быстрых проверок (без полной синхронизации):

```bash
# Только базовые проверки
docker run --rm --privileged cellframe-node-qa /opt/qa-tests/health-check.sh
```

## Файлы проекта

```
qa-tests/
├── Dockerfile.qa          # Docker контейнер для тестов
├── test-suite.sh          # Полный набор тестов (11 секций)
├── health-check.sh        # Быстрая проверка здоровья
├── README.md              # Полная документация
└── QUICK_START.md         # Этот файл

QA_SPECIFICATION_LINUX.md  # Эталонная спецификация (150+ страниц)
```

## Кастомизация

### Изменить сети для тестирования

Редактировать `test-suite.sh`:

```bash
cellframe-node cellframe-node/backbone_enabled boolean false
cellframe-node cellframe-node/riemann_enabled boolean true  # тестнет вместо мейннета
```

### Добавить свои тесты

```bash
test_section "12. My Custom Tests"

if [[ условие ]]; then
    test_pass "Описание теста"
else
    test_fail "Название теста" "Сообщение об ошибке"
fi
```

## Best Practices

1. **Всегда запускать тесты перед релизом**
2. **Проверять в чистом контейнере** (не в production окружении)
3. **Сохранять логи тестов** для анализа
4. **Автоматизировать в CI/CD**
5. **Мониторить регулярно** (каждые 5-30 минут)

## Контакты

- Документация: `QA_SPECIFICATION_LINUX.md`
- Полная инструкция: `README.md`
- Issues: https://gitlab.demlabs.net/cellframe/cellframe-node/issues
- Telegram: t.me/cellframe_dev_en

## Лицензия

Как у основного проекта Cellframe Node

