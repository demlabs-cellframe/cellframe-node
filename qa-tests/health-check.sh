#!/bin/bash
# Cellframe Node Health Check Script
# Purpose: Quick health check for monitoring (used by Docker HEALTHCHECK)
# Reference: QA_SPECIFICATION_LINUX.md Section 11.4

set -e

# Exit codes
EXIT_OK=0
EXIT_FAIL=1

# Check 1: Process running
if ! pgrep -f cellframe-node > /dev/null; then
    echo "FAIL: cellframe-node process not running"
    exit $EXIT_FAIL
fi

# Check 2: Service active
if ! systemctl is-active --quiet cellframe-node 2>/dev/null; then
    echo "FAIL: cellframe-node service not active"
    exit $EXIT_FAIL
fi

# Check 3: CLI responds
if ! timeout 5 /opt/cellframe-node/bin/cellframe-node-cli version > /dev/null 2>&1; then
    echo "FAIL: CLI not responding within 5 seconds"
    exit $EXIT_FAIL
fi

# Check 4: At least one network present
if ! /opt/cellframe-node/bin/cellframe-node-cli net list > /dev/null 2>&1; then
    echo "FAIL: Cannot query network list"
    exit $EXIT_FAIL
fi

# Check 5: Log file not too large (>1GB indicates problem)
LOG_SIZE=$(stat -c%s "/opt/cellframe-node/var/log/cellframe-node.log" 2>/dev/null || echo "0")
if [ "$LOG_SIZE" -gt 1073741824 ]; then
    echo "WARN: Log file very large (>1GB)"
    # Don't fail, just warn
fi

# Check 6: No recent CRITICAL errors
RECENT_CRITICAL=$(tail -100 /opt/cellframe-node/var/log/cellframe-node.log 2>/dev/null | grep -c "\[L_CRITICAL\]" || echo "0")
if [ "$RECENT_CRITICAL" -gt 0 ]; then
    echo "FAIL: Found CRITICAL errors in recent log"
    exit $EXIT_FAIL
fi

# All checks passed
echo "OK: cellframe-node is healthy"
exit $EXIT_OK

