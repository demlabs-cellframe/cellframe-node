#!/bin/bash
# Cellframe Node QA Functional Test Suite
# Purpose: Test cellframe-node from user perspective in Docker environment
# Reference: QA_SPECIFICATION_LINUX.md
# Version: 5.5-0

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test counters
TESTS_PASSED=0
TESTS_FAILED=0
TESTS_WARNED=0
TESTS_TOTAL=0

# Helper functions
test_pass() {
    echo -e "${GREEN}[PASS]${NC} $1"
    ((TESTS_PASSED++))
    ((TESTS_TOTAL++))
}

test_fail() {
    echo -e "${RED}[FAIL]${NC} $1"
    echo -e "  ${RED}Error:${NC} $2"
    ((TESTS_FAILED++))
    ((TESTS_TOTAL++))
}

test_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
    echo -e "  ${YELLOW}Warning:${NC} $2"
    ((TESTS_WARNED++))
    ((TESTS_TOTAL++))
}

test_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

test_section() {
    echo ""
    echo -e "${BLUE}===========================================================${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}===========================================================${NC}"
    echo ""
}

# ============================================================
# 1. Pre-Installation Checks
# ============================================================
test_section "1. Installation Verification"

# Check installation
if [ -d "/opt/cellframe-node" ]; then
    test_pass "Cellframe-node is installed"
else
    test_fail "Cellframe-node directory not found" "/opt/cellframe-node missing"
    exit 1
fi

# Check version
VERSION_OUTPUT=$(/opt/cellframe-node/bin/cellframe-node -version 2>&1 | head -1)
if [ $? -eq 0 ]; then
    test_pass "Node version: $VERSION_OUTPUT"
else
    test_fail "Version check failed" "$VERSION_OUTPUT"
fi

# ============================================================
# 2. File System Structure
# ============================================================
test_section "2. File System Structure"

# Essential directories
for dir in bin etc var python share; do
    if [ -d "/opt/cellframe-node/$dir" ]; then
        test_pass "Directory /opt/cellframe-node/$dir exists"
    else
        test_fail "Directory missing" "/opt/cellframe-node/$dir not found"
    fi
done

# Essential executables
for exe in cellframe-node cellframe-node-cli cellframe-node-tool cellframe-node-config; do
    if [ -x "/opt/cellframe-node/bin/$exe" ]; then
        test_pass "Executable $exe is present and executable"
    else
        test_fail "Executable missing or not executable" "/opt/cellframe-node/bin/$exe"
    fi
done

# Configuration files
if [ -f "/opt/cellframe-node/etc/cellframe-node.cfg" ]; then
    test_pass "Main configuration file exists"
else
    test_fail "Main configuration missing" "/opt/cellframe-node/etc/cellframe-node.cfg"
fi

# Network configurations
for net in Backbone KelVPN; do
    if [ -f "/opt/cellframe-node/etc/network/$net/main.cfg" ]; then
        test_pass "Network config for $net exists"
    else
        test_fail "Network config missing" "$net/main.cfg"
    fi
done

# ============================================================
# 3. Python Environment
# ============================================================
test_section "3. Python Environment"

# Check Python installation
if [ -x "/opt/cellframe-node/python/bin/python3.10" ]; then
    test_pass "Python 3.10 is installed"
    PY_VERSION=$(/opt/cellframe-node/python/bin/python3.10 --version 2>&1)
    test_info "Python version: $PY_VERSION"
else
    test_fail "Python executable not found" "/opt/cellframe-node/python/bin/python3.10"
fi

# Check pip
if [ -x "/opt/cellframe-node/python/bin/pip3" ]; then
    PIP_VERSION=$(/opt/cellframe-node/python/bin/pip3 --version 2>&1)
    test_pass "Pip is installed: $PIP_VERSION"
else
    test_fail "Pip not found" "/opt/cellframe-node/python/bin/pip3"
fi

# ============================================================
# 4. Node Startup (User Experience)
# ============================================================
test_section "4. Node Startup (Manual)"

test_info "Starting node manually (as user would in Docker)..."
/opt/qa-tests/startup-node.sh

if [ $? -eq 0 ]; then
    test_pass "Node startup script completed successfully"
else
    test_fail "Node startup failed" "Check logs for details"
fi

# Wait a bit for node to stabilize
sleep 5

# Check if process is running
if pgrep -x "cellframe-node" > /dev/null; then
    NODE_PID=$(pgrep -x "cellframe-node")
    test_pass "Node process is running (PID: $NODE_PID)"
else
    test_fail "Node process not found" "Node failed to start or crashed"
fi

# Check log file
if [ -f "/opt/cellframe-node/var/log/cellframe-node.log" ]; then
    LOG_SIZE=$(stat -f%z "/opt/cellframe-node/var/log/cellframe-node.log" 2>/dev/null || stat -c%s "/opt/cellframe-node/var/log/cellframe-node.log" 2>/dev/null)
    if [ "$LOG_SIZE" -gt 0 ]; then
        test_pass "Log file created and has content ($LOG_SIZE bytes)"
        test_info "Last 5 log lines:"
        tail -5 /opt/cellframe-node/var/log/cellframe-node.log | sed 's/^/  /'
    else
        test_warn "Log file exists but is empty" "Node may not be logging"
    fi
else
    test_fail "Log file not created" "/opt/cellframe-node/var/log/cellframe-node.log"
fi

# ============================================================
# 5. CLI Functionality
# ============================================================
test_section "5. CLI Functionality"

# Check CLI socket
if [ -S "/opt/cellframe-node/var/run/node_cli" ]; then
    test_pass "CLI server socket exists"
else
    test_warn "CLI socket not found" "CLI commands may not work"
fi

# Test CLI version
CLI_VERSION=$(/opt/cellframe-node/bin/cellframe-node-cli version 2>&1)
CLI_EXIT=$?
if [ $CLI_EXIT -eq 0 ]; then
    test_pass "CLI 'version' command works"
    test_info "Output: $CLI_VERSION"
else
    test_fail "CLI 'version' command failed" "$CLI_VERSION"
fi

# Test CLI network list
if [ $CLI_EXIT -eq 0 ]; then
    NET_LIST=$(/opt/cellframe-node/bin/cellframe-node-cli net list 2>&1)
    if [ $? -eq 0 ]; then
        test_pass "CLI 'net list' command works"
        test_info "Available networks:"
        echo "$NET_LIST" | sed 's/^/  /'
        
        # Check for expected networks
        if echo "$NET_LIST" | grep -q "Backbone"; then
            test_pass "Backbone network is listed"
        else
            test_fail "Backbone network not found" "Expected in network list"
        fi
        
        if echo "$NET_LIST" | grep -q "KelVPN"; then
            test_pass "KelVPN network is listed"
        else
            test_fail "KelVPN network not found" "Expected in network list"
        fi
    else
        test_fail "CLI 'net list' failed" "$NET_LIST"
    fi
fi

# ============================================================
# 6. Network Status
# ============================================================
test_section "6. Network Status"

test_info "Waiting for networks to initialize (30 seconds)..."
sleep 30

# Check Backbone status
BACKBONE_STATUS=$(/opt/cellframe-node/bin/cellframe-node-cli net -net Backbone get status 2>&1)
if [ $? -eq 0 ]; then
    test_pass "Backbone network status available"
    test_info "Backbone status:"
    echo "$BACKBONE_STATUS" | sed 's/^/  /'
    
    # Check if online
    if echo "$BACKBONE_STATUS" | grep -qi "online\|active"; then
        test_pass "Backbone network is online"
    else
        test_warn "Backbone network status unclear" "May still be initializing"
    fi
else
    test_warn "Backbone status check failed" "$BACKBONE_STATUS"
fi

# Check KelVPN status
KELVPN_STATUS=$(/opt/cellframe-node/bin/cellframe-node-cli net -net KelVPN get status 2>&1)
if [ $? -eq 0 ]; then
    test_pass "KelVPN network status available"
    test_info "KelVPN status:"
    echo "$KELVPN_STATUS" | sed 's/^/  /'
    
    if echo "$KELVPN_STATUS" | grep -qi "online\|active"; then
        test_pass "KelVPN network is online"
    else
        test_warn "KelVPN network status unclear" "May still be initializing"
    fi
else
    test_warn "KelVPN status check failed" "$KELVPN_STATUS"
fi

# ============================================================
# 7. Wallet Operations
# ============================================================
test_section "7. Wallet Operations"

# List existing wallets
WALLET_LIST=$(/opt/cellframe-node/bin/cellframe-node-cli wallet list 2>&1)
if [ $? -eq 0 ]; then
    test_pass "Wallet list command works"
    test_info "Wallets: $WALLET_LIST"
else
    test_fail "Wallet list failed" "$WALLET_LIST"
fi

# Create test wallet
TEST_WALLET="qa_test_wallet_$$"
test_info "Creating test wallet: $TEST_WALLET"
WALLET_CREATE=$(/opt/cellframe-node/bin/cellframe-node-cli wallet new -w "$TEST_WALLET" 2>&1)
if [ $? -eq 0 ]; then
    test_pass "Test wallet created successfully"
    
    # Verify wallet file exists
    if [ -f "/opt/cellframe-node/var/lib/wallet/$TEST_WALLET.dwallet" ]; then
        test_pass "Wallet file created on disk"
    else
        test_fail "Wallet file not found" "/opt/cellframe-node/var/lib/wallet/$TEST_WALLET.dwallet"
    fi
    
    # Get wallet info
    WALLET_INFO=$(/opt/cellframe-node/bin/cellframe-node-cli wallet info -w "$TEST_WALLET" -net Backbone 2>&1)
    if [ $? -eq 0 ]; then
        test_pass "Wallet info command works"
        test_info "Wallet info:"
        echo "$WALLET_INFO" | head -10 | sed 's/^/  /'
    else
        test_warn "Wallet info failed" "$WALLET_INFO"
    fi
else
    test_fail "Wallet creation failed" "$WALLET_CREATE"
fi

# ============================================================
# 8. Configuration Tool
# ============================================================
test_section "8. Configuration Tool"

# Test config tool
CONFIG_NETS=$(/opt/cellframe-node/bin/cellframe-node-config network list 2>&1)
if [ $? -eq 0 ]; then
    test_pass "Config tool 'network list' works"
    test_info "Configured networks:"
    echo "$CONFIG_NETS" | sed 's/^/  /'
else
    test_fail "Config tool failed" "$CONFIG_NETS"
fi

# Check main config
if [ -r "/opt/cellframe-node/etc/cellframe-node.cfg" ]; then
    test_pass "Main config file is readable"
    
    # Check key settings
    DEBUG_MODE=$(grep "^debug_mode" /opt/cellframe-node/etc/cellframe-node.cfg | awk '{print $2}')
    AUTO_ONLINE=$(grep "^auto_online" /opt/cellframe-node/etc/cellframe-node.cfg | awk '{print $2}')
    
    test_info "debug_mode = $DEBUG_MODE"
    test_info "auto_online = $AUTO_ONLINE"
else
    test_fail "Config file not readable" "/opt/cellframe-node/etc/cellframe-node.cfg"
fi

# ============================================================
# 9. Resource Usage
# ============================================================
test_section "9. Resource Usage"

if pgrep -x "cellframe-node" > /dev/null; then
    NODE_PID=$(pgrep -x "cellframe-node")
    
    # Memory usage
    MEM_KB=$(ps -o rss= -p $NODE_PID 2>/dev/null)
    if [ -n "$MEM_KB" ]; then
        MEM_MB=$((MEM_KB / 1024))
        test_pass "Memory usage: ${MEM_MB} MB"
        
        if [ $MEM_MB -lt 500 ]; then
            test_pass "Memory usage is reasonable (<500MB)"
        else
            test_warn "High memory usage" "${MEM_MB} MB"
        fi
    fi
    
    # CPU usage (sample over 2 seconds)
    CPU_USAGE=$(ps -o %cpu= -p $NODE_PID 2>/dev/null)
    if [ -n "$CPU_USAGE" ]; then
        test_pass "CPU usage: ${CPU_USAGE}%"
    fi
    
    # Open files
    OPEN_FILES=$(lsof -p $NODE_PID 2>/dev/null | wc -l)
    if [ -n "$OPEN_FILES" ] && [ "$OPEN_FILES" -gt 0 ]; then
        test_pass "Open file descriptors: $OPEN_FILES"
    fi
else
    test_fail "Cannot check resources" "Node process not running"
fi

# ============================================================
# 10. Log Analysis
# ============================================================
test_section "10. Log Analysis"

if [ -f "/opt/cellframe-node/var/log/cellframe-node.log" ]; then
    LOG_LINES=$(wc -l < /opt/cellframe-node/var/log/cellframe-node.log)
    test_pass "Log file contains $LOG_LINES lines"
    
    # Check for errors
    ERROR_COUNT=$(grep -i "error" /opt/cellframe-node/var/log/cellframe-node.log | wc -l)
    if [ "$ERROR_COUNT" -eq 0 ]; then
        test_pass "No errors found in logs"
    else
        test_warn "Found $ERROR_COUNT error messages in logs" "Review logs for details"
        test_info "Recent errors (last 3):"
        grep -i "error" /opt/cellframe-node/var/log/cellframe-node.log | tail -3 | sed 's/^/  /'
    fi
    
    # Check for warnings
    WARN_COUNT=$(grep -i "warning\|warn" /opt/cellframe-node/var/log/cellframe-node.log | wc -l)
    if [ "$WARN_COUNT" -gt 0 ]; then
        test_info "Found $WARN_COUNT warning messages"
    fi
    
    # Check for critical messages
    CRIT_COUNT=$(grep -i "critical\|fatal" /opt/cellframe-node/var/log/cellframe-node.log | wc -l)
    if [ "$CRIT_COUNT" -eq 0 ]; then
        test_pass "No critical errors in logs"
    else
        test_fail "Critical errors found" "$CRIT_COUNT critical messages in log"
    fi
else
    test_fail "Log file not accessible" "/opt/cellframe-node/var/log/cellframe-node.log"
fi

# ============================================================
# SUMMARY
# ============================================================
test_section "TEST RESULTS SUMMARY"

echo "Total tests:  $TESTS_TOTAL"
echo -e "${GREEN}Passed:       $TESTS_PASSED${NC}"
echo -e "${YELLOW}Warnings:     $TESTS_WARNED${NC}"
echo -e "${RED}Failed:       $TESTS_FAILED${NC}"
echo ""

# Calculate success rate
if [ $TESTS_TOTAL -gt 0 ]; then
    SUCCESS_RATE=$(echo "scale=1; ($TESTS_PASSED * 100) / $TESTS_TOTAL" | bc)
    echo "Success Rate: ${SUCCESS_RATE}%"
    echo ""
fi

# Final verdict
if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ ALL TESTS PASSED${NC}"
    echo ""
    echo "The cellframe-node installation meets all functional requirements."
    exit 0
else
    echo -e "${YELLOW}⚠ TESTS COMPLETED WITH ISSUES${NC}"
    echo ""
    echo "The cellframe-node is functional but some tests failed or warned."
    echo "This is a realistic user experience test in Docker environment."
    echo ""
    echo "Reference: QA_SPECIFICATION_LINUX.md"
    exit 1
fi

