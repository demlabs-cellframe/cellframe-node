#!/usr/bin/env python3
"""
Test Configuration Module
Централизованная конфигурация для всех тестов
"""

import os
from dataclasses import dataclass
from typing import Dict, List, Optional
from pathlib import Path


@dataclass
class NodeConfig:
    """Конфигурация Cellframe Node"""
    base_dir: str
    bin_dir: str
    log_dir: str
    config_dir: str
    data_dir: str
    
    @property
    def node_binary(self) -> str:
        return f"{self.bin_dir}/cellframe-node"
    
    @property
    def cli_binary(self) -> str:
        return f"{self.bin_dir}/cellframe-node-cli"
    
    @property
    def config_binary(self) -> str:
        return f"{self.bin_dir}/cellframe-node-config"
    
    @property
    def log_file(self) -> str:
        return f"{self.log_dir}/cellframe-node.log"


@dataclass
class NetworkConfig:
    """Конфигурация сетей"""
    backbone: Dict[str, str]
    kelvpn: Dict[str, str]
    test_networks: List[str]


@dataclass
class TestLimits:
    """Лимиты для тестов"""
    max_memory_mb: int
    max_cpu_percent: float
    max_startup_time_sec: int
    max_response_time_sec: int
    max_log_errors: int


@dataclass
class TestConfig:
    """Главная конфигурация тестов"""
    node: NodeConfig
    networks: NetworkConfig
    limits: TestLimits
    environment: str
    debug_mode: bool
    parallel_execution: bool
    retry_count: int
    timeout_sec: int


class ConfigManager:
    """Менеджер конфигурации"""
    
    def __init__(self):
        self._config: Optional[TestConfig] = None
    
    @property
    def config(self) -> TestConfig:
        """Получить конфигурацию (lazy loading)"""
        if self._config is None:
            self._config = self._load_config()
        return self._config
    
    def _load_config(self) -> TestConfig:
        """Загрузить конфигурацию из переменных окружения"""
        
        # Node configuration
        node_base_dir = os.getenv('CELLFRAME_NODE_DIR', '/opt/cellframe-node')
        node_config = NodeConfig(
            base_dir=node_base_dir,
            bin_dir=self._find_bin_directory(),
            log_dir=f"{node_base_dir}/var/log",
            config_dir=f"{node_base_dir}/etc",
            data_dir=f"{node_base_dir}/var/lib"
        )
        
        # Network configuration
        networks_config = NetworkConfig(
            backbone={
                'name': 'Backbone',
                'expected_status': 'NET_STATE_ONLINE',
                'chain': 'main'
            },
            kelvpn={
                'name': 'KelVPN', 
                'expected_status': 'NET_STATE_ONLINE',
                'chain': 'main'
            },
            test_networks=['Backbone', 'KelVPN']
        )
        
        # Test limits
        limits = TestLimits(
            max_memory_mb=int(os.getenv('QA_MAX_MEMORY_MB', '1024')),
            max_cpu_percent=float(os.getenv('QA_MAX_CPU_PERCENT', '50.0')),
            max_startup_time_sec=int(os.getenv('QA_MAX_STARTUP_TIME', '60')),
            max_response_time_sec=int(os.getenv('QA_MAX_RESPONSE_TIME', '30')),
            max_log_errors=int(os.getenv('QA_MAX_LOG_ERRORS', '10'))
        )
        
        return TestConfig(
            node=node_config,
            networks=networks_config,
            limits=limits,
            environment=os.getenv('QA_ENVIRONMENT', 'docker'),
            debug_mode=os.getenv('QA_DEBUG', 'false').lower() == 'true',
            parallel_execution=os.getenv('QA_PARALLEL', 'false').lower() == 'true',
            retry_count=int(os.getenv('QA_RETRY_COUNT', '2')),
            timeout_sec=int(os.getenv('QA_TIMEOUT', '300'))
        )
    
    def _find_bin_directory(self) -> str:
        """Найти директорию с бинарниками"""
        possible_paths = [
            '/opt/cellframe-node/bin',
            '/usr/bin',
            '/usr/local/bin',
            '/bin'
        ]
        
        for path in possible_paths:
            if Path(f"{path}/cellframe-node-cli").exists():
                return path
        
        # Fallback to default
        return '/opt/cellframe-node/bin'
    
    def reload(self):
        """Перезагрузить конфигурацию"""
        self._config = None


# Глобальный экземпляр менеджера конфигурации
config_manager = ConfigManager()


def get_config() -> TestConfig:
    """Получить текущую конфигурацию"""
    return config_manager.config


def reload_config():
    """Перезагрузить конфигурацию"""
    config_manager.reload()
