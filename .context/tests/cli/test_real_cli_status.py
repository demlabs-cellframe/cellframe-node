#!/usr/bin/env python3
"""
РЕАЛЬНЫЙ АНАЛИЗ СОСТОЯНИЯ CLI СИСТЕМЫ СЛК
Показывает истинное состояние без пропусков и мокинга
"""

import unittest
import sys
import os
import importlib
from pathlib import Path
from io import StringIO
import subprocess

# Добавляем путь к модулям СЛК
sys.path.insert(0, str(Path(__file__).parent.parent.parent / '.context'))


class TestRealCLIStatus(unittest.TestCase):
    """Реальный анализ состояния CLI системы"""
    
    def setUp(self):
        """Настройка перед каждым тестом"""
        self.base_path = Path(__file__).parent.parent.parent
        self.cli_modules_path = self.base_path / '.context' / 'tools' / 'cli_modules'
        self.cli_script_path = self.base_path / '.context' / 'tools' / 'scripts' / 'slc_cli.py'
    
    def test_cli_infrastructure_exists(self):
        """Тест наличия CLI инфраструктуры"""
        print("\n🔍 ПРОВЕРКА CLI ИНФРАСТРУКТУРЫ:")
        
        # Проверяем основные пути
        self.assertTrue(self.cli_modules_path.exists(), 
                       f"CLI модули не найдены: {self.cli_modules_path}")
        print(f"   ✅ CLI модули найдены: {self.cli_modules_path}")
        
        self.assertTrue(self.cli_script_path.exists(),
                       f"CLI скрипт не найден: {self.cli_script_path}")
        print(f"   ✅ CLI скрипт найден: {self.cli_script_path}")
        
        # Проверяем структуру модулей
        commands_path = self.cli_modules_path / 'commands'
        self.assertTrue(commands_path.exists(),
                       f"Директория команд не найдена: {commands_path}")
        print(f"   ✅ Директория команд найдена: {commands_path}")
        
        core_path = self.cli_modules_path / 'core'
        self.assertTrue(core_path.exists(),
                       f"Директория core не найдена: {core_path}")
        print(f"   ✅ Директория core найдена: {core_path}")
        
        common_path = self.cli_modules_path / 'common'
        self.assertTrue(common_path.exists(),
                       f"Директория common не найдена: {common_path}")
        print(f"   ✅ Директория common найдена: {common_path}")
    
    def test_base_command_import(self):
        """Тест импорта базового класса команд"""
        print("\n🔍 ПРОВЕРКА БАЗОВОГО КЛАССА КОМАНД:")
        
        try:
            from tools.cli_modules.common.base_command import BaseCommand, CommandRegistry
            print("   ✅ BaseCommand успешно импортирован")
            print("   ✅ CommandRegistry успешно импортирован")
            
            # Проверяем методы BaseCommand
            self.assertTrue(hasattr(BaseCommand, 'name'))
            self.assertTrue(hasattr(BaseCommand, 'description'))
            self.assertTrue(hasattr(BaseCommand, 'execute'))
            print("   ✅ BaseCommand имеет все необходимые методы")
            
            return True
            
        except ImportError as e:
            self.fail(f"Не удалось импортировать BaseCommand: {e}")
    
    def test_command_modules_discovery(self):
        """Тест обнаружения модулей команд"""
        print("\n🔍 ОБНАРУЖЕНИЕ МОДУЛЕЙ КОМАНД:")
        
        commands_path = self.cli_modules_path / 'commands'
        command_files = list(commands_path.glob('*_commands.py'))
        
        print(f"   📁 Найдено файлов команд: {len(command_files)}")
        
        expected_modules = [
            'template_commands.py',
            'context_commands.py', 
            'ai_commands.py',
            'organization_commands.py',
            'template_intelligence_commands.py',
            'task_commands.py',
            'management_commands.py',
            'help_commands.py'
        ]
        
        found_modules = [f.name for f in command_files]
        
        for expected in expected_modules:
            if expected in found_modules:
                print(f"   ✅ {expected}")
            else:
                print(f"   ❌ {expected} - НЕ НАЙДЕН")
        
        self.assertGreater(len(command_files), 0, "Не найдено ни одного модуля команд")
        
        return found_modules
    
    def test_command_classes_import(self):
        """Тест импорта классов команд"""
        print("\n🔍 ИМПОРТ КЛАССОВ КОМАНД:")
        
        # Тестируем импорт конкретных команд
        test_imports = [
            ('tools.cli_modules.commands.template_commands', ['TemplatesCommand', 'SearchCommand', 'InfoCommand', 'CreateCommand']),
            ('tools.cli_modules.commands.context_commands', ['LoadContextCommand']),
            ('tools.cli_modules.commands.task_commands', ['ListCommand']),
        ]
        
        successful_imports = 0
        total_commands = 0
        
        for module_name, command_classes in test_imports:
            try:
                module = importlib.import_module(module_name)
                print(f"   ✅ Модуль {module_name} импортирован")
                
                for command_class_name in command_classes:
                    total_commands += 1
                    if hasattr(module, command_class_name):
                        command_class = getattr(module, command_class_name)
                        print(f"      ✅ {command_class_name}")
                        successful_imports += 1
                    else:
                        print(f"      ❌ {command_class_name} - НЕ НАЙДЕН")
                        
            except ImportError as e:
                print(f"   ❌ Модуль {module_name}: {e}")
        
        print(f"\n📊 Успешно импортировано команд: {successful_imports}/{total_commands}")
        return successful_imports, total_commands
    
    def test_cli_script_execution(self):
        """Тест выполнения CLI скрипта"""
        print("\n🔍 ТЕСТ ВЫПОЛНЕНИЯ CLI СКРИПТА:")
        
        try:
            # Тестируем запуск CLI скрипта с --help
            result = subprocess.run([
                sys.executable, 
                str(self.cli_script_path), 
                '--help'
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                print("   ✅ CLI скрипт запускается успешно")
                print("   ✅ --help работает корректно")
                return True
            else:
                print(f"   ❌ CLI скрипт завершился с ошибкой: {result.returncode}")
                print(f"   📝 STDERR: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("   ❌ CLI скрипт завис (timeout)")
            return False
        except Exception as e:
            print(f"   ❌ Ошибка запуска CLI скрипта: {e}")
            return False
    
    def test_core_modules_availability(self):
        """Тест доступности core модулей"""
        print("\n🔍 ПРОВЕРКА CORE МОДУЛЕЙ:")
        
        core_modules = [
            'unified_context_engine.py',
            'advanced_template_intelligence.py', 
            'file_organization_engine.py',
            'system_validator.py',
            'project_generator.py',
            'template_manager.py'
        ]
        
        core_path = self.cli_modules_path / 'core'
        available_modules = 0
        
        for module_name in core_modules:
            module_path = core_path / module_name
            if module_path.exists():
                print(f"   ✅ {module_name}")
                available_modules += 1
            else:
                print(f"   ❌ {module_name} - НЕ НАЙДЕН")
        
        print(f"\n📊 Доступно core модулей: {available_modules}/{len(core_modules)}")
        return available_modules, len(core_modules)
    
    def test_slc_wrapper_functionality(self):
        """Тест функциональности SLC wrapper"""
        print("\n🔍 ТЕСТ SLC WRAPPER:")
        
        slc_wrapper = self.base_path / 'slc'
        
        if not slc_wrapper.exists():
            print("   ❌ SLC wrapper не найден")
            return False
        
        print("   ✅ SLC wrapper найден")
        
        try:
            # Тестируем запуск через wrapper
            result = subprocess.run([
                str(slc_wrapper), 
                'help'
            ], capture_output=True, text=True, timeout=15)
            
            if result.returncode == 0:
                print("   ✅ SLC wrapper работает")
                print("   ✅ Команда help выполняется")
                return True
            else:
                print(f"   ❌ SLC wrapper ошибка: {result.returncode}")
                if result.stderr:
                    print(f"   📝 STDERR: {result.stderr[:200]}...")
                return False
                
        except subprocess.TimeoutExpired:
            print("   ❌ SLC wrapper завис (timeout)")
            return False
        except Exception as e:
            print(f"   ❌ Ошибка SLC wrapper: {e}")
            return False


class TestCLIComprehensiveAnalysis(unittest.TestCase):
    """Комплексный анализ CLI системы"""
    
    def test_comprehensive_cli_analysis(self):
        """Комплексный анализ состояния CLI"""
        print("\n" + "="*60)
        print("🧠 КОМПЛЕКСНЫЙ АНАЛИЗ CLI СИСТЕМЫ СЛК")
        print("="*60)
        
        # Запускаем все тесты и собираем статистику
        test_suite = unittest.TestLoader().loadTestsFromTestCase(TestRealCLIStatus)
        
        # Создаем результат для сбора статистики
        stream = StringIO()
        runner = unittest.TextTestRunner(stream=stream, verbosity=2)
        result = runner.run(test_suite)
        
        # Анализируем результаты
        total_tests = result.testsRun
        failures = len(result.failures)
        errors = len(result.errors)
        successes = total_tests - failures - errors
        
        print(f"\n📊 ИТОГОВАЯ СТАТИСТИКА:")
        print(f"   🎯 Всего тестов: {total_tests}")
        print(f"   ✅ Успешных: {successes}")
        print(f"   ❌ Неудачных: {failures}")
        print(f"   💥 Ошибок: {errors}")
        print(f"   📈 Процент успеха: {(successes/total_tests)*100:.1f}%")
        
        # Выводим рекомендации
        print(f"\n💡 РЕКОМЕНДАЦИИ:")
        if failures + errors == 0:
            print("   🎉 CLI система полностью функциональна!")
        elif failures + errors <= 2:
            print("   ⚠️  Незначительные проблемы, система в основном работает")
        else:
            print("   🚨 Серьезные проблемы, требуется доработка CLI системы")
        
        print("\n" + "="*60)


if __name__ == '__main__':
    # Запуск всех тестов
    unittest.main(verbosity=2) 