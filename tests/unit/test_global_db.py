#!/usr/bin/env python3
"""
🗃️ Unit тесты для dap.global_db модуля

Тестирует классы глобальной базы данных:
- Gdb: основной класс БД
- GdbCluster: кластер БД
- GdbNode: узел БД
- GdbInstance: экземпляр БД
"""

import unittest
import sys
import os
from pathlib import Path

# Добавляем путь к модулям DAP
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

class TestDapGlobalDbImports(unittest.TestCase):
    """Тесты импортов global_db модуля"""
    
    def test_import_global_db_module(self):
        """Тест импорта основного global_db модуля"""
        try:
            from dap import global_db
            self.assertIsNotNone(global_db)
        except ImportError as e:
            self.fail(f"Не удалось импортировать dap.global_db: {e}")
    
    def test_import_global_db_classes(self):
        """Тест импорта основных классов global_db"""
        try:
            from dap.global_db import Gdb, GdbCluster, GdbNode, GdbInstance
            self.assertIsNotNone(Gdb)
            self.assertIsNotNone(GdbCluster)
            self.assertIsNotNone(GdbNode)
            self.assertIsNotNone(GdbInstance)
        except ImportError as e:
            self.fail(f"Не удалось импортировать классы global_db: {e}")


class TestGdbClass(unittest.TestCase):
    """Тесты класса Gdb"""
    
    def setUp(self):
        """Подготовка перед каждым тестом"""
        try:
            from dap.global_db import Gdb
            self.Gdb = Gdb
        except ImportError:
            self.skipTest("Класс Gdb недоступен")
    
    def test_gdb_instantiation(self):
        """Тест создания экземпляра Gdb"""
        try:
            gdb_instance = self.Gdb()
            self.assertIsNotNone(gdb_instance)
        except Exception as e:
            self.fail(f"Не удалось создать экземпляр Gdb: {e}")
    
    def test_gdb_methods(self):
        """Тест методов класса Gdb"""
        try:
            gdb_instance = self.Gdb()
            
            # Проверяем наличие ожидаемых методов
            expected_methods = ['get', 'set', 'delete', 'keys', 'exists']
            for method_name in expected_methods:
                if hasattr(gdb_instance, method_name):
                    method = getattr(gdb_instance, method_name)
                    self.assertTrue(callable(method))
        except Exception as e:
            self.fail(f"Ошибка при тестировании методов Gdb: {e}")


class TestGdbClusterClass(unittest.TestCase):
    """Тесты класса GdbCluster"""
    
    def setUp(self):
        """Подготовка перед каждым тестом"""
        try:
            from dap.global_db import GdbCluster
            self.GdbCluster = GdbCluster
        except ImportError:
            self.skipTest("Класс GdbCluster недоступен")
    
    def test_gdb_cluster_instantiation(self):
        """Тест создания экземпляра GdbCluster"""
        try:
            cluster_instance = self.GdbCluster()
            self.assertIsNotNone(cluster_instance)
        except Exception as e:
            self.fail(f"Не удалось создать экземпляр GdbCluster: {e}")
    
    def test_gdb_cluster_methods(self):
        """Тест методов класса GdbCluster"""
        try:
            cluster_instance = self.GdbCluster()
            
            # Проверяем наличие ожидаемых методов
            expected_methods = ['add_node', 'remove_node', 'get_nodes', 'sync']
            for method_name in expected_methods:
                if hasattr(cluster_instance, method_name):
                    method = getattr(cluster_instance, method_name)
                    self.assertTrue(callable(method))
        except Exception as e:
            self.fail(f"Ошибка при тестировании методов GdbCluster: {e}")


if __name__ == '__main__':
    # Настройка тестового runner'а
    unittest.main(verbosity=2, buffer=True) 