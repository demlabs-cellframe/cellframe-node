#!/bin/bash

# Allure TestOps Defect Manager
# Автоматическое создание и управление дефектами для упавших тестов

set -euo pipefail

# Configuration
ALLURE_ENDPOINT="${ALLURE_ENDPOINT:-http://178.49.151.230:8080}"
ALLURE_TOKEN="${ALLURE_TOKEN:-c9d45bd4-394a-4e6c-aab2-f7bce2b5be44}"
ALLURE_PROJECT_ID="${ALLURE_PROJECT_ID:-1}"
REDMINE_URL="${REDMINE_URL:-}"
REDMINE_API_KEY="${REDMINE_API_KEY:-}"
REDMINE_PROJECT_ID="${REDMINE_PROJECT_ID:-}"
ALLURECTL_PATH="./allurectl"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
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

log_defect() {
    echo -e "${CYAN}[DEFECT]${NC} $1"
}

# Function to get failed test results from launch
get_failed_test_results() {
    local launch_id="$1"
    
    log_info "Getting failed test results from launch ID: ${launch_id}"
    
    # Get launch data with test results
    local launch_data
    launch_data=$("${ALLURECTL_PATH}" launch get "${launch_id}" \
        -e "${ALLURE_ENDPOINT}" \
        -t "${ALLURE_TOKEN}" \
        --output json 2>/dev/null || echo "[]")
    
    if [[ "${launch_data}" == "[]" ]]; then
        log_error "Failed to get launch data"
        return 1
    fi
    
    # Extract failed test count and basic info
    local failed_count
    failed_count=$(echo "${launch_data}" | jq -r '.[0].statistic[]? | select(.status=="failed") | .count // 0')
    
    if [[ "${failed_count}" -gt 0 ]]; then
        log_warning "Found ${failed_count} failed tests in launch ${launch_id}"
        
        # Save launch data for further processing
        echo "${launch_data}" > ".launch_${launch_id}_data.json"
        echo "${failed_count}"
        return 0
    else
        log_info "No failed tests found in launch ${launch_id}"
        echo "0"
        return 0
    fi
}

# Function to analyze failed test and determine defect type
analyze_failed_test() {
    local test_name="$1"
    local error_message="$2"
    local stack_trace="$3"
    
    # Analyzing failed test: ${test_name} (debug disabled for JSON parsing)
    
    # Simple categorization based on error patterns
    local defect_category="Unknown"
    local defect_priority="Normal"
    local defect_severity="Minor"
    
    # Analyze error message for categorization
    if [[ "${error_message}" =~ [Cc]onnection.*[Ff]ailed|[Tt]imeout|[Nn]etwork ]]; then
        defect_category="Network/Connection"
        defect_priority="High"
        defect_severity="Major"
    elif [[ "${error_message}" =~ [Aa]ssertion.*[Ff]ailed|[Ee]xpected.*but.*was|AssertionError ]]; then
        defect_category="Logic/Assertion"
        defect_priority="Normal"
        defect_severity="Normal"
    elif [[ "${error_message}" =~ [Nn]ull.*[Pp]ointer|[Ss]egmentation.*[Ff]ault ]]; then
        defect_category="Critical Error"
        defect_priority="Critical"
        defect_severity="Critical"
    elif [[ "${error_message}" =~ [Ff]ile.*not.*found|[Pp]ath.*not.*exist ]]; then
        defect_category="Environment/Setup"
        defect_priority="High"
        defect_severity="Major"
    elif [[ "${error_message}" =~ [Pp]ermission.*denied|[Aa]ccess.*denied ]]; then
        defect_category="Permissions"
        defect_priority="High"
        defect_severity="Major"
    fi
    
    # Create defect analysis result using jq to ensure proper JSON formatting
    jq -n \
        --arg test_name "${test_name}" \
        --arg category "${defect_category}" \
        --arg priority "${defect_priority}" \
        --arg severity "${defect_severity}" \
        --arg error_message "${error_message}" \
        --arg stack_trace "${stack_trace}" \
        '{
            test_name: $test_name,
            category: $category,
            priority: $priority,
            severity: $severity,
            error_message: $error_message,
            stack_trace: $stack_trace
        }'
}

# Function to create Redmine issue for defect
create_redmine_defect() {
    local defect_data="$1"
    local launch_id="$2"
    local launch_name="$3"
    local node_version="$4"
    local commit_hash="$5"
    local pipeline_url="$6"
    
    if [[ -z "${REDMINE_URL}" || -z "${REDMINE_API_KEY}" || -z "${REDMINE_PROJECT_ID}" ]]; then
        log_warning "Redmine integration not configured"
        log_info "Set REDMINE_URL, REDMINE_API_KEY, and REDMINE_PROJECT_ID"
        return 1
    fi
    
    # Parse defect data
    local test_name category priority severity error_message
    test_name=$(echo "${defect_data}" | jq -r '.test_name')
    category=$(echo "${defect_data}" | jq -r '.category')
    priority=$(echo "${defect_data}" | jq -r '.priority')
    severity=$(echo "${defect_data}" | jq -r '.severity')
    error_message=$(echo "${defect_data}" | jq -r '.error_message')
    
    # Generate issue subject
    local subject="[QA Defect] ${test_name} - ${category} (${node_version})"
    
    # Generate issue description
    local description
    description=$(cat << EOF
## 🐛 Автоматически созданный дефект

### 📊 Информация о тесте
- **Тест**: ${test_name}
- **Категория**: ${category}
- **Приоритет**: ${priority}
- **Серьезность**: ${severity}
- **Версия ноды**: ${node_version}
- **Коммит**: ${commit_hash}

### 🔍 Детали ошибки
\`\`\`
${error_message}
\`\`\`

### 🔗 Ссылки
- **TestOps Launch**: ${ALLURE_ENDPOINT}/launch/${launch_id}
- **TestOps Project**: ${ALLURE_ENDPOINT}/project/${ALLURE_PROJECT_ID}
- **GitLab Pipeline**: ${pipeline_url}

### 📋 Шаги для воспроизведения
1. Запустить тест: ${test_name}
2. Использовать версию ноды: ${node_version}
3. Проверить окружение и конфигурацию

### 🎯 Критерии приемки
- [ ] Тест проходит успешно
- [ ] Ошибка не воспроизводится
- [ ] Добавлены дополнительные проверки (при необходимости)

---
*Дефект создан автоматически системой QA*  
*Дата: $(date '+%d.%m.%Y %H:%M:%S')*  
*Launch ID: ${launch_id}*
EOF
    )
    
    # Map priority to Redmine priority ID
    local redmine_priority_id=2  # Normal by default
    case "${priority}" in
        "Critical") redmine_priority_id=5 ;;
        "High") redmine_priority_id=4 ;;
        "Normal") redmine_priority_id=3 ;;
        "Low") redmine_priority_id=2 ;;
    esac
    
    # Create JSON payload for Redmine
    local json_payload
    json_payload=$(jq -n \
        --arg subject "${subject}" \
        --arg description "${description}" \
        --arg project_id "${REDMINE_PROJECT_ID}" \
        --arg priority_id "${redmine_priority_id}" \
        --arg tracker_id "1" \
        '{
            issue: {
                subject: $subject,
                description: $description,
                project_id: ($project_id | tonumber),
                priority_id: ($priority_id | tonumber),
                tracker_id: ($tracker_id | tonumber),
                status_id: 1
            }
        }')
    
    log_info "Creating Redmine defect: ${subject}"
    
    # Create issue via Redmine API
    local response
    response=$(curl -s -X POST \
        "${REDMINE_URL}/issues.json" \
        -H "X-Redmine-API-Key: ${REDMINE_API_KEY}" \
        -H "Content-Type: application/json" \
        -d "${json_payload}" || echo "{}")
    
    # Check if issue was created
    local issue_id
    issue_id=$(echo "${response}" | jq -r '.issue.id // empty')
    
    if [[ -n "${issue_id}" ]]; then
        local issue_url="${REDMINE_URL}/issues/${issue_id}"
        log_success "Redmine defect created: ${issue_url}"
        echo "${issue_id}"
        return 0
    else
        log_error "Failed to create Redmine defect"
        log_debug "Response: ${response}"
        return 1
    fi
}

# Function to create TestOps defect
create_testops_defect() {
    local defect_data="$1"
    local launch_id="$2"
    local launch_name="$3"
    local node_version="$4"
    local commit_hash="$5"
    local pipeline_url="$6"
    
    local test_name category priority severity error_message
    test_name=$(echo "${defect_data}" | jq -r '.test_name')
    category=$(echo "${defect_data}" | jq -r '.category')
    priority=$(echo "${defect_data}" | jq -r '.priority')
    severity=$(echo "${defect_data}" | jq -r '.severity')
    error_message=$(echo "${defect_data}" | jq -r '.error_message')
    
    log_info "Creating TestOps defect for test: ${test_name}"
    
    # Generate defect name and description
    local defect_name="[${category}] ${test_name} - ${node_version}"
    local defect_description
    defect_description=$(cat << EOF
## 🐛 Автоматически созданный дефект

### 📊 Информация о тесте
- **Тест**: ${test_name}
- **Категория**: ${category}
- **Приоритет**: ${priority}
- **Серьезность**: ${severity}
- **Версия ноды**: ${node_version}
- **Коммит**: ${commit_hash}

### 🔍 Детали ошибки
\`\`\`
${error_message}
\`\`\`

### 🔗 Ссылки
- **TestOps Launch**: ${ALLURE_ENDPOINT}/launch/${launch_id}
- **TestOps Project**: ${ALLURE_ENDPOINT}/project/${ALLURE_PROJECT_ID}
- **GitLab Pipeline**: ${pipeline_url}

### 📋 Шаги для воспроизведения
1. Запустить тест: ${test_name}
2. Использовать версию ноды: ${node_version}
3. Проверить окружение и конфигурацию

---
*Дефект создан автоматически системой QA*  
*Дата: $(date '+%d.%m.%Y %H:%M:%S')*  
*Launch ID: ${launch_id}*
EOF
    )
    
    # Create JSON payload for TestOps defect
    local json_payload
    json_payload=$(jq -n \
        --arg name "${defect_name}" \
        --arg description "${defect_description}" \
        --arg projectId "${ALLURE_PROJECT_ID}" \
        '{
            name: $name,
            description: $description,
            projectId: ($projectId | tonumber)
        }')
    
    log_debug "Creating TestOps defect with payload: ${json_payload}"
    
    # Create defect via TestOps API
    local response
    response=$(curl -s -X POST \
        "${ALLURE_ENDPOINT}/api/rs/defect?projectId=${ALLURE_PROJECT_ID}" \
        -H "Authorization: Api-Token ${ALLURE_TOKEN}" \
        -H "Content-Type: application/json" \
        -d "${json_payload}" || echo "{}")
    
    # Check if defect was created
    local defect_id
    defect_id=$(echo "${response}" | jq -r '.id // empty')
    
    if [[ -n "${defect_id}" ]]; then
        local defect_url="${ALLURE_ENDPOINT}/project/${ALLURE_PROJECT_ID}/defects/${defect_id}"
        log_success "TestOps defect created: ${defect_url}"
        log_success "Defect ID: ${defect_id}"
        echo "${defect_id}"
        return 0
    else
        log_error "Failed to create TestOps defect"
        log_debug "Response: ${response}"
        return 1
    fi
}

# Function to process failed tests and create defects
process_failed_tests_for_defects() {
    local launch_id="$1"
    local launch_name="${2:-Unknown Launch}"
    local node_version="${3:-unknown}"
    local commit_hash="${4:-unknown}"
    local pipeline_url="${5:-}"
    
    log_info "Processing failed tests for defect creation in launch ${launch_id}"
    
    # Get failed test count
    local failed_count
    failed_count=$(get_failed_test_results "${launch_id}")
    
    if [[ "${failed_count}" == "0" ]]; then
        log_success "No failed tests - no defects to create"
        return 0
    fi
    
    log_defect "Found ${failed_count} failed tests - analyzing for defect creation"
    
    # Get real failed test data from TestOps API
    log_info "Fetching failed test details from TestOps API..."
    local api_response
    api_response=$(curl -s -H "Authorization: Api-Token ${ALLURE_TOKEN}" \
        "${ALLURE_ENDPOINT}/api/rs/testresult?launchId=${launch_id}&size=50")
    
    local test_name test_message
    test_name=$(echo "${api_response}" | jq -r '.content[] | select(.status=="failed") | .name' | head -1)
    test_message=$(echo "${api_response}" | jq -r '.content[] | select(.status=="failed") | .message' | head -1)
    
    if [[ -z "${test_name}" || "${test_name}" == "null" ]]; then
        log_warning "No failed test details found via API, using fallback"
        test_name="unknown_test"
        test_message="Test failed - details not available"
    else
        log_success "Found real failed test data from API"
        log_info "Processing failed test: ${test_name}"
        
        if [[ "${test_message}" == "null" || -z "${test_message}" ]]; then
            test_message="Test failed without error message"
        fi
        
        log_debug "Error message: ${test_message}"
    fi
    
    local sample_defect_data
    sample_defect_data=$(analyze_failed_test \
        "${test_name}" \
        "${test_message}" \
        "Stack trace from TestOps")
    
    # Note: Don't log the JSON data as it interferes with parsing
    
    # Always create TestOps defect
    local testops_defect_id
    if testops_defect_id=$(create_testops_defect \
        "${sample_defect_data}" \
        "${launch_id}" \
        "${launch_name}" \
        "${node_version}" \
        "${commit_hash}" \
        "${pipeline_url}"); then
        
        log_success "TestOps defect created with ID: ${testops_defect_id}"
    else
        log_warning "Failed to create TestOps defect"
    fi
    
    # Create Redmine defect if configured
    if [[ -n "${REDMINE_API_KEY:-}" && -n "${REDMINE_URL:-}" && -n "${REDMINE_PROJECT_ID:-}" ]]; then
        local defect_id
        if defect_id=$(create_redmine_defect \
            "${sample_defect_data}" \
            "${launch_id}" \
            "${launch_name}" \
            "${node_version}" \
            "${commit_hash}" \
            "${pipeline_url}"); then
            
            log_success "Redmine defect created with ID: ${defect_id}"
        else
            log_warning "Failed to create Redmine defect"
        fi
    else
        log_info "Redmine not configured - skipping Redmine defect creation"
    fi
    
    return 0
}

# Function to check Redmine connection
test_redmine_connection() {
    if [[ -z "${REDMINE_URL}" || -z "${REDMINE_API_KEY}" ]]; then
        log_error "Redmine not configured"
        log_info "Set REDMINE_URL and REDMINE_API_KEY environment variables"
        return 1
    fi
    
    log_info "Testing Redmine connection..."
    
    local response
    response=$(curl -s -H "X-Redmine-API-Key: ${REDMINE_API_KEY}" \
        "${REDMINE_URL}/projects.json?limit=1" || echo "{}")
    
    local project_count
    project_count=$(echo "${response}" | jq -r '.total_count // 0')
    
    if [[ "${project_count}" -gt 0 ]]; then
        log_success "Redmine connection OK - Found ${project_count} projects"
        return 0
    else
        log_error "Redmine connection failed"
        log_debug "Response: ${response}"
        return 1
    fi
}

# Function to list recent defects from Redmine
list_recent_defects() {
    local limit="${1:-10}"
    
    if [[ -z "${REDMINE_URL}" || -z "${REDMINE_API_KEY}" ]]; then
        log_error "Redmine not configured"
        return 1
    fi
    
    log_info "Listing recent QA defects from Redmine (limit: ${limit})"
    
    local response
    response=$(curl -s -H "X-Redmine-API-Key: ${REDMINE_API_KEY}" \
        "${REDMINE_URL}/issues.json?limit=${limit}&sort=created_on:desc&subject=*QA%20Defect*" || echo "{}")
    
    echo "${response}" | jq -r '.issues[]? | "#\(.id) - \(.subject) (\(.status.name)) - \(.created_on)"'
}

# Function to list TestOps defects
list_testops_defects() {
    local limit="${1:-10}"
    
    log_info "Listing TestOps defects (limit: ${limit})"
    
    local response
    response=$(curl -s -H "Authorization: Api-Token ${ALLURE_TOKEN}" \
        "${ALLURE_ENDPOINT}/api/rs/defect?projectId=${ALLURE_PROJECT_ID}&size=${limit}" || echo "{}")
    
    local defects
    defects=$(echo "${response}" | jq -r '.content[]? | "#\(.id) - \(.name) (\(.closed | if . then "Closed" else "Open" end)) - Count: \(.count)"')
    
    if [[ -n "${defects}" ]]; then
        echo "${defects}"
    else
        echo "No defects found in TestOps"
    fi
}

# Function to get defect statistics
get_defect_statistics() {
    local days="${1:-7}"
    
    if [[ -z "${REDMINE_URL}" || -z "${REDMINE_API_KEY}" ]]; then
        log_error "Redmine not configured"
        return 1
    fi
    
    log_info "Getting defect statistics for last ${days} days"
    
    local date_from
    date_from=$(date -d "${days} days ago" '+%Y-%m-%d')
    
    local response
    response=$(curl -s -H "X-Redmine-API-Key: ${REDMINE_API_KEY}" \
        "${REDMINE_URL}/issues.json?created_on=%3E%3D${date_from}&subject=*QA%20Defect*&limit=100" || echo "{}")
    
    local total_defects open_defects closed_defects
    total_defects=$(echo "${response}" | jq -r '.total_count // 0')
    open_defects=$(echo "${response}" | jq -r '[.issues[]? | select(.status.is_closed == false)] | length')
    closed_defects=$(echo "${response}" | jq -r '[.issues[]? | select(.status.is_closed == true)] | length')
    
    echo ""
    echo "=== Defect Statistics (Last ${days} days) ==="
    echo "Total Defects: ${total_defects}"
    echo "Open Defects: ${open_defects}"
    echo "Closed Defects: ${closed_defects}"
    echo "Resolution Rate: $(( closed_defects * 100 / (total_defects > 0 ? total_defects : 1) ))%"
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
            process_failed_tests_for_defects "$@"
            ;;
        "test-redmine")
            test_redmine_connection
            ;;
        "list")
            local limit="${1:-10}"
            list_recent_defects "${limit}"
            ;;
        "list-testops")
            local limit="${1:-10}"
            list_testops_defects "${limit}"
            ;;
        "stats")
            local days="${1:-7}"
            get_defect_statistics "${days}"
            ;;
        "analyze")
            if [[ $# -lt 3 ]]; then
                log_error "Usage: $0 analyze <test_name> <error_message> <stack_trace>"
                exit 1
            fi
            analyze_failed_test "$1" "$2" "$3"
            ;;
        "create-testops")
            if [[ $# -lt 6 ]]; then
                log_error "Usage: $0 create-testops <test_name> <error_message> <launch_id> <launch_name> <node_version> <commit_hash> [pipeline_url]"
                exit 1
            fi
            local defect_data
            defect_data=$(analyze_failed_test "$1" "$2" "Stack trace not available" 2>/dev/null | tail -n +2)
            create_testops_defect "${defect_data}" "$3" "$4" "$5" "$6" "${7:-}"
            ;;
        "help"|*)
            echo "Usage: $0 {process|test-redmine|list|list-testops|stats|analyze|create-testops}"
            echo ""
            echo "Commands:"
            echo "  process <launch_id> [name] [version] [commit] [url]  - Process failed tests and create defects"
            echo "  test-redmine                                         - Test Redmine connection"
            echo "  list [limit]                                         - List recent QA defects from Redmine"
            echo "  list-testops [limit]                                 - List defects from TestOps"
            echo "  stats [days]                                         - Get defect statistics"
            echo "  analyze <test> <error> <trace>                       - Analyze test failure"
            echo "  create-testops <test> <error> <launch> <name> <ver> <commit> [url] - Create TestOps defect"
            echo ""
            echo "Environment variables:"
            echo "  REDMINE_URL         - Redmine instance URL"
            echo "  REDMINE_API_KEY     - Redmine API key"
            echo "  REDMINE_PROJECT_ID  - Redmine project ID"
            echo "  ALLURE_ENDPOINT     - TestOps endpoint"
            echo "  ALLURE_TOKEN        - TestOps API token"
            echo "  ALLURE_PROJECT_ID   - TestOps project ID"
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
