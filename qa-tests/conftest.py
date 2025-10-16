#!/usr/bin/env python3
"""
Global pytest configuration
Глобальная конфигурация pytest для всех тестов
"""

import pytest
import logging
import sys
import os
from pathlib import Path

# Добавляем framework в Python path
sys.path.insert(0, str(Path(__file__).parent))

from framework import get_config, NodeCLI, NodeAssertions
from framework.fixtures import *


def pytest_configure(config):
    """Конфигурация pytest"""
    
    # Настройка логирования
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('test_execution.log')
        ]
    )
    
    # Кастомные маркеры
    config.addinivalue_line("markers", "smoke: smoke tests - быстрые проверки основной функциональности")
    config.addinivalue_line("markers", "integration: integration tests - тесты взаимодействия компонентов")
    config.addinivalue_line("markers", "e2e: end-to-end tests - полные сценарии использования")
    config.addinivalue_line("markers", "performance: performance tests - тесты производительности")
    config.addinivalue_line("markers", "network: network-related tests - сетевые тесты")
    config.addinivalue_line("markers", "cli: CLI-related tests - тесты CLI интерфейса")
    config.addinivalue_line("markers", "slow: slow tests (> 30s) - медленные тесты")
    config.addinivalue_line("markers", "critical: critical functionality tests - критически важные тесты")
    config.addinivalue_line("markers", "stability: stability tests - тесты стабильности")


def pytest_collection_modifyitems(config, items):
    """Модификация собранных тестов"""
    
    # Автоматически добавляем маркер slow для тестов с большим timeout
    for item in items:
        # Проверяем timeout маркер
        timeout_marker = item.get_closest_marker("timeout")
        if timeout_marker and timeout_marker.args[0] > 30:
            item.add_marker(pytest.mark.slow)
        
        # Добавляем маркер critical для smoke тестов
        if item.get_closest_marker("smoke"):
            item.add_marker(pytest.mark.critical)


def pytest_runtest_setup(item):
    """Настройка перед каждым тестом"""
    
    # Проверяем что нода доступна для тестов, требующих её
    if any(marker.name in ['integration', 'e2e', 'network'] for marker in item.iter_markers()):
        try:
            node_cli = NodeCLI()
            if not node_cli.is_node_running():
                pytest.skip("Node is not running - required for this test category")
        except Exception as e:
            pytest.skip(f"Cannot access node: {e}")


def pytest_runtest_teardown(item, nextitem):
    """Очистка после каждого теста"""
    
    # Логируем завершение теста
    logging.info(f"Test completed: {item.nodeid}")


def pytest_sessionstart(session):
    """Начало сессии тестирования"""
    
    logging.info("=== Cellframe Node QA Test Session Started ===")
    
    # Загружаем и валидируем конфигурацию
    try:
        config = get_config()
        logging.info(f"Test configuration loaded:")
        logging.info(f"  Environment: {config.environment}")
        logging.info(f"  Node directory: {config.node.base_dir}")
        logging.info(f"  Debug mode: {config.debug_mode}")
        logging.info(f"  Test networks: {config.networks.test_networks}")
        
    except Exception as e:
        logging.error(f"Failed to load test configuration: {e}")
        pytest.exit("Configuration error", returncode=1)
    
    # Проверяем доступность основных компонентов
    try:
        node_cli = NodeCLI()
        if node_cli.is_node_running():
            node_info = node_cli.get_node_info()
            logging.info(f"Node detected: version {node_info.version}, PID {node_info.pid}")
        else:
            logging.warning("Node is not running - some tests may be skipped")
            
    except Exception as e:
        logging.warning(f"Node check failed: {e}")


def pytest_sessionfinish(session, exitstatus):
    """Завершение сессии тестирования"""
    
    logging.info("=== Cellframe Node QA Test Session Finished ===")
    logging.info(f"Exit status: {exitstatus}")
    
    # Статистика по результатам
    if hasattr(session, 'testscollected'):
        logging.info(f"Tests collected: {session.testscollected}")
    
    if hasattr(session, 'testsfailed'):
        logging.info(f"Tests failed: {session.testsfailed}")


# Глобальные фикстуры
@pytest.fixture(scope="session")
def node_assertions():
    """Глобальная фикстура для assertions"""
    return NodeAssertions()


@pytest.fixture(autouse=True)
def test_logging(request):
    """Автоматическое логирование для каждого теста"""
    
    test_name = request.node.nodeid
    logging.info(f"Starting test: {test_name}")
    
    yield
    
    logging.info(f"Finished test: {test_name}")


# Хуки для интеграции с Allure
def pytest_runtest_makereport(item, call):
    """Создание отчета о тесте для Allure"""
    
    if call.when == "call":
        # Добавляем дополнительную информацию в Allure отчет
        try:
            import allure
            
            # Добавляем информацию об окружении
            config = get_config()
            allure.attach(
                f"Environment: {config.environment}\n"
                f"Node directory: {config.node.base_dir}\n"
                f"Test timeout: {config.timeout_sec}s\n"
                f"Debug mode: {config.debug_mode}",
                name="Test Environment",
                attachment_type=allure.attachment_type.TEXT
            )
            
            # Если тест упал, добавляем системную информацию
            if call.excinfo is not None:
                try:
                    node_cli = NodeCLI()
                    if node_cli.is_node_running():
                        health_report = node_cli.validate_node_health()
                        allure.attach(
                            str(health_report),
                            name="Node Health at Failure",
                            attachment_type=allure.attachment_type.JSON
                        )
                except Exception:
                    pass  # Не падаем если не можем получить health report
                    
        except ImportError:
            pass  # Allure не установлен
        except Exception as e:
            logging.warning(f"Failed to add Allure attachments: {e}")


# Конфигурация для параллельного выполнения (pytest-xdist)
def pytest_configure_node(node):
    """Конфигурация для worker node при параллельном выполнении"""
    
    # Каждый worker получает уникальный ID
    worker_id = getattr(node, 'workerinput', {}).get('workerid', 'master')
    logging.info(f"Configuring worker: {worker_id}")


# Фильтры для выбора тестов
def pytest_addoption(parser):
    """Добавление кастомных опций командной строки"""
    
    parser.addoption(
        "--run-slow", action="store_true", default=False,
        help="run slow tests"
    )
    
    parser.addoption(
        "--node-required", action="store_true", default=False,
        help="skip tests if node is not running"
    )
    
    parser.addoption(
        "--test-category", action="store", default=None,
        help="run only specific test category (smoke/integration/e2e)"
    )


def pytest_collection_modifyitems(config, items):
    """Модификация коллекции тестов на основе опций"""
    
    # Пропускаем медленные тесты если не указано --run-slow
    if not config.getoption("--run-slow"):
        skip_slow = pytest.mark.skip(reason="need --run-slow option to run")
        for item in items:
            if "slow" in item.keywords:
                item.add_marker(skip_slow)
    
    # Фильтрация по категории тестов
    test_category = config.getoption("--test-category")
    if test_category:
        selected_items = []
        for item in items:
            if test_category in item.keywords:
                selected_items.append(item)
        items[:] = selected_items
    
    # Проверка доступности ноды
    if config.getoption("--node-required"):
        try:
            node_cli = NodeCLI()
            if not node_cli.is_node_running():
                pytest.exit("Node is required but not running", returncode=1)
        except Exception as e:
            pytest.exit(f"Cannot access node: {e}", returncode=1)
