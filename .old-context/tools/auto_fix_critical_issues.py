#!/usr/bin/env python3
"""
Auto Fix Critical Issues in Python Cellframe
Автоматическое исправление критических проблем в Python Cellframe
"""

import os
import re
import json
import shutil
from pathlib import Path
from datetime import datetime

class CriticalIssueFixer:
    """Автоматический исправитель критических проблем"""
    
    def __init__(self, base_path="python-cellframe"):
        self.base_path = Path(base_path)
        self.backup_dir = Path(".context/backups")
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.fixes_applied = []
        
    def backup_file(self, file_path):
        """Создает резервную копию файла"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{file_path.name}_{timestamp}.backup"
        backup_path = self.backup_dir / backup_name
        
        shutil.copy2(file_path, backup_path)
        print(f"📁 Создана резервная копия: {backup_path}")
        return backup_path
    
    def fix_missing_return_null(self, file_path, line_number):
        """Исправляет отсутствие return NULL после PyErr_SetString"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except Exception as e:
            print(f"❌ Ошибка чтения файла {file_path}: {e}")
            return False
        
        if line_number > len(lines):
            print(f"❌ Неверный номер строки {line_number} в файле {file_path}")
            return False
        
        # Проверяем, что в строке есть PyErr_SetString
        target_line = lines[line_number - 1]
        if 'PyErr_SetString' not in target_line:
            print(f"❌ PyErr_SetString не найден в строке {line_number}")
            return False
        
        # Проверяем, нет ли уже return NULL в следующих строках
        for i in range(line_number, min(line_number + 3, len(lines))):
            if 'return NULL' in lines[i] or 'return' in lines[i]:
                print(f"⚠️  return уже есть в строке {i + 1}, пропускаем")
                return False
        
        # Определяем отступ
        indent = len(target_line) - len(target_line.lstrip())
        indent_str = ' ' * indent
        
        # Добавляем return NULL после строки с PyErr_SetString
        lines.insert(line_number, f"{indent_str}return NULL;\n")
        
        # Сохраняем файл
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            
            fix_info = {
                "type": "missing_return_null",
                "file": str(file_path),
                "line": line_number,
                "description": "Added return NULL after PyErr_SetString",
                "timestamp": datetime.now().isoformat()
            }
            self.fixes_applied.append(fix_info)
            print(f"✅ Исправлено: добавлен return NULL в {file_path}:{line_number}")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка записи файла {file_path}: {e}")
            return False
    
    def fix_malloc_null_check(self, file_path, line_number):
        """Добавляет проверку NULL после malloc"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except Exception as e:
            print(f"❌ Ошибка чтения файла {file_path}: {e}")
            return False
        
        if line_number > len(lines):
            print(f"❌ Неверный номер строки {line_number} в файле {file_path}")
            return False
        
        target_line = lines[line_number - 1]
        
        # Извлекаем имя переменной из malloc
        var_match = re.search(r'(\w+)\s*=\s*(?:malloc|calloc|realloc)\s*\(', target_line)
        if not var_match:
            print(f"❌ Не удалось найти переменную malloc в строке {line_number}")
            return False
        
        var_name = var_match.group(1)
        
        # Проверяем, нет ли уже проверки NULL
        for i in range(line_number, min(line_number + 5, len(lines))):
            if f'if' in lines[i] and var_name in lines[i] and 'NULL' in lines[i]:
                print(f"⚠️  Проверка NULL уже есть, пропускаем")
                return False
        
        # Определяем отступ
        indent = len(target_line) - len(target_line.lstrip())
        indent_str = ' ' * indent
        
        # Добавляем проверку NULL
        null_check = f"{indent_str}if ({var_name} == NULL) {{\n"
        null_check += f"{indent_str}    PyErr_SetString(PyExc_MemoryError, \"Memory allocation failed\");\n"
        null_check += f"{indent_str}    return NULL;\n"
        null_check += f"{indent_str}}}\n"
        
        lines.insert(line_number, null_check)
        
        # Сохраняем файл
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            
            fix_info = {
                "type": "malloc_null_check",
                "file": str(file_path),
                "line": line_number,
                "description": f"Added NULL check for {var_name}",
                "timestamp": datetime.now().isoformat()
            }
            self.fixes_applied.append(fix_info)
            print(f"✅ Исправлено: добавлена проверка NULL для {var_name} в {file_path}:{line_number}")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка записи файла {file_path}: {e}")
            return False
    
    def fix_critical_issues(self):
        """Исправляет все критические проблемы"""
        print("🔧 Автоматическое исправление критических проблем...")
        
        # Загружаем отчет с критическими проблемами
        report_file = Path(".context/analysis/detailed_issues_report.json")
        if not report_file.exists():
            print("❌ Отчет с проблемами не найден. Запустите сначала detailed_issue_analyzer.py")
            return False
        
        with open(report_file, 'r', encoding='utf-8') as f:
            report = json.load(f)
        
        critical_issues = []
        
        # Собираем все критические проблемы
        for category, issues in report["analysis_categories"].items():
            for issue in issues:
                if issue["severity"] == "HIGH":
                    critical_issues.append(issue)
        
        if not critical_issues:
            print("✅ Критических проблем не найдено!")
            return True
        
        print(f"🔍 Найдено {len(critical_issues)} критических проблем")
        
        fixed_count = 0
        
        for issue in critical_issues:
            file_path = Path(issue["file"])
            
            # Проверяем, что файл существует
            if not file_path.exists():
                print(f"⚠️  Файл не найден: {file_path}")
                continue
            
            # Создаем резервную копию
            self.backup_file(file_path)
            
            # Применяем исправление в зависимости от типа проблемы
            if "Missing return NULL after PyErr_SetString" in issue["issue"]:
                if self.fix_missing_return_null(file_path, issue["line"]):
                    fixed_count += 1
            
            elif "malloc/calloc result not checked for NULL" in issue["issue"]:
                if self.fix_malloc_null_check(file_path, issue["line"]):
                    fixed_count += 1
        
        print(f"\n📊 Результаты автоматического исправления:")
        print(f"   🔧 Исправлено проблем: {fixed_count}")
        print(f"   📁 Создано резервных копий: {len(os.listdir(self.backup_dir))}")
        
        # Сохраняем отчет об исправлениях
        fixes_report = {
            "timestamp": datetime.now().isoformat(),
            "total_fixes": len(self.fixes_applied),
            "fixes": self.fixes_applied
        }
        
        with open(".context/analysis/auto_fixes_report.json", 'w', encoding='utf-8') as f:
            json.dump(fixes_report, f, ensure_ascii=False, indent=2)
        
        print(f"📋 Отчет об исправлениях сохранен: .context/analysis/auto_fixes_report.json")
        
        return fixed_count > 0
    
    def create_manual_fix_guide(self):
        """Создает руководство по ручному исправлению"""
        print("📖 Создание руководства по ручному исправлению...")
        
        guide = {
            "title": "Руководство по исправлению проблем Python Cellframe",
            "timestamp": datetime.now().isoformat(),
            "sections": {
                "error_handling": {
                    "title": "Обработка ошибок",
                    "description": "Проблемы с обработкой ошибок Python API",
                    "fixes": [
                        {
                            "problem": "Missing return NULL after PyErr_SetString",
                            "solution": "Добавить 'return NULL;' после каждого PyErr_SetString",
                            "example_before": "PyErr_SetString(PyExc_ValueError, \"Invalid parameter\");",
                            "example_after": "PyErr_SetString(PyExc_ValueError, \"Invalid parameter\");\nreturn NULL;",
                            "priority": "CRITICAL"
                        }
                    ]
                },
                "memory_management": {
                    "title": "Управление памятью",
                    "description": "Проблемы с malloc/free и утечками памяти", 
                    "fixes": [
                        {
                            "problem": "malloc result not checked for NULL",
                            "solution": "Добавить проверку NULL после каждого malloc/calloc",
                            "example_before": "char *buffer = malloc(size);",
                            "example_after": "char *buffer = malloc(size);\nif (buffer == NULL) {\n    PyErr_SetString(PyExc_MemoryError, \"Memory allocation failed\");\n    return NULL;\n}",
                            "priority": "HIGH"
                        },
                        {
                            "problem": "Potential memory leak",
                            "solution": "Добавить free() для каждого malloc/calloc",
                            "example_before": "char *buffer = malloc(size);\n// use buffer\nreturn result;",
                            "example_after": "char *buffer = malloc(size);\n// use buffer\nfree(buffer);\nreturn result;",
                            "priority": "MEDIUM"
                        }
                    ]
                },
                "thread_safety": {
                    "title": "Потокобезопасность",
                    "description": "Проблемы с thread safety",
                    "fixes": [
                        {
                            "problem": "Non-const static variables",
                            "solution": "Использовать thread-local storage или синхронизацию",
                            "example_before": "static int counter = 0;",
                            "example_after": "__thread int counter = 0;  // или использовать mutex",
                            "priority": "MEDIUM"
                        }
                    ]
                },
                "best_practices": {
                    "title": "Лучшие практики",
                    "description": "Рекомендации по улучшению кода",
                    "practices": [
                        "Всегда проверяйте возвращаемые значения malloc/calloc",
                        "Используйте RAII паттерны где возможно",
                        "Добавляйте return NULL после PyErr_SetString",
                        "Избегайте глобальных и статических переменных",
                        "Используйте const для неизменяемых данных",
                        "Добавляйте комментарии к сложной логике"
                    ]
                }
            }
        }
        
        with open(".context/analysis/manual_fix_guide.json", 'w', encoding='utf-8') as f:
            json.dump(guide, f, ensure_ascii=False, indent=2)
        
        print("📋 Руководство сохранено: .context/analysis/manual_fix_guide.json")
        
        return guide

def main():
    """Главная функция"""
    if not Path("python-cellframe").exists():
        print("❌ Директория python-cellframe не найдена")
        return 1
    
    fixer = CriticalIssueFixer()
    
    print("🔧 Автоматическое исправление критических проблем Python Cellframe")
    print("=" * 60)
    
    # Исправляем критические проблемы
    success = fixer.fix_critical_issues()
    
    # Создаем руководство по ручному исправлению
    fixer.create_manual_fix_guide()
    
    if success:
        print("\n✅ Автоматическое исправление завершено успешно!")
        print("📋 Проверьте файлы и протестируйте изменения")
        print("📁 Резервные копии сохранены в .context/backups/")
    else:
        print("\n⚠️  Не удалось исправить все проблемы автоматически")
        print("📖 Используйте руководство по ручному исправлению")
    
    return 0

if __name__ == '__main__':
    exit(main()) 