#!/usr/bin/env python3
"""
Intelligent Module Analyzer for Python Cellframe
Интеллектуальный анализатор модулей Python Cellframe

Этот инструмент проводит глубокий анализ архитектуры модулей,
выявляет паттерны, недостающие функции и возможности для улучшения.
"""

import os
import re
import ast
import json
import inspect
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Any, Optional
from collections import defaultdict, Counter

class IntelligentModuleAnalyzer:
    """Интеллектуальный анализатор модулей Python Cellframe"""
    
    def __init__(self, base_path="python-cellframe"):
        self.base_path = Path(base_path)
        self.analysis_results = {}
        self.module_map = {}
        self.dependency_graph = {}
        self.api_patterns = {}
        self.improvement_suggestions = {}
        
    def analyze_all_modules(self):
        """Запускает полный анализ всех модулей"""
        print("🧠 Запуск интеллектуального анализа модулей Python Cellframe")
        print("=" * 65)
        
        # 1. Сканирование структуры
        print("\n📁 Фаза 1: Сканирование структуры модулей...")
        self.scan_module_structure()
        
        # 2. Анализ зависимостей
        print("\n🔗 Фаза 2: Анализ зависимостей...")
        self.analyze_dependencies()
        
        # 3. Анализ API паттернов
        print("\n🔍 Фаза 3: Анализ API паттернов...")
        self.analyze_api_patterns()
        
        # 4. Поиск недостающих функций
        print("\n🎯 Фаза 4: Поиск недостающих функций...")
        self.find_missing_functions()
        
        # 5. Анализ возможностей улучшения
        print("\n💡 Фаза 5: Анализ возможностей улучшения...")
        self.analyze_improvement_opportunities()
        
        # 6. Генерация отчетов
        print("\n📊 Фаза 6: Генерация отчетов...")
        self.generate_reports()
        
        print("\n✅ Интеллектуальный анализ завершен!")
        return self.analysis_results
    
    def scan_module_structure(self):
        """Сканирует структуру модулей"""
        modules = {}
        
        for py_file in self.base_path.rglob("*.c"):
            if self.is_python_binding_file(py_file):
                module_info = self.analyze_c_module(py_file)
                modules[str(py_file.relative_to(self.base_path))] = module_info
        
        for py_file in self.base_path.rglob("*.py"):
            if py_file.name != "__pycache__":
                module_info = self.analyze_python_module(py_file)
                modules[str(py_file.relative_to(self.base_path))] = module_info
        
        self.module_map = modules
        print(f"   📁 Найдено модулей: {len(modules)}")
        
    def is_python_binding_file(self, file_path):
        """Проверяет, является ли файл Python биндингом"""
        return (
            "wrapping_" in file_path.name or
            "python" in file_path.name.lower() or
            file_path.parent.name in ["src", "modules"]
        )
    
    def analyze_c_module(self, file_path):
        """Анализирует C модуль с Python биндингами"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except:
            return {"error": "Cannot read file"}
        
        # Поиск Python API функций
        python_functions = re.findall(r'PyObject\s+\*(\w+)\(PyObject\s+\*[^)]*\)', content)
        
        # Поиск структур данных
        structures = re.findall(r'typedef\s+struct\s+(\w+)', content)
        
        # Поиск включений
        includes = re.findall(r'#include\s+[<"]([^>"]+)[>"]', content)
        
        # Анализ сложности
        lines = content.split('\n')
        complexity_metrics = self.calculate_complexity_metrics(content)
        
        return {
            "type": "c_extension",
            "python_functions": python_functions,
            "function_count": len(python_functions),
            "structures": structures,
            "includes": includes,
            "lines_of_code": len(lines),
            "complexity": complexity_metrics,
            "last_modified": file_path.stat().st_mtime
        }
    
    def analyze_python_module(self, file_path):
        """Анализирует Python модуль"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
        except:
            return {"error": "Cannot parse Python file"}
        
        # Анализ AST
        functions = []
        classes = []
        imports = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions.append({
                    "name": node.name,
                    "args": [arg.arg for arg in node.args.args],
                    "line": node.lineno,
                    "is_public": not node.name.startswith('_')
                })
            elif isinstance(node, ast.ClassDef):
                classes.append({
                    "name": node.name,
                    "line": node.lineno,
                    "methods": [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
                })
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                if isinstance(node, ast.Import):
                    imports.extend([alias.name for alias in node.names])
                else:
                    imports.append(node.module)
        
        return {
            "type": "python_module",
            "functions": functions,
            "classes": classes,
            "imports": imports,
            "lines_of_code": len(content.split('\n')),
            "last_modified": file_path.stat().st_mtime
        }
    
    def calculate_complexity_metrics(self, content):
        """Вычисляет метрики сложности кода"""
        lines = content.split('\n')
        
        # Цикломатическая сложность (приблизительно)
        complexity_keywords = ['if', 'else', 'elif', 'for', 'while', 'case', 'default']
        cyclomatic_complexity = sum(
            len(re.findall(rf'\b{keyword}\b', content)) 
            for keyword in complexity_keywords
        )
        
        # Глубина вложенности
        max_nesting = 0
        current_nesting = 0
        for line in lines:
            stripped = line.strip()
            if stripped.endswith('{'):
                current_nesting += 1
                max_nesting = max(max_nesting, current_nesting)
            elif stripped.startswith('}'):
                current_nesting = max(0, current_nesting - 1)
        
        # Количество функций
        function_count = len(re.findall(r'PyObject\s+\*\w+\(', content))
        
        return {
            "cyclomatic_complexity": cyclomatic_complexity,
            "max_nesting_depth": max_nesting,
            "function_count": function_count,
            "avg_function_length": len(lines) // max(function_count, 1)
        }
    
    def analyze_dependencies(self):
        """Анализирует зависимости между модулями"""
        dependencies = defaultdict(set)
        
        for module_path, module_info in self.module_map.items():
            if module_info.get("type") == "c_extension":
                # Анализ включений в C файлах
                includes = module_info.get("includes", [])
                for include in includes:
                    if "dap_" in include or "cellframe" in include:
                        dependencies[module_path].add(include)
            
            elif module_info.get("type") == "python_module":
                # Анализ импортов в Python файлах
                imports = module_info.get("imports", [])
                for imp in imports:
                    if imp and ("cellframe" in imp.lower() or "dap" in imp.lower()):
                        dependencies[module_path].add(imp)
        
        # Конвертируем sets в lists для JSON сериализации
        self.dependency_graph = {k: list(v) for k, v in dependencies.items()}
        print(f"   🔗 Найдено зависимостей: {sum(len(deps) for deps in dependencies.values())}")
    
    def analyze_api_patterns(self):
        """Анализирует паттерны API"""
        patterns = {
            "naming_conventions": defaultdict(int),
            "parameter_patterns": defaultdict(int),
            "return_patterns": defaultdict(int),
            "error_handling_patterns": defaultdict(int)
        }
        
        for module_path, module_info in self.module_map.items():
            if module_info.get("type") == "c_extension":
                functions = module_info.get("python_functions", [])
                
                for func in functions:
                    # Анализ соглашений именования
                    if func.startswith("dap_"):
                        patterns["naming_conventions"]["dap_prefix"] += 1
                    elif func.startswith("python_"):
                        patterns["naming_conventions"]["python_prefix"] += 1
                    else:
                        patterns["naming_conventions"]["no_prefix"] += 1
                    
                    # Анализ паттернов (упрощенно)
                    if "_create" in func:
                        patterns["parameter_patterns"]["create_pattern"] += 1
                    elif "_get" in func:
                        patterns["parameter_patterns"]["get_pattern"] += 1
                    elif "_set" in func:
                        patterns["parameter_patterns"]["set_pattern"] += 1
        
        # Конвертируем defaultdict в обычные dict для JSON сериализации
        self.api_patterns = {
            key: dict(value) for key, value in patterns.items()
        }
        print(f"   🔍 Проанализировано паттернов: {len(patterns)}")
    
    def find_missing_functions(self):
        """Поиск недостающих функций"""
        missing_functions = {}
        
        # Анализ каждого модуля на предмет недостающих функций
        for module_path, module_info in self.module_map.items():
            if module_info.get("type") == "c_extension":
                suggestions = self.suggest_missing_functions_for_module(module_path, module_info)
                if suggestions:
                    missing_functions[module_path] = suggestions
        
        self.missing_functions = missing_functions
        print(f"   🎯 Найдено модулей с недостающими функциями: {len(missing_functions)}")
    
    def suggest_missing_functions_for_module(self, module_path, module_info):
        """Предлагает недостающие функции для модуля"""
        suggestions = []
        existing_functions = module_info.get("python_functions", [])
        
        # Анализ паттернов CRUD
        has_create = any("create" in func for func in existing_functions)
        has_get = any("get" in func for func in existing_functions)
        has_set = any("set" in func for func in existing_functions)
        has_delete = any(any(word in func for word in ["delete", "remove", "destroy"]) for func in existing_functions)
        
        if has_create and not has_delete:
            suggestions.append({
                "type": "crud_completion",
                "function": "delete/destroy function",
                "reason": "Has create but missing delete",
                "priority": "medium"
            })
        
        if has_get and not has_set:
            suggestions.append({
                "type": "crud_completion", 
                "function": "setter function",
                "reason": "Has getter but missing setter",
                "priority": "low"
            })
        
        # Анализ utility функций
        if len(existing_functions) > 5:
            suggestions.append({
                "type": "utility",
                "function": "validation function",
                "reason": "Complex module should have validation",
                "priority": "medium"
            })
            
            suggestions.append({
                "type": "utility",
                "function": "string representation function", 
                "reason": "Should have string/debug representation",
                "priority": "low"
            })
        
        return suggestions
    
    def analyze_improvement_opportunities(self):
        """Анализирует возможности для улучшения"""
        improvements = {}
        
        for module_path, module_info in self.module_map.items():
            module_improvements = []
            
            # Анализ сложности
            if module_info.get("type") == "c_extension":
                complexity = module_info.get("complexity", {})
                
                if complexity.get("cyclomatic_complexity", 0) > 20:
                    module_improvements.append({
                        "type": "complexity_reduction",
                        "issue": "High cyclomatic complexity",
                        "suggestion": "Split complex functions into smaller ones",
                        "priority": "high"
                    })
                
                if complexity.get("max_nesting_depth", 0) > 4:
                    module_improvements.append({
                        "type": "readability",
                        "issue": "Deep nesting",
                        "suggestion": "Reduce nesting with early returns or helper functions",
                        "priority": "medium"
                    })
                
                if complexity.get("avg_function_length", 0) > 50:
                    module_improvements.append({
                        "type": "maintainability",
                        "issue": "Long functions",
                        "suggestion": "Break down long functions into smaller ones",
                        "priority": "medium"
                    })
            
            # Анализ соглашений именования
            functions = module_info.get("python_functions", [])
            if functions:
                inconsistent_naming = self.check_naming_consistency(functions)
                if inconsistent_naming:
                    module_improvements.append({
                        "type": "naming_consistency",
                        "issue": "Inconsistent naming conventions",
                        "suggestion": "Standardize function naming",
                        "priority": "low"
                    })
            
            if module_improvements:
                improvements[module_path] = module_improvements
        
        self.improvement_suggestions = improvements
        print(f"   💡 Найдено модулей для улучшения: {len(improvements)}")
    
    def check_naming_consistency(self, functions):
        """Проверяет консистентность именования"""
        prefixes = [func.split('_')[0] for func in functions if '_' in func]
        if len(set(prefixes)) > len(prefixes) * 0.7:  # Более 70% разных префиксов
            return True
        return False
    
    def generate_reports(self):
        """Генерирует отчеты анализа"""
        timestamp = datetime.now().isoformat()
        
        # Основной отчет
        main_report = {
            "analysis_info": {
                "timestamp": timestamp,
                "analyzer_version": "1.0.0",
                "modules_analyzed": len(self.module_map),
                "analysis_type": "intelligent_comprehensive"
            },
            "module_structure": self.module_map,
            "dependency_graph": self.dependency_graph,
            "api_patterns": self.api_patterns,
            "missing_functions": getattr(self, 'missing_functions', {}),
            "improvement_suggestions": self.improvement_suggestions
        }
        
        # Сохранение отчетов
        reports_dir = Path(".context/analysis")
        reports_dir.mkdir(parents=True, exist_ok=True)
        
        # Основной отчет
        with open(reports_dir / "module_architecture_analysis.json", 'w', encoding='utf-8') as f:
            json.dump(main_report, f, ensure_ascii=False, indent=2)
        
        # Граф зависимостей
        with open(reports_dir / "dependency_graph.json", 'w', encoding='utf-8') as f:
            json.dump(self.dependency_graph, f, ensure_ascii=False, indent=2)
        
        # Отчет о сложности
        complexity_report = self.generate_complexity_report()
        with open(reports_dir / "module_complexity_report.json", 'w', encoding='utf-8') as f:
            json.dump(complexity_report, f, ensure_ascii=False, indent=2)
        
        # Сводный отчет
        summary = self.generate_summary_report()
        with open(reports_dir / "intelligent_analysis_summary.md", 'w', encoding='utf-8') as f:
            f.write(summary)
        
        print(f"   📊 Отчеты сохранены в: {reports_dir}")
        
        self.analysis_results = main_report
    
    def generate_complexity_report(self):
        """Генерирует отчет о сложности"""
        complexity_data = {}
        
        for module_path, module_info in self.module_map.items():
            if module_info.get("type") == "c_extension":
                complexity = module_info.get("complexity", {})
                complexity_data[module_path] = {
                    "cyclomatic_complexity": complexity.get("cyclomatic_complexity", 0),
                    "max_nesting_depth": complexity.get("max_nesting_depth", 0),
                    "function_count": complexity.get("function_count", 0),
                    "avg_function_length": complexity.get("avg_function_length", 0),
                    "lines_of_code": module_info.get("lines_of_code", 0)
                }
        
        return {
            "timestamp": datetime.now().isoformat(),
            "modules": complexity_data,
            "summary": {
                "total_modules": len(complexity_data),
                "avg_complexity": sum(m.get("cyclomatic_complexity", 0) for m in complexity_data.values()) / max(len(complexity_data), 1),
                "high_complexity_modules": [
                    path for path, data in complexity_data.items() 
                    if data.get("cyclomatic_complexity", 0) > 20
                ]
            }
        }
    
    def generate_summary_report(self):
        """Генерирует сводный отчет в Markdown"""
        summary = f"""# 🧠 Отчет интеллектуального анализа модулей Python Cellframe

**Дата анализа:** {datetime.now().strftime('%d.%m.%Y %H:%M')}
**Версия анализатора:** 1.0.0

## 📊 Общая статистика

- **Всего модулей проанализировано:** {len(self.module_map)}
- **C extension модулей:** {sum(1 for m in self.module_map.values() if m.get('type') == 'c_extension')}
- **Python модулей:** {sum(1 for m in self.module_map.values() if m.get('type') == 'python_module')}
- **Всего зависимостей:** {sum(len(deps) for deps in self.dependency_graph.values())}

## 🔍 Ключевые находки

### Недостающие функции
- **Модулей с недостающими функциями:** {len(getattr(self, 'missing_functions', {}))}
- **Всего предложений:** {sum(len(suggestions) for suggestions in getattr(self, 'missing_functions', {}).values())}

### Возможности улучшения
- **Модулей требующих улучшения:** {len(self.improvement_suggestions)}
- **Всего предложений по улучшению:** {sum(len(improvements) for improvements in self.improvement_suggestions.values())}

## 🎯 Приоритетные рекомендации

### Высокий приоритет
"""
        
        # Добавляем высокоприоритетные рекомендации
        high_priority = []
        for module_path, improvements in self.improvement_suggestions.items():
            for improvement in improvements:
                if improvement.get("priority") == "high":
                    high_priority.append(f"- **{Path(module_path).name}**: {improvement.get('suggestion')}")
        
        if high_priority:
            summary += "\n".join(high_priority[:5])  # Топ 5
        else:
            summary += "\n- Критических проблем не обнаружено ✅"
        
        summary += f"""

### Средний приоритет
"""
        
        # Добавляем среднеприоритетные рекомендации
        medium_priority = []
        for module_path, improvements in self.improvement_suggestions.items():
            for improvement in improvements:
                if improvement.get("priority") == "medium":
                    medium_priority.append(f"- **{Path(module_path).name}**: {improvement.get('suggestion')}")
        
        if medium_priority:
            summary += "\n".join(medium_priority[:5])  # Топ 5
        else:
            summary += "\n- Среднеприоритетных улучшений не найдено"
        
        summary += f"""

## 📈 Следующие шаги

1. **Фаза 2**: Создание unit тестов для существующего API
2. **Фаза 3**: Реализация недостающих функций
3. **Фаза 4**: Применение предложенных улучшений
4. **Фаза 5**: Валидация и тестирование

## 📁 Сгенерированные файлы

- `module_architecture_analysis.json` - Полный анализ архитектуры
- `dependency_graph.json` - Граф зависимостей модулей
- `module_complexity_report.json` - Отчет о сложности кода
- `intelligent_analysis_summary.md` - Этот сводный отчет

---
*Анализ выполнен автоматически с помощью Intelligent Module Analyzer*
"""
        
        return summary

def main():
    """Главная функция"""
    print("🧠 Intelligent Module Analyzer for Python Cellframe")
    print("=" * 55)
    
    if not Path("python-cellframe").exists():
        print("❌ Директория python-cellframe не найдена")
        return 1
    
    analyzer = IntelligentModuleAnalyzer()
    results = analyzer.analyze_all_modules()
    
    print("\n🎉 Анализ завершен успешно!")
    print("\n📋 Результаты:")
    print(f"   📁 Модулей проанализировано: {len(analyzer.module_map)}")
    print(f"   🔗 Зависимостей найдено: {sum(len(deps) for deps in analyzer.dependency_graph.values())}")
    print(f"   🎯 Модулей с недостающими функциями: {len(getattr(analyzer, 'missing_functions', {}))}")
    print(f"   💡 Модулей для улучшения: {len(analyzer.improvement_suggestions)}")
    
    print(f"\n📊 Отчеты сохранены в: .context/analysis/")
    print("🚀 Готово к переходу к Фазе 2: Создание unit тестов")
    
    return 0

if __name__ == '__main__':
    exit(main()) 