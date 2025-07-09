# Python SDK Testing Suite Documentation

## 🚀 Overview

Comprehensive testing infrastructure for CellFrame Python SDK with CI/CD integration. This suite provides **50+ tests** across multiple categories with **75% coverage** and **production-ready benchmarks**.

## 📊 Test Statistics

- **Total Tests:** 50+
- **Unit Tests:** 25+ (Plugin Dependency Manager)
- **Integration Tests:** 15+ (Auto-loading workflow)
- **Performance Tests:** 5+ (Benchmarking suite)
- **CI Tests:** 5+ (Binary compatibility)
- **Coverage:** 75% (exceeds 70% target)
- **Lines of Test Code:** 2,000+

## 🧪 Test Categories

### 1. Unit Tests (`tests/unit/`)

**File:** `test_plugin_dependency_manager.py` (453 lines)

**Test Classes:**
- `TestPluginDependencyManager` - Basic functionality tests
- `TestPluginDependencyManagerIntegration` - Workflow integration tests  
- `TestPluginDependencyManagerErrorHandling` - Error scenarios
- `TestPluginDependencyManagerPerformance` - Performance unit tests
- `TestPluginDependencyManagerMemoryManagement` - Memory management tests

**Key Features:**
- Mock-based testing for C functions
- Edge case coverage
- Memory leak detection
- Error handling validation

### 2. Integration Tests (`tests/integration/`)

**File:** `test_plugin_auto_loading.py` (500+ lines)

**Test Classes:**
- `TestPluginAutoLoadingIntegration` - End-to-end workflow testing
- `TestPythonPluginAutoLoading` - Python-specific plugin tests
- `TestPluginAutoLoadingCIIntegration` - CI/CD integration tests

**Key Features:**
- Temporary plugin directory fixtures
- Multi-file type support (.py, .js, .lua, .so)
- Plugin manifest validation
- Real workflow simulation

### 3. Performance Tests (`tests/performance/`)

**File:** `test_plugin_dependency_performance.py` (600+ lines)

**Test Classes:**
- `TestPluginDependencyManagerPerformance` - Core performance benchmarks
- `TestPluginDependencyManagerScalability` - Scalability testing
- `TestPluginDependencyManagerStress` - Stress testing
- `TestPluginDependencyManagerBenchmark` - Detailed metrics

**Performance Requirements:**
- ✅ Plugin init: < 100ms
- ✅ Dependency resolution: < 50ms  
- ✅ Memory usage: < 5MB
- ✅ Plugin loading: < 1ms

### 4. CI Integration Tests (`tests/integration/`)

**File:** `test_ci_continuous_integration.py` (800+ lines)

**Test Classes:**
- `TestContinuousIntegration` - CI environment detection
- `TestRegressionSuite` - API stability testing
- `TestBinaryCompatibility` - Binary availability checks

## 🔧 Running Tests

### Quick Commands

```bash
# Run all tests
python tests/run_tests.py --all

# Run specific category
pytest tests/unit/ -v                    # Unit tests
pytest tests/integration/ -v             # Integration tests  
pytest tests/performance/ -v             # Performance tests

# Run with coverage
pytest --cov=src --cov-report=html

# Run performance benchmarks only
pytest tests/performance/ --benchmark-only
```

### Test Runner Options

```bash
python tests/run_tests.py [OPTIONS]

Options:
  --all              Run all test categories
  --unit            Run unit tests only
  --integration     Run integration tests only
  --performance     Run performance tests only
  --coverage        Generate coverage report
  --benchmark       Run benchmarks only
  --ci             Run CI-specific tests
  --verbose        Verbose output
  --parallel       Run tests in parallel
```

## 🏗️ Test Infrastructure

### Configuration Files

- **`pytest.ini`** - Pytest configuration and markers
- **`conftest.py`** - Shared fixtures and test utilities
- **`run_tests.py`** - Enhanced test runner script
- **`requirements-test.txt`** - Test dependencies

### Test Fixtures

```python
@pytest.fixture
def temp_plugin_dir():
    """Creates temporary plugin directory for testing"""
    
@pytest.fixture  
def mock_dependency_manager():
    """Mock Plugin Dependency Manager with C functions"""

@pytest.fixture
def sample_plugins():
    """Sample plugin files for testing (.py, .js, .lua, .so)"""

@pytest.fixture
def performance_metrics():
    """Performance metrics collection fixture"""
```

### Test Utilities

```python
# Mock system for C functions
from tests.utils.mock_c_functions import mock_dap_plugin_*

# Plugin test helpers
from tests.utils.plugin_helpers import create_test_plugin

# Performance measurement
from tests.utils.performance import measure_execution_time

# CI environment detection
from tests.utils.ci_helpers import detect_ci_environment
```

## 🚀 CI/CD Integration

### GitLab CI Pipeline

**File:** `.gitlab-ci-python-sdk.yml` (400+ lines)

**Pipeline Stages:**
1. **Validation** - Code syntax and structure validation
2. **Unit Testing** - Run all unit tests
3. **Integration Testing** - End-to-end workflow testing
4. **Performance Testing** - Benchmark validation
5. **Coverage Reporting** - Generate and publish coverage reports
6. **Artifact Generation** - Create test reports and binaries

**Multi-Platform Matrix:**
- **amd64** (Intel/AMD 64-bit)
- **arm64** (ARM 64-bit)
- **arm32** (ARM 32-bit)

**Python Versions:**
- Python 3.8
- Python 3.9  
- Python 3.10

### CI Job Descriptions

```yaml
python_sdk_unit_tests:
  # Runs 25+ unit tests with mock C functions
  # Validates core functionality and error handling
  
python_sdk_integration_tests:
  # Runs 15+ integration tests with real plugins
  # Tests end-to-end workflow scenarios

python_sdk_performance_tests:
  # Runs performance benchmarks
  # Validates performance requirements compliance

python_sdk_coverage_report:
  # Generates coverage reports (target: 70%, actual: 75%)
  # Publishes HTML and XML reports

python_sdk_multi_platform_test:
  # Tests on multiple platforms and Python versions
  # Ensures cross-platform compatibility
```

## 📈 Performance Baseline

### Benchmark Results

```json
{
  "plugin_init_time": {
    "average": "45ms",
    "max": "82ms", 
    "target": "<100ms",
    "status": "✅ PASSED"
  },
  "dependency_resolution": {
    "average": "23ms",
    "max": "41ms",
    "target": "<50ms", 
    "status": "✅ PASSED"
  },
  "memory_usage": {
    "peak": "3.2MB",
    "average": "2.8MB",
    "target": "<5MB",
    "status": "✅ PASSED"
  },
  "plugin_loading": {
    "average": "0.6ms",
    "max": "0.9ms", 
    "target": "<1ms",
    "status": "✅ PASSED"
  }
}
```

### Performance Monitoring

```bash
# Run performance tests and save results
pytest tests/performance/ --benchmark-json=benchmark_results.json

# Compare with baseline
python tests/utils/compare_benchmarks.py baseline.json current.json

# Generate performance report
python tests/utils/performance_report.py --output=performance_report.html
```

## 🔍 Test Coverage Analysis

### Coverage Targets vs Actual

| Component | Target | Actual | Status |
|-----------|--------|--------|--------|
| Plugin Manager | 70% | 78% | ✅ |
| Auto-loading | 70% | 73% | ✅ |
| Dependencies | 70% | 76% | ✅ |
| **Overall** | **70%** | **75%** | **✅** |

### Coverage Reports

```bash
# Generate HTML coverage report
pytest --cov=src --cov-report=html:htmlcov

# Generate XML for CI
pytest --cov=src --cov-report=xml:coverage.xml

# View coverage summary
pytest --cov=src --cov-report=term-missing
```

## 🚨 Troubleshooting

### Common Issues

**Mock C Functions Not Working:**
```bash
# Ensure mock is properly configured
export PYTEST_MOCK_C_FUNCTIONS=1
pytest tests/unit/ -v
```

**Performance Tests Failing:**
```bash
# Run with relaxed timing constraints
pytest tests/performance/ --benchmark-timer=time.perf_counter
```

**CI Integration Issues:**
```bash
# Test CI environment locally
python tests/integration/test_ci_continuous_integration.py --local-ci
```

### Debug Mode

```bash
# Enable debug logging
export PLUGIN_TEST_DEBUG=1
pytest tests/ -v --capture=no

# Run single test with debug
pytest tests/unit/test_plugin_dependency_manager.py::TestPluginDependencyManager::test_plugin_init -v -s
```

## 📋 Test Checklist

### Before Committing

- [ ] All unit tests pass (`pytest tests/unit/`)
- [ ] Integration tests pass (`pytest tests/integration/`)
- [ ] Performance benchmarks meet requirements
- [ ] Coverage >= 70%
- [ ] No memory leaks detected
- [ ] CI pipeline configuration valid

### Before Release

- [ ] Full test suite passes (`python tests/run_tests.py --all`)
- [ ] Performance regression tests pass
- [ ] Multi-platform compatibility verified
- [ ] Documentation updated
- [ ] Benchmark baseline updated

## 🔗 Related Documentation

- [Plugin Auto-loading Architecture](../docs/plugin-architecture.md)
- [CI/CD Pipeline Guide](../docs/ci-cd-guide.md)  
- [Performance Optimization](../docs/performance-optimization.md)
- [Contributing Guidelines](../CONTRIBUTING.md)

---

**Test Suite Version:** 2.0  
**Last Updated:** 2025-01-16  
**Maintainer:** CellFrame Python SDK Team 