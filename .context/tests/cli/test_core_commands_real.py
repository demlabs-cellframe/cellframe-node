#!/usr/bin/env python3
"""
РЕАЛЬНЫЕ Unit тесты для основных команд СЛК CLI (БЕЗ ПРОПУСКОВ)
Показывает истинное состояние CLI системы
"""

import unittest
import sys
import os
import tempfile
import json
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from io import StringIO

# Добавляем путь к модулям СЛК
sys.path.insert(0, str(Path(__file__).parent.parent.parent / '.context' / 'tools'))

try:
    from cli_modules.commands.core_commands import (
        ListCommand, TemplatesCommand, SearchCommand, 
        LoadContextCommand, CreateCommand, InfoCommand
    )
    CLI_MODULES_AVAILABLE = True
except ImportError as e:
    CLI_MODULES_AVAILABLE = False
    print(f"⚠️  Модули CLI не найдены: {e}")


class TestCoreCommandsReal(unittest.TestCase):
    """РЕАЛЬНЫЕ тесты основных CLI команд (без пропусков)"""
    
    def setUp(self):
        """Настройка перед каждым тестом"""
        self.temp_dir = tempfile.mkdtemp()
        self.mock_data = {
            'tasks': {
                "project": "Test Project",
                "version": "1.0.0",
                "status": "active"
            },
            'templates': [
                {"name": "python_development", "category": "languages"},
                {"name": "documentation_systems", "category": "methodologies"}
            ]
        }
    
    def tearDown(self):
        """Очистка после каждого теста"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)


class TestListCommandReal(TestCoreCommandsReal):
    """РЕАЛЬНЫЕ тесты команды list"""
    
    def test_list_command_creation(self):
        """Тест создания команды list"""
        cmd = ListCommand()
        self.assertEqual(cmd.name, "list")
        self.assertIn("список", cmd.description.lower())
    
    @patch('cli_modules.commands.core_commands.Path')
    def test_list_command_execute_with_tasks(self, mock_path):
        """Тест выполнения команды list с существующими задачами"""
        # Мокаем файловую систему
        mock_tasks_file = Mock()
        mock_tasks_file.exists.return_value = True
        mock_tasks_file.read_text.return_value = json.dumps(self.mock_data['tasks'])
        
        mock_path.return_value = mock_tasks_file
        
        cmd = ListCommand()
        
        # Перехватываем stdout
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            result = cmd.execute([])
            output = mock_stdout.getvalue()
        
        self.assertTrue(result)
        self.assertIn("Test Project", output)
        self.assertIn("active", output)


class TestTemplatesCommandReal(TestCoreCommandsReal):
    """РЕАЛЬНЫЕ тесты команды templates"""
    
    def test_templates_command_creation(self):
        """Тест создания команды templates"""
        cmd = TemplatesCommand()
        self.assertEqual(cmd.name, "templates")
        self.assertIn("шаблон", cmd.description.lower())


class TestSearchCommandReal(TestCoreCommandsReal):
    """РЕАЛЬНЫЕ тесты команды search"""
    
    def test_search_command_creation(self):
        """Тест создания команды search"""
        cmd = SearchCommand()
        self.assertEqual(cmd.name, "search")
        self.assertIn("поиск", cmd.description.lower())


class TestLoadContextCommandReal(TestCoreCommandsReal):
    """РЕАЛЬНЫЕ тесты команды load-context"""
    
    def test_load_context_command_creation(self):
        """Тест создания команды load-context"""
        cmd = LoadContextCommand()
        self.assertEqual(cmd.name, "load-context")
        self.assertIn("контекст", cmd.description.lower())


class TestCreateCommandReal(TestCoreCommandsReal):
    """РЕАЛЬНЫЕ тесты команды create"""
    
    def test_create_command_creation(self):
        """Тест создания команды create"""
        cmd = CreateCommand()
        self.assertEqual(cmd.name, "create")
        self.assertIn("создать", cmd.description.lower())


class TestInfoCommandReal(TestCoreCommandsReal):
    """РЕАЛЬНЫЕ тесты команды info"""
    
    def test_info_command_creation(self):
        """Тест создания команды info"""
        cmd = InfoCommand()
        self.assertEqual(cmd.name, "info")
        self.assertIn("информация", cmd.description.lower())


class TestCLIModulesAvailability(unittest.TestCase):
    """Тесты доступности CLI модулей"""
    
    def test_cli_modules_import(self):
        """Тест импорта CLI модулей"""
        try:
            from cli_modules.commands.core_commands import ListCommand
            self.assertTrue(True, "CLI модули успешно импортированы")
        except ImportError as e:
            self.fail(f"CLI модули недоступны: {e}")
    
    def test_cli_modules_structure(self):
        """Тест структуры CLI модулей"""
        cli_modules_path = Path(__file__).parent.parent.parent / '.context' / 'tools' / 'cli_modules'
        
        # Проверяем основные директории
        self.assertTrue(cli_modules_path.exists(), 
                       f"Директория cli_modules не найдена: {cli_modules_path}")
        
        commands_path = cli_modules_path / 'commands'
        self.assertTrue(commands_path.exists(),
                       f"Директория commands не найдена: {commands_path}")
        
        # Проверяем основные файлы
        core_commands_path = commands_path / 'core_commands.py'
        self.assertTrue(core_commands_path.exists(),
                       f"Файл core_commands.py не найден: {core_commands_path}")
    
    def test_base_command_class(self):
        """Тест базового класса команд"""
        try:
            from cli_modules.commands.base_command import BaseCommand
            
            # Проверяем, что это действительно базовый класс
            self.assertTrue(hasattr(BaseCommand, 'name'))
            self.assertTrue(hasattr(BaseCommand, 'description'))
            self.assertTrue(hasattr(BaseCommand, 'execute'))
            
        except ImportError as e:
            self.fail(f"BaseCommand класс недоступен: {e}")


class TestCLIInfrastructure(unittest.TestCase):
    """Тесты CLI инфраструктуры"""
    
    def test_slc_cli_script_exists(self):
        """Тест наличия главного CLI скрипта"""
        cli_script = Path(__file__).parent.parent.parent / '.context' / 'tools' / 'scripts' / 'slc_cli.py'
        self.assertTrue(cli_script.exists(),
                       f"CLI скрипт не найден: {cli_script}")
    
    def test_slc_wrapper_exists(self):
        """Тест наличия SLC wrapper"""
        slc_wrapper = Path(__file__).parent.parent.parent / 'slc'
        self.assertTrue(slc_wrapper.exists(),
                       f"SLC wrapper не найден: {slc_wrapper}")
    
    def test_unified_context_engine(self):
        """Тест Unified Context Engine"""
        try:
            from cli_modules.core.unified_context_engine import UnifiedContextEngine
            
            # Проверяем основные методы
            engine = UnifiedContextEngine()
            self.assertTrue(hasattr(engine, 'load_context'))
            self.assertTrue(hasattr(engine, 'load_files_content'))
            
        except ImportError as e:
            self.fail(f"UnifiedContextEngine недоступен: {e}")
    
    def test_template_intelligence(self):
        """Тест Template Intelligence системы"""
        try:
            from cli_modules.core.template_intelligence import TemplateIntelligence
            
            # Проверяем основные методы
            intelligence = TemplateIntelligence()
            self.assertTrue(hasattr(intelligence, 'recommend_templates'))
            self.assertTrue(hasattr(intelligence, 'analyze_usage_patterns'))
            
        except ImportError as e:
            self.fail(f"TemplateIntelligence недоступен: {e}")


if __name__ == '__main__':
    # Запуск только тестов этого модуля
    unittest.main(verbosity=2) 