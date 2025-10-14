#!/usr/bin/env python3
"""
Demo test for Allure TestOps integration
Простой демо тест для демонстрации интеграции с Allure TestOps
"""

import pytest
import allure
import os
import time


@allure.feature("Demo Integration")
@allure.story("Allure TestOps Integration")
@allure.severity(allure.severity_level.CRITICAL)
class TestAllureIntegration:
    """Demo test suite for Allure TestOps integration"""

    @allure.title("Demo test - Check allurectl installation")
    @allure.description("Проверяем что allurectl установлен и работает")
    def test_allurectl_installed(self):
        with allure.step("Check if allurectl exists"):
            allurectl_path = "./allurectl"
            assert os.path.exists(allurectl_path), f"allurectl not found at {allurectl_path}"
            allure.attach(f"allurectl found at: {allurectl_path}", name="allurectl path")

        with allure.step("Check allurectl version"):
            import subprocess
            try:
                result = subprocess.run([allurectl_path, "--version"], 
                                      capture_output=True, text=True, timeout=10)
                assert result.returncode == 0, f"allurectl version failed: {result.stderr}"
                version = result.stdout.strip()
                allure.attach(version, name="allurectl version")
                print(f"allurectl version: {version}")
            except Exception as e:
                pytest.fail(f"Failed to get allurectl version: {e}")

    @allure.title("Demo test - Check configuration files")
    @allure.description("Проверяем наличие конфигурационных файлов")
    def test_config_files_exist(self):
        config_files = [
            "allurectl.env",
            "allurectl.env.demo", 
            "run-tests-with-allurectl.sh",
            "Dockerfile.qa-allurectl",
            "ALLURECTL_INTEGRATION.md"
        ]
        
        for config_file in config_files:
            with allure.step(f"Check {config_file}"):
                assert os.path.exists(config_file), f"Config file {config_file} not found"
                allure.attach(f"✓ {config_file} exists", name=f"{config_file} status")

    @allure.title("Demo test - Simulate test execution")
    @allure.description("Симулируем выполнение тестов")
    def test_simulate_execution(self):
        with allure.step("Simulate test preparation"):
            time.sleep(1)  # Симуляция подготовки
            allure.attach("Test preparation completed", name="Preparation status")

        with allure.step("Simulate test execution"):
            time.sleep(2)  # Симуляция выполнения
            allure.attach("Test execution completed", name="Execution status")

        with allure.step("Simulate test validation"):
            time.sleep(1)  # Симуляция валидации
            allure.attach("Test validation completed", name="Validation status")

        # Всегда проходим для демо
        assert True, "Demo test completed successfully"

    @allure.title("Demo test - Check environment variables")
    @allure.description("Проверяем переменные окружения для TestOps")
    def test_environment_variables(self):
        required_vars = [
            "ALLURE_ENDPOINT",
            "ALLURE_TOKEN", 
            "ALLURE_PROJECT_ID"
        ]
        
        with allure.step("Check required environment variables"):
            for var in required_vars:
                value = os.environ.get(var, "NOT_SET")
                allure.attach(f"{var}={value}", name=f"Environment variable {var}")
                
                # Для демо не требуем реальные значения
                if value == "NOT_SET":
                    allure.attach(f"⚠️ {var} not set (expected for demo)", 
                                name=f"{var} status", 
                                attachment_type=allure.attachment_type.TEXT)

    @allure.title("Demo test - Generate test data")
    @allure.description("Генерируем тестовые данные для демонстрации")
    def test_generate_test_data(self):
        with allure.step("Generate test metrics"):
            test_data = {
                "total_tests": 5,
                "passed_tests": 5,
                "failed_tests": 0,
                "execution_time": "10.5s",
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
            allure.attach(str(test_data), name="Test metrics", 
                         attachment_type=allure.attachment_type.JSON)
            
        with allure.step("Generate sample log"):
            sample_log = f"""
[INFO] Starting Cellframe Node QA tests
[INFO] Test environment: demo
[INFO] Timestamp: {time.strftime("%Y-%m-%d %H:%M:%S")}
[INFO] Running 5 test cases
[PASS] test_allurectl_installed - 1.2s
[PASS] test_config_files_exist - 0.8s  
[PASS] test_simulate_execution - 4.1s
[PASS] test_environment_variables - 0.5s
[PASS] test_generate_test_data - 0.9s
[INFO] All tests completed successfully
[INFO] Total execution time: 7.5s
"""
            allure.attach(sample_log, name="Sample test log", 
                         attachment_type=allure.attachment_type.TEXT)

        assert True, "Test data generated successfully"


if __name__ == "__main__":
    # Запуск тестов напрямую
    pytest.main([__file__, "-v", "--alluredir=allure-results"])




