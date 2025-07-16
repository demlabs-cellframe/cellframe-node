#!/bin/bash
# run_tests.sh - Main test runner for CellFrame Node

set -e

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Source utilities
source "$SCRIPT_DIR/helpers/test_utils.sh"

# Test categories
INTEGRATION_TESTS=(
    "test_node_startup.sh"
    "test_binary_plugins.sh"
    "test_python_plugins.sh"
)

E2E_TESTS=(
    # Will be added later
)

ALL_TESTS=("${INTEGRATION_TESTS[@]}" "${E2E_TESTS[@]}")

# Configuration
TEST_RESULTS_FILE="$SCRIPT_DIR/test_results.xml"
TEST_LOG_FILE="$SCRIPT_DIR/logs/test_run.log"

# Usage information
usage() {
    echo "CellFrame Node Test Runner"
    echo
    echo "Usage: $0 [CATEGORY] [OPTIONS]"
    echo
    echo "Categories:"
    echo "  all          Run all tests (default)"
    echo "  integration  Run integration tests only"
    echo "  e2e          Run end-to-end tests only"
    echo "  plugins      Run plugin tests only"
    echo
    echo "Options:"
    echo "  -h, --help         Show this help message"
    echo "  -v, --verbose      Enable verbose output"
    echo "  -d, --debug        Enable debug output"
    echo "  -k, --keep-running Keep services running after tests"
    echo "  -t, --timeout SEC  Set test timeout (default: 30)"
    echo "  -j, --junit FILE   Generate JUnit XML report"
    echo "  --skip-build       Skip building the node"
    echo "  --node-path PATH   Path to cellframe-node binary"
    echo
    echo "Examples:"
    echo "  $0                           # Run all tests"
    echo "  $0 integration              # Run integration tests"
    echo "  $0 plugins -v               # Run plugin tests with verbose output"
    echo "  $0 --node-path ./my-node    # Use custom node binary"
    echo
    echo "Environment Variables:"
    echo "  CELLFRAME_NODE_PATH    Path to cellframe-node binary"
    echo "  PYTHON_PLUGIN_PATH     Path to Python plugin .so file"
    echo "  TEST_TIMEOUT           Test timeout in seconds"
    echo "  DEBUG                  Enable debug mode (0/1)"
    echo "  VERBOSE                Enable verbose mode (0/1)"
}

# Parse command line arguments
parse_args() {
    local category="all"
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                usage
                exit 0
                ;;
            -v|--verbose)
                export VERBOSE=1
                ;;
            -d|--debug)
                export DEBUG=1
                ;;
            -k|--keep-running)
                export KEEP_RUNNING=1
                ;;
            -t|--timeout)
                export TEST_TIMEOUT="$2"
                shift
                ;;
            -j|--junit)
                TEST_RESULTS_FILE="$2"
                shift
                ;;
            --skip-build)
                export SKIP_BUILD=1
                ;;
            --node-path)
                export CELLFRAME_NODE_PATH="$2"
                shift
                ;;
            all|integration|e2e|plugins)
                category="$1"
                ;;
            *)
                log_error "Unknown option: $1"
                usage
                exit 1
                ;;
        esac
        shift
    done
    
    echo "$category"
}

# Build CellFrame Node if needed
build_node() {
    if [[ "${SKIP_BUILD:-0}" == "1" ]]; then
        log_info "Skipping node build"
        return 0
    fi
    
    log_info "Building CellFrame Node..."
    
    cd "$PROJECT_ROOT"
    
    # Create build directory
    if [[ ! -d "build" ]]; then
        mkdir build
        cd build
        
        # Configure without Python plugins (they'll be loaded as binary plugins)
        cmake .. -DSUPPORT_PYTHON_PLUGINS=OFF -DCMAKE_BUILD_TYPE=Debug
    else
        cd build
    fi
    
    # Build
    make -j$(nproc 2>/dev/null || echo "2") cellframe-node cellframe-node-cli
    
    # Build plugin if it exists
    if [[ -f "$PROJECT_ROOT/plugin/plugin-python/CMakeLists.txt" ]]; then
        log_info "Building Python plugin..."
        cd "$PROJECT_ROOT/plugin/plugin-python"
        
        if [[ ! -d "build" ]]; then
            mkdir build
            cd build
            cmake .. -DBUILD_PLUGIN_PACKAGE=ON
        else
            cd build
        fi
        
        make -j$(nproc 2>/dev/null || echo "2")
    fi
    
    cd "$PROJECT_ROOT"
    log_success "Build completed"
}

# Run a single test
run_single_test() {
    local test_script="$1"
    local test_path="$SCRIPT_DIR/integration/$test_script"
    
    if [[ ! -f "$test_path" ]]; then
        log_error "Test script not found: $test_path"
        return 1
    fi
    
    log_info "Running test: $test_script"
    
    # Make sure script is executable
    chmod +x "$test_path"
    
    # Run the test
    if "$test_path"; then
        log_success "Test passed: $test_script"
        return 0
    else
        log_error "Test failed: $test_script"
        return 1
    fi
}

# Run test category
run_test_category() {
    local category="$1"
    local tests_to_run=()
    
    case "$category" in
        all)
            tests_to_run=("${ALL_TESTS[@]}")
            ;;
        integration)
            tests_to_run=("${INTEGRATION_TESTS[@]}")
            ;;
        e2e)
            tests_to_run=("${E2E_TESTS[@]}")
            ;;
        plugins)
            tests_to_run=(
                "test_binary_plugins.sh"
                "test_python_plugins.sh"
            )
            ;;
        *)
            log_error "Unknown test category: $category"
            return 1
            ;;
    esac
    
    if [[ ${#tests_to_run[@]} -eq 0 ]]; then
        log_warning "No tests to run for category: $category"
        return 0
    fi
    
    log_info "Running ${#tests_to_run[@]} tests in category: $category"
    
    local passed=0
    local failed=0
    local failed_tests=()
    
    for test in "${tests_to_run[@]}"; do
        if run_single_test "$test"; then
            ((passed++))
        else
            ((failed++))
            failed_tests+=("$test")
        fi
        echo # Add spacing between tests
    done
    
    # Print category summary
    echo "=========================================="
    echo "         CATEGORY SUMMARY: $category"
    echo "=========================================="
    echo "Tests run: $((passed + failed))"
    echo -e "Passed: ${GREEN}$passed${NC}"
    echo -e "Failed: ${RED}$failed${NC}"
    
    if [[ $failed -gt 0 ]]; then
        echo
        echo "Failed tests:"
        for test in "${failed_tests[@]}"; do
            echo -e "  ${RED}✗${NC} $test"
        done
        return 1
    else
        echo -e "${GREEN}All tests in category '$category' passed!${NC}"
        return 0
    fi
}

# Generate JUnit XML report
generate_junit_report() {
    local results_file="$1"
    
    # This is a basic implementation - could be enhanced
    cat > "$results_file" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<testsuite name="CellFrameNodeTests" tests="$TESTS_TOTAL" failures="$TESTS_FAILED" time="$(date +%s)">
EOF

    # Add individual test results (simplified)
    for test in "${ALL_TESTS[@]}"; do
        cat >> "$results_file" << EOF
  <testcase name="$test" classname="CellFrameNode.Integration">
  </testcase>
EOF
    done
    
    echo "</testsuite>" >> "$results_file"
    
    log_info "JUnit report generated: $results_file"
}

# Prerequisites check is now in test_utils.sh

# Main function
main() {
    local category
    category=$(parse_args "$@")
    
    # Setup logging
    mkdir -p "$(dirname "$TEST_LOG_FILE")"
    
    # Print header
    echo "=========================================="
    echo "        CELLFRAME NODE TEST SUITE"
    echo "=========================================="
    echo "Category: $category"
    echo "Debug: ${DEBUG:-0}"
    echo "Verbose: ${VERBOSE:-0}"
    echo "Timeout: ${TEST_TIMEOUT:-30}s"
    echo "=========================================="
    echo
    
    # Check prerequisites
    if ! check_prerequisites; then
        exit 1
    fi
    
    # Setup test environment
    if ! setup_test_environment; then
        log_error "Failed to setup test environment"
        exit 1
    fi
    
    # Build if needed
    if ! build_node; then
        log_error "Failed to build CellFrame Node"
        exit 1
    fi
    
    # Run tests
    local start_time=$(date +%s)
    
    if run_test_category "$category"; then
        local end_time=$(date +%s)
        local duration=$((end_time - start_time))
        
        echo
        echo "=========================================="
        echo "           FINAL RESULTS"
        echo "=========================================="
        echo -e "Status: ${GREEN}PASSED${NC}"
        echo "Duration: ${duration}s"
        echo "Category: $category"
        
        # Generate JUnit report if requested
        if [[ -n "$TEST_RESULTS_FILE" ]]; then
            generate_junit_report "$TEST_RESULTS_FILE"
        fi
        
        # Cleanup unless keeping running
        if [[ "${KEEP_RUNNING:-0}" != "1" ]]; then
            cleanup_test_environment
        else
            log_info "Services left running (KEEP_RUNNING=1)"
        fi
        
        exit 0
    else
        local end_time=$(date +%s)
        local duration=$((end_time - start_time))
        
        echo
        echo "=========================================="
        echo "           FINAL RESULTS"
        echo "=========================================="
        echo -e "Status: ${RED}FAILED${NC}"
        echo "Duration: ${duration}s"
        echo "Category: $category"
        
        # Generate JUnit report if requested
        if [[ -n "$TEST_RESULTS_FILE" ]]; then
            generate_junit_report "$TEST_RESULTS_FILE"
        fi
        
        # Cleanup
        cleanup_test_environment
        
        exit 1
    fi
}

# Run main function
main "$@" 