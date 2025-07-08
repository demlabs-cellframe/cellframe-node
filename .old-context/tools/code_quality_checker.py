#!/usr/bin/env python3
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
                    
                    malloc_count = len(re.findall(r'malloc\s*\(|calloc\s*\(|realloc\s*\(', content))
                    free_count = len(re.findall(r'free\s*\(|DAP_DELETE\s*\(', content))
                    
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
