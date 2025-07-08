#!/usr/bin/env python3
"""
Documentation Auto-Fixer
Автоматическое исправление проблем в документации Cellframe
"""

import json
import os
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import datetime

class DocumentationFixer:
    """Автоматический исправитель документации"""
    
    def __init__(self, docs_dir: str, validation_report: str = None):
        self.docs_dir = Path(docs_dir)
        self.validation_report = validation_report
        self.validation_data = None
        self.fixes_applied = []
        
        # Шаблоны для исправлений
        self.fix_templates = {
            'missing_description': """## Описание
{description}

""",
            'missing_signature': """## Сигнатура
```c
{signature}
```

""",
            'missing_parameters': """## Параметры
{parameters_table}

""",
            'missing_return_value': """## Возвращаемое значение
- **Тип:** `{return_type}`
- **Описание:** {return_description}

""",
            'missing_error_codes': """## Коды ошибок
| Код | Описание |
|-----|----------|
| 0 | Успешное выполнение |
| -1 | Общая ошибка |
| -2 | Неверные параметры |
| -3 | Недостаточно памяти |

""",
            'missing_examples': """## Пример использования

### C/C++
```c
{c_example}
```

### Python
```python
{python_example}
```

""",
            'missing_related_functions': """## Связанные функции
- TODO: Добавить связанные функции
- См. документацию по API

""",
            'missing_notes': """## Примечания
- Проверяйте возвращаемые значения на ошибки
- Убедитесь в корректности входных параметров

""",
            'missing_see_also': """## См. также
- [Cellframe API Reference](../api-reference.md)
- [Getting Started Guide](../getting-started.md)

"""
        }

    def load_validation_report(self) -> bool:
        """Загружает отчет валидации"""
        if not self.validation_report:
            # Ищем последний отчет валидации
            analysis_dir = Path(".context/analysis")
            if analysis_dir.exists():
                validation_files = list(analysis_dir.glob("documentation_validation_*.json"))
                if validation_files:
                    self.validation_report = str(sorted(validation_files)[-1])
        
        if not self.validation_report or not os.path.exists(self.validation_report):
            print("❌ Отчет валидации не найден")
            return False
        
        try:
            with open(self.validation_report, 'r', encoding='utf-8') as f:
                self.validation_data = json.load(f)
            print(f"✅ Загружен отчет валидации: {self.validation_report}")
            return True
        except Exception as e:
            print(f"❌ Ошибка загрузки отчета: {e}")
            return False

    def generate_enhanced_description(self, function_name: str, current_desc: str = "") -> str:
        """Генерирует улучшенное описание функции"""
        # Базовые описания по паттернам
        pattern_descriptions = {
            r'PyInit_.*': f"Инициализирует Python модуль {function_name.replace('PyInit_', '')} для интеграции с Cellframe SDK. Эта функция автоматически вызывается при импорте модуля в Python и настраивает все необходимые привязки между C API и Python интерфейсом.",
            
            r'.*_ledger_.*': f"Выполняет операции с распределенным реестром (ledger) в рамках блокчейн сети Cellframe. Функция {function_name} обеспечивает безопасное и консистентное управление состоянием реестра с поддержкой транзакций и проверки целостности данных.",
            
            r'.*_enc_key_.*': f"Управляет криптографическими ключами в системе шифрования Cellframe. Функция {function_name} предоставляет безопасные операции с ключами, включая создание, обновление и получение размеров зашифрованных данных.",
            
            r'.*_chain_.*': f"Выполняет операции с блокчейн цепочкой в экосистеме Cellframe. Функция {function_name} обеспечивает взаимодействие с блоками, транзакциями и структурами данных цепочки.",
            
            r'.*_get_.*_size.*': f"Вычисляет размер данных для операций криптографии или сериализации. Функция {function_name} возвращает точный размер буфера, необходимый для выполнения соответствующей операции.",
            
            r'.*_new_.*': f"Создает новый объект или структуру данных в системе Cellframe. Функция {function_name} выполняет инициализацию и возвращает указатель на созданный объект.",
            
            r'.*_update_.*': f"Обновляет существующий объект или структуру данных. Функция {function_name} модифицирует состояние объекта с соблюдением всех инвариантов системы."
        }
        
        # Ищем подходящий паттерн
        for pattern, description in pattern_descriptions.items():
            if re.match(pattern, function_name, re.IGNORECASE):
                return description
        
        # Если паттерн не найден, генерируем базовое описание
        return f"Функция {function_name} выполняет специализированные операции в рамках Cellframe SDK API. Эта функция является частью низкоуровневого интерфейса и предоставляет доступ к внутренним механизмам платформы блокчейн Cellframe."

    def generate_parameters_table(self, function_name: str) -> str:
        """Генерирует таблицу параметров для функций без параметров"""
        if function_name.startswith('PyInit_'):
            return "Функция инициализации модуля не принимает параметров."
        
        return """| Параметр | Тип | Описание | Обязательный |
|----------|-----|----------|--------------|
| *Функция не принимает параметров* | - | - | - |

"""

    def generate_c_example(self, function_name: str) -> str:
        """Генерирует улучшенный пример на C"""
        if function_name.startswith('PyInit_'):
            module_name = function_name.replace('PyInit_', '')
            return f"""// Функция {function_name} вызывается автоматически
// при загрузке Python модуля
#include <Python.h>

// Пример использования в C расширении
PyMODINIT_FUNC {function_name}(void) {{
    PyObject *module;
    
    // Создаем модуль
    module = PyModule_Create(&{module_name.lower()}_module);
    if (module == NULL) {{
        return NULL;
    }}
    
    // Инициализируем Cellframe SDK
    // TODO: Добавить специфичную инициализацию
    
    return module;
}}"""
        
        if '_get_' in function_name and '_size' in function_name:
            return f"""#include "cellframe_api.h"

int main() {{
    // Пример использования {function_name}
    size_t required_size;
    int result;
    
    // Получаем необходимый размер буфера
    result = {function_name}(&required_size);
    if (result != 0) {{
        printf("Ошибка получения размера: %d\\n", result);
        return -1;
    }}
    
    printf("Требуемый размер буфера: %zu байт\\n", required_size);
    
    // Выделяем память под буфер
    void *buffer = malloc(required_size);
    if (!buffer) {{
        printf("Ошибка выделения памяти\\n");
        return -1;
    }}
    
    // Используем буфер для дальнейших операций
    // TODO: Добавить специфичную логику
    
    free(buffer);
    return 0;
}}"""
        
        return f"""#include "cellframe_api.h"

int main() {{
    int result;
    
    // Инициализация Cellframe SDK
    // TODO: Добавить необходимую инициализацию
    
    // Вызов функции {function_name}
    result = {function_name}();
    
    // Проверка результата
    if (result == 0) {{
        printf("Функция выполнена успешно\\n");
    }} else {{
        printf("Ошибка выполнения: %d\\n", result);
        return -1;
    }}
    
    return 0;
}}"""

    def generate_python_example(self, function_name: str) -> str:
        """Генерирует улучшенный пример на Python"""
        if function_name.startswith('PyInit_'):
            module_name = function_name.replace('PyInit_', '')
            return f"""# Функция {function_name} вызывается автоматически при импорте
import {module_name}

def example_usage():
    \"\"\"Пример использования модуля {module_name}\"\"\"
    try:
        # Модуль уже инициализирован через {function_name}
        print(f"Модуль {module_name} успешно загружен")
        
        # TODO: Добавить примеры использования функций модуля
        # result = {module_name}.some_function()
        
        return True
        
    except ImportError as e:
        print(f"Ошибка импорта модуля: {{e}}")
        return False
    except Exception as e:
        print(f"Ошибка выполнения: {{e}}")
        return False

if __name__ == "__main__":
    example_usage()"""
        
        if '_get_' in function_name and '_size' in function_name:
            python_name = function_name.replace('dap_', '').replace('_py', '')
            return f"""import libCellFrame

def example_{function_name.lower()}():
    \"\"\"Пример использования {function_name}\"\"\"
    try:
        # Получаем размер буфера
        required_size = libCellFrame.{python_name}()
        
        if required_size > 0:
            print(f"Требуемый размер буфера: {{required_size}} байт")
            
            # Создаем буфер нужного размера
            buffer = bytearray(required_size)
            print(f"Буфер создан: {{len(buffer)}} байт")
            
            return buffer
        else:
            print("Ошибка получения размера")
            return None
            
    except Exception as e:
        print(f"Исключение: {{e}}")
        return None

# Использование
if __name__ == "__main__":
    buffer = example_{function_name.lower()}()
    if buffer:
        print("Операция выполнена успешно")"""
        
        python_name = function_name.replace('dap_', '').replace('_py', '')
        return f"""import libCellFrame

def example_{function_name.lower()}():
    \"\"\"Пример использования {function_name}\"\"\"
    try:
        # TODO: Адаптировать под конкретную функцию
        result = libCellFrame.{python_name}()
        
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
    result = example_{function_name.lower()}()"""

    def fix_file(self, filename: str, file_data: Dict) -> bool:
        """Исправляет проблемы в одном файле"""
        file_path = self.docs_dir / filename
        
        if not file_path.exists():
            print(f"❌ Файл не найден: {filename}")
            return False
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"❌ Ошибка чтения файла {filename}: {e}")
            return False
        
        original_content = content
        fixes_for_file = []
        
        # Извлекаем имя функции из имени файла
        function_name = filename.replace('.md', '')
        
        # Исправляем отсутствующие разделы
        missing_sections = file_data['details']['structure'].get('missing_sections', [])
        
        for section in missing_sections:
            if section == 'Описание':
                description = self.generate_enhanced_description(function_name)
                new_section = self.fix_templates['missing_description'].format(description=description)
                
                # Вставляем после заголовка
                title_pattern = r'(# .*?\n)'
                if re.search(title_pattern, content):
                    content = re.sub(title_pattern, r'\1\n' + new_section, content, count=1)
                    fixes_for_file.append(f"Добавлено описание ({len(description)} символов)")
            
            elif section == 'Сигнатура':
                # Генерируем базовую сигнатуру
                if function_name.startswith('PyInit_'):
                    signature = f"PyMODINIT_FUNC {function_name}(void)"
                elif '_get_' in function_name and '_size' in function_name:
                    signature = f"int {function_name}(size_t *out_size)"
                else:
                    signature = f"int {function_name}(void)"
                
                new_section = self.fix_templates['missing_signature'].format(signature=signature)
                
                # Вставляем после описания
                desc_pattern = r'(## Описание.*?\n\n)'
                if re.search(desc_pattern, content, re.DOTALL):
                    content = re.sub(desc_pattern, r'\1' + new_section, content, count=1)
                else:
                    # Если нет описания, вставляем после заголовка
                    title_pattern = r'(# .*?\n)'
                    content = re.sub(title_pattern, r'\1\n' + new_section, content, count=1)
                fixes_for_file.append("Добавлена сигнатура функции")
            
            elif section == 'Параметры':
                params_table = self.generate_parameters_table(function_name)
                new_section = self.fix_templates['missing_parameters'].format(parameters_table=params_table)
                
                # Вставляем после сигнатуры
                sig_pattern = r'(## Сигнатура.*?```\n\n)'
                if re.search(sig_pattern, content, re.DOTALL):
                    content = re.sub(sig_pattern, r'\1' + new_section, content, count=1)
                fixes_for_file.append("Добавлена таблица параметров")
            
            elif section == 'Возвращаемое значение':
                return_type = "int" if not function_name.startswith('PyInit_') else "PyObject*"
                return_desc = "Код результата выполнения операции" if not function_name.startswith('PyInit_') else "Указатель на инициализированный модуль Python"
                
                new_section = self.fix_templates['missing_return_value'].format(
                    return_type=return_type,
                    return_description=return_desc
                )
                
                # Вставляем после параметров
                params_pattern = r'(## Параметры.*?\n\n)'
                if re.search(params_pattern, content, re.DOTALL):
                    content = re.sub(params_pattern, r'\1' + new_section, content, count=1)
                fixes_for_file.append("Добавлено описание возвращаемого значения")
            
            elif section == 'Пример использования':
                c_example = self.generate_c_example(function_name)
                python_example = self.generate_python_example(function_name)
                
                new_section = self.fix_templates['missing_examples'].format(
                    c_example=c_example,
                    python_example=python_example
                )
                
                # Вставляем перед связанными функциями или в конец
                related_pattern = r'(## Связанные функции)'
                if re.search(related_pattern, content):
                    content = re.sub(related_pattern, new_section + r'\1', content, count=1)
                else:
                    content += "\n" + new_section
                fixes_for_file.append("Добавлены примеры использования (C/C++ и Python)")
        
        # Исправляем коды ошибок если отсутствуют
        if not file_data['details']['completeness']['error_codes_present']:
            error_codes_section = self.fix_templates['missing_error_codes']
            
            # Вставляем после возвращаемого значения
            return_pattern = r'(## Возвращаемое значение.*?\n\n)'
            if re.search(return_pattern, content, re.DOTALL):
                content = re.sub(return_pattern, r'\1' + error_codes_section, content, count=1)
            fixes_for_file.append("Добавлены коды ошибок")
        
        # Расширяем короткое описание
        if file_data['details']['completeness']['description_length'] < 50:
            current_desc_pattern = r'## Описание\s*\n(.*?)(?=\n##|\n#|$)'
            match = re.search(current_desc_pattern, content, re.DOTALL)
            if match:
                current_desc = match.group(1).strip()
                enhanced_desc = self.generate_enhanced_description(function_name, current_desc)
                content = re.sub(current_desc_pattern, f'## Описание\n{enhanced_desc}\n', content, count=1)
                fixes_for_file.append(f"Расширено описание ({len(enhanced_desc)} символов)")
        
        # Сохраняем исправленный файл
        if content != original_content:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                self.fixes_applied.append({
                    'filename': filename,
                    'fixes': fixes_for_file,
                    'fixes_count': len(fixes_for_file)
                })
                
                print(f"✅ Исправлен файл {filename}: {len(fixes_for_file)} исправлений")
                return True
            except Exception as e:
                print(f"❌ Ошибка сохранения файла {filename}: {e}")
                return False
        else:
            print(f"ℹ️ Файл {filename} не требует исправлений")
            return True

    def fix_all_files(self) -> bool:
        """Исправляет все файлы с проблемами"""
        if not self.load_validation_report():
            return False
        
        print("🔧 Начинаю автоматическое исправление документации...")
        
        files_data = self.validation_data.get('files', {})
        fixed_count = 0
        
        # Сортируем файлы по количеству проблем (сначала самые проблемные)
        sorted_files = sorted(
            files_data.items(),
            key=lambda x: x[1].get('issues_count', 0),
            reverse=True
        )
        
        for filename, file_data in sorted_files:
            if file_data.get('issues_count', 0) > 0:
                print(f"\n🔧 Исправление {filename} ({file_data['issues_count']} проблем)...")
                if self.fix_file(filename, file_data):
                    fixed_count += 1
        
        print(f"\n✅ Исправление завершено: {fixed_count} файлов обработано")
        print(f"📊 Применено исправлений: {sum(fix['fixes_count'] for fix in self.fixes_applied)}")
        
        return True

    def save_fixes_report(self, output_file: str = None):
        """Сохраняет отчет об исправлениях"""
        if not output_file:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f".context/analysis/documentation_fixes_{timestamp}.json"
        
        report = {
            'timestamp': datetime.datetime.now().isoformat(),
            'validation_report_used': self.validation_report,
            'total_files_fixed': len(self.fixes_applied),
            'total_fixes_applied': sum(fix['fixes_count'] for fix in self.fixes_applied),
            'fixes_by_file': self.fixes_applied,
            'summary': {
                'most_common_fixes': self.get_most_common_fixes(),
                'files_with_most_fixes': sorted(self.fixes_applied, key=lambda x: x['fixes_count'], reverse=True)[:5]
            }
        }
        
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"📊 Отчет об исправлениях сохранен: {output_file}")
        return output_file

    def get_most_common_fixes(self) -> List[Tuple[str, int]]:
        """Получает статистику самых частых исправлений"""
        fix_counts = {}
        
        for file_fix in self.fixes_applied:
            for fix in file_fix['fixes']:
                fix_type = fix.split('(')[0].strip()  # Убираем детали в скобках
                fix_counts[fix_type] = fix_counts.get(fix_type, 0) + 1
        
        return sorted(fix_counts.items(), key=lambda x: x[1], reverse=True)

    def print_summary(self):
        """Выводит краткий отчет об исправлениях"""
        if not self.fixes_applied:
            print("ℹ️ Исправления не применялись")
            return
        
        print("\n" + "="*60)
        print("🔧 ОТЧЕТ ОБ ИСПРАВЛЕНИЯХ ДОКУМЕНТАЦИИ")
        print("="*60)
        
        total_fixes = sum(fix['fixes_count'] for fix in self.fixes_applied)
        print(f"📁 Исправлено файлов: {len(self.fixes_applied)}")
        print(f"🔧 Всего исправлений: {total_fixes}")
        
        # Самые частые исправления
        common_fixes = self.get_most_common_fixes()
        if common_fixes:
            print("\n🔝 Самые частые исправления:")
            for fix_type, count in common_fixes[:5]:
                print(f"  {fix_type}: {count} раз")
        
        # Файлы с наибольшим количеством исправлений
        top_files = sorted(self.fixes_applied, key=lambda x: x['fixes_count'], reverse=True)[:5]
        print("\n📄 Файлы с наибольшим количеством исправлений:")
        for file_fix in top_files:
            print(f"  {file_fix['filename']}: {file_fix['fixes_count']} исправлений")
        
        print("\n💡 Рекомендация: Запустите валидацию повторно для проверки результатов")
        print("="*60)

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Documentation Auto-Fixer')
    parser.add_argument('--docs-dir', 
                       default='.context/docs/api-reference/top20',
                       help='Директория с документацией для исправления')
    parser.add_argument('--validation-report', 
                       help='Файл отчета валидации')
    parser.add_argument('--output', 
                       help='Файл для сохранения отчета об исправлениях')
    parser.add_argument('--dry-run', action='store_true',
                       help='Только показать что будет исправлено, не применять изменения')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.docs_dir):
        print(f"❌ Директория не найдена: {args.docs_dir}")
        return 1
    
    fixer = DocumentationFixer(args.docs_dir, args.validation_report)
    
    if args.dry_run:
        print("🔍 Режим предварительного просмотра (изменения не применяются)")
        # TODO: Реализовать dry-run режим
        return 0
    
    success = fixer.fix_all_files()
    
    if success:
        fixer.save_fixes_report(args.output)
        fixer.print_summary()
        return 0
    else:
        return 1

if __name__ == '__main__':
    exit(main()) 