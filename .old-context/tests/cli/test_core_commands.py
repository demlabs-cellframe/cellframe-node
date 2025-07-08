#!/usr/bin/env python3
"""
Unit тесты для основных команд СЛК CLI (ОБНОВЛЕНО ПОД РЕАЛЬНУЮ АРХИТЕКТУРУ)
Тестирует реальные модули команд без фиктивных импортов

Версия: 2.0.0
Обновлено: 2025-01-25
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

# Проверяем доступность реальных CLI модулей
try:
    from cli_modules.commands.template_commands import (
        TemplatesCommand, SearchCommand, InfoCommand, CreateCommand
    )
    from cli_modules.commands.context_commands import LoadContextCommand
    from cli_modules.commands.task_commands import ListCommand
    from cli_modules.commands.ai_commands import IntelligentRecommendCommand
    from cli_modules.commands.management_commands import StatusCommand, ValidateCommand
    from cli_modules.common.base_command import BaseCommand
    REAL_CLI_MODULES_AVAILABLE = True
except ImportError as e:
    REAL_CLI_MODULES_AVAILABLE = False
    print(f"⚠️  Реальные CLI модули недоступны: {e}")


class TestRealCLIArchitecture(unittest.TestCase):
    """Тесты реальной архитектуры CLI"""
    
    def setUp(self):
        """Настройка перед каждым тестом"""
        self.temp_dir = tempfile.mkdtemp()
        self.base_path = str(Path(__file__).parent.parent.parent)
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
    
    @unittest.skipUnless(REAL_CLI_MODULES_AVAILABLE, "Реальные CLI модули недоступны")
    def test_base_command_structure(self):
        """Тест базовой структуры команд"""
        # Проверяем, что BaseCommand имеет все необходимые методы
        self.assertTrue(hasattr(BaseCommand, 'name'))
        self.assertTrue(hasattr(BaseCommand, 'description'))
        self.assertTrue(hasattr(BaseCommand, 'execute'))
        self.assertTrue(hasattr(BaseCommand, 'add_arguments'))


class TestTemplateCommands(unittest.TestCase):
    """Тесты команд работы с шаблонами"""
    
    def setUp(self):
        self.base_path = str(Path(__file__).parent.parent.parent)
    
    @unittest.skipUnless(REAL_CLI_MODULES_AVAILABLE, "Реальные CLI модули недоступны")
    def test_templates_command_creation(self):
        """Тест создания команды templates"""
        cmd = TemplatesCommand(self.base_path)
        self.assertEqual(cmd.name, "templates")
        self.assertIn("шаблон", cmd.description.lower())
    
    @unittest.skipUnless(REAL_CLI_MODULES_AVAILABLE, "Реальные CLI модули недоступны") 
    def test_search_command_creation(self):
        """Тест создания команды search"""
        cmd = SearchCommand(self.base_path)
        self.assertEqual(cmd.name, "search")
        self.assertIn("поиск", cmd.description.lower())
    
    @unittest.skipUnless(REAL_CLI_MODULES_AVAILABLE, "Реальные CLI модули недоступны")
    def test_info_command_creation(self):
        """Тест создания команды info"""
        cmd = InfoCommand(self.base_path)
        self.assertEqual(cmd.name, "info")
        self.assertIn("информация", cmd.description.lower())
    
    @unittest.skipUnless(REAL_CLI_MODULES_AVAILABLE, "Реальные CLI модули недоступны")
    def test_create_command_creation(self):
        """Тест создания команды create"""
        cmd = CreateCommand(self.base_path)
        self.assertEqual(cmd.name, "create")
        self.assertIn("создать", cmd.description.lower())


class TestContextCommands(unittest.TestCase):
    """Тесты команд управления контекстом"""
    
    def setUp(self):
        self.base_path = str(Path(__file__).parent.parent.parent)
    
    @unittest.skipUnless(REAL_CLI_MODULES_AVAILABLE, "Реальные CLI модули недоступны")
    def test_load_context_command_creation(self):
        """Тест создания команды load-context"""
        cmd = LoadContextCommand(self.base_path)
        self.assertEqual(cmd.name, "load-context")
        self.assertIn("контекст", cmd.description.lower())


class TestTaskCommands(unittest.TestCase):
    """Тесты команд управления задачами"""
    
    def setUp(self):
        self.base_path = str(Path(__file__).parent.parent.parent)
    
    @unittest.skipUnless(REAL_CLI_MODULES_AVAILABLE, "Реальные CLI модули недоступны")
    def test_list_command_creation(self):
        """Тест создания команды list"""
        cmd = ListCommand(self.base_path)
        self.assertEqual(cmd.name, "list")
        self.assertIn("список", cmd.description.lower())


class TestAICommands(unittest.TestCase):
    """Тесты AI команд"""
    
    def setUp(self):
        self.base_path = str(Path(__file__).parent.parent.parent)
    
    @unittest.skipUnless(REAL_CLI_MODULES_AVAILABLE, "Реальные CLI модули недоступны")
    def test_intelligent_recommend_command_creation(self):
        """Тест создания команды intelligent-recommend"""
        cmd = IntelligentRecommendCommand(self.base_path)
        self.assertEqual(cmd.name, "intelligent-recommend")
        self.assertIn("рекоменд", cmd.description.lower())


class TestManagementCommands(unittest.TestCase):
    """Тесты команд управления системой"""
    
    def setUp(self):
        self.base_path = str(Path(__file__).parent.parent.parent)
    
    @unittest.skipUnless(REAL_CLI_MODULES_AVAILABLE, "Реальные CLI модули недоступны")
    def test_status_command_creation(self):
        """Тест создания команды status"""
        cmd = StatusCommand(self.base_path)
        self.assertEqual(cmd.name, "status")
        self.assertIn("статус", cmd.description.lower())
    
    @unittest.skipUnless(REAL_CLI_MODULES_AVAILABLE, "Реальные CLI модули недоступны")
    def test_validate_command_creation(self):
        """Тест создания команды validate"""
        cmd = ValidateCommand(self.base_path)
        self.assertEqual(cmd.name, "validate")
        self.assertIn("проверк", cmd.description.lower())


class TestCLIIntegration(unittest.TestCase):
    """Интеграционные тесты CLI системы"""
    
    @unittest.skipUnless(REAL_CLI_MODULES_AVAILABLE, "Реальные CLI модули недоступны")
    def test_command_registry_integration(self):
        """Тест интеграции с реестром команд"""
        from cli_modules.common.base_command import CommandRegistry
        
        registry = CommandRegistry()
        self.assertEqual(len(registry.get_all_commands()), 0)
        
        # Регистрируем команду
        base_path = str(Path(__file__).parent.parent.parent)
        templates_cmd = TemplatesCommand(base_path)
        registry.register(templates_cmd)
        
        self.assertEqual(len(registry.get_all_commands()), 1)
        self.assertEqual(registry.get_command("templates"), templates_cmd)
    
    @unittest.skipUnless(REAL_CLI_MODULES_AVAILABLE, "Реальные CLI модули недоступны")
    def test_multiple_commands_registration(self):
        """Тест регистрации нескольких команд"""
        from cli_modules.common.base_command import CommandRegistry
        
        registry = CommandRegistry()
        base_path = str(Path(__file__).parent.parent.parent)
        
        # Регистрируем несколько команд
        commands = [
            TemplatesCommand(base_path),
            SearchCommand(base_path),
            ListCommand(base_path),
            StatusCommand(base_path)
        ]
        
        for cmd in commands:
            registry.register(cmd)
        
        self.assertEqual(len(registry.get_all_commands()), 4)
        
        # Проверяем, что все команды доступны
        for cmd in commands:
            self.assertEqual(registry.get_command(cmd.name), cmd)


class TestCLIPerformance(unittest.TestCase):
    """Тесты производительности CLI"""
    
    @unittest.skipUnless(REAL_CLI_MODULES_AVAILABLE, "Реальные CLI модули недоступны")
    def test_command_creation_performance(self):
        """Тест производительности создания команд"""
        import time
        
        base_path = str(Path(__file__).parent.parent.parent)
        
        start_time = time.time()
        
        # Создаем команды
        commands = [
            TemplatesCommand(base_path),
            SearchCommand(base_path),
            InfoCommand(base_path),
            CreateCommand(base_path),
            LoadContextCommand(base_path),
            ListCommand(base_path)
        ]
        
        creation_time = time.time() - start_time
        
        # Команды должны создаваться быстро (менее 1 секунды)
        self.assertLess(creation_time, 1.0)
        self.assertEqual(len(commands), 6)


class TestCLIErrorHandling(unittest.TestCase):
    """Тесты обработки ошибок в CLI"""
    
    @unittest.skipUnless(REAL_CLI_MODULES_AVAILABLE, "Реальные CLI модули недоступны")
    def test_invalid_base_path_handling(self):
        """Тест обработки неверного base_path"""
        # Некоторые команды могут работать с неверным путем
        # но должны корректно обрабатывать ошибки
        invalid_path = "/nonexistent/path"
        
        try:
            cmd = TemplatesCommand(invalid_path)
            self.assertEqual(cmd.name, "templates")
        except Exception as e:
            # Если возникает исключение, оно должно быть информативным
            self.assertIsInstance(e, (FileNotFoundError, OSError, ValueError))


if __name__ == '__main__':
    # Запуск только тестов этого модуля
    unittest.main(verbosity=2) 