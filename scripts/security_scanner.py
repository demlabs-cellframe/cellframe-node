#!/usr/bin/env python3
"""
CellFrame Security Scanner
Автоматический сканер безопасности для обнаружения потенциальных уязвимостей
"""

import os
import re
import sys
import json
from pathlib import Path
from typing import List, Dict, Tuple

class SecurityIssue:
    def __init__(self, severity: str, issue_type: str, file_path: str, 
                 line_num: int, description: str, recommendation: str):
        self.severity = severity
        self.issue_type = issue_type
        self.file_path = file_path
        self.line_num = line_num
        self.description = description
        self.recommendation = recommendation

class CellFrameSecurityScanner:
    def __init__(self):
        self.issues: List[SecurityIssue] = []
        
        # Паттерны для поиска потенциальных уязвимостей
        self.security_patterns = {
            # Memory management issues
            'unsafe_string_functions': {
                'pattern': r'\b(strcpy|strcat|sprintf|gets)\s*\(',
                'severity': 'HIGH',
                'description': 'Unsafe string function usage',
                'recommendation': 'Use safe alternatives: strncpy, strncat, snprintf, fgets'
            },
            'unchecked_malloc': {
                'pattern': r'\bmalloc\s*\([^)]+\)\s*;(?!\s*if)',
                'severity': 'MEDIUM', 
                'description': 'Unchecked malloc result',
                'recommendation': 'Always check malloc return value for NULL'
            },
            'memset_password': {
                'pattern': r'\bmemset\s*\(\s*\w*pass\w*',
                'severity': 'HIGH',
                'description': 'Using memset for password clearing',
                'recommendation': 'Use explicit_bzero() for secure memory clearing'
            },
            
            # Crypto issues
            'weak_random': {
                'pattern': r'\b(rand\(\)|srand\()',
                'severity': 'CRITICAL',
                'description': 'Weak random number generation',
                'recommendation': 'Use cryptographically secure random: randombytes()'
            },
            'hardcoded_crypto': {
                'pattern': r'(key|password|secret)\s*=\s*["\'][^"\']{8,}["\']',
                'severity': 'CRITICAL',
                'description': 'Hardcoded cryptographic material',
                'recommendation': 'Use secure key management and configuration'
            },
            
            # Input validation
            'missing_size_check': {
                'pattern': r'\breadd?\s*\([^)]*\)\s*;(?!\s*if)',
                'severity': 'MEDIUM',
                'description': 'Unchecked read operation',
                'recommendation': 'Always validate read size and check return value'
            },
            'integer_overflow_risk': {
                'pattern': r'\w+\s*\+\s*\w+(?!\s*[<>])',
                'severity': 'LOW',
                'description': 'Potential integer overflow in arithmetic',
                'recommendation': 'Check for overflow before arithmetic operations'
            },
            
            # Network security
            'unsafe_eval': {
                'pattern': r'\beval\s*\(',
                'severity': 'HIGH',
                'description': 'Unsafe eval usage',
                'recommendation': 'Avoid eval, use direct command execution'
            },
            'path_traversal_risk': {
                'pattern': r'(fopen|open)\s*\([^,]*\.\.',
                'severity': 'HIGH',
                'description': 'Potential path traversal vulnerability',
                'recommendation': 'Validate and sanitize file paths'
            }
        }
    
    def scan_file(self, file_path: Path) -> None:
        """Сканирует отдельный файл на предмет уязвимостей"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                
            for line_num, line in enumerate(lines, 1):
                for pattern_name, pattern_info in self.security_patterns.items():
                    if re.search(pattern_info['pattern'], line, re.IGNORECASE):
                        issue = SecurityIssue(
                            severity=pattern_info['severity'],
                            issue_type=pattern_name,
                            file_path=str(file_path),
                            line_num=line_num,
                            description=pattern_info['description'],
                            recommendation=pattern_info['recommendation']
                        )
                        self.issues.append(issue)
                        
        except Exception as e:
            print(f"❌ Error scanning {file_path}: {e}")
    
    def scan_directory(self, directory: Path, extensions: List[str]) -> None:
        """Сканирует директорию рекурсивно"""
        for ext in extensions:
            for file_path in directory.rglob(f"*.{ext}"):
                # Пропускаем build директории и 3rdparty
                if any(part in str(file_path) for part in ['build', '3rdparty', '.git']):
                    continue
                self.scan_file(file_path)
    
    def generate_report(self) -> Dict:
        """Генерирует отчет о найденных проблемах"""
        report = {
            'scan_summary': {
                'total_issues': len(self.issues),
                'critical': len([i for i in self.issues if i.severity == 'CRITICAL']),
                'high': len([i for i in self.issues if i.severity == 'HIGH']),
                'medium': len([i for i in self.issues if i.severity == 'MEDIUM']),
                'low': len([i for i in self.issues if i.severity == 'LOW'])
            },
            'issues_by_file': {},
            'issues_by_type': {}
        }
        
        # Группировка по файлам
        for issue in self.issues:
            if issue.file_path not in report['issues_by_file']:
                report['issues_by_file'][issue.file_path] = []
            report['issues_by_file'][issue.file_path].append({
                'line': issue.line_num,
                'severity': issue.severity,
                'type': issue.issue_type,
                'description': issue.description,
                'recommendation': issue.recommendation
            })
        
        # Группировка по типам
        for issue in self.issues:
            if issue.issue_type not in report['issues_by_type']:
                report['issues_by_type'][issue.issue_type] = 0
            report['issues_by_type'][issue.issue_type] += 1
            
        return report
    
    def print_report(self) -> None:
        """Выводит отчет в консоль"""
        report = self.generate_report()
        summary = report['scan_summary']
        
        print("\n📊 === Security Scan Results ===")
        print(f"Total issues found: {summary['total_issues']}")
        print(f"🚨 Critical: {summary['critical']}")
        print(f"🔥 High: {summary['high']}")
        print(f"⚠️ Medium: {summary['medium']}")
        print(f"ℹ️ Low: {summary['low']}")
        
        if summary['total_issues'] == 0:
            print("\n🎉 No security issues found! All fixes are working correctly.")
            return
            
        print("\n📋 Issues by severity:")
        
        # Показываем только критические и высокие
        critical_and_high = [i for i in self.issues if i.severity in ['CRITICAL', 'HIGH']]
        if critical_and_high:
            print("\n🚨 Critical and High severity issues:")
            for issue in critical_and_high[:10]:  # Показываем первые 10
                print(f"  {issue.severity}: {issue.file_path}:{issue.line_num}")
                print(f"    {issue.description}")
                print(f"    💡 {issue.recommendation}")
                print()
        
        # Статистика по типам
        print("📈 Issues by type:")
        for issue_type, count in sorted(report['issues_by_type'].items(), 
                                       key=lambda x: x[1], reverse=True):
            print(f"  {issue_type}: {count}")

def main():
    if len(sys.argv) > 1 and sys.argv[1] == '--help':
        print("CellFrame Security Scanner")
        print("Usage: python3 security_scanner.py [--json]")
        print("  --json: Output results in JSON format")
        return
    
    scanner = CellFrameSecurityScanner()
    
    # Сканируем основные директории
    base_path = Path('.')
    
    print("🔍 Scanning DAP SDK...")
    if (base_path / 'dap-sdk').exists():
        scanner.scan_directory(base_path / 'dap-sdk', ['c', 'h'])
    
    print("🔍 Scanning CellFrame SDK...")
    if (base_path / 'cellframe-sdk').exists():
        scanner.scan_directory(base_path / 'cellframe-sdk', ['c', 'h'])
    
    print("🔍 Scanning Python bindings...")
    if (base_path / 'python-cellframe').exists():
        scanner.scan_directory(base_path / 'python-cellframe', ['c', 'h', 'py'])
    
    print("🔍 Scanning main sources...")
    if (base_path / 'sources').exists():
        scanner.scan_directory(base_path / 'sources', ['c', 'h'])
    
    # Генерируем отчет
    if len(sys.argv) > 1 and sys.argv[1] == '--json':
        report = scanner.generate_report()
        print(json.dumps(report, indent=2))
    else:
        scanner.print_report()

if __name__ == '__main__':
    main()
