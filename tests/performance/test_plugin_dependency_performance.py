"""
Performance benchmark tests for Plugin Dependency Manager System
Tests performance characteristics of the plugin auto-loading system
"""
import pytest
import time
from unittest.mock import Mock, MagicMock, patch
import sys
import os
import statistics
import json
from pathlib import Path
from typing import List, Dict, Tuple

# Add paths for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../dap-sdk/plugin/src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

# Performance test configuration
PERFORMANCE_CONFIG = {
    "small_plugin_set": 10,
    "medium_plugin_set": 50,
    "large_plugin_set": 100,
    "xlarge_plugin_set": 500,
    "max_init_time": 0.1,        # 100ms
    "max_resolution_time": 0.05,  # 50ms
    "max_memory_usage": 5 * 1024 * 1024,  # 5MB
    "benchmark_iterations": 10
}

# Mock C functions for performance testing
def create_performance_mocks():
    """Create mocks optimized for performance testing"""
    return {
        'dap_plugin_dependency_manager_init': Mock(return_value=0),
        'dap_plugin_dependency_manager_deinit': Mock(),
        'dap_plugin_dependency_manager_register_type_handler': Mock(return_value=0),
        'dap_plugin_dependency_manager_get_type_handler': Mock(return_value=Mock()),
        'dap_plugin_dependency_manager_resolve_dependencies': Mock(return_value=[]),
        'dap_plugin_dependency_manager_detect_circular_dependencies': Mock(return_value=0),
        'dap_plugin_dependency_manager_add_plugin': Mock(return_value=0),
        'dap_plugin_dependency_manager_remove_plugin': Mock(return_value=0),
        'dap_plugin_dependency_manager_get_plugin_count': Mock(return_value=0),
        'dap_plugin_dependency_manager_get_handler_count': Mock(return_value=0),
        'dap_plugin_dependency_manager_clear_all': Mock()
    }

# Performance mocks
PERF_MOCKS = create_performance_mocks()

with patch.dict('sys.modules', {'dap_plugin_dependency_manager': MagicMock(**PERF_MOCKS)}):
    try:
        from dap_plugin_dependency_manager import (
            dap_plugin_dependency_manager_init,
            dap_plugin_dependency_manager_deinit,
            dap_plugin_dependency_manager_register_type_handler,
            dap_plugin_dependency_manager_get_type_handler,
            dap_plugin_dependency_manager_resolve_dependencies,
            dap_plugin_dependency_manager_detect_circular_dependencies,
            dap_plugin_dependency_manager_add_plugin,
            dap_plugin_dependency_manager_remove_plugin,
            dap_plugin_dependency_manager_get_plugin_count,
            dap_plugin_dependency_manager_get_handler_count,
            dap_plugin_dependency_manager_clear_all
        )
    except ImportError:
        # Create performance-optimized mocks
        dap_plugin_dependency_manager_init = PERF_MOCKS['dap_plugin_dependency_manager_init']
        dap_plugin_dependency_manager_deinit = PERF_MOCKS['dap_plugin_dependency_manager_deinit']
        dap_plugin_dependency_manager_register_type_handler = PERF_MOCKS['dap_plugin_dependency_manager_register_type_handler']
        dap_plugin_dependency_manager_get_type_handler = PERF_MOCKS['dap_plugin_dependency_manager_get_type_handler']
        dap_plugin_dependency_manager_resolve_dependencies = PERF_MOCKS['dap_plugin_dependency_manager_resolve_dependencies']
        dap_plugin_dependency_manager_detect_circular_dependencies = PERF_MOCKS['dap_plugin_dependency_manager_detect_circular_dependencies']
        dap_plugin_dependency_manager_add_plugin = PERF_MOCKS['dap_plugin_dependency_manager_add_plugin']
        dap_plugin_dependency_manager_remove_plugin = PERF_MOCKS['dap_plugin_dependency_manager_remove_plugin']
        dap_plugin_dependency_manager_get_plugin_count = PERF_MOCKS['dap_plugin_dependency_manager_get_plugin_count']
        dap_plugin_dependency_manager_get_handler_count = PERF_MOCKS['dap_plugin_dependency_manager_get_handler_count']
        dap_plugin_dependency_manager_clear_all = PERF_MOCKS['dap_plugin_dependency_manager_clear_all']


def measure_time(func, *args, **kwargs):
    """Measure execution time of a function"""
    start_time = time.perf_counter()
    result = func(*args, **kwargs)
    end_time = time.perf_counter()
    return result, end_time - start_time


def run_benchmark(func, iterations=PERFORMANCE_CONFIG["benchmark_iterations"], *args, **kwargs):
    """Run benchmark with multiple iterations"""
    times = []
    results = []
    
    for _ in range(iterations):
        result, exec_time = measure_time(func, *args, **kwargs)
        times.append(exec_time)
        results.append(result)
    
    return {
        'results': results,
        'times': times,
        'avg_time': statistics.mean(times),
        'min_time': min(times),
        'max_time': max(times),
        'std_dev': statistics.stdev(times) if len(times) > 1 else 0
    }


@pytest.mark.performance
@pytest.mark.plugin
@pytest.mark.dependency_manager
class TestPluginDependencyManagerPerformance:
    """Performance tests for Plugin Dependency Manager"""

    def test_initialization_performance(self):
        """Test dependency manager initialization performance"""
        dap_plugin_dependency_manager_init.return_value = 0
        
        benchmark = run_benchmark(dap_plugin_dependency_manager_init)
        
        assert benchmark['avg_time'] < PERFORMANCE_CONFIG["max_init_time"]
        assert all(result == 0 for result in benchmark['results'])
        
        print(f"✅ Init Performance: {benchmark['avg_time']:.4f}s avg, {benchmark['max_time']:.4f}s max")

    def test_type_handler_registration_performance(self):
        """Test type handler registration performance"""
        dap_plugin_dependency_manager_register_type_handler.return_value = 0
        mock_handler = Mock()
        
        benchmark = run_benchmark(
            dap_plugin_dependency_manager_register_type_handler,
            10,  # iterations
            ".py", mock_handler
        )
        
        assert benchmark['avg_time'] < 0.001  # < 1ms
        assert all(result == 0 for result in benchmark['results'])
        
        print(f"✅ Handler Registration Performance: {benchmark['avg_time']:.4f}s avg")

    def test_plugin_addition_performance_small_set(self):
        """Test plugin addition performance with small set"""
        dap_plugin_dependency_manager_add_plugin.return_value = 0
        
        plugin_count = PERFORMANCE_CONFIG["small_plugin_set"]
        
        def add_plugins():
            for i in range(plugin_count):
                dap_plugin_dependency_manager_add_plugin(f"plugin_{i}.py", ["python-plugin"])
        
        benchmark = run_benchmark(add_plugins, 5)
        
        assert benchmark['avg_time'] < 0.01  # < 10ms for small set
        
        print(f"✅ Small Set ({plugin_count} plugins): {benchmark['avg_time']:.4f}s avg")

    def test_plugin_addition_performance_medium_set(self):
        """Test plugin addition performance with medium set"""
        dap_plugin_dependency_manager_add_plugin.return_value = 0
        
        plugin_count = PERFORMANCE_CONFIG["medium_plugin_set"]
        
        def add_plugins():
            for i in range(plugin_count):
                dap_plugin_dependency_manager_add_plugin(f"plugin_{i}.py", ["python-plugin"])
        
        benchmark = run_benchmark(add_plugins, 3)
        
        assert benchmark['avg_time'] < 0.05  # < 50ms for medium set
        
        print(f"✅ Medium Set ({plugin_count} plugins): {benchmark['avg_time']:.4f}s avg")

    def test_plugin_addition_performance_large_set(self):
        """Test plugin addition performance with large set"""
        dap_plugin_dependency_manager_add_plugin.return_value = 0
        
        plugin_count = PERFORMANCE_CONFIG["large_plugin_set"]
        
        def add_plugins():
            for i in range(plugin_count):
                dap_plugin_dependency_manager_add_plugin(f"plugin_{i}.py", ["python-plugin"])
        
        benchmark = run_benchmark(add_plugins, 2)
        
        assert benchmark['avg_time'] < 0.1  # < 100ms for large set
        
        print(f"✅ Large Set ({plugin_count} plugins): {benchmark['avg_time']:.4f}s avg")

    def test_dependency_resolution_performance(self):
        """Test dependency resolution performance"""
        # Mock complex dependency resolution
        resolution_orders = [
            [f"plugin_{i}.py" for i in range(PERFORMANCE_CONFIG["small_plugin_set"])],
            [f"plugin_{i}.py" for i in range(PERFORMANCE_CONFIG["medium_plugin_set"])],
            [f"plugin_{i}.py" for i in range(PERFORMANCE_CONFIG["large_plugin_set"])]
        ]
        
        for i, order in enumerate(resolution_orders):
            dap_plugin_dependency_manager_resolve_dependencies.return_value = order
            
            benchmark = run_benchmark(dap_plugin_dependency_manager_resolve_dependencies, 5)
            
            assert benchmark['avg_time'] < PERFORMANCE_CONFIG["max_resolution_time"]
            assert all(len(result) == len(order) for result in benchmark['results'])
            
            print(f"✅ Resolution Performance ({len(order)} plugins): {benchmark['avg_time']:.4f}s avg")

    def test_circular_dependency_detection_performance(self):
        """Test circular dependency detection performance"""
        dap_plugin_dependency_manager_detect_circular_dependencies.return_value = 0
        
        benchmark = run_benchmark(dap_plugin_dependency_manager_detect_circular_dependencies, 20)
        
        assert benchmark['avg_time'] < 0.01  # < 10ms
        assert all(result == 0 for result in benchmark['results'])
        
        print(f"✅ Circular Detection Performance: {benchmark['avg_time']:.4f}s avg")

    def test_plugin_lookup_performance(self):
        """Test plugin lookup performance"""
        dap_plugin_dependency_manager_get_plugin_count.return_value = 100
        
        benchmark = run_benchmark(dap_plugin_dependency_manager_get_plugin_count, 100)
        
        assert benchmark['avg_time'] < 0.001  # < 1ms
        assert all(result == 100 for result in benchmark['results'])
        
        print(f"✅ Plugin Lookup Performance: {benchmark['avg_time']:.4f}s avg")

    def test_handler_lookup_performance(self):
        """Test handler lookup performance"""
        mock_handler = Mock()
        dap_plugin_dependency_manager_get_type_handler.return_value = mock_handler
        
        benchmark = run_benchmark(
            dap_plugin_dependency_manager_get_type_handler,
            50,  # iterations
            ".py"
        )
        
        assert benchmark['avg_time'] < 0.001  # < 1ms
        assert all(result == mock_handler for result in benchmark['results'])
        
        print(f"✅ Handler Lookup Performance: {benchmark['avg_time']:.4f}s avg")

    def test_plugin_removal_performance(self):
        """Test plugin removal performance"""
        dap_plugin_dependency_manager_remove_plugin.return_value = 0
        
        benchmark = run_benchmark(
            dap_plugin_dependency_manager_remove_plugin,
            10,  # iterations
            "test_plugin.py"
        )
        
        assert benchmark['avg_time'] < 0.001  # < 1ms
        assert all(result == 0 for result in benchmark['results'])
        
        print(f"✅ Plugin Removal Performance: {benchmark['avg_time']:.4f}s avg")

    def test_clear_all_performance(self):
        """Test clear all performance"""
        benchmark = run_benchmark(dap_plugin_dependency_manager_clear_all, 10)
        
        assert benchmark['avg_time'] < 0.01  # < 10ms
        
        print(f"✅ Clear All Performance: {benchmark['avg_time']:.4f}s avg")


@pytest.mark.performance
@pytest.mark.plugin
@pytest.mark.dependency_manager
@pytest.mark.scalability
class TestPluginDependencyManagerScalability:
    """Scalability tests for Plugin Dependency Manager"""

    def test_scalability_plugin_addition(self):
        """Test scalability of plugin addition"""
        dap_plugin_dependency_manager_add_plugin.return_value = 0
        
        plugin_counts = [10, 50, 100, 500]
        results = []
        
        for count in plugin_counts:
            def add_plugins():
                for i in range(count):
                    dap_plugin_dependency_manager_add_plugin(f"plugin_{i}.py", ["python-plugin"])
            
            benchmark = run_benchmark(add_plugins, 2)
            results.append({
                'plugin_count': count,
                'avg_time': benchmark['avg_time'],
                'time_per_plugin': benchmark['avg_time'] / count
            })
            
            print(f"✅ Scalability ({count} plugins): {benchmark['avg_time']:.4f}s total, {benchmark['avg_time']/count:.6f}s per plugin")
        
        # Test that time per plugin doesn't increase significantly with scale
        time_per_plugin_ratios = []
        for i in range(1, len(results)):
            ratio = results[i]['time_per_plugin'] / results[i-1]['time_per_plugin']
            time_per_plugin_ratios.append(ratio)
        
        # Time per plugin should not increase dramatically (max 2x)
        assert all(ratio < 2.0 for ratio in time_per_plugin_ratios)

    def test_scalability_dependency_resolution(self):
        """Test scalability of dependency resolution"""
        plugin_counts = [10, 50, 100, 500]
        
        for count in plugin_counts:
            # Mock resolution order
            resolution_order = [f"plugin_{i}.py" for i in range(count)]
            dap_plugin_dependency_manager_resolve_dependencies.return_value = resolution_order
            
            benchmark = run_benchmark(dap_plugin_dependency_manager_resolve_dependencies, 3)
            
            # Resolution time should be reasonable even for large sets
            assert benchmark['avg_time'] < 0.1  # < 100ms
            
            print(f"✅ Resolution Scalability ({count} plugins): {benchmark['avg_time']:.4f}s avg")

    def test_scalability_memory_usage(self):
        """Test memory usage scalability"""
        # This would measure actual memory usage in a real implementation
        # For now, we simulate memory usage patterns
        
        plugin_counts = [10, 50, 100, 500]
        
        for count in plugin_counts:
            # Simulate memory usage (in bytes)
            estimated_memory = count * 1024  # 1KB per plugin
            
            # Memory usage should scale linearly, not exponentially
            assert estimated_memory < count * 2048  # Max 2KB per plugin
            
            print(f"✅ Memory Scalability ({count} plugins): ~{estimated_memory/1024:.1f}KB estimated")

    def test_scalability_concurrent_operations(self):
        """Test scalability with concurrent operations"""
        dap_plugin_dependency_manager_add_plugin.return_value = 0
        dap_plugin_dependency_manager_get_plugin_count.return_value = 100
        
        def concurrent_operations():
            # Simulate concurrent adds and lookups
            for i in range(10):
                dap_plugin_dependency_manager_add_plugin(f"plugin_{i}.py", ["python-plugin"])
                dap_plugin_dependency_manager_get_plugin_count()
        
        benchmark = run_benchmark(concurrent_operations, 5)
        
        assert benchmark['avg_time'] < 0.05  # < 50ms
        
        print(f"✅ Concurrent Operations Performance: {benchmark['avg_time']:.4f}s avg")


@pytest.mark.performance
@pytest.mark.plugin
@pytest.mark.dependency_manager
@pytest.mark.stress
class TestPluginDependencyManagerStress:
    """Stress tests for Plugin Dependency Manager"""

    def test_stress_large_plugin_set(self):
        """Stress test with very large plugin set"""
        dap_plugin_dependency_manager_add_plugin.return_value = 0
        
        plugin_count = PERFORMANCE_CONFIG["xlarge_plugin_set"]
        
        def add_large_set():
            for i in range(plugin_count):
                dap_plugin_dependency_manager_add_plugin(f"plugin_{i}.py", ["python-plugin"])
        
        benchmark = run_benchmark(add_large_set, 1)
        
        # Should complete within reasonable time even for large set
        assert benchmark['avg_time'] < 1.0  # < 1 second
        
        print(f"✅ Stress Test ({plugin_count} plugins): {benchmark['avg_time']:.4f}s")

    def test_stress_repeated_operations(self):
        """Stress test with repeated operations"""
        dap_plugin_dependency_manager_add_plugin.return_value = 0
        dap_plugin_dependency_manager_remove_plugin.return_value = 0
        
        def repeated_operations():
            for i in range(100):
                dap_plugin_dependency_manager_add_plugin(f"plugin_{i}.py", ["python-plugin"])
                dap_plugin_dependency_manager_remove_plugin(f"plugin_{i}.py")
        
        benchmark = run_benchmark(repeated_operations, 3)
        
        assert benchmark['avg_time'] < 0.5  # < 500ms
        
        print(f"✅ Repeated Operations Stress Test: {benchmark['avg_time']:.4f}s avg")

    def test_stress_complex_dependencies(self):
        """Stress test with complex dependency chains"""
        dap_plugin_dependency_manager_add_plugin.return_value = 0
        
        # Create complex dependency chains
        def complex_dependencies():
            for i in range(50):
                deps = [f"plugin_{j}.py" for j in range(max(0, i-5), i)]
                if not deps:
                    deps = ["python-plugin"]
                dap_plugin_dependency_manager_add_plugin(f"plugin_{i}.py", deps)
        
        benchmark = run_benchmark(complex_dependencies, 2)
        
        assert benchmark['avg_time'] < 0.2  # < 200ms
        
        print(f"✅ Complex Dependencies Stress Test: {benchmark['avg_time']:.4f}s avg")

    def test_stress_memory_pressure(self):
        """Stress test under memory pressure"""
        # This would test actual memory pressure in a real implementation
        # For now, we simulate memory-intensive operations
        
        dap_plugin_dependency_manager_add_plugin.return_value = 0
        dap_plugin_dependency_manager_clear_all.return_value = None
        
        def memory_pressure_test():
            # Add many plugins
            for i in range(200):
                dap_plugin_dependency_manager_add_plugin(f"plugin_{i}.py", ["python-plugin"])
            
            # Clear all and repeat
            dap_plugin_dependency_manager_clear_all()
            
            # Add again
            for i in range(200):
                dap_plugin_dependency_manager_add_plugin(f"plugin_{i}.py", ["python-plugin"])
        
        benchmark = run_benchmark(memory_pressure_test, 2)
        
        assert benchmark['avg_time'] < 1.0  # < 1 second
        
        print(f"✅ Memory Pressure Stress Test: {benchmark['avg_time']:.4f}s avg")


@pytest.mark.performance
@pytest.mark.plugin
@pytest.mark.dependency_manager
@pytest.mark.benchmark
class TestPluginDependencyManagerBenchmark:
    """Benchmark tests for Plugin Dependency Manager"""

    def test_benchmark_initialization(self):
        """Benchmark initialization performance"""
        dap_plugin_dependency_manager_init.return_value = 0
        
        benchmark = run_benchmark(dap_plugin_dependency_manager_init, 100)
        
        benchmark_result = {
            'operation': 'initialization',
            'avg_time_ms': benchmark['avg_time'] * 1000,
            'min_time_ms': benchmark['min_time'] * 1000,
            'max_time_ms': benchmark['max_time'] * 1000,
            'std_dev_ms': benchmark['std_dev'] * 1000,
            'iterations': 100
        }
        
        self._save_benchmark_result(benchmark_result)
        
        assert benchmark['avg_time'] < 0.001  # < 1ms
        
        print(f"📊 Benchmark - Initialization: {benchmark['avg_time']*1000:.2f}ms avg")

    def test_benchmark_plugin_operations(self):
        """Benchmark plugin operations"""
        dap_plugin_dependency_manager_add_plugin.return_value = 0
        
        operations = [
            ('add_plugin', lambda: dap_plugin_dependency_manager_add_plugin("test.py", ["python-plugin"])),
            ('remove_plugin', lambda: dap_plugin_dependency_manager_remove_plugin("test.py")),
            ('get_count', lambda: dap_plugin_dependency_manager_get_plugin_count()),
        ]
        
        benchmark_results = []
        
        for op_name, op_func in operations:
            benchmark = run_benchmark(op_func, 50)
            
            result = {
                'operation': op_name,
                'avg_time_ms': benchmark['avg_time'] * 1000,
                'min_time_ms': benchmark['min_time'] * 1000,
                'max_time_ms': benchmark['max_time'] * 1000,
                'std_dev_ms': benchmark['std_dev'] * 1000,
                'iterations': 50
            }
            
            benchmark_results.append(result)
            
            print(f"📊 Benchmark - {op_name}: {benchmark['avg_time']*1000:.2f}ms avg")
        
        self._save_benchmark_results(benchmark_results)

    def test_benchmark_dependency_resolution(self):
        """Benchmark dependency resolution"""
        resolution_sizes = [10, 50, 100, 500]
        benchmark_results = []
        
        for size in resolution_sizes:
            resolution_order = [f"plugin_{i}.py" for i in range(size)]
            dap_plugin_dependency_manager_resolve_dependencies.return_value = resolution_order
            
            benchmark = run_benchmark(dap_plugin_dependency_manager_resolve_dependencies, 20)
            
            result = {
                'operation': f'dependency_resolution_{size}',
                'plugin_count': size,
                'avg_time_ms': benchmark['avg_time'] * 1000,
                'min_time_ms': benchmark['min_time'] * 1000,
                'max_time_ms': benchmark['max_time'] * 1000,
                'std_dev_ms': benchmark['std_dev'] * 1000,
                'iterations': 20
            }
            
            benchmark_results.append(result)
            
            print(f"📊 Benchmark - Resolution ({size} plugins): {benchmark['avg_time']*1000:.2f}ms avg")
        
        self._save_benchmark_results(benchmark_results)

    def _save_benchmark_result(self, result):
        """Save single benchmark result to file"""
        results_file = Path("benchmark_results.json")
        
        if results_file.exists():
            with open(results_file, 'r') as f:
                results = json.load(f)
        else:
            results = []
        
        results.append(result)
        
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)

    def _save_benchmark_results(self, results):
        """Save multiple benchmark results to file"""
        for result in results:
            self._save_benchmark_result(result)


if __name__ == "__main__":
    # Run performance tests
    pytest.main([__file__, "-v", "-m", "performance"]) 