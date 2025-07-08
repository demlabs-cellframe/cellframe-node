#!/bin/bash

# 📦 Smart Layered Context v2.0 - Создание архива для развертывания
# Версия: 2.0
# Создает готовый к развертыванию архив SLK v2.0

set -e  # Выход при ошибке

# Цвета для вывода
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Настройки
ARCHIVE_NAME="smart-layered-context-v2.0"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONTEXT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
PROJECT_ROOT="$(cd "$CONTEXT_DIR/.." && pwd)"

echo -e "${BLUE}📦 Smart Layered Context v2.0 - Archive Creator${NC}"
echo -e "${BLUE}Creating production-ready archive...${NC}"
echo ""

# Проверка что мы в правильной директории
if [[ ! -f "$CONTEXT_DIR/core/manifest.json" ]]; then
    echo -e "${RED}❌ Ошибка: manifest.json не найден в $CONTEXT_DIR/core/${NC}"
    echo "Убедитесь что скрипт запущен из context/ директории"
    exit 1
fi

# Создание временной директории для архива
TEMP_DIR=$(mktemp -d)
ARCHIVE_DIR="$TEMP_DIR/$ARCHIVE_NAME"
mkdir -p "$ARCHIVE_DIR"

echo -e "${YELLOW}📂 Создание структуры архива...${NC}"

# Создание структуры директорий
mkdir -p "$ARCHIVE_DIR"/{core,modules,tasks,tools,docs}
mkdir -p "$ARCHIVE_DIR/tasks/templates"
mkdir -p "$ARCHIVE_DIR/tools"/{scripts,deployment,templates}

# Копирование основных файлов
echo -e "${YELLOW}📋 Копирование основных файлов...${NC}"

# Core files
cp "$CONTEXT_DIR/core/manifest.json" "$ARCHIVE_DIR/core/"
cp "$CONTEXT_DIR/core/standards.json" "$ARCHIVE_DIR/core/"
cp "$CONTEXT_DIR/core/project.json" "$ARCHIVE_DIR/core/"

# Modules
cp -r "$CONTEXT_DIR/modules/" "$ARCHIVE_DIR/modules/"

# Tasks (создаем шаблонные версии)
touch "$ARCHIVE_DIR/tasks/"
cp "$CONTEXT_DIR/tasks/templates"/* "$ARCHIVE_DIR/tasks/templates/" 2>/dev/null || true

# Создание шаблонной активной задачи
cat > "$ARCHIVE_DIR/tasks/active.json" << 'EOF'
{
    "project": "Ваш проект",
    "version": "1.0",
    "phase": "НАЧАЛЬНАЯ НАСТРОЙКА",
    "completion": "0%",
    "status": "ПРОЕКТ СОЗДАН - ГОТОВ К РАБОТЕ",
    "timestamp": "2024-12-28T21:00:00Z",
    "last_updated": "2024-12-28 21:00:00",
    
    "discovery": {
        "title": "ПРОЕКТ УСПЕШНО ИНИЦИАЛИЗИРОВАН",
        "summary": "Smart Layered Context v2.0 развернут и готов к использованию",
        "impact": "Эффективное взаимодействие с ИИ настроено"
    },
    
    "current_focus": {
        "title": "Настройка проекта под ваши нужды",
        "tasks": [
            "Обновить project.json с информацией о вашем проекте",
            "Настроить стандарты кодирования в standards.json",
            "Создать первую реальную задачу",
            "Протестировать загрузку контекста"
        ]
    }
}
EOF

# Tools - Scripts
cp "$CONTEXT_DIR/tools/scripts/smart_context_loader.sh" "$ARCHIVE_DIR/tools/scripts/"
cp "$CONTEXT_DIR/tools/scripts/new_task.sh" "$ARCHIVE_DIR/tools/scripts/"

# Tools - Deployment
cp "$CONTEXT_DIR/tools/deployment/deploy_new_context.sh" "$ARCHIVE_DIR/tools/deployment/"

# Tools - Templates
cp "$CONTEXT_DIR/tools/templates"/* "$ARCHIVE_DIR/tools/templates/" 2>/dev/null || true

# Documentation
cp -r "$CONTEXT_DIR/docs/" "$ARCHIVE_DIR/docs/"

# Копирование скрипта создания архива (для референса)
cp "$0" "$ARCHIVE_DIR/tools/deployment/"

echo -e "${YELLOW}🔧 Настройка разрешений...${NC}"

# Установка исполнимых разрешений
chmod +x "$ARCHIVE_DIR/tools/scripts"/*.sh
chmod +x "$ARCHIVE_DIR/tools/deployment"/*.sh

echo -e "${YELLOW}📝 Создание версионного файла...${NC}"

# Создание файла версии
cat > "$ARCHIVE_DIR/VERSION" << EOF
Smart Layered Context v2.0
Created: $(date)
Timestamp: $TIMESTAMP

Components:
- Intelligent context navigation (manifest.json)
- Unified coding standards
- Modular architecture 
- Task management system
- Cross-platform automation scripts (Linux/macOS)
- Complete documentation

Archive contents:
$(find "$ARCHIVE_DIR" -type f | wc -l) files
$(du -sh "$ARCHIVE_DIR" | cut -f1) total size

Ready for deployment in any development project.
EOF

echo -e "${YELLOW}📜 Создание README для архива...${NC}"

# Создание README для архива
cat > "$ARCHIVE_DIR/README.md" << 'EOF'
# 🚀 Smart Layered Context v2.0

## Быстрое развертывание

```bash
# 1. Распаковать в корень проекта
tar -xzf smart-layered-context-v2.0.tar.gz

# 2. Автоматическая настройка
cd context
chmod +x tools/deployment/deploy_new_context.sh
./tools/deployment/deploy_new_context.sh --auto

# 3. Первое использование
./tools/scripts/smart_context_loader.sh "hello world"
```

## Документация

- 📖 `README_DEPLOYMENT.md` - Полная инструкция по развертыванию
- 📋 `docs/user_guide.md` - Подробное руководство пользователя

## Поддержка

- ✅ Linux, macOS
- ✅ Автоматическое развертывание
- ✅ Кроссплатформенные скрипты
- ✅ Без интерактивных промптов

**Начните с**: `./tools/scripts/smart_context_loader.sh "start"`
EOF

echo -e "${YELLOW}📦 Создание архивов...${NC}"

# Переход в директорию с архивом
cd "$TEMP_DIR"

# Создание tar.gz архива
echo -e "${BLUE}Creating tar.gz archive...${NC}"
tar -czf "${ARCHIVE_NAME}.tar.gz" "$ARCHIVE_NAME"

# Создание zip архива  
echo -e "${BLUE}Creating zip archive...${NC}"
zip -r "${ARCHIVE_NAME}.zip" "$ARCHIVE_NAME" > /dev/null

# Перемещение архивов в проект
mv "${ARCHIVE_NAME}.tar.gz" "$PROJECT_ROOT/"
mv "${ARCHIVE_NAME}.zip" "$PROJECT_ROOT/"

# Информация об архивах
TAR_SIZE=$(du -h "$PROJECT_ROOT/${ARCHIVE_NAME}.tar.gz" | cut -f1)
ZIP_SIZE=$(du -h "$PROJECT_ROOT/${ARCHIVE_NAME}.zip" | cut -f1)

echo ""
echo -e "${GREEN}✅ Архивы успешно созданы:${NC}"
echo -e "${BLUE}📦 $PROJECT_ROOT/${ARCHIVE_NAME}.tar.gz${NC} (${TAR_SIZE})"
echo -e "${BLUE}📦 $PROJECT_ROOT/${ARCHIVE_NAME}.zip${NC} (${ZIP_SIZE})"
echo ""

echo -e "${GREEN}📊 Статистика архива:${NC}"
echo -e "   📁 Файлов: $(find "$ARCHIVE_DIR" -type f | wc -l)"
echo -e "   📏 Размер: $(du -sh "$ARCHIVE_DIR" | cut -f1)"
echo -e "   🗂️  Структура:"

# Показать структуру архива
cd "$ARCHIVE_DIR"
tree . -L 3 2>/dev/null || find . -type d | head -20

echo ""
echo -e "${GREEN}🚀 Готово к развертыванию!${NC}"
echo ""
echo -e "${YELLOW}Для развертывания на новом проекте:${NC}"
echo -e "1. ${BLUE}tar -xzf ${ARCHIVE_NAME}.tar.gz${NC}"
echo -e "2. ${BLUE}cd context && ./tools/deployment/deploy_new_context.sh --auto${NC}"
echo -e "3. ${BLUE}./tools/scripts/smart_context_loader.sh \"hello world\"${NC}"

# Очистка временной директории
rm -rf "$TEMP_DIR"

echo ""
echo -e "${GREEN}🎉 Smart Layered Context v2.0 готов к распространению!${NC}" 
