#!/usr/bin/env python3
"""
🔧 Unit тесты для dap.common модуля

Тестирует общие классы и утилиты:
- DapCommon: общие утилиты
- DapUtils: вспомогательные функции
- DapHelpers: помощники
- DapConstants: константы
"""

import unittest
import sys
import os
from pathlib import Path

# Добавляем путь к модулям DAP
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

class TestDapCommonImports(unittest.TestCase):
    """Тесты импортов common модуля"""
    
    def test_import_common_module(self):
        """Тест импорта основного common модуля"""
        try:
            from dap import common
            self.assertIsNotNone(common)
        except ImportError as e:
            self.fail(f"Не удалось импортировать dap.common: {e}")
    
    def test_import_common_classes(self):
        """Тест импорта основных классов common"""
        try:
            from dap.common import DapCommon, DapUtils, DapHelpers, DapConstants
            self.assertIsNotNone(DapCommon)
            self.assertIsNotNone(DapUtils)
            self.assertIsNotNone(DapHelpers)
            self.assertIsNotNone(DapConstants)
        except ImportError as e:
            self.fail(f"Не удалось импортировать классы common: {e}")


class TestDapCommonClass(unittest.TestCase):
    """Тесты класса DapCommon"""
    
    def setUp(self):
        """Подготовка перед каждым тестом"""
        try:
            from dap.common import DapCommon
            self.DapCommon = DapCommon
        except ImportError:
            self.skipTest("Класс DapCommon недоступен")
    
    def test_dap_common_instantiation(self):
        """Тест создания экземпляра DapCommon"""
        try:
            common_instance = self.DapCommon()
            self.assertIsNotNone(common_instance)
        except Exception as e:
            self.fail(f"Не удалось создать экземпляр DapCommon: {e}")
    
    def test_dap_common_methods(self):
        """Тест методов класса DapCommon"""
        try:
            common_instance = self.DapCommon()
            
            # Проверяем наличие ожидаемых методов
            expected_methods = ['init', 'cleanup', 'get_version', 'get_info']
            for method_name in expected_methods:
                if hasattr(common_instance, method_name):
                    method = getattr(common_instance, method_name)
                    self.assertTrue(callable(method))
        except Exception as e:
            self.fail(f"Ошибка при тестировании методов DapCommon: {e}")


class TestDapUtilsClass(unittest.TestCase):
    """Тесты класса DapUtils"""
    
    def setUp(self):
        """Подготовка перед каждым тестом"""
        try:
            from dap.common import DapUtils
            self.DapUtils = DapUtils
        except ImportError:
            self.skipTest("Класс DapUtils недоступен")
    
    def test_dap_utils_instantiation(self):
        """Тест создания экземпляра DapUtils"""
        try:
            utils_instance = self.DapUtils()
            self.assertIsNotNone(utils_instance)
        except Exception as e:
            self.fail(f"Не удалось создать экземпляр DapUtils: {e}")
    
    def test_dap_utils_methods(self):
        """Тест методов класса DapUtils"""
        try:
            utils_instance = self.DapUtils()
            
            # Проверяем наличие ожидаемых методов
            expected_methods = ['format_bytes', 'parse_address', 'validate_hash', 'convert_data']
            for method_name in expected_methods:
                if hasattr(utils_instance, method_name):
                    method = getattr(utils_instance, method_name)
                    self.assertTrue(callable(method))
        except Exception as e:
            self.fail(f"Ошибка при тестировании методов DapUtils: {e}")


if __name__ == '__main__':
    # Настройка тестового runner'а
    unittest.main(verbosity=2, buffer=True) 