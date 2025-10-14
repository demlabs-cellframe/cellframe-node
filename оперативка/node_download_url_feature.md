# NODE_DOWNLOAD_URL Feature - Тестирование кастомных версий ноды

## 🎯 **Описание**

Добавлена возможность тестировать любую версию Cellframe Node через переменную `NODE_DOWNLOAD_URL` в GitLab CI пайплайне.

## 🔧 **Как использовать**

### **1. По умолчанию (автоматически)**
```yaml
NODE_DOWNLOAD_URL: "https://internal-pub.cellframe.net/linux/cellframe-node/master/latest-amd64"
```
- ✅ Скачивается последняя стабильная версия
- ✅ Используется если переменная не задана

### **2. Кастомная версия (через TestOps или ручной запуск)**

**Примеры ссылок для тестирования:**
```bash
# Hotfix версии
https://internal-pub.cellframe.net/linux/cellframe-node/hotfix-mem/cellframe-node-5.5-356-amd64.deb
https://internal-pub.cellframe.net/linux/cellframe-node/hotfix-15316/cellframe-node-5.5-357-amd64.deb

# Bugfix версии  
https://internal-pub.cellframe.net/linux/cellframe-node/bugfix-18923/cellframe-node-5.4-359-amd64.deb

# Feature версии
https://internal-pub.cellframe.net/linux/cellframe-node/feature-18831/cellframe-node-5.5-357-amd64.deb
```

## 🚀 **Способы запуска**

### **Способ 1: Через TestOps (рекомендуется)**
1. Открыть TestOps: http://178.49.151.230:8080
2. Найти проект "Cellframe node"
3. Создать новый Launch с параметром:
   ```
   NODE_DOWNLOAD_URL=https://internal-pub.cellframe.net/linux/cellframe-node/hotfix-mem/cellframe-node-5.5-356-amd64.deb
   ```

### **Способ 2: Ручной запуск в GitLab**
1. Открыть GitLab: https://gitlab.demlabs.net/cellframe/cellframe-node
2. Перейти в CI/CD → Pipelines
3. Нажать "Run pipeline"
4. Добавить переменную:
   - **Key**: `NODE_DOWNLOAD_URL`
   - **Value**: `https://internal-pub.cellframe.net/linux/cellframe-node/hotfix-mem/cellframe-node-5.5-356-amd64.deb`
5. Запустить pipeline

### **Способ 3: Через API (для автоматизации)**
```bash
curl -X POST \
  -F token=YOUR_TRIGGER_TOKEN \
  -F ref=qa \
  -F "variables[NODE_DOWNLOAD_URL]=https://internal-pub.cellframe.net/linux/cellframe-node/hotfix-mem/cellframe-node-5.5-356-amd64.deb" \
  https://gitlab.demlabs.net/api/v4/projects/PROJECT_ID/trigger/pipeline
```

## 📊 **Что происходит при тестировании**

### **1. Docker Build**
```bash
# Dockerfile получает URL как аргумент
ARG NODE_DOWNLOAD_URL=https://internal-pub.cellframe.net/linux/cellframe-node/master/latest-amd64
RUN echo "Downloading Cellframe Node from: ${NODE_DOWNLOAD_URL}"
RUN wget -q "${NODE_DOWNLOAD_URL}" -O /tmp/cellframe-node.deb
```

### **2. Environment Properties**
```properties
NODE_DOWNLOAD_URL=https://internal-pub.cellframe.net/linux/cellframe-node/hotfix-mem/cellframe-node-5.5-356-amd64.deb
DEBIAN_VERSION=24.04
PYTHON_VERSION=3.12.3
PYTEST_VERSION=8.4.2
ALLURE_VERSION=2.24.1
```

### **3. TestOps Launch Name**
```
QA Tests - 14.10.2024_15:30 - cellframe-node-5.5-356-amd64 - v4caa190f
```
- ✅ Включает дату/время
- ✅ Включает версию ноды из URL
- ✅ Включает commit hash

## 🎯 **Преимущества**

### **1. Гибкость тестирования**
- ✅ Тестирование hotfix веток
- ✅ Тестирование feature веток  
- ✅ Тестирование bugfix веток
- ✅ Тестирование любых кастомных сборок

### **2. Трассируемость**
- ✅ URL сохраняется в environment.properties
- ✅ Версия отображается в launch name
- ✅ Полная история в TestOps

### **3. Удобство использования**
- ✅ Работает из TestOps
- ✅ Работает из GitLab UI
- ✅ Работает через API
- ✅ По умолчанию использует latest

## 🔍 **Примеры использования**

### **Тестирование hotfix**
```bash
NODE_DOWNLOAD_URL="https://internal-pub.cellframe.net/linux/cellframe-node/hotfix-mem/cellframe-node-5.5-356-amd64.deb"
```
**Результат**: Тестируется hotfix для проблем с памятью

### **Тестирование feature**
```bash
NODE_DOWNLOAD_URL="https://internal-pub.cellframe.net/linux/cellframe-node/feature-18831/cellframe-node-5.5-357-amd64.deb"
```
**Результат**: Тестируется новая функциональность

### **Тестирование bugfix**
```bash
NODE_DOWNLOAD_URL="https://internal-pub.cellframe.net/linux/cellframe-node/bugfix-18923/cellframe-node-5.4-359-amd64.deb"
```
**Результат**: Тестируется исправление бага

## 📈 **Мониторинг и отчетность**

### **В TestOps будет видно:**
- 📊 Какая версия ноды тестировалась
- 📈 Результаты тестов для каждой версии
- 🔍 Сравнение между версиями
- 📝 История тестирования веток

### **В GitLab CI будет видно:**
- 🔗 Какой URL использовался
- 📦 Какая версия скачалась
- ✅ Результаты установки и тестов

## 🚨 **Важные замечания**

1. **URL должен быть доступен** из GitLab CI runners
2. **Файл должен быть .deb пакетом** для Ubuntu/Debian
3. **Версия отображается в отчетах** для трассируемости
4. **По умолчанию используется latest** если URL не задан

## 🎯 **Следующие шаги**

1. ✅ Протестировать с кастомной ссылкой
2. 📚 Обучить тестировщиков использованию
3. 🔄 Настроить автоматические тесты для веток
4. 📊 Настроить дашборды в TestOps
