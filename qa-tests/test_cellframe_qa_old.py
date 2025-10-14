#!/usr/bin/env python3
"""
Cellframe Node QA Test Suite with Official Allure Reports
Professional implementation using pytest + allure-pytest

Usage:
    pytest test_cellframe_qa.py --alluredir=allure-results
    allure generate allure-results -o allure-report --clean
    allure serve allure-results
"""

import subprocess
import time
import os
import pytest
import allure
from pathlib import Path


# Test Configuration
NODE_BIN = "/opt/cellframe-node/bin/cellframe-node"
CLI_BIN = "/opt/cellframe-node/bin/cellframe-node-cli"
CONFIG_BIN = "/opt/cellframe-node/bin/cellframe-node-config"
NODE_DIR = "/opt/cellframe-node"
LOG_FILE = "/opt/cellframe-node/var/log/cellframe-node.log"


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


def attach_log(description="Log file"):
    """Attach log file to Allure report"""
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'r') as f:
            allure.attach(
                f.read(),
                name=description,
                attachment_type=allure.attachment_type.TEXT
            )


@allure.feature("Installation")
@allure.story("Package Installation")
@allure.severity(allure.severity_level.CRITICAL)
class TestInstallation:
    """Test suite for Cellframe Node installation verification"""

    @allure.title("Verify Cellframe Node is installed")
    @allure.description("Check if /opt/cellframe-node directory exists")
    def test_node_directory_exists(self):
        with allure.step("Check if node directory exists"):
            assert os.path.exists(NODE_DIR), f"Node directory {NODE_DIR} not found"
            allure.attach(f"Directory found: {NODE_DIR}", name="Result")

    @allure.title("Verify node version")
    @allure.description("Get and verify Cellframe Node version")
    def test_node_version(self):
        with allure.step("Execute cellframe-node -version"):
            code, stdout, stderr = run_command(f"{NODE_BIN} -version")
            
        with allure.step("Verify version output"):
            assert code == 0, f"Version check failed: {stderr}"
            assert "CellframeNode" in stdout, "Invalid version output"
            
            allure.attach(stdout, name="Version Info", attachment_type=allure.attachment_type.TEXT)


@allure.feature("File System")
@allure.story("Directory Structure")
@allure.severity(allure.severity_level.NORMAL)
class TestFileSystem:
    """Test suite for file system structure verification"""

    @allure.title("Verify essential directories exist")
    @pytest.mark.parametrize("directory", [
        "bin", "etc", "var", "python", "share"
    ])
    def test_directories_exist(self, directory):
        path = f"{NODE_DIR}/{directory}"
        with allure.step(f"Check {directory} directory"):
            assert os.path.exists(path), f"Directory {path} not found"
            allure.attach(f"✓ {path}", name=f"{directory} directory")

    @allure.title("Verify executables are present")
    @pytest.mark.parametrize("executable", [
        "cellframe-node",
        "cellframe-node-cli",
        "cellframe-node-tool",
        "cellframe-node-config"
    ])
    def test_executables_exist(self, executable):
        path = f"{NODE_DIR}/bin/{executable}"
        with allure.step(f"Check {executable} exists"):
            assert os.path.exists(path), f"Executable {path} not found"
            
        with allure.step(f"Check {executable} is executable"):
            assert os.access(path, os.X_OK), f"{path} is not executable"
            allure.attach(f"✓ {path}", name=f"{executable} status")

    @allure.title("Verify main configuration file")
    def test_main_config_exists(self):
        config_path = f"{NODE_DIR}/etc/cellframe-node.cfg"
        with allure.step("Check main configuration file"):
            assert os.path.exists(config_path), "Main config not found"
            
        with allure.step("Check config is readable"):
            assert os.access(config_path, os.R_OK), "Config not readable"
            allure.attach(config_path, name="Config path")

    @allure.title("Verify network configurations")
    @pytest.mark.parametrize("network", ["Backbone", "KelVPN"])
    def test_network_configs(self, network):
        config_path = f"{NODE_DIR}/etc/network/{network}/main.cfg"
        with allure.step(f"Check {network} configuration"):
            assert os.path.exists(config_path), f"{network} config not found"
            allure.attach(config_path, name=f"{network} config")


@allure.feature("Python Environment")
@allure.story("Python Installation")
@allure.severity(allure.severity_level.NORMAL)
class TestPythonEnvironment:
    """Test suite for Python environment verification"""

    @allure.title("Verify Python 3.10 is installed")
    def test_python_installed(self):
        python_path = f"{NODE_DIR}/python/bin/python3.10"
        with allure.step("Check Python executable"):
            assert os.path.exists(python_path), "Python 3.10 not found"
            assert os.access(python_path, os.X_OK), "Python not executable"

        with allure.step("Get Python version"):
            code, stdout, stderr = run_command(f"{python_path} --version")
            assert code == 0, f"Python version check failed: {stderr}"
            allure.attach(stdout, name="Python Version")

    @allure.title("Verify pip is installed")
    def test_pip_installed(self):
        pip_path = f"{NODE_DIR}/python/bin/pip3"
        with allure.step("Check pip executable"):
            assert os.path.exists(pip_path), "pip not found"

        with allure.step("Get pip version"):
            code, stdout, stderr = run_command(f"{pip_path} --version")
            assert code == 0, f"pip check failed: {stderr}"
            allure.attach(stdout, name="Pip Version")


@allure.feature("Node Startup")
@allure.story("Manual Startup")
@allure.severity(allure.severity_level.CRITICAL)
class TestNodeStartup:
    """Test suite for node startup verification"""

    @pytest.fixture(scope="class", autouse=True)
    def start_node(self):
        """Start cellframe-node before tests"""
        with allure.step("Starting cellframe-node"):
            # Check if already running
            code, stdout, _ = run_command("pgrep -x cellframe-node")
            if code == 0:
                allure.attach("Node already running", name="Startup")
                yield
                return

            # Start node
            os.makedirs(f"{NODE_DIR}/var/log", exist_ok=True)
            cmd = f"cd {NODE_DIR} && {NODE_BIN} > {LOG_FILE} 2>&1 &"
            subprocess.Popen(cmd, shell=True)
            
            allure.attach("Node startup initiated", name="Startup Command")
            
            # Wait for node to start
            time.sleep(5)
            
        yield
        
        # Attach logs after all tests
        attach_log("Node startup logs")

    @allure.title("Verify node process is running")
    def test_node_process_running(self):
        with allure.step("Check for node process"):
            code, stdout, stderr = run_command("pgrep -x cellframe-node")
            assert code == 0, "Node process not found"
            
            pid = stdout.strip()
            allure.attach(f"PID: {pid}", name="Process Info")

    @allure.title("Verify log file is created")
    def test_log_file_exists(self):
        with allure.step("Check log file"):
            # Wait a bit for logs to be written
            time.sleep(2)
            assert os.path.exists(LOG_FILE), "Log file not created"
            
        with allure.step("Check log file has content"):
            size = os.path.getsize(LOG_FILE)
            assert size > 0, "Log file is empty"
            allure.attach(f"Log size: {size} bytes", name="Log Info")


@allure.feature("CLI Functionality")
@allure.story("CLI Commands")
@allure.severity(allure.severity_level.CRITICAL)
class TestCLI:
    """Test suite for CLI functionality"""

    @pytest.fixture(scope="class")
    def wait_for_cli(self):
        """Wait for CLI socket to be ready"""
        with allure.step("Waiting for CLI server"):
            cli_socket = f"{NODE_DIR}/var/run/node_cli"
            for i in range(30):
                if os.path.exists(cli_socket):
                    allure.attach(f"CLI ready after {i} seconds", name="CLI Status")
                    break
                time.sleep(1)
            else:
                pytest.fail("CLI socket not created after 30 seconds")
        yield

    @allure.title("Verify CLI version command")
    def test_cli_version(self, wait_for_cli):
        with allure.step("Execute 'cellframe-node-cli version'"):
            code, stdout, stderr = run_command(f"{CLI_BIN} version")
            
        with allure.step("Verify command succeeded"):
            assert code == 0, f"CLI version failed: {stderr}"
            assert "cellframe-node version" in stdout, "Invalid version output"
            allure.attach(stdout, name="CLI Version Output")

    @allure.title("Verify CLI net list command")
    def test_cli_net_list(self, wait_for_cli):
        with allure.step("Execute 'cellframe-node-cli net list'"):
            code, stdout, stderr = run_command(f"{CLI_BIN} net list")
            
        with allure.step("Verify command succeeded"):
            assert code == 0, f"CLI net list failed: {stderr}"
            allure.attach(stdout, name="Network List")

        with allure.step("Verify Backbone network is listed"):
            assert "Backbone" in stdout, "Backbone network not found"

        with allure.step("Verify KelVPN network is listed"):
            assert "KelVPN" in stdout, "KelVPN network not found"


@allure.feature("Network Status")
@allure.story("Network Connectivity")
@allure.severity(allure.severity_level.CRITICAL)
class TestNetworkStatus:
    """Test suite for network status verification"""

    @pytest.fixture(scope="class", autouse=True)
    def wait_for_networks(self):
        """Wait for networks to initialize"""
        with allure.step("Waiting 30 seconds for networks to initialize"):
            time.sleep(30)
        yield

    @allure.title("Verify Backbone network status")
    @allure.issue("NET-001", "Network connectivity")
    def test_backbone_status(self, wait_for_networks):
        with allure.step("Get Backbone network status"):
            code, stdout, stderr = run_command(
                f"{CLI_BIN} net -net Backbone get status"
            )
            
        with allure.step("Verify status command succeeded"):
            if code != 0:
                attach_log("Node logs on failure")
                pytest.fail(f"Backbone status check failed: {stderr}")
            
            allure.attach(stdout, name="Backbone Status", 
                         attachment_type=allure.attachment_type.TEXT)

        with allure.step("Check network is active"):
            assert "net: Backbone" in stdout, "Backbone not in output"
            
            # Check for links
            if "active:" in stdout:
                allure.attach("Network has active links", name="Link Status")

    @allure.title("Verify KelVPN network status")
    @allure.issue("NET-002", "KelVPN connectivity")
    def test_kelvpn_status(self, wait_for_networks):
        with allure.step("Get KelVPN network status"):
            code, stdout, stderr = run_command(
                f"{CLI_BIN} net -net KelVPN get status"
            )
            
        with allure.step("Verify status command succeeded"):
            if code != 0:
                attach_log("Node logs on failure")
                pytest.fail(f"KelVPN status check failed: {stderr}")
            
            allure.attach(stdout, name="KelVPN Status",
                         attachment_type=allure.attachment_type.TEXT)

        with allure.step("Check network is active"):
            assert "net: KelVPN" in stdout, "KelVPN not in output"


@allure.feature("Wallet Operations")
@allure.story("Wallet Management")
@allure.severity(allure.severity_level.NORMAL)
class TestWallet:
    """Test suite for wallet operations"""

    @allure.title("List existing wallets")
    def test_wallet_list(self):
        with allure.step("Execute 'wallet list'"):
            code, stdout, stderr = run_command(f"{CLI_BIN} wallet list")
            assert code == 0, f"Wallet list failed: {stderr}"
            allure.attach(stdout, name="Wallet List")

    @allure.title("Create test wallet")
    @allure.description("Create a new wallet for testing purposes")
    def test_wallet_create(self):
        wallet_name = f"qa_test_wallet_{int(time.time())}"
        
        with allure.step(f"Create wallet: {wallet_name}"):
            code, stdout, stderr = run_command(
                f"{CLI_BIN} wallet new -w {wallet_name}"
            )
            assert code == 0, f"Wallet creation failed: {stderr}"
            allure.attach(stdout, name="Wallet Creation Output")

        with allure.step("Verify wallet file exists"):
            wallet_file = f"{NODE_DIR}/var/lib/wallet/{wallet_name}.dwallet"
            assert os.path.exists(wallet_file), "Wallet file not created"
            allure.attach(wallet_file, name="Wallet File Path")

        with allure.step("Get wallet info"):
            code, stdout, stderr = run_command(
                f"{CLI_BIN} wallet info -w {wallet_name} -net Backbone"
            )
            if code == 0:
                allure.attach(stdout, name="Wallet Info")


@allure.feature("Resource Usage")
@allure.story("Performance Metrics")
@allure.severity(allure.severity_level.MINOR)
class TestResourceUsage:
    """Test suite for resource usage monitoring"""

    @allure.title("Check memory usage")
    def test_memory_usage(self):
        with allure.step("Get node PID"):
            code, pid, _ = run_command("pgrep -x cellframe-node")
            if code != 0:
                pytest.skip("Node not running")
            pid = pid.strip()

        with allure.step("Get memory usage"):
            code, mem_kb, _ = run_command(f"ps -o rss= -p {pid}")
            assert code == 0, "Failed to get memory usage"
            
            mem_mb = int(mem_kb.strip()) // 1024
            allure.attach(f"{mem_mb} MB", name="Memory Usage")

        with allure.step("Verify memory is within limits"):
            assert mem_mb < 500, f"High memory usage: {mem_mb} MB"

    @allure.title("Check CPU usage")
    def test_cpu_usage(self):
        with allure.step("Get node PID"):
            code, pid, _ = run_command("pgrep -x cellframe-node")
            if code != 0:
                pytest.skip("Node not running")
            pid = pid.strip()

        with allure.step("Get CPU usage"):
            code, cpu, _ = run_command(f"ps -o %cpu= -p {pid}")
            assert code == 0, "Failed to get CPU usage"
            
            cpu_percent = float(cpu.strip())
            allure.attach(f"{cpu_percent}%", name="CPU Usage")


@allure.feature("Log Analysis")
@allure.story("Error Detection")
@allure.severity(allure.severity_level.NORMAL)
class TestLogAnalysis:
    """Test suite for log file analysis"""

    @allure.title("Verify log file exists and has content")
    def test_log_file_exists(self):
        with allure.step("Check log file"):
            assert os.path.exists(LOG_FILE), "Log file not found"

        with allure.step("Count log lines"):
            with open(LOG_FILE, 'r') as f:
                lines = len(f.readlines())
            allure.attach(f"{lines} lines", name="Log Size")
            assert lines > 0, "Log file is empty"

    @allure.title("Check for critical errors in logs")
    @allure.description("Scan logs for CRITICAL or FATAL messages")
    def test_no_critical_errors(self):
        with allure.step("Search for critical errors"):
            code, stdout, _ = run_command(
                f"grep -i 'critical\\|fatal' {LOG_FILE} || true"
            )
            
            if stdout:
                allure.attach(stdout, name="Critical Errors Found",
                            attachment_type=allure.attachment_type.TEXT)
                pytest.fail(f"Found critical errors in logs")
            else:
                allure.attach("No critical errors", name="Result")

    @allure.title("Count error messages in logs")
    def test_error_count(self):
        with allure.step("Count ERROR messages"):
            code, count, _ = run_command(
                f"grep -i 'error' {LOG_FILE} | wc -l"
            )
            
            error_count = int(count.strip())
            allure.attach(f"{error_count} errors", name="Error Count")
            
            if error_count > 0:
                # Get last few errors
                _, errors, _ = run_command(
                    f"grep -i 'error' {LOG_FILE} | tail -5"
                )
                allure.attach(errors, name="Recent Errors",
                            attachment_type=allure.attachment_type.TEXT)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--alluredir=allure-results"])

