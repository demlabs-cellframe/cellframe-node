#!/usr/bin/env python3
"""
Test Data for Network Tests
Тестовые данные для сетевых тестов
"""

import pytest
from typing import Dict, List, Any


# Данные для тестирования сетей
NETWORK_TEST_DATA = {
    'backbone': {
        'name': 'Backbone',
        'expected_states': ['NET_STATE_ONLINE', 'NET_STATE_OFFLINE', 'NET_STATE_CONNECTING'],
        'valid_commands': [
            'net -net Backbone get status',
            'net -net Backbone get info'
        ],
        'invalid_commands': [
            'net -net Backbone invalid_command',
            'net -net Backbone get nonexistent'
        ]
    },
    'kelvpn': {
        'name': 'KelVPN',
        'expected_states': ['NET_STATE_ONLINE', 'NET_STATE_OFFLINE', 'NET_STATE_CONNECTING'],
        'valid_commands': [
            'net -net KelVPN get status',
            'net -net KelVPN get info'
        ],
        'invalid_commands': [
            'net -net KelVPN invalid_command',
            'net -net KelVPN get nonexistent'
        ]
    }
}

# Данные для тестирования производительности
PERFORMANCE_TEST_DATA = {
    'response_time_limits': {
        'version': 2.0,  # секунды
        'help': 1.0,
        'network_status': 5.0,
        'network_info': 10.0
    },
    'resource_limits': {
        'memory_mb': 1024,
        'cpu_percent': 50.0,
        'startup_time_sec': 60
    },
    'concurrent_test_params': {
        'max_workers': 4,
        'test_duration_sec': 30,
        'expected_efficiency': 1.5  # минимальная эффективность параллелизма
    }
}

# Данные для стресс-тестирования
STRESS_TEST_DATA = {
    'stability_test': {
        'duration_minutes': 5,
        'check_interval_seconds': 30,
        'min_success_rate': 0.95,
        'max_memory_growth_mb': 200
    },
    'load_test': {
        'concurrent_requests': 10,
        'requests_per_second': 2,
        'test_duration_sec': 60
    }
}

# Валидные и невалидные команды для тестирования
COMMAND_TEST_DATA = {
    'valid_commands': [
        ('version', 'Get node version'),
        ('help', 'Get help information'),
        ('net -net Backbone get status', 'Get Backbone status'),
        ('net -net KelVPN get status', 'Get KelVPN status')
    ],
    'invalid_commands': [
        ('invalid_command_xyz', 'Non-existent command'),
        ('net -net NonExistentNetwork get status', 'Non-existent network'),
        ('version --invalid-flag', 'Invalid flag'),
        ('', 'Empty command')
    ],
    'malformed_commands': [
        ('net -net', 'Incomplete network command'),
        ('net get status', 'Missing network parameter'),
        ('net -net Backbone', 'Incomplete command')
    ]
}

# Ожидаемые паттерны в выводе команд
OUTPUT_PATTERNS = {
    'version': [
        r'cellframe-node\s+version\s+[\d\.]+-?\d*',
        r'build\s+\d{4}-\d{2}-\d{2}',
    ],
    'help': [
        r'Usage:',
        r'Commands:',
        r'Options:'
    ],
    'network_status': {
        'backbone': [
            r'net:\s*Backbone',
            r'State:\s*\w+',
        ],
        'kelvpn': [
            r'net:\s*KelVPN',
            r'State:\s*\w+',
        ]
    }
}

# Конфигурация для различных окружений
ENVIRONMENT_CONFIG = {
    'docker': {
        'node_startup_timeout': 60,
        'network_ready_timeout': 120,
        'expected_memory_usage_mb': 512,
        'expected_cpu_usage_percent': 30.0
    },
    'local': {
        'node_startup_timeout': 30,
        'network_ready_timeout': 60,
        'expected_memory_usage_mb': 256,
        'expected_cpu_usage_percent': 20.0
    },
    'ci': {
        'node_startup_timeout': 90,
        'network_ready_timeout': 180,
        'expected_memory_usage_mb': 768,
        'expected_cpu_usage_percent': 40.0
    }
}


# Параметризованные данные для pytest
@pytest.fixture(params=NETWORK_TEST_DATA.keys())
def network_data(request):
    """Фикстура для параметризации тестов по сетям"""
    return NETWORK_TEST_DATA[request.param]


@pytest.fixture(params=COMMAND_TEST_DATA['valid_commands'])
def valid_command_data(request):
    """Фикстура для валидных команд"""
    return request.param


@pytest.fixture(params=COMMAND_TEST_DATA['invalid_commands'])
def invalid_command_data(request):
    """Фикстура для невалидных команд"""
    return request.param


def get_network_test_data(network_name: str) -> Dict[str, Any]:
    """Получить тестовые данные для конкретной сети"""
    return NETWORK_TEST_DATA.get(network_name.lower(), {})


def get_performance_limits(environment: str = 'docker') -> Dict[str, Any]:
    """Получить лимиты производительности для окружения"""
    env_config = ENVIRONMENT_CONFIG.get(environment, ENVIRONMENT_CONFIG['docker'])
    performance_limits = PERFORMANCE_TEST_DATA['resource_limits'].copy()
    
    # Адаптируем лимиты под окружение
    performance_limits.update({
        'memory_mb': env_config['expected_memory_usage_mb'] * 2,  # Удваиваем для лимита
        'cpu_percent': env_config['expected_cpu_usage_percent'] * 1.5,  # 1.5x для лимита
        'startup_time_sec': env_config['node_startup_timeout']
    })
    
    return performance_limits


def get_expected_patterns(command_type: str, network_name: str = None) -> List[str]:
    """Получить ожидаемые паттерны для команды"""
    if command_type in OUTPUT_PATTERNS:
        patterns = OUTPUT_PATTERNS[command_type]
        
        if isinstance(patterns, dict) and network_name:
            return patterns.get(network_name.lower(), [])
        elif isinstance(patterns, list):
            return patterns
    
    return []


# Генераторы тестовых данных
def generate_stress_test_scenarios():
    """Генерировать сценарии для стресс-тестирования"""
    scenarios = []
    
    # Различные комбинации нагрузки
    for duration in [1, 5, 10]:  # минуты
        for interval in [10, 30, 60]:  # секунды
            scenarios.append({
                'duration_minutes': duration,
                'check_interval_seconds': interval,
                'scenario_name': f'stress_{duration}m_{interval}s'
            })
    
    return scenarios


def generate_concurrent_test_scenarios():
    """Генерировать сценарии для тестирования параллелизма"""
    scenarios = []
    
    # Различные уровни параллелизма
    for workers in [2, 4, 8]:
        for duration in [30, 60]:  # секунды
            scenarios.append({
                'max_workers': workers,
                'test_duration_sec': duration,
                'scenario_name': f'concurrent_{workers}w_{duration}s'
            })
    
    return scenarios


# Утилиты для работы с тестовыми данными
class TestDataManager:
    """Менеджер тестовых данных"""
    
    @staticmethod
    def get_network_commands(network_name: str, command_type: str = 'valid') -> List[str]:
        """Получить команды для сети"""
        network_data = get_network_test_data(network_name)
        
        if command_type == 'valid':
            return network_data.get('valid_commands', [])
        elif command_type == 'invalid':
            return network_data.get('invalid_commands', [])
        
        return []
    
    @staticmethod
    def validate_test_data():
        """Валидация тестовых данных"""
        errors = []
        
        # Проверяем что все сети имеют необходимые поля
        for network_name, network_data in NETWORK_TEST_DATA.items():
            required_fields = ['name', 'expected_states', 'valid_commands']
            
            for field in required_fields:
                if field not in network_data:
                    errors.append(f"Network {network_name} missing field: {field}")
        
        # Проверяем лимиты производительности
        for env_name, env_config in ENVIRONMENT_CONFIG.items():
            required_fields = ['node_startup_timeout', 'network_ready_timeout']
            
            for field in required_fields:
                if field not in env_config:
                    errors.append(f"Environment {env_name} missing field: {field}")
        
        if errors:
            raise ValueError(f"Test data validation failed: {errors}")
        
        return True


# Валидация при импорте модуля
if __name__ == "__main__":
    TestDataManager.validate_test_data()
    print("Test data validation passed")
