# Как запустить QA тесты

## 🚀 Быстрый запуск

### Полный функциональный тест:
```bash
cd qa-tests
docker build -f Dockerfile.qa-functional -t cellframe-node-qa .
docker run --rm --privileged cellframe-node-qa
```

**Время выполнения**: ~2 минуты  
**Тестов**: 40  
**Результат**: Детальный отчет в консоль

---

## 📋 Варианты запуска

### 1. Тест последней версии из internal репозитория (рекомендуется):
```bash
docker build -f Dockerfile.qa-functional -t cellframe-node-qa .
docker run --rm --privileged cellframe-node-qa
```

### 2. Тест пакета из публичного репозитория:
```bash
docker build -f Dockerfile.qa -t cellframe-node-qa-public .
docker run --rm --privileged cellframe-node-qa-public
```

### 3. Только проверка здоровья (быстро):
```bash
docker run --rm --privileged cellframe-node-qa /opt/qa-tests/health-check.sh
```

### 4. Интерактивный режим (для отладки):
```bash
docker run --rm -it --privileged cellframe-node-qa bash
# Внутри контейнера:
/opt/qa-tests/startup-node.sh
/opt/cellframe-node/bin/cellframe-node-cli version
/opt/cellframe-node/bin/cellframe-node-cli net list
```

---

## 📊 Что тестируется

✅ **Установка** (2 теста)
- Наличие пакета
- Версия ноды

✅ **Файловая структура** (12 тестов)
- Директории (bin, etc, var, python, share)
- Исполняемые файлы (node, cli, tool, config)
- Конфигурации (main, networks)

✅ **Python окружение** (2 теста)
- Python 3.10
- Pip и пакеты

✅ **Запуск ноды** (3 теста)
- Запуск процесса
- Создание логов
- Создание CLI сокета

✅ **CLI функциональность** (5 тестов)
- Версия
- Список сетей
- Наличие Backbone и KelVPN

✅ **Статус сетей** (4 теста)
- Backbone status
- KelVPN status
- Подключение к сети
- Синхронизация

✅ **Операции с кошельками** (4 теста)
- Список кошельков
- Создание
- Просмотр информации
- Сохранение на диск

✅ **Конфигурация** (2 теста)
- Config tool
- Настройки

✅ **Использование ресурсов** (3 теста)
- Память
- CPU
- Файловые дескрипторы

✅ **Анализ логов** (3 теста)
- Наличие логов
- Ошибки
- Критические сообщения

---

## 📈 Ожидаемые результаты

### Успешный запуск:
```
Total tests:  40
Passed:       39
Warnings:     1
Failed:       0

Success Rate: 97.5%

✓ ALL TESTS PASSED
```

### Что считается нормальным:
- ⚠️ Несколько warning'ов в логах (python plugins, авторизация)
- ⚠️ Синхронизация сетей может быть не завершена (это нормально)
- ⚠️ Пустой список кошельков (это ожидаемо)

### Что НЕ нормально:
- ❌ Нода не запускается
- ❌ CLI не отвечает
- ❌ Сети не подключаются
- ❌ Critical errors в логах

---

## 🐛 Отладка

### Если тесты не проходят:

1. **Проверьте логи ноды**:
```bash
docker run --rm -it --privileged cellframe-node-qa bash
/opt/qa-tests/startup-node.sh
cat /opt/cellframe-node/var/log/cellframe-node.log
```

2. **Проверьте процесс**:
```bash
ps aux | grep cellframe-node
pgrep cellframe-node
```

3. **Проверьте CLI сокет**:
```bash
ls -la /opt/cellframe-node/var/run/node_cli
```

4. **Запустите CLI команды вручную**:
```bash
/opt/cellframe-node/bin/cellframe-node-cli version
/opt/cellframe-node/bin/cellframe-node-cli net list
```

### Сохранить результаты тестов:
```bash
docker run --rm --privileged cellframe-node-qa 2>&1 | tee test-results-$(date +%Y%m%d-%H%M%S).log
```

---

## 🔧 Кастомизация тестов

### Запуск с другим пакетом:

Отредактируйте `Dockerfile.qa-functional`:
```dockerfile
RUN wget -q https://your-repo/cellframe-node-X.Y-Z-amd64.deb -O /tmp/cellframe-node.deb
```

### Добавить свои тесты:

Отредактируйте `test-suite-functional.sh`, добавьте секцию:
```bash
test_section "11. My Custom Tests"

# Your test here
MY_RESULT=$(your_command)
if [ $? -eq 0 ]; then
    test_pass "My test passed"
else
    test_fail "My test failed" "$MY_RESULT"
fi
```

---

## 📚 Дополнительная документация

- `QA_SPECIFICATION_LINUX.md` - Полная спецификация (1984 строки)
- `QA_TEST_REPORT.md` - Последний отчет о тестировании
- `QA_PROJECT_SUMMARY.md` - Обзор проекта
- `НАЧАЛО_РАБОТЫ.md` - Быстрый старт на русском

---

## 🎯 CI/CD Integration

### Для GitLab CI:
```yaml
test:cellframe-node:
  stage: test
  image: docker:latest
  services:
    - docker:dind
  script:
    - cd qa-tests
    - docker build -f Dockerfile.qa-functional -t cellframe-node-qa .
    - docker run --rm --privileged cellframe-node-qa
  only:
    - master
    - develop
```

### Для GitHub Actions:
```yaml
name: QA Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Build test container
        run: |
          cd qa-tests
          docker build -f Dockerfile.qa-functional -t cellframe-node-qa .
      - name: Run tests
        run: docker run --rm --privileged cellframe-node-qa
```

---

## ⚡ Production проверка

### На реальном сервере (с systemd):
```bash
# Статус службы
sudo systemctl status cellframe-node

# Версия
sudo /opt/cellframe-node/bin/cellframe-node-cli version

# Сети
sudo /opt/cellframe-node/bin/cellframe-node-cli net list

# Статус Backbone
sudo /opt/cellframe-node/bin/cellframe-node-cli net -net Backbone get status

# Логи
sudo tail -f /opt/cellframe-node/var/log/cellframe-node.log

# Использование ресурсов
ps aux | grep cellframe-node
sudo systemctl status cellframe-node | grep Memory
```

---

**Создано**: 2025-10-03  
**Версия тестов**: 1.0  
**Поддержка**: См. QA_SPECIFICATION_LINUX.md

