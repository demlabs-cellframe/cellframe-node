#!/bin/bash

# Test script for defect management system
# Демонстрационный скрипт для тестирования системы создания дефектов

set -euo pipefail

echo "🔬 Testing Defect Management System"
echo "==================================="

# Load configuration
if [[ -f "redmine_config.env" ]]; then
    source redmine_config.env
    echo "✅ Redmine configuration loaded"
else
    echo "⚠️ Redmine configuration file not found - using defaults"
fi

# Check dependencies
echo ""
echo "🔍 Checking dependencies..."

if [[ ! -f "./allurectl" ]]; then
    echo "❌ allurectl not found"
    exit 1
else
    echo "✅ allurectl found"
fi

if [[ ! -f "./defect_manager.sh" ]]; then
    echo "❌ defect_manager.sh not found"
    exit 1
else
    echo "✅ defect_manager.sh found"
fi

if [[ ! -f "./launch_manager.sh" ]]; then
    echo "❌ launch_manager.sh not found"
    exit 1
else
    echo "✅ launch_manager.sh found"
fi

# Test Redmine connection (if configured)
echo ""
echo "🔗 Testing Redmine connection..."
if [[ -n "${REDMINE_API_KEY:-}" && -n "${REDMINE_URL:-}" ]]; then
    ./defect_manager.sh test-redmine
else
    echo "⚠️ Redmine not configured - skipping connection test"
    echo "   Set REDMINE_URL and REDMINE_API_KEY in redmine_config.env"
fi

# Test TestOps connection
echo ""
echo "🔗 Testing TestOps connection..."
if ./allurectl launch list -e "${ALLURE_ENDPOINT}" -t "${ALLURE_TOKEN}" --project-id "${ALLURE_PROJECT_ID}" --output json > /dev/null 2>&1; then
    echo "✅ TestOps connection OK"
else
    echo "❌ TestOps connection failed"
    exit 1
fi

# Test defect analysis
echo ""
echo "🧠 Testing defect analysis..."
echo "Analyzing sample test failure..."

echo "Running defect analysis..."
SAMPLE_ANALYSIS=$(./defect_manager.sh analyze \
    "test_cellframe_node_connection" \
    "Connection timeout after 30 seconds" \
    "ConnectionError: Failed to connect to cellframe-node at localhost:8080" 2>/dev/null | tail -n +2)

echo "Sample analysis result:"
if [[ -n "${SAMPLE_ANALYSIS}" ]]; then
    echo "${SAMPLE_ANALYSIS}" | jq '.'
else
    echo "Failed to get analysis result"
fi

# List recent launches with failed tests
echo ""
echo "📊 Recent TestOps launches with failures:"
./allurectl launch list \
    -e "${ALLURE_ENDPOINT}" \
    -t "${ALLURE_TOKEN}" \
    --project-id "${ALLURE_PROJECT_ID}" \
    --format "ID,Name,Failed,Broken" \
    | head -5 | awk 'NR==1 || $3>0 || $4>0'

# List recent defects (if Redmine configured)
echo ""
echo "🐛 Recent defects from Redmine:"
if [[ -n "${REDMINE_API_KEY:-}" && -n "${REDMINE_URL:-}" ]]; then
    ./defect_manager.sh list 5 || echo "No defects found or Redmine not accessible"
else
    echo "⚠️ Redmine not configured - cannot list defects"
fi

# Get defect statistics (if Redmine configured)
echo ""
echo "📈 Defect statistics:"
if [[ -n "${REDMINE_API_KEY:-}" && -n "${REDMINE_URL:-}" ]]; then
    ./defect_manager.sh stats 7 || echo "Cannot get statistics - Redmine not accessible"
else
    echo "⚠️ Redmine not configured - cannot get statistics"
fi

# Demo: Simulate defect creation workflow
echo ""
echo "🎭 Demo: Simulating defect creation workflow..."

# Find a launch with failed tests
FAILED_LAUNCH_ID=$(./allurectl launch list \
    -e "${ALLURE_ENDPOINT}" \
    -t "${ALLURE_TOKEN}" \
    --project-id "${ALLURE_PROJECT_ID}" \
    --output json | jq -r '.[] | select(.statistic[]?.status=="failed" and .statistic[]?.count > 0) | .id' | head -1)

if [[ -n "${FAILED_LAUNCH_ID}" && "${FAILED_LAUNCH_ID}" != "null" ]]; then
    echo "Found launch with failed tests: ${FAILED_LAUNCH_ID}"
    
    # Simulate defect processing
    echo ""
    echo "🔄 Simulating defect processing..."
    echo "Would process defects for:"
    echo "  Launch ID: ${FAILED_LAUNCH_ID}"
    echo "  Launch Name: Demo Defect Processing"
    echo "  Node Version: demo-v1.0"
    echo "  Commit: abc123"
    echo "  Pipeline URL: https://gitlab.demlabs.net/cellframe/cellframe-node/-/pipelines/demo"
    
    if [[ -n "${REDMINE_API_KEY:-}" ]]; then
        echo ""
        echo "⚠️ Note: Actual defect creation is disabled in demo mode"
        echo "   To enable, run: ./defect_manager.sh process ${FAILED_LAUNCH_ID} ..."
    else
        echo ""
        echo "⚠️ Redmine not configured - defect creation would be skipped"
    fi
else
    echo "No launches with failed tests found for demo"
fi

echo ""
echo "🎉 Defect Management System Test Complete!"
echo ""
echo "📋 System capabilities:"
echo "✅ Automatic defect analysis and categorization"
echo "✅ Redmine integration for defect creation"
echo "✅ TestOps integration for test result analysis"
echo "✅ Configurable defect priorities and categories"
echo "✅ Statistics and reporting"
echo ""
echo "🔧 Configuration needed for full functionality:"
echo "1. Set REDMINE_URL in redmine_config.env"
echo "2. Set REDMINE_API_KEY in redmine_config.env"
echo "3. Set REDMINE_PROJECT_ID in redmine_config.env"
echo "4. Configure Redmine project with TestOps plugin (optional)"
echo ""
echo "🔗 Useful links:"
echo "  TestOps: ${ALLURE_ENDPOINT}"
echo "  Redmine: ${REDMINE_URL:-'Not configured'}"
echo "  Documentation: https://docs.qatools.ru/integrations/issue-trackers/redmine"
