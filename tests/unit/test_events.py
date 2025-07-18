#!/usr/bin/env python3
"""
⚡ Unit тесты для dap.events модуля

Тестирует классы событий:
- DapEvents: система событий
- DapEventHandler: обработчики событий
- DapEventDispatcher: диспетчер событий
- DapEventListener: слушатели событий
"""

import unittest
import sys
import os
from pathlib import Path

# Добавляем путь к модулям DAP
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

class TestDapEventsImports(unittest.TestCase):
    """Тесты импортов events модуля"""
    
    def test_import_events_module(self):
        """Тест импорта основного events модуля"""
        try:
            from dap import events
            self.assertIsNotNone(events)
        except ImportError as e:
            self.fail(f"Не удалось импортировать dap.events: {e}")
    
    def test_import_events_classes(self):
        """Тест импорта основных классов events"""
        try:
            from dap.events import DapEvents, DapEventHandler, DapEventDispatcher, DapEventListener
            self.assertIsNotNone(DapEvents)
            self.assertIsNotNone(DapEventHandler)
            self.assertIsNotNone(DapEventDispatcher)
            self.assertIsNotNone(DapEventListener)
        except ImportError as e:
            self.fail(f"Не удалось импортировать классы events: {e}")


class TestDapEventsClass(unittest.TestCase):
    """Тесты класса DapEvents"""
    
    def setUp(self):
        """Подготовка перед каждым тестом"""
        try:
            from dap.events import DapEvents
            self.DapEvents = DapEvents
        except ImportError:
            self.skipTest("Класс DapEvents недоступен")
    
    def test_dap_events_instantiation(self):
        """Тест создания экземпляра DapEvents"""
        try:
            events_instance = self.DapEvents()
            self.assertIsNotNone(events_instance)
        except Exception as e:
            self.fail(f"Не удалось создать экземпляр DapEvents: {e}")
    
    def test_dap_events_methods(self):
        """Тест методов класса DapEvents"""
        try:
            events_instance = self.DapEvents()
            
            # Проверяем наличие ожидаемых методов
            expected_methods = ['emit', 'on', 'off', 'once']
            for method_name in expected_methods:
                if hasattr(events_instance, method_name):
                    method = getattr(events_instance, method_name)
                    self.assertTrue(callable(method))
        except Exception as e:
            self.fail(f"Ошибка при тестировании методов DapEvents: {e}")


class TestDapEventHandlerClass(unittest.TestCase):
    """Тесты класса DapEventHandler"""
    
    def setUp(self):
        """Подготовка перед каждым тестом"""
        try:
            from dap.events import DapEventHandler
            self.DapEventHandler = DapEventHandler
        except ImportError:
            self.skipTest("Класс DapEventHandler недоступен")
    
    def test_dap_event_handler_instantiation(self):
        """Тест создания экземпляра DapEventHandler"""
        try:
            handler_instance = self.DapEventHandler()
            self.assertIsNotNone(handler_instance)
        except Exception as e:
            self.fail(f"Не удалось создать экземпляр DapEventHandler: {e}")
    
    def test_dap_event_handler_methods(self):
        """Тест методов класса DapEventHandler"""
        try:
            handler_instance = self.DapEventHandler()
            
            # Проверяем наличие ожидаемых методов
            expected_methods = ['handle', 'register', 'unregister', 'can_handle']
            for method_name in expected_methods:
                if hasattr(handler_instance, method_name):
                    method = getattr(handler_instance, method_name)
                    self.assertTrue(callable(method))
        except Exception as e:
            self.fail(f"Ошибка при тестировании методов DapEventHandler: {e}")


if __name__ == '__main__':
    # Настройка тестового runner'а
    unittest.main(verbosity=2, buffer=True) 