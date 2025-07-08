#!/usr/bin/env python3
"""
Detailed Issue Analyzer for Python Cellframe
Детальный анализатор конкретных проблем в Python Cellframe
"""

import os
import re
import json
from pathlib import Path
from datetime import datetime

def analyze_error_handling_issues():
    """Анализирует проблемы обработки ошибок"""
    print("🔍 Анализ проблем обработки ошибок...")
    
    issues = []
    base_path = Path("python-cellframe")
    
    for c_file in base_path.rglob("*.c"):
        try:
            with open(c_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.split('\n')
        except:
            continue
        
        # Ищем PyErr_SetString без последующего return NULL
        for i, line in enumerate(lines):
            if 'PyErr_SetString' in line:
                # Проверяем следующие 3 строки на наличие return NULL
                next_lines = '\n'.join(lines[i+1:i+4])
                if 'return NULL' not in next_lines and 'return' not in next_lines:
                    issues.append({
                        "file": str(c_file),
                        "line": i + 1,
                        "issue": "Missing return NULL after PyErr_SetString",
                        "code": line.strip(),
                        "severity": "HIGH",
                        "fix": "Add 'return NULL;' after error setting"
                    })
    
    return issues

def analyze_memory_management():
    """Анализирует проблемы управления памятью"""
    print("🔍 Анализ управления памятью...")
    
    issues = []
    base_path = Path("python-cellframe")
    
    for c_file in base_path.rglob("*.c"):
        try:
            with open(c_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.split('\n')
        except:
            continue
        
        # Ищем malloc без проверки на NULL
        for i, line in enumerate(lines):
            if re.search(r'=\s*malloc\s*\(|=\s*calloc\s*\(|=\s*realloc\s*\(', line):
                # Проверяем следующие 5 строк на проверку NULL
                next_lines = '\n'.join(lines[i+1:i+6])
                if 'if' not in next_lines or 'NULL' not in next_lines:
                    issues.append({
                        "file": str(c_file),
                        "line": i + 1,
                        "issue": "malloc/calloc result not checked for NULL",
                        "code": line.strip(),
                        "severity": "HIGH",
                        "fix": "Add NULL check: if (ptr == NULL) { handle error; }"
                    })
        
        # Ищем потенциальные утечки памяти
        malloc_lines = []
        free_lines = []
        
        for i, line in enumerate(lines):
            if re.search(r'malloc\s*\(|calloc\s*\(|realloc\s*\(', line):
                # Извлекаем имя переменной
                var_match = re.search(r'(\w+)\s*=.*(?:malloc|calloc|realloc)', line)
                if var_match:
                    malloc_lines.append((i + 1, var_match.group(1)))
            
            if 'free(' in line:
                var_match = re.search(r'free\s*\(\s*(\w+)\s*\)', line)
                if var_match:
                    free_lines.append((i + 1, var_match.group(1)))
        
        # Проверяем соответствие malloc/free
        malloc_vars = {var for _, var in malloc_lines}
        free_vars = {var for _, var in free_lines}
        
        unfreed_vars = malloc_vars - free_vars
        for line_num, var in malloc_lines:
            if var in unfreed_vars:
                issues.append({
                    "file": str(c_file),
                    "line": line_num,
                    "issue": f"Potential memory leak: variable '{var}' allocated but not freed",
                    "code": lines[line_num - 1].strip() if line_num <= len(lines) else "",
                    "severity": "MEDIUM",
                    "fix": f"Add free({var}); before function returns"
                })
    
    return issues

def analyze_thread_safety():
    """Анализирует проблемы thread safety"""
    print("🔍 Анализ thread safety...")
    
    issues = []
    base_path = Path("python-cellframe")
    
    for c_file in base_path.rglob("*.c"):
        try:
            with open(c_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.split('\n')
        except:
            continue
        
        # Ищем статические переменные
        for i, line in enumerate(lines):
            if re.search(r'static\s+(?!const)\w+.*=', line):
                # Исключаем константы и функции
                if 'const' not in line and '(' not in line:
                    issues.append({
                        "file": str(c_file),
                        "line": i + 1,
                        "issue": "Non-const static variable may cause thread safety issues",
                        "code": line.strip(),
                        "severity": "MEDIUM",
                        "fix": "Consider thread-local storage (__thread) or proper synchronization"
                    })
    
    return issues

def analyze_api_consistency():
    """Анализирует консистентность API"""
    print("🔍 Анализ консистентности API...")
    
    issues = []
    base_path = Path("python-cellframe")
    api_functions = {}
    
    # Собираем все API функции
    for c_file in base_path.rglob("*.c"):
        try:
            with open(c_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except:
            continue
        
        # Ищем PyMethodDef структуры
        method_matches = re.finditer(r'{\s*"(\w+)"\s*,\s*(\w+)\s*,\s*(METH_\w+)', content)
        for match in method_matches:
            func_name = match.group(1)
            c_func_name = match.group(2)
            method_type = match.group(3)
            
            if func_name not in api_functions:
                api_functions[func_name] = []
            
            api_functions[func_name].append({
                "file": str(c_file),
                "c_function": c_func_name,
                "method_type": method_type
            })
    
    # Анализируем паттерны именования
    naming_patterns = {}
    for func_name in api_functions.keys():
        if '_' in func_name:
            prefix = func_name.split('_')[0]
            if prefix not in naming_patterns:
                naming_patterns[prefix] = []
            naming_patterns[prefix].append(func_name)
    
    # Проверяем консистентность
    for prefix, funcs in naming_patterns.items():
        if len(funcs) > 1:
            # Проверяем стили именования
            snake_case = [f for f in funcs if f.islower() and '_' in f]
            camel_case = [f for f in funcs if any(c.isupper() for c in f[1:])]
            
            if snake_case and camel_case:
                issues.append({
                    "file": "API",
                    "line": 0,
                    "issue": f"Mixed naming styles in {prefix} functions",
                    "code": f"snake_case: {snake_case[:3]}, camelCase: {camel_case[:3]}",
                    "severity": "LOW",
                    "fix": "Standardize on one naming convention (prefer snake_case)"
                })
    
    return issues

def analyze_performance_issues():
    """Анализирует проблемы производительности"""
    print("🔍 Анализ производительности...")
    
    issues = []
    base_path = Path("python-cellframe")
    
    for c_file in base_path.rglob("*.c"):
        try:
            with open(c_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.split('\n')
        except:
            continue
        
        # Ищем неэффективные паттерны
        for i, line in enumerate(lines):
            # Частые вызовы PyUnicode_AsUTF8 в циклах
            if 'for' in line.lower() and i + 5 < len(lines):
                loop_body = '\n'.join(lines[i:i+5])
                if loop_body.count('PyUnicode_AsUTF8') > 1:
                    issues.append({
                        "file": str(c_file),
                        "line": i + 1,
                        "issue": "Multiple PyUnicode_AsUTF8 calls in loop",
                        "code": line.strip(),
                        "severity": "MEDIUM",
                        "fix": "Cache string conversion outside loop"
                    })
            
            # Избыточные проверки типов
            if line.count('PyObject_Type') > 1:
                issues.append({
                    "file": str(c_file),
                    "line": i + 1,
                    "issue": "Multiple type checks on same line",
                    "code": line.strip(),
                    "severity": "LOW",
                    "fix": "Cache type check result"
                })
            
            # Неэффективная конкатенация строк
            if 'PyUnicode_Concat' in line and ('for' in lines[max(0, i-3):i] or 'while' in lines[max(0, i-3):i]):
                issues.append({
                    "file": str(c_file),
                    "line": i + 1,
                    "issue": "String concatenation in loop",
                    "code": line.strip(),
                    "severity": "MEDIUM",
                    "fix": "Use PyUnicode_Join or build list first"
                })
    
    return issues

def generate_detailed_report():
    """Генерирует детальный отчет по всем проблемам"""
    print("📋 Генерация детального отчета...")
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "analysis_categories": {
            "error_handling": analyze_error_handling_issues(),
            "memory_management": analyze_memory_management(),
            "thread_safety": analyze_thread_safety(),
            "api_consistency": analyze_api_consistency(),
            "performance": analyze_performance_issues()
        }
    }
    
    # Подсчитываем статистику
    total_issues = sum(len(issues) for issues in report["analysis_categories"].values())
    
    severity_counts = {
        "HIGH": 0,
        "MEDIUM": 0,
        "LOW": 0
    }
    
    for category_issues in report["analysis_categories"].values():
        for issue in category_issues:
            severity_counts[issue["severity"]] += 1
    
    report["summary"] = {
        "total_issues": total_issues,
        "severity_breakdown": severity_counts,
        "categories_breakdown": {
            category: len(issues) 
            for category, issues in report["analysis_categories"].items()
        }
    }
    
    return report

def create_refactoring_tasks():
    """Создает конкретные задачи для рефакторинга"""
    print("📝 Создание задач рефакторинга...")
    
    report = generate_detailed_report()
    
    tasks = {
        "immediate_fixes": [],
        "short_term": [],
        "long_term": []
    }
    
    # Группируем задачи по приоритету
    for category, issues in report["analysis_categories"].items():
        for issue in issues:
            task = {
                "category": category,
                "file": Path(issue["file"]).name,
                "line": issue["line"],
                "description": issue["issue"],
                "fix": issue["fix"],
                "estimated_time": "30min" if issue["severity"] == "HIGH" else "15min"
            }
            
            if issue["severity"] == "HIGH":
                tasks["immediate_fixes"].append(task)
            elif issue["severity"] == "MEDIUM":
                tasks["short_term"].append(task)
            else:
                tasks["long_term"].append(task)
    
    # Добавляем архитектурные задачи
    tasks["architectural_improvements"] = [
        {
            "category": "architecture",
            "description": "Создать единую систему error handling",
            "estimated_time": "2-3 дня",
            "priority": "HIGH"
        },
        {
            "category": "architecture", 
            "description": "Внедрить RAII паттерны для управления памятью",
            "estimated_time": "1 неделя",
            "priority": "MEDIUM"
        },
        {
            "category": "architecture",
            "description": "Создать thread-safe API wrapper",
            "estimated_time": "3-5 дней",
            "priority": "MEDIUM"
        },
        {
            "category": "testing",
            "description": "Добавить unit тесты для всех API функций",
            "estimated_time": "2 недели",
            "priority": "HIGH"
        },
        {
            "category": "documentation",
            "description": "Создать API документацию с примерами",
            "estimated_time": "1 неделя",
            "priority": "MEDIUM"
        }
    ]
    
    return tasks

def main():
    """Главная функция"""
    if not Path("python-cellframe").exists():
        print("❌ Директория python-cellframe не найдена")
        return 1
    
    # Генерируем детальный отчет
    report = generate_detailed_report()
    
    # Создаем задачи рефакторинга
    tasks = create_refactoring_tasks()
    
    # Выводим сводку
    print("\n📊 Детальный анализ Python Cellframe:")
    print(f"   ⚠️  Всего проблем: {report['summary']['total_issues']}")
    print(f"   🔴 Высокий приоритет: {report['summary']['severity_breakdown']['HIGH']}")
    print(f"   🟡 Средний приоритет: {report['summary']['severity_breakdown']['MEDIUM']}")
    print(f"   🟢 Низкий приоритет: {report['summary']['severity_breakdown']['LOW']}")
    
    print("\n📋 Проблемы по категориям:")
    for category, count in report['summary']['categories_breakdown'].items():
        print(f"   • {category}: {count} проблем")
    
    print(f"\n🚨 Немедленные исправления: {len(tasks['immediate_fixes'])} задач")
    print(f"📅 Краткосрочные: {len(tasks['short_term'])} задач")
    print(f"🎯 Долгосрочные: {len(tasks['long_term'])} задач")
    
    # Сохраняем отчеты
    output_dir = Path(".context/analysis")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    with open(output_dir / "detailed_issues_report.json", 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    with open(output_dir / "refactoring_tasks.json", 'w', encoding='utf-8') as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)
    
    print(f"\n📋 Детальный отчет сохранен: {output_dir / 'detailed_issues_report.json'}")
    print(f"📋 Задачи рефакторинга: {output_dir / 'refactoring_tasks.json'}")
    
    # Показываем топ-5 критических проблем
    if tasks['immediate_fixes']:
        print("\n🔥 Топ-5 критических проблем:")
        for i, task in enumerate(tasks['immediate_fixes'][:5], 1):
            print(f"   {i}. {task['file']}:{task['line']} - {task['description']}")
    
    return 0

if __name__ == '__main__':
    exit(main()) 