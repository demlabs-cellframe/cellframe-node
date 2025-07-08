#!/bin/bash

# 📦 Smart Layered Context v4.1.2 - Создание архива для развертывания
# Версия: 4.1.2
# Создает готовый к развертыванию архив SLC v4.1.2 с чистой архитектурой

set -e  # Выход при ошибке

# Цвета для вывода
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Настройки
VERSION="4.1.2"
ARCHIVE_NAME="smart-layered-context-v${VERSION}"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONTEXT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
PROJECT_ROOT="$(cd "$CONTEXT_DIR/.." && pwd)"

echo -e "${BLUE}📦 Smart Layered Context v${VERSION} - Archive Creator${NC}"
echo -e "${BLUE}Creating production-ready archive with clean architecture...${NC}"
echo ""

# Проверка что мы в правильной директории
if [[ ! -f "$CONTEXT_DIR/manifest.json" ]]; then
    echo -e "${RED}❌ Ошибка: manifest.json не найден в $CONTEXT_DIR/${NC}"
    echo "Убедитесь что скрипт запущен из правильной директории"
    exit 1
fi

# Создание временной директории для архива
TEMP_DIR=$(mktemp -d)
ARCHIVE_DIR="$TEMP_DIR/$ARCHIVE_NAME"
mkdir -p "$ARCHIVE_DIR"

echo -e "${YELLOW}📂 Создание структуры архива v${VERSION}...${NC}"

# Создание полной структуры .context
mkdir -p "$ARCHIVE_DIR/.context"

# Копирование основных файлов
echo -e "${YELLOW}📋 Копирование системных файлов...${NC}"

# Главный манифест
cp "$CONTEXT_DIR/manifest.json" "$ARCHIVE_DIR/.context/"

# Создаем структуру директорий принудительно
mkdir -p "$ARCHIVE_DIR/.context/modules"
mkdir -p "$ARCHIVE_DIR/.context/tools"
mkdir -p "$ARCHIVE_DIR/.context/docs"
mkdir -p "$ARCHIVE_DIR/.context/tests"

# Modules - ТОЛЬКО правильная структура шаблонов
echo -e "   📁 Копирование modules (шаблоны)..."
if [[ -d "$CONTEXT_DIR/modules" ]] && [[ -n "$(ls -A "$CONTEXT_DIR/modules" 2>/dev/null)" ]]; then
    cp -r "$CONTEXT_DIR/modules"/* "$ARCHIVE_DIR/.context/modules/"
    echo -e "      ✅ Скопировано шаблонов: $(find "$ARCHIVE_DIR/.context/modules" -name "*.json" | wc -l)"
else
    echo -e "      ❌ Modules пустые или не найдены"
fi

# Tools - CLI система полностью
echo -e "   🛠️  Копирование tools (CLI система)..."
if [[ -d "$CONTEXT_DIR/tools" ]] && [[ -n "$(ls -A "$CONTEXT_DIR/tools" 2>/dev/null)" ]]; then
    cp -r "$CONTEXT_DIR/tools"/* "$ARCHIVE_DIR/.context/tools/"
    echo -e "      ✅ Скопировано CLI файлов: $(find "$ARCHIVE_DIR/.context/tools" -name "*.py" | wc -l)"
else
    echo -e "      ❌ Tools пустые или не найдены"
fi

# Docs - полностью  
echo -e "   📚 Копирование docs..."
if [[ -d "$CONTEXT_DIR/docs" ]] && [[ -n "$(ls -A "$CONTEXT_DIR/docs" 2>/dev/null)" ]]; then
    cp -r "$CONTEXT_DIR/docs"/* "$ARCHIVE_DIR/.context/docs/"
    echo -e "      ✅ Скопировано docs"
else
    echo -e "      ❌ Docs пустые или не найдены"
fi

# Tests - полностью
echo -e "   🧪 Копирование tests..."
if [[ -d "$CONTEXT_DIR/tests" ]] && [[ -n "$(ls -A "$CONTEXT_DIR/tests" 2>/dev/null)" ]]; then
    cp -r "$CONTEXT_DIR/tests"/* "$ARCHIVE_DIR/.context/tests/"
    echo -e "      ✅ Скопировано tests"
else
    echo -e "      ❌ Tests пустые или не найдены"
fi

# НЕ копируем промежуточные папки из старой структуры
echo -e "   🚫 Исключаем устаревшие папки..."
# Удаляем промежуточные папки если они попали (НО НЕ modules, docs, tools, tests, tasks!)
rm -rf "$ARCHIVE_DIR/.context/ai_ml" 2>/dev/null || true
rm -rf "$ARCHIVE_DIR/.context/cli" 2>/dev/null || true  
rm -rf "$ARCHIVE_DIR/.context/cli_modules" 2>/dev/null || true
rm -rf "$ARCHIVE_DIR/.context/core" 2>/dev/null || true
rm -rf "$ARCHIVE_DIR/.context/deployment" 2>/dev/null || true
rm -rf "$ARCHIVE_DIR/.context/developer" 2>/dev/null || true
rm -rf "$ARCHIVE_DIR/.context/languages" 2>/dev/null || true
rm -rf "$ARCHIVE_DIR/.context/legacy" 2>/dev/null || true
rm -rf "$ARCHIVE_DIR/.context/methodologies" 2>/dev/null || true
rm -rf "$ARCHIVE_DIR/.context/networking_communication" 2>/dev/null || true
rm -rf "$ARCHIVE_DIR/.context/projects" 2>/dev/null || true
rm -rf "$ARCHIVE_DIR/.context/releases" 2>/dev/null || true
rm -rf "$ARCHIVE_DIR/.context/scripts" 2>/dev/null || true
rm -rf "$ARCHIVE_DIR/.context/user" 2>/dev/null || true
# Удаляем старые JSON файлы из корня .context (НО НЕ manifest.json и НЕ основные файлы)
rm -f "$ARCHIVE_DIR/.context/core_foundation.json" 2>/dev/null || true
rm -f "$ARCHIVE_DIR/.context/decision_logging_system.json" 2>/dev/null || true  
rm -f "$ARCHIVE_DIR/.context/networking_communication.json" 2>/dev/null || true
# Удаляем markdown файлы (кроме README.md в корне архива)
find "$ARCHIVE_DIR/.context" -maxdepth 1 -name "*.md" -delete 2>/dev/null || true
# Удаляем python файлы
find "$ARCHIVE_DIR/.context" -maxdepth 1 -name "*.py" -delete 2>/dev/null || true

# Tasks - ТОЛЬКО пустая структура
echo -e "   📋 Создание чистой структуры tasks..."
mkdir -p "$ARCHIVE_DIR/.context/tasks"
mkdir -p "$ARCHIVE_DIR/.context/tasks/templates"
mkdir -p "$ARCHIVE_DIR/.context/tasks/completed"
mkdir -p "$ARCHIVE_DIR/.context/tasks/analysis"

# Создание пустого active.json
cat > "$ARCHIVE_DIR/.context/tasks/active.json" << 'EOF'
{
    "project": "Новый проект",
    "version": "1.0.0",
    "phase": "НАЧАЛЬНАЯ НАСТРОЙКА",
    "completion": "0%",
    "status": "ПРОЕКТ СОЗДАН - ГОТОВ К РАБОТЕ",
    "timestamp": "",
    "last_updated": "",
    
    "discovery": {
        "title": "SMART LAYERED CONTEXT РАЗВЕРНУТ",
        "summary": "Система готова к использованию. Обновите информацию о проекте в manifest.json",
        "impact": "Эффективное взаимодействие с AI настроено"
    },
    
    "current_focus": {
        "title": "Настройка проекта под ваши нужды",
        "tasks": [
            "Обновить информацию о проекте в .context/manifest.json",
            "Настроить стандарты в .context/modules/core/standards.json",
            "Создать первую реальную задачу",
            "Протестировать команды: ./slc help"
        ]
    }
}
EOF

# Создание пустого history.json
cat > "$ARCHIVE_DIR/.context/tasks/history.json" << 'EOF'
{
    "task_history": [],
    "total_tasks": 0,
    "last_completed": null,
    "created": "",
    "note": "История задач будет заполняться автоматически при работе с системой"
}
EOF

# Копирование исполняемого файла slc
echo -e "   🚀 Копирование slc..."
cp "$PROJECT_ROOT/slc" "$ARCHIVE_DIR/"

# Копирование .cursorrules
echo -e "   📝 Копирование .cursorrules..."
cp "$PROJECT_ROOT/.cursorrules" "$ARCHIVE_DIR/"

# НЕ копируем archives - это локальные данные
echo -e "   🚫 Пропускаем archives/ (локальные данные)..."

# Другие системные файлы если есть
for file in ".slc_usage_stats.json" "template_intelligence.json" "template_patterns.json"; do
    if [[ -f "$CONTEXT_DIR/$file" ]]; then
        echo -e "   📊 Копирование $file..."
        cp "$CONTEXT_DIR/$file" "$ARCHIVE_DIR/.context/"
    fi
done

echo -e "${YELLOW}🔧 Настройка разрешений...${NC}"

# Установка исполнимых разрешений
find "$ARCHIVE_DIR/.context/tools" -name "*.sh" -exec chmod +x {} \;
chmod +x "$ARCHIVE_DIR/slc"

echo -e "${YELLOW}📝 Создание файлов развертывания...${NC}"

# Создание VERSION файла
cat > "$ARCHIVE_DIR/VERSION" << EOF
Smart Layered Context v${VERSION}
Build: $(date +%Y%m%d.%H%M%S)
Created: $(date)

🎯 Ключевые возможности:
- 28 CLI команд с русскими алиасами  
- JSON контекст для AI интеграции
- Система эволюции export/import
- Чистая архитектура (только .context + .cursorrules в корне)
- Zero duplication принцип

📦 Содержимое архива:
- .context/ - Вся система СЛК
- slc - Исполняемый CLI файл
- .cursorrules - Правила для Cursor IDE
- VERSION - Этот файл

🚀 Быстрый старт:
1. Распаковать в корень проекта
2. ./slc help - Показать все команды
3. ./slc list - Показать задачи
4. ./slc templates - Показать шаблоны

Готов к работе!
EOF

# Создание README для развертывания
cat > "$ARCHIVE_DIR/README.md" << 'EOF'
# 🚀 Smart Layered Context v4.1.2

**Система интеллектуального управления контекстом для AI-ассистированной разработки**

## ⚡ Быстрое развертывание

```bash
# 1. Распаковать архив в корень проекта
tar -xzf smart-layered-context-v4.1.2.tar.gz
# или
unzip smart-layered-context-v4.1.2.zip

# 2. Сразу начать работу
./slc help          # Показать все команды
./slc list          # Показать задачи
./slc templates     # Показать шаблоны
```

## 🎯 Основные команды

### Русские команды для AI помощника:
- `слк старт` - Загрузить базовый контекст
- `слк контекст [задача]` - Загрузить контекст для задачи  
- `слк обнови` - Обновить контекст
- `слк список` - Показать задачи
- `слк шаблоны` - Показать шаблоны
- `слк помощь` - Показать все команды

### CLI команды:
- `./slc status` - Статус системы
- `./slc validate` - Проверить целостность  
- `./slc organize` - Организовать файлы
- `./slc export` - Экспорт изменений

## 📁 Структура

```
.context/           # Вся система СЛК
├── manifest.json   # Главный манифест (автозагрузка в Cursor)
├── modules/        # 34 шаблона в 9 категориях
├── tools/          # CLI система (28 команд)
├── tasks/          # Управление задачами
├── docs/           # Документация
└── tests/          # Тесты

slc                 # Исполняемый CLI файл
.cursorrules        # Правила для Cursor IDE
```

## 🧠 AI интеграция

Система автоматически интегрируется с Cursor IDE через `.cursorrules` и предоставляет:
- Автозагрузку контекста через `@.context/manifest.json`
- JSON выходы команд для AI интеграции
- Умные рекомендации на основе анализа проекта

## 📊 Характеристики

- **28 CLI команд** с полной поддержкой русского языка
- **34 шаблона** в 9 категориях (AI/ML, языки, методологии и др.)
- **Система эволюции** для синхронизации между проектами
- **Zero duplication** - единая точка истины
- **Чистая архитектура** - только необходимые файлы в корне

## 🆘 Помощь

- `./slc help` - Полный список команд
- `./slc help [команда]` - Помощь по конкретной команде
- `./slc status` - Проверить состояние системы

**Готов к работе из коробки!** 🎉
EOF

echo -e "${YELLOW}📦 Создание архивов...${NC}"

# Переход в директорию с архивом
cd "$TEMP_DIR"

# Создание tar.gz архива
echo -e "${BLUE}Создание tar.gz архива...${NC}"
tar -czf "${ARCHIVE_NAME}.tar.gz" "$ARCHIVE_NAME"

# Создание zip архива  
echo -e "${BLUE}Создание zip архива...${NC}"
zip -r "${ARCHIVE_NAME}.zip" "$ARCHIVE_NAME" > /dev/null

# Создание директории releases если её нет
RELEASES_DIR="$PROJECT_ROOT/../releases"
mkdir -p "$RELEASES_DIR"

# Перемещение архивов
mv "${ARCHIVE_NAME}.tar.gz" "$RELEASES_DIR/"
mv "${ARCHIVE_NAME}.zip" "$RELEASES_DIR/"

# Информация об архивах
TAR_SIZE=$(du -h "$RELEASES_DIR/${ARCHIVE_NAME}.tar.gz" | cut -f1)
ZIP_SIZE=$(du -h "$RELEASES_DIR/${ARCHIVE_NAME}.zip" | cut -f1)

echo ""
echo -e "${GREEN}✅ Архивы успешно созданы:${NC}"
echo -e "${BLUE}📦 $RELEASES_DIR/${ARCHIVE_NAME}.tar.gz${NC} (${TAR_SIZE})"
echo -e "${BLUE}📦 $RELEASES_DIR/${ARCHIVE_NAME}.zip${NC} (${ZIP_SIZE})"
echo ""

echo -e "${GREEN}📊 Статистика архива v${VERSION}:${NC}"
echo -e "   📁 Файлов: $(find "$ARCHIVE_DIR" -type f | wc -l)"
echo -e "   📏 Размер: $(du -sh "$ARCHIVE_DIR" | cut -f1)"
echo -e "   🗂️  Компоненты:"
echo -e "      • CLI команд: 28"
echo -e "      • Шаблонов: 34"
echo -e "      • Категорий: 9"
echo -e "      • Tasks: чистая структура (active.json + history.json)"
echo -e "      • Archives: исключены (локальные данные)"

echo ""
echo -e "${GREEN}🚀 Готово к развертыванию!${NC}"
echo ""
echo -e "${YELLOW}Для развертывания на новом проекте:${NC}"
echo -e "1. ${BLUE}tar -xzf ${ARCHIVE_NAME}.tar.gz${NC} (или unzip ${ARCHIVE_NAME}.zip)"
echo -e "2. ${BLUE}./slc help${NC} - посмотреть все команды"
echo -e "3. ${BLUE}./slc list${NC} - начать работу с задачами"

# Очистка временной директории
rm -rf "$TEMP_DIR"

echo ""
echo -e "${GREEN}🎉 Smart Layered Context v${VERSION} готов к распространению!${NC}" 