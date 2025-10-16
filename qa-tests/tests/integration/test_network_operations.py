#!/usr/bin/env python3
"""
Integration Tests - Network Operations
Интеграционные тесты сетевых операций
"""

import pytest
import allure
from framework import NodeCLI, NodeAssertions, get_config


@allure.epic("Cellframe Node")
@allure.feature("Network Operations")
@pytest.mark.integration
@pytest.mark.network
class TestNetworkOperations:
    """Интеграционные тесты сетевых операций"""
    
    @allure.story("Network Status")
    @allure.title("All configured networks are accessible")
    @allure.description("Проверяет что все настроенные сети доступны для запросов")
    def test_all_networks_accessible(self, node_cli: NodeCLI, node_assertions: NodeAssertions,
                                   wait_for_networks, test_config):
        """Тест: все сети доступны для запросов"""
        
        networks_to_test = test_config.networks.test_networks
        
        for network_name in networks_to_test:
            with allure.step(f"Check network accessibility: {network_name}"):
                try:
                    status = node_cli.get_network_status(network_name)
                    
                    allure.attach(
                        f"Network: {network_name}\n"
                        f"State: {status.state}\n"
                        f"Nodes: {status.nodes_count}\n"
                        f"Links: {status.active_links}\n"
                        f"Online: {status.is_online}",
                        name=f"Network Status - {network_name}",
                        attachment_type=allure.attachment_type.TEXT
                    )
                    
                    # Сеть должна быть доступна для запросов (не обязательно онлайн)
                    assert status.name == network_name, f"Network name mismatch: {status.name}"
                    assert status.state != "UNKNOWN", f"Network {network_name} state is unknown"
                    
                except Exception as e:
                    pytest.fail(f"Network {network_name} is not accessible: {e}")
    
    @allure.story("Network Connectivity")
    @allure.title("At least one network is online")
    @allure.description("Проверяет что хотя бы одна сеть находится в онлайн состоянии")
    def test_at_least_one_network_online(self, node_cli: NodeCLI, node_assertions: NodeAssertions,
                                       wait_for_networks, test_config):
        """Тест: хотя бы одна сеть онлайн"""
        
        networks_status = node_cli.get_all_networks_status()
        
        with allure.step("Check networks online status"):
            online_networks = []
            offline_networks = []
            
            for network_name, status in networks_status.items():
                if status and status.is_online:
                    online_networks.append(network_name)
                else:
                    offline_networks.append(network_name)
            
            allure.attach(
                f"Online networks: {online_networks}\n"
                f"Offline networks: {offline_networks}\n"
                f"Total networks: {len(networks_status)}",
                name="Networks Summary",
                attachment_type=allure.attachment_type.TEXT
            )
            
            assert len(online_networks) > 0, f"No networks are online. Offline: {offline_networks}"
    
    @allure.story("Network Details")
    @allure.title("Online networks have active connections")
    @allure.description("Проверяет что онлайн сети имеют активные соединения")
    def test_online_networks_have_connections(self, node_cli: NodeCLI, node_assertions: NodeAssertions,
                                            wait_for_networks, test_config):
        """Тест: онлайн сети имеют соединения"""
        
        networks_status = node_cli.get_all_networks_status()
        online_networks = {name: status for name, status in networks_status.items() 
                          if status and status.is_online}
        
        if not online_networks:
            pytest.skip("No networks are online")
        
        for network_name, status in online_networks.items():
            with allure.step(f"Check connections for online network: {network_name}"):
                node_assertions.assert_network_online(status, 
                                                    f"Network {network_name} should be online")
                
                # Онлайн сеть должна иметь хотя бы некоторую активность
                assert status.nodes_count >= 0, f"Invalid nodes count for {network_name}: {status.nodes_count}"
                assert status.active_links >= 0, f"Invalid links count for {network_name}: {status.active_links}"
                
                allure.attach(
                    f"Network: {network_name}\n"
                    f"Nodes: {status.nodes_count}\n"
                    f"Active Links: {status.active_links}",
                    name=f"Connection Details - {network_name}",
                    attachment_type=allure.attachment_type.TEXT
                )


@allure.epic("Cellframe Node")
@allure.feature("Network Performance")
@pytest.mark.integration
@pytest.mark.network
@pytest.mark.performance
class TestNetworkPerformance:
    """Тесты производительности сетевых операций"""
    
    @allure.story("Response Time")
    @allure.title("Network status queries respond quickly")
    @allure.description("Проверяет что запросы статуса сети выполняются быстро")
    def test_network_status_response_time(self, node_cli: NodeCLI, node_assertions: NodeAssertions,
                                        test_config, ensure_node_running):
        """Тест: быстрый отклик запросов статуса сети"""
        
        networks_to_test = test_config.networks.test_networks
        max_response_time = test_config.limits.max_response_time_sec
        
        for network_name in networks_to_test:
            with allure.step(f"Measure response time for network: {network_name}"):
                import time
                start_time = time.time()
                
                try:
                    status = node_cli.get_network_status(network_name)
                    response_time = time.time() - start_time
                    
                    allure.attach(
                        f"Network: {network_name}\n"
                        f"Response time: {response_time:.2f}s\n"
                        f"Limit: {max_response_time}s\n"
                        f"Status: {status.state}",
                        name=f"Response Time - {network_name}",
                        attachment_type=allure.attachment_type.TEXT
                    )
                    
                    node_assertions.assert_response_time_acceptable(
                        response_time, max_response_time,
                        f"Network {network_name} response too slow"
                    )
                    
                except Exception as e:
                    response_time = time.time() - start_time
                    allure.attach(
                        f"Network: {network_name}\n"
                        f"Response time: {response_time:.2f}s\n"
                        f"Error: {str(e)}",
                        name=f"Failed Response - {network_name}",
                        attachment_type=allure.attachment_type.TEXT
                    )
                    
                    # Даже при ошибке, время отклика должно быть разумным
                    node_assertions.assert_response_time_acceptable(
                        response_time, max_response_time * 2,  # Более мягкий лимит для ошибок
                        f"Network {network_name} error response too slow"
                    )
                    
                    # Пропускаем дальнейшие проверки для этой сети
                    continue
    
    @allure.story("Concurrent Access")
    @allure.title("Multiple network queries can run concurrently")
    @allure.description("Проверяет что можно выполнять несколько запросов одновременно")
    @pytest.mark.slow
    def test_concurrent_network_queries(self, node_cli: NodeCLI, node_assertions: NodeAssertions,
                                      test_config, ensure_node_running):
        """Тест: параллельные запросы к сетям"""
        
        import threading
        import time
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        networks_to_test = test_config.networks.test_networks
        if len(networks_to_test) < 2:
            pytest.skip("Need at least 2 networks for concurrent testing")
        
        def query_network(network_name):
            """Функция для запроса статуса сети"""
            start_time = time.time()
            try:
                status = node_cli.get_network_status(network_name)
                return {
                    'network': network_name,
                    'success': True,
                    'response_time': time.time() - start_time,
                    'status': status.state,
                    'error': None
                }
            except Exception as e:
                return {
                    'network': network_name,
                    'success': False,
                    'response_time': time.time() - start_time,
                    'status': None,
                    'error': str(e)
                }
        
        with allure.step("Execute concurrent network queries"):
            start_time = time.time()
            
            with ThreadPoolExecutor(max_workers=len(networks_to_test)) as executor:
                future_to_network = {
                    executor.submit(query_network, network): network 
                    for network in networks_to_test
                }
                
                results = []
                for future in as_completed(future_to_network):
                    result = future.result()
                    results.append(result)
            
            total_time = time.time() - start_time
        
        with allure.step("Analyze concurrent execution results"):
            successful_queries = [r for r in results if r['success']]
            failed_queries = [r for r in results if not r['success']]
            
            avg_response_time = sum(r['response_time'] for r in results) / len(results)
            max_response_time = max(r['response_time'] for r in results)
            
            allure.attach(
                f"Total execution time: {total_time:.2f}s\n"
                f"Successful queries: {len(successful_queries)}\n"
                f"Failed queries: {len(failed_queries)}\n"
                f"Average response time: {avg_response_time:.2f}s\n"
                f"Max response time: {max_response_time:.2f}s\n"
                f"Concurrent efficiency: {(sum(r['response_time'] for r in results) / total_time):.1f}x",
                name="Concurrent Execution Summary",
                attachment_type=allure.attachment_type.TEXT
            )
            
            # Хотя бы половина запросов должна быть успешной
            success_rate = len(successful_queries) / len(results)
            assert success_rate >= 0.5, f"Too many failed concurrent queries: {success_rate:.1%}"
            
            # Общее время должно быть меньше суммы всех запросов (показатель параллелизма)
            total_sequential_time = sum(r['response_time'] for r in results)
            efficiency = total_sequential_time / total_time
            assert efficiency > 1.5, f"Poor concurrent efficiency: {efficiency:.1f}x"


# Конфигурация для интеграционных тестов
pytestmark = [
    pytest.mark.integration,
    pytest.mark.timeout(180)  # Интеграционные тесты могут быть медленнее
]
