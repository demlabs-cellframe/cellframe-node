#!/bin/bash
# Cellframe Node QA Test Suite with Allure Reporting
# Reference: QA_SPECIFICATION_LINUX.md

# Source allure generator
source /opt/qa-tests/allure-results-generator.sh

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Test counters
TESTS_PASSED=0
TESTS_FAILED=0
TESTS_WARNED=0
TESTS_TOTAL=0

# Allure results
ALLURE_RESULTS_DIR="/opt/qa-tests/allure-results"
export ALLURE_RESULTS_DIR

# Initialize Allure
mkdir -p "$ALLURE_RESULTS_DIR"
create_environment
create_categories

# Helper functions
test_pass() {
    local name="$1"
    local description="${2:-Test passed successfully}"
    echo -e "${GREEN}[PASS]${NC} $name"
    create_test_result "$name" "passed" "$description" "" "1000" '{"name": "suite", "value": "QA Tests"},'
    ((TESTS_PASSED++))
    ((TESTS_TOTAL++))
}

test_fail() {
    local name="$1"
    local error="$2"
    echo -e "${RED}[FAIL]${NC} $name"
    echo -e "  ${RED}Error:${NC} $error"
    create_test_result "$name" "failed" "Test failed" "$error" "1000" '{"name": "suite", "value": "QA Tests"},'
    ((TESTS_FAILED++))
    ((TESTS_TOTAL++))
}

test_warn() {
    local name="$1"
    local warning="$2"
    echo -e "${YELLOW}[WARN]${NC} $name"
    echo -e "  ${YELLOW}Warning:${NC} $warning"
    create_test_result "$name" "passed" "Test passed with warnings" "$warning" "1000" '{"name": "suite", "value": "QA Tests"},{"name": "severity", "value": "minor"},'
    ((TESTS_WARNED++))
    ((TESTS_TOTAL++))
}

test_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

test_section() {
    local section_name="$1"
    echo ""
    echo -e "${BLUE}===========================================================${NC}"
    echo -e "${BLUE}  $section_name${NC}"
    echo -e "${BLUE}===========================================================${NC}"
    echo ""
}

# Start test execution
SUITE_START_TIME=$(get_timestamp_ms)

test_section "1. Installation Verification"

if [ -d "/opt/cellframe-node" ]; then
    test_pass "Cellframe-node installation" "Node is installed in /opt/cellframe-node"
else
    test_fail "Cellframe-node installation" "Directory /opt/cellframe-node not found"
    exit 1
fi

VERSION_OUTPUT=$(/opt/cellframe-node/bin/cellframe-node -version 2>&1 | head -1)
if [ $? -eq 0 ]; then
    test_pass "Node version check" "Version: $VERSION_OUTPUT"
else
    test_fail "Node version check" "Failed to get version: $VERSION_OUTPUT"
fi

test_section "2. File System Structure"

for dir in bin etc var python share; do
    if [ -d "/opt/cellframe-node/$dir" ]; then
        test_pass "Directory $dir exists" "Found at /opt/cellframe-node/$dir"
    else
        test_fail "Directory $dir missing" "Expected /opt/cellframe-node/$dir"
    fi
done

for exe in cellframe-node cellframe-node-cli cellframe-node-tool cellframe-node-config; do
    if [ -x "/opt/cellframe-node/bin/$exe" ]; then
        test_pass "Executable $exe" "Present and executable"
    else
        test_fail "Executable $exe" "Missing or not executable"
    fi
done

test_section "3. Python Environment"

if [ -x "/opt/cellframe-node/python/bin/python3.10" ]; then
    PY_VERSION=$(/opt/cellframe-node/python/bin/python3.10 --version 2>&1)
    test_pass "Python 3.10 installation" "$PY_VERSION"
else
    test_fail "Python 3.10" "Not found or not executable"
fi

test_section "4. Node Startup"

test_info "Starting node manually..."
/opt/qa-tests/startup-node.sh > /tmp/startup.log 2>&1

if [ $? -eq 0 ]; then
    test_pass "Node startup" "Node started successfully"
else
    test_fail "Node startup" "Failed to start node"
fi

sleep 5

if pgrep -x "cellframe-node" > /dev/null; then
    NODE_PID=$(pgrep -x "cellframe-node")
    test_pass "Node process running" "PID: $NODE_PID"
else
    test_fail "Node process" "Process not found"
fi

test_section "5. CLI Functionality"

CLI_VERSION=$(/opt/cellframe-node/bin/cellframe-node-cli version 2>&1)
if [ $? -eq 0 ]; then
    test_pass "CLI version command" "Command executed successfully"
else
    test_fail "CLI version command" "$CLI_VERSION"
fi

NET_LIST=$(/opt/cellframe-node/bin/cellframe-node-cli net list 2>&1)
if [ $? -eq 0 ]; then
    test_pass "CLI net list command" "Command executed successfully"
    
    if echo "$NET_LIST" | grep -q "Backbone"; then
        test_pass "Backbone network listed" "Found in network list"
    else
        test_fail "Backbone network" "Not found in list"
    fi
    
    if echo "$NET_LIST" | grep -q "KelVPN"; then
        test_pass "KelVPN network listed" "Found in network list"
    else
        test_fail "KelVPN network" "Not found in list"
    fi
else
    test_fail "CLI net list" "$NET_LIST"
fi

test_section "6. Network Status (30 sec wait)"

sleep 30

BACKBONE_STATUS=$(/opt/cellframe-node/bin/cellframe-node-cli net -net Backbone get status 2>&1)
if [ $? -eq 0 ]; then
    test_pass "Backbone network status" "Status retrieved successfully"
else
    test_warn "Backbone status" "May still be initializing"
fi

KELVPN_STATUS=$(/opt/cellframe-node/bin/cellframe-node-cli net -net KelVPN get status 2>&1)
if [ $? -eq 0 ]; then
    test_pass "KelVPN network status" "Status retrieved successfully"
else
    test_warn "KelVPN status" "May still be initializing"
fi

test_section "7. Wallet Operations"

TEST_WALLET="qa_allure_wallet_$$"
WALLET_CREATE=$(/opt/cellframe-node/bin/cellframe-node-cli wallet new -w "$TEST_WALLET" 2>&1)
if [ $? -eq 0 ]; then
    test_pass "Wallet creation" "Wallet $TEST_WALLET created"
    
    if [ -f "/opt/cellframe-node/var/lib/wallet/$TEST_WALLET.dwallet" ]; then
        test_pass "Wallet file on disk" "File exists"
    else
        test_fail "Wallet file" "File not found"
    fi
else
    test_fail "Wallet creation" "$WALLET_CREATE"
fi

test_section "8. Resource Usage"

if pgrep -x "cellframe-node" > /dev/null; then
    NODE_PID=$(pgrep -x "cellframe-node")
    
    MEM_KB=$(ps -o rss= -p $NODE_PID 2>/dev/null)
    if [ -n "$MEM_KB" ]; then
        MEM_MB=$((MEM_KB / 1024))
        test_pass "Memory usage" "${MEM_MB} MB"
        
        if [ $MEM_MB -lt 500 ]; then
            test_pass "Memory usage reasonable" "Below 500MB threshold"
        else
            test_warn "High memory usage" "${MEM_MB} MB"
        fi
    fi
    
    CPU_USAGE=$(ps -o %cpu= -p $NODE_PID 2>/dev/null)
    if [ -n "$CPU_USAGE" ]; then
        test_pass "CPU usage" "${CPU_USAGE}%"
    fi
fi

test_section "9. Log Analysis"

if [ -f "/opt/cellframe-node/var/log/cellframe-node.log" ]; then
    LOG_LINES=$(wc -l < /opt/cellframe-node/var/log/cellframe-node.log)
    test_pass "Log file exists" "$LOG_LINES lines"
    
    ERROR_COUNT=$(grep -i "error" /opt/cellframe-node/var/log/cellframe-node.log | wc -l)
    if [ "$ERROR_COUNT" -eq 0 ]; then
        test_pass "No errors in logs" "Clean log file"
    else
        test_warn "Errors found in logs" "$ERROR_COUNT error messages (review recommended)"
    fi
    
    CRIT_COUNT=$(grep -i "critical\|fatal" /opt/cellframe-node/var/log/cellframe-node.log | wc -l)
    if [ "$CRIT_COUNT" -eq 0 ]; then
        test_pass "No critical errors" "No fatal issues found"
    else
        test_fail "Critical errors found" "$CRIT_COUNT critical messages"
    fi
else
    test_fail "Log file" "Not found"
fi

# Generate final summary
test_section "TEST RESULTS SUMMARY"

echo "Total tests:  $TESTS_TOTAL"
echo -e "${GREEN}Passed:       $TESTS_PASSED${NC}"
echo -e "${YELLOW}Warnings:     $TESTS_WARNED${NC}"
echo -e "${RED}Failed:       $TESTS_FAILED${NC}"
echo ""

if [ $TESTS_TOTAL -gt 0 ]; then
    SUCCESS_RATE=$(echo "scale=1; ($TESTS_PASSED * 100) / $TESTS_TOTAL" | bc)
    echo "Success Rate: ${SUCCESS_RATE}%"
    echo ""
fi

# Create summary attachment for Allure
SUMMARY_FILE="$ALLURE_RESULTS_DIR/summary.txt"
cat > "$SUMMARY_FILE" << EOF
Cellframe Node QA Test Results

Total Tests: $TESTS_TOTAL
Passed: $TESTS_PASSED
Warnings: $TESTS_WARNED
Failed: $TESTS_FAILED
Success Rate: ${SUCCESS_RATE}%

Test Duration: $(($(get_timestamp_ms) - SUITE_START_TIME))ms
Build Hash: $(grep BUILD_HASH /opt/cellframe-node/bin/cellframe-node 2>/dev/null | head -1 | cut -d'"' -f2 || echo "Unknown")
Test Date: $(date '+%Y-%m-%d %H:%M:%S')
EOF

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ ALL TESTS PASSED${NC}"
    echo ""
    echo "Allure results saved to: $ALLURE_RESULTS_DIR"
    echo "Generate report with: allure generate $ALLURE_RESULTS_DIR -o allure-report"
    exit 0
else
    echo -e "${YELLOW}⚠ TESTS COMPLETED WITH ISSUES${NC}"
    echo ""
    echo "Allure results saved to: $ALLURE_RESULTS_DIR"
    echo "Generate report with: allure generate $ALLURE_RESULTS_DIR -o allure-report"
    exit 1
fi

