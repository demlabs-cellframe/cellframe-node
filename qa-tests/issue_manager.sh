#!/bin/bash

# Allure TestOps Issue Manager
# Автоматическое создание и управление issues для упавших тестов

set -euo pipefail

# Configuration
GITLAB_URL="${GITLAB_URL:-https://gitlab.demlabs.net}"
GITLAB_PROJECT_ID="${GITLAB_PROJECT_ID:-}"
GITLAB_TOKEN="${GITLAB_TOKEN:-}"
ALLURE_ENDPOINT="${ALLURE_ENDPOINT:-http://178.49.151.230:8080}"
ALLURE_TOKEN="${ALLURE_TOKEN:-c9d45bd4-394a-4e6c-aab2-f7bce2b5be44}"
ALLURE_PROJECT_ID="${ALLURE_PROJECT_ID:-1}"
ALLURECTL_PATH="./allurectl"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_debug() {
    echo -e "${PURPLE}[DEBUG]${NC} $1"
}

# Function to get failed tests from launch
get_failed_tests() {
    local launch_id="$1"
    
    log_info "Getting failed tests from launch ID: ${launch_id}"
    
    # Get launch results
    local launch_data
    launch_data=$("${ALLURECTL_PATH}" launch get "${launch_id}" \
        -e "${ALLURE_ENDPOINT}" \
        -t "${ALLURE_TOKEN}" \
        --output json 2>/dev/null || echo "[]")
    
    if [[ "${launch_data}" == "[]" ]]; then
        log_error "Failed to get launch data"
        return 1
    fi
    
    # Extract failed test count
    local failed_count
    failed_count=$(echo "${launch_data}" | jq -r '.[0].statistic[]? | select(.status=="failed") | .count // 0')
    
    if [[ "${failed_count}" -gt 0 ]]; then
        log_warning "Found ${failed_count} failed tests in launch ${launch_id}"
        echo "${failed_count}"
        return 0
    else
        log_info "No failed tests found in launch ${launch_id}"
        echo "0"
        return 0
    fi
}

# Function to create GitLab issue
create_gitlab_issue() {
    local title="$1"
    local description="$2"
    local labels="$3"
    
    if [[ -z "${GITLAB_TOKEN}" || -z "${GITLAB_PROJECT_ID}" ]]; then
        log_warning "GitLab integration not configured (missing GITLAB_TOKEN or GITLAB_PROJECT_ID)"
        log_info "Would create issue: ${title}"
        return 0
    fi
    
    log_info "Creating GitLab issue: ${title}"
    
    # Prepare JSON payload
    local json_payload
    json_payload=$(jq -n \
        --arg title "${title}" \
        --arg description "${description}" \
        --arg labels "${labels}" \
        '{
            title: $title,
            description: $description,
            labels: $labels
        }')
    
    # Create issue via GitLab API
    local response
    response=$(curl -s -X POST \
        "${GITLAB_URL}/api/v4/projects/${GITLAB_PROJECT_ID}/issues" \
        -H "PRIVATE-TOKEN: ${GITLAB_TOKEN}" \
        -H "Content-Type: application/json" \
        -d "${json_payload}" || echo "{}")
    
    # Check if issue was created
    local issue_id
    issue_id=$(echo "${response}" | jq -r '.id // empty')
    
    if [[ -n "${issue_id}" ]]; then
        local issue_url
        issue_url=$(echo "${response}" | jq -r '.web_url // empty')
        log_success "GitLab issue created: ${issue_url}"
        echo "${issue_id}"
        return 0
    else
        log_error "Failed to create GitLab issue"
        log_debug "Response: ${response}"
        return 1
    fi
}

# Function to check if issue already exists
check_existing_issue() {
    local search_title="$1"
    
    if [[ -z "${GITLAB_TOKEN}" || -z "${GITLAB_PROJECT_ID}" ]]; then
        return 1
    fi
    
    log_debug "Checking for existing issue with title: ${search_title}"
    
    # Search for existing issues
    local response
    response=$(curl -s -G \
        "${GITLAB_URL}/api/v4/projects/${GITLAB_PROJECT_ID}/issues" \
        -H "PRIVATE-TOKEN: ${GITLAB_TOKEN}" \
        --data-urlencode "search=${search_title}" \
        --data-urlencode "state=opened" || echo "[]")
    
    # Check if any issues found
    local issue_count
    issue_count=$(echo "${response}" | jq '. | length')
    
    if [[ "${issue_count}" -gt 0 ]]; then
        local existing_issue_url
        existing_issue_url=$(echo "${response}" | jq -r '.[0].web_url // empty')
        log_info "Found existing issue: ${existing_issue_url}"
        return 0
    else
        log_debug "No existing issue found"
        return 1
    fi
}

# Function to generate issue description
generate_issue_description() {
    local launch_id="$1"
    local launch_name="$2"
    local failed_count="$3"
    local node_version="$4"
    local commit_hash="$5"
    local pipeline_url="$6"
    
    cat << EOF
## 🐛 Автоматически созданная задача для упавших тестов

### 📊 Информация о запуске
- **Launch ID**: ${launch_id}
- **Launch Name**: ${launch_name}
- **Failed Tests**: ${failed_count}
- **Node Version**: ${node_version}
- **Commit**: ${commit_hash}
- **Pipeline**: ${pipeline_url}

### 🔗 Ссылки
- **TestOps Launch**: ${ALLURE_ENDPOINT}/launch/${launch_id}
- **TestOps Project**: ${ALLURE_ENDPOINT}/project/${ALLURE_PROJECT_ID}
- **GitLab Pipeline**: ${pipeline_url}

### 📋 Действия для исправления
1. Проверить детали упавших тестов в TestOps
2. Проанализировать логи тестов
3. Определить причину падения
4. Исправить код или тесты
5. Запустить тесты повторно

### 🏷️ Метки
- \`qa-failure\`
- \`automated-issue\`
- \`testing\`

---
*Эта задача создана автоматически системой QA при обнаружении упавших тестов.*
*Дата создания: $(date '+%d.%m.%Y %H:%M:%S')*
EOF
}

# Function to process failed tests and create issues
process_failed_tests() {
    local launch_id="$1"
    local launch_name="${2:-Unknown Launch}"
    local node_version="${3:-unknown}"
    local commit_hash="${4:-unknown}"
    local pipeline_url="${5:-}"
    
    log_info "Processing failed tests for launch ${launch_id}"
    
    # Get failed test count
    local failed_count
    failed_count=$(get_failed_tests "${launch_id}")
    
    if [[ "${failed_count}" == "0" ]]; then
        log_success "No failed tests - no issues to create"
        return 0
    fi
    
    # Generate issue title
    local issue_title="QA: ${failed_count} tests failed in ${node_version} (${commit_hash})"
    
    # Check if similar issue already exists
    if check_existing_issue "${issue_title}"; then
        log_info "Similar issue already exists - skipping creation"
        return 0
    fi
    
    # Generate issue description
    local issue_description
    issue_description=$(generate_issue_description \
        "${launch_id}" \
        "${launch_name}" \
        "${failed_count}" \
        "${node_version}" \
        "${commit_hash}" \
        "${pipeline_url}")
    
    # Create GitLab issue
    local issue_id
    if issue_id=$(create_gitlab_issue \
        "${issue_title}" \
        "${issue_description}" \
        "qa-failure,automated-issue,testing"); then
        
        log_success "Issue created successfully with ID: ${issue_id}"
        
        # Add issue to TestOps launch (if integration configured)
        if add_issue_to_testops "${launch_id}" "${issue_id}"; then
            log_success "Issue linked to TestOps launch"
        else
            log_warning "Failed to link issue to TestOps launch"
        fi
        
        return 0
    else
        log_error "Failed to create issue"
        return 1
    fi
}

# Function to add issue to TestOps launch
add_issue_to_testops() {
    local launch_id="$1"
    local issue_id="$2"
    
    # Note: This requires TestOps integration setup
    # For now, we'll just log the action
    log_info "Adding issue ${issue_id} to TestOps launch ${launch_id}"
    log_warning "TestOps integration not fully configured yet"
    
    # TODO: Implement when TestOps integration is set up
    # "${ALLURECTL_PATH}" launch add-issue \
    #     -e "${ALLURE_ENDPOINT}" \
    #     -t "${ALLURE_TOKEN}" \
    #     --launch-id "${launch_id}" \
    #     --issue-keys "${issue_id}" \
    #     --integration-id 1
    
    return 0
}

# Function to close issues when tests pass
close_resolved_issues() {
    local launch_id="$1"
    local node_version="${2:-unknown}"
    
    log_info "Checking if any issues can be closed for ${node_version}"
    
    if [[ -z "${GITLAB_TOKEN}" || -z "${GITLAB_PROJECT_ID}" ]]; then
        log_warning "GitLab integration not configured - cannot close issues"
        return 0
    fi
    
    # Get failed test count
    local failed_count
    failed_count=$(get_failed_tests "${launch_id}")
    
    if [[ "${failed_count}" == "0" ]]; then
        log_info "All tests passed - looking for issues to close"
        
        # Search for open QA issues for this node version
        local response
        response=$(curl -s -G \
            "${GITLAB_URL}/api/v4/projects/${GITLAB_PROJECT_ID}/issues" \
            -H "PRIVATE-TOKEN: ${GITLAB_TOKEN}" \
            --data-urlencode "search=QA: tests failed in ${node_version}" \
            --data-urlencode "state=opened" \
            --data-urlencode "labels=qa-failure,automated-issue" || echo "[]")
        
        local issue_count
        issue_count=$(echo "${response}" | jq '. | length')
        
        if [[ "${issue_count}" -gt 0 ]]; then
            log_info "Found ${issue_count} issues that can be closed"
            
            # Close each issue
            echo "${response}" | jq -r '.[].iid' | while read -r issue_iid; do
                if [[ -n "${issue_iid}" ]]; then
                    close_issue "${issue_iid}" "${launch_id}"
                fi
            done
        else
            log_info "No issues found to close"
        fi
    else
        log_info "Tests still failing (${failed_count}) - not closing issues"
    fi
}

# Function to close a specific issue
close_issue() {
    local issue_iid="$1"
    local launch_id="$2"
    
    log_info "Closing issue #${issue_iid}"
    
    local close_comment="🎉 **Автоматическое закрытие**

Все тесты прошли успешно в launch ${launch_id}.
Проблема решена автоматически.

**TestOps**: ${ALLURE_ENDPOINT}/launch/${launch_id}

*Закрыто автоматически системой QA: $(date '+%d.%m.%Y %H:%M:%S')*"
    
    # Add comment and close issue
    local json_payload
    json_payload=$(jq -n \
        --arg body "${close_comment}" \
        '{body: $body}')
    
    # Add comment
    curl -s -X POST \
        "${GITLAB_URL}/api/v4/projects/${GITLAB_PROJECT_ID}/issues/${issue_iid}/notes" \
        -H "PRIVATE-TOKEN: ${GITLAB_TOKEN}" \
        -H "Content-Type: application/json" \
        -d "${json_payload}" > /dev/null
    
    # Close issue
    json_payload=$(jq -n '{state_event: "close"}')
    
    local response
    response=$(curl -s -X PUT \
        "${GITLAB_URL}/api/v4/projects/${GITLAB_PROJECT_ID}/issues/${issue_iid}" \
        -H "PRIVATE-TOKEN: ${GITLAB_TOKEN}" \
        -H "Content-Type: application/json" \
        -d "${json_payload}")
    
    local state
    state=$(echo "${response}" | jq -r '.state // empty')
    
    if [[ "${state}" == "closed" ]]; then
        log_success "Issue #${issue_iid} closed successfully"
    else
        log_error "Failed to close issue #${issue_iid}"
    fi
}

# Function to list recent issues
list_recent_issues() {
    local limit="${1:-10}"
    
    if [[ -z "${GITLAB_TOKEN}" || -z "${GITLAB_PROJECT_ID}" ]]; then
        log_error "GitLab integration not configured"
        return 1
    fi
    
    log_info "Listing recent QA issues (limit: ${limit})"
    
    local response
    response=$(curl -s -G \
        "${GITLAB_URL}/api/v4/projects/${GITLAB_PROJECT_ID}/issues" \
        -H "PRIVATE-TOKEN: ${GITLAB_TOKEN}" \
        --data-urlencode "labels=qa-failure,automated-issue" \
        --data-urlencode "per_page=${limit}" \
        --data-urlencode "order_by=created_at" \
        --data-urlencode "sort=desc" || echo "[]")
    
    echo "${response}" | jq -r '.[] | "#\(.iid) - \(.title) (\(.state)) - \(.web_url)"'
}

# Main function
main() {
    if [[ $# -eq 0 ]]; then
        action="help"
    else
        local action="$1"
        shift
    fi
    
    case "${action}" in
        "process")
            if [[ $# -lt 1 ]]; then
                log_error "Usage: $0 process <launch_id> [launch_name] [node_version] [commit_hash] [pipeline_url]"
                exit 1
            fi
            process_failed_tests "$@"
            ;;
        "close-resolved")
            if [[ $# -lt 1 ]]; then
                log_error "Usage: $0 close-resolved <launch_id> [node_version]"
                exit 1
            fi
            close_resolved_issues "$@"
            ;;
        "list")
            local limit="${1:-10}"
            list_recent_issues "${limit}"
            ;;
        "test-gitlab")
            if [[ -z "${GITLAB_TOKEN}" || -z "${GITLAB_PROJECT_ID}" ]]; then
                log_error "GitLab integration not configured"
                log_info "Set GITLAB_TOKEN and GITLAB_PROJECT_ID environment variables"
                exit 1
            fi
            log_info "Testing GitLab connection..."
            local response
            response=$(curl -s "${GITLAB_URL}/api/v4/projects/${GITLAB_PROJECT_ID}" \
                -H "PRIVATE-TOKEN: ${GITLAB_TOKEN}")
            local project_name
            project_name=$(echo "${response}" | jq -r '.name // "ERROR"')
            if [[ "${project_name}" != "ERROR" ]]; then
                log_success "GitLab connection OK - Project: ${project_name}"
            else
                log_error "GitLab connection failed"
                log_debug "Response: ${response}"
            fi
            ;;
        "help"|*)
            echo "Usage: $0 {process|close-resolved|list|test-gitlab}"
            echo ""
            echo "Commands:"
            echo "  process <launch_id> [name] [version] [commit] [url]  - Process failed tests and create issues"
            echo "  close-resolved <launch_id> [version]                 - Close resolved issues"
            echo "  list [limit]                                         - List recent QA issues"
            echo "  test-gitlab                                          - Test GitLab connection"
            echo ""
            echo "Environment variables:"
            echo "  GITLAB_URL         - GitLab instance URL (default: https://gitlab.demlabs.net)"
            echo "  GITLAB_PROJECT_ID  - GitLab project ID (required)"
            echo "  GITLAB_TOKEN       - GitLab API token (required)"
            exit 1
            ;;
    esac
}

# Check dependencies
if [[ ! -f "${ALLURECTL_PATH}" ]]; then
    log_error "allurectl not found at ${ALLURECTL_PATH}"
    exit 1
fi

if ! command -v jq &> /dev/null; then
    log_error "jq is required but not installed"
    exit 1
fi

if ! command -v curl &> /dev/null; then
    log_error "curl is required but not installed"
    exit 1
fi

# Run main function
main "$@"
