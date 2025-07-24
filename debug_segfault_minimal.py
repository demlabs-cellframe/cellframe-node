#!/usr/bin/env python3

import sys
import os

# Добавляем путь к библиотеке
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lib'))

print("=== МИНИМАЛЬНЫЙ ТЕСТ ДЛЯ ИЗОЛЯЦИИ SEGFAULT ===")

import python_dap

# Повторяем цикл init/deinit несколько раз как в тестах
for i in range(5):
    print(f"\n--- ЦИКЛ {i+1} ---")
    
    try:
        # Создаем уникальные директории для каждого цикла
        test_dir = f"/tmp/debug_cycle_{i}"
        os.makedirs(f"{test_dir}/etc", exist_ok=True)
        os.makedirs(f"{test_dir}/tmp", exist_ok=True)
        os.makedirs(f"{test_dir}/var/log", exist_ok=True)
        
        print(f"1. Инициализация цикла {i+1}...")
        result = python_dap.dap_sdk_init(
            f"debug_test_{i}",
            test_dir,
            f"{test_dir}/etc", 
            f"{test_dir}/tmp",
            f"{test_dir}/var/log/debug.log",
            2,
            5000,
            True
        )
        print(f"   dap_sdk_init вернул: {result}")
        
        if result != 0:
            print(f"   ОШИБКА: Инициализация неудачна в цикле {i+1}")
            break
            
        print(f"2. Деинициализация цикла {i+1}...")
        python_dap.dap_sdk_deinit()
        print(f"   dap_sdk_deinit завершен для цикла {i+1}")
        
    except Exception as e:
        print(f"ОШИБКА в цикле {i+1}: {e}")
        import traceback
        traceback.print_exc()
        break

print("\n=== ТЕСТ ЗАВЕРШЕН ===") 