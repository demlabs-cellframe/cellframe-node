#!/usr/bin/env python3
"""
Node CLI Page Object
Реализация паттерна Page Object для работы с CLI Cellframe Node
"""

import re
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from ..config import get_config
from ..utils import execute_command, CommandResult, RetryConfig, RetryStrategy
from ..assertions import NodeAssertions


@dataclass
class NetworkStatus:
    """Статус сети"""
    name: str
    state: str
    nodes_count: int
    active_links: int
    target_state: str
    is_online: bool
    
    @classmethod
    def from_cli_output(cls, network_name: str, output: str) -> 'NetworkStatus':
        """Создать NetworkStatus из вывода CLI"""
        # Парсинг вывода команды net get status
        state_match = re.search(r'State:\s*(\w+)', output)
        nodes_match = re.search(r'Nodes:\s*(\d+)', output)
        links_match = re.search(r'Active links:\s*(\d+)', output)
        
        state = state_match.group(1) if state_match else "UNKNOWN"
        nodes_count = int(nodes_match.group(1)) if nodes_match else 0
        active_links = int(links_match.group(1)) if links_match else 0
        
        return cls(
            name=network_name,
            state=state,
            nodes_count=nodes_count,
            active_links=active_links,
            target_state="NET_STATE_ONLINE",
            is_online=state == "NET_STATE_ONLINE"
        )


@dataclass
class NodeInfo:
    """Информация о ноде"""
    version: str
    build_date: str
    uptime: str
    pid: Optional[int]
    memory_usage_mb: float
    cpu_usage_percent: float
    
    @classmethod
    def from_system_info(cls, version_output: str, pid: Optional[int] = None) -> 'NodeInfo':
        """Создать NodeInfo из системной информации"""
        # Парсинг версии и build date
        version_match = re.search(r'version\s+([^\s]+)', version_output)
        build_match = re.search(r'build\s+([^\n]+)', version_output)
        
        return cls(
            version=version_match.group(1) if version_match else "unknown",
            build_date=build_match.group(1) if build_match else "unknown",
            uptime="0s",  # Будет обновлено отдельно
            pid=pid,
            memory_usage_mb=0.0,  # Будет обновлено отдельно
            cpu_usage_percent=0.0  # Будет обновлено отдельно
        )


class NodeCLI:
    """Page Object для работы с CLI Cellframe Node"""
    
    def __init__(self):
        self.config = get_config()
        self.assertions = NodeAssertions()
        
        # Конфигурация retry для разных типов команд
        self.quick_retry = RetryConfig(
            strategy=RetryStrategy.FIXED_DELAY,
            max_attempts=2,
            delay_seconds=0.5
        )
        
        self.network_retry = RetryConfig(
            strategy=RetryStrategy.EXPONENTIAL_BACKOFF,
            max_attempts=3,
            delay_seconds=2.0,
            backoff_multiplier=2.0
        )
    
    def get_version(self) -> CommandResult:
        """Получить версию ноды"""
        command = f"{self.config.node.cli_binary} version"
        return execute_command(
            command, 
            timeout=10,
            retry_config=self.quick_retry
        )
    
    def get_node_info(self) -> NodeInfo:
        """Получить полную информацию о ноде"""
        version_result = self.get_version()
        self.assertions.assert_command_success(version_result, "Failed to get node version")
        
        # Получаем PID процесса
        pid_result = execute_command("pgrep -x cellframe-node")
        pid = int(pid_result.stdout.strip()) if pid_result.success else None
        
        return NodeInfo.from_system_info(version_result.stdout, pid)
    
    def get_network_status(self, network_name: str) -> NetworkStatus:
        """Получить статус сети"""
        command = f"{self.config.node.cli_binary} net -net {network_name} get status"
        result = execute_command(
            command,
            timeout=30,
            retry_config=self.network_retry
        )
        
        self.assertions.assert_command_success(
            result, 
            f"Failed to get status for network {network_name}"
        )
        
        return NetworkStatus.from_cli_output(network_name, result.stdout)
    
    def get_all_networks_status(self) -> Dict[str, NetworkStatus]:
        """Получить статус всех сетей"""
        networks_status = {}
        
        for network_name in self.config.networks.test_networks:
            try:
                status = self.get_network_status(network_name)
                networks_status[network_name] = status
            except Exception as e:
                # Логируем ошибку, но продолжаем для других сетей
                print(f"Warning: Failed to get status for network {network_name}: {e}")
        
        return networks_status
    
    def wait_for_network_online(self, network_name: str, 
                               timeout_sec: int = 60) -> NetworkStatus:
        """Ждать пока сеть не станет онлайн"""
        import time
        
        start_time = time.time()
        last_status = None
        
        while time.time() - start_time < timeout_sec:
            try:
                status = self.get_network_status(network_name)
                last_status = status
                
                if status.is_online:
                    return status
                
                print(f"Network {network_name} is {status.state}, waiting...")
                time.sleep(5)
                
            except Exception as e:
                print(f"Error checking network {network_name}: {e}")
                time.sleep(5)
        
        # Таймаут достигнут
        if last_status:
            raise TimeoutError(
                f"Network {network_name} did not come online within {timeout_sec}s. "
                f"Last status: {last_status.state}"
            )
        else:
            raise TimeoutError(
                f"Failed to check network {network_name} status within {timeout_sec}s"
            )
    
    def is_node_running(self) -> bool:
        """Проверить запущена ли нода"""
        result = execute_command("pgrep -x cellframe-node")
        return result.success and result.stdout.strip()
    
    def get_node_pid(self) -> Optional[int]:
        """Получить PID процесса ноды"""
        result = execute_command("pgrep -x cellframe-node")
        if result.success and result.stdout.strip():
            return int(result.stdout.strip())
        return None
    
    def get_memory_usage(self, pid: Optional[int] = None) -> float:
        """Получить использование памяти в MB"""
        if pid is None:
            pid = self.get_node_pid()
        
        if pid is None:
            raise RuntimeError("Node is not running")
        
        # Получаем RSS память в KB, конвертируем в MB
        result = execute_command(f"ps -p {pid} -o rss= | tr -d ' '")
        if result.success and result.stdout.strip():
            rss_kb = int(result.stdout.strip())
            return rss_kb / 1024.0  # Конвертируем KB в MB
        
        raise RuntimeError(f"Failed to get memory usage for PID {pid}")
    
    def get_cpu_usage(self, pid: Optional[int] = None, 
                     measurement_duration: int = 5) -> float:
        """Получить использование CPU в процентах"""
        if pid is None:
            pid = self.get_node_pid()
        
        if pid is None:
            raise RuntimeError("Node is not running")
        
        # Используем top для получения CPU usage
        command = f"top -p {pid} -b -n 2 -d {measurement_duration} | tail -1 | awk '{{print $9}}'"
        result = execute_command(command, timeout=measurement_duration + 10)
        
        if result.success and result.stdout.strip():
            try:
                return float(result.stdout.strip())
            except ValueError:
                pass
        
        # Fallback: используем ps
        result = execute_command(f"ps -p {pid} -o %cpu= | tr -d ' '")
        if result.success and result.stdout.strip():
            try:
                return float(result.stdout.strip())
            except ValueError:
                pass
        
        raise RuntimeError(f"Failed to get CPU usage for PID {pid}")
    
    def execute_custom_command(self, cli_args: str, 
                              timeout: int = 30) -> CommandResult:
        """Выполнить произвольную CLI команду"""
        command = f"{self.config.node.cli_binary} {cli_args}"
        return execute_command(command, timeout=timeout)
    
    def validate_node_health(self) -> Dict[str, Any]:
        """Комплексная проверка здоровья ноды"""
        health_report = {
            'node_running': False,
            'version_accessible': False,
            'networks_online': {},
            'resource_usage': {},
            'overall_healthy': False
        }
        
        try:
            # Проверяем что нода запущена
            health_report['node_running'] = self.is_node_running()
            
            if health_report['node_running']:
                # Проверяем доступность версии
                version_result = self.get_version()
                health_report['version_accessible'] = version_result.success
                
                # Проверяем статус сетей
                networks_status = self.get_all_networks_status()
                health_report['networks_online'] = {
                    name: status.is_online 
                    for name, status in networks_status.items()
                }
                
                # Проверяем использование ресурсов
                try:
                    pid = self.get_node_pid()
                    if pid:
                        health_report['resource_usage'] = {
                            'memory_mb': self.get_memory_usage(pid),
                            'cpu_percent': self.get_cpu_usage(pid, 2)  # Быстрое измерение
                        }
                except Exception as e:
                    health_report['resource_usage'] = {'error': str(e)}
            
            # Определяем общее здоровье
            health_report['overall_healthy'] = (
                health_report['node_running'] and
                health_report['version_accessible'] and
                any(health_report['networks_online'].values())
            )
            
        except Exception as e:
            health_report['error'] = str(e)
        
        return health_report
