# 🧠 Unified Context Engine - Руководство пользователя

**Единая система автоматической загрузки контекста СЛК v4.0**

---

## 📖 Обзор

Unified Context Engine (UCE) - это революционная система автоматической загрузки контекста, которая объединяет:

- 🤖 **AI-powered анализ запросов** - понимание намерений пользователя
- 🧠 **Интеллектуальные рекомендации** - TF-IDF и семантический анализ  
- 📊 **Adaptive learning** - обучение на основе использования
- ⚡ **Автоматическая загрузка** - 95% случаев без ручного вмешательства

### 🎯 Решаемые проблемы

❌ **БЫЛО (СЛК v3.0):**
- Контекст нужно загружать вручную
- 3 конфликтующих системы загрузки
- Постоянные запросы "загрузи оттуда и оттуда"
- 40-60% времени тратилось на setup

✅ **СТАЛО (СЛК v4.0):**
- Автоматическая загрузка в 95% случаев
- Единая интеллектуальная система
- Готовые команды для копирования в чат
- Время setup < 30 секунд

---

## 🚀 Быстрый старт

### Базовое использование

```bash
# Автоматическая загрузка контекста
python3 tools/scripts/slc_cli.py load-context "создать AI chatbot"

# Подробный анализ с рекомендациями  
python3 tools/scripts/slc_cli.py load-context "python ML проект" --verbose

# Загрузка полного контекста
python3 tools/scripts/slc_cli.py load-context "всё" --strategy full
```

### Результат - готовые команды для ИИ

```
📥 СКОПИРУЙТЕ И ВСТАВЬТЕ В ЧАТ С ИИ:
==================================================

🏠 Core система:
cat core/manifest.json
cat core/standards.json
cat core/project.json

📚 Модули:  
cat modules/ai_ml/prompt_engineering.json
cat modules/languages/python/python_development.json

==================================================
✅ Готово! Контекст из 5 файлов загружен
```

---

## 🎛️ Команды и опции

### Основная команда

```bash
slc_cli.py load-context <запрос> [опции]
```

### Стратегии загрузки

| Стратегия | Описание | Когда использовать |
|-----------|----------|-------------------|
| `auto` (по умолчанию) | AI-powered автоматическая | Большинство случаев |
| `pattern` | На основе ключевых слов | Технические запросы |
| `manual` | Минимальный набор + предложения | Неясные задачи |
| `full` | Загрузить всё | Комплексная работа |

### Форматы вывода

| Формат | Описание | Пример использования |
|--------|----------|-------------------|
| `copy` (по умолчанию) | Готовые команды для ИИ | Работа с ассистентом |
| `list` | Простой список файлов | Скрипты и автоматизация |
| `json` | Структурированные данные | API интеграция |

### Полный список опций

```bash
slc_cli.py load-context "запрос" [опции]

Опции:
  --strategy {auto,pattern,manual,full}  Стратегия загрузки
  --max-modules INT                      Максимум модулей (по умолчанию: 10)
  --no-core                             Не загружать core файлы  
  --no-tasks                            Не загружать задачи
  --format {list,json,copy}             Формат вывода
  --verbose                             Подробный анализ
  --save-result FILE                    Сохранить в файл
```

---

## 💡 Примеры использования

### AI/ML разработка

```bash
# Создание ML проекта
slc_cli.py load-context "создать машинное обучение проект"

# Prompt engineering
slc_cli.py load-context "оптимизация промптов для LLM"

# Fine-tuning модели
slc_cli.py load-context "дообучение нейронной сети"
```

### Криптография и блокчейн

```bash
# DeFi audit
slc_cli.py load-context "аудит безопасности DeFi протокола"

# Smart contracts
slc_cli.py load-context "разработка смарт контрактов"

# Post-quantum криптография
slc_cli.py load-context "post-quantum cryptography"
```

### Веб-разработка

```bash
# Python web app
slc_cli.py load-context "создать FastAPI приложение"

# JavaScript проект
slc_cli.py load-context "React application"

# Документация
slc_cli.py load-context "создать техническую документацию"
```

### Системная работа

```bash
# Анализ проблем
slc_cli.py load-context "отладка performance issues"

# Методологии
slc_cli.py load-context "best practices разработки"

# Инструменты
slc_cli.py load-context "автоматизация deployment"
```

---

## 🧠 Как работает интеллектуальный анализ

### 1. Анализ намерений

UCE определяет тип задачи:
- 🏗️ **create_project** - создание нового проекта
- 🔍 **find_information** - поиск информации 
- 🐛 **solve_problem** - решение проблем
- 📊 **analyze_technology** - анализ технологий
- 📚 **learn_domain** - изучение области
- ⚡ **optimize_performance** - оптимизация

### 2. Определение доменов

```
Домены:
🤖 ai_ml        - искусственный интеллект, ML
🐍 python       - Python разработка
🌐 javascript   - JS/web разработка  
🔐 crypto       - криптография, блокчейн
📋 methodologies - методологии разработки
🛠️ tools        - инструменты и автоматизация
📚 documentation - документация
```

### 3. AI-powered рекомендации

- **TF-IDF анализ** - семантическое соответствие (40%)
- **Usage tracking** - популярность модулей (30%)
- **Context relevance** - релевантность контексту (20%)
- **Semantic matching** - семантическое соответствие (10%)

### 4. Confidence Score

| Score | Интерпретация | Действие |
|-------|---------------|----------|
| 0.8-1.0 | Высокая уверенность | Автоматическая загрузка |
| 0.6-0.8 | Средняя уверенность | Загрузка + предложения |
| 0.4-0.6 | Низкая уверенность | Manual selection |
| 0.0-0.4 | Неопределенность | Fallback suggestions |

---

## 📊 Мониторинг и аналитика

### Просмотр статистики

```bash
# Анализ использования (в разработке)
slc_cli.py analyze-context --current-files module1.json module2.json

# Предложения по улучшению  
slc_cli.py analyze-context --suggest-improvements
```

### Отчёты в JSON

```bash
# Сохранение результатов для анализа
slc_cli.py load-context "запрос" --format json --save-result result.json
```

---

## 🔧 Интеграция и автоматизация

### Python API

```python
from tools.cli_modules.core.unified_context_engine import quick_load_context

# Быстрая загрузка
result = quick_load_context("создать AI проект", verbose=True)

# Проверка результата
if result.success:
    print(f"Загружено {len(result.loaded_files)} файлов")
    print(f"Confidence: {result.confidence_score:.2f}")
```

### Скрипты автоматизации

```bash
#!/bin/bash
# auto_context.sh - автоматическая загрузка для CI/CD

QUERY="$1"
slc_cli.py load-context "$QUERY" --format list > context_files.txt

# Загружаем каждый файл
while read file; do
    echo "Loading: $file"
    cat "$file"
done < context_files.txt
```

---

## 🚨 Устранение неполадок

### Частые проблемы

#### ❌ "AI engine error"
**Причина:** Конфликт версий AI recommendation engine

**Решение:**
```bash
# Используйте pattern-based стратегию
slc_cli.py load-context "запрос" --strategy pattern
```

#### ❌ "Низкий confidence score"
**Причина:** Неясный или слишком общий запрос

**Решение:**
- Используйте более конкретные термины
- Укажите технологию: "python ML" вместо "ML"
- Используйте --verbose для анализа

#### ❌ "Загружено мало файлов"
**Причина:** Слишком специфичный запрос

**Решение:**
```bash
# Увеличьте лимит модулей
slc_cli.py load-context "запрос" --max-modules 20

# Или используйте full стратегию
slc_cli.py load-context "запрос" --strategy full
```

### Логи и отладка

```bash
# Подробная диагностика
slc_cli.py load-context "запрос" --verbose

# Сохранение результатов для анализа
slc_cli.py load-context "запрос" --save-result debug.json
```

---

## 🔮 Планы развития

### В разработке

- 🎯 **Персонализация** - адаптация под стиль пользователя
- 📈 **Advanced analytics** - детальная аналитика использования
- 🔗 **IDE интеграция** - плагины для Cursor, VSCode
- 🌐 **Remote context** - загрузка контекста по сети
- 🤖 **Improved AI** - интеграция с GPT-4, Claude API

### Запланированные улучшения

- **Multi-language support** - поддержка разных языков
- **Context templates** - предустановленные шаблоны контекста
- **Collaborative context** - совместная работа над контекстом
- **Performance optimization** - ускорение анализа и загрузки

---

## 📞 Поддержка

### Сообщить о проблеме

1. Опишите шаги воспроизведения
2. Приложите вывод с `--verbose`
3. Укажите версию системы: `cat VERSION`

### Предложить улучшение

1. Опишите желаемую функциональность
2. Приведите примеры использования
3. Укажите приоритет (low/medium/high)

---

## 📚 Дополнительная документация

- 📖 [Архитектура UCE](unified_context_engine_architecture.md)
- 🔧 [API Reference](unified_context_engine_api.md)
- 💼 [Best Practices](context_loading_best_practices.md)
- 🎓 [Примеры интеграции](context_integration_examples.md)

---

**СЛК v4.0 - Unified Context Engine**  
*Делаем загрузку контекста простой и интеллектуальной* 