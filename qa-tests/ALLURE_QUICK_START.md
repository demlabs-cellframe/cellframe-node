# 🚀 Allure Reports - Быстрый старт

## Запустить тесты и получить отчет:

\`\`\`bash
cd qa-tests

# 1. Собрать образ (один раз)
docker build -f Dockerfile.qa-allure -t cellframe-node-qa-allure .

# 2. Запустить тесты с генерацией отчета
docker run --rm --privileged \
  -v $(pwd)/allure-report:/opt/qa-tests/allure-report \
  -v $(pwd)/allure-results:/opt/qa-tests/allure-results \
  cellframe-node-qa-allure

# 3. Открыть отчет в браузере
xdg-open allure-report/index.html
# или
firefox allure-report/index.html
\`\`\`

## 📊 Что в отчете:

- ✅ **Overview**: Общая статистика и графики
- 📊 **Suites**: Тесты по категориям
- 📈 **Graphs**: Визуализация результатов
- 🏷️ **Categories**: Группировка ошибок
- 🌍 **Environment**: Информация об окружении
- 📝 **Timeline**: Время выполнения тестов

## 📁 Структура файлов:

\`\`\`
qa-tests/
├── allure-results/          # JSON с результатами
│   ├── *-result.json       # Результаты тестов
│   ├── categories.json     # Категории ошибок
│   └── environment.properties
│
└── allure-report/           # HTML отчет ✨
    ├── index.html          # 👈 ОТКРЫТЬ ЭТОТ ФАЙЛ
    ├── data/
    ├── styles.css
    └── widgets/
\`\`\`

## 🎨 Скриншоты того, что увидишь:

### 📊 Overview Dashboard:
- Круговая диаграмма: passed/failed/warnings
- Success rate: 96.4%
- Total tests: 28
- Duration: 38 секунд

### 📋 Test Suites:
- Installation Verification (2 tests)
- File System Structure (9 tests)
- Python Environment (1 test)
- Node Startup (2 tests)
- CLI Functionality (4 tests)
- Network Status (2 tests)
- Wallet Operations (2 tests)
- Resource Usage (3 tests)
- Log Analysis (3 tests)

### 🏷️ Categories (автоматическая группировка):
- Installation Issues
- Network Issues
- CLI Issues
- Wallet Issues
- Non-critical Warnings

## 🔄 CI/CD интеграция:

Уже добавлено в GitLab CI! После пуша ветки \`qa\`:
1. Pipeline запустится автоматически
2. Job \`qa_functional_tests\` создаст отчет
3. Скачать через Artifacts → allure-report/

## 💡 Полезные команды:

\`\`\`bash
# Только генерация отчета (если есть results)
docker run --rm -v $(pwd)/allure-results:/results \
  -v $(pwd)/allure-report:/report \
  ubuntu:24.04 bash -c \
  "apt-get update && apt-get install -y wget openjdk-17-jre-headless && \
   wget -q https://github.com/allure-framework/allure2/releases/download/2.24.1/allure-2.24.1.tgz && \
   tar -xzf allure-2.24.1.tgz && \
   ./allure-2.24.1/bin/allure generate /results -o /report --clean"

# Открыть отчет через Python HTTP сервер
cd allure-report
python3 -m http.server 8000
# Открыть http://localhost:8000 в браузере
\`\`\`

## 📚 Подробная документация:

См. \`ALLURE_REPORTS.md\` для полной информации.
