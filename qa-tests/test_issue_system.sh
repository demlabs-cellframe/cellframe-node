#!/bin/bash

# Test script for issue management system
# Демонстрационный скрипт для тестирования системы создания issues

set -euo pipefail

echo "🧪 Testing Issue Management System"
echo "=================================="

# Load configuration
if [[ -f "issue_config.env" ]]; then
    source issue_config.env
    echo "✅ Configuration loaded"
else
    echo "⚠️ Configuration file not found - using defaults"
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

if [[ ! -f "./issue_manager.sh" ]]; then
    echo "❌ issue_manager.sh not found"
    exit 1
else
    echo "✅ issue_manager.sh found"
fi

if [[ ! -f "./launch_manager.sh" ]]; then
    echo "❌ launch_manager.sh not found"
    exit 1
else
    echo "✅ launch_manager.sh found"
fi

# Test GitLab connection (if configured)
echo ""
echo "🔗 Testing GitLab connection..."
if [[ -n "${GITLAB_TOKEN:-}" && -n "${GITLAB_PROJECT_ID:-}" ]]; then
    ./issue_manager.sh test-gitlab
else
    echo "⚠️ GitLab not configured - skipping connection test"
    echo "   Set GITLAB_TOKEN and GITLAB_PROJECT_ID in issue_config.env"
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

# List recent launches
echo ""
echo "📊 Recent TestOps launches:"
./allurectl launch list \
    -e "${ALLURE_ENDPOINT}" \
    -t "${ALLURE_TOKEN}" \
    --project-id "${ALLURE_PROJECT_ID}" \
    --format "ID,Name,Passed,Failed,Broken" \
    | head -5

# List recent issues (if GitLab configured)
echo ""
echo "🐛 Recent QA issues:"
if [[ -n "${GITLAB_TOKEN:-}" && -n "${GITLAB_PROJECT_ID:-}" ]]; then
    ./issue_manager.sh list 5 || echo "No issues found or GitLab not accessible"
else
    echo "⚠️ GitLab not configured - cannot list issues"
fi

# Demo: Create a test launch and simulate issue creation
echo ""
echo "🎭 Demo: Simulating issue creation workflow..."

# Create a demo launch
DEMO_LAUNCH_NAME="Demo Issue Test - $(date +%H:%M:%S)"
echo "Creating demo launch: ${DEMO_LAUNCH_NAME}"

DEMO_LAUNCH_ID=$(./launch_manager.sh create "${DEMO_LAUNCH_NAME}" "demo,test,issue-system")
if [[ -n "${DEMO_LAUNCH_ID}" ]]; then
    echo "✅ Demo launch created: ${DEMO_LAUNCH_ID}"
    
    # Simulate processing issues for a failed test scenario
    echo ""
    echo "🔄 Simulating issue processing for failed tests..."
    
    # Note: In a real scenario, this would be called after actual test results are uploaded
    # For demo purposes, we'll just show what would happen
    echo "Would process issues for:"
    echo "  Launch ID: ${DEMO_LAUNCH_ID}"
    echo "  Launch Name: ${DEMO_LAUNCH_NAME}"
    echo "  Node Version: demo-v1.0"
    echo "  Commit: abc123"
    echo "  Pipeline URL: https://gitlab.demlabs.net/cellframe/cellframe-node/-/pipelines/demo"
    
    # Clean up demo launch
    echo ""
    echo "🧹 Cleaning up demo launch..."
    ./launch_manager.sh close "${DEMO_LAUNCH_ID}"
    echo "✅ Demo launch closed"
else
    echo "❌ Failed to create demo launch"
fi

echo ""
echo "🎉 Issue Management System Test Complete!"
echo ""
echo "📋 Next steps:"
echo "1. Configure GitLab token in issue_config.env"
echo "2. Test with real failed tests"
echo "3. Monitor automatic issue creation in GitLab"
echo "4. Verify issue closure when tests pass"
echo ""
echo "🔗 Useful links:"
echo "  TestOps: ${ALLURE_ENDPOINT}"
echo "  GitLab: ${GITLAB_URL}/cellframe/cellframe-node/-/issues"
