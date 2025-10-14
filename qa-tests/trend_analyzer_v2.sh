#!/bin/bash

# TestOps Trend Analyzer v2
# Анализ трендов и метрик тестирования для оптимизации QA процесса

set -euo pipefail

# Configuration
ALLURE_ENDPOINT="${ALLURE_ENDPOINT:-http://178.49.151.230:8080}"
ALLURE_TOKEN="${ALLURE_TOKEN:-c9d45bd4-394a-4e6c-aab2-f7bce2b5be44}"
ALLURE_PROJECT_ID="${ALLURE_PROJECT_ID:-1}"

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

log_trend() {
    echo -e "${CYAN}[TREND]${NC} $1"
}

log_metric() {
    echo -e "${PURPLE}[METRIC]${NC} $1"
}

# Function to get recent launches
get_recent_launches() {
    local limit="${1:-10}"
    
    log_info "Getting recent launches (limit: ${limit})"
    
    curl -s -H "Authorization: Api-Token ${ALLURE_TOKEN}" \
        "${ALLURE_ENDPOINT}/api/rs/launch?projectId=${ALLURE_PROJECT_ID}&size=${limit}"
}

# Function to get launch statistics
get_launch_statistics() {
    local launch_id="$1"
    
    local test_results
    test_results=$(curl -s -H "Authorization: Api-Token ${ALLURE_TOKEN}" \
        "${ALLURE_ENDPOINT}/api/rs/testresult?launchId=${launch_id}&size=100")
    
    local passed failed broken skipped total
    passed=$(echo "${test_results}" | jq '[.content[] | select(.status=="passed")] | length')
    failed=$(echo "${test_results}" | jq '[.content[] | select(.status=="failed")] | length')
    broken=$(echo "${test_results}" | jq '[.content[] | select(.status=="broken")] | length')
    skipped=$(echo "${test_results}" | jq '[.content[] | select(.status=="skipped")] | length')
    total=$((passed + failed + broken + skipped))
    
    local success_rate=0
    if [[ "${total}" -gt 0 ]]; then
        success_rate=$((passed * 100 / total))
    fi
    
    echo "${passed}:${failed}:${broken}:${skipped}:${success_rate}"
}

# Function to analyze success rate trends
analyze_success_rate_trend() {
    local limit="${1:-10}"
    
    log_trend "Analyzing success rate trends for last ${limit} launches"
    
    local launches_response
    launches_response=$(get_recent_launches "${limit}")
    
    local launches_data
    launches_data=$(echo "${launches_response}" | jq '.content')
    
    if [[ -z "${launches_data}" || "${launches_data}" == "null" ]]; then
        log_warning "No launch data found"
        return 1
    fi
    
    echo ""
    echo "=== Success Rate Trend ==="
    echo "Launch | Name                 | Passed | Failed | Broken | Success Rate"
    echo "-------|----------------------|--------|--------|--------|-------------"
    
    local total_success_rate=0
    local launch_count=0
    
    # Get launch IDs
    local launch_ids
    launch_ids=$(echo "${launches_data}" | jq -r '.[] | .id')
    
    # Process each launch
    for launch_id in ${launch_ids}; do
        if [[ -n "${launch_id}" ]]; then
            local launch_name
            launch_name=$(echo "${launches_data}" | jq -r ".[] | select(.id==${launch_id}) | .name")
            
            local stats
            stats=$(get_launch_statistics "${launch_id}")
            
            local passed failed broken skipped success_rate
            IFS=':' read -r passed failed broken skipped success_rate <<< "${stats}"
            
            printf "%-6s | %-20s | %-6s | %-6s | %-6s | %s%%\n" \
                "${launch_id}" \
                "${launch_name:0:20}" \
                "${passed}" \
                "${failed}" \
                "${broken}" \
                "${success_rate}"
            
            total_success_rate=$((total_success_rate + success_rate))
            launch_count=$((launch_count + 1))
        fi
    done
    
    if [[ "${launch_count}" -gt 0 ]]; then
        local avg_success_rate=$((total_success_rate / launch_count))
        
        echo ""
        log_metric "Average Success Rate: ${avg_success_rate}%"
        log_metric "Total Launches Analyzed: ${launch_count}"
        
        if [[ "${avg_success_rate}" -gt 90 ]]; then
            log_success "Excellent quality! Success rate > 90%"
        elif [[ "${avg_success_rate}" -gt 80 ]]; then
            log_warning "Good quality, but room for improvement (80-90%)"
        else
            log_error "Quality needs attention! Success rate < 80%"
        fi
    fi
}

# Function to find most unstable tests
find_unstable_tests() {
    local limit="${1:-10}"
    
    log_trend "Finding most unstable tests (last ${limit} launches)"
    
    local launches_response
    launches_response=$(get_recent_launches "${limit}")
    
    local launches_data
    launches_data=$(echo "${launches_response}" | jq '.content')
    
    if [[ -z "${launches_data}" || "${launches_data}" == "null" ]]; then
        log_warning "No launch data found"
        return 1
    fi
    
    # Get all launch IDs
    local launch_ids
    launch_ids=$(echo "${launches_data}" | jq -r '.[] | .id')
    
    echo ""
    echo "=== Most Unstable Tests ==="
    echo "Getting test results from recent launches..."
    
    # Create temporary file for test failure analysis
    local temp_file="/tmp/test_failures_$$"
    
    # Get failed tests from all recent launches
    for launch_id in ${launch_ids}; do
        curl -s -H "Authorization: Api-Token ${ALLURE_TOKEN}" \
            "${ALLURE_ENDPOINT}/api/rs/testresult?launchId=${launch_id}&size=100" | \
            jq -r '.content[] | select(.status=="failed" or .status=="broken") | .name' >> "${temp_file}" 2>/dev/null || true
    done
    
    if [[ -f "${temp_file}" && -s "${temp_file}" ]]; then
        echo ""
        echo "Test Name                      | Failure Count"
        echo "-------------------------------|-------------"
        sort "${temp_file}" | uniq -c | sort -nr | head -10 | \
        awk '{printf "%-30s | %d\n", substr($0, 9), $1}'
        
        local most_unstable
        most_unstable=$(sort "${temp_file}" | uniq -c | sort -nr | head -1 | awk '{print substr($0, 9)}')
        local failure_count
        failure_count=$(sort "${temp_file}" | uniq -c | sort -nr | head -1 | awk '{print $1}')
        
        echo ""
        log_warning "Most unstable test: ${most_unstable} (${failure_count} failures)"
        
        rm -f "${temp_file}"
    else
        log_success "No failed tests found in recent launches!"
    fi
}

# Function to analyze defect trends
analyze_defect_trends() {
    log_trend "Analyzing defect trends"
    
    local defects_data
    defects_data=$(curl -s -H "Authorization: Api-Token ${ALLURE_TOKEN}" \
        "${ALLURE_ENDPOINT}/api/rs/defect?projectId=${ALLURE_PROJECT_ID}&size=20")
    
    local total_defects open_defects closed_defects
    total_defects=$(echo "${defects_data}" | jq '.totalElements // 0')
    open_defects=$(echo "${defects_data}" | jq '[.content[]? | select(.closed == false)] | length')
    closed_defects=$(echo "${defects_data}" | jq '[.content[]? | select(.closed == true)] | length')
    
    echo ""
    echo "=== Defect Trends ==="
    log_metric "Total Defects: ${total_defects}"
    log_metric "Open Defects: ${open_defects}"
    log_metric "Closed Defects: ${closed_defects}"
    
    if [[ "${total_defects}" -gt 0 ]]; then
        local resolution_rate
        resolution_rate=$(( closed_defects * 100 / total_defects ))
        log_metric "Resolution Rate: ${resolution_rate}%"
        
        if [[ "${resolution_rate}" -gt 80 ]]; then
            log_success "Good defect resolution rate!"
        else
            log_warning "Consider improving defect resolution process"
        fi
    fi
    
    # Show recent defects
    echo ""
    echo "Recent Defects:"
    echo "ID | Name                           | Status"
    echo "---|--------------------------------|-------"
    echo "${defects_data}" | jq -r '.content[]? | 
        "\(.id) | \(.name[0:30]) | \(if .closed then "Closed" else "Open" end)"' | head -5
}

# Function to generate quality dashboard
generate_dashboard() {
    local limit="${1:-10}"
    
    echo ""
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║                    📊 QA Quality Dashboard                     ║"
    echo "║                   Last ${limit} launches analysis                      ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    
    analyze_success_rate_trend "${limit}"
    echo ""
    find_unstable_tests "${limit}"
    echo ""
    analyze_defect_trends
    
    echo ""
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║                       📈 Recommendations                       ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    
    # Get current metrics for recommendations
    local launches_response
    launches_response=$(get_recent_launches 5)
    
    local launches_data
    launches_data=$(echo "${launches_response}" | jq '.content')
    
    local launch_ids
    launch_ids=$(echo "${launches_data}" | jq -r '.[] | .id')
    
    local total_success_rate=0
    local launch_count=0
    
    for launch_id in ${launch_ids}; do
        local stats
        stats=$(get_launch_statistics "${launch_id}")
        local success_rate
        success_rate=$(echo "${stats}" | cut -d':' -f5)
        total_success_rate=$((total_success_rate + success_rate))
        launch_count=$((launch_count + 1))
    done
    
    local avg_success_rate=0
    if [[ "${launch_count}" -gt 0 ]]; then
        avg_success_rate=$((total_success_rate / launch_count))
    fi
    
    if [[ "${avg_success_rate}" -lt 85 ]]; then
        echo "🔍 Focus on stabilizing failing tests"
        echo "📋 Review and update test cases"
        echo "🛠️ Consider infrastructure improvements"
    else
        echo "✅ Quality is good, maintain current practices"
        echo "🚀 Consider adding more comprehensive tests"
        echo "📊 Monitor trends for early problem detection"
    fi
    
    echo ""
    echo "🔗 TestOps Project: ${ALLURE_ENDPOINT}/project/${ALLURE_PROJECT_ID}"
    echo "📅 Generated: $(date '+%d.%m.%Y %H:%M:%S')"
}

# Function to compare launches
compare_launches() {
    local launch1="$1"
    local launch2="$2"
    
    log_info "Comparing launches ${launch1} vs ${launch2}"
    
    local stats1 stats2
    stats1=$(get_launch_statistics "${launch1}")
    stats2=$(get_launch_statistics "${launch2}")
    
    local l1_passed l1_failed l1_broken l1_skipped l1_rate
    IFS=':' read -r l1_passed l1_failed l1_broken l1_skipped l1_rate <<< "${stats1}"
    
    local l2_passed l2_failed l2_broken l2_skipped l2_rate
    IFS=':' read -r l2_passed l2_failed l2_broken l2_skipped l2_rate <<< "${stats2}"
    
    echo ""
    echo "=== Launch Comparison ==="
    echo "Metric      | Launch ${launch1} | Launch ${launch2} | Difference"
    echo "------------|-----------|-----------|----------"
    echo "Passed      | ${l1_passed}        | ${l2_passed}        | $((l2_passed - l1_passed))"
    echo "Failed      | ${l1_failed}        | ${l2_failed}        | $((l2_failed - l1_failed))"
    echo "Broken      | ${l1_broken}        | ${l2_broken}        | $((l2_broken - l1_broken))"
    echo "Success %   | ${l1_rate}%       | ${l2_rate}%       | $((l2_rate - l1_rate))%"
    
    local failed_diff=$((l2_failed - l1_failed))
    local broken_diff=$((l2_broken - l1_broken))
    local total_issues_diff=$((failed_diff + broken_diff))
    
    echo ""
    if [[ "${total_issues_diff}" -gt 0 ]]; then
        log_warning "Regression detected: ${total_issues_diff} more issues"
    elif [[ "${total_issues_diff}" -lt 0 ]]; then
        log_success "Improvement: ${total_issues_diff#-} fewer issues"
    else
        log_info "No change in issue count"
    fi
}

# Main function
main() {
    if [[ $# -eq 0 ]]; then
        action="dashboard"
    else
        local action="$1"
        shift
    fi
    
    case "${action}" in
        "dashboard")
            local limit="${1:-10}"
            generate_dashboard "${limit}"
            ;;
        "trends")
            local limit="${1:-10}"
            analyze_success_rate_trend "${limit}"
            ;;
        "unstable")
            local limit="${1:-10}"
            find_unstable_tests "${limit}"
            ;;
        "defects")
            analyze_defect_trends
            ;;
        "compare")
            if [[ $# -lt 2 ]]; then
                log_error "Usage: $0 compare <launch_id1> <launch_id2>"
                exit 1
            fi
            compare_launches "$1" "$2"
            ;;
        "help"|*)
            echo "Usage: $0 {dashboard|trends|unstable|defects|compare}"
            echo ""
            echo "Commands:"
            echo "  dashboard [limit]          - Generate quality dashboard (default: 10 launches)"
            echo "  trends [limit]             - Analyze success rate trends"
            echo "  unstable [limit]           - Find most unstable tests"
            echo "  defects                    - Analyze defect trends"
            echo "  compare <id1> <id2>        - Compare two launches"
            echo ""
            echo "Examples:"
            echo "  $0 dashboard 20            - Dashboard for last 20 launches"
            echo "  $0 unstable 30             - Most unstable tests in 30 launches"
            echo "  $0 compare 31 30           - Compare launches 31 and 30"
            exit 1
            ;;
    esac
}

# Check dependencies
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
