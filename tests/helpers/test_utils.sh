#!/bin/bash
# test_utils.sh - Common functions for CellFrame Node tests

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test counters
TESTS_TOTAL=0
TESTS_PASSED=0
TESTS_FAILED=0

# Default values
DEFAULT_TIMEOUT=30
DEFAULT_TEST_NETWORK="testnet"
DEFAULT_TEST_PORT=8079

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TESTS_ROOT="$(dirname "$SCRIPT_DIR")"
PROJECT_ROOT="$(dirname "$TESTS_ROOT")"

# Set defaults if not provided
CELLFRAME_NODE_PATH="${CELLFRAME_NODE_PATH:-$PROJECT_ROOT/build/cellframe-node}"
CELLFRAME_CONFIG_PATH="${CELLFRAME_CONFIG_PATH:-$TESTS_ROOT/fixtures/configs}"
TEST_TIMEOUT="${TEST_TIMEOUT:-$DEFAULT_TIMEOUT}"
TEST_NETWORK="${TEST_NETWORK:-$DEFAULT_TEST_NETWORK}"
TEST_PORT="${TEST_PORT:-$DEFAULT_TEST_PORT}"
PLUGINS_DIR="${PLUGINS_DIR:-$PROJECT_ROOT/build/plugins}"
LOG_DIR="${LOG_DIR:-$TESTS_ROOT/logs}"

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1" >&2
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" >&2
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" >&2
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

log_debug() {
    if [[ "${DEBUG:-0}" == "1" ]]; then
        echo -e "${BLUE}[DEBUG]${NC} $1" >&2
    fi
}

# Test assertion functions
assert_equals() {
    local expected="$1"
    local actual="$2"
    local message="$3"
    
    TESTS_TOTAL=$((TESTS_TOTAL + 1))
    
    if [[ "$expected" == "$actual" ]]; then
        TESTS_PASSED=$((TESTS_PASSED + 1))
        log_success "PASS: $message"
        return 0
    else
        TESTS_FAILED=$((TESTS_FAILED + 1))
        log_error "FAIL: $message"
        log_error "  Expected: '$expected'"
        log_error "  Actual:   '$actual'"
        return 1
    fi
}

assert_not_equals() {
    local expected="$1"
    local actual="$2"
    local message="$3"
    
    TESTS_TOTAL=$((TESTS_TOTAL + 1))
    
    if [[ "$expected" != "$actual" ]]; then
        TESTS_PASSED=$((TESTS_PASSED + 1))
        log_success "PASS: $message"
        return 0
    else
        TESTS_FAILED=$((TESTS_FAILED + 1))
        log_error "FAIL: $message"
        log_error "  Expected NOT: '$expected'"
        log_error "  Actual:       '$actual'"
        return 1
    fi
}

assert_contains() {
    local string="$1"
    local substring="$2"
    local message="$3"
    
    TESTS_TOTAL=$((TESTS_TOTAL + 1))
    
    if [[ "$string" == *"$substring"* ]]; then
        TESTS_PASSED=$((TESTS_PASSED + 1))
        log_success "PASS: $message"
        return 0
    else
        TESTS_FAILED=$((TESTS_FAILED + 1))
        log_error "FAIL: $message"
        log_error "  String: '$string'"
        log_error "  Should contain: '$substring'"
        return 1
    fi
}

assert_file_exists() {
    local file_path="$1"
    local message="$2"
    
    TESTS_TOTAL=$((TESTS_TOTAL + 1))
    
    if [[ -f "$file_path" ]]; then
        TESTS_PASSED=$((TESTS_PASSED + 1))
        log_success "PASS: $message"
        return 0
    else
        TESTS_FAILED=$((TESTS_FAILED + 1))
        log_error "FAIL: $message"
        log_error "  File does not exist: '$file_path'"
        return 1
    fi
}

assert_process_running() {
    local process_name="$1"
    local message="$2"
    
    TESTS_TOTAL=$((TESTS_TOTAL + 1))
    
    if pgrep -f "$process_name" > /dev/null; then
        TESTS_PASSED=$((TESTS_PASSED + 1))
        log_success "PASS: $message"
        return 0
    else
        TESTS_FAILED=$((TESTS_FAILED + 1))
        log_error "FAIL: $message"
        log_error "  Process not running: '$process_name'"
        return 1
    fi
}

assert_process_not_running() {
    local process_name="$1"
    local message="$2"
    
    TESTS_TOTAL=$((TESTS_TOTAL + 1))
    
    if ! pgrep -f "$process_name" > /dev/null; then
        TESTS_PASSED=$((TESTS_PASSED + 1))
        log_success "PASS: $message"
        return 0
    else
        TESTS_FAILED=$((TESTS_FAILED + 1))
        log_error "FAIL: $message"
        log_error "  Process is running: '$process_name'"
        return 1
    fi
}

# Utility functions
wait_for_process() {
    local process_name="$1"
    local timeout="${2:-$TEST_TIMEOUT}"
    local check_interval=1
    
    log_info "Waiting for process '$process_name' (timeout: ${timeout}s)"
    
    for ((i=0; i<timeout; i+=check_interval)); do
        if pgrep -f "$process_name" > /dev/null; then
            log_success "Process '$process_name' is running"
            return 0
        fi
        sleep $check_interval
    done
    
    log_error "Timeout waiting for process '$process_name'"
    return 1
}

wait_for_port() {
    local port="$1"
    local timeout="${2:-$TEST_TIMEOUT}"
    local check_interval=1
    
    log_info "Waiting for port $port to be open (timeout: ${timeout}s)"
    
    for ((i=0; i<timeout; i+=check_interval)); do
        if nc -z localhost "$port" 2>/dev/null; then
            log_success "Port $port is open"
            return 0
        fi
        sleep $check_interval
    done
    
    log_error "Timeout waiting for port $port"
    return 1
}

wait_for_file() {
    local file_path="$1"
    local timeout="${2:-$TEST_TIMEOUT}"
    local check_interval=1
    
    log_info "Waiting for file '$file_path' (timeout: ${timeout}s)"
    
    for ((i=0; i<timeout; i+=check_interval)); do
        if [[ -f "$file_path" ]]; then
            log_success "File '$file_path' exists"
            return 0
        fi
        sleep $check_interval
    done
    
    log_error "Timeout waiting for file '$file_path'"
    return 1
}

# Test execution wrapper
run_test() {
    local test_name="$1"
    local test_function="$2"
    
    log_info "Running test: $test_name"
    
    # Reset counters for this test
    local prev_total=$TESTS_TOTAL
    local prev_passed=$TESTS_PASSED
    local prev_failed=$TESTS_FAILED
    
    # Run the test function
    if "$test_function"; then
        local test_assertions=$((TESTS_TOTAL - prev_total))
        local test_passed=$((TESTS_PASSED - prev_passed))
        log_success "Test '$test_name' completed: $test_passed/$test_assertions assertions passed"
        return 0
    else
        local test_assertions=$((TESTS_TOTAL - prev_total))
        local test_failed=$((TESTS_FAILED - prev_failed))
        log_error "Test '$test_name' failed: $test_failed/$test_assertions assertions failed"
        return 1
    fi
}

# Test suite management
print_test_summary() {
    echo
    echo "=========================================="
    echo "           TEST SUMMARY"
    echo "=========================================="
    echo "Total assertions: $TESTS_TOTAL"
    echo -e "Passed: ${GREEN}$TESTS_PASSED${NC}"
    echo -e "Failed: ${RED}$TESTS_FAILED${NC}"
    
    if [[ $TESTS_FAILED -eq 0 ]]; then
        echo -e "${GREEN}All tests passed!${NC}"
        return 0
    else
        echo -e "${RED}Some tests failed!${NC}"
        return 1
    fi
}

# Cleanup function
cleanup_test_environment() {
    log_info "Cleaning up test environment"
    
    # Stop any running test processes
    pkill -f "cellframe-node.*test" 2>/dev/null || true
    
    # Remove temporary files
    rm -rf "${LOG_DIR}/test_*" 2>/dev/null || true
    
    log_success "Test environment cleaned up"
}

# Setup function
setup_test_environment() {
    log_info "Setting up test environment"
    
    # Create log directory
    mkdir -p "$LOG_DIR"
    
    # Check required binaries (warn if not found, don't fail)
    if [[ ! -x "$CELLFRAME_NODE_PATH" ]]; then
        log_warning "CellFrame Node binary not found: $CELLFRAME_NODE_PATH"
        log_warning "Some tests may be skipped or use mock implementations"
    else
        log_success "CellFrame Node binary found: $CELLFRAME_NODE_PATH"
    fi
    
    # Check required tools
    for tool in curl jq timeout nc; do
        if ! command -v "$tool" >/dev/null 2>&1; then
            log_warning "Tool '$tool' not found, some tests may fail"
        fi
    done
    
    log_success "Test environment set up"
    return 0
}

# Export functions
export -f log_info log_success log_warning log_error log_debug
export -f assert_equals assert_not_equals assert_contains assert_file_exists
export -f assert_process_running assert_process_not_running
export -f wait_for_process wait_for_port wait_for_file
export -f run_test print_test_summary cleanup_test_environment setup_test_environment 

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check required tools
    local required_tools=("curl" "nc" "pkill")
    local missing_tools=()
    
    # Check for timeout command (different on macOS)
    if command -v timeout >/dev/null 2>&1; then
        # Linux timeout available
        export TIMEOUT_CMD="timeout"
    elif command -v gtimeout >/dev/null 2>&1; then
        # macOS gtimeout available (brew install coreutils)
        export TIMEOUT_CMD="gtimeout"
    else
        log_warning "timeout/gtimeout not found - some tests may not have timeout protection"
        export TIMEOUT_CMD=""
    fi
    
    for tool in "${required_tools[@]}"; do
        if ! command -v "$tool" >/dev/null 2>&1; then
            missing_tools+=("$tool")
        fi
    done
    
    if [[ ${#missing_tools[@]} -gt 0 ]]; then
        log_error "Missing required tools: ${missing_tools[*]}"
        log_error "Please install missing tools and try again"
        return 1
    fi
    
    # Check if jq is available (optional but recommended)
    if ! command -v jq >/dev/null 2>&1; then
        log_warning "jq not found - JSON validation tests will be skipped"
    fi
    
    log_success "Prerequisites check passed"
    return 0
} 