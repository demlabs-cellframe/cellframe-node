# Анализ allurectl - CLI для Allure TestOps

**Дата анализа**: 2025-01-27  
**Источник**: https://docs.qatools.ru/ecosystem/allurectl  
**Назначение**: Приложение командной строки для работы с API Allure TestOps

## 📋 Обзор allurectl

**allurectl** — это приложение командной строки для работы с API Allure TestOps, которое позволяет:

- ✅ Загружать результаты тестов в реальном времени из CI/CD джоб
- ✅ Управлять сущностями на стороне TestOps (тест-кейсы, запуски, проекты)
- ✅ Интегрироваться с различными CI-системами
- ✅ Автоматизировать процесс отчетности

## 🎯 Основные возможности

### 1. Загрузка результатов тестов
- Загрузка в реальном времени из CI/CD пайплайнов
- Создание запусков и сессий автоматически
- Обработка больших объемов данных (показан пример с 7.17 GB)
- Пакетная загрузка файлов (по умолчанию 10 файлов в пакете)

### 2. Управление сущностями TestOps
- Создание и управление тест-кейсами
- Управление запусками тестов
- Работа с проектами
- Связывание с таск-трекерами (Jira, GitLab, GitHub и др.)

### 3. Интеграция с CI/CD
Поддерживаемые системы:
- ✅ **AWS CodePipeline**
- ✅ **Azure DevOps**
- ✅ **Bamboo**
- ✅ **Bitbucket**
- ✅ **CircleCI**
- ✅ **GitHub**
- ✅ **GitLab**
- ✅ **Jenkins**
- ✅ **TeamCity**

## 🚀 Установка и настройка

### Скачивание
Доступны бинарные файлы для различных платформ:

```bash
# Linux x64
wget https://github.com/allure-framework/allurectl/releases/latest/download/allurectl_linux_amd64 -O ./allurectl
chmod +x ./allurectl

# macOS Intel
wget https://github.com/allure-framework/allurectl/releases/latest/download/allurectl_darwin_amd64 -O ./allurectl

# macOS M1 (ARM64)
wget https://github.com/allure-framework/allurectl/releases/latest/download/allurectl_darwin_arm64 -O ./allurectl

# Windows x64
wget https://github.com/allure-framework/allurectl/releases/latest/download/allurectl_windows_amd64.exe -O ./allurectl.exe
```

### Создание API-токена
Перед использованием необходимо создать API-токен в меню пользователя TestOps для аутентификации.

## 🔧 Режимы работы

### 1. Режим Non-CI (локальный)
Используется для локальной загрузки с ПК разработчика.

#### Передача параметров через командную строку:
```bash
allurectl upload --endpoint https://testops.example.com \
--token 55555555-5555-5555-5555-555555555555 \
--project-id 100 \
--launch-name "Ручной локальный запуск 2020-12-31" \
path/to/allure-results
```

#### Передача параметров через переменные окружения:
```bash
# Объявление переменных окружения
export ALLURE_ENDPOINT=https://testops.example.com
export ALLURE_TOKEN=55555555-5555-5555-5555-555555555555
export ALLURE_PROJECT_ID=100
export ALLURE_LAUNCH_NAME="Ручной локальный запуск 2020-12-31"
export ALLURE_LAUNCH_TAGS="release, critical"

# Запуск загрузки
allurectl upload path/to/allure-results
```

### 2. Режим CI
Автоматически определяется по наличию переменных CI окружения. Позволяет управлять параметрами запуска джоб.

## 📊 Процесс загрузки и отчетность

### Что происходит при загрузке:
1. Создается новый запуск с указанным названием
2. Создается новая сессия для загрузки результатов
3. Результаты загружаются в рамках созданной сессии
4. Сессия закрывается
5. Запуск остается открытым до ручного или автоматического закрытия

### Детальная статистика загрузки:

#### Индексация файлов:
```
+-----------+----------------------+---------------+--------------+----------------+
|  TIMINGS: |  Duration=6m26.95s   | Min=325.101ms | Avg=2m50.77s | Max=6m26.8992s |
+-----------+----------------------+---------------+--------------+----------------+
```

#### Пропуски (orphan files):
```
+-----------+-------------------------------------------------------------+------------------+
|   SKIPS:  |                            Reason                           |       Count      |
+-----------+-------------------------------------------------------------+------------------+
|           | can't find *-result.json or *-container.json for attachment |        828       |
+-----------+-------------------------------------------------------------+------------------+
```

#### Большие файлы (предупреждения):
```
!!! WARNING !!!
+------------------------------------------------------------------------------------------------------------+-----------+
| The following test results files have the size over 2,000,000 bytes and will be skipped by Allure TestOps: |           |
+------------------------------------------------------------------------------------------------------------+-----------+
|               /opt/allurectl/allure-results/a86295d3-483c-44e5-b1a7-ce6cdea3b1b1-result.json               | 6.751 MB  |
|               /opt/allurectl/allure-results/24cd7f86-26e2-483c-9184-f51044debbe2-result.json               | 75.140 MB |
+------------------------------------------------------------------------------------------------------------+-----------+
```

#### Статистика загрузки:
```
+-------------------------------------------------------------------------------------------------------------------+
| Uploading Stats                                                                                                   |
+----------+--------------------------+------------------+---------------------+--------------------+---------------+
|  FILES:  | TotalBatches=3645        | TotalFiles=28968 | UploadedFiles=28968 | TotalSize=7.170 GB | ErrorsCount=0 |
+----------+--------------------------+------------------+---------------------+--------------------+---------------+
| TIMINGS: | Duration=6m25.911071126s |  Min=47.595229ms |   Avg=210.704214ms  |  Max=3.663549864s  |               |
+----------+--------------------------+------------------+---------------------+--------------------+---------------+
```

### Индикация прогресса:
```
Total files indexed: 29796 || Finished files: 28968 || Orphan Files: 828
```

### Завершение загрузки:
```
Watcher finished in [6m28.100628726s]
You can find report here: https://testops.example.com/launch/34
Stop 2024-01-15 114008
```

## 🔗 Интеграции

### CI-системы:
- AWS CodePipeline
- Azure DevOps
- Bamboo
- Bitbucket
- CircleCI
- GitHub
- GitLab
- Jenkins
- TeamCity

### Таск-трекеры:
- Битрикс24
- EvaProject
- GitHub
- GitLab
- Jira Data Center
- Jira Software Cloud
- Kaiten
- Redmine
- Wrike
- Yandex Tracker
- YouTrack

### Системы управления тестированием:
- Allure TestOps
- TestRail
- Xray
- Zephyr

## 💡 Применение для Cellframe Node QA

### Интеграция с существующей QA системой:

#### 1. Расширение pytest тестов:
```bash
# В qa-tests/test_cellframe_qa.py уже используется allure-pytest
pytest test_cellframe_qa.py --alluredir=allure-results -v

# Добавить загрузку в TestOps
allurectl upload allure-results
```

#### 2. CI/CD интеграция в GitLab:
```yaml
qa-tests:
  stage: test
  image: docker:latest
  services:
    - docker:dind
  script:
    - cd qa-tests
    - docker build -f Dockerfile.qa-pytest -t cellframe-node-qa .
    - docker run --rm --privileged -v $(pwd)/allure-results:/opt/qa-tests/allure-results cellframe-node-qa
    - wget https://github.com/allure-framework/allurectl/releases/latest/download/allurectl_linux_amd64 -O ./allurectl
    - chmod +x ./allurectl
    - allurectl upload allure-results
  artifacts:
    paths:
      - allure-results/
    expire_in: 1 week
```

#### 3. Настройка переменных окружения:
```bash
export ALLURE_ENDPOINT=https://testops.cellframe.net
export ALLURE_TOKEN=your-api-token
export ALLURE_PROJECT_ID=cellframe-node-qa
export ALLURE_LAUNCH_NAME="Cellframe Node QA - $(date +%Y-%m-%d)"
export ALLURE_LAUNCH_TAGS="cellframe,node,qa,automated"
```

## 🎯 Преимущества для проекта

### 1. Централизованная отчетность:
- Все результаты тестов в одном месте
- История запусков и тренды
- Сравнение результатов между версиями

### 2. Интеграция с разработкой:
- Автоматические отчеты при каждом коммите
- Связывание с задачами в GitLab Issues
- Уведомления о падающих тестах

### 3. Аналитика и метрики:
- Статистика по покрытию тестами
- Анализ стабильности тестов
- Выявление проблемных областей

### 4. Командная работа:
- Общий доступ к результатам тестов
- Комментирование и обсуждение результатов
- Назначение ответственных за исправление

## 🛠️ Практические рекомендации

### 1. Настройка для Cellframe Node:

#### Создание проекта в TestOps:
- Название: "Cellframe Node QA"
- Описание: "Автоматизированное тестирование Cellframe Node"
- Теги: cellframe, node, blockchain, qa

#### Настройка автоматических запусков:
```bash
# В CI/CD pipeline
allurectl upload allure-results \
  --launch-name "Cellframe Node v$(cat version.mk | grep VERSION | cut -d'=' -f2) - $(date +%Y-%m-%d_%H-%M)" \
  --launch-tags "version-$(cat version.mk | grep VERSION | cut -d'=' -f2),automated,ci"
```

### 2. Мониторинг и алертинг:
- Настройка уведомлений о падающих тестах
- Интеграция с Slack/Telegram для команды
- Еженедельные отчеты о качестве

### 3. Анализ результатов:
- Отслеживание трендов стабильности
- Выявление флаки тестов
- Анализ покрытия функциональности

## 📈 Метрики и KPI

### Ключевые показатели:
1. **Стабильность тестов**: % успешных запусков
2. **Скорость выполнения**: время выполнения тестов
3. **Покрытие**: % функциональности покрытой тестами
4. **Время исправления**: от обнаружения до исправления бага

### Дашборды в TestOps:
- Обзор качества релизов
- Тренды по времени выполнения
- Статистика по типам ошибок
- Покрытие тестами по модулям

## 🔮 Возможности развития

### Краткосрочные улучшения:
1. Интеграция allurectl в существующие Docker контейнеры
2. Настройка автоматических отчетов в CI/CD
3. Создание дашбордов для мониторинга

### Долгосрочные планы:
1. Интеграция с системой релизов
2. Автоматическое создание тест-кейсов
3. Связывание с системой управления требованиями

## ⚠️ Ограничения и особенности

### Ограничения файлов:
- Файлы результатов > 2MB пропускаются
- Orphan files (не связанные с результатами) удаляются
- Максимальный размер пакета: 10 файлов

### Производительность:
- Загрузка больших объемов может занимать время (пример: 6+ минут для 7GB)
- Рекомендуется использовать в CI/CD для автоматизации
- Локальная загрузка подходит для разовых проверок

## 📚 Дополнительные ресурсы

### Документация:
- [Allure TestOps Documentation](https://docs.qatools.ru/)
- [allurectl GitHub Releases](https://github.com/allure-framework/allurectl/releases)
- [Allure Framework](https://allurereport.org/)

### Интеграции:
- [GitLab CI Integration](https://docs.qatools.ru/integrations/ci-systems/gitlab)
- [Jenkins Integration](https://docs.qatools.ru/integrations/ci-systems/jenkins)
- [Jira Integration](https://docs.qatools.ru/integrations/task-trackers/jira-data-center)

## ✅ Заключение

**allurectl** представляет собой мощный инструмент для интеграции Allure TestOps в процесс разработки Cellframe Node:

### Ключевые преимущества:
- ✅ **Централизованная отчетность** - все результаты в одном месте
- ✅ **CI/CD интеграция** - автоматические отчеты при каждом коммите
- ✅ **Детальная аналитика** - статистика, тренды, метрики
- ✅ **Командная работа** - общий доступ и обсуждение результатов
- ✅ **Интеграция с таск-трекерами** - связывание с GitLab Issues

### Рекомендации для внедрения:
1. **Начать с локального тестирования** - настроить allurectl для ручных запусков
2. **Интегрировать в CI/CD** - добавить в GitLab CI pipeline
3. **Настроить мониторинг** - создать дашборды и алерты
4. **Обучить команду** - провести обучение по работе с TestOps

### Следующие шаги:
1. Создать аккаунт в Allure TestOps
2. Настроить проект для Cellframe Node
3. Интегрировать allurectl в существующие тесты
4. Настроить автоматические отчеты в CI/CD

**Статус**: ✅ **ГОТОВ К ВНЕДРЕНИЮ** в существующую QA систему Cellframe Node

---

**Анализ выполнен**: 2025-01-27  
**Источник**: https://docs.qatools.ru/ecosystem/allurectl  
**Рекомендация**: Интегрировать в существующую QA инфраструктуру для улучшения отчетности и аналитики




