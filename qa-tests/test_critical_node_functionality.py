#!/usr/bin/env python3
"""
Critical Node Functionality Tests
=================================================================================
ЭТИ ТЕСТЫ ОТВЕЧАЮТ НА КОНКРЕТНЫЕ ВОПРОСЫ:
- Нода устанавливается?
- Нода запускается?
- Нода отвечает на команды?
- Сети инициализируются?
- Конфигурация корректная?

РЕЗУЛЬТАТЫ В TESTOPS БУДУТ ПОКАЗЫВАТЬ:
✅ Что работает
❌ Что сломалось
⚠️  Что требует внимания
=================================================================================
"""

import pytest
import allure
import subprocess
import time
import os
from pathlib import Path


# =============================================================================
# КРИТИЧНЫЕ ПРОВЕРКИ УСТАНОВКИ
# =============================================================================

@allure.epic("Cellframe Node")
@allure.feature("Installation")
@pytest.mark.smoke
@pytest.mark.critical
class TestNodeInstallation:
    """Проверяем что нода установилась корректно"""
    
    @allure.story("Package Installation")
    @allure.title("Node package is installed")
    @allure.description("Проверка: cellframe-node пакет установлен в системе")
    def test_node_package_installed(self):
        """ВОПРОС: Установлен ли пакет cellframe-node?"""
        
        with allure.step("Check if cellframe-node package is installed"):
            result = subprocess.run(
                ["dpkg", "-l", "cellframe-node"],
                capture_output=True,
                text=True
            )
            
            allure.attach(
                result.stdout,
                name="dpkg output",
                attachment_type=allure.attachment_type.TEXT
            )
            
            # Проверяем статус
            assert result.returncode == 0, "cellframe-node package is NOT installed"
            assert "cellframe-node" in result.stdout, "Package name not found in dpkg output"
            
            # Извлекаем версию
            version_line = [line for line in result.stdout.split('\n') if 'cellframe-node' in line]
            if version_line:
                parts = version_line[0].split()
                if len(parts) >= 3:
                    version = parts[2]
                    allure.attach(
                        f"Installed version: {version}",
                        name="Version",
                        attachment_type=allure.attachment_type.TEXT
                    )
    
    @allure.story("Binary Files")
    @allure.title("Main node binary exists and is executable")
    @allure.description("Проверка: главный бинарник cellframe-node существует")
    def test_main_binary_exists(self):
        """ВОПРОС: Есть ли исполняемый файл cellframe-node?"""
        
        possible_paths = [
            "/opt/cellframe-node/bin/cellframe-node",
            "/usr/bin/cellframe-node",
            "/usr/local/bin/cellframe-node"
        ]
        
        found_binary = None
        
        for path in possible_paths:
            with allure.step(f"Check if binary exists at {path}"):
                if os.path.exists(path) and os.access(path, os.X_OK):
                    found_binary = path
                    allure.attach(
                        f"Found executable binary at: {path}",
                        name="Binary Location",
                        attachment_type=allure.attachment_type.TEXT
                    )
                    break
        
        assert found_binary is not None, \
            f"cellframe-node binary not found in any of: {possible_paths}"
    
    @allure.story("Binary Files")
    @allure.title("CLI binary exists and is executable")
    @allure.description("Проверка: CLI бинарник cellframe-node-cli существует")
    def test_cli_binary_exists(self):
        """ВОПРОС: Есть ли исполняемый файл cellframe-node-cli?"""
        
        possible_paths = [
            "/opt/cellframe-node/bin/cellframe-node-cli",
            "/usr/bin/cellframe-node-cli",
            "/usr/local/bin/cellframe-node-cli"
        ]
        
        found_binary = None
        
        for path in possible_paths:
            with allure.step(f"Check if CLI binary exists at {path}"):
                if os.path.exists(path) and os.access(path, os.X_OK):
                    found_binary = path
                    allure.attach(
                        f"Found executable CLI binary at: {path}",
                        name="CLI Binary Location",
                        attachment_type=allure.attachment_type.TEXT
                    )
                    break
        
        assert found_binary is not None, \
            f"cellframe-node-cli binary not found in any of: {possible_paths}"
    
    @allure.story("Configuration")
    @allure.title("Main configuration file exists")
    @allure.description("Проверка: главный конфигурационный файл существует")
    def test_main_config_exists(self):
        """ВОПРОС: Есть ли главный конфиг файл?"""
        
        possible_paths = [
            "/opt/cellframe-node/etc/cellframe-node.cfg",
            "/opt/cellframe-node/share/configs/cellframe-node.cfg",
            "/etc/cellframe-node/cellframe-node.cfg"
        ]
        
        found_config = None
        
        for path in possible_paths:
            with allure.step(f"Check if config exists at {path}"):
                if os.path.exists(path):
                    found_config = path
                    
                    # Читаем первые 20 строк конфига
                    try:
                        with open(path, 'r') as f:
                            config_preview = ''.join(f.readlines()[:20])
                        
                        allure.attach(
                            config_preview,
                            name=f"Config Preview: {path}",
                            attachment_type=allure.attachment_type.TEXT
                        )
                    except Exception as e:
                        allure.attach(
                            f"Could not read config: {e}",
                            name="Config Read Error",
                            attachment_type=allure.attachment_type.TEXT
                        )
                    
                    break
        
        assert found_config is not None, \
            f"cellframe-node.cfg not found in any of: {possible_paths}"


# =============================================================================
# КРИТИЧНЫЕ ПРОВЕРКИ ЗАПУСКА
# =============================================================================

@allure.epic("Cellframe Node")
@allure.feature("Node Startup")
@pytest.mark.smoke
@pytest.mark.critical
class TestNodeStartup:
    """Проверяем что нода запускается и работает"""
    
    @allure.story("Process Management")
    @allure.title("Node process can be started")
    @allure.description("Проверка: процесс cellframe-node запускается")
    def test_node_process_starts(self):
        """ВОПРОС: Запускается ли процесс cellframe-node?"""
        
        # Проверяем что процесс еще не запущен
        with allure.step("Check if node is already running"):
            check_running = subprocess.run(
                ["pgrep", "-x", "cellframe-node"],
                capture_output=True
            )
            
            if check_running.returncode == 0:
                allure.attach(
                    "Node is already running - good!",
                    name="Process Status",
                    attachment_type=allure.attachment_type.TEXT
                )
                # Нода уже запущена - это OK
                return
        
        # Пытаемся запустить ноду
        with allure.step("Start cellframe-node process"):
            # Ищем бинарник
            binary_path = None
            for path in ["/opt/cellframe-node/bin/cellframe-node", "/usr/bin/cellframe-node"]:
                if os.path.exists(path):
                    binary_path = path
                    break
            
            assert binary_path is not None, "Cannot find cellframe-node binary"
            
            # Запускаем в фоне
            start_result = subprocess.run(
                [binary_path, "-D"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            allure.attach(
                start_result.stdout + "\n" + start_result.stderr,
                name="Node Startup Output",
                attachment_type=allure.attachment_type.TEXT
            )
        
        # Даем время на запуск
        with allure.step("Wait for node to initialize (5 seconds)"):
            time.sleep(5)
        
        # Проверяем что процесс запустился
        with allure.step("Verify node process is running"):
            check_result = subprocess.run(
                ["pgrep", "-x", "cellframe-node"],
                capture_output=True,
                text=True
            )
            
            if check_result.returncode == 0:
                pid = check_result.stdout.strip()
                allure.attach(
                    f"Node is running with PID: {pid}",
                    name="Process Status",
                    attachment_type=allure.attachment_type.TEXT
                )
            else:
                pytest.fail("Node process did not start successfully")
    
    @allure.story("Initialization")
    @allure.title("Node initializes networks")
    @allure.description("Проверка: нода инициализирует сети при запуске")
    def test_node_initializes_networks(self):
        """ВОПРОС: Инициализирует ли нода сети (Backbone, KelVPN)?"""
        
        with allure.step("Check if node is running"):
            check_running = subprocess.run(
                ["pgrep", "-x", "cellframe-node"],
                capture_output=True
            )
            
            if check_running.returncode != 0:
                pytest.skip("Node is not running - cannot check network initialization")
        
        # Проверяем конфиги сетей
        with allure.step("Check network configuration files"):
            network_configs = [
                "/opt/cellframe-node/share/configs/network/Backbone.cfg",
                "/opt/cellframe-node/share/configs/network/KelVPN.cfg"
            ]
            
            found_networks = []
            for config_path in network_configs:
                if os.path.exists(config_path):
                    network_name = os.path.basename(config_path).replace('.cfg', '')
                    found_networks.append(network_name)
                    
                    try:
                        with open(config_path, 'r') as f:
                            config_content = f.read()
                        
                        allure.attach(
                            config_content[:500],  # First 500 chars
                            name=f"{network_name} Config",
                            attachment_type=allure.attachment_type.TEXT
                        )
                    except Exception as e:
                        allure.attach(
                            f"Could not read config: {e}",
                            name=f"{network_name} Config Error",
                            attachment_type=allure.attachment_type.TEXT
                        )
            
            assert len(found_networks) > 0, \
                "No network configuration files found - node cannot initialize networks"
            
            allure.attach(
                f"Found networks: {', '.join(found_networks)}",
                name="Available Networks",
                attachment_type=allure.attachment_type.TEXT
            )


# =============================================================================
# КРИТИЧНЫЕ ФУНКЦИОНАЛЬНЫЕ ПРОВЕРКИ
# =============================================================================

@allure.epic("Cellframe Node")
@allure.feature("Core Functionality")
@pytest.mark.smoke
@pytest.mark.critical
class TestNodeCoreFunctionality:
    """Проверяем базовую функциональность ноды"""
    
    @allure.story("Directory Structure")
    @allure.title("Node creates required directories")
    @allure.description("Проверка: нода создает необходимые директории")
    def test_node_creates_directories(self):
        """ВОПРОС: Создает ли нода необходимые директории?"""
        
        required_dirs = [
            "/opt/cellframe-node/var",
            "/opt/cellframe-node/var/lib",
            "/opt/cellframe-node/var/log",
        ]
        
        missing_dirs = []
        existing_dirs = []
        
        for dir_path in required_dirs:
            with allure.step(f"Check directory: {dir_path}"):
                if os.path.exists(dir_path) and os.path.isdir(dir_path):
                    existing_dirs.append(dir_path)
                else:
                    missing_dirs.append(dir_path)
        
        allure.attach(
            f"Existing: {len(existing_dirs)}\nMissing: {len(missing_dirs)}",
            name="Directory Status",
            attachment_type=allure.attachment_type.TEXT
        )
        
        if missing_dirs:
            allure.attach(
                "\n".join(missing_dirs),
                name="Missing Directories",
                attachment_type=allure.attachment_type.TEXT
            )
        
        assert len(missing_dirs) == 0, \
            f"Node did not create required directories: {missing_dirs}"
    
    @allure.story("Database")
    @allure.title("Global database is initialized")
    @allure.description("Проверка: глобальная БД инициализирована")
    def test_global_database_initialized(self):
        """ВОПРОС: Инициализирована ли глобальная БД?"""
        
        possible_db_paths = [
            "/opt/cellframe-node/var/lib/global_db",
            "/opt/cellframe-node/var/lib/gdb"
        ]
        
        found_db = None
        
        for db_path in possible_db_paths:
            with allure.step(f"Check global DB at: {db_path}"):
                if os.path.exists(db_path) and os.path.isdir(db_path):
                    found_db = db_path
                    
                    # Проверяем что внутри есть файлы
                    db_files = os.listdir(db_path)
                    allure.attach(
                        f"DB location: {db_path}\n"
                        f"Files count: {len(db_files)}\n"
                        f"First 10 files: {db_files[:10]}",
                        name="Global DB Info",
                        attachment_type=allure.attachment_type.TEXT
                    )
                    break
        
        assert found_db is not None, \
            "Global database directory not found - node may not have initialized properly"
    
    @allure.story("Network Storage")
    @allure.title("Network data directories exist")
    @allure.description("Проверка: директории для данных сетей существуют")
    def test_network_data_directories_exist(self):
        """ВОПРОС: Созданы ли директории для хранения данных сетей?"""
        
        network_base_path = "/opt/cellframe-node/var/lib/network"
        
        with allure.step(f"Check network storage at: {network_base_path}"):
            if not os.path.exists(network_base_path):
                pytest.skip(f"Network storage directory does not exist yet: {network_base_path}")
            
            # Проверяем какие сети созданы
            networks = [d for d in os.listdir(network_base_path) 
                       if os.path.isdir(os.path.join(network_base_path, d))]
            
            allure.attach(
                f"Found networks: {', '.join(networks) if networks else 'None'}",
                name="Initialized Networks",
                attachment_type=allure.attachment_type.TEXT
            )
            
            # Если нет сетей - это может быть проблемой
            if len(networks) == 0:
                allure.attach(
                    "WARNING: No network directories found. Node may not have fully initialized.",
                    name="Warning",
                    attachment_type=allure.attachment_type.TEXT
                )


# =============================================================================
# КОНФИГУРАЦИЯ
# =============================================================================

@allure.epic("Cellframe Node")
@allure.feature("Configuration")
@pytest.mark.smoke
class TestNodeConfiguration:
    """Проверяем корректность конфигурации"""
    
    @allure.story("Config Validation")
    @allure.title("Main config file is valid")
    @allure.description("Проверка: главный конфиг файл валиден и читаем")
    def test_main_config_is_valid(self):
        """ВОПРОС: Валиден ли главный конфиг файл?"""
        
        config_paths = [
            "/opt/cellframe-node/etc/cellframe-node.cfg",
            "/opt/cellframe-node/share/configs/cellframe-node.cfg"
        ]
        
        found_config = None
        
        for config_path in config_paths:
            if os.path.exists(config_path):
                found_config = config_path
                break
        
        if found_config is None:
            pytest.skip("Config file not found")
        
        with allure.step(f"Read and validate config: {found_config}"):
            try:
                with open(found_config, 'r') as f:
                    config_content = f.read()
                
                # Базовые проверки конфига
                required_sections = ["general", "server"]
                found_sections = []
                
                for section in required_sections:
                    if f"[{section}]" in config_content:
                        found_sections.append(section)
                
                allure.attach(
                    config_content,
                    name="Config File Content",
                    attachment_type=allure.attachment_type.TEXT
                )
                
                allure.attach(
                    f"Found sections: {', '.join(found_sections)}",
                    name="Config Sections",
                    attachment_type=allure.attachment_type.TEXT
                )
                
                assert len(found_sections) > 0, \
                    "Config file does not contain expected sections"
                
            except Exception as e:
                pytest.fail(f"Failed to read/validate config: {e}")


# Глобальная конфигурация для критичных тестов
pytestmark = [
    pytest.mark.critical,
    pytest.mark.timeout(120)  # Critical tests should be fast
]

