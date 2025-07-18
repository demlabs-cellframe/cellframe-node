#!/usr/bin/env python3
"""
🏃‍♂️ Runner для всех unit тестов Python DAP SDK

Запускает все unit тесты модулей:
- test_core.py: тесты core модуля
- test_crypto.py: тесты crypto модуля  
- test_network.py: тесты network модуля
- test_config.py: тесты config модуля
- test_events.py: тесты events модуля
- test_global_db.py: тесты global_db модуля
- test_common.py: тесты common модуля
"""

import unittest
import sys
import os
from pathlib import Path

# Добавляем путь к модулям DAP
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

def run_all_unit_tests():
    """Запуск всех unit тестов"""
    
    # Находим все тестовые файлы
    test_dir = Path(__file__).parent
    test_files = [
        'test_core.py',
        'test_crypto.py', 
        'test_network.py',
        'test_config.py',
        'test_events.py',
        'test_global_db.py',
        'test_common.py'
    ]
    
    print("🚀 Запуск всех unit тестов Python DAP SDK")
    print("=" * 60)
    
    # Создаем test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Добавляем тесты из каждого файла
    for test_file in test_files:
        test_path = test_dir / test_file
        if test_path.exists():
            print(f"📝 Загружаю тесты из {test_file}")
            try:
                # Импортируем модуль
                module_name = test_file[:-3]  # убираем .py
                spec = unittest.util.spec_from_file_location(module_name, test_path)
                module = unittest.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Добавляем тесты в suite
                module_suite = loader.loadTestsFromModule(module)
                suite.addTest(module_suite)
                
            except Exception as e:
                print(f"⚠️  Ошибка загрузки {test_file}: {e}")
        else:
            print(f"❌ Файл {test_file} не найден")
    
    print("=" * 60)
    
    # Запускаем тесты
    runner = unittest.TextTestRunner(
        verbosity=2,
        buffer=True,
        stream=sys.stdout
    )
    
    result = runner.run(suite)
    
    # Выводим итоговую статистику
    print("=" * 60)
    print(f"📊 Результаты тестирования:")
    print(f"   ✅ Успешно: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"   ❌ Провалено: {len(result.failures)}")
    print(f"   💥 Ошибки: {len(result.errors)}")
    print(f"   ⏭️  Пропущено: {len(result.skipped) if hasattr(result, 'skipped') else 0}")
    print(f"   📈 Всего тестов: {result.testsRun}")
    
    if result.wasSuccessful():
        print("🎉 Все тесты прошли успешно!")
        return 0
    else:
        print("⚠️  Есть проваленные тесты")
        return 1


if __name__ == '__main__':
    sys.exit(run_all_unit_tests()) 