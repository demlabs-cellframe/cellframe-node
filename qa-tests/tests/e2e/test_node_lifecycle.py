#!/usr/bin/env python3
"""
End-to-End Tests - Node Lifecycle
E2E тесты жизненного цикла ноды
"""

import pytest
import allure
import time
from framework import NodeCLI, NodeAssertions, get_config


@allure.epic("Cellframe Node")
@allure.feature("Node Lifecycle")
@pytest.mark.e2e
@pytest.mark.critical
class TestNodeLifecycle:
    """E2E тесты жизненного цикла ноды"""
    
    @allure.story("Node Stability")
    @allure.title("Node maintains stability during extended operation")
    @allure.description("Проверяет стабильность ноды в течение продолжительного времени")
    @pytest.mark.slow
    def test_node_extended_stability(self, node_cli: NodeCLI, node_assertions: NodeAssertions,
                                   performance_monitor, test_config, ensure_node_running):
        """Тест: стабильность ноды при длительной работе"""
        
        test_duration_minutes = 5  # Можно увеличить для более длительного теста
        check_interval_seconds = 30
        
        start_time = time.time()
        end_time = start_time + (test_duration_minutes * 60)
        
        stability_metrics = {
            'checks_performed': 0,
            'successful_checks': 0,
            'failed_checks': 0,
            'memory_measurements': [],
            'cpu_measurements': [],
            'network_status_changes': {},
            'errors': []
        }
        
        with allure.step(f"Monitor node stability for {test_duration_minutes} minutes"):
            while time.time() < end_time:
                check_start = time.time()
                stability_metrics['checks_performed'] += 1
                
                try:
                    # Проверяем что нода все еще работает
                    assert node_cli.is_node_running(), "Node stopped during stability test"
                    
                    # Проверяем доступность версии
                    version_result = node_cli.get_version()
                    node_assertions.assert_command_success(version_result, "Version check failed")
                    
                    # Мониторим ресурсы
                    pid = node_cli.get_node_pid()
                    if pid:
                        memory_mb = node_cli.get_memory_usage(pid)
                        stability_metrics['memory_measurements'].append(memory_mb)
                        
                        # Проверяем что память не растет неконтролируемо
                        if len(stability_metrics['memory_measurements']) > 1:
                            memory_growth = memory_mb - stability_metrics['memory_measurements'][0]
                            if memory_growth > 500:  # 500MB рост - подозрительно
                                allure.attach(
                                    f"Potential memory leak detected:\n"
                                    f"Initial memory: {stability_metrics['memory_measurements'][0]:.1f} MB\n"
                                    f"Current memory: {memory_mb:.1f} MB\n"
                                    f"Growth: {memory_growth:.1f} MB",
                                    name="Memory Growth Warning",
                                    attachment_type=allure.attachment_type.TEXT
                                )
                    
                    # Проверяем статус сетей
                    networks_status = node_cli.get_all_networks_status()
                    for network_name, status in networks_status.items():
                        if network_name not in stability_metrics['network_status_changes']:
                            stability_metrics['network_status_changes'][network_name] = []
                        
                        if status:
                            stability_metrics['network_status_changes'][network_name].append({
                                'timestamp': time.time(),
                                'state': status.state,
                                'is_online': status.is_online
                            })
                    
                    stability_metrics['successful_checks'] += 1
                    
                except Exception as e:
                    stability_metrics['failed_checks'] += 1
                    stability_metrics['errors'].append({
                        'timestamp': time.time(),
                        'error': str(e)
                    })
                    
                    allure.attach(
                        f"Stability check failed at {time.time():.0f}: {e}",
                        name=f"Stability Error #{stability_metrics['failed_checks']}",
                        attachment_type=allure.attachment_type.TEXT
                    )
                
                # Ждем до следующей проверки
                check_duration = time.time() - check_start
                sleep_time = max(0, check_interval_seconds - check_duration)
                if sleep_time > 0:
                    time.sleep(sleep_time)
        
        with allure.step("Analyze stability metrics"):
            success_rate = stability_metrics['successful_checks'] / stability_metrics['checks_performed']
            
            # Расчет статистики памяти
            memory_stats = {}
            if stability_metrics['memory_measurements']:
                memory_stats = {
                    'min': min(stability_metrics['memory_measurements']),
                    'max': max(stability_metrics['memory_measurements']),
                    'avg': sum(stability_metrics['memory_measurements']) / len(stability_metrics['memory_measurements']),
                    'growth': stability_metrics['memory_measurements'][-1] - stability_metrics['memory_measurements'][0]
                }
            
            allure.attach(
                f"Stability Test Results:\n"
                f"Duration: {test_duration_minutes} minutes\n"
                f"Total checks: {stability_metrics['checks_performed']}\n"
                f"Successful checks: {stability_metrics['successful_checks']}\n"
                f"Failed checks: {stability_metrics['failed_checks']}\n"
                f"Success rate: {success_rate:.1%}\n"
                f"Memory stats: {memory_stats}\n"
                f"Network status changes: {len(stability_metrics['network_status_changes'])} networks monitored",
                name="Stability Test Summary",
                attachment_type=allure.attachment_type.TEXT
            )
            
            # Проверяем критерии стабильности
            assert success_rate >= 0.95, f"Stability test failed: {success_rate:.1%} success rate"
            
            if memory_stats:
                node_assertions.assert_memory_usage_within_limit(
                    memory_stats['max'], 
                    message=f"Peak memory usage too high during stability test"
                )
                
                # Проверяем что нет значительной утечки памяти
                if memory_stats['growth'] > 200:  # 200MB рост за тест
                    pytest.fail(f"Potential memory leak: {memory_stats['growth']:.1f} MB growth")
    
    @allure.story("Resource Management")
    @allure.title("Node resource usage remains within acceptable limits")
    @allure.description("Проверяет что нода не превышает лимиты использования ресурсов")
    def test_resource_usage_limits(self, node_cli: NodeCLI, node_assertions: NodeAssertions,
                                 performance_monitor, test_config, ensure_node_running):
        """Тест: использование ресурсов в пределах лимитов"""
        
        pid = node_cli.get_node_pid()
        if not pid:
            pytest.skip("Cannot get node PID for resource monitoring")
        
        # Собираем метрики в течение некоторого времени
        measurement_duration = 60  # 1 минута
        measurements = []
        
        with allure.step(f"Collect resource metrics for {measurement_duration}s"):
            start_time = time.time()
            
            while time.time() - start_time < measurement_duration:
                try:
                    memory_mb = node_cli.get_memory_usage(pid)
                    cpu_percent = node_cli.get_cpu_usage(pid, measurement_duration=2)
                    
                    measurements.append({
                        'timestamp': time.time(),
                        'memory_mb': memory_mb,
                        'cpu_percent': cpu_percent
                    })
                    
                    # Обновляем peak memory в performance monitor
                    if memory_mb > performance_monitor['peak_memory_mb']:
                        performance_monitor['peak_memory_mb'] = memory_mb
                    
                    time.sleep(10)  # Измерения каждые 10 секунд
                    
                except Exception as e:
                    allure.attach(f"Resource measurement error: {e}", 
                                 name="Measurement Error", 
                                 attachment_type=allure.attachment_type.TEXT)
                    time.sleep(5)
        
        if not measurements:
            pytest.skip("No resource measurements collected")
        
        with allure.step("Analyze resource usage"):
            memory_values = [m['memory_mb'] for m in measurements]
            cpu_values = [m['cpu_percent'] for m in measurements if m['cpu_percent'] is not None]
            
            memory_stats = {
                'min': min(memory_values),
                'max': max(memory_values),
                'avg': sum(memory_values) / len(memory_values)
            }
            
            cpu_stats = {}
            if cpu_values:
                cpu_stats = {
                    'min': min(cpu_values),
                    'max': max(cpu_values),
                    'avg': sum(cpu_values) / len(cpu_values)
                }
            
            allure.attach(
                f"Resource Usage Analysis:\n"
                f"Measurement duration: {measurement_duration}s\n"
                f"Measurements collected: {len(measurements)}\n"
                f"Memory stats (MB): {memory_stats}\n"
                f"CPU stats (%): {cpu_stats}\n"
                f"Memory limit: {test_config.limits.max_memory_mb} MB\n"
                f"CPU limit: {test_config.limits.max_cpu_percent}%",
                name="Resource Usage Report",
                attachment_type=allure.attachment_type.TEXT
            )
            
            # Проверяем лимиты
            node_assertions.assert_memory_usage_within_limit(
                memory_stats['max'],
                message=f"Peak memory usage exceeds limit: {memory_stats['max']:.1f} MB"
            )
            
            if cpu_stats:
                node_assertions.assert_cpu_usage_within_limit(
                    cpu_stats['avg'],
                    message=f"Average CPU usage exceeds limit: {cpu_stats['avg']:.1f}%"
                )
                
                # Проверяем что нет постоянной высокой нагрузки
                high_cpu_measurements = [c for c in cpu_values if c > test_config.limits.max_cpu_percent]
                high_cpu_ratio = len(high_cpu_measurements) / len(cpu_values)
                
                assert high_cpu_ratio < 0.3, f"Too many high CPU measurements: {high_cpu_ratio:.1%}"


@allure.epic("Cellframe Node")
@allure.feature("System Integration")
@pytest.mark.e2e
@pytest.mark.integration
class TestSystemIntegration:
    """E2E тесты системной интеграции"""
    
    @allure.story("Full Workflow")
    @allure.title("Complete node operation workflow")
    @allure.description("Полный рабочий процесс операций с нодой")
    def test_complete_node_workflow(self, node_cli: NodeCLI, node_assertions: NodeAssertions,
                                  isolated_test_environment, test_config):
        """Тест: полный рабочий процесс с нодой"""
        
        workflow_steps = []
        
        with allure.step("Step 1: Verify node is operational"):
            # Проверяем что нода работает
            assert node_cli.is_node_running(), "Node must be running for workflow test"
            
            # Получаем базовую информацию
            node_info = node_cli.get_node_info()
            workflow_steps.append(f"Node version: {node_info.version}")
            
            allure.attach(f"Node Info: {node_info}", name="Initial Node State", 
                         attachment_type=allure.attachment_type.TEXT)
        
        with allure.step("Step 2: Check network connectivity"):
            # Проверяем доступность сетей
            networks_status = node_cli.get_all_networks_status()
            online_networks = [name for name, status in networks_status.items() 
                             if status and status.is_online]
            
            workflow_steps.append(f"Networks online: {len(online_networks)}")
            
            if online_networks:
                allure.attach(f"Online networks: {online_networks}", 
                             name="Network Connectivity", 
                             attachment_type=allure.attachment_type.TEXT)
            else:
                allure.attach("No networks are online", 
                             name="Network Connectivity Warning", 
                             attachment_type=allure.attachment_type.TEXT)
        
        with allure.step("Step 3: Perform health validation"):
            # Комплексная проверка здоровья
            health_report = node_cli.validate_node_health()
            workflow_steps.append(f"Health check: {'PASS' if health_report['overall_healthy'] else 'FAIL'}")
            
            allure.attach(str(health_report), name="Health Validation", 
                         attachment_type=allure.attachment_type.JSON)
            
            node_assertions.assert_node_health_good(health_report, "Health validation failed")
        
        with allure.step("Step 4: Test CLI responsiveness"):
            # Проверяем отзывчивость CLI
            commands_to_test = ["version", "help"]
            response_times = []
            
            for cmd in commands_to_test:
                start_time = time.time()
                result = node_cli.execute_custom_command(cmd, timeout=10)
                response_time = time.time() - start_time
                
                node_assertions.assert_command_success(result, f"Command failed: {cmd}")
                response_times.append(response_time)
            
            avg_response_time = sum(response_times) / len(response_times)
            workflow_steps.append(f"Average CLI response: {avg_response_time:.2f}s")
            
            node_assertions.assert_response_time_acceptable(
                avg_response_time, 
                message="CLI responsiveness test failed"
            )
        
        with allure.step("Step 5: Validate resource efficiency"):
            # Проверяем эффективность использования ресурсов
            pid = node_cli.get_node_pid()
            if pid:
                memory_mb = node_cli.get_memory_usage(pid)
                workflow_steps.append(f"Memory usage: {memory_mb:.1f} MB")
                
                node_assertions.assert_memory_usage_within_limit(
                    memory_mb, 
                    message="Resource efficiency validation failed"
                )
        
        # Финальный отчет о workflow
        with allure.step("Workflow completion summary"):
            workflow_summary = "\n".join([f"✓ {step}" for step in workflow_steps])
            
            allure.attach(
                f"Complete Node Workflow - SUCCESS\n\n{workflow_summary}\n\n"
                f"Total workflow time: {isolated_test_environment['duration']:.2f}s",
                name="Workflow Summary",
                attachment_type=allure.attachment_type.TEXT
            )


# Конфигурация для E2E тестов
pytestmark = [
    pytest.mark.e2e,
    pytest.mark.timeout(600)  # E2E тесты могут быть длительными
]
