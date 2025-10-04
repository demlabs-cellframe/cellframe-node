#!/bin/bash
# Allure Results Generator for Cellframe Node QA Tests
# Converts test results to Allure JSON format

ALLURE_RESULTS_DIR="${ALLURE_RESULTS_DIR:-./allure-results}"
mkdir -p "$ALLURE_RESULTS_DIR"

# Generate UUID
generate_uuid() {
    cat /proc/sys/kernel/random/uuid 2>/dev/null || python3 -c "import uuid; print(uuid.uuid4())"
}

# Get current timestamp in milliseconds
get_timestamp_ms() {
    date +%s%3N 2>/dev/null || echo $(($(date +%s) * 1000))
}

# Test suite start
TEST_SUITE_UUID=$(generate_uuid)
TEST_START_TIME=$(get_timestamp_ms)

# Create test result container
create_test_result() {
    local name="$1"
    local status="$2"  # passed, failed, broken, skipped
    local description="$3"
    local error_message="$4"
    local duration="${5:-0}"
    local labels="$6"
    
    local uuid=$(generate_uuid)
    local start_time=$TEST_START_TIME
    local stop_time=$((start_time + duration))
    
    local result_file="$ALLURE_RESULTS_DIR/${uuid}-result.json"
    
    cat > "$result_file" << EOF
{
  "uuid": "$uuid",
  "historyId": "$(echo -n "$name" | md5sum | cut -d' ' -f1)",
  "name": "$name",
  "status": "$status",
  "stage": "finished",
  "description": "$description",
  "start": $start_time,
  "stop": $stop_time,
  "labels": [
    {"name": "framework", "value": "bash"},
    {"name": "language", "value": "shell"},
    {"name": "host", "value": "$(hostname)"},
    {"name": "thread", "value": "$$"},
    $labels
    {"name": "package", "value": "cellframe-node-qa"}
  ],
  "links": []
EOF

    if [ -n "$error_message" ]; then
        cat >> "$result_file" << EOF
,
  "statusDetails": {
    "message": "$error_message",
    "trace": ""
  }
EOF
    fi

    cat >> "$result_file" << EOF
}
EOF
}

# Create test container
create_test_container() {
    local name="$1"
    local uuid="${2:-$(generate_uuid)}"
    local start_time="${3:-$TEST_START_TIME}"
    
    local container_file="$ALLURE_RESULTS_DIR/${uuid}-container.json"
    
    cat > "$container_file" << EOF
{
  "uuid": "$uuid",
  "name": "$name",
  "children": [],
  "befores": [],
  "afters": [],
  "start": $start_time,
  "stop": $(get_timestamp_ms)
}
EOF
}

# Create environment properties
create_environment() {
    local env_file="$ALLURE_RESULTS_DIR/environment.properties"
    
    cat > "$env_file" << EOF
Node.Version=$(cat /etc/os-release 2>/dev/null | grep PRETTY_NAME | cut -d'"' -f2 || echo "Unknown")
Docker.Image=$(hostname)
Test.Framework=Cellframe Node QA Suite
Test.Type=Functional
Build.Hash=$(grep BUILD_HASH /opt/cellframe-node/bin/cellframe-node 2>/dev/null | head -1 | cut -d'"' -f2 || echo "Unknown")
Python.Version=$(/opt/cellframe-node/python/bin/python3 --version 2>/dev/null || echo "Not installed")
EOF
}

# Create categories for test classification
create_categories() {
    local categories_file="$ALLURE_RESULTS_DIR/categories.json"
    
    cat > "$categories_file" << 'EOF'
[
  {
    "name": "Installation Issues",
    "matchedStatuses": ["failed"],
    "messageRegex": ".*[Ii]nstallation.*"
  },
  {
    "name": "Network Issues",
    "matchedStatuses": ["failed"],
    "messageRegex": ".*[Nn]etwork.*|.*[Cc]onnection.*"
  },
  {
    "name": "CLI Issues",
    "matchedStatuses": ["failed"],
    "messageRegex": ".*CLI.*|.*command.*"
  },
  {
    "name": "Wallet Issues",
    "matchedStatuses": ["failed"],
    "messageRegex": ".*[Ww]allet.*"
  },
  {
    "name": "Configuration Issues",
    "matchedStatuses": ["failed"],
    "messageRegex": ".*[Cc]onfig.*"
  },
  {
    "name": "Resource Issues",
    "matchedStatuses": ["failed"],
    "messageRegex": ".*[Mm]emory.*|.*CPU.*"
  },
  {
    "name": "Non-critical Warnings",
    "matchedStatuses": ["passed"],
    "messageRegex": ".*[Ww]arning.*"
  }
]
EOF
}

# Export functions for use in test scripts
export -f create_test_result
export -f create_test_container
export -f create_environment
export -f create_categories
export -f generate_uuid
export -f get_timestamp_ms

# If run directly, create environment and categories
if [ "${BASH_SOURCE[0]}" -eq "$0" ]; then
    create_environment
    create_categories
    echo "Allure results directory initialized: $ALLURE_RESULTS_DIR"
fi

