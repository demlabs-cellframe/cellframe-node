#!/usr/bin/env python3
"""
Simple Python Cellframe Analyzer
Упрощенный анализатор для выявления основных проблем в Python Cellframe
"""

import os
import re
import json
from pathlib import Path
from datetime import datetime

def analyze_file(file_path):
    """Анализирует отдельный файл"""
    issues = []
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            lines = content.split('\n')
    except Exception as e:
        return {"error": str(e), "issues": []}
    
    # Анализ утечек памяти
    malloc_count = len(re.findall(r'malloc\s*\(|calloc\s*\(|realloc\s*\(', content))
    free_count = len(re.findall(r'free\s*\(', content))
    
    if malloc_count > free_count:
        issues.append({
            "type": "memory_leak",
            "severity": "HIGH",
            "description": f"Potential memory leak: {malloc_count} malloc vs {free_count} free",
            "suggestion": "Add corresponding free() calls"
        })
    
    # Анализ обработки ошибок
    pyerr_count = len(re.findall(r'PyErr_SetString', content))
    return_null_count = len(re.findall(r'return\s+NULL', content))
    
    if pyerr_count > return_null_count:
        issues.append({
            "type": "error_handling",
            "severity": "HIGH", 
            "description": f"Missing return NULL after PyErr_SetString: {pyerr_count} vs {return_null_count}",
            "suggestion": "Add 'return NULL;' after setting Python errors"
        })
    
    # Статические переменные (thread safety)
    static_vars = len(re.findall(r'static\s+(?!const)\w+.*=', content))
    if static_vars > 0:
        issues.append({
            "type": "thread_safety",
            "severity": "MEDIUM",
            "description": f"Found {static_vars} non-const static variables",
            "suggestion": "Consider thread-local storage or synchronization"
        })
    
    # Сложность функций
    functions = re.findall(r'^\w+.*\(.*\)\s*{', content, re.MULTILINE)
    if len(functions) > 20:
        issues.append({
            "type": "complexity",
            "severity": "MEDIUM",
            "description": f"High function count: {len(functions)} functions in one file",
            "suggestion": "Consider splitting into multiple files"
        })
    
    return {
        "file": str(file_path),
        "lines": len(lines),
        "functions": len(functions),
        "issues": issues,
        "malloc_calls": malloc_count,
        "free_calls": free_count,
        "static_vars": static_vars
    }

def analyze_project():
    """Анализирует весь проект Python Cellframe"""
    
    print("🔍 Анализ Python Cellframe...")
    
    base_path = Path("python-cellframe")
    if not base_path.exists():
        print("❌ Директория python-cellframe не найдена")
        return None
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "project_stats": {
            "total_files": 0,
            "total_lines": 0,
            "c_files": 0,
            "python_files": 0,
            "total_issues": 0
        },
        "files": [],
        "summary": {
            "critical_issues": 0,
            "high_issues": 0,
            "medium_issues": 0,
            "recommendations": []
        }
    }
    
    # Анализируем все файлы
    for root, dirs, files in os.walk(base_path):
        for file in files:
            file_path = Path(root) / file
            results["project_stats"]["total_files"] += 1
            
            if file.endswith('.c') or file.endswith('.h'):
                results["project_stats"]["c_files"] += 1
                analysis = analyze_file(file_path)
                results["files"].append(analysis)
                results["project_stats"]["total_lines"] += analysis.get("lines", 0)
                results["project_stats"]["total_issues"] += len(analysis.get("issues", []))
                
                # Подсчет по серьезности
                for issue in analysis.get("issues", []):
                    severity = issue.get("severity", "LOW").lower()
                    if severity == "critical":
                        results["summary"]["critical_issues"] += 1
                    elif severity == "high":
                        results["summary"]["high_issues"] += 1
                    elif severity == "medium":
                        results["summary"]["medium_issues"] += 1
            
            elif file.endswith('.py'):
                results["project_stats"]["python_files"] += 1
    
    # Генерируем рекомендации
    if results["summary"]["critical_issues"] > 0:
        results["summary"]["recommendations"].append(
            f"КРИТИЧНО: Исправить {results['summary']['critical_issues']} критических проблем"
        )
    
    if results["summary"]["high_issues"] > 0:
        results["summary"]["recommendations"].append(
            f"ВЫСОКИЙ ПРИОРИТЕТ: Исправить {results['summary']['high_issues']} проблем высокой важности"
        )
    
    # Анализ основных проблем
    memory_issues = sum(1 for f in results["files"] for i in f.get("issues", []) if i.get("type") == "memory_leak")
    if memory_issues > 0:
        results["summary"]["recommendations"].append(
            f"Исправить {memory_issues} потенциальных утечек памяти"
        )
    
    error_handling_issues = sum(1 for f in results["files"] for i in f.get("issues", []) if i.get("type") == "error_handling")
    if error_handling_issues > 0:
        results["summary"]["recommendations"].append(
            f"Улучшить обработку ошибок в {error_handling_issues} местах"
        )
    
    thread_safety_issues = sum(1 for f in results["files"] for i in f.get("issues", []) if i.get("type") == "thread_safety")
    if thread_safety_issues > 0:
        results["summary"]["recommendations"].append(
            f"Проверить thread safety в {thread_safety_issues} местах"
        )
    
    return results

def main():
    """Главная функция"""
    
    # Запускаем анализ
    results = analyze_project()
    
    if not results:
        return 1
    
    # Выводим результаты
    print("\n📊 Результаты анализа Python Cellframe:")
    print(f"   📁 Всего файлов: {results['project_stats']['total_files']}")
    print(f"   📝 C/C++ файлов: {results['project_stats']['c_files']}")
    print(f"   🐍 Python файлов: {results['project_stats']['python_files']}")
    print(f"   📄 Строк кода: {results['project_stats']['total_lines']:,}")
    print(f"   ⚠️  Всего проблем: {results['project_stats']['total_issues']}")
    print(f"   🔴 Критических: {results['summary']['critical_issues']}")
    print(f"   🟡 Высокоприоритетных: {results['summary']['high_issues']}")
    print(f"   🟠 Средних: {results['summary']['medium_issues']}")
    
    # Топ проблемные файлы
    problematic_files = sorted(
        [f for f in results["files"] if f.get("issues")],
        key=lambda x: len(x.get("issues", [])),
        reverse=True
    )[:5]
    
    if problematic_files:
        print("\n🔥 Топ проблемных файлов:")
        for i, file_info in enumerate(problematic_files, 1):
            print(f"   {i}. {Path(file_info['file']).name} - {len(file_info['issues'])} проблем")
    
    # Рекомендации
    if results["summary"]["recommendations"]:
        print("\n🎯 Рекомендации:")
        for i, rec in enumerate(results["summary"]["recommendations"], 1):
            print(f"   {i}. {rec}")
    
    # Сохраняем отчет
    output_dir = Path(".context/analysis")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / "python_cellframe_analysis.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n📋 Подробный отчет сохранен: {output_file}")
    
    # Создаем план рефакторинга
    refactoring_plan = {
        "phase_1_critical": {
            "title": "Критические исправления",
            "duration": "1-2 недели",
            "tasks": [
                "Исправить утечки памяти",
                "Добавить проверки return NULL после PyErr_SetString",
                "Исправить критические проблемы безопасности"
            ]
        },
        "phase_2_architecture": {
            "title": "Архитектурные улучшения", 
            "duration": "2-3 недели",
            "tasks": [
                "Улучшить thread safety",
                "Рефакторинг сложных функций",
                "Оптимизация производительности",
                "Улучшение API консистентности"
            ]
        },
        "phase_3_quality": {
            "title": "Повышение качества",
            "duration": "1-2 недели",
            "tasks": [
                "Добавить unit тесты",
                "Улучшить документацию",
                "Добавить статический анализ",
                "Code review процесс"
            ]
        }
    }
    
    plan_file = output_dir / "refactoring_plan.json"
    with open(plan_file, 'w', encoding='utf-8') as f:
        json.dump(refactoring_plan, f, ensure_ascii=False, indent=2)
    
    print(f"📋 План рефакторинга сохранен: {plan_file}")
    
    return 0

if __name__ == '__main__':
    exit(main()) 