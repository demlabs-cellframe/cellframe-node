#!/usr/bin/env python3
"""
Smoke Tests - Node Basic Functionality
Быстрые тесты основной функциональности ноды
"""

import pytest
import allure
from framework import NodeCLI, NodeAssertions


@allure.epic("Cellframe Node")
@allure.feature("Basic Functionality")
@pytest.mark.smoke
@pytest.mark.critical
class TestNodeBasic:
    """Базовые smoke тесты ноды"""
    
    @allure.story("Node Status")
    @allure.title("Node is running and accessible")
    @allure.description("Проверяет что нода запущена и отвечает на команды")
    def test_node_is_running(self, node_cli: NodeCLI, ensure_node_running):
        """Тест: нода запущена и доступна"""
        
        with allure.step("Check if node process is running"):
            assert node_cli.is_node_running(), "Node process is not running"
        
        with allure.step("Get node PID"):
            pid = node_cli.get_node_pid()
            assert pid is not None, "Cannot get node PID"
            assert pid > 0, f"Invalid PID: {pid}"
            
            allure.attach(str(pid), name="Node PID", attachment_type=allure.attachment_type.TEXT)
    
    @allure.story("Version Information")
    @allure.title("Node version is accessible and valid")
    @allure.description("Проверяет что можно получить версию ноды и она валидна")
    def test_node_version_accessible(self, node_cli: NodeCLI, node_assertions: NodeAssertions, 
                                   ensure_node_running):
        """Тест: версия ноды доступна и валидна"""
        
        with allure.step("Execute version command"):
            result = node_cli.get_version()
            
            allure.attach(result.stdout, name="Version Output", 
                         attachment_type=allure.attachment_type.TEXT)
            allure.attach(f"Execution time: {result.execution_time:.2f}s", 
                         name="Performance", attachment_type=allure.attachment_type.TEXT)
        
        with allure.step("Validate command execution"):
            node_assertions.assert_command_success(result, "Failed to get node version")
            node_assertions.assert_execution_time_within(result, 10.0, "Version command too slow")
        
        with allure.step("Validate version format"):
            node_assertions.assert_node_version_valid(result.stdout, "Invalid version format")
            node_assertions.assert_output_contains(result, "cellframe-node", 
                                                 message="Version output missing node name")
    
    @allure.story("Node Health")
    @allure.title("Node health check passes")
    @allure.description("Комплексная проверка здоровья ноды")
    def test_node_health_check(self, node_cli: NodeCLI, node_assertions: NodeAssertions,
                             ensure_node_running):
        """Тест: комплексная проверка здоровья ноды"""
        
        with allure.step("Perform comprehensive health check"):
            health_report = node_cli.validate_node_health()
            
            allure.attach(str(health_report), name="Health Report", 
                         attachment_type=allure.attachment_type.JSON)
        
        with allure.step("Validate overall health"):
            node_assertions.assert_node_health_good(health_report, "Node health check failed")
        
        with allure.step("Validate individual components"):
            assert health_report['node_running'], "Node should be running"
            assert health_report['version_accessible'], "Version should be accessible"
            
            # Проверяем что хотя бы одна сеть онлайн
            networks_online = health_report.get('networks_online', {})
            online_count = sum(1 for online in networks_online.values() if online)
            assert online_count > 0, f"No networks online: {networks_online}"


@allure.epic("Cellframe Node")
@allure.feature("CLI Interface")
@pytest.mark.smoke
@pytest.mark.cli
class TestNodeCLI:
    """Smoke тесты CLI интерфейса"""
    
    @allure.story("CLI Responsiveness")
    @allure.title("CLI commands respond within acceptable time")
    @allure.description("Проверяет что CLI команды отвечают быстро")
    def test_cli_responsiveness(self, node_cli: NodeCLI, node_assertions: NodeAssertions,
                              ensure_node_running):
        """Тест: CLI команды отвечают быстро"""
        
        quick_commands = [
            ("version", "Get version"),
            ("help", "Get help")
        ]
        
        for cmd_args, description in quick_commands:
            with allure.step(f"Execute quick command: {description}"):
                result = node_cli.execute_custom_command(cmd_args, timeout=5)
                
                allure.attach(f"Command: {cmd_args}\nTime: {result.execution_time:.2f}s", 
                             name=f"Command Performance - {description}", 
                             attachment_type=allure.attachment_type.TEXT)
                
                node_assertions.assert_command_success(result, f"Command failed: {cmd_args}")
                node_assertions.assert_execution_time_within(result, 3.0, 
                                                           f"Command too slow: {cmd_args}")
    
    @allure.story("Error Handling")
    @allure.title("CLI handles invalid commands gracefully")
    @allure.description("Проверяет что CLI корректно обрабатывает неверные команды")
    def test_cli_error_handling(self, node_cli: NodeCLI, node_assertions: NodeAssertions,
                              ensure_node_running):
        """Тест: CLI корректно обрабатывает ошибки"""
        
        invalid_commands = [
            "invalid_command_xyz",
            "net -net NonExistentNetwork get status"
        ]
        
        for invalid_cmd in invalid_commands:
            with allure.step(f"Execute invalid command: {invalid_cmd}"):
                result = node_cli.execute_custom_command(invalid_cmd, timeout=10)
                
                allure.attach(f"Command: {invalid_cmd}\nReturn code: {result.returncode}\n"
                             f"Stderr: {result.stderr}", 
                             name=f"Invalid Command Result", 
                             attachment_type=allure.attachment_type.TEXT)
                
                # Команда должна провалиться, но не зависнуть
                node_assertions.assert_command_failure(result, 
                                                     message=f"Invalid command should fail: {invalid_cmd}")
                node_assertions.assert_execution_time_within(result, 10.0, 
                                                           f"Invalid command took too long: {invalid_cmd}")


# Конфигурация для smoke тестов
pytestmark = [
    pytest.mark.smoke,
    pytest.mark.timeout(60)  # Smoke тесты должны быть быстрыми
]
