# 🚫 .gitignore Setup Guide - СЛК v4.0.0

> **Правильная настройка .gitignore для проектов с Smart Layered Context**

[![Git](https://img.shields.io/badge/git-configuration-orange.svg)]() [![Best Practice](https://img.shields.io/badge/best%20practice-✓-green.svg)]()

---

## 🎯 Зачем нужно исключать .context/ из git?

### ❌ Проблемы при включении .context/ в репозиторий
1. **Конфликты версий** - разные разработчики используют разные версии СЛК
2. **Персональные настройки** - каждый адаптирует систему под себя
3. **Размер репозитория** - СЛК может содержать 50+ МБ данных
4. **Частые изменения** - система обновляется независимо от кода

### ✅ Преимущества исключения .context/
1. **Чистый репозиторий** - только код проекта
2. **Гибкость команды** - каждый использует удобную версию СЛК
3. **Производительность** - быстрые клонирование и push
4. **Безопасность** - локальные конфиги не попадают в общий доступ

---

## 🔧 Быстрая настройка

### 📋 Copy-Paste конфигурация

```gitignore
# Smart Layered Context - AI Development Assistant
# Исключаем из версионирования для гибкости команды
.context/
.slc/

# Бэкапы и кэши СЛК
*.slc_backup
.slc_cache/
.slc_temp/
*.slc_log

# Персональные настройки разработчика
.slc_user_config
.context_user_settings
```

### 🚀 Промпт для Cursor AI

```
📋 НАСТРОЙКА .GITIGNORE ДЛЯ СЛК:
Добавь в .gitignore правильные исключения для Smart Layered Context:

1. Скопируй эти строки в .gitignore:
   # Smart Layered Context - AI Development Assistant
   .context/
   .slc/
   *.slc_backup
   .slc_cache/
   .slc_temp/
   *.slc_log
   .slc_user_config
   .context_user_settings

2. Объясни почему это важно для командной работы
3. Покажи как проверить что исключение работает
```

---

## 📁 Полные конфигурации по языкам

### 🐍 Python проект с СЛК

```gitignore
# Smart Layered Context
.context/
.slc/
*.slc_backup
.slc_cache/
.slc_temp/
*.slc_log
.slc_user_config
.context_user_settings

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual environments
venv/
env/
ENV/
env.bak/
venv.bak/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Logs
*.log
logs/

# Environment variables
.env
.env.local
.env.*.local

# Testing
.coverage
.pytest_cache/
htmlcov/

# Documentation builds
docs/_build/
```

### 🌐 JavaScript/Node.js проект с СЛК

```gitignore
# Smart Layered Context
.context/
.slc/
*.slc_backup
.slc_cache/
.slc_temp/
*.slc_log
.slc_user_config
.context_user_settings

# Node.js
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*
lerna-debug.log*

# Runtime data
pids
*.pid
*.seed
*.pid.lock

# Coverage directory used by tools like istanbul
coverage/
*.lcov

# Build outputs
dist/
build/
.next/
.nuxt/

# Environment variables
.env
.env.local
.env.development.local
.env.test.local
.env.production.local

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
.DS_Store?
._*
Thumbs.db

# Logs
logs
*.log
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Package manager
.pnpm-debug.log*
.yarn/cache
.yarn/unplugged
.yarn/build-state.yml
.yarn/install-state.gz
.pnp.*
```

### ⚙️ C/C++ проект с СЛК

```gitignore
# Smart Layered Context
.context/
.slc/
*.slc_backup
.slc_cache/
.slc_temp/
*.slc_log
.slc_user_config
.context_user_settings

# C/C++
# Prerequisites
*.d

# Object files
*.o
*.ko
*.obj
*.elf

# Linker output
*.ilk
*.map
*.exp

# Precompiled Headers
*.gch
*.pch

# Libraries
*.lib
*.a
*.la
*.lo

# Shared objects (inc. Windows DLLs)
*.dll
*.so
*.so.*
*.dylib

# Executables
*.exe
*.out
*.app
*.i*86
*.x86_64
*.hex

# Debug files
*.dSYM/
*.su
*.idb
*.pdb

# Build directories
build/
debug/
release/
bin/
obj/

# CMake
CMakeCache.txt
CMakeFiles/
CMakeScripts/
Makefile
cmake_install.cmake
install_manifest.txt
compile_commands.json
CTestTestfile.cmake

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
```

---

## 🔍 Проверка настройки

### ✅ Проверочные команды

```bash
# Проверить что .context/ игнорируется
git status

# Должно быть пусто или без упоминания .context/
```

### 📋 Промпт для проверки

```
📋 ПРОВЕРКА .GITIGNORE:
Проверь что .gitignore правильно настроен для Smart Layered Context:

1. Выполни команду: git status
2. Убедись что папка .context/ не отображается в untracked files
3. Если видишь .context/ - значит настройка неправильная
4. Покажи статус git и объясни результат
```

---

## 👥 Работа в команде

### 📖 Инструкции для команды

#### Создание README секции

```markdown
## 🔧 Настройка разработки

### Smart Layered Context
Этот проект использует Smart Layered Context для AI-ассистированной разработки.

1. **Установите СЛК:**
   ```bash
   # Скачайте в папку .context
   wget https://github.com/slc/archive/latest.tar.gz
   tar -xzf latest.tar.gz -C .context
   ```

2. **Проверьте .gitignore:**
   - Папка `.context/` должна быть исключена из git
   - Персональные настройки не синхронизируются

3. **Начните работу:**
   ```bash
   # Загрузите контекст для проекта
   .context/tools/scripts/slc_cli.py load-context "наш проект"
   ```
```

### 🔄 Синхронизация настроек команды

#### Рекомендуемый подход
1. **Базовые настройки** - в отдельном репозитории команды
2. **Персональная кастомизация** - локально у каждого
3. **Обновления СЛК** - независимо от проекта

#### Структура проекта команды
```
team_project/
├── .gitignore              # Исключает .context/
├── README.md               # Инструкции по СЛК
├── docs/
│   └── slc-team-guide.md   # Командные настройки СЛК
├── src/                    # Код проекта
└── .context/               # Локально у каждого (не в git)
    ├── modules/
    ├── tools/
    └── team-config/        # Ссылка на командные настройки
```

---

## ⚡ Автоматизация настройки

### 🛠️ Скрипт инициализации

```bash
#!/bin/bash
# setup-slc-gitignore.sh - Автоматическая настройка .gitignore для СЛК

echo "🔧 Настройка .gitignore для Smart Layered Context..."

# Создаем или дополняем .gitignore
cat >> .gitignore << 'EOF'

# Smart Layered Context - AI Development Assistant
# Исключаем из версионирования для гибкости команды
.context/
.slc/
*.slc_backup
.slc_cache/
.slc_temp/
*.slc_log
.slc_user_config
.context_user_settings
EOF

echo "✅ .gitignore обновлен для СЛК"

# Проверяем результат
if git check-ignore .context/ >/dev/null 2>&1; then
    echo "✅ Проверка: .context/ правильно исключена"
else
    echo "⚠️  Внимание: .context/ может не исключаться"
fi

echo "🎉 Настройка завершена!"
```

### 📋 Промпт для автоматизации

```
📋 АВТОМАТИЧЕСКАЯ НАСТРОЙКА .GITIGNORE:
Создай и выполни скрипт для автоматической настройки .gitignore:

1. Создай файл setup-slc-gitignore.sh
2. Добавь необходимые исключения для СЛК
3. Выполни скрипт: bash setup-slc-gitignore.sh
4. Проверь что всё работает командой git status
5. Покажи результат
```

---

## 🆘 Решение проблем

### ❌ Типичные ошибки

#### ".context/ уже в репозитории"
```bash
# Удалить из git (но сохранить локально)
git rm -r --cached .context/
echo ".context/" >> .gitignore
git add .gitignore
git commit -m "Add .context/ to .gitignore"
```

#### "Конфликты при merge"
```bash
# Если .context/ была закоммичена ранее
git reset --hard HEAD~1  # ОСТОРОЖНО: потеряете последний коммит
# Или сделайте revert commit
```

#### "Команда использует разные версии СЛК"
```bash
# Решение: документируйте рекомендуемую версию в README
echo "Рекомендуемая версия СЛК: v4.0.0" >> README.md
```

### 📋 Промпты для решения проблем

#### Удаление .context/ из репозитория
```
📋 УДАЛЕНИЕ .context/ ИЗ GIT:
Помоги убрать .context/ из git репозитория:

1. Выполни: git rm -r --cached .context/
2. Проверь что .context/ в .gitignore
3. Закоммить изменения: git add .gitignore && git commit -m "Remove .context from tracking"
4. Проверь что папка больше не отслеживается
5. Объясни что произошло
```

---

## 📚 Дополнительные ресурсы

### 🔗 Полезные ссылки
- [Git documentation on .gitignore](https://git-scm.com/docs/gitignore)
- [GitHub .gitignore templates](https://github.com/github/gitignore)
- [Cursor IDE Quick Start](cursor-quick-start.md)

### 💡 Best Practices
1. **Регулярно обновляйте** .gitignore при добавлении новых инструментов
2. **Документируйте специфичные исключения** в README проекта
3. **Проверяйте после настройки** командой `git status`
4. **Обучите команду** правильному использованию СЛК

---

**🎯 Правильная настройка .gitignore = счастливая команда разработчиков!**

> **Помните:** СЛК должна помогать разработке, а не создавать проблемы в репозитории. 