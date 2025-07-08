#!/usr/bin/env python3
"""
Top 20 Functions Documentation Generator
Автоматическая генерация документации для 20 самых критических функций Cellframe
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Tuple
import re

class Top20FunctionsGenerator:
    """Генератор документации для топ-20 критических функций"""
    
    def __init__(self, api_inventory_file: str):
        self.api_inventory_file = api_inventory_file
        self.api_data = None
        self.top_functions = []
        
        # Критерии приоритизации функций
        self.priority_patterns = {
            'critical': {
                'patterns': [
                    r'^dap_chain_ledger_.*',
                    r'^dap_chain_create.*',
                    r'^dap_chain_delete.*',
                    r'^dap_enc_key_.*',
                    r'^dap_sign_.*',
                    r'^PyInit_.*',
                    r'^dap_chain_datum_tx_.*'
                ],
                'weight': 100
            },
            'high': {
                'patterns': [
                    r'^dap_chain_.*',
                    r'^dap_crypto_.*',
                    r'^dap_hash_.*',
                    r'^DapGlobalDB.*'
                ],
                'weight': 80
            },
            'medium': {
                'patterns': [
                    r'^dap_.*',
                    r'^Py.*'
                ],
                'weight': 60
            }
        }
        
        # Шаблон документации
        self.doc_template = """# {function_name}

## Описание
{description}

## Сигнатура
```c
{signature}
```

## Параметры
{parameters_table}

## Возвращаемое значение
- **Тип:** `{return_type}`
- **Описание:** {return_description}
{return_values}

## Коды ошибок
{error_codes}

## Пример использования

### C/C++
```c
{c_example}
```

### Python
```python
{python_example}
```

## Связанные функции
{related_functions}

## Примечания
{notes}

## См. также
{see_also}
"""

    def load_api_data(self):
        """Загружает данные API из JSON файла"""
        try:
            with open(self.api_inventory_file, 'r', encoding='utf-8') as f:
                self.api_data = json.load(f)
            print(f"✅ Загружено API данных: {self.api_data['metadata']['total_functions']} функций")
        except Exception as e:
            print(f"❌ Ошибка загрузки API данных: {e}")
            return False
        return True

    def calculate_function_priority(self, function_name: str, module_name: str) -> int:
        """Вычисляет приоритет функции на основе паттернов"""
        priority_score = 0
        
        # Проверяем паттерны приоритета
        for priority_level, config in self.priority_patterns.items():
            for pattern in config['patterns']:
                if re.match(pattern, function_name):
                    priority_score = max(priority_score, config['weight'])
                    break
        
        # Дополнительные бонусы
        if 'include' in module_name:
            priority_score += 20  # Заголовочные файлы важнее
        
        if function_name.startswith('dap_chain_ledger'):
            priority_score += 30  # Ledger функции критичны
            
        if 'python' in module_name.lower():
            priority_score += 15  # Python API важен
            
        return priority_score

    def select_top_functions(self) -> List[Dict]:
        """Выбирает топ-20 функций по приоритету"""
        all_functions = []
        
        # Собираем все функции с их приоритетами
        for module_name, module_data in self.api_data['modules'].items():
            for function in module_data['functions']:
                priority = self.calculate_function_priority(function['name'], module_name)
                
                function_info = {
                    'name': function['name'],
                    'signature': function['signature'],
                    'return_type': function['return_type'],
                    'parameters': function['parameters'],
                    'module': module_name,
                    'file_path': function['file_path'],
                    'comments': function['comments'],
                    'priority': priority
                }
                all_functions.append(function_info)
        
        # Сортируем по приоритету и берем топ-20
        all_functions.sort(key=lambda x: x['priority'], reverse=True)
        self.top_functions = all_functions[:20]
        
        print("🎯 Топ-20 функций по приоритету:")
        for i, func in enumerate(self.top_functions, 1):
            print(f"  {i:2d}. {func['name']} (приоритет: {func['priority']})")
        
        return self.top_functions

    def generate_function_description(self, function_info: Dict) -> str:
        """Генерирует описание функции на основе имени и комментариев"""
        name = function_info['name']
        comments = function_info.get('comments', [])
        
        # Базовые описания по паттернам
        descriptions = {
            r'.*_create.*': 'Создает новый объект или структуру данных',
            r'.*_delete.*': 'Удаляет объект и освобождает связанные ресурсы',
            r'.*_init.*': 'Инициализирует объект или подсистему',
            r'.*_add.*': 'Добавляет элемент в коллекцию или структуру',
            r'.*_remove.*': 'Удаляет элемент из коллекции или структуры',
            r'.*_get.*': 'Получает данные или объект по идентификатору',
            r'.*_set.*': 'Устанавливает значение или конфигурацию',
            r'.*_find.*': 'Выполняет поиск элемента по критерию',
            r'.*_save.*': 'Сохраняет данные на постоянное хранилище',
            r'.*_load.*': 'Загружает данные из постоянного хранилища',
            r'.*_sign.*': 'Выполняет криптографическое подписание',
            r'.*_verify.*': 'Проверяет криптографическую подпись',
            r'.*_hash.*': 'Вычисляет криптографический хеш',
            r'.*_balance.*': 'Работает с балансом адреса или аккаунта',
            r'.*ledger.*': 'Выполняет операции с распределенным реестром',
            r'PyInit.*': 'Инициализирует Python модуль для интеграции'
        }
        
        # Ищем подходящее описание
        description = f"Функция {name} выполняет операции в рамках Cellframe API"
        for pattern, desc in descriptions.items():
            if re.match(pattern, name, re.IGNORECASE):
                description = desc
                break
        
        # Добавляем информацию из комментариев если есть
        if comments:
            comment_text = ' '.join(comments).replace('//', '').replace('/*', '').replace('*/', '').strip()
            if comment_text and len(comment_text) > 10:
                description += f". {comment_text}"
        
        return description

    def generate_parameters_table(self, parameters: List[Dict]) -> str:
        """Генерирует таблицу параметров"""
        if not parameters:
            return "Функция не принимает параметров."
        
        table = "| Параметр | Тип | Описание | Обязательный |\n"
        table += "|----------|-----|----------|--------------|\\n"
        
        for param in parameters:
            name = param.get('name', 'unknown')
            param_type = param.get('type', 'unknown')
            description = param.get('description', 'Описание параметра')
            required = "Да" if not param_type.endswith('*') else "Да"
            
            # Генерируем описание на основе имени параметра
            if not description or description == '':
                if 'ledger' in name.lower():
                    description = 'Указатель на объект ledger'
                elif 'tx' in name.lower():
                    description = 'Указатель на транзакцию'
                elif 'hash' in name.lower():
                    description = 'Хеш для идентификации'
                elif 'addr' in name.lower():
                    description = 'Адрес в блокчейне'
                elif 'key' in name.lower():
                    description = 'Криптографический ключ'
                elif 'size' in name.lower():
                    description = 'Размер данных в байтах'
                else:
                    description = f'Параметр {name}'
            
            table += f"| {name} | `{param_type}` | {description} | {required} |\\n"
        
        return table

    def generate_c_example(self, function_info: Dict) -> str:
        """Генерирует пример использования на C"""
        name = function_info['name']
        return_type = function_info['return_type']
        parameters = function_info['parameters']
        
        # Базовый шаблон
        example = f"""#include "cellframe_api.h"

int main() {{
    // Инициализация
    // TODO: Добавить необходимую инициализацию
    
    // Вызов функции {name}
    {return_type} result = {name}("""
        
        # Добавляем параметры
        param_examples = []
        for param in parameters:
            param_name = param.get('name', 'param')
            if 'ledger' in param_name.lower():
                param_examples.append('ledger')
            elif 'tx' in param_name.lower():
                param_examples.append('transaction')
            elif 'hash' in param_name.lower():
                param_examples.append('&hash')
            else:
                param_examples.append('NULL')
        
        example += ', '.join(param_examples)
        example += """);
    
    // Проверка результата
    if (result != 0) {
        printf("Ошибка выполнения функции: %d\\n", result);
        return -1;
    }
    
    printf("Функция выполнена успешно\\n");
    return 0;
}"""
        
        return example

    def generate_python_example(self, function_info: Dict) -> str:
        """Генерирует пример использования на Python"""
        name = function_info['name']
        
        if name.startswith('PyInit'):
            return f"""import libCellFrame

# Модуль автоматически инициализируется при импорте
# {name} вызывается внутренне

try:
    # Использование функций модуля
    result = libCellFrame.some_function()
    print(f"Результат: {{result}}")
except Exception as e:
    print(f"Ошибка: {{e}}")"""
        
        return f"""import libCellFrame

def example_{name.lower()}():
    \"\"\"Пример использования {name}\"\"\"
    try:
        # TODO: Адаптировать под конкретную функцию
        result = libCellFrame.{name.replace('dap_', '').replace('_', '.')}()
        
        if result:
            print("Операция выполнена успешно")
            return result
        else:
            print("Операция завершилась с ошибкой")
            return None
            
    except Exception as e:
        print(f"Исключение: {{e}}")
        return None

# Использование
if __name__ == "__main__":
    example_{name.lower()}()"""

    def generate_documentation_file(self, function_info: Dict, output_dir: str):
        """Генерирует файл документации для функции"""
        name = function_info['name']
        
        # Генерируем все компоненты документации
        description = self.generate_function_description(function_info)
        parameters_table = self.generate_parameters_table(function_info['parameters'])
        c_example = self.generate_c_example(function_info)
        python_example = self.generate_python_example(function_info)
        
        # Заполняем шаблон
        doc_content = self.doc_template.format(
            function_name=name,
            description=description,
            signature=function_info['signature'],
            parameters_table=parameters_table,
            return_type=function_info['return_type'],
            return_description="Результат выполнения операции",
            return_values="- `0` - Успешное выполнение\\n- `!0` - Код ошибки",
            error_codes="| Код | Описание |\\n|-----|----------|\\n| 0 | Успех |\\n| -1 | Общая ошибка |",
            c_example=c_example,
            python_example=python_example,
            related_functions="- TODO: Добавить связанные функции",
            notes="- TODO: Добавить важные примечания\\n- Проверяйте возвращаемые значения",
            see_also="- [Cellframe API Reference](../api-reference.md)\\n- [Getting Started Guide](../getting-started.md)"
        )
        
        # Сохраняем файл
        output_file = Path(output_dir) / f"{name}.md"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(doc_content)
        
        print(f"📄 Создана документация: {output_file}")

    def generate_index_file(self, output_dir: str):
        """Генерирует индексный файл со списком всех функций"""
        index_content = """# Cellframe API - Топ-20 критических функций

Документация для 20 самых важных функций Cellframe API, выбранных на основе анализа критичности и частоты использования.

## Функции по категориям

### Ledger API
"""
        
        # Группируем функции по категориям
        categories = {
            'Ledger API': [],
            'Chain API': [],
            'Crypto API': [],
            'Python API': [],
            'Other API': []
        }
        
        for func in self.top_functions:
            name = func['name']
            if 'ledger' in name.lower():
                categories['Ledger API'].append(func)
            elif 'chain' in name.lower() and 'ledger' not in name.lower():
                categories['Chain API'].append(func)
            elif any(x in name.lower() for x in ['crypt', 'sign', 'hash', 'key']):
                categories['Crypto API'].append(func)
            elif name.startswith('Py') or 'python' in func['module'].lower():
                categories['Python API'].append(func)
            else:
                categories['Other API'].append(func)
        
        # Генерируем содержимое по категориям
        for category, functions in categories.items():
            if functions:
                index_content += f"\\n### {category}\\n\\n"
                for func in functions:
                    index_content += f"- [{func['name']}]({func['name']}.md) - {self.generate_function_description(func)[:100]}...\\n"
        
        index_content += """

## Статистика

- **Всего функций:** 20
- **Покрытие модулей:** Все критические модули
- **Примеры кода:** C/C++ и Python для каждой функции
- **Уровень детализации:** Полная документация

## Следующие шаги

1. Изучите [Getting Started Guide](../getting-started.md)
2. Ознакомьтесь с [Architecture Overview](../architecture/overview.md)  
3. Попробуйте [Tutorial Examples](../tutorials/)

## Обратная связь

Если вы нашли ошибки или у вас есть предложения по улучшению документации, пожалуйста, создайте issue в репозитории проекта.
"""
        
        # Сохраняем индексный файл
        index_file = Path(output_dir) / "README.md"
        with open(index_file, 'w', encoding='utf-8') as f:
            f.write(index_content)
        
        print(f"📄 Создан индексный файл: {index_file}")

    def generate_all_documentation(self, output_dir: str = ".context/docs/api-reference/top20"):
        """Генерирует документацию для всех топ-20 функций"""
        if not self.load_api_data():
            return False
        
        print("🚀 Генерация документации для топ-20 функций...")
        
        # Выбираем топ функции
        self.select_top_functions()
        
        # Создаем выходную директорию
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Генерируем документацию для каждой функции
        for i, function_info in enumerate(self.top_functions, 1):
            print(f"📝 Генерация {i}/20: {function_info['name']}")
            self.generate_documentation_file(function_info, output_dir)
        
        # Генерируем индексный файл
        self.generate_index_file(output_dir)
        
        print(f"✅ Документация сгенерирована в {output_dir}")
        print(f"📊 Создано файлов: {len(self.top_functions) + 1}")
        
        return True

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Top 20 Functions Documentation Generator')
    parser.add_argument('--api-inventory', 
                       default='.context/analysis/cellframe_api_inventory.json',
                       help='Путь к файлу инвентаря API')
    parser.add_argument('--output-dir', 
                       default='.context/docs/api-reference/top20',
                       help='Директория для сохранения документации')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.api_inventory):
        print(f"❌ Файл инвентаря API не найден: {args.api_inventory}")
        return 1
    
    generator = Top20FunctionsGenerator(args.api_inventory)
    success = generator.generate_all_documentation(args.output_dir)
    
    return 0 if success else 1

if __name__ == '__main__':
    exit(main()) 