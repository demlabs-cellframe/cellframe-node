#!/usr/bin/env python3
"""
Cellframe Node QA Test Suite - ИСПРАВЛЕННАЯ ВЕРСИЯ v2
Устранены критические проблемы с ложными срабатываниями
ИСПРАВЛЕНИЕ v2: Автоматический поиск путей к бинарникам
"""

import subprocess
import time
import os
import pytest
import allure
from pathlib import Path


def find_cellframe_binaries():
    """Автоматический поиск путей к бинарникам Cellframe Node"""
    possible_paths = [
        '/opt/cellframe-node/bin',
        '/usr/bin',
        '/usr/local/bin',
        '/bin',
        '/sbin',
        '/usr/sbin'
    ]
    
    binaries = {
        'node': None,
        'cli': None,
        'config': None
    }
    
    # Поиск бинарников в возможных путях
    for path in possible_paths:
        if os.path.exists(f"{path}/cellframe-node"):
            binaries['node'] = f"{path}/cellframe-node"
        if os.path.exists(f"{path}/cellframe-node-cli"):
            binaries['cli'] = f"{path}/cellframe-node-cli"
        if os.path.exists(f"{path}/cellframe-node-config"):
            binaries['config'] = f"{path}/cellframe-node-config"
    
    # Дополнительный поиск через which
    if not binaries['cli']:
        try:
            result = subprocess.run(['which', 'cellframe-node-cli'], capture_output=True, text=True)
            if result.returncode == 0:
                binaries['cli'] = result.stdout.strip()
        except:
            pass
    
    if not binaries['node']:
        try:
            result = subprocess.run(['which', 'cellframe-node'], capture_output=True, text=True)
            if result.returncode == 0:
                binaries['node'] = result.stdout.strip()
        except:
            pass
            
    return binaries


# ИСПРАВЛЕНИЕ 1: Конфигурируемые пути с автопоиском
NODE_DIR = os.environ.get('CELLFRAME_NODE_DIR', '/opt/cellframe-node')

# Автоматический поиск бинарников
BINARIES = find_cellframe_binaries()
NODE_BIN = BINARIES['node'] or f"{NODE_DIR}/bin/cellframe-node"
CLI_BIN = BINARIES['cli'] or f"{NODE_DIR}/bin/cellframe-node-cli"  
CONFIG_BIN = BINARIES['config'] or f"{NODE_DIR}/bin/cellframe-node-config"
LOG_FILE = f"{NODE_DIR}/var/log/cellframe-node.log"

# Отладочная информация
print(f"🔍 DEBUGGING: Found binaries:")
print(f"   NODE_BIN: {NODE_BIN} (exists: {os.path.exists(NODE_BIN)})")
print(f"   CLI_BIN: {CLI_BIN} (exists: {os.path.exists(CLI_BIN)})")
print(f"   CONFIG_BIN: {CONFIG_BIN} (exists: {os.path.exists(CONFIG_BIN)})")
print(f"   LOG_FILE: {LOG_FILE}")


def run_command(cmd, timeout=30):
    """Execute shell command and return result"""
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            capture_output=True, 
            text=True, 
            timeout=timeout
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "Command timeout"
    except Exception as e:
        return -1, "", str(e)


def get_system_memory_gb():
    """Get total system memory in GB"""
    try:
        with open('/proc/meminfo', 'r') as f:
            for line in f:
                if line.startswith('MemTotal:'):
                    kb = int(line.split()[1])
                    return kb // (1024 * 1024)
    except:
        return 8  # Default fallback


def wait_for_condition(check_func, timeout=60, interval=1):
    """ИСПРАВЛЕНИЕ 2: Активное ожидание вместо sleep"""
    for i in range(timeout):
        if check_func():
            return True
        time.sleep(interval)
    return False


def check_network_ready(network):
    """Проверка готовности сети"""
    code, stdout, stderr = run_command(f"{CLI_BIN} net -net {network} get status")
    if code != 0:
        return False
    
    # Проверяем что нет ошибок в выводе
    stdout_lower = stdout.lower()
    if any(error in stdout_lower for error in ['error', 'failed', 'timeout', 'unreachable']):
        return False
        
    return f"net: {network}" in stdout


@allure.feature("Network Status")
@allure.story("Network Connectivity")
@allure.severity(allure.severity_level.CRITICAL)
class TestNetworkStatusFixed:
    """ИСПРАВЛЕННЫЕ тесты сети - устранены ложные срабатывания"""

    @pytest.fixture(scope="class", autouse=True)
    def wait_for_networks(self):
        """ИСПРАВЛЕНИЕ: Активное ожидание готовности сетей"""
        with allure.step("Waiting for networks to initialize"):
            backbone_ready = wait_for_condition(
                lambda: check_network_ready("Backbone"), 
                timeout=120
            )
            kelvpn_ready = wait_for_condition(
                lambda: check_network_ready("KelVPN"), 
                timeout=120
            )
            
            if not backbone_ready:
                allure.attach("Backbone network not ready after 120s", name="Warning")
            if not kelvpn_ready:
                allure.attach("KelVPN network not ready after 120s", name="Warning")
        yield

    @allure.title("Verify Backbone network status - FIXED")
    @allure.description("ИСПРАВЛЕНО: Проверяет реальный статус подключения, не только наличие текста")
    def test_backbone_status_fixed(self, wait_for_networks):
        with allure.step("Get Backbone network status"):
            code, stdout, stderr = run_command(f"{CLI_BIN} net -net Backbone get status")
            
        # ИСПРАВЛЕНИЕ: Проверяем код возврата
        with allure.step("Verify command succeeded"):
            assert code == 0, f"Network command failed (code: {code}): {stderr}"
            
        # ИСПРАВЛЕНИЕ: Проверяем отсутствие ошибок в выводе
        with allure.step("Verify no error messages in output"):
            stdout_lower = stdout.lower()
            error_keywords = ['error', 'failed', 'timeout', 'unreachable', 'disconnected']
            found_errors = [kw for kw in error_keywords if kw in stdout_lower]
            
            if found_errors:
                allure.attach(stdout, name="Command Output with Errors")
                pytest.fail(f"Network errors detected: {found_errors}")
            
        # ИСПРАВЛЕНИЕ: Более строгая проверка содержимого
        with allure.step("Verify network is properly identified"):
            assert "net: Backbone" in stdout, "Backbone network not found in output"
            
        # ИСПРАВЛЕНИЕ: Дополнительные проверки статуса (если доступны)
        with allure.step("Check for positive status indicators"):
            positive_indicators = ['active', 'connected', 'running', 'online']
            has_positive = any(indicator in stdout_lower for indicator in positive_indicators)
            
            if has_positive:
                allure.attach("Network shows positive status", name="Status Check")
            else:
                allure.attach("No clear positive status found", name="Status Warning")
                
        allure.attach(stdout, name="Full Network Status")

    @allure.title("Verify KelVPN network status - FIXED")
    def test_kelvpn_status_fixed(self, wait_for_networks):
        with allure.step("Get KelVPN network status"):
            code, stdout, stderr = run_command(f"{CLI_BIN} net -net KelVPN get status")
            
        with allure.step("Verify command succeeded"):
            assert code == 0, f"KelVPN command failed (code: {code}): {stderr}"
            
        with allure.step("Verify no error messages"):
            stdout_lower = stdout.lower()
            error_keywords = ['error', 'failed', 'timeout', 'unreachable', 'disconnected']
            found_errors = [kw for kw in error_keywords if kw in stdout_lower]
            
            if found_errors:
                allure.attach(stdout, name="KelVPN Output with Errors")
                pytest.fail(f"KelVPN errors detected: {found_errors}")
                
        with allure.step("Verify network identification"):
            assert "net: KelVPN" in stdout, "KelVPN network not found in output"
            
        allure.attach(stdout, name="KelVPN Status")


@allure.feature("Resource Usage")
@allure.story("Performance Metrics")
@allure.severity(allure.severity_level.MINOR)
class TestResourceUsageFixed:
    """ИСПРАВЛЕННЫЕ тесты ресурсов - адекватные лимиты"""

    @allure.title("Check memory usage - FIXED")
    @allure.description("ИСПРАВЛЕНО: Адекватные лимиты памяти на основе системных характеристик")
    def test_memory_usage_fixed(self):
        with allure.step("Get node PID"):
            code, pid, _ = run_command("pgrep -x cellframe-node")
            if code != 0:
                pytest.skip("Node not running")
            pid = pid.strip()

        with allure.step("Get memory usage"):
            code, mem_kb, _ = run_command(f"ps -o rss= -p {pid}")
            assert code == 0, "Failed to get memory usage"
            
            mem_mb = int(mem_kb.strip()) // 1024
            allure.attach(f"{mem_mb} MB", name="Current Memory Usage")

        # ИСПРАВЛЕНИЕ: Адекватные лимиты памяти
        with allure.step("Calculate appropriate memory limits"):
            system_mem_gb = get_system_memory_gb()
            
            # Базовый лимит: 1GB или 15% от системной памяти (что меньше)
            base_limit_mb = 1024
            percentage_limit_mb = int(system_mem_gb * 1024 * 0.15)
            memory_limit_mb = min(base_limit_mb, percentage_limit_mb)
            
            # Минимальный лимит 512MB для корректной работы
            memory_limit_mb = max(memory_limit_mb, 512)
            
            allure.attach(
                f"System RAM: {system_mem_gb}GB, Limit: {memory_limit_mb}MB", 
                name="Memory Limits"
            )

        with allure.step("Verify memory is within reasonable limits"):
            if mem_mb > memory_limit_mb:
                # Дополнительная проверка - может быть временный пик
                time.sleep(5)
                code, mem_kb2, _ = run_command(f"ps -o rss= -p {pid}")
                if code == 0:
                    mem_mb2 = int(mem_kb2.strip()) // 1024
                    allure.attach(f"Recheck: {mem_mb2} MB", name="Memory Recheck")
                    
                    if mem_mb2 > memory_limit_mb:
                        pytest.fail(
                            f"Excessive memory usage: {mem_mb2} MB > {memory_limit_mb} MB limit"
                        )
                else:
                    pytest.fail(
                        f"High memory usage: {mem_mb} MB > {memory_limit_mb} MB limit"
                    )

    @allure.title("Check CPU usage - IMPROVED")
    def test_cpu_usage_improved(self):
        with allure.step("Get node PID"):
            code, pid, _ = run_command("pgrep -x cellframe-node")
            if code != 0:
                pytest.skip("Node not running")
            pid = pid.strip()

        # ИСПРАВЛЕНИЕ: Несколько измерений CPU для точности
        cpu_measurements = []
        
        with allure.step("Take multiple CPU measurements"):
            for i in range(3):
                code, cpu, _ = run_command(f"ps -o %cpu= -p {pid}")
                if code == 0:
                    cpu_percent = float(cpu.strip())
                    cpu_measurements.append(cpu_percent)
                    time.sleep(2)
                    
        if not cpu_measurements:
            pytest.fail("Failed to get CPU measurements")
            
        avg_cpu = sum(cpu_measurements) / len(cpu_measurements)
        max_cpu = max(cpu_measurements)
        
        allure.attach(
            f"Measurements: {cpu_measurements}\nAverage: {avg_cpu:.1f}%\nMax: {max_cpu:.1f}%", 
            name="CPU Usage Analysis"
        )
        
        # Разумные лимиты CPU
        with allure.step("Verify CPU usage is reasonable"):
            assert avg_cpu < 50.0, f"High average CPU usage: {avg_cpu:.1f}%"
            assert max_cpu < 80.0, f"CPU spike detected: {max_cpu:.1f}%"


@allure.feature("Log Analysis")
@allure.story("Error Detection")
@allure.severity(allure.severity_level.CRITICAL)
class TestLogAnalysisFixed:
    """ИСПРАВЛЕННЫЙ анализ логов - расширенный поиск критических ошибок"""

    @allure.title("Check for critical errors in logs - FIXED")
    @allure.description("ИСПРАВЛЕНО: Расширенный поиск критических ошибок")
    def test_no_critical_errors_fixed(self):
        if not os.path.exists(LOG_FILE):
            pytest.skip("Log file not found")
            
        # ИСПРАВЛЕНИЕ: Расширенный список критических паттернов
        critical_patterns = [
            'critical', 'fatal', 'panic', 'abort',
            'segmentation fault', 'segfault', 'sigsegv',
            'core dumped', 'assertion failed', 'assert.*failed',
            'stack overflow', 'buffer overflow',
            'memory leak', 'out of memory', 'oom',
            'deadlock', 'race condition',
            'corruption', 'corrupted'
        ]
        
        found_critical_errors = []
        
        for pattern in critical_patterns:
            with allure.step(f"Search for pattern: {pattern}"):
                code, stdout, _ = run_command(
                    f"grep -i '{pattern}' {LOG_FILE} | head -5 || true"
                )
                
                if stdout.strip():
                    found_critical_errors.append({
                        'pattern': pattern,
                        'matches': stdout.strip()
                    })
                    allure.attach(
                        stdout, 
                        name=f"Critical Error: {pattern}",
                        attachment_type=allure.attachment_type.TEXT
                    )
        
        if found_critical_errors:
            error_summary = "\n".join([
                f"Pattern '{err['pattern']}': {len(err['matches'].split(chr(10)))} matches"
                for err in found_critical_errors
            ])
            
            allure.attach(error_summary, name="Critical Errors Summary")
            pytest.fail(f"Found {len(found_critical_errors)} types of critical errors in logs")
        else:
            allure.attach("No critical errors found", name="Result")

    @allure.title("Analyze error patterns - NEW")
    @allure.description("Новый тест: Анализ паттернов ошибок для выявления проблем")
    def test_error_patterns_analysis(self):
        if not os.path.exists(LOG_FILE):
            pytest.skip("Log file not found")
            
        with allure.step("Count different types of errors"):
            error_types = {
                'ERROR': 0,
                'WARNING': 0,
                'TIMEOUT': 0,
                'CONNECTION': 0,
                'NETWORK': 0
            }
            
            # Подсчет ошибок по типам
            for error_type in error_types.keys():
                code, count, _ = run_command(
                    f"grep -i '{error_type}' {LOG_FILE} | wc -l"
                )
                if code == 0:
                    error_types[error_type] = int(count.strip())
            
            total_errors = sum(error_types.values())
            
            allure.attach(
                f"Error Analysis:\n" + 
                "\n".join([f"{k}: {v}" for k, v in error_types.items()]) +
                f"\nTotal: {total_errors}",
                name="Error Statistics"
            )
            
        with allure.step("Verify error levels are acceptable"):
            # Разумные лимиты для разных типов ошибок
            assert error_types['ERROR'] < 50, f"Too many ERROR messages: {error_types['ERROR']}"
            assert error_types['TIMEOUT'] < 10, f"Too many TIMEOUT errors: {error_types['TIMEOUT']}"
            assert total_errors < 100, f"Excessive total errors: {total_errors}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--alluredir=allure-results"])
