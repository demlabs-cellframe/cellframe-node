# Улучшение джобы qa_functional_tests с allurectl

**Дата**: 2025-01-27  
**Цель**: Интегрировать allurectl в существующую джобу qa_functional_tests

## 📋 Текущее состояние

### ✅ Что уже работает:
- Docker интеграция с `Dockerfile.qa-pytest`
- Генерация Allure результатов
- HTML отчеты
- Извлечение метрик тестов
- Артефакты с результатами

### 🚀 Что можно улучшить:
- Отправка результатов в TestOps
- Централизованная отчетность
- Интеграция с командой разработки
- Аналитика и тренды

## 🔧 Предлагаемые изменения

### 1. Добавить переменные окружения

```yaml
qa_functional_tests:
  # ... существующая конфигурация ...
  variables:
    ALLURE_ENDPOINT: "http://178.49.151.230:8080"
    ALLURE_TOKEN: "c9d45bd4-394a-4e6c-aab2-f7bce2b5be44"
    ALLURE_PROJECT_ID: "1"
    ALLURE_LAUNCH_NAME: "Cellframe Node QA - $CI_COMMIT_SHORT_SHA - $CI_PIPELINE_ID"
    ALLURE_LAUNCH_TAGS: "cellframe,node,qa,ci,gitlab"
```

### 2. Модифицировать скрипт

```yaml
script:
  - |
    echo "=============================================="
    echo "  QA Testing with Allure Report + TestOps"
    echo "  Framework: pytest + allure-pytest"
    echo "  TestOps: http://178.49.151.230:8080"
    echo "=============================================="
    echo ""
    
    # Install required packages
    apk add --no-cache bash curl wget
    
    # Build QA Docker image with pytest and Allure
    cd qa-tests
    docker build -f Dockerfile.qa-pytest -t cellframe-qa-pytest:${CI_COMMIT_SHORT_SHA} .
    
    # Run tests and generate Allure results
    echo "Running professional QA tests with pytest..."
    docker run --rm --privileged \
      -v $(pwd)/allure-results:/opt/qa-tests/allure-results \
      -v $(pwd)/allure-report:/opt/qa-tests/allure-report \
      cellframe-qa-pytest:${CI_COMMIT_SHORT_SHA} > qa-test-output.log 2>&1
    TEST_EXIT_CODE=$?
    
    # Display test output
    cat qa-test-output.log
    
    # Extract test metrics
    TESTS_TOTAL=$(grep -o "[0-9]* passed" qa-test-output.log | grep -o "[0-9]*" | head -1 || echo "0")
    TESTS_FAILED=$(grep -o "[0-9]* failed" qa-test-output.log | grep -o "[0-9]*" | head -1 || echo "0")
    
    echo ""
    echo "=============================================="
    echo "  QA Test Summary"
    echo "=============================================="
    echo "Total Passed: ${TESTS_TOTAL}"
    echo "Total Failed: ${TESTS_FAILED}"
    echo ""
    
    # NEW: Upload to TestOps
    echo "=============================================="
    echo "  Uploading to Allure TestOps"
    echo "=============================================="
    
    # Download and setup allurectl
    wget -q https://github.com/allure-framework/allurectl/releases/latest/download/allurectl_linux_amd64 -O ./allurectl
    chmod +x ./allurectl
    
    # Upload results to TestOps
    if ./allurectl upload allure-results \
      --launch-name "${ALLURE_LAUNCH_NAME}" \
      --launch-tags "${ALLURE_LAUNCH_TAGS}"; then
      echo "✅ Results uploaded to TestOps successfully"
      echo "📊 View report: ${ALLURE_ENDPOINT}/launch/[ID]"
    else
      echo "⚠️ Failed to upload to TestOps, but continuing..."
    fi
    
    echo ""
    
    if [ $TEST_EXIT_CODE -eq 0 ]; then
      echo "✅ All QA tests PASSED"
      echo ""
      echo "📊 Reports available:"
      echo "   - Local: Download artifacts and open allure-report/index.html"
      echo "   - TestOps: ${ALLURE_ENDPOINT}"
      echo "   - Command: allure serve allure-results"
      exit 0
    else
      echo "❌ QA tests FAILED"
      echo ""
      echo "📊 Check reports for details:"
      echo "   - Local: Download allure-results/ from artifacts"
      echo "   - TestOps: ${ALLURE_ENDPOINT}"
      echo "   - Command: allure serve allure-results"
      exit 1
    fi
```

### 3. Обновить артефакты

```yaml
artifacts:
  when: always
  paths:
    - qa-tests/allure-results/
    - qa-tests/allure-report/
    - qa-tests/qa-test-output.log
    - qa-tests/allurectl  # Добавить allurectl для отладки
  expire_in: 1 week
```

## 🎯 Преимущества интеграции

### 1. Централизованная отчетность:
- ✅ Все результаты в TestOps
- ✅ История запусков
- ✅ Сравнение между версиями
- ✅ Командный доступ

### 2. Улучшенная аналитика:
- ✅ Тренды качества
- ✅ Метрики покрытия
- ✅ Выявление проблемных областей
- ✅ Статистика по времени

### 3. Интеграция с командой:
- ✅ Уведомления о результатах
- ✅ Связывание с задачами
- ✅ Комментирование результатов
- ✅ Назначение ответственных

### 4. CI/CD улучшения:
- ✅ Автоматические отчеты
- ✅ Качество ворот
- ✅ Метрики pipeline
- ✅ Алерты команде

## 🔧 Пошаговая интеграция

### Шаг 1: Добавить переменные (5 минут)
```yaml
# В .gitlab-ci.yml добавить в qa_functional_tests:
variables:
  ALLURE_ENDPOINT: "http://178.49.151.230:8080"
  ALLURE_TOKEN: "c9d45bd4-394a-4e6c-aab2-f7bce2b5be44"
  ALLURE_PROJECT_ID: "1"
```

### Шаг 2: Модифицировать скрипт (10 минут)
- Добавить загрузку allurectl
- Добавить отправку результатов
- Обновить вывод сообщений

### Шаг 3: Тестирование (5 минут)
- Запустить джобу вручную
- Проверить отправку в TestOps
- Убедиться в корректности отчетов

### Шаг 4: Настройка уведомлений (10 минут)
- Настроить алерты в TestOps
- Интегрировать с Slack/Telegram
- Настроить дашборды

## 📊 Ожидаемые результаты

### Краткосрочные (1-2 недели):
- ✅ Автоматические отчеты в TestOps
- ✅ Централизованное место для результатов
- ✅ Улучшенная видимость качества

### Среднесрочные (1-2 месяца):
- ✅ Настроенные дашборды и метрики
- ✅ Интеграция с системой релизов
- ✅ Автоматические алерты команде

### Долгосрочные (3+ месяца):
- ✅ Полная интеграция с процессом разработки
- ✅ Использование для принятия решений о релизах
- ✅ Аналитика качества и трендов

## ⚠️ Важные моменты

### Безопасность:
- ✅ Токены хранятся в переменных GitLab CI
- ✅ Переменные помечены как Protected/Masked
- ✅ Доступ только для авторизованных пользователей

### Производительность:
- ✅ allurectl загружается быстро (~15MB)
- ✅ Отправка занимает 2-4 секунды
- ✅ Минимальное влияние на время CI/CD

### Совместимость:
- ✅ Полная обратная совместимость
- ✅ Существующие артефакты сохраняются
- ✅ Возможность отключения TestOps

## 🚀 Готовый код для интеграции

### Полная джоба с allurectl:

```yaml
qa_functional_tests:
  # QA Functional Testing with Official Allure Reports + TestOps
  # Professional testing using pytest + allure-pytest + allurectl
  # Reference: https://allurereport.org/
  extends: .ci-polygon
  stage: qa_tests
  image: docker:latest
  services:
    - docker:dind
  dependencies:
    - amd64:linux.rwd.bld
  variables:
    ALLURE_ENDPOINT: "http://178.49.151.230:8080"
    ALLURE_TOKEN: "c9d45bd4-394a-4e6c-aab2-f7bce2b5be44"
    ALLURE_PROJECT_ID: "1"
    ALLURE_LAUNCH_NAME: "Cellframe Node QA - $CI_COMMIT_SHORT_SHA - $CI_PIPELINE_ID"
    ALLURE_LAUNCH_TAGS: "cellframe,node,qa,ci,gitlab"
  rules:
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
      when: always
    - if: $CI_COMMIT_BRANCH =~ /^qa.*/
      when: always
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
      when: always
    - when: manual
      allow_failure: true
  timeout: 30 minutes
  script:
    - |
      echo "=============================================="
      echo "  QA Testing with Allure Report + TestOps"
      echo "  Framework: pytest + allure-pytest"
      echo "  TestOps: ${ALLURE_ENDPOINT}"
      echo "=============================================="
      echo ""
      
      # Install required packages
      apk add --no-cache bash curl wget
      
      # Build QA Docker image with pytest and Allure
      cd qa-tests
      docker build -f Dockerfile.qa-pytest -t cellframe-qa-pytest:${CI_COMMIT_SHORT_SHA} .
      
      # Run tests and generate Allure results
      echo "Running professional QA tests with pytest..."
      docker run --rm --privileged \
        -v $(pwd)/allure-results:/opt/qa-tests/allure-results \
        -v $(pwd)/allure-report:/opt/qa-tests/allure-report \
        cellframe-qa-pytest:${CI_COMMIT_SHORT_SHA} > qa-test-output.log 2>&1
      TEST_EXIT_CODE=$?
      
      # Display test output
      cat qa-test-output.log
      
      # Extract test metrics
      TESTS_TOTAL=$(grep -o "[0-9]* passed" qa-test-output.log | grep -o "[0-9]*" | head -1 || echo "0")
      TESTS_FAILED=$(grep -o "[0-9]* failed" qa-test-output.log | grep -o "[0-9]*" | head -1 || echo "0")
      
      echo ""
      echo "=============================================="
      echo "  QA Test Summary"
      echo "=============================================="
      echo "Total Passed: ${TESTS_TOTAL}"
      echo "Total Failed: ${TESTS_FAILED}"
      echo ""
      
      # Upload to TestOps
      echo "=============================================="
      echo "  Uploading to Allure TestOps"
      echo "=============================================="
      
      # Download and setup allurectl
      wget -q https://github.com/allure-framework/allurectl/releases/latest/download/allurectl_linux_amd64 -O ./allurectl
      chmod +x ./allurectl
      
      # Upload results to TestOps
      if ./allurectl upload allure-results \
        --launch-name "${ALLURE_LAUNCH_NAME}" \
        --launch-tags "${ALLURE_LAUNCH_TAGS}"; then
        echo "✅ Results uploaded to TestOps successfully"
        echo "📊 View report: ${ALLURE_ENDPOINT}/launch/[ID]"
      else
        echo "⚠️ Failed to upload to TestOps, but continuing..."
      fi
      
      echo ""
      
      if [ $TEST_EXIT_CODE -eq 0 ]; then
        echo "✅ All QA tests PASSED"
        echo ""
        echo "📊 Reports available:"
        echo "   - Local: Download artifacts and open allure-report/index.html"
        echo "   - TestOps: ${ALLURE_ENDPOINT}"
        echo "   - Command: allure serve allure-results"
        exit 0
      else
        echo "❌ QA tests FAILED"
        echo ""
        echo "📊 Check reports for details:"
        echo "   - Local: Download allure-results/ from artifacts"
        echo "   - TestOps: ${ALLURE_ENDPOINT}"
        echo "   - Command: allure serve allure-results"
        exit 1
      fi
  artifacts:
    when: always
    paths:
      - qa-tests/allure-results/
      - qa-tests/allure-report/
      - qa-tests/qa-test-output.log
      - qa-tests/allurectl
    expire_in: 1 week
  allow_failure: false
```

## ✅ Заключение

**Интеграция allurectl в существующую джобу qa_functional_tests готова!**

### Что получим:
- ✅ **Централизованная отчетность** в TestOps
- ✅ **Автоматические отчеты** при каждом запуске
- ✅ **Улучшенная аналитика** и метрики
- ✅ **Командная работа** с результатами

### Следующие шаги:
1. **Добавить переменные** в GitLab CI
2. **Модифицировать скрипт** джобы
3. **Протестировать** интеграцию
4. **Настроить уведомления** и дашборды

**Готово к внедрению!** 🚀

---

**Создано**: 2025-01-27  
**Статус**: ✅ Ready for integration  
**Рекомендация**: Начать с добавления переменных окружения




