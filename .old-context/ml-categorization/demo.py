#!/usr/bin/env python3
"""
ML Categorization Demo
Демонстрация системы автоматической категоризации функций
"""

import json
import re
from typing import Dict, Tuple

class SimpleCategorizer:
    """Упрощенная система категоризации"""
    
    def __init__(self):
        self.categories = {
            'critical_core': {
                'patterns': [r'^dap_common_.*', r'.*_init$', r'.*_deinit$'],
                'keywords': ['init', 'deinit', 'core', 'main']
            },
            'blockchain_operations': {
                'patterns': [r'^dap_chain_.*', r'^dap_ledger_.*'],
                'keywords': ['chain', 'block', 'ledger', 'transaction']
            },
            'cryptography': {
                'patterns': [r'^dap_enc_.*', r'^dap_hash_.*'],
                'keywords': ['crypto', 'hash', 'sign', 'encrypt']
            },
            'network_layer': {
                'patterns': [r'^dap_stream_.*', r'^dap_client_.*'],
                'keywords': ['net', 'stream', 'client', 'server']
            }
        }
    
    def categorize(self, function_name: str) -> Tuple[str, float]:
        """Категоризирует функцию"""
        for category, config in self.categories.items():
            # Проверяем паттерны
            for pattern in config['patterns']:
                if re.match(pattern, function_name, re.IGNORECASE):
                    return category, 0.9
            
            # Проверяем ключевые слова
            for keyword in config['keywords']:
                if keyword in function_name.lower():
                    return category, 0.7
        
        return 'utilities', 0.5
    
    def demo(self):
        """Демонстрация работы"""
        test_functions = [
            'dap_common_init',
            'dap_chain_ledger_get',
            'dap_enc_key_generate',
            'dap_stream_client_connect',
            'dap_string_duplicate'
        ]
        
        print("🤖 Демонстрация ML категоризации:")
        for func in test_functions:
            category, confidence = self.categorize(func)
            print(f"   {func} -> {category} (уверенность: {confidence:.1f})")

if __name__ == '__main__':
    categorizer = SimpleCategorizer()
    categorizer.demo()
