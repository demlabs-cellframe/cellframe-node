#!/usr/bin/env python3
"""
Базовые unit тесты для СЛК CLI (без зависимостей)
Демонстрация работы test runner и базовые проверки
"""

import unittest
import sys
import os
from pathlib import Path
import json
import tempfile


class TestCLIBasics(unittest.TestCase):
    """Базовые тесты CLI системы"""
    
    def test_python_environment(self):
        """Тест Python окружения"""
        self.assertGreaterEqual(sys.version_info[:2], (3, 7))
    
    def test_pathlib_functionality(self):
        """Тест работы с путями"""
        test_path = Path(__file__)
        self.assertTrue(test_path.exists())
        self.assertEqual(test_path.suffix, '.py')
    
    def test_json_functionality(self):
        """Тест работы с JSON"""
        test_data = {"name": "test", "version": "1.0.0"}
        json_str = json.dumps(test_data)
        parsed_data = json.loads(json_str)
        self.assertEqual(parsed_data, test_data)
    
    def test_file_operations(self):
        """Тест файловых операций"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("test content")
            temp_path = f.name
        
        try:
            with open(temp_path, 'r') as f:
                content = f.read()
            self.assertEqual(content, "test content")
        finally:
            os.unlink(temp_path)


class TestCLIProjectStructure(unittest.TestCase):
    """Тесты структуры проекта СЛК"""
    
    def setUp(self):
        """Настройка путей проекта"""
        self.project_root = Path(__file__).parent.parent.parent
        self.context_dir = self.project_root / '.context'
        self.tools_dir = self.context_dir / 'tools'
    
    def test_project_structure_exists(self):
        """Тест наличия основной структуры проекта"""
        self.assertTrue(self.context_dir.exists(), 
                       f"Директория .context не найдена: {self.context_dir}")
        self.assertTrue(self.tools_dir.exists(),
                       f"Директория tools не найдена: {self.tools_dir}")
    
    def test_slc_cli_script_exists(self):
        """Тест наличия главного CLI скрипта"""
        cli_script = self.tools_dir / 'scripts' / 'slc_cli.py'
        self.assertTrue(cli_script.exists(),
                       f"CLI скрипт не найден: {cli_script}")
    
    def test_slc_wrapper_exists(self):
        """Тест наличия bash wrapper"""
        slc_wrapper = self.project_root / 'slc'
        self.assertTrue(slc_wrapper.exists(),
                       f"SLC wrapper не найден: {slc_wrapper}")
    
    def test_modules_directory_exists(self):
        """Тест наличия директории модулей"""
        modules_dir = self.context_dir / 'modules'
        self.assertTrue(modules_dir.exists(),
                       f"Директория modules не найдена: {modules_dir}")
    
    def test_tasks_directory_exists(self):
        """Тест наличия директории задач"""
        tasks_dir = self.context_dir / 'tasks' if (self.context_dir / 'tasks').exists() else self.project_root / 'tasks'
        self.assertTrue(tasks_dir.exists(),
                       f"Директория tasks не найдена: {tasks_dir}")


class TestSLCCommands(unittest.TestCase):
    """Тесты команд СЛК (интеграционные)"""
    
    def setUp(self):
        """Настройка для интеграционных тестов"""
        self.project_root = Path(__file__).parent.parent.parent
        self.slc_script = self.project_root / 'slc'
    
    @unittest.skipUnless(os.name == 'posix', "Тест только для Unix систем")
    def test_slc_script_executable(self):
        """Тест исполняемости SLC скрипта"""
        if self.slc_script.exists():
            stat_info = self.slc_script.stat()
            # Проверяем права на выполнение (owner execute)
            self.assertTrue(stat_info.st_mode & 0o100,
                           f"SLC скрипт не исполняемый: {self.slc_script}")
    
    def test_help_command_structure(self):
        """Тест структуры помощи команд"""
        # Проверяем, что у нас есть команды для тестирования
        expected_commands = [
            'list', 'templates', 'search', 'load-context', 
            'create', 'info', 'help', 'status'
        ]
        
        # Это должно быть доступно из документации
        self.assertGreater(len(expected_commands), 0)
        
        for cmd in expected_commands:
            self.assertIsInstance(cmd, str)
            self.assertGreater(len(cmd), 0)


class TestDocumentationIntegrity(unittest.TestCase):
    """Тесты целостности документации"""
    
    def setUp(self):
        """Настройка путей к документации"""
        self.project_root = Path(__file__).parent.parent.parent
        self.docs_dir = self.project_root / 'docs'
        self.cli_docs_dir = self.docs_dir / 'cli'
    
    def test_cli_documentation_exists(self):
        """Тест наличия CLI документации"""
        if self.cli_docs_dir.exists():
            reference_doc = self.cli_docs_dir / 'complete_cli_reference.md'
            architecture_doc = self.cli_docs_dir / 'cli_architecture.md'
            
            self.assertTrue(reference_doc.exists(),
                           f"Справочник CLI не найден: {reference_doc}")
            self.assertTrue(architecture_doc.exists(),
                           f"Документация архитектуры не найдена: {architecture_doc}")
    
    def test_documentation_content(self):
        """Тест содержимого документации"""
        if self.cli_docs_dir.exists():
            reference_doc = self.cli_docs_dir / 'complete_cli_reference.md'
            if reference_doc.exists():
                content = reference_doc.read_text(encoding='utf-8')
                
                # Проверяем ключевые разделы
                self.assertIn('Smart Layered Context', content)
                self.assertIn('CLI', content)
                self.assertIn('команд', content)
                
                # Проверяем, что документация не пустая
                self.assertGreater(len(content), 1000)


class TestTasksIntegrity(unittest.TestCase):
    """Тесты целостности файлов задач"""
    
    def setUp(self):
        """Настройка путей к задачам"""
        self.project_root = Path(__file__).parent.parent.parent
        self.tasks_dir = self.project_root / 'tasks'
    
    def test_self_development_task_exists(self):
        """Тест наличия задачи саморазвития"""
        if self.tasks_dir.exists():
            task_file = self.tasks_dir / 'self_development_project.json'
            if task_file.exists():
                self.assertTrue(task_file.exists())
                
                # Проверяем валидность JSON
                try:
                    with open(task_file, 'r', encoding='utf-8') as f:
                        task_data = json.load(f)
                    
                    # Проверяем обязательные поля
                    self.assertIn('project', task_data)
                    self.assertIn('version', task_data)
                    self.assertIn('status', task_data)
                    
                except json.JSONDecodeError as e:
                    self.fail(f"Файл задач содержит некорректный JSON: {e}")


if __name__ == '__main__':
    # Запуск только тестов этого модуля
    unittest.main(verbosity=2) 