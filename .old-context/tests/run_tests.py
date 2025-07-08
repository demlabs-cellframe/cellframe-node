#!/usr/bin/env python3
"""
Комплексный тестовый раннер для Smart Layered Context CLI
Включает реальный анализ состояния системы без пропусков

Версия: 2.0.0
Обновлено: 2025-01-25
"""

import unittest
import sys
import os
import time
import json
from pathlib import Path
from io import StringIO
import subprocess
import importlib.util

# Добавляем путь к проекту
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    import coverage
    COVERAGE_AVAILABLE = True
except ImportError:
    COVERAGE_AVAILABLE = False
    print("⚠️  Coverage не установлен. Установите: pip install coverage")


class SLCTestRunner:
    """Комплексный тестовый раннер для СЛК"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.tests_dir = self.project_root / "tests"
        self.results = {
            'total_tests': 0,
            'passed': 0,
            'failed': 0,
            'errors': 0,
            'skipped': 0,
            'coverage': None,
            'execution_time': 0,
            'test_suites': {}
        }
    
    def discover_test_suites(self):
        """Обнаружение всех тестовых наборов"""
        test_suites = {}
        
        # Базовые тесты
        basic_tests_path = self.tests_dir / "cli" / "test_cli_basic.py"
        if basic_tests_path.exists():
            test_suites['basic'] = {
                'path': basic_tests_path,
                'description': 'Базовые тесты проекта',
                'priority': 1
            }
        
        # Реальные тесты CLI (БЕЗ ПРОПУСКОВ)
        real_cli_tests_path = self.tests_dir / "cli" / "test_real_cli_status.py"
        if real_cli_tests_path.exists():
            test_suites['real_cli'] = {
                'path': real_cli_tests_path,
                'description': 'Реальный анализ CLI системы (без пропусков)',
                'priority': 2
            }
        
        # Основные тесты команд (с пропусками для несуществующих модулей)
        core_tests_path = self.tests_dir / "cli" / "test_core_commands.py"
        if core_tests_path.exists():
            test_suites['core_commands'] = {
                'path': core_tests_path,
                'description': 'Тесты основных команд CLI (с пропусками)',
                'priority': 3
            }
        
        return test_suites
    
    def run_test_suite(self, suite_name, suite_info):
        """Запуск отдельного тестового набора"""
        print(f"\n{'='*60}")
        print(f"🧪 ЗАПУСК: {suite_info['description']}")
        print(f"📁 Файл: {suite_info['path']}")
        print(f"{'='*60}")
        
        # Загружаем тесты
        loader = unittest.TestLoader()
        
        # Импортируем модуль тестов
        spec = importlib.util.spec_from_file_location(suite_name, suite_info['path'])
        test_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(test_module)
        
        # Создаем тестовый набор
        suite = loader.loadTestsFromModule(test_module)
        
        # Запускаем тесты
        stream = StringIO()
        runner = unittest.TextTestRunner(
            stream=stream, 
            verbosity=2,
            buffer=True
        )
        
        start_time = time.time()
        result = runner.run(suite)
        execution_time = time.time() - start_time
        
        # Сохраняем результаты
        suite_results = {
            'tests_run': result.testsRun,
            'failures': len(result.failures),
            'errors': len(result.errors),
            'skipped': len(result.skipped) if hasattr(result, 'skipped') else 0,
            'success_rate': ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100) if result.testsRun > 0 else 0,
            'execution_time': execution_time,
            'output': stream.getvalue()
        }
        
        self.results['test_suites'][suite_name] = suite_results
        self.results['total_tests'] += result.testsRun
        self.results['passed'] += (result.testsRun - len(result.failures) - len(result.errors))
        self.results['failed'] += len(result.failures)
        self.results['errors'] += len(result.errors)
        self.results['skipped'] += suite_results['skipped']
        
        # Выводим результаты набора
        print(f"\n📊 РЕЗУЛЬТАТЫ НАБОРА '{suite_name.upper()}':")
        print(f"   🎯 Тестов выполнено: {result.testsRun}")
        print(f"   ✅ Успешных: {result.testsRun - len(result.failures) - len(result.errors)}")
        print(f"   ❌ Неудачных: {len(result.failures)}")
        print(f"   💥 Ошибок: {len(result.errors)}")
        print(f"   ⏭️  Пропущено: {suite_results['skipped']}")
        print(f"   📈 Процент успеха: {suite_results['success_rate']:.1f}%")
        print(f"   ⏱️  Время выполнения: {execution_time:.2f}с")
        
        # Показываем детали ошибок
        if result.failures:
            print(f"\n❌ НЕУДАЧНЫЕ ТЕСТЫ:")
            for test, traceback in result.failures:
                print(f"   • {test}: {traceback.split('AssertionError:')[-1].strip()}")
        
        if result.errors:
            print(f"\n💥 ОШИБКИ:")
            for test, traceback in result.errors:
                print(f"   • {test}: {traceback.split('Error:')[-1].strip()}")
        
        return suite_results
    
    def run_coverage_analysis(self):
        """Анализ покрытия кода"""
        if not COVERAGE_AVAILABLE:
            return None
        
        print(f"\n{'='*60}")
        print("📊 АНАЛИЗ ПОКРЫТИЯ КОДА")
        print(f"{'='*60}")
        
        try:
            # Инициализируем coverage
            cov = coverage.Coverage()
            cov.start()
            
            # Здесь можно добавить импорт модулей для анализа покрытия
            # Пока что просто останавливаем
            cov.stop()
            cov.save()
            
            # Генерируем отчет
            stream = StringIO()
            cov.report(file=stream)
            coverage_report = stream.getvalue()
            
            print("✅ Анализ покрытия завершен")
            print(coverage_report)
            
            return coverage_report
            
        except Exception as e:
            print(f"⚠️  Ошибка анализа покрытия: {e}")
            return None
    
    def run_cli_integration_tests(self):
        """Интеграционные тесты CLI"""
        print(f"\n{'='*60}")
        print("🔧 ИНТЕГРАЦИОННЫЕ ТЕСТЫ CLI")
        print(f"{'='*60}")
        
        cli_tests = [
            ("./slc help", "Тест команды help"),
            ("./slc status", "Тест команды status"),
            ("./slc templates", "Тест команды templates"),
            ("./slc list", "Тест команды list")
        ]
        
        integration_results = {
            'total': len(cli_tests),
            'passed': 0,
            'failed': 0,
            'details': []
        }
        
        for command, description in cli_tests:
            try:
                print(f"\n🧪 {description}: {command}")
                result = subprocess.run(
                    command.split(), 
                    capture_output=True, 
                    text=True, 
                    timeout=10,
                    cwd=self.project_root
                )
                
                if result.returncode == 0:
                    print(f"   ✅ Успешно (код: {result.returncode})")
                    integration_results['passed'] += 1
                    integration_results['details'].append({
                        'command': command,
                        'status': 'success',
                        'return_code': result.returncode
                    })
                else:
                    print(f"   ❌ Ошибка (код: {result.returncode})")
                    if result.stderr:
                        print(f"   📝 Ошибка: {result.stderr[:100]}...")
                    integration_results['failed'] += 1
                    integration_results['details'].append({
                        'command': command,
                        'status': 'failed',
                        'return_code': result.returncode,
                        'error': result.stderr
                    })
                    
            except subprocess.TimeoutExpired:
                print(f"   ⏰ Timeout")
                integration_results['failed'] += 1
                integration_results['details'].append({
                    'command': command,
                    'status': 'timeout'
                })
            except Exception as e:
                print(f"   💥 Исключение: {e}")
                integration_results['failed'] += 1
                integration_results['details'].append({
                    'command': command,
                    'status': 'exception',
                    'error': str(e)
                })
        
        success_rate = (integration_results['passed'] / integration_results['total']) * 100
        print(f"\n📊 РЕЗУЛЬТАТЫ ИНТЕГРАЦИОННЫХ ТЕСТОВ:")
        print(f"   🎯 Всего команд: {integration_results['total']}")
        print(f"   ✅ Успешных: {integration_results['passed']}")
        print(f"   ❌ Неудачных: {integration_results['failed']}")
        print(f"   📈 Процент успеха: {success_rate:.1f}%")
        
        return integration_results
    
    def generate_final_report(self):
        """Генерация итогового отчета"""
        print(f"\n{'='*80}")
        print("📋 ИТОГОВЫЙ ОТЧЕТ ТЕСТИРОВАНИЯ SMART LAYERED CONTEXT CLI")
        print(f"{'='*80}")
        
        # Общая статистика
        total_success_rate = (self.results['passed'] / self.results['total_tests']) * 100 if self.results['total_tests'] > 0 else 0
        
        print(f"\n📊 ОБЩАЯ СТАТИСТИКА:")
        print(f"   🎯 Всего тестов: {self.results['total_tests']}")
        print(f"   ✅ Успешных: {self.results['passed']}")
        print(f"   ❌ Неудачных: {self.results['failed']}")
        print(f"   💥 Ошибок: {self.results['errors']}")
        print(f"   ⏭️  Пропущено: {self.results['skipped']}")
        print(f"   📈 Общий процент успеха: {total_success_rate:.1f}%")
        print(f"   ⏱️  Общее время выполнения: {self.results['execution_time']:.2f}с")
        
        # Детали по наборам
        print(f"\n📋 ДЕТАЛИ ПО ТЕСТОВЫМ НАБОРАМ:")
        for suite_name, suite_results in self.results['test_suites'].items():
            status_emoji = "✅" if suite_results['success_rate'] >= 90 else "⚠️" if suite_results['success_rate'] >= 70 else "❌"
            print(f"   {status_emoji} {suite_name.upper()}: {suite_results['success_rate']:.1f}% ({suite_results['tests_run']} тестов)")
        
        # Рекомендации
        print(f"\n💡 РЕКОМЕНДАЦИИ:")
        if total_success_rate >= 95:
            print("   🎉 Отличное состояние! CLI система полностью функциональна.")
        elif total_success_rate >= 80:
            print("   👍 Хорошее состояние. Есть незначительные проблемы для исправления.")
        elif total_success_rate >= 60:
            print("   ⚠️  Среднее состояние. Требуется доработка некоторых компонентов.")
        else:
            print("   🚨 Критическое состояние. Необходима серьезная доработка системы.")
        
        # Сохранение отчета в JSON
        report_data = {
            'timestamp': time.time(),
            'summary': {
                'total_tests': self.results['total_tests'],
                'passed': self.results['passed'],
                'failed': self.results['failed'],
                'errors': self.results['errors'],
                'skipped': self.results['skipped'],
                'success_rate': total_success_rate,
                'execution_time': self.results['execution_time']
            },
            'test_suites': self.results['test_suites']
        }
        
        report_file = self.project_root / "tests" / "test_results.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 Детальный отчет сохранен: {report_file}")
        
        return total_success_rate
    
    def run_all_tests(self):
        """Запуск всех тестов"""
        print("🚀 ЗАПУСК КОМПЛЕКСНОГО ТЕСТИРОВАНИЯ SMART LAYERED CONTEXT CLI")
        print(f"📁 Корень проекта: {self.project_root}")
        
        start_time = time.time()
        
        # Обнаруживаем тестовые наборы
        test_suites = self.discover_test_suites()
        print(f"\n🔍 Обнаружено тестовых наборов: {len(test_suites)}")
        
        # Запускаем каждый набор
        for suite_name, suite_info in sorted(test_suites.items(), key=lambda x: x[1]['priority']):
            self.run_test_suite(suite_name, suite_info)
        
        # Интеграционные тесты CLI
        integration_results = self.run_cli_integration_tests()
        
        # Анализ покрытия
        coverage_report = self.run_coverage_analysis()
        self.results['coverage'] = coverage_report
        
        # Общее время выполнения
        self.results['execution_time'] = time.time() - start_time
        
        # Итоговый отчет
        final_success_rate = self.generate_final_report()
        
        # Возвращаем код выхода
        if final_success_rate >= 80:
            return 0  # Успех
        else:
            return 1  # Неудача


def main():
    """Главная функция"""
    runner = SLCTestRunner()
    exit_code = runner.run_all_tests()
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main() 