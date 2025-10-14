# Launch Manager Integration - Автоматическое управление запусками TestOps

## 🎯 **Описание**

Реализована система автоматического управления запусками (launches) в Allure TestOps с полной интеграцией в GitLab CI пайплайн.

## 🔧 **Что добавлено**

### **1. Launch Manager Script (`launch_manager.sh`)**

**Возможности:**
- ✅ Создание новых launches с метаданными
- ✅ Автоматическая загрузка результатов в существующий launch
- ✅ Получение статистики по launch (passed/failed/broken/skipped)
- ✅ Сравнение с предыдущим launch для выявления регрессий
- ✅ Автоматическое закрытие launch после завершения
- ✅ Цветной вывод и подробное логирование

**Команды:**
```bash
./launch_manager.sh create <name> <tags>     # Создать новый launch
./launch_manager.sh upload [launch_id] [dir] # Загрузить результаты
./launch_manager.sh stats [launch_id]        # Получить статистику
./launch_manager.sh compare [launch_id]      # Сравнить с предыдущим
./launch_manager.sh close [launch_id]        # Закрыть launch
./launch_manager.sh current                  # Показать текущий launch ID
```

### **2. GitLab CI Integration**

**Обновленный пайплайн:**
1. **Создание launch** перед запуском тестов
2. **Загрузка результатов** в созданный launch
3. **Анализ статистики** и выявление регрессий
4. **Автоматическое закрытие** launch

## 🚀 **Workflow в GitLab CI**

### **Шаг 1: Подготовка**
```bash
# Установка зависимостей
apk add --no-cache bash curl wget jq

# Скачивание allurectl
wget allurectl_linux_amd64 -O ./allurectl
chmod +x ./allurectl
```

### **Шаг 2: Создание Launch**
```bash
# Генерация имени launch
NODE_VERSION_INFO=$(echo "${NODE_DOWNLOAD_URL}" | sed 's|.*/||' | sed 's|\.deb$||')
LAUNCH_NAME="QA Tests - $(date +%d.%m.%Y_%H:%M) - ${NODE_VERSION_INFO} - v${CI_COMMIT_SHORT_SHA}"
LAUNCH_TAGS="${ALLURE_LAUNCH_TAGS}"

# Создание launch
./launch_manager.sh create "${LAUNCH_NAME}" "${LAUNCH_TAGS}"
```

### **Шаг 3: Запуск тестов**
```bash
# Обычный запуск Docker контейнера с тестами
docker run cellframe-qa-pytest:${CI_COMMIT_SHORT_SHA}
docker cp results...
```

### **Шаг 4: Загрузка и анализ**
```bash
# Загрузка результатов
./launch_manager.sh upload

# Получение статистики
./launch_manager.sh stats

# Анализ регрессий
./launch_manager.sh compare

# Закрытие launch
./launch_manager.sh close
```

## 📊 **Примеры вывода**

### **Создание Launch:**
```
[INFO] Creating new launch: QA Tests - 14.10.2025_21:00 - latest-amd64 - v2d9b110f
[INFO] Tags: cellframe,node,qa,ci,gitlab,qa-v2
[SUCCESS] Launch created with ID: 25
```

### **Статистика Launch:**
```
[INFO] Getting statistics for launch ID: 25
Launch Statistics:
  Passed: 24
  Failed: 5
  Broken: 0
  Skipped: 0
```

### **Сравнение с предыдущим Launch:**
```
[INFO] Comparing with previous launch...
[INFO] Comparing with previous launch ID: 24

=== Launch Comparison ===
Previous launch: 24 (2 failed)
Current launch:  25 (5 failed)
[WARNING] REGRESSION DETECTED: More tests failed than in previous launch
```

### **Закрытие Launch:**
```
[INFO] Closing launch ID: 25
[SUCCESS] Launch 25 closed successfully
```

## 🎯 **Преимущества новой системы**

### **1. Структурированность**
- ✅ Каждый запуск тестов = отдельный launch в TestOps
- ✅ Четкая связь между GitLab CI job и TestOps launch
- ✅ Автоматическое именование с версией ноды и commit hash

### **2. Анализ регрессий**
- ✅ Автоматическое сравнение с предыдущим запуском
- ✅ Выявление новых падений тестов
- ✅ Предупреждения о регрессиях в CI логах

### **3. Полная автоматизация**
- ✅ Создание → Загрузка → Анализ → Закрытие
- ✅ Обработка ошибок и откат при сбоях
- ✅ Подробное логирование всех операций

### **4. Трассируемость**
- ✅ Launch ID сохраняется в `.launch_id` файле
- ✅ Связь с GitLab CI pipeline через теги
- ✅ Информация о версии ноды в имени launch

## 🔧 **Конфигурация**

### **Переменные окружения:**
```bash
ALLURE_ENDPOINT="http://178.49.151.230:8080"
ALLURE_TOKEN="c9d45bd4-394a-4e6c-aab2-f7bce2b5be44"
ALLURE_PROJECT_ID="1"
ALLURE_LAUNCH_TAGS="cellframe,node,qa,ci,gitlab,${CI_COMMIT_REF_NAME}"
```

### **Зависимости:**
- `allurectl` - CLI для работы с TestOps
- `jq` - обработка JSON ответов
- `bash` - выполнение скриптов

## 📈 **Результаты в TestOps**

### **Структура Launch:**
```
Launch Name: "QA Tests - 14.10.2025_21:00 - cellframe-node-5.5-356-amd64 - v2d9b110f"
Tags: ["cellframe", "node", "qa", "ci", "gitlab", "qa-v2"]
Status: Closed
Results: 24 passed, 5 failed, 0 broken, 0 skipped
```

### **Связь с GitLab CI:**
- 🔗 **Pipeline ID** в тегах
- 🔗 **Commit hash** в имени launch
- 🔗 **Branch name** в тегах
- 🔗 **Node version** в имени launch

## 🚨 **Обработка ошибок**

### **Сценарии отката:**
1. **Ошибка создания launch** → Продолжение с обычной загрузкой
2. **Ошибка загрузки результатов** → Попытка закрыть launch
3. **Ошибка получения статистики** → Продолжение без анализа
4. **Ошибка сравнения** → Продолжение без регрессионного анализа

### **Логирование:**
- 🔵 **[INFO]** - информационные сообщения
- 🟢 **[SUCCESS]** - успешные операции
- 🟡 **[WARNING]** - предупреждения (регрессии)
- 🔴 **[ERROR]** - ошибки выполнения

## 🎯 **Следующие шаги**

### **Планируемые улучшения:**
1. **Автоматическое создание issues** для упавших тестов
2. **Интеграция с GitLab Issues** через API
3. **Дашборды и метрики** в TestOps
4. **Уведомления в Slack/Teams** о регрессиях
5. **Мержинг launches** для batch тестирования

### **Возможные расширения:**
- Поддержка multiple projects
- Кастомные правила для регрессий
- Интеграция с Jira/YouTrack
- Автоматическое создание тест-планов

## ✅ **Статус интеграции**

- ✅ **Launch Manager** - реализован и протестирован
- ✅ **GitLab CI Integration** - интегрирован в пайплайн
- ✅ **Regression Analysis** - автоматическое сравнение
- ✅ **Error Handling** - обработка всех сценариев
- ✅ **Documentation** - полная документация

**Система готова к продуктивному использованию!** 🚀
