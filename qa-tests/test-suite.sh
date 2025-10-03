#!/bin/bash
# Cellframe Node QA Test Suite
# Reference: QA_SPECIFICATION_LINUX.md
# Purpose: Automated testing of cellframe-node installation and functionality

set -e

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test counters
TESTS_PASSED=0
TESTS_FAILED=0
TESTS_TOTAL=0

# Log function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

# Test result functions
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
}

test_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

# Test section header
test_section() {
    echo ""
    echo -e "${BLUE}===========================================================${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}===========================================================${NC}"
    echo ""
}

# Wait for condition with timeout
wait_for() {
    local timeout=$1
    local check_command=$2
    local description=$3
    local elapsed=0
    
    while [ $elapsed -lt $timeout ]; do
        if eval "$check_command" 2>/dev/null; then
            return 0
        fi
        sleep 5
        ((elapsed+=5))
        test_info "$description... ${elapsed}s/${timeout}s"
    done
    return 1
}

# =============================================================================
# TEST SECTION 1: PRE-INSTALLATION CHECKS
# =============================================================================
test_section "1. Pre-Installation Checks"

# Check disk space
DISK_SPACE=$(df / | awk 'NR==2 {print $4}')
if [ "$DISK_SPACE" -gt 5242880 ]; then  # 5GB in KB
    test_pass "Disk space sufficient (>5GB available)"
else
    test_fail "Disk space insufficient" "Less than 5GB available"
fi

# Check internet connectivity
if ping -c 1 8.8.8.8 >/dev/null 2>&1; then
    test_pass "Internet connectivity available"
else
    test_fail "Internet connectivity" "Cannot reach 8.8.8.8"
fi

# Check no existing process
if ! pgrep -f cellframe-node >/dev/null; then
    test_pass "No existing cellframe-node process running"
else
    test_fail "Process check" "cellframe-node already running"
fi

# =============================================================================
# TEST SECTION 2: INSTALLATION
# =============================================================================
test_section "2. Package Installation"

# Pre-configure debconf answers
test_info "Pre-configuring installation parameters..."
cat <<EOF | debconf-set-selections
cellframe-node cellframe-node/auto_online boolean true
cellframe-node cellframe-node/debug_mode boolean false
cellframe-node cellframe-node/server_enabled boolean false
cellframe-node cellframe-node/accept_connections boolean false
cellframe-node cellframe-node/server_addr string 0.0.0.0
cellframe-node cellframe-node/server_port string 8079
cellframe-node cellframe-node/backbone_enabled boolean true
cellframe-node cellframe-node/kelvpn_enabled boolean true
EOF

# Install package
log "Installing cellframe-node package..."
if apt-get install -y cellframe-node >/tmp/install.log 2>&1; then
    test_pass "Package installation completed"
else
    test_fail "Package installation" "apt-get install failed (see /tmp/install.log)"
    cat /tmp/install.log
    exit 1
fi

# Check installation exit code
if [ $? -eq 0 ]; then
    test_pass "Installation exit code is 0"
else
    test_fail "Installation exit code" "Exit code: $?"
fi

# =============================================================================
# TEST SECTION 3: FILE SYSTEM CHECKS
# =============================================================================
test_section "3. File System Verification"

# Check main directories
for dir in bin etc var python share; do
    if [ -d "/opt/cellframe-node/$dir" ]; then
        test_pass "Directory /opt/cellframe-node/$dir exists"
    else
        test_fail "Directory check" "/opt/cellframe-node/$dir missing"
    fi
done

# Check executables
for exe in cellframe-node cellframe-node-cli cellframe-node-tool cellframe-node-config; do
    if [ -x "/opt/cellframe-node/bin/$exe" ]; then
        test_pass "Executable /opt/cellframe-node/bin/$exe present and executable"
    else
        test_fail "Executable check" "/opt/cellframe-node/bin/$exe missing or not executable"
    fi
done

# Check main config
if [ -f "/opt/cellframe-node/etc/cellframe-node.cfg" ]; then
    test_pass "Main config file exists"
else
    test_fail "Main config" "cellframe-node.cfg missing"
fi

# Check network configs
for net in Backbone KelVPN; do
    if [ -f "/opt/cellframe-node/etc/network/$net/main.cfg" ]; then
        test_pass "Network config for $net exists"
    else
        test_fail "Network config" "$net/main.cfg missing"
    fi
done

# Check var directory structure
for subdir in log run lib/wallet lib/global_db lib/plugins; do
    if [ -d "/opt/cellframe-node/var/$subdir" ]; then
        test_pass "Directory /opt/cellframe-node/var/$subdir exists"
    else
        test_fail "Var directory" "$subdir missing"
    fi
done

# =============================================================================
# TEST SECTION 4: PYTHON ENVIRONMENT
# =============================================================================
test_section "4. Python Environment Verification"

# Check Python interpreter
if [ -x "/opt/cellframe-node/python/bin/python3" ]; then
    PYTHON_VERSION=$(/opt/cellframe-node/python/bin/python3 --version)
    test_pass "Python interpreter present: $PYTHON_VERSION"
else
    test_fail "Python interpreter" "python3 not found or not executable"
fi

# Check pip
if [ -x "/opt/cellframe-node/python/bin/pip3" ]; then
    PIP_VERSION=$(/opt/cellframe-node/python/bin/pip3 --version)
    test_pass "Pip present: $PIP_VERSION"
else
    test_fail "Pip" "pip3 not found or not executable"
fi

# Check pycfhelpers
if /opt/cellframe-node/python/bin/python3 -c "import pycfhelpers" 2>/dev/null; then
    PKG_VERSION=$(/opt/cellframe-node/python/bin/python3 -c "import pycfhelpers; print(pycfhelpers.__version__)" 2>/dev/null || echo "unknown")
    test_pass "pycfhelpers package imports successfully (version: $PKG_VERSION)"
else
    test_warn "pycfhelpers import" "Package not available or import failed"
fi

# Check pycftools
if /opt/cellframe-node/python/bin/python3 -c "import pycftools" 2>/dev/null; then
    PKG_VERSION=$(/opt/cellframe-node/python/bin/python3 -c "import pycftools; print(pycftools.__version__)" 2>/dev/null || echo "unknown")
    test_pass "pycftools package imports successfully (version: $PKG_VERSION)"
else
    test_warn "pycftools import" "Package not available or import failed"
fi

# =============================================================================
# TEST SECTION 5: SERVICE MANAGEMENT
# =============================================================================
test_section "5. Service Management"

# Wait for service to start (it should auto-start after installation)
sleep 5

# Check service file
if [ -f "/opt/cellframe-node/share/cellframe-node.service" ]; then
    test_pass "Systemd service file exists"
else
    test_fail "Service file" "cellframe-node.service missing"
fi

# Check if service is enabled
if systemctl is-enabled cellframe-node >/dev/null 2>&1; then
    test_pass "Service is enabled"
else
    test_warn "Service enabled" "Service not enabled for auto-start"
fi

# Check if service is running
if systemctl is-active cellframe-node >/dev/null 2>&1; then
    test_pass "Service is active (running)"
else
    test_fail "Service status" "Service is not active"
    systemctl status cellframe-node || true
fi

# Check process
if pgrep -f cellframe-node >/dev/null; then
    PID=$(pgrep -f cellframe-node)
    test_pass "cellframe-node process is running (PID: $PID)"
else
    test_fail "Process check" "No cellframe-node process found"
fi

# Check PID file
if [ -f "/opt/cellframe-node/var/run/cellframe-node.pid" ]; then
    test_pass "PID file created"
else
    test_warn "PID file" "cellframe-node.pid not found"
fi

# Check log file
if [ -f "/opt/cellframe-node/var/log/cellframe-node.log" ]; then
    test_pass "Log file created"
    LOG_SIZE=$(stat -c%s "/opt/cellframe-node/var/log/cellframe-node.log")
    test_info "Log file size: $LOG_SIZE bytes"
else
    test_fail "Log file" "cellframe-node.log not found"
fi

# =============================================================================
# TEST SECTION 6: CLI FUNCTIONALITY
# =============================================================================
test_section "6. CLI Functionality"

# Wait for CLI to be ready
sleep 10

# Test version command
if /opt/cellframe-node/bin/cellframe-node-cli version >/tmp/version.out 2>&1; then
    VERSION=$(cat /tmp/version.out)
    test_pass "CLI version command works: $VERSION"
else
    test_fail "CLI version" "Command failed or timeout"
    cat /tmp/version.out
fi

# Test CLI response time
START_TIME=$(date +%s)
/opt/cellframe-node/bin/cellframe-node-cli version >/dev/null 2>&1
END_TIME=$(date +%s)
RESPONSE_TIME=$((END_TIME - START_TIME))
if [ $RESPONSE_TIME -lt 5 ]; then
    test_pass "CLI response time acceptable ($RESPONSE_TIME seconds)"
else
    test_warn "CLI response time" "Slow response: $RESPONSE_TIME seconds"
fi

# Test network list command
if /opt/cellframe-node/bin/cellframe-node-cli net list >/tmp/netlist.out 2>&1; then
    test_pass "CLI net list command works"
    cat /tmp/netlist.out | head -20
else
    test_fail "CLI net list" "Command failed"
    cat /tmp/netlist.out
fi

# Check for Backbone network
if grep -q "Backbone" /tmp/netlist.out; then
    test_pass "Backbone network found in network list"
else
    test_fail "Backbone network" "Not found in network list"
fi

# Check for KelVPN network
if grep -q "KelVPN" /tmp/netlist.out; then
    test_pass "KelVPN network found in network list"
else
    test_fail "KelVPN network" "Not found in network list"
fi

# =============================================================================
# TEST SECTION 7: NETWORK CONNECTIVITY
# =============================================================================
test_section "7. Network Connectivity"

# Wait for networks to initialize (up to 2 minutes)
log "Waiting for networks to initialize (up to 120 seconds)..."
sleep 30

# Check Backbone status
if /opt/cellframe-node/bin/cellframe-node-cli net -net Backbone get status >/tmp/backbone-status.out 2>&1; then
    test_pass "Backbone status query successful"
    BACKBONE_STATUS=$(cat /tmp/backbone-status.out)
    test_info "Backbone status: $BACKBONE_STATUS"
    
    # Check if online or syncing
    if echo "$BACKBONE_STATUS" | grep -q "NET_STATE_ONLINE\|NET_STATE_SYNC"; then
        test_pass "Backbone network is online or syncing"
    else
        test_warn "Backbone state" "Network not yet online (may need more time)"
    fi
else
    test_warn "Backbone status" "Status query failed"
    cat /tmp/backbone-status.out
fi

# Check KelVPN status
if /opt/cellframe-node/bin/cellframe-node-cli net -net KelVPN get status >/tmp/kelvpn-status.out 2>&1; then
    test_pass "KelVPN status query successful"
    KELVPN_STATUS=$(cat /tmp/kelvpn-status.out)
    test_info "KelVPN status: $KELVPN_STATUS"
    
    # Check if online or syncing
    if echo "$KELVPN_STATUS" | grep -q "NET_STATE_ONLINE\|NET_STATE_SYNC"; then
        test_pass "KelVPN network is online or syncing"
    else
        test_warn "KelVPN state" "Network not yet online (may need more time)"
    fi
else
    test_warn "KelVPN status" "Status query failed"
    cat /tmp/kelvpn-status.out
fi

# Check node connections
if /opt/cellframe-node/bin/cellframe-node-cli node connections >/tmp/connections.out 2>&1; then
    test_pass "Node connections command works"
    CONNECTION_COUNT=$(cat /tmp/connections.out | grep -c "Link\|connection" || echo "0")
    test_info "Active connections: $CONNECTION_COUNT"
else
    test_warn "Node connections" "Command failed"
fi

# =============================================================================
# TEST SECTION 8: WALLET FUNCTIONALITY
# =============================================================================
test_section "8. Wallet Functionality"

# Test wallet list
if /opt/cellframe-node/bin/cellframe-node-cli wallet list >/tmp/wallet-list.out 2>&1; then
    test_pass "Wallet list command works"
else
    test_fail "Wallet list" "Command failed"
    cat /tmp/wallet-list.out
fi

# Test wallet creation
TEST_WALLET="qa_test_wallet"
if /opt/cellframe-node/bin/cellframe-node-cli wallet new -w $TEST_WALLET >/tmp/wallet-new.out 2>&1; then
    test_pass "Wallet creation successful"
    cat /tmp/wallet-new.out
else
    test_fail "Wallet creation" "Failed to create test wallet"
    cat /tmp/wallet-new.out
fi

# Test wallet info
if /opt/cellframe-node/bin/cellframe-node-cli wallet info -w $TEST_WALLET -net Backbone >/tmp/wallet-info.out 2>&1; then
    test_pass "Wallet info command works"
    WALLET_ADDR=$(grep "addr:" /tmp/wallet-info.out | awk '{print $2}')
    test_info "Wallet address: $WALLET_ADDR"
else
    test_warn "Wallet info" "Command failed (network may not be ready)"
    cat /tmp/wallet-info.out
fi

# =============================================================================
# TEST SECTION 9: RESOURCE USAGE
# =============================================================================
test_section "9. Resource Usage"

# Check memory usage
if pgrep -f cellframe-node >/dev/null; then
    MEMORY_KB=$(ps aux | grep cellframe-node | grep -v grep | awk '{print $6}')
    MEMORY_MB=$((MEMORY_KB / 1024))
    
    if [ $MEMORY_MB -lt 2048 ]; then
        test_pass "Memory usage acceptable: ${MEMORY_MB}MB"
    else
        test_warn "Memory usage" "High memory usage: ${MEMORY_MB}MB"
    fi
else
    test_fail "Memory check" "Process not running"
fi

# Check CPU usage (average over 5 seconds)
if pgrep -f cellframe-node >/dev/null; then
    CPU_USAGE=$(ps aux | grep cellframe-node | grep -v grep | awk '{print $3}')
    test_info "CPU usage: ${CPU_USAGE}%"
    
    # During initial sync, CPU can be high, so we're lenient
    if (( $(echo "$CPU_USAGE < 80" | bc -l) )); then
        test_pass "CPU usage acceptable: ${CPU_USAGE}%"
    else
        test_warn "CPU usage" "High CPU usage: ${CPU_USAGE}% (may be normal during sync)"
    fi
else
    test_fail "CPU check" "Process not running"
fi

# =============================================================================
# TEST SECTION 10: LOG ANALYSIS
# =============================================================================
test_section "10. Log Analysis"

LOG_FILE="/opt/cellframe-node/var/log/cellframe-node.log"

if [ -f "$LOG_FILE" ]; then
    # Check for critical errors
    CRITICAL_COUNT=$(grep -c "\[L_CRITICAL\]" "$LOG_FILE" 2>/dev/null || echo "0")
    if [ "$CRITICAL_COUNT" -eq 0 ]; then
        test_pass "No CRITICAL errors in log"
    else
        test_fail "Critical errors" "Found $CRITICAL_COUNT CRITICAL errors"
        grep "\[L_CRITICAL\]" "$LOG_FILE" | tail -5
    fi
    
    # Check for error patterns
    ERROR_COUNT=$(grep -c "\[L_ERROR\]" "$LOG_FILE" 2>/dev/null || echo "0")
    test_info "ERROR messages in log: $ERROR_COUNT"
    if [ "$ERROR_COUNT" -lt 10 ]; then
        test_pass "Acceptable number of ERROR messages"
    else
        test_warn "Error count" "High number of errors: $ERROR_COUNT"
    fi
    
    # Check for version message
    if grep -q "CellFrame Node version" "$LOG_FILE"; then
        VERSION_LINE=$(grep "CellFrame Node version" "$LOG_FILE" | tail -1)
        test_pass "Version logged: $VERSION_LINE"
    else
        test_warn "Version log" "Version string not found in log"
    fi
    
    # Check for network initialization
    if grep -q "Network.*initialized" "$LOG_FILE"; then
        test_pass "Networks initialization logged"
    else
        test_warn "Network init log" "Network initialization messages not found"
    fi
    
    # Show last 20 log lines
    test_info "Last 20 log lines:"
    tail -20 "$LOG_FILE"
else
    test_fail "Log file" "Log file not found"
fi

# =============================================================================
# TEST SECTION 11: CONFIGURATION VERIFICATION
# =============================================================================
test_section "11. Configuration Verification"

# Check main config parameters
CONFIG_FILE="/opt/cellframe-node/etc/cellframe-node.cfg"

if [ -f "$CONFIG_FILE" ]; then
    test_pass "Main configuration file accessible"
    
    # Check debug_mode
    DEBUG_MODE=$(grep "^debug_mode=" "$CONFIG_FILE" | cut -d= -f2)
    test_info "debug_mode: $DEBUG_MODE"
    
    # Check auto_online
    AUTO_ONLINE=$(grep "^auto_online=" "$CONFIG_FILE" | cut -d= -f2)
    test_info "auto_online: $AUTO_ONLINE"
    
    # Check server enabled
    SERVER_ENABLED=$(grep "^enabled=" "$CONFIG_FILE" | head -1 | cut -d= -f2)
    test_info "server.enabled: $SERVER_ENABLED"
    
else
    test_fail "Config file" "Cannot read configuration"
fi

# Use config tool to list networks
if /opt/cellframe-node/bin/cellframe-node-config -e net_list on >/tmp/netlist-config.out 2>&1; then
    test_pass "Config tool net_list command works"
    test_info "Active networks:"
    cat /tmp/netlist-config.out
else
    test_warn "Config tool" "net_list command failed"
fi

# =============================================================================
# FINAL RESULTS
# =============================================================================
echo ""
echo -e "${BLUE}===========================================================${NC}"
echo -e "${BLUE}  TEST RESULTS SUMMARY${NC}"
echo -e "${BLUE}===========================================================${NC}"
echo ""

echo -e "Total tests:  ${TESTS_TOTAL}"
echo -e "${GREEN}Passed:       ${TESTS_PASSED}${NC}"
echo -e "${RED}Failed:       ${TESTS_FAILED}${NC}"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ ALL TESTS PASSED${NC}"
    echo ""
    echo "The cellframe-node installation meets all QA specifications."
    echo "Reference: QA_SPECIFICATION_LINUX.md"
    exit 0
else
    echo -e "${RED}✗ SOME TESTS FAILED${NC}"
    echo ""
    echo "The cellframe-node installation does not meet all QA specifications."
    echo "Please review the failures above."
    echo "Reference: QA_SPECIFICATION_LINUX.md"
    exit 1
fi

