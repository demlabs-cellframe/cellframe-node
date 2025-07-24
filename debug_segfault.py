#!/usr/bin/env python3

import sys
import os

# Добавляем путь к библиотеке
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lib'))

print("Импортируем python_dap...")
import python_dap

print("Инициализируем DAP SDK...")
python_dap.dap_common_init()
python_dap.dap_config_init("./test_config.cfg")

print("Тестируем dap_sdk_deinit...")
try:
    python_dap.dap_sdk_deinit()
    print("dap_sdk_deinit завершен успешно")
except Exception as e:
    print(f"Ошибка в dap_sdk_deinit: {e}")

print("Скрипт завершен") 