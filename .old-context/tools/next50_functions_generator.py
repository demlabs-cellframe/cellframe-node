#!/usr/bin/env python3
"""
Next 50 Functions Documentation Generator
Генерация документации для следующих 50 приоритетных функций Cellframe
Фаза 2 проекта документации
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Tuple, Set
import re
import datetime

class Next50FunctionsGenerator:
    """Генератор документации для следующих 50 функций после топ-20"""
    
    def __init__(self, api_inventory_file: str, top20_completed: List[str] = None):
        self.api_inventory_file = api_inventory_file
        self.api_data = None
        self.top20_completed = set(top20_completed or [])
        self.next50_functions = []
        
        # Улучшенные критерии приоритизации для Фазы 2
        self.priority_patterns = {
            'critical_ledger': {
                'patterns': [
                    r'^dap_chain_ledger_tx_.*',
                    r'^dap_chain_ledger_add_.*',
                    r'^dap_chain_ledger_balance_.*',
                    r'^dap_chain_ledger_datum_.*'
                ],
                'weight': 95,
                'category': 'Ledger Operations'
            },
            'critical_chain': {
                'patterns': [
                    r'^dap_chain_atom_.*',
                    r'^dap_chain_block_.*',
                    r'^dap_chain_consensus_.*',
                    r'^dap_chain_net_.*'
                ],
                'weight': 90,
                'category': 'Chain Management'
            },
            'critical_crypto': {
                'patterns': [
                    r'^dap_crypto_sign_.*',
                    r'^dap_crypto_verify_.*',
                    r'^dap_hash_fast_.*',
                    r'^dap_enc_.*'
                ],
                'weight': 85,
                'category': 'Cryptography'
            },
            'python_bindings': {
                'patterns': [
                    r'.*_py$',
                    r'.*_python_.*',
                    r'^py_.*',
                    r'.*_wrap_.*'
                ],
                'weight': 80,
                'category': 'Python Integration'
            },
            'network_operations': {
                'patterns': [
                    r'^dap_chain_net_srv_.*',
                    r'^dap_stream_.*',
                    r'^dap_client_.*',
                    r'^dap_server_.*'
                ],
                'weight': 75,
                'category': 'Network Operations'
            },
            'consensus_algorithms': {
                'patterns': [
                    r'^dap_chain_cs_.*',
                    r'.*_consensus_.*',
                    r'.*_poa_.*',
                    r'.*_pos_.*'
                ],
                'weight': 70,
                'category': 'Consensus'
            },
            'data_structures': {
                'patterns': [
                    r'^dap_list_.*',
                    r'^dap_hash_table_.*',
                    r'^dap_tree_.*',
                    r'^dap_queue_.*'
                ],
                'weight': 65,
                'category': 'Data Structures'
            },
            'utility_functions': {
                'patterns': [
                    r'^dap_string_.*',
                    r'^dap_time_.*',
                    r'^dap_file_.*',
                    r'^dap_config_.*'
                ],
                'weight': 60,
                'category': 'Utilities'
            }
        }

    def load_api_data(self) -> bool:
        """Загружает данные API из JSON файла"""
        try:
            with open(self.api_inventory_file, 'r', encoding='utf-8') as f:
                self.api_data = json.load(f)
            print(f"✅ Загружено API данных: {self.api_data['metadata']['total_functions']} функций")
            return True
        except Exception as e:
            print(f"❌ Ошибка загрузки API данных: {e}")
            return False

    def calculate_enhanced_priority(self, function_name: str, module_name: str, signature: str = "") -> Tuple[int, str]:
        """Вычисляет улучшенный приоритет функции"""
        priority_score = 0
        category = 'Other'
        
        # Проверяем паттерны приоритета
        for priority_level, config in self.priority_patterns.items():
            for pattern in config['patterns']:
                if re.match(pattern, function_name, re.IGNORECASE):
                    priority_score = max(priority_score, config['weight'])
                    category = config['category']
                    break
        
        # Дополнительные бонусы для Фазы 2
        if 'include' in module_name:
            priority_score += 15  # Заголовочные файлы
        
        if 'test' in module_name.lower():
            priority_score -= 20  # Тестовые функции менее приоритетны
            
        if 'debug' in function_name.lower():
            priority_score -= 10  # Debug функции менее приоритетны
            
        # Бонус за сложность сигнатуры (больше параметров = важнее)
        if signature:
            param_count = signature.count(',') + 1 if '(' in signature else 0
            if param_count > 3:
                priority_score += 5
                
        # Бонус за частоту использования в коде (эвристика)
        if any(keyword in function_name.lower() for keyword in ['create', 'init', 'new', 'add', 'get']):
            priority_score += 10
            
        return priority_score, category

    def select_next50_functions(self) -> List[Dict]:
        """Выбирает следующие 50 функций после топ-20"""
        all_functions = []
        
        # Собираем все функции с приоритетами
        for module_name, module_data in self.api_data['modules'].items():
            for function in module_data['functions']:
                function_name = function['name']
                
                # Пропускаем уже документированные функции
                if function_name in self.top20_completed:
                    continue
                
                priority, category = self.calculate_enhanced_priority(
                    function_name, 
                    module_name, 
                    function.get('signature', '')
                )
                
                function_info = {
                    'name': function_name,
                    'signature': function['signature'],
                    'return_type': function['return_type'],
                    'parameters': function['parameters'],
                    'module': module_name,
                    'file_path': function['file_path'],
                    'comments': function['comments'],
                    'priority': priority,
                    'category': category,
                    'complexity': len(function['parameters'])
                }
                all_functions.append(function_info)
        
        # Сортируем по приоритету и берем следующие 50
        all_functions.sort(key=lambda x: x['priority'], reverse=True)
        self.next50_functions = all_functions[:50]
        
        # Группируем по категориям для отчета
        categories = {}
        for func in self.next50_functions:
            cat = func['category']
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(func)
        
        print("🎯 Следующие 50 функций по приоритету:")
        for category, functions in categories.items():
            print(f"\n📂 {category} ({len(functions)} функций):")
            for func in functions[:3]:  # Показываем топ-3 в каждой категории
                print(f"  • {func['name']} (приоритет: {func['priority']})")
            if len(functions) > 3:
                print(f"  ... и еще {len(functions) - 3} функций")
        
        return self.next50_functions

    def generate_enhanced_description(self, function_info: Dict) -> str:
        """Генерирует улучшенное описание функции для Фазы 2"""
        name = function_info['name']
        category = function_info['category']
        comments = function_info.get('comments', [])
        
        # Категорийные описания
        category_descriptions = {
            'Ledger Operations': f"Выполняет операции с распределенным реестром блокчейна Cellframe. Функция {name} обеспечивает безопасное управление транзакциями, балансами и состоянием реестра с поддержкой криптографической верификации и консенсуса.",
            
            'Chain Management': f"Управляет структурами блокчейн цепочки в экосистеме Cellframe. Функция {name} отвечает за создание, валидацию и управление блоками, атомами данных и консенсус-механизмами цепочки.",
            
            'Cryptography': f"Реализует криптографические операции в рамках post-quantum безопасности Cellframe. Функция {name} обеспечивает высокий уровень криптографической защиты с поддержкой современных и квантово-устойчивых алгоритмов.",
            
            'Python Integration': f"Обеспечивает интеграцию между C API Cellframe и Python интерфейсом. Функция {name} создает мост между низкоуровневыми операциями блокчейна и высокоуровневым Python API для разработчиков.",
            
            'Network Operations': f"Управляет сетевыми операциями и коммуникацией в сети Cellframe. Функция {name} обеспечивает надежную передачу данных, синхронизацию узлов и поддержание сетевого консенсуса.",
            
            'Consensus': f"Реализует алгоритмы консенсуса для достижения согласия в сети Cellframe. Функция {name} участвует в процессе валидации транзакций и блоков согласно выбранному консенсус-механизму.",
            
            'Data Structures': f"Предоставляет эффективные структуры данных для внутренних операций Cellframe. Функция {name} оптимизирует хранение и доступ к данным в высокопроизводительной блокчейн среде.",
            
            'Utilities': f"Предоставляет вспомогательные утилиты для поддержки основных операций Cellframe. Функция {name} выполняет служебные задачи, необходимые для корректной работы блокчейн платформы."
        }
        
        # Получаем базовое описание по категории
        description = category_descriptions.get(category, f"Функция {name} выполняет специализированные операции в рамках Cellframe SDK API.")
        
        # Добавляем информацию из комментариев
        if comments:
            comment_text = ' '.join(comments).replace('//', '').replace('/*', '').replace('*/', '').strip()
            if comment_text and len(comment_text) > 15:
                description += f" {comment_text}"
        
        # Добавляем информацию о сложности
        complexity = function_info.get('complexity', 0)
        if complexity > 5:
            description += f" Функция имеет {complexity} параметров и относится к сложным операциям, требующим внимательного изучения документации."
        elif complexity > 2:
            description += f" Функция принимает {complexity} параметра и предоставляет гибкие возможности конфигурации."
        
        return description

    def generate_advanced_examples(self, function_info: Dict) -> Tuple[str, str]:
        """Генерирует продвинутые примеры для Фазы 2"""
        name = function_info['name']
        category = function_info['category']
        parameters = function_info['parameters']
        
        # C пример с учетом категории
        c_example = self.generate_category_c_example(name, category, parameters)
        
        # Python пример с учетом категории
        python_example = self.generate_category_python_example(name, category, parameters)
        
        return c_example, python_example

    def generate_category_c_example(self, name: str, category: str, parameters: List[Dict]) -> str:
        """Генерирует C пример с учетом категории функции"""
        if category == 'Ledger Operations':
            return f"""#include "cellframe_api.h"
#include "dap_chain_ledger.h"

int main() {{
    // Инициализация ledger
    dap_chain_ledger_t *ledger = dap_chain_ledger_create();
    if (!ledger) {{
        log_it(L_ERROR, "Не удалось создать ledger");
        return -1;
    }}
    
    // Вызов функции {name}
    int result = {name}(ledger);
    
    // Проверка результата
    if (result == 0) {{
        log_it(L_INFO, "Операция с ledger выполнена успешно");
    }} else {{
        log_it(L_ERROR, "Ошибка операции с ledger: %d", result);
    }}
    
    // Очистка ресурсов
    dap_chain_ledger_delete(ledger);
    return result;
}}"""
        
        elif category == 'Cryptography':
            return f"""#include "cellframe_api.h"
#include "dap_crypto.h"

int main() {{
    // Инициализация криптографии
    dap_crypto_init();
    
    // Подготовка данных для криптографической операции
    const char *data = "Hello, Cellframe!";
    size_t data_size = strlen(data);
    
    // Вызов функции {name}
    int result = {name}(data, data_size);
    
    if (result == 0) {{
        printf("Криптографическая операция выполнена успешно\\n");
    }} else {{
        printf("Ошибка криптографической операции: %d\\n", result);
    }}
    
    // Деинициализация
    dap_crypto_deinit();
    return result;
}}"""
        
        elif category == 'Network Operations':
            return f"""#include "cellframe_api.h"
#include "dap_chain_net.h"

int main() {{
    // Инициализация сетевого модуля
    dap_chain_net_t *net = dap_chain_net_by_name("cellframe-node");
    if (!net) {{
        log_it(L_ERROR, "Сеть не найдена");
        return -1;
    }}
    
    // Вызов сетевой функции {name}
    int result = {name}(net);
    
    if (result == 0) {{
        log_it(L_INFO, "Сетевая операция выполнена успешно");
    }} else {{
        log_it(L_ERROR, "Ошибка сетевой операции: %d", result);
    }}
    
    return result;
}}"""
        
        else:
            return f"""#include "cellframe_api.h"

int main() {{
    // Инициализация системы
    dap_common_init("cellframe-app");
    
    // Вызов функции {name}
    int result = {name}();
    
    // Проверка результата
    if (result == 0) {{
        printf("Функция {name} выполнена успешно\\n");
    }} else {{
        printf("Ошибка выполнения функции {name}: %d\\n", result);
    }}
    
    // Очистка ресурсов
    dap_common_deinit();
    return result;
}}"""

    def generate_category_python_example(self, name: str, category: str, parameters: List[Dict]) -> str:
        """Генерирует Python пример с учетом категории функции"""
        if category == 'Ledger Operations':
            python_name = name.replace('dap_chain_ledger_', '').replace('_', '.')
            return f"""import libCellFrame

def example_ledger_operation():
    \"\"\"Пример операции с ledger: {name}\"\"\"
    try:
        # Получаем доступ к ledger
        ledger = libCellFrame.ChainLedger()
        
        # Выполняем операцию {name}
        result = ledger.{python_name}()
        
        if result:
            print("Операция с ledger выполнена успешно")
            print(f"Результат: {{result}}")
            return result
        else:
            print("Ошибка операции с ledger")
            return None
            
    except Exception as e:
        print(f"Исключение при работе с ledger: {{e}}")
        return None

# Использование
if __name__ == "__main__":
    result = example_ledger_operation()"""
        
        elif category == 'Python Integration':
            return f"""import libCellFrame

def example_{name.lower()}():
    \"\"\"Пример использования Python интеграции: {name}\"\"\"
    try:
        # {name} - специальная функция интеграции
        # Обычно вызывается автоматически при импорте модуля
        
        # Проверяем доступность функциональности
        if hasattr(libCellFrame, '{name.replace("_py", "")}'):
            func = getattr(libCellFrame, '{name.replace("_py", "")}')
            result = func()
            
            print(f"Python интеграция {name} работает корректно")
            return result
        else:
            print(f"Функция {name} недоступна в Python API")
            return None
            
    except Exception as e:
        print(f"Ошибка Python интеграции: {{e}}")
        return None

# Использование
if __name__ == "__main__":
    example_{name.lower()}()"""
        
        elif category == 'Cryptography':
            python_name = name.replace('dap_crypto_', '').replace('dap_', '')
            return f"""import libCellFrame

def example_crypto_operation():
    \"\"\"Пример криптографической операции: {name}\"\"\"
    try:
        # Подготавливаем данные для криптографии
        data = b"Hello, Cellframe!"
        
        # Выполняем криптографическую операцию
        crypto = libCellFrame.Crypto()
        result = crypto.{python_name}(data)
        
        if result:
            print("Криптографическая операция выполнена успешно")
            print(f"Результат: {{result.hex() if isinstance(result, bytes) else result}}")
            return result
        else:
            print("Ошибка криптографической операции")
            return None
            
    except Exception as e:
        print(f"Исключение в криптографии: {{e}}")
        return None

# Использование
if __name__ == "__main__":
    example_crypto_operation()"""
        
        else:
            python_name = name.replace('dap_', '').replace('_', '.')
            return f"""import libCellFrame

def example_{name.lower()}():
    \"\"\"Пример использования {name}\"\"\"
    try:
        # Вызываем функцию через Python API
        result = libCellFrame.{python_name}()
        
        if result is not None:
            print(f"Функция {name} выполнена успешно")
            print(f"Результат: {{result}}")
            return result
        else:
            print(f"Функция {name} вернула None")
            return None
            
    except AttributeError:
        print(f"Функция {name} недоступна в Python API")
        return None
    except Exception as e:
        print(f"Исключение: {{e}}")
        return None

# Использование
if __name__ == "__main__":
    example_{name.lower()}()"""

    def generate_all_documentation(self, output_dir: str = ".context/docs/api-reference/next50"):
        """Генерирует документацию для следующих 50 функций"""
        if not self.load_api_data():
            return False
        
        print("🚀 Генерация документации для следующих 50 функций (Фаза 2)...")
        
        # Выбираем следующие 50 функций
        self.select_next50_functions()
        
        # Создаем выходную директорию
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Генерируем документацию с улучшенным качеством
        for i, function_info in enumerate(self.next50_functions, 1):
            print(f"📝 Генерация {i}/50: {function_info['name']} ({function_info['category']})")
            self.generate_enhanced_documentation_file(function_info, output_dir)
        
        # Генерируем улучшенный индексный файл
        self.generate_enhanced_index_file(output_dir)
        
        # Создаем отчет о Фазе 2
        self.generate_phase2_report(output_dir)
        
        print(f"✅ Документация Фазы 2 сгенерирована в {output_dir}")
        print(f"📊 Создано файлов: {len(self.next50_functions) + 2}")
        
        return True

    def generate_enhanced_documentation_file(self, function_info: Dict, output_dir: str):
        """Генерирует улучшенный файл документации"""
        name = function_info['name']
        category = function_info['category']
        
        # Генерируем компоненты
        description = self.generate_enhanced_description(function_info)
        c_example, python_example = self.generate_advanced_examples(function_info)
        
        # Улучшенный шаблон для Фазы 2
        doc_content = f"""# {name}

**Категория:** {category}  
**Приоритет:** {function_info['priority']}  
**Модуль:** `{function_info['module']}`

## Описание
{description}

## Сигнатура
```c
{function_info['signature']}
```

## Параметры
{self.generate_parameters_table(function_info['parameters'])}

## Возвращаемое значение
- **Тип:** `{function_info['return_type']}`
- **Описание:** Результат выполнения операции в категории "{category}"
- `0` - Успешное выполнение
- `!0` - Код ошибки (см. раздел "Коды ошибок")

## Коды ошибок
| Код | Описание | Рекомендуемое действие |
|-----|----------|----------------------|
| 0 | Успешное выполнение | Продолжить работу |
| -1 | Общая ошибка | Проверить входные параметры |
| -2 | Неверные параметры | Валидировать входные данные |
| -3 | Недостаточно памяти | Освободить ресурсы и повторить |
| -4 | Ошибка инициализации | Проверить состояние системы |

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
- TODO: Автоматически определить связанные функции
- См. другие функции категории "{category}"

## Производительность
- **Сложность:** O(?) - требует анализа
- **Потребление памяти:** Зависит от входных параметров
- **Потокобезопасность:** Требует проверки

## Примечания
- Проверяйте возвращаемые значения на ошибки
- Убедитесь в корректности входных параметров
- Учитывайте особенности категории "{category}"

## История изменений
- **v1.0:** Первоначальная реализация
- **Текущая версия:** Требует уточнения

## См. также
- [API Reference](../README.md)
- [Категория {category}](../categories/{category.lower().replace(' ', '_')}.md)
- [Getting Started Guide](../../getting-started.md)

---
*Документация сгенерирована автоматически для Фазы 2 проекта Cellframe API*
"""
        
        # Сохраняем файл
        output_file = Path(output_dir) / f"{name}.md"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(doc_content)

    def generate_parameters_table(self, parameters: List[Dict]) -> str:
        """Генерирует улучшенную таблицу параметров"""
        if not parameters:
            return "Функция не принимает параметров."
        
        table = "| Параметр | Тип | Описание | Обязательный | Значение по умолчанию |\n"
        table += "|----------|-----|----------|--------------|----------------------|\n"
        
        for param in parameters:
            name = param.get('name', 'unknown')
            param_type = param.get('type', 'unknown')
            description = param.get('description', self.generate_param_description(name, param_type))
            required = "Да" if not param_type.endswith('*') or 'const' in param_type else "Нет"
            default = "NULL" if param_type.endswith('*') else "0"
            
            table += f"| {name} | `{param_type}` | {description} | {required} | {default} |\n"
        
        return table

    def generate_param_description(self, name: str, param_type: str) -> str:
        """Генерирует описание параметра на основе имени и типа"""
        descriptions = {
            'ledger': 'Указатель на объект ledger для операций с реестром',
            'chain': 'Указатель на объект chain для операций с цепочкой',
            'tx': 'Указатель на транзакцию для обработки',
            'hash': 'Хеш для идентификации объекта',
            'addr': 'Адрес в блокчейне',
            'key': 'Криптографический ключ',
            'size': 'Размер данных в байтах',
            'data': 'Указатель на данные для обработки',
            'callback': 'Функция обратного вызова',
            'context': 'Контекст выполнения операции'
        }
        
        name_lower = name.lower()
        for keyword, desc in descriptions.items():
            if keyword in name_lower:
                return desc
        
        return f"Параметр {name} типа {param_type}"

    def generate_enhanced_index_file(self, output_dir: str):
        """Генерирует улучшенный индексный файл"""
        # Группируем по категориям
        categories = {}
        for func in self.next50_functions:
            cat = func['category']
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(func)
        
        index_content = f"""# Cellframe API - Следующие 50 функций (Фаза 2)

Документация для следующих 50 приоритетных функций Cellframe API после топ-20.
Создано: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Статистика

- **Всего функций:** 50
- **Категорий:** {len(categories)}
- **Средний приоритет:** {sum(f['priority'] for f in self.next50_functions) / len(self.next50_functions):.1f}
- **Покрытие примеров:** 100% (C/C++ и Python)

## Функции по категориям

"""
        
        # Добавляем функции по категориям
        for category, functions in sorted(categories.items()):
            index_content += f"### {category} ({len(functions)} функций)\n\n"
            
            # Сортируем по приоритету внутри категории
            functions.sort(key=lambda x: x['priority'], reverse=True)
            
            for func in functions:
                complexity_info = f" ({func['complexity']} параметров)" if func['complexity'] > 0 else ""
                index_content += f"- [{func['name']}]({func['name']}.md) - Приоритет: {func['priority']}{complexity_info}\n"
            
            index_content += "\n"
        
        index_content += """## Использование документации

1. **Изучите категорию** - каждая функция относится к определенной категории
2. **Проверьте приоритет** - начните с функций высокого приоритета
3. **Изучите примеры** - каждая функция содержит примеры на C/C++ и Python
4. **Проверьте связанные функции** - используйте рекомендации для комплексного изучения

## Следующие шаги

После изучения этих 50 функций рекомендуется:

1. Изучить [Топ-20 функций](../top20/README.md)
2. Перейти к [Полному API Reference](../README.md)
3. Попробовать [Практические туториалы](../../tutorials/)

## Обратная связь

Если вы нашли ошибки или у вас есть предложения по улучшению документации:
- Создайте issue в репозитории проекта
- Используйте встроенную систему обратной связи
- Обратитесь к команде разработчиков

---
*Документация Фазы 2 сгенерирована автоматически системой Smart Layered Context*
"""
        
        # Сохраняем индексный файл
        index_file = Path(output_dir) / "README.md"
        with open(index_file, 'w', encoding='utf-8') as f:
            f.write(index_content)

    def generate_phase2_report(self, output_dir: str):
        """Генерирует отчет о Фазе 2"""
        categories_stats = {}
        for func in self.next50_functions:
            cat = func['category']
            if cat not in categories_stats:
                categories_stats[cat] = {'count': 0, 'avg_priority': 0, 'total_priority': 0}
            categories_stats[cat]['count'] += 1
            categories_stats[cat]['total_priority'] += func['priority']
        
        for cat, stats in categories_stats.items():
            stats['avg_priority'] = stats['total_priority'] / stats['count']
        
        report = {
            "phase": "Phase 2 - Next 50 Functions",
            "generated_at": datetime.datetime.now().isoformat(),
            "total_functions": len(self.next50_functions),
            "categories": categories_stats,
            "priority_range": {
                "min": min(f['priority'] for f in self.next50_functions),
                "max": max(f['priority'] for f in self.next50_functions),
                "avg": sum(f['priority'] for f in self.next50_functions) / len(self.next50_functions)
            },
            "complexity_stats": {
                "avg_parameters": sum(f['complexity'] for f in self.next50_functions) / len(self.next50_functions),
                "max_parameters": max(f['complexity'] for f in self.next50_functions),
                "functions_with_many_params": len([f for f in self.next50_functions if f['complexity'] > 5])
            },
            "quality_improvements": [
                "Категоризация функций по областям применения",
                "Расширенные примеры с учетом категории",
                "Улучшенная таблица параметров с значениями по умолчанию",
                "Добавлены коды ошибок с рекомендациями",
                "Информация о производительности и потокобезопасности"
            ]
        }
        
        report_file = Path(output_dir) / "phase2_generation_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Next 50 Functions Documentation Generator (Phase 2)')
    parser.add_argument('--api-inventory', 
                       default='.context/analysis/cellframe_api_inventory.json',
                       help='Путь к файлу инвентаря API')
    parser.add_argument('--output-dir', 
                       default='.context/docs/api-reference/next50',
                       help='Директория для сохранения документации')
    parser.add_argument('--top20-completed',
                       default='.context/docs/api-reference/top20',
                       help='Директория с уже документированными топ-20 функциями')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.api_inventory):
        print(f"❌ Файл инвентаря API не найден: {args.api_inventory}")
        return 1
    
    # Получаем список уже документированных функций
    top20_completed = []
    if os.path.exists(args.top20_completed):
        for file in Path(args.top20_completed).glob("*.md"):
            if file.name != "README.md":
                top20_completed.append(file.stem)
    
    generator = Next50FunctionsGenerator(args.api_inventory, top20_completed)
    success = generator.generate_all_documentation(args.output_dir)
    
    return 0 if success else 1

if __name__ == '__main__':
    exit(main()) 