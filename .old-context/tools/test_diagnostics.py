#!/usr/bin/env python3
"""
Диагностический скрипт для анализа skipped тестов Python Cellframe
Цель: определить точные причины пропуска тестов и пути их исправления
"""

import os
import sys
import re
import json
from pathlib import Path
from typing import Dict, List, Set, Tuple

class TestDiagnostics:
    def __init__(self, tests_dir: str = "python-cellframe/tests"):
        self.tests_dir = Path(tests_dir)
        self.results = {
            "total_test_files": 0,
            "total_test_functions": 0,
            "skipped_tests": 0,
            "skip_reasons": {},
            "cellframe_imports": [],
            "missing_dependencies": [],
            "test_categories": {},
            "recommendations": []
        }
    
    def analyze_test_files(self):
        """Анализ всех тестовых файлов"""
        print("🔍 Анализ тестовых файлов...")
        
        for test_file in self.tests_dir.rglob("test_*.py"):
            self._analyze_single_file(test_file)
            
        self._generate_recommendations()
        return self.results
    
    def _analyze_single_file(self, file_path: Path):
        """Анализ одного тестового файла"""
        self.results["total_test_files"] += 1
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Поиск тестовых функций
            test_functions = re.findall(r'def (test_\w+)', content)
            self.results["total_test_functions"] += len(test_functions)
            
            # Поиск skip условий
            skip_patterns = [
                r'@pytest\.mark\.skipif\(([^)]+)\)',
                r'pytest\.skip\(([^)]+)\)',
                r'if.*cellframe_available.*skip'
            ]
            
            for pattern in skip_patterns:
                matches = re.findall(pattern, content, re.MULTILINE)
                for match in matches:
                    self.results["skipped_tests"] += len(test_functions)
                    reason = match.strip()
                    if reason not in self.results["skip_reasons"]:
                        self.results["skip_reasons"][reason] = 0
                    self.results["skip_reasons"][reason] += 1
            
            # Поиск импортов CellFrame
            cellframe_imports = re.findall(r'(import.*CellFrame.*|from.*CellFrame.*)', content)
            if cellframe_imports:
                self.results["cellframe_imports"].extend([
                    {"file": str(file_path), "imports": cellframe_imports}
                ])
            
            # Категоризация тестов
            category = self._categorize_test(file_path)
            if category not in self.results["test_categories"]:
                self.results["test_categories"][category] = 0
            self.results["test_categories"][category] += len(test_functions)
            
        except Exception as e:
            print(f"❌ Ошибка анализа {file_path}: {e}")
    
    def _categorize_test(self, file_path: Path) -> str:
        """Категоризация тестов по типам"""
        path_str = str(file_path).lower()
        
        if "core" in path_str:
            return "core"
        elif "service" in path_str:
            return "services"
        elif "integration" in path_str:
            return "integration"
        elif "util" in path_str:
            return "utils"
        else:
            return "other"
    
    def _generate_recommendations(self):
        """Генерация рекомендаций на основе анализа"""
        recommendations = []
        
        # Анализ skip reasons
        if "not cellframe_available" in str(self.results["skip_reasons"]):
            recommendations.append({
                "priority": "HIGH",
                "action": "Исправить cellframe_available проверку",
                "description": "Основная причина пропуска тестов - недоступность CellFrame модуля",
                "solution": "Создать standalone CellFrame.so extension или mock объект"
            })
        
        # Анализ импортов
        if self.results["cellframe_imports"]:
            recommendations.append({
                "priority": "MEDIUM", 
                "action": "Проверить все CellFrame импорты",
                "description": f"Найдено {len(self.results['cellframe_imports'])} файлов с CellFrame импортами",
                "solution": "Убедиться что все импорты работают после исправления модуля"
            })
        
        # Анализ категорий
        core_tests = self.results["test_categories"].get("core", 0)
        if core_tests > 50:
            recommendations.append({
                "priority": "HIGH",
                "action": "Приоритет на core тесты",
                "description": f"Найдено {core_tests} core тестов - критически важны для рефакторинга",
                "solution": "Начать с исправления core тестов, затем services и integration"
            })
        
        self.results["recommendations"] = recommendations
    
    def check_cellframe_availability(self):
        """Проверка текущей доступности CellFrame модуля"""
        print("\n🔬 Проверка доступности CellFrame модуля...")
        
        availability_check = {
            "direct_import": False,
            "with_build_path": False,
            "error_messages": [],
            "python_paths": sys.path[:5]
        }
        
        # Прямой импорт
        try:
            import CellFrame
            availability_check["direct_import"] = True
            print("✅ CellFrame доступен через прямой импорт")
        except Exception as e:
            availability_check["error_messages"].append(f"Direct import: {e}")
            print(f"❌ Прямой импорт не работает: {e}")
        
        # Импорт с build path
        build_path = Path("build_with_python/python-cellframe")
        if build_path.exists():
            sys.path.insert(0, str(build_path))
            try:
                import CellFrame
                availability_check["with_build_path"] = True
                print("✅ CellFrame доступен с build path")
            except Exception as e:
                availability_check["error_messages"].append(f"With build path: {e}")
                print(f"❌ Импорт с build path не работает: {e}")
        
        return availability_check
    
    def generate_action_plan(self):
        """Генерация детального плана действий"""
        print("\n📋 Генерация плана действий...")
        
        plan = {
            "immediate_actions": [
                {
                    "step": 1,
                    "action": "Исследовать текущий build процесс",
                    "command": "cd python-cellframe && python3 setup.py build_ext --inplace",
                    "expected": "Создание CellFrame.so extension модуля"
                },
                {
                    "step": 2, 
                    "action": "Модифицировать CMakeLists.txt",
                    "target": "python-cellframe/CMakeLists.txt",
                    "change": "SHARED_LIBRARY вместо MODULE для CellFrame target"
                },
                {
                    "step": 3,
                    "action": "Создать test runner скрипт",
                    "file": "run_tests.py",
                    "purpose": "Запуск тестов с правильным PYTHONPATH"
                }
            ],
            "validation_steps": [
                "python3 -c 'import CellFrame; print(\"Success!\")'",
                "python3 -m pytest tests/core/test_libdap_client_python.py::TestLibdapClientPython::test_dao_client_set_uplink_py_exists -v",
                "python3 -m pytest tests/ --tb=short | grep -E '(PASSED|FAILED|SKIPPED)' | wc -l"
            ]
        }
        
        return plan
    
    def save_results(self, output_file: str = ".context/analysis/test_diagnostics_report.json"):
        """Сохранение результатов анализа"""
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        full_report = {
            "analysis_date": "2025-06-18T19:50:00Z",
            "diagnostics": self.results,
            "cellframe_availability": self.check_cellframe_availability(),
            "action_plan": self.generate_action_plan()
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(full_report, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Отчет сохранен в {output_file}")
        return full_report

def main():
    print("🚀 Запуск диагностики тестов Python Cellframe")
    print("=" * 50)
    
    diagnostics = TestDiagnostics()
    
    # Анализ тестовых файлов
    results = diagnostics.analyze_test_files()
    
    # Вывод краткой статистики
    print(f"\n📊 КРАТКАЯ СТАТИСТИКА:")
    print(f"   Тестовых файлов: {results['total_test_files']}")
    print(f"   Тестовых функций: {results['total_test_functions']}")
    print(f"   Пропущенных тестов: {results['skipped_tests']}")
    print(f"   Причин пропуска: {len(results['skip_reasons'])}")
    
    print(f"\n🏷️  КАТЕГОРИИ ТЕСТОВ:")
    for category, count in results['test_categories'].items():
        print(f"   {category}: {count} тестов")
    
    print(f"\n⚡ РЕКОМЕНДАЦИИ:")
    for i, rec in enumerate(results['recommendations'], 1):
        print(f"   {i}. [{rec['priority']}] {rec['action']}")
        print(f"      {rec['description']}")
    
    # Сохранение полного отчета
    full_report = diagnostics.save_results()
    
    print(f"\n✅ Диагностика завершена!")
    print(f"   Следующий шаг: Выполнить план действий из отчета")
    
    return full_report

if __name__ == "__main__":
    main() 