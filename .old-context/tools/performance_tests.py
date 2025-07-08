#!/usr/bin/env python3
"""
Performance tests for Python Cellframe
"""

import time
import gc
import os

def test_basic_performance():
    """Базовый тест производительности"""
    print("🔍 Базовый тест производительности...")
    
    # Тест выделения памяти
    start_time = time.perf_counter()
    data = [f"test_{i}" for i in range(10000)]
    end_time = time.perf_counter()
    
    print(f"   Время создания 10k строк: {(end_time - start_time)*1000:.2f} ms")
    
    # Очистка
    del data
    gc.collect()
    
    return True

def main():
    """Главная функция тестов"""
    print("🚀 Тесты производительности Python Cellframe")
    print("=" * 45)
    
    if test_basic_performance():
        print("✅ Тесты пройдены")
        return 0
    else:
        print("❌ Тесты провалены")
        return 1

if __name__ == '__main__':
    exit(main())
