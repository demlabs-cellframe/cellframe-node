# Profiling and Performance Testing Guidelines

## Core Principles

### 🚫 NO Standalone Test Executables
- **ALL NEW TESTS MUST BE PART OF CMAKE UNIT TEST SUITE**
- No individual `.c` files compiled as separate executables
- All profiling/performance tests integrated into CMake framework
- Tests discoverable via `make test` or `ctest`

### 📊 Profile-First Optimization
- **NEVER optimize without profiling first**
- Establish baseline measurements before any changes
- Use systematic profiling to identify actual bottlenecks
- Avoid assumptions about performance bottlenecks

## Implementation Standards

### Test Organization
```
crypto/test/crypto/
├── chipmunk_performance_test.c    # Main performance test suite
├── chipmunk_profiling_test.c      # Detailed profiling tests
└── *_test.c                       # Other unit tests
```

### Naming Conventions
- Test files: `*_test.c`
- Test functions: `test_*`
- Performance tests: `test_performance_*`
- Profiling tests: `test_profiling_*`

### CMake Integration
```cmake
# Add to CMakeLists.txt
add_executable(chipmunk_profiling_test chipmunk_profiling_test.c)
target_link_libraries(chipmunk_profiling_test dap_crypto dap_core)
add_test(NAME chipmunk_profiling COMMAND chipmunk_profiling_test)
```

### Test Discovery
- Tests must be runnable via: `ctest`
- Individual tests via: `ctest -R test_name`
- Verbose output: `ctest -V`

## Performance Testing Workflow

### Step 1: Baseline Measurement
```c
// Example baseline test
int test_baseline_chipmunk_operations(void) {
    // Measure current performance
    // Store baseline metrics
    // Return 0 for success, -1 for failure
}
```

### Step 2: Systematic Profiling
```c
// Example profiling test
int test_profiling_chipmunk_bottlenecks(void) {
    // Profile individual operations
    // Identify actual bottlenecks
    // Generate profiling report
}
```

### Step 3: Targeted Optimization
```c
// Example optimization validation
int test_optimization_validation(void) {
    // Test optimized vs baseline
    // Verify correctness
    // Measure improvement
}
```

## Profiling Data Collection

### Required Metrics
- **Time measurements**: High-precision timing for operations
- **Memory usage**: Stack/heap allocation patterns
- **CPU utilization**: Profile CPU-intensive operations  
- **Cache performance**: Memory access patterns

### Reporting Format
```c
typedef struct {
    const char* operation_name;
    double baseline_time_ms;
    double optimized_time_ms;
    double speedup_factor;
    bool correctness_verified;
} performance_result_t;
```

## Integration with Existing Systems

### Current Performance Test
- `crypto/test/crypto/chipmunk_performance_test.c` - main framework
- Environment variables for test modes
- Comprehensive operation coverage

### Migration Plan
1. Integrate standalone profilers into CMake suite
2. Remove individual executable generation
3. Standardize on CMake test discovery
4. Update documentation and workflows

## Quality Assurance

### Test Validation
- All performance tests must pass in CI/CD
- Baseline measurements stored and tracked
- Regression detection for performance degradation
- Automated reporting of optimization results

### Documentation Requirements
- Document all performance baselines
- Explain optimization rationale
- Provide before/after measurements
- Include correctness verification

---

**Remember**: Profile first, optimize second. No guessing, only measuring. 