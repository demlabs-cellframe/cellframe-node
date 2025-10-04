# Allure Reports для Cellframe Node QA

## 📊 Что такое Allure?

Allure Framework - это гибкий инструмент для создания красивых и подробных отчетов о тестировании. Позволяет визуализировать результаты тестов, отслеживать историю, группировать по категориям и многое другое.

## 🚀 Быстрый старт

### 1. Собрать Docker образ с Allure:

```bash
cd qa-tests
docker build -f Dockerfile.qa-allure -t cellframe-node-qa-allure .
```

### 2. Запустить тесты и сгенерировать отчет:

```bash
docker run --rm --privileged \
  -v $(pwd)/reports:/opt/qa-tests/allure-report \
  cellframe-node-qa-allure
```

### 3. Открыть отчет:

```bash
# Отчет будет сохранен в qa-tests/reports/
# Открыть в браузере:
xdg-open reports/index.html
# или
firefox reports/index.html
```

---

## 📁 Структура Allure отчетов

```
allure-results/          # JSON файлы с результатами тестов
├── *-result.json       # Результаты отдельных тестов
├── *-container.json    # Контейнеры (suites)
├── categories.json     # Категории ошибок
├── environment.properties  # Информация об окружении
└── summary.txt         # Текстовое резюме

allure-report/          # Сгенерированный HTML отчет
├── index.html          # Главная страница отчета
├── styles.css
├── app.js
└── data/              # Данные для визуализации
```

---

## 🎨 Что показывает Allure отчет

### 📈 Overview (Обзор):
- Общее количество тестов
- Процент прохождения
- Время выполнения
- Тренды (если есть история)

### 📊 Suites (Наборы):
- Тесты сгруппированные по категориям:
  - Installation Verification
  - File System Structure
  - Python Environment
  - Node Startup
  - CLI Functionality
  - Network Status
  - Wallet Operations
  - Resource Usage
  - Log Analysis

### 📉 Graphs (Графики):
- Status распределение (passed/failed/warnings)
- Severity распределение
- Duration тестов
- Timeline выполнения

### 🏷️ Categories (Категории ошибок):
- Installation Issues
- Network Issues
- CLI Issues
- Wallet Issues
- Configuration Issues
- Resource Issues
- Non-critical Warnings

### 🌍 Environment (Окружение):
- Node Version
- Docker Image
- Test Framework
- Build Hash
- Python Version

---

## 🔧 Использование в CI/CD

### GitLab CI:

Уже добавлено в `.gitlab-ci.yml`:

```yaml
qa_functional_tests:
  stage: qa_tests
  artifacts:
    when: always
    paths:
      - qa-tests/allure-results
      - qa-tests/allure-report
    expire_in: 1 week
  script:
    - docker build -f qa-tests/Dockerfile.qa-allure -t qa-allure .
    - docker run --rm -v $(pwd)/qa-tests/reports:/opt/qa-tests/allure-report qa-allure
```

### Просмотр в GitLab:
1. Зайти в Pipeline → Job → Browse artifacts
2. Открыть `allure-report/index.html`
3. Скачать и открыть локально

---

## 📝 Формат результатов

### Test Result JSON:
```json
{
  "uuid": "unique-id",
  "name": "Node version check",
  "status": "passed",
  "stage": "finished",
  "description": "Version: CellframeNode, 5.5-0...",
  "start": 1696425600000,
  "stop": 1696425601000,
  "labels": [
    {"name": "suite", "value": "QA Tests"},
    {"name": "framework", "value": "bash"},
    {"name": "severity", "value": "critical"}
  ]
}
```

### Categories JSON:
```json
[
  {
    "name": "Network Issues",
    "matchedStatuses": ["failed"],
    "messageRegex": ".*[Nn]etwork.*"
  }
]
```

---

## 🎯 Расширенное использование

### Генерация истории (trends):

```bash
# Сохранить предыдущие результаты
mkdir -p allure-history
cp -r allure-report/history/* allure-history/

# При следующей генерации использовать историю
allure generate allure-results -o allure-report --clean
cp -r allure-history/* allure-report/history/
```

### Добавление attachments (скриншотов, логов):

```bash
# В тест скрипте
cp /opt/cellframe-node/var/log/cellframe-node.log \
   $ALLURE_RESULTS_DIR/node-log-attachment.txt
```

### Кастомные категории:

Редактировать `allure-results-generator.sh`, секцию `create_categories()`:

```json
{
  "name": "Custom Category",
  "matchedStatuses": ["failed"],
  "messageRegex": ".*pattern.*"
}
```

---

## 🔍 Примеры команд

### Локальный запуск с сохранением отчета:

```bash
# Запустить тесты
docker run --rm --privileged \
  -v $(pwd)/allure-results:/opt/qa-tests/allure-results \
  -v $(pwd)/allure-report:/opt/qa-tests/allure-report \
  cellframe-node-qa-allure

# Посмотреть результаты
allure open allure-report
```

### Генерация отчета из существующих результатов:

```bash
# Если у вас есть allure-results от предыдущих запусков
allure generate allure-results -o allure-report --clean

# Открыть в браузере
allure open allure-report
```

### Сравнение с предыдущими запусками:

```bash
# Сохранить текущий отчет
cp -r allure-report allure-report-$(date +%Y%m%d)

# Запустить новые тесты
./test-suite-allure.sh

# Сравнить результаты вручную или через Allure trends
```

---

## 📊 Интеграция с другими инструментами

### Jenkins:
```groovy
stage('QA Tests') {
    steps {
        sh 'docker run cellframe-node-qa-allure'
        allure includeProperties: false,
               jdk: '',
               results: [[path: 'allure-results']]
    }
}
```

### GitHub Actions:
```yaml
- name: Run QA Tests
  run: docker run --rm cellframe-node-qa-allure
  
- name: Publish Allure Report
  uses: simple-elf/allure-report-action@master
  with:
    allure_results: allure-results
    allure_report: allure-report
```

---

## 🐛 Troubleshooting

### Allure не генерирует отчет:
```bash
# Проверить что есть результаты
ls -la allure-results/*.json

# Проверить Java версию
java -version  # Должна быть 11+

# Переустановить Allure
wget https://github.com/allure-framework/allure2/releases/download/2.24.1/allure-2.24.1.tgz
tar -xzf allure-2.24.1.tgz
./allure-2.24.1/bin/allure generate allure-results
```

### Отчет не открывается в браузере:
```bash
# Использовать встроенный сервер Allure
allure serve allure-results  # Откроет браузер автоматически
```

### JSON файлы некорректные:
```bash
# Проверить формат
cat allure-results/*-result.json | jq .

# Пересоздать
rm -rf allure-results
mkdir allure-results
./test-suite-allure.sh
```

---

## 📚 Дополнительная информация

- **Документация Allure**: https://docs.qameta.io/allure/
- **GitHub**: https://github.com/allure-framework
- **Примеры**: https://demo.qameta.io/allure/

---

## ✨ Преимущества Allure отчетов

✅ **Визуализация**: Красивые графики и диаграммы  
✅ **История**: Отслеживание трендов между запусками  
✅ **Категории**: Автоматическая группировка ошибок  
✅ **Attachments**: Логи, скриншоты, файлы  
✅ **Интеграция**: Jenkins, GitLab, GitHub Actions  
✅ **Открытый код**: Бесплатно и расширяемо  

---

**Создано**: 2025-10-04  
**Версия**: 1.0  
**Поддержка**: См. QA_SPECIFICATION_LINUX.md

