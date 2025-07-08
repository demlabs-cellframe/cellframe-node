#!/usr/bin/env python3
"""
Interactive Documentation Explorer
Интерактивный исследователь документации Cellframe API
"""

import json
import os
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Set
import datetime
import webbrowser
import subprocess
import sys

class InteractiveDocsExplorer:
    """Интерактивный исследователь документации"""
    
    def __init__(self, docs_root: str = ".context/docs"):
        self.docs_root = Path(docs_root)
        self.api_reference = self.docs_root / "api-reference"
        self.search_index = {}
        self.function_categories = {}
        self.build_search_index()
    
    def build_search_index(self):
        """Строит индекс для быстрого поиска"""
        print("🔍 Построение поискового индекса...")
        
        # Сканируем все .md файлы
        for md_file in self.api_reference.rglob("*.md"):
            if md_file.name == "README.md":
                continue
                
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Извлекаем метаданные
                function_name = md_file.stem
                category = self.extract_category(content)
                description = self.extract_description(content)
                parameters = self.extract_parameters(content)
                
                self.search_index[function_name] = {
                    'file_path': str(md_file),
                    'category': category,
                    'description': description,
                    'parameters': parameters,
                    'content': content,
                    'keywords': self.extract_keywords(content)
                }
                
                # Группируем по категориям
                if category not in self.function_categories:
                    self.function_categories[category] = []
                self.function_categories[category].append(function_name)
                
            except Exception as e:
                print(f"⚠️ Ошибка обработки {md_file}: {e}")
        
        print(f"✅ Индекс построен: {len(self.search_index)} функций в {len(self.function_categories)} категориях")

    def extract_category(self, content: str) -> str:
        """Извлекает категорию из документации"""
        category_match = re.search(r'\*\*Категория:\*\*\s*(.+)', content)
        return category_match.group(1).strip() if category_match else "Uncategorized"

    def extract_description(self, content: str) -> str:
        """Извлекает описание функции"""
        desc_match = re.search(r'## Описание\s*\n(.*?)(?=\n##|\n#|$)', content, re.DOTALL)
        if desc_match:
            return desc_match.group(1).strip()[:200] + "..."
        return "Описание не найдено"

    def extract_parameters(self, content: str) -> List[str]:
        """Извлекает список параметров"""
        # Ищем таблицу параметров
        table_match = re.search(r'\| Параметр.*?\n(.*?)(?=\n\n|\n#)', content, re.DOTALL)
        if table_match:
            table_content = table_match.group(1)
            params = []
            for line in table_content.split('\n'):
                if '|' in line and not line.strip().startswith('|---'):
                    cells = [cell.strip() for cell in line.split('|') if cell.strip()]
                    if len(cells) >= 2:
                        params.append(cells[0])
            return params
        return []

    def extract_keywords(self, content: str) -> Set[str]:
        """Извлекает ключевые слова для поиска"""
        keywords = set()
        
        # Добавляем слова из заголовков
        for match in re.finditer(r'#+\s*(.+)', content):
            keywords.update(match.group(1).lower().split())
        
        # Добавляем слова из кода
        for match in re.finditer(r'`([^`]+)`', content):
            keywords.add(match.group(1).lower())
        
        # Добавляем технические термины
        tech_terms = re.findall(r'\b(ledger|chain|crypto|hash|sign|verify|block|tx|addr|key)\b', content.lower())
        keywords.update(tech_terms)
        
        return keywords

    def search_functions(self, query: str) -> List[Tuple[str, float]]:
        """Поиск функций по запросу"""
        query_lower = query.lower()
        results = []
        
        for func_name, func_data in self.search_index.items():
            score = 0
            
            # Точное совпадение имени
            if query_lower in func_name.lower():
                score += 100
            
            # Совпадение в категории
            if query_lower in func_data['category'].lower():
                score += 50
            
            # Совпадение в описании
            if query_lower in func_data['description'].lower():
                score += 30
            
            # Совпадение в параметрах
            for param in func_data['parameters']:
                if query_lower in param.lower():
                    score += 20
            
            # Совпадение в ключевых словах
            for keyword in func_data['keywords']:
                if query_lower in keyword:
                    score += 10
            
            if score > 0:
                results.append((func_name, score))
        
        # Сортируем по релевантности
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:10]  # Топ-10 результатов

    def display_search_results(self, results: List[Tuple[str, float]]):
        """Отображает результаты поиска"""
        if not results:
            print("❌ Функции не найдены")
            return
        
        print(f"\n🔍 Найдено {len(results)} функций:")
        print("=" * 60)
        
        for i, (func_name, score) in enumerate(results, 1):
            func_data = self.search_index[func_name]
            print(f"{i:2d}. {func_name}")
            print(f"    Категория: {func_data['category']}")
            print(f"    Описание: {func_data['description'][:80]}...")
            print(f"    Релевантность: {score:.0f}")
            print()

    def show_function_details(self, function_name: str):
        """Показывает детальную информацию о функции"""
        if function_name not in self.search_index:
            print(f"❌ Функция '{function_name}' не найдена")
            return
        
        func_data = self.search_index[function_name]
        
        print(f"\n📚 Документация: {function_name}")
        print("=" * 60)
        print(f"Категория: {func_data['category']}")
        print(f"Файл: {func_data['file_path']}")
        print()
        
        # Показываем содержимое файла
        try:
            with open(func_data['file_path'], 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Показываем первые разделы
            sections = content.split('\n## ')
            for i, section in enumerate(sections[:4]):  # Первые 4 раздела
                if i == 0:
                    print(section)
                else:
                    print(f"## {section}")
                print()
                
            if len(sections) > 4:
                print("... (показаны первые разделы)")
                print(f"\n💡 Для полного просмотра используйте: открыть {function_name}")
                
        except Exception as e:
            print(f"❌ Ошибка чтения файла: {e}")

    def open_function_docs(self, function_name: str):
        """Открывает документацию функции в редакторе/браузере"""
        if function_name not in self.search_index:
            print(f"❌ Функция '{function_name}' не найдена")
            return
        
        file_path = self.search_index[function_name]['file_path']
        
        try:
            # Пытаемся открыть в VS Code
            result = subprocess.run(['code', file_path], capture_output=True)
            if result.returncode == 0:
                print(f"📝 Открыто в VS Code: {function_name}")
                return
        except:
            pass
        
        try:
            # Пытаемся открыть в системном редакторе
            if sys.platform == "darwin":  # macOS
                subprocess.run(['open', file_path])
            elif sys.platform == "linux":
                subprocess.run(['xdg-open', file_path])
            elif sys.platform == "win32":
                subprocess.run(['start', file_path], shell=True)
            
            print(f"📖 Открыто в системном редакторе: {function_name}")
            
        except Exception as e:
            print(f"❌ Не удалось открыть файл: {e}")
            print(f"Путь к файлу: {file_path}")

    def list_categories(self):
        """Показывает список категорий"""
        print("\n📂 Категории функций:")
        print("=" * 40)
        
        for category, functions in sorted(self.function_categories.items()):
            print(f"{category} ({len(functions)} функций)")
        
        print(f"\n💡 Используйте 'категория <название>' для просмотра функций в категории")

    def show_category_functions(self, category: str):
        """Показывает функции в категории"""
        # Поиск категории (нечувствительный к регистру)
        found_category = None
        for cat in self.function_categories:
            if category.lower() in cat.lower():
                found_category = cat
                break
        
        if not found_category:
            print(f"❌ Категория '{category}' не найдена")
            print("Доступные категории:")
            for cat in sorted(self.function_categories.keys()):
                print(f"  - {cat}")
            return
        
        functions = self.function_categories[found_category]
        
        print(f"\n📂 Функции в категории '{found_category}':")
        print("=" * 60)
        
        for i, func_name in enumerate(sorted(functions), 1):
            func_data = self.search_index[func_name]
            print(f"{i:2d}. {func_name}")
            print(f"    {func_data['description'][:60]}...")
            print()

    def show_statistics(self):
        """Показывает статистику документации"""
        print("\n📊 Статистика документации:")
        print("=" * 40)
        
        total_functions = len(self.search_index)
        print(f"Всего функций: {total_functions}")
        print(f"Категорий: {len(self.function_categories)}")
        
        # Статистика по категориям
        print("\nРаспределение по категориям:")
        for category, functions in sorted(self.function_categories.items(), 
                                        key=lambda x: len(x[1]), reverse=True):
            percentage = len(functions) / total_functions * 100
            print(f"  {category}: {len(functions)} ({percentage:.1f}%)")
        
        # Статистика по параметрам
        param_counts = [len(func_data['parameters']) for func_data in self.search_index.values()]
        if param_counts:
            avg_params = sum(param_counts) / len(param_counts)
            max_params = max(param_counts)
            print(f"\nПараметры:")
            print(f"  Среднее количество: {avg_params:.1f}")
            print(f"  Максимальное количество: {max_params}")

    def show_help(self):
        """Показывает справку по командам"""
        help_text = """
🔍 Интерактивный исследователь документации Cellframe API

Доступные команды:
  поиск <запрос>          - Поиск функций по ключевым словам
  функция <имя>           - Показать детали функции
  открыть <имя>           - Открыть документацию функции в редакторе
  категории               - Показать список всех категорий
  категория <название>    - Показать функции в категории
  статистика              - Показать статистику документации
  помощь                  - Показать эту справку
  выход                   - Выйти из программы

Примеры:
  поиск ledger           - Найти все функции связанные с ledger
  функция dap_chain_ledger_tx_add - Показать детали функции
  категория crypto       - Показать функции криптографии
  открыть PyInit_libDAP  - Открыть документацию в редакторе

Советы:
  - Используйте частичные названия для поиска
  - Поиск работает по именам, категориям и описаниям
  - Результаты сортируются по релевантности
"""
        print(help_text)

    def run_interactive(self):
        """Запускает интерактивный режим"""
        print("🚀 Интерактивный исследователь документации Cellframe API")
        print("Введите 'помощь' для получения списка команд")
        
        while True:
            try:
                command = input("\n📚 docs> ").strip()
                
                if not command:
                    continue
                
                parts = command.split(maxsplit=1)
                cmd = parts[0].lower()
                arg = parts[1] if len(parts) > 1 else ""
                
                if cmd in ['выход', 'exit', 'quit', 'q']:
                    print("👋 До свидания!")
                    break
                    
                elif cmd in ['помощь', 'help', 'h']:
                    self.show_help()
                    
                elif cmd in ['поиск', 'search', 's']:
                    if arg:
                        results = self.search_functions(arg)
                        self.display_search_results(results)
                    else:
                        print("❌ Укажите запрос для поиска")
                        
                elif cmd in ['функция', 'function', 'f']:
                    if arg:
                        self.show_function_details(arg)
                    else:
                        print("❌ Укажите имя функции")
                        
                elif cmd in ['открыть', 'open', 'o']:
                    if arg:
                        self.open_function_docs(arg)
                    else:
                        print("❌ Укажите имя функции")
                        
                elif cmd in ['категории', 'categories', 'cats']:
                    self.list_categories()
                    
                elif cmd in ['категория', 'category', 'cat']:
                    if arg:
                        self.show_category_functions(arg)
                    else:
                        print("❌ Укажите название категории")
                        
                elif cmd in ['статистика', 'stats']:
                    self.show_statistics()
                    
                else:
                    print(f"❌ Неизвестная команда: {cmd}")
                    print("Введите 'помощь' для получения списка команд")
                    
            except KeyboardInterrupt:
                print("\n👋 До свидания!")
                break
            except Exception as e:
                print(f"❌ Ошибка: {e}")

    def generate_quick_reference(self) -> str:
        """Генерирует краткий справочник"""
        print("📋 Генерация краткого справочника...")
        
        reference_content = f"""# Cellframe API - Краткий справочник

Сгенерировано: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Статистика
- **Всего функций:** {len(self.search_index)}
- **Категорий:** {len(self.function_categories)}

## Функции по категориям

"""
        
        for category, functions in sorted(self.function_categories.items()):
            reference_content += f"### {category} ({len(functions)} функций)\n\n"
            
            for func_name in sorted(functions):
                func_data = self.search_index[func_name]
                params_info = f" ({len(func_data['parameters'])} параметров)" if func_data['parameters'] else ""
                reference_content += f"- **{func_name}**{params_info} - {func_data['description'][:60]}...\n"
            
            reference_content += "\n"
        
        reference_content += """
## Использование интерактивного исследователя

```bash
python .context/tools/interactive_docs_explorer.py
```

### Основные команды:
- `поиск <запрос>` - Поиск функций
- `функция <имя>` - Детали функции  
- `категория <название>` - Функции в категории
- `открыть <имя>` - Открыть в редакторе

### Примеры поиска:
- `поиск ledger` - Все функции ledger
- `поиск crypto sign` - Функции криптографического подписания
- `поиск python` - Python интеграция

---
*Автоматически сгенерированный справочник*
"""
        
        # Сохраняем справочник
        reference_file = self.docs_root / "quick_reference.md"
        with open(reference_file, 'w', encoding='utf-8') as f:
            f.write(reference_content)
        
        print(f"✅ Краткий справочник создан: {reference_file}")
        return str(reference_file)

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Interactive Documentation Explorer')
    parser.add_argument('--docs-root', default='.context/docs',
                       help='Корневая директория документации')
    parser.add_argument('--generate-reference', action='store_true',
                       help='Сгенерировать краткий справочник')
    parser.add_argument('--search', help='Выполнить поиск и выйти')
    parser.add_argument('--function', help='Показать детали функции и выйти')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.docs_root):
        print(f"❌ Директория документации не найдена: {args.docs_root}")
        return 1
    
    explorer = InteractiveDocsExplorer(args.docs_root)
    
    if args.generate_reference:
        explorer.generate_quick_reference()
        return 0
    
    if args.search:
        results = explorer.search_functions(args.search)
        explorer.display_search_results(results)
        return 0
    
    if args.function:
        explorer.show_function_details(args.function)
        return 0
    
    # Интерактивный режим
    explorer.run_interactive()
    return 0

if __name__ == '__main__':
    exit(main()) 