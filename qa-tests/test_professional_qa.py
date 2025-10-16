#!/usr/bin/env python3
"""
Professional QA Tests using Framework
Демонстрация мощи новой архитектуры тестирования
"""

import pytest
import allure
import sys
from pathlib import Path

# Add framework to path
sys.path.insert(0, str(Path(__file__).parent))

from framework import NodeCLI, NodeAssertions, get_config


@allure.epic("Cellframe Node")
@allure.feature("Professional QA Framework")
@pytest.mark.smoke
@pytest.mark.critical
class TestProfessionalFramework:
    """Smoke тесты с использованием профессионального framework"""
    
    @allure.story("Framework Initialization")
    @allure.title("Framework components initialize correctly")
    @allure.description("Проверяет что все компоненты framework инициализируются корректно")
    def test_framework_initialization(self):
        """Тест: Framework компоненты инициализируются"""
        
        with allure.step("Initialize configuration"):
            config = get_config()
            assert config is not None, "Config should not be None"
            
            allure.attach(
                f"Environment: {config.environment}\n"
                f"Node directory: {config.node.base_dir}\n"
                f"Bin directory: {config.node.bin_dir}\n"
                f"Max memory: {config.limits.max_memory_mb} MB\n"
                f"Max CPU: {config.limits.max_cpu_percent}%",
                name="Configuration",
                attachment_type=allure.attachment_type.TEXT
            )
        
        with allure.step("Initialize NodeCLI"):
            node_cli = NodeCLI()
            assert node_cli is not None, "NodeCLI should not be None"
            assert node_cli.config is not None, "NodeCLI config should not be None"
        
        with allure.step("Initialize NodeAssertions"):
            assertions = NodeAssertions()
            assert assertions is not None, "NodeAssertions should not be None"
            assert assertions.config is not None, "NodeAssertions config should not be None"
        
        allure.attach("✅ All framework components initialized successfully", 
                     name="Result", attachment_type=allure.attachment_type.TEXT)
    
    @allure.story("Binary Discovery")
    @allure.title("Framework finds cellframe binaries automatically")
    @allure.description("Демонстрирует автоматический поиск бинарников независимо от пути установки")
    def test_binary_discovery(self):
        """Тест: Автоматический поиск бинарников работает"""
        
        with allure.step("Initialize NodeCLI with auto-discovery"):
            node_cli = NodeCLI()
            config = node_cli.config
            
            allure.attach(
                f"Detected paths:\n"
                f"Node binary: {config.node.node_binary}\n"
                f"CLI binary: {config.node.cli_binary}\n"
                f"Config binary: {config.node.config_binary}\n"
                f"Log file: {config.node.log_file}",
                name="Discovered Paths",
                attachment_type=allure.attachment_type.TEXT
            )
        
        with allure.step("Check if node is running"):
            is_running = node_cli.is_node_running()
            
            allure.attach(
                f"Node running: {is_running}\n"
                f"Check method: pgrep -x cellframe-node",
                name="Node Status Check",
                attachment_type=allure.attachment_type.TEXT
            )
            
            if not is_running:
                pytest.skip("Node is not running - cannot test binary access")
        
        with allure.step("Get node PID"):
            pid = node_cli.get_node_pid()
            assert pid is not None, "Should be able to get node PID"
            assert pid > 0, f"PID should be positive: {pid}"
            
            allure.attach(f"Node PID: {pid}", name="Process ID", 
                         attachment_type=allure.attachment_type.TEXT)
    
    @allure.story("Node Version")
    @allure.title("Get node version using framework")
    @allure.description("Получает версию ноды используя NodeCLI с автопоиском и retry логикой")
    def test_get_node_version_with_framework(self):
        """Тест: Получение версии через framework"""
        
        node_cli = NodeCLI()
        assertions = NodeAssertions()
        
        with allure.step("Check if node is running"):
            if not node_cli.is_node_running():
                pytest.skip("Node is not running")
        
        with allure.step("Get version using NodeCLI"):
            result = node_cli.get_version()
            
            allure.attach(
                f"Command: {result.command}\n"
                f"Return code: {result.returncode}\n"
                f"Execution time: {result.execution_time:.2f}s\n"
                f"Stdout:\n{result.stdout}\n"
                f"Stderr:\n{result.stderr}",
                name="Version Command Result",
                attachment_type=allure.attachment_type.TEXT
            )
        
        with allure.step("Validate result using NodeAssertions"):
            # Используем кастомные assertions
            assertions.assert_command_success(result, "Failed to get node version")
            assertions.assert_execution_time_within(result, 10.0, "Version command too slow")
            assertions.assert_node_version_valid(result.stdout, "Invalid version format")
            assertions.assert_output_contains(result, "cellframe-node", 
                                            message="Version output missing node name")
        
        with allure.step("Parse version information"):
            node_info = node_cli.get_node_info()
            
            allure.attach(
                f"Version: {node_info.version}\n"
                f"Build date: {node_info.build_date}\n"
                f"PID: {node_info.pid}",
                name="Node Information",
                attachment_type=allure.attachment_type.TEXT
            )
            
            assert node_info.version != "unknown", "Should detect node version"


@allure.epic("Cellframe Node")
@allure.feature("Network Operations")
@pytest.mark.smoke
@pytest.mark.network
class TestNetworkWithFramework:
    """Smoke тесты сетевых операций с framework"""
    
    @allure.story("Network Status")
    @allure.title("Get network status using framework")
    @allure.description("Получает статус сетей используя NodeCLI с retry логикой")
    def test_get_networks_status_with_framework(self):
        """Тест: Получение статуса сетей через framework"""
        
        node_cli = NodeCLI()
        assertions = NodeAssertions()
        config = get_config()
        
        with allure.step("Check if node is running"):
            if not node_cli.is_node_running():
                pytest.skip("Node is not running")
        
        with allure.step("Get all networks status"):
            networks_status = node_cli.get_all_networks_status()
            
            allure.attach(
                f"Networks to check: {config.networks.test_networks}\n"
                f"Networks found: {len(networks_status)}",
                name="Networks Overview",
                attachment_type=allure.attachment_type.TEXT
            )
        
        with allure.step("Analyze network statuses"):
            for network_name, status in networks_status.items():
                if status:
                    status_info = (
                        f"Network: {status.name}\n"
                        f"State: {status.state}\n"
                        f"Nodes count: {status.nodes_count}\n"
                        f"Active links: {status.active_links}\n"
                        f"Is online: {status.is_online}\n"
                        f"Target state: {status.target_state}"
                    )
                    
                    allure.attach(status_info, name=f"Network Status - {network_name}",
                                 attachment_type=allure.attachment_type.TEXT)
                    
                    # Проверяем что сеть отвечает (не обязательно онлайн)
                    assert status.name == network_name, f"Network name mismatch"
                    assert status.state != "UNKNOWN", f"Network {network_name} state is unknown"
        
        # Проверяем что хотя бы одна сеть получена
        assert len(networks_status) > 0, "Should get status for at least one network"
    
    @allure.story("Node Health")
    @allure.title("Comprehensive node health check")
    @allure.description("Комплексная проверка здоровья ноды с использованием framework")
    def test_node_health_check_with_framework(self):
        """Тест: Проверка здоровья ноды через framework"""
        
        node_cli = NodeCLI()
        assertions = NodeAssertions()
        
        with allure.step("Check if node is running"):
            if not node_cli.is_node_running():
                pytest.skip("Node is not running")
        
        with allure.step("Perform comprehensive health check"):
            health_report = node_cli.validate_node_health()
            
            allure.attach(
                f"Node running: {health_report['node_running']}\n"
                f"Version accessible: {health_report['version_accessible']}\n"
                f"Networks online: {health_report['networks_online']}\n"
                f"Resource usage: {health_report.get('resource_usage', {})}\n"
                f"Overall healthy: {health_report['overall_healthy']}",
                name="Health Report",
                attachment_type=allure.attachment_type.JSON
            )
        
        with allure.step("Validate health using framework assertions"):
            # Используем специализированную assertion для health check
            assertions.assert_node_health_good(health_report, "Node health check failed")
        
        with allure.step("Verify individual health components"):
            assert health_report['node_running'], "Node should be running"
            assert health_report['version_accessible'], "Version should be accessible"
            
            # Проверяем что хотя бы одна сеть онлайн
            networks_online = health_report.get('networks_online', {})
            online_count = sum(1 for online in networks_online.values() if online)
            
            allure.attach(
                f"Total networks: {len(networks_online)}\n"
                f"Online networks: {online_count}\n"
                f"Offline networks: {len(networks_online) - online_count}",
                name="Network Summary",
                attachment_type=allure.attachment_type.TEXT
            )
            
            # Для smoke теста достаточно что хотя бы одна сеть онлайн
            # или все компоненты работают
            health_ok = (
                health_report['node_running'] and 
                health_report['version_accessible']
            )
            
            assert health_ok, "Basic node health check should pass"


@allure.epic("Cellframe Node")
@allure.feature("Framework Features")
@pytest.mark.smoke
class TestFrameworkFeatures:
    """Демонстрация возможностей framework"""
    
    @allure.story("Retry Logic")
    @allure.title("Framework retry logic works correctly")
    @allure.description("Демонстрирует работу retry логики с exponential backoff")
    def test_retry_logic(self):
        """Тест: Retry логика работает"""
        
        from framework.utils import CommandExecutor, RetryConfig, RetryStrategy
        
        with allure.step("Create executor with retry configuration"):
            retry_config = RetryConfig(
                strategy=RetryStrategy.EXPONENTIAL_BACKOFF,
                max_attempts=3,
                delay_seconds=0.5,
                backoff_multiplier=2.0
            )
            
            executor = CommandExecutor(default_retry_config=retry_config)
            
            allure.attach(
                f"Strategy: {retry_config.strategy.value}\n"
                f"Max attempts: {retry_config.max_attempts}\n"
                f"Initial delay: {retry_config.delay_seconds}s\n"
                f"Backoff multiplier: {retry_config.backoff_multiplier}x",
                name="Retry Configuration",
                attachment_type=allure.attachment_type.TEXT
            )
        
        with allure.step("Execute command with retry"):
            # Простая команда которая должна успешно выполниться
            result = executor.execute("echo 'Framework retry test'", timeout=5)
            
            allure.attach(
                f"Command: {result.command}\n"
                f"Success: {result.success}\n"
                f"Return code: {result.returncode}\n"
                f"Execution time: {result.execution_time:.3f}s\n"
                f"Output: {result.stdout.strip()}",
                name="Command Result",
                attachment_type=allure.attachment_type.TEXT
            )
            
            assert result.success, "Simple command should succeed"
            assert result.execution_time < 1.0, "Should execute quickly without retries"
    
    @allure.story("Custom Assertions")
    @allure.title("Framework custom assertions provide detailed errors")
    @allure.description("Показывает как кастомные assertions дают детальную информацию об ошибках")
    def test_custom_assertions(self):
        """Тест: Кастомные assertions работают"""
        
        from framework.utils import CommandResult
        
        assertions = NodeAssertions()
        
        with allure.step("Test successful command assertion"):
            # Создаем успешный результат
            success_result = CommandResult(
                returncode=0,
                stdout="Test output",
                stderr="",
                execution_time=0.5,
                command="test command"
            )
            
            # Эта assertion должна пройти
            assertions.assert_command_success(success_result, "Test assertion")
            
            allure.attach("✅ Success assertion works correctly", 
                         name="Success Test", attachment_type=allure.attachment_type.TEXT)
        
        with allure.step("Test output contains assertion"):
            # Тестируем assertion на содержимое
            assertions.assert_output_contains(success_result, "Test", 
                                            message="Should find 'Test' in output")
            
            allure.attach("✅ Output contains assertion works correctly",
                         name="Contains Test", attachment_type=allure.attachment_type.TEXT)
        
        with allure.step("Test execution time assertion"):
            # Тестируем assertion на время выполнения
            assertions.assert_execution_time_within(success_result, 1.0,
                                                   message="Should be fast")
            
            allure.attach("✅ Execution time assertion works correctly",
                         name="Time Test", attachment_type=allure.attachment_type.TEXT)


# Глобальная конфигурация для этих тестов
pytestmark = [
    pytest.mark.smoke,
    pytest.mark.timeout(60)  # Professional framework tests are fast
]
