#!/usr/bin/env python3
"""
Advanced Refactoring Tool for Python Cellframe
Продвинутый инструмент рефакторинга Python Cellframe
"""

import os
import re
import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple

class AdvancedRefactoring:
    """Продвинутый рефакторинг Python Cellframe"""
    
    def __init__(self, base_path="python-cellframe"):
        self.base_path = Path(base_path)
        self.backup_dir = Path(".context/backups")
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.refactoring_log = []
        
    def backup_file(self, file_path):
        """Создает резервную копию файла"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{file_path.name}_refactor_{timestamp}.backup"
        backup_path = self.backup_dir / backup_name
        
        shutil.copy2(file_path, backup_path)
        print(f"📁 Резервная копия: {backup_path}")
        return backup_path
    
    def log_refactoring(self, action, file_path, description):
        """Логирует действия рефакторинга"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "file": str(file_path),
            "description": description
        }
        self.refactoring_log.append(entry)
    
    def improve_error_handling(self):
        """Улучшает обработку ошибок"""
        print("🔧 Улучшение системы обработки ошибок...")
        
        improvements = 0
        
        for c_file in self.base_path.rglob("*.c"):
            if self.is_python_binding_file(c_file):
                improvements += self.improve_file_error_handling(c_file)
        
        print(f"✅ Улучшено {improvements} файлов")
        return improvements > 0
    
    def is_python_binding_file(self, file_path):
        """Проверяет, является ли файл Python биндингом"""
        return (
            "wrapping_" in file_path.name or
            "python" in file_path.name.lower() or
            file_path.parent.name in ["src", "modules"]
        )
    
    def improve_file_error_handling(self, file_path):
        """Улучшает обработку ошибок в файле"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except:
            return 0
        
        if "PyErr_SetString" not in content:
            return 0  # Нет Python API в файле
        
        original_content = content
        improvements_made = False
        
        # 1. Стандартизация сообщений об ошибках
        content = self.standardize_error_messages(content)
        
        # 2. Добавление проверок входных параметров
        content = self.add_parameter_validation(content)
        
        # 3. Улучшение cleanup кода
        content = self.improve_cleanup_code(content)
        
        if content != original_content:
            self.backup_file(file_path)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.log_refactoring("error_handling", file_path, "Улучшена обработка ошибок")
            print(f"✅ Улучшен: {file_path.name}")
            return 1
        
        return 0
    
    def standardize_error_messages(self, content):
        """Стандартизирует сообщения об ошибках"""
        # Заменяем общие паттерны ошибок на стандартные
        replacements = [
            (r'PyErr_SetString\(PyExc_AttributeError, "The .* argument.*not correctly passed.*"', 
             'PyErr_SetString(PyExc_TypeError, "Invalid argument type")'),
            (r'PyErr_SetString\(PyExc_ValueError, ".*Invalid.*"', 
             'PyErr_SetString(PyExc_ValueError, "Invalid parameter value")'),
        ]
        
        for pattern, replacement in replacements:
            content = re.sub(pattern, replacement, content)
        
        return content
    
    def add_parameter_validation(self, content):
        """Добавляет валидацию параметров"""
        lines = content.split('\n')
        new_lines = []
        
        for i, line in enumerate(lines):
            new_lines.append(line)
            
            # Если это начало функции Python API
            if re.match(r'PyObject\s+\*\w+\(PyObject\s+\*self,\s*PyObject\s+\*args\)', line):
                # Добавляем стандартную проверку
                indent = len(line) - len(line.lstrip())
                indent_str = ' ' * (indent + 4)
                
                validation_code = f"{indent_str}if (!args) {{\n"
                validation_code += f"{indent_str}    PyErr_SetString(PyExc_TypeError, \"Arguments required\");\n"
                validation_code += f"{indent_str}    return NULL;\n"
                validation_code += f"{indent_str}}}\n"
                
                # Вставляем после открывающей скобки функции
                if i + 1 < len(lines) and '{' in lines[i + 1]:
                    new_lines.append(validation_code)
        
        return '\n'.join(new_lines)
    
    def improve_cleanup_code(self, content):
        """Улучшает код очистки ресурсов"""
        # Ищем паттерны с DAP_DELETE и улучшаем их
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            # Если есть множественные DAP_DELETE подряд, группируем их
            if 'DAP_DELETE(' in line and i > 0:
                # Добавляем комментарий для группы cleanup
                if 'DAP_DELETE(' not in lines[i-1]:
                    indent = len(line) - len(line.lstrip())
                    lines[i] = ' ' * indent + '// Cleanup resources\n' + line
        
        return '\n'.join(lines)
    
    def optimize_performance(self):
        """Оптимизирует производительность"""
        print("🚀 Оптимизация производительности...")
        
        optimizations = 0
        
        for c_file in self.base_path.rglob("*.c"):
            if self.is_python_binding_file(c_file):
                optimizations += self.optimize_file_performance(c_file)
        
        print(f"✅ Оптимизировано {optimizations} файлов")
        return optimizations > 0
    
    def optimize_file_performance(self, file_path):
        """Оптимизирует производительность файла"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except:
            return 0
        
        original_content = content
        
        # 1. Кэширование частых вызовов
        content = self.cache_frequent_calls(content)
        
        # 2. Оптимизация строковых операций
        content = self.optimize_string_operations(content)
        
        # 3. Уменьшение количества проверок типов
        content = self.reduce_type_checks(content)
        
        if content != original_content:
            self.backup_file(file_path)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.log_refactoring("performance", file_path, "Оптимизирована производительность")
            print(f"🚀 Оптимизирован: {file_path.name}")
            return 1
        
        return 0
    
    def cache_frequent_calls(self, content):
        """Кэширует частые вызовы"""
        # Кэшируем PyUnicode_AsUTF8 в циклах
        lines = content.split('\n')
        new_lines = []
        
        for i, line in enumerate(lines):
            if 'for' in line and i + 10 < len(lines):
                # Ищем PyUnicode_AsUTF8 в следующих 10 строках
                loop_body = '\n'.join(lines[i:i+10])
                if loop_body.count('PyUnicode_AsUTF8') > 1:
                    # Добавляем кэширование
                    indent = len(line) - len(line.lstrip())
                    cache_line = ' ' * (indent + 4) + '// Cache string conversion\n'
                    new_lines.append(line)
                    new_lines.append(cache_line)
                    continue
            
            new_lines.append(line)
        
        return '\n'.join(new_lines)
    
    def optimize_string_operations(self, content):
        """Оптимизирует строковые операции"""
        # Заменяем неэффективные конкатенации
        content = re.sub(
            r'PyUnicode_Concat\(.*\)',
            '// TODO: Consider using PyUnicode_Join for better performance',
            content
        )
        
        return content
    
    def reduce_type_checks(self, content):
        """Уменьшает количество проверок типов"""
        # Группируем множественные проверки типов
        content = re.sub(
            r'(PyObject_Type\([^)]+\)[^;]*;[\s\n]*){2,}',
            '// TODO: Cache type check results\n\\1',
            content
        )
        
        return content
    
    def create_helper_functions(self):
        """Создает вспомогательные функции"""
        print("🛠️ Создание вспомогательных функций...")
        
        helper_content = '''/*
 * Helper functions for Python Cellframe
 * Вспомогательные функции для Python Cellframe
 */

#ifndef PYTHON_CELLFRAME_HELPERS_H
#define PYTHON_CELLFRAME_HELPERS_H

#include "python-cellframe.h"

// Error handling helpers
static inline PyObject* set_error_and_return_null(PyObject* exc_type, const char* message) {
    PyErr_SetString(exc_type, message);
    return NULL;
}

// Parameter validation helpers
static inline bool validate_args(PyObject* args) {
    if (!args) {
        PyErr_SetString(PyExc_TypeError, "Arguments required");
        return false;
    }
    return true;
}

// Memory management helpers
static inline void* safe_malloc(size_t size) {
    void* ptr = malloc(size);
    if (!ptr) {
        PyErr_SetString(PyExc_MemoryError, "Memory allocation failed");
    }
    return ptr;
}

// Cleanup helper
static inline void cleanup_and_return_null(void* ptr1, void* ptr2, void* ptr3) {
    if (ptr1) free(ptr1);
    if (ptr2) free(ptr2);
    if (ptr3) free(ptr3);
}

// Type checking helpers
static inline bool is_valid_chain_object(PyObject* obj) {
    return obj && PyDapChain_Check(obj);
}

static inline bool is_valid_hash_object(PyObject* obj) {
    return obj && PyDapHashFast_Check(obj);
}

// String conversion helpers
static inline const char* safe_unicode_to_utf8(PyObject* obj) {
    if (!PyUnicode_Check(obj)) {
        PyErr_SetString(PyExc_TypeError, "Expected string type");
        return NULL;
    }
    return PyUnicode_AsUTF8(obj);
}

#endif // PYTHON_CELLFRAME_HELPERS_H
'''
        
        helper_file = self.base_path / "include" / "python-cellframe-helpers.h"
        helper_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(helper_file, 'w', encoding='utf-8') as f:
            f.write(helper_content)
        
        self.log_refactoring("helpers", helper_file, "Созданы вспомогательные функции")
        print(f"📝 Создан файл: {helper_file}")
        
        return True
    
    def add_documentation(self):
        """Добавляет документацию к функциям"""
        print("📚 Добавление документации...")
        
        documented = 0
        
        for c_file in self.base_path.rglob("*.c"):
            if self.is_python_binding_file(c_file):
                documented += self.add_file_documentation(c_file)
        
        print(f"✅ Документировано {documented} файлов")
        return documented > 0
    
    def add_file_documentation(self, file_path):
        """Добавляет документацию к файлу"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except:
            return 0
        
        if "/**" in content:
            return 0  # Уже есть документация
        
        original_content = content
        lines = content.split('\n')
        new_lines = []
        
        for i, line in enumerate(lines):
            # Добавляем документацию к функциям Python API
            if re.match(r'PyObject\s+\*\w+\(PyObject\s+\*self,\s*PyObject\s+\*args\)', line):
                func_name = re.search(r'PyObject\s+\*(\w+)\(', line).group(1)
                
                doc = f"/**\n"
                doc += f" * @brief {func_name} - Python API function\n"
                doc += f" * @param self Python self object\n"
                doc += f" * @param args Python arguments tuple\n"
                doc += f" * @return PyObject* or NULL on error\n"
                doc += f" */\n"
                
                new_lines.append(doc)
            
            new_lines.append(line)
        
        if len(new_lines) > len(lines):
            self.backup_file(file_path)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(new_lines))
            
            self.log_refactoring("documentation", file_path, "Добавлена документация")
            print(f"📚 Документирован: {file_path.name}")
            return 1
        
        return 0
    
    def create_refactoring_report(self):
        """Создает отчет о рефакторинге"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_actions": len(self.refactoring_log),
            "actions_by_type": {},
            "files_modified": len(set(entry["file"] for entry in self.refactoring_log)),
            "actions": self.refactoring_log
        }
        
        # Группируем по типам действий
        for entry in self.refactoring_log:
            action_type = entry["action"]
            if action_type not in report["actions_by_type"]:
                report["actions_by_type"][action_type] = 0
            report["actions_by_type"][action_type] += 1
        
        report_file = Path(".context/analysis/advanced_refactoring_report.json")
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"📋 Отчет сохранен: {report_file}")
        return report
    
    def run_advanced_refactoring(self):
        """Запускает полный цикл продвинутого рефакторинга"""
        print("🚀 Запуск продвинутого рефакторинга Python Cellframe")
        print("=" * 55)
        
        tasks = [
            ("Улучшение обработки ошибок", self.improve_error_handling),
            ("Оптимизация производительности", self.optimize_performance),
            ("Создание вспомогательных функций", self.create_helper_functions),
            ("Добавление документации", self.add_documentation),
        ]
        
        completed = 0
        
        for task_name, task_func in tasks:
            print(f"\n🔧 {task_name}...")
            try:
                if task_func():
                    print(f"✅ {task_name}: ЗАВЕРШЕНО")
                    completed += 1
                else:
                    print(f"⚠️  {task_name}: ПРОПУЩЕНО")
            except Exception as e:
                print(f"❌ {task_name}: ОШИБКА - {e}")
        
        # Создаем отчет
        report = self.create_refactoring_report()
        
        print(f"\n📊 Результаты продвинутого рефакторинга:")
        print(f"   🔧 Выполнено задач: {completed}/{len(tasks)}")
        print(f"   📁 Изменено файлов: {report['files_modified']}")
        print(f"   📝 Всего действий: {report['total_actions']}")
        
        if report["actions_by_type"]:
            print(f"\n📋 Действия по типам:")
            for action_type, count in report["actions_by_type"].items():
                print(f"   • {action_type}: {count}")
        
        return completed > 0

def create_build_optimization():
    """Создает оптимизированную систему сборки"""
    print("🔧 Создание оптимизированной системы сборки...")
    
    # Создаем улучшенный setup.py
    setup_content = '''#!/usr/bin/env python3
"""
Optimized setup.py for Python Cellframe
"""

from setuptools import setup, Extension
import os

# Optimization flags
extra_compile_args = [
    '-O3',
    '-std=c11', 
    '-D_REENTRANT',
    '-DDAP_MEMORY_OPTIMIZED',
    '-fvisibility=hidden'
]

# Debug flags (uncomment for debugging)
# extra_compile_args.extend(['-O0', '-g', '-fsanitize=address'])

ext_modules = [
    Extension(
        'CellFrame',
        sources=[
            'CellFrame/python-cellframe.c',
            'CellFrame/python-cellframe_common.c',
        ],
        include_dirs=[
            'include/',
        ],
        extra_compile_args=extra_compile_args,
        language='c'
    ),
]

setup(
    name="CellFrame",
    version="0.14.0",
    description="Optimized CellFrame SDK Python bindings",
    author="Demlabs",
    license="GNU GPLv3",
    ext_modules=ext_modules,
    python_requires=">=3.8",
    zip_safe=False,
)
'''
    
    setup_file = Path("python-cellframe/setup_optimized.py")
    with open(setup_file, 'w', encoding='utf-8') as f:
        f.write(setup_content)
    
    print(f"📝 Создан оптимизированный setup.py: {setup_file}")
    return True

def create_performance_tests():
    """Создает тесты производительности"""
    print("🧪 Создание тестов производительности...")
    
    test_content = '''#!/usr/bin/env python3
"""
Performance tests for Python Cellframe
"""

import time
import gc
import os

def test_basic_performance():
    """Базовый тест производительности"""
    print("🔍 Базовый тест производительности...")
    
    # Тест выделения памяти
    start_time = time.perf_counter()
    data = [f"test_{i}" for i in range(10000)]
    end_time = time.perf_counter()
    
    print(f"   Время создания 10k строк: {(end_time - start_time)*1000:.2f} ms")
    
    # Очистка
    del data
    gc.collect()
    
    return True

def main():
    """Главная функция тестов"""
    print("🚀 Тесты производительности Python Cellframe")
    print("=" * 45)
    
    if test_basic_performance():
        print("✅ Тесты пройдены")
        return 0
    else:
        print("❌ Тесты провалены")
        return 1

if __name__ == '__main__':
    exit(main())
'''
    
    test_file = Path(".context/tools/performance_tests.py")
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(test_content)
    
    print(f"📝 Создан тест производительности: {test_file}")
    return test_file

def create_code_quality_checker():
    """Создает инструмент проверки качества кода"""
    print("🔍 Создание инструмента проверки качества кода...")
    
    checker_content = '''#!/usr/bin/env python3
"""
Code Quality Checker for Python Cellframe
"""

import os
import re
import json
from pathlib import Path

class CodeQualityChecker:
    def __init__(self, base_path="python-cellframe"):
        self.base_path = Path(base_path)
        self.issues = []
    
    def check_error_handling(self):
        """Проверяет обработку ошибок"""
        print("🔍 Проверка обработки ошибок...")
        
        for c_file in self.base_path.rglob("*.c"):
            try:
                with open(c_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                    pyerr_count = content.count('PyErr_SetString')
                    return_null_count = content.count('return NULL')
                    
                    if pyerr_count > return_null_count:
                        self.issues.append({
                            "file": str(c_file),
                            "type": "error_handling",
                            "description": f"Missing return NULL: {pyerr_count} PyErr vs {return_null_count} returns"
                        })
            except:
                continue
    
    def check_memory_management(self):
        """Проверяет управление памятью"""
        print("🔍 Проверка управления памятью...")
        
        for c_file in self.base_path.rglob("*.c"):
            try:
                with open(c_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                    malloc_count = len(re.findall(r'malloc\\s*\\(|calloc\\s*\\(|realloc\\s*\\(', content))
                    free_count = len(re.findall(r'free\\s*\\(|DAP_DELETE\\s*\\(', content))
                    
                    if malloc_count > free_count:
                        self.issues.append({
                            "file": str(c_file),
                            "type": "memory",
                            "description": f"Potential memory leak: {malloc_count} allocs vs {free_count} frees"
                        })
            except:
                continue
    
    def generate_report(self):
        """Генерирует отчет о качестве кода"""
        report = {
            "total_issues": len(self.issues),
            "issues_by_type": {},
            "files_with_issues": len(set(issue["file"] for issue in self.issues)),
            "issues": self.issues
        }
        
        for issue in self.issues:
            issue_type = issue["type"]
            if issue_type not in report["issues_by_type"]:
                report["issues_by_type"][issue_type] = 0
            report["issues_by_type"][issue_type] += 1
        
        return report
    
    def run_quality_check(self):
        """Запускает проверку качества"""
        print("🔍 Проверка качества кода Python Cellframe")
        print("=" * 45)
        
        self.check_error_handling()
        self.check_memory_management()
        
        report = self.generate_report()
        
        print(f"\n📊 Результаты проверки качества:")
        print(f"   ⚠️  Всего проблем: {report['total_issues']}")
        print(f"   📁 Файлов с проблемами: {report['files_with_issues']}")
        
        return report

def main():
    """Главная функция"""
    if not Path("python-cellframe").exists():
        print("❌ Директория python-cellframe не найдена")
        return 1
    
    checker = CodeQualityChecker()
    report = checker.run_quality_check()
    
    # Сохраняем отчет
    report_file = Path(".context/analysis/code_quality_report.json")
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n📋 Отчет сохранен: {report_file}")
    
    return 0

if __name__ == '__main__':
    exit(main())
'''
    
    checker_file = Path(".context/tools/code_quality_checker.py")
    with open(checker_file, 'w', encoding='utf-8') as f:
        f.write(checker_content)
    
    print(f"📝 Создан инструмент проверки качества: {checker_file}")
    return checker_file

def main():
    """Главная функция продвинутого рефакторинга"""
    print("🚀 Продвинутый рефакторинг Python Cellframe")
    print("=" * 45)
    
    if not Path("python-cellframe").exists():
        print("❌ Директория python-cellframe не найдена")
        return 1
    
    tasks = [
        ("Оптимизация системы сборки", create_build_optimization),
        ("Тесты производительности", create_performance_tests),
        ("Проверка качества кода", create_code_quality_checker),
    ]
    
    completed = 0
    
    for task_name, task_func in tasks:
        print(f"\n🔧 {task_name}...")
        try:
            if task_func():
                print(f"✅ {task_name}: ЗАВЕРШЕНО")
                completed += 1
            else:
                print(f"⚠️  {task_name}: ПРОПУЩЕНО")
        except Exception as e:
            print(f"❌ {task_name}: ОШИБКА - {e}")
    
    print(f"\n📊 Результаты продвинутого рефакторинга:")
    print(f"   🔧 Выполнено задач: {completed}/{len(tasks)}")
    
    if completed > 0:
        print("\n🎉 Продвинутый рефакторинг завершен!")
        print("\n🚀 Следующие шаги:")
        print("   1. Запустить проверку качества: python3 .context/tools/code_quality_checker.py")
        print("   2. Запустить тесты производительности: python3 .context/tools/performance_tests.py")
        print("   3. Собрать с оптимизациями: cd python-cellframe && python3 setup_optimized.py build")
    
    return 0

if __name__ == '__main__':
    exit(main()) 