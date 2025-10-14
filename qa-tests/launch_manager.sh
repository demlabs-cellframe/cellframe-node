#!/bin/bash

# Allure TestOps Launch Manager
# Автоматическое управление запусками тестов в TestOps

set -euo pipefail

# Configuration
ALLURE_ENDPOINT="${ALLURE_ENDPOINT:-http://178.49.151.230:8080}"
ALLURE_TOKEN="${ALLURE_TOKEN:-c9d45bd4-394a-4e6c-aab2-f7bce2b5be44}"
ALLURE_PROJECT_ID="${ALLURE_PROJECT_ID:-1}"
ALLURECTL_PATH="./allurectl"
ISSUE_MANAGER_PATH="./issue_manager.sh"
DEFECT_MANAGER_PATH="./defect_manager.sh"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

# Function to create a new launch
create_launch() {
    local launch_name="$1"
    local launch_tags="$2"
    
    log_info "Creating new launch: ${launch_name}"
    log_info "Tags: ${launch_tags}"
    
    local launch_id
    launch_id=$("${ALLURECTL_PATH}" launch create \
        -e "${ALLURE_ENDPOINT}" \
        -t "${ALLURE_TOKEN}" \
        --project-id "${ALLURE_PROJECT_ID}" \
        --launch-name "${launch_name}" \
        --launch-tags "${launch_tags}" \
        --output json | jq -r '.[0].id // empty')
    
    if [[ -n "${launch_id}" ]]; then
        log_success "Launch created with ID: ${launch_id}"
        echo "${launch_id}" > .launch_id
        return 0
    else
        log_error "Failed to create launch"
        return 1
    fi
}

# Function to process issues based on test results
process_issues() {
    local launch_id="$1"
    local launch_name="${2:-Unknown Launch}"
    local node_version="${3:-unknown}"
    local commit_hash="${4:-unknown}"
    local pipeline_url="${5:-}"
    
    # Load issue configuration if available
    if [[ -f "issue_config.env" ]]; then
        source issue_config.env
    fi
    
    # Check if issue manager is available and configured
    if [[ ! -f "${ISSUE_MANAGER_PATH}" ]]; then
        log_warning "Issue manager not found at ${ISSUE_MANAGER_PATH}"
        return 0
    fi
    
    if [[ -z "${GITLAB_TOKEN:-}" ]]; then
        log_warning "GitLab token not configured - skipping issue management"
        return 0
    fi
    
    log_info "Processing issues for launch ${launch_id}"
    
    # Get failed test count from current launch
    local launch_data
    launch_data=$("${ALLURECTL_PATH}" launch get "${launch_id}" \
        -e "${ALLURE_ENDPOINT}" \
        -t "${ALLURE_TOKEN}" \
        --output json 2>/dev/null || echo "[]")
    
    local failed_count=0
    if [[ "${launch_data}" != "[]" ]]; then
        failed_count=$(echo "${launch_data}" | jq -r '.[0].statistic[]? | select(.status=="failed") | .count // 0')
    fi
    
    if [[ "${failed_count}" -gt 0 ]]; then
        log_info "Found ${failed_count} failed tests - creating issue"
        
        # Create issue for failed tests
        if [[ "${CREATE_ISSUES_ON_FAILURE:-true}" == "true" ]]; then
            "${ISSUE_MANAGER_PATH}" process \
                "${launch_id}" \
                "${launch_name}" \
                "${node_version}" \
                "${commit_hash}" \
                "${pipeline_url}"
        fi
    else
        log_info "All tests passed - checking for issues to close"
        
        # Close resolved issues
        if [[ "${CLOSE_ISSUES_ON_SUCCESS:-true}" == "true" ]]; then
            "${ISSUE_MANAGER_PATH}" close-resolved \
                "${launch_id}" \
                "${node_version}"
        fi
    fi
}

# Function to process defects based on test results
process_defects() {
    local launch_id="$1"
    local launch_name="${2:-Unknown Launch}"
    local node_version="${3:-unknown}"
    local commit_hash="${4:-unknown}"
    local pipeline_url="${5:-}"
    
    # Load defect configuration if available
    if [[ -f "redmine_config.env" ]]; then
        source redmine_config.env
    fi
    
    # Check if defect manager is available and configured
    if [[ ! -f "${DEFECT_MANAGER_PATH}" ]]; then
        log_warning "Defect manager not found at ${DEFECT_MANAGER_PATH}"
        return 0
    fi
    
    # Note: We can create TestOps defects even without Redmine
    if [[ -z "${REDMINE_API_KEY:-}" ]]; then
        log_info "Redmine API key not configured - will create only TestOps defects"
    fi
    
    log_info "Processing defects for launch ${launch_name} (ID: ${launch_id})"
    
    # Get failed test count from current launch
    local launch_data
    launch_data=$("${ALLURECTL_PATH}" launch get "${launch_id}" \
        -e "${ALLURE_ENDPOINT}" \
        -t "${ALLURE_TOKEN}" \
        --output json 2>/dev/null || echo "[]")
    
    local failed_count=0
    if [[ "${launch_data}" != "[]" ]]; then
        failed_count=$(echo "${launch_data}" | jq -r '.[0].statistic[]? | select(.status=="failed") | .count // 0')
    fi
    
    if [[ "${failed_count}" -gt 0 ]]; then
        log_info "Found ${failed_count} failed tests - creating defects"
        
        # Create defects for failed tests
        if [[ "${CREATE_DEFECTS_ON_FAILURE:-true}" == "true" ]]; then
            log_info "Creating defects for ${failed_count} failed tests"
            "${DEFECT_MANAGER_PATH}" process \
                "${launch_id}" \
                "${launch_name}" \
                "${node_version}" \
                "${commit_hash}" \
                "${pipeline_url}"
        fi
    else
        log_info "All tests passed - no defects to create"
    fi
}

# Function to close a launch
close_launch() {
    local launch_id="$1"
    
    log_info "Closing launch ID: ${launch_id}"
    
    if "${ALLURECTL_PATH}" launch close "${launch_id}" \
        -e "${ALLURE_ENDPOINT}" \
        -t "${ALLURE_TOKEN}" \
        --output json > /dev/null 2>&1; then
        log_success "Launch ${launch_id} closed successfully"
        rm -f .launch_id
        return 0
    else
        log_error "Failed to close launch ${launch_id}"
        return 1
    fi
}

# Function to get current launch ID
get_current_launch_id() {
    if [[ -f .launch_id ]]; then
        cat .launch_id
    else
        echo ""
    fi
}

# Function to upload results to existing launch
upload_to_launch() {
    local launch_id="$1"
    local results_dir="$2"
    
    log_info "Uploading results to launch ID: ${launch_id}"
    log_info "Results directory: ${results_dir}"
    
    if [[ ! -d "${results_dir}" ]]; then
        log_error "Results directory not found: ${results_dir}"
        return 1
    fi
    
    if "${ALLURECTL_PATH}" upload "${results_dir}" \
        -e "${ALLURE_ENDPOINT}" \
        -t "${ALLURE_TOKEN}" \
        --project-id "${ALLURE_PROJECT_ID}" \
        --launch-id "${launch_id}" > /dev/null 2>&1; then
        log_success "Results uploaded to launch ${launch_id}"
        return 0
    else
        log_error "Failed to upload results to launch ${launch_id}"
        return 1
    fi
}

# Function to add issue to launch (for failed tests)
add_issue_to_launch() {
    local launch_id="$1"
    local issue_key="$2"
    local integration_id="${3:-1}"  # Default integration ID
    
    log_info "Adding issue ${issue_key} to launch ${launch_id}"
    
    # Note: This requires integration setup in TestOps
    # For now, we'll just log the action
    log_warning "Issue tracking integration not configured yet"
    log_info "Would add issue: ${issue_key} to launch: ${launch_id}"
}

# Function to get launch statistics
get_launch_stats() {
    local launch_id="$1"
    
    log_info "Getting statistics for launch ID: ${launch_id}"
    
    local stats
    stats=$("${ALLURECTL_PATH}" launch get "${launch_id}" \
        -e "${ALLURE_ENDPOINT}" \
        -t "${ALLURE_TOKEN}" \
        --output json 2>/dev/null || echo "{}")
    
    if [[ "${stats}" != "{}" ]]; then
        local passed failed broken skipped
        passed=$(echo "${stats}" | jq -r '.[0].statistic[]? | select(.status=="passed") | .count // 0')
        failed=$(echo "${stats}" | jq -r '.[0].statistic[]? | select(.status=="failed") | .count // 0')
        broken=$(echo "${stats}" | jq -r '.[0].statistic[]? | select(.status=="broken") | .count // 0')
        skipped=$(echo "${stats}" | jq -r '.[0].statistic[]? | select(.status=="skipped") | .count // 0')
        
        echo "Launch Statistics:"
        echo "  Passed: ${passed}"
        echo "  Failed: ${failed}"
        echo "  Broken: ${broken}"
        echo "  Skipped: ${skipped}"
        
        # Return non-zero if there are failures
        if [[ "${failed}" -gt 0 || "${broken}" -gt 0 ]]; then
            return 1
        else
            return 0
        fi
    else
        log_error "Failed to get launch statistics"
        return 1
    fi
}

# Function to compare with previous launch
compare_with_previous() {
    local current_launch_id="$1"
    
    log_info "Comparing with previous launch..."
    
    # Get list of recent launches
    local previous_launches
    previous_launches=$("${ALLURECTL_PATH}" launch list \
        -e "${ALLURE_ENDPOINT}" \
        -t "${ALLURE_TOKEN}" \
        --project-id "${ALLURE_PROJECT_ID}" \
        --output json 2>/dev/null || echo "[]")
    
    # Find previous launch (excluding current one)
    local previous_launch_id
    previous_launch_id=$(echo "${previous_launches}" | jq -r --arg current "${current_launch_id}" \
        '.[] | select(.id != ($current | tonumber)) | .id' | head -1)
    
    if [[ -n "${previous_launch_id}" && "${previous_launch_id}" != "null" ]]; then
        log_info "Comparing with previous launch ID: ${previous_launch_id}"
        
        # Get current stats
        local current_stats previous_stats
        current_stats=$("${ALLURECTL_PATH}" launch get "${current_launch_id}" \
            -e "${ALLURE_ENDPOINT}" \
            -t "${ALLURE_TOKEN}" \
            --output json 2>/dev/null || echo "{}")
        
        previous_stats=$("${ALLURECTL_PATH}" launch get "${previous_launch_id}" \
            -e "${ALLURE_ENDPOINT}" \
            -t "${ALLURE_TOKEN}" \
            --output json 2>/dev/null || echo "{}")
        
        if [[ "${current_stats}" != "{}" && "${previous_stats}" != "{}" ]]; then
            local curr_failed prev_failed
            curr_failed=$(echo "${current_stats}" | jq -r '.[0].statistic[]? | select(.status=="failed") | .count // 0')
            prev_failed=$(echo "${previous_stats}" | jq -r '.[0].statistic[]? | select(.status=="failed") | .count // 0')
            
            echo ""
            echo "=== Launch Comparison ==="
            echo "Previous launch: ${previous_launch_id} (${prev_failed} failed)"
            echo "Current launch:  ${current_launch_id} (${curr_failed} failed)"
            
            if [[ "${curr_failed}" -gt "${prev_failed}" ]]; then
                log_warning "REGRESSION DETECTED: More tests failed than in previous launch"
                return 1
            elif [[ "${curr_failed}" -lt "${prev_failed}" ]]; then
                log_success "IMPROVEMENT: Fewer tests failed than in previous launch"
                return 0
            else
                log_info "STABLE: Same number of failed tests as previous launch"
                return 0
            fi
        else
            log_warning "Could not compare launches - missing statistics"
            return 0
        fi
    else
        log_info "No previous launch found for comparison"
        return 0
    fi
}

# Main function
main() {
    local action="$1"
    shift
    
    case "${action}" in
        "create")
            if [[ $# -lt 2 ]]; then
                log_error "Usage: $0 create <launch_name> <launch_tags>"
                exit 1
            fi
            create_launch "$1" "$2"
            ;;
        "close")
            local launch_id="${1:-$(get_current_launch_id)}"
            if [[ -z "${launch_id}" ]]; then
                log_error "No launch ID provided and no current launch found"
                exit 1
            fi
            close_launch "${launch_id}"
            ;;
        "upload")
            local launch_id="${1:-$(get_current_launch_id)}"
            local results_dir="${2:-allure-results}"
            if [[ -z "${launch_id}" ]]; then
                log_error "No launch ID provided and no current launch found"
                exit 1
            fi
            upload_to_launch "${launch_id}" "${results_dir}"
            ;;
        "stats")
            local launch_id="${1:-$(get_current_launch_id)}"
            if [[ -z "${launch_id}" ]]; then
                log_error "No launch ID provided and no current launch found"
                exit 1
            fi
            get_launch_stats "${launch_id}"
            ;;
        "compare")
            local launch_id="${1:-$(get_current_launch_id)}"
            if [[ -z "${launch_id}" ]]; then
                log_error "No launch ID provided and no current launch found"
                exit 1
            fi
            compare_with_previous "${launch_id}"
            ;;
        "add-issue")
            if [[ $# -lt 2 ]]; then
                log_error "Usage: $0 add-issue <launch_id> <issue_key>"
                exit 1
            fi
            add_issue_to_launch "$1" "$2"
            ;;
        "current")
            local current_id
            current_id=$(get_current_launch_id)
            if [[ -n "${current_id}" ]]; then
                echo "Current launch ID: ${current_id}"
            else
                echo "No current launch"
            fi
            ;;
        "issues")
            shift
            process_issues "$@"
            ;;
        "defects")
            shift
            process_defects "$@"
            ;;
        *)
            echo "Usage: $0 {create|close|upload|stats|compare|add-issue|current|issues|defects}"
            echo ""
            echo "Commands:"
            echo "  create <name> <tags>     - Create new launch"
            echo "  close [launch_id]        - Close launch (current if not specified)"
            echo "  upload [launch_id] [dir] - Upload results to launch"
            echo "  stats [launch_id]        - Get launch statistics"
            echo "  compare [launch_id]      - Compare with previous launch"
            echo "  add-issue <id> <key>     - Add issue to launch"
            echo "  current                  - Show current launch ID"
            echo "  issues <id> [name] [ver] [commit] [url] - Process issues for launch"
            echo "  defects <id> [name] [ver] [commit] [url] - Process defects for launch"
            exit 1
            ;;
    esac
}

# Check if allurectl exists
if [[ ! -f "${ALLURECTL_PATH}" ]]; then
    log_error "allurectl not found at ${ALLURECTL_PATH}"
    log_info "Please download allurectl first"
    exit 1
fi

# Check if jq is available
if ! command -v jq &> /dev/null; then
    log_error "jq is required but not installed"
    log_info "Please install jq: apt-get install jq"
    exit 1
fi

# Run main function
main "$@"
