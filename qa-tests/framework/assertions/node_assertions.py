#!/usr/bin/env python3
"""
Node Assertions
Кастомные assertion методы для тестирования Cellframe Node
"""

import re
from typing import List, Optional, Dict, Any, Union
from ..utils import CommandResult
from ..config import get_config


class NodeAssertions:
    """Кастомные assertions для тестирования ноды"""
    
    def __init__(self):
        self.config = get_config()
    
    def assert_command_success(self, result: CommandResult, 
                             message: Optional[str] = None):
        """Проверить что команда выполнена успешно"""
        if not result.success:
            error_msg = message or f"Command failed: {result.command}"
            error_msg += f"\nReturn code: {result.returncode}"
            error_msg += f"\nStdout: {result.stdout}"
            error_msg += f"\nStderr: {result.stderr}"
            raise AssertionError(error_msg)
    
    def assert_command_failure(self, result: CommandResult,
                             expected_code: Optional[int] = None,
                             message: Optional[str] = None):
        """Проверить что команда провалилась с ожидаемым кодом"""
        if result.success:
            error_msg = message or f"Expected command to fail, but it succeeded: {result.command}"
            error_msg += f"\nStdout: {result.stdout}"
            raise AssertionError(error_msg)
        
        if expected_code is not None and result.returncode != expected_code:
            error_msg = message or f"Expected return code {expected_code}, got {result.returncode}"
            error_msg += f"\nCommand: {result.command}"
            error_msg += f"\nStderr: {result.stderr}"
            raise AssertionError(error_msg)
    
    def assert_output_contains(self, result: CommandResult, 
                             expected_texts: Union[str, List[str]],
                             case_sensitive: bool = True,
                             message: Optional[str] = None):
        """Проверить что вывод содержит ожидаемый текст"""
        if isinstance(expected_texts, str):
            expected_texts = [expected_texts]
        
        output = result.stdout
        if not case_sensitive:
            output = output.lower()
            expected_texts = [text.lower() for text in expected_texts]
        
        for expected_text in expected_texts:
            if expected_text not in output:
                error_msg = message or f"Expected text '{expected_text}' not found in output"
                error_msg += f"\nCommand: {result.command}"
                error_msg += f"\nActual output: {result.stdout}"
                raise AssertionError(error_msg)
    
    def assert_output_not_contains(self, result: CommandResult,
                                 forbidden_texts: Union[str, List[str]],
                                 case_sensitive: bool = True,
                                 message: Optional[str] = None):
        """Проверить что вывод НЕ содержит запрещенный текст"""
        if isinstance(forbidden_texts, str):
            forbidden_texts = [forbidden_texts]
        
        output = result.stdout
        if not case_sensitive:
            output = output.lower()
            forbidden_texts = [text.lower() for text in forbidden_texts]
        
        for forbidden_text in forbidden_texts:
            if forbidden_text in output:
                error_msg = message or f"Forbidden text '{forbidden_text}' found in output"
                error_msg += f"\nCommand: {result.command}"
                error_msg += f"\nActual output: {result.stdout}"
                raise AssertionError(error_msg)
    
    def assert_output_matches_regex(self, result: CommandResult,
                                  pattern: str,
                                  message: Optional[str] = None):
        """Проверить что вывод соответствует регулярному выражению"""
        if not re.search(pattern, result.stdout, re.MULTILINE):
            error_msg = message or f"Output does not match pattern '{pattern}'"
            error_msg += f"\nCommand: {result.command}"
            error_msg += f"\nActual output: {result.stdout}"
            raise AssertionError(error_msg)
    
    def assert_execution_time_within(self, result: CommandResult,
                                   max_seconds: float,
                                   message: Optional[str] = None):
        """Проверить что команда выполнилась за разумное время"""
        if result.execution_time > max_seconds:
            error_msg = message or f"Command took too long: {result.execution_time:.2f}s > {max_seconds}s"
            error_msg += f"\nCommand: {result.command}"
            raise AssertionError(error_msg)
    
    def assert_network_online(self, network_status, 
                            message: Optional[str] = None):
        """Проверить что сеть онлайн"""
        if not network_status.is_online:
            error_msg = message or f"Network {network_status.name} is not online"
            error_msg += f"\nActual state: {network_status.state}"
            error_msg += f"\nExpected state: {network_status.target_state}"
            raise AssertionError(error_msg)
    
    def assert_network_has_nodes(self, network_status,
                               min_nodes: int = 1,
                               message: Optional[str] = None):
        """Проверить что в сети есть достаточно нод"""
        if network_status.nodes_count < min_nodes:
            error_msg = message or f"Network {network_status.name} has insufficient nodes"
            error_msg += f"\nActual nodes: {network_status.nodes_count}"
            error_msg += f"\nMinimum required: {min_nodes}"
            raise AssertionError(error_msg)
    
    def assert_memory_usage_within_limit(self, memory_mb: float,
                                       max_memory_mb: Optional[float] = None,
                                       message: Optional[str] = None):
        """Проверить что использование памяти в пределах нормы"""
        max_memory_mb = max_memory_mb or self.config.limits.max_memory_mb
        
        if memory_mb > max_memory_mb:
            error_msg = message or f"Memory usage exceeds limit"
            error_msg += f"\nActual memory: {memory_mb:.1f} MB"
            error_msg += f"\nLimit: {max_memory_mb} MB"
            raise AssertionError(error_msg)
    
    def assert_cpu_usage_within_limit(self, cpu_percent: float,
                                    max_cpu_percent: Optional[float] = None,
                                    message: Optional[str] = None):
        """Проверить что использование CPU в пределах нормы"""
        max_cpu_percent = max_cpu_percent or self.config.limits.max_cpu_percent
        
        if cpu_percent > max_cpu_percent:
            error_msg = message or f"CPU usage exceeds limit"
            error_msg += f"\nActual CPU: {cpu_percent:.1f}%"
            error_msg += f"\nLimit: {max_cpu_percent}%"
            raise AssertionError(error_msg)
    
    def assert_node_version_valid(self, version_output: str,
                                message: Optional[str] = None):
        """Проверить что версия ноды валидна"""
        # Ожидаем формат типа "cellframe-node version 5.2-123"
        version_pattern = r'cellframe-node\s+version\s+[\d\.]+-?\d*'
        
        if not re.search(version_pattern, version_output, re.IGNORECASE):
            error_msg = message or "Invalid node version format"
            error_msg += f"\nActual output: {version_output}"
            error_msg += f"\nExpected pattern: {version_pattern}"
            raise AssertionError(error_msg)
    
    def assert_log_errors_within_limit(self, error_count: int,
                                     max_errors: Optional[int] = None,
                                     message: Optional[str] = None):
        """Проверить что количество ошибок в логах в пределах нормы"""
        max_errors = max_errors or self.config.limits.max_log_errors
        
        if error_count > max_errors:
            error_msg = message or f"Too many errors in logs"
            error_msg += f"\nActual errors: {error_count}"
            error_msg += f"\nLimit: {max_errors}"
            raise AssertionError(error_msg)
    
    def assert_node_health_good(self, health_report: Dict[str, Any],
                              message: Optional[str] = None):
        """Проверить что общее здоровье ноды хорошее"""
        if not health_report.get('overall_healthy', False):
            error_msg = message or "Node health check failed"
            error_msg += f"\nHealth report: {health_report}"
            
            # Добавляем детали о проблемах
            issues = []
            if not health_report.get('node_running', False):
                issues.append("Node is not running")
            if not health_report.get('version_accessible', False):
                issues.append("Version is not accessible")
            
            networks_online = health_report.get('networks_online', {})
            offline_networks = [name for name, online in networks_online.items() if not online]
            if offline_networks:
                issues.append(f"Networks offline: {', '.join(offline_networks)}")
            
            if issues:
                error_msg += f"\nIssues found: {'; '.join(issues)}"
            
            raise AssertionError(error_msg)
    
    def assert_response_time_acceptable(self, response_time: float,
                                      max_response_time: Optional[float] = None,
                                      message: Optional[str] = None):
        """Проверить что время отклика приемлемо"""
        max_response_time = max_response_time or self.config.limits.max_response_time_sec
        
        if response_time > max_response_time:
            error_msg = message or f"Response time too slow"
            error_msg += f"\nActual time: {response_time:.2f}s"
            error_msg += f"\nLimit: {max_response_time}s"
            raise AssertionError(error_msg)
