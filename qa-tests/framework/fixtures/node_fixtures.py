#!/usr/bin/env python3
"""
Node Fixtures
Pytest fixtures для тестирования Cellframe Node
"""

import pytest
import time
import logging
from typing import Generator, Dict, Any

from ..config import get_config
from ..pages.node_cli import NodeCLI, NodeInfo
from ..utils import execute_command


@pytest.fixture(scope="session")
def test_config():
    """Конфигурация тестов (session scope)"""
    return get_config()


@pytest.fixture(scope="session")
def node_cli():
    """CLI интерфейс ноды (session scope)"""
    return NodeCLI()


@pytest.fixture(scope="session")
def ensure_node_running(node_cli: NodeCLI) -> Generator[bool, None, None]:
    """Убедиться что нода запущена перед тестами"""
    config = get_config()
    
    # Проверяем что нода запущена
    if not node_cli.is_node_running():
        pytest.skip("Cellframe Node is not running")
    
    # Ждем готовности ноды
    max_wait = config.limits.max_startup_time_sec
    start_time = time.time()
    
    while time.time() - start_time < max_wait:
        try:
            version_result = node_cli.get_version()
            if version_result.success:
                break
        except Exception:
            pass
        time.sleep(2)
    else:
        pytest.skip(f"Node did not become ready within {max_wait}s")
    
    yield True
    
    # Teardown: проверяем что нода все еще работает
    if not node_cli.is_node_running():
        logging.warning("Node stopped during test execution")


@pytest.fixture(scope="session")
def node_info(node_cli: NodeCLI, ensure_node_running) -> NodeInfo:
    """Информация о ноде (session scope)"""
    return node_cli.get_node_info()


@pytest.fixture(scope="function")
def fresh_node_state(node_cli: NodeCLI, ensure_node_running):
    """Свежее состояние ноды для каждого теста"""
    # Setup: проверяем базовое состояние
    if not node_cli.is_node_running():
        pytest.skip("Node is not running")
    
    yield
    
    # Teardown: можем добавить очистку если нужно
    pass


@pytest.fixture(scope="session")
def wait_for_networks(node_cli: NodeCLI, ensure_node_running) -> Dict[str, Any]:
    """Ждать готовности сетей"""
    config = get_config()
    networks_status = {}
    
    for network_name in config.networks.test_networks:
        try:
            # Пытаемся дождаться онлайн статуса
            status = node_cli.wait_for_network_online(
                network_name, 
                timeout_sec=60
            )
            networks_status[network_name] = status
            logging.info(f"Network {network_name} is online")
            
        except TimeoutError as e:
            logging.warning(f"Network {network_name} timeout: {e}")
            # Получаем последний статус для информации
            try:
                status = node_cli.get_network_status(network_name)
                networks_status[network_name] = status
            except Exception:
                networks_status[network_name] = None
        
        except Exception as e:
            logging.error(f"Failed to check network {network_name}: {e}")
            networks_status[network_name] = None
    
    return networks_status


@pytest.fixture(scope="function")
def performance_monitor(node_cli: NodeCLI, ensure_node_running):
    """Монитор производительности для теста"""
    pid = node_cli.get_node_pid()
    if not pid:
        pytest.skip("Cannot get node PID for performance monitoring")
    
    # Начальные метрики
    start_memory = node_cli.get_memory_usage(pid)
    start_time = time.time()
    
    monitor_data = {
        'pid': pid,
        'start_memory_mb': start_memory,
        'start_time': start_time,
        'peak_memory_mb': start_memory,
        'measurements': []
    }
    
    yield monitor_data
    
    # Финальные метрики
    try:
        end_memory = node_cli.get_memory_usage(pid)
        end_time = time.time()
        
        monitor_data.update({
            'end_memory_mb': end_memory,
            'end_time': end_time,
            'duration_sec': end_time - start_time,
            'memory_delta_mb': end_memory - start_memory
        })
        
        # Логируем результаты
        logging.info(f"Performance monitor results:")
        logging.info(f"  Duration: {monitor_data['duration_sec']:.2f}s")
        logging.info(f"  Memory delta: {monitor_data['memory_delta_mb']:.1f} MB")
        logging.info(f"  Peak memory: {monitor_data['peak_memory_mb']:.1f} MB")
        
    except Exception as e:
        logging.warning(f"Failed to collect final performance metrics: {e}")


@pytest.fixture(scope="function")
def log_capture(test_config):
    """Захват логов во время теста"""
    log_file = test_config.node.log_file
    
    # Получаем текущий размер лога
    try:
        import os
        start_size = os.path.getsize(log_file) if os.path.exists(log_file) else 0
    except Exception:
        start_size = 0
    
    log_data = {
        'log_file': log_file,
        'start_size': start_size,
        'new_entries': []
    }
    
    yield log_data
    
    # Читаем новые записи в логе
    try:
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                f.seek(start_size)
                new_content = f.read()
                if new_content:
                    log_data['new_entries'] = new_content.strip().split('\n')
    except Exception as e:
        logging.warning(f"Failed to capture new log entries: {e}")


@pytest.fixture(scope="function")
def isolated_test_environment(fresh_node_state, log_capture, performance_monitor):
    """Изолированное окружение для теста"""
    test_env = {
        'start_time': time.time(),
        'log_capture': log_capture,
        'performance_monitor': performance_monitor
    }
    
    yield test_env
    
    # Cleanup и отчетность
    test_env['end_time'] = time.time()
    test_env['duration'] = test_env['end_time'] - test_env['start_time']
    
    # Можем добавить автоматические проверки
    if test_env['duration'] > 300:  # 5 минут
        logging.warning(f"Test took too long: {test_env['duration']:.2f}s")


# Маркеры для категоризации тестов
def pytest_configure(config):
    """Конфигурация pytest с кастомными маркерами"""
    config.addinivalue_line("markers", "smoke: smoke tests")
    config.addinivalue_line("markers", "integration: integration tests")
    config.addinivalue_line("markers", "e2e: end-to-end tests")
    config.addinivalue_line("markers", "performance: performance tests")
    config.addinivalue_line("markers", "network: network-related tests")
    config.addinivalue_line("markers", "cli: CLI-related tests")
    config.addinivalue_line("markers", "slow: slow tests (> 30s)")
    config.addinivalue_line("markers", "critical: critical functionality tests")
