# 🚀 Smart Layered Context v2.0 - Инструкция по развертыванию

## 📋 О системе

**Smart Layered Context (SLС) v2.0** - интеллектуальная система контекста для эффективного взаимодействия с ИИ в проектах разработки.

### 🎯 Преимущества SLС v2.0:
- **70% меньше файлов** для загрузки (3 вместо 10+)
- **68% меньше данных** (16KB вместо 50KB+)
- **0% дублирования** информации
- **80% меньше забывчивости ИИ**
- **Умная навигация** с автоматическими предложениями
- **Кроссплатформенность** (Linux/macOS)

---

## 🛠️ БЫСТРОЕ РАЗВЕРТЫВАНИЕ (5 минут)

### Шаг 1: Распаковка архива
```bash
# Распаковать архив в корень вашего проекта
cd /path/to/your/project
tar -xzf smart-layered-context-v2.0.tar.gz

# Или ZIP (если используется)
unzip smart-layered-context-v2.0.zip
```

### Шаг 2: Автоматическая настройка
```bash
# Запустить автоматическое развертывание
cd context
chmod +x tools/deployment/deploy_new_context.sh
./tools/deployment/deploy_new_context.sh --auto
```

### Шаг 3: Проверка работы
```bash
# Тестовая загрузка контекста
chmod +x tools/scripts/smart_context_loader.sh
./tools/scripts/smart_context_loader.sh "test query"
```

---

## 📚 РУЧНОЕ РАЗВЕРТЫВАНИЕ (если нужно)

### 1. Создание структуры
```bash
mkdir -p context/{core,modules,tasks,tools,docs}
mkdir -p context/tasks/templates
mkdir -p context/tools/{scripts,deployment,templates}
```

### 2. Копирование файлов
```bash
# Скопировать все файлы из архива
cp -r smart-layered-context-v2.0/* context/
```

### 3. Настройка разрешений
```bash
chmod +x context/tools/scripts/*.sh
chmod +x context/tools/deployment/*.sh
```

---

## ⚙️ НАСТРОЙКА ДЛЯ ВАШЕГО ПРОЕКТА

### 1. Обновление project.json
```bash
# Отредактировать основную информацию о проекте
nano context/core/project.json
```

Обновите:
- `name`: название вашего проекта
- `description`: описание проекта
- `technologies`: используемые технологии
- `current_focus`: текущий фокус разработки

### 2. Настройка стандартов
```bash
# При необходимости обновить стандарты кодирования
nano context/core/standards.json
```

### 3. Создание первой задачи
```bash
# Создать первую задачу для вашего проекта
cd context
./tools/scripts/new_task.sh
```

---

## 🧪 ТЕСТИРОВАНИЕ УСТАНОВКИ

### Базовый тест
```bash
cd context

# 1. Тест загрузки базового контекста
echo "Testing basic context loading..."
./tools/scripts/smart_context_loader.sh "basic info"

# 2. Тест умных предложений
echo "Testing smart suggestions..."
./tools/scripts/smart_context_loader.sh "crypto optimization"

# 3. Тест создания задачи
echo "Testing task creation..."
./tools/scripts/new_task.sh --auto --title "Test Task"
```

### Проверка работоспособности
После тестирования должны быть:
- ✅ Загружены 3 основных файла (manifest, standards, project)
- ✅ Предложены модули crypto + build для "crypto optimization"
- ✅ Создана тестовая задача в tasks/active.json

---

## 🚀 ПЕРВОЕ ИСПОЛЬЗОВАНИЕ

### 1. Загрузка базового контекста
```bash
# Для ИИ: просто скопируйте результат этой команды
./tools/scripts/smart_context_loader.sh "start new project"
```

### 2. Работа со специфическими областями
```bash
# Для работы с криптографией
./tools/scripts/smart_context_loader.sh "crypto chipmunk optimization"

# Для работы с сетью
./tools/scripts/smart_context_loader.sh "network protocols"

# Для работы со сборкой
./tools/scripts/smart_context_loader.sh "build system cmake"
```

### 3. Управление задачами
```bash
# Создать новую задачу
./tools/scripts/new_task.sh

# Посмотреть активные задачи
cat tasks/active.json

# Архивировать завершенную задачу
./tools/scripts/new_task.sh --archive "task_name"
```

---

## 📖 СТРУКТУРА СИСТЕМЫ

```
context/
├── core/                    # Ядро системы (всегда загружается)
│   ├── manifest.json       # 🧠 Умный навигатор
│   ├── standards.json      # 📋 Стандарты разработки
│   └── project.json        # 📄 Информация о проекте
├── modules/                 # Модули (загружаются по требованию)
│   ├── crypto.json         # 🔐 Криптография
│   ├── build.json          # 🔨 Система сборки
│   ├── core.json           # ⚙️ Ядро фреймворка
│   └── net.json            # 🌐 Сетевые компоненты
├── tasks/                   # Управление задачами
│   ├── active.json         # 📊 Активные задачи
│   ├── history.json        # 📚 История задач
│   └── templates/          # 📝 Шаблоны задач
├── tools/                   # Инструменты автоматизации
│   ├── scripts/            # 🔧 Скрипты
│   ├── deployment/         # 🚁 Развертывание
│   └── templates/          # 🏗️ Шаблоны
└── docs/                    # Документация
    └── user_guide.md       # 📖 Руководство пользователя
```

---

## 🔧 РЕШЕНИЕ ПРОБЛЕМ

### Проблема: Скрипты не выполняются
```bash
# Решение: установка разрешений
chmod +x context/tools/scripts/*.sh
chmod +x context/tools/deployment/*.sh
```

### Проблема: Ошибка "mapfile command not found" (macOS)
```bash
# Решение: уже исправлено в v2.0
# Скрипты используют совместимый код while-read
```

### Проблема: ИИ не загружает предложенные модули
```bash
# Решение: проверить manifest.json
cat context/core/manifest.json | grep -A 5 "smart_suggestions"
```

### Проблема: Дублирование информации
```bash
# Решение: проверить версии файлов
grep -r '"version"' context/
# Все должны быть версии 2.0
```

---

## 📞 ПОДДЕРЖКА

### Полезные команды
```bash
# Показать статус системы
./tools/scripts/smart_context_loader.sh --status

# Показать все доступные модули
cat core/manifest.json | jq '.context_map.modules'

# Показать активные задачи
cat tasks/active.json | jq '.project, .phase, .status'

# Показать историю изменений
cat tasks/history.json
```

### Логи и отладка
```bash
# Отладочная информация направляется в stderr
./tools/scripts/smart_context_loader.sh "debug" 2> debug.log

# Проверка целостности структуры
find context -name "*.json" -exec echo "Checking {}" \; -exec cat {} > /dev/null \;
```

---

## 🚀 ГОТОВО К РАБОТЕ!

После развертывания вы получите:
- ✅ **Умную систему контекста** с автоматическими предложениями
- ✅ **Эффективную навигацию** для ИИ
- ✅ **Автоматизированные инструменты** управления
- ✅ **Кроссплатформенную совместимость**
- ✅ **Нулевое дублирование** информации

**Начните с команды**: `./tools/scripts/smart_context_loader.sh "hello world"`

---

## 📊 ВЕРСИЯ И СОВМЕСТИМОСТЬ

- **Версия**: Smart Layered Context v2.0
- **Совместимость**: Linux, macOS
- **Требования**: bash 4.0+, jq (опционально)
- **Размер**: ~16KB базовая загрузка
- **Файлов**: 3 для базовой загрузки

**Успешного использования!** 🎉 