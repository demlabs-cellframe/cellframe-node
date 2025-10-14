#!/bin/bash

# Working Trend Analyzer
# Простая рабочая версия анализатора трендов

set -euo pipefail

# Configuration
ALLURE_ENDPOINT="${ALLURE_ENDPOINT:-http://178.49.151.230:8080}"
ALLURE_TOKEN="${ALLURE_TOKEN:-c9d45bd4-394a-4e6c-aab2-f7bce2b5be44}"
ALLURE_PROJECT_ID="${ALLURE_PROJECT_ID:-1}"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_trend() { echo -e "${CYAN}[TREND]${NC} $1"; }

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

# Function to analyze trends
analyze_trends() {
    local limit="${1:-5}"
    
    log_trend "Analyzing trends for last ${limit} launches"
    
    # Get launches and save to temp file
    local temp_file="/tmp/launches_$$.json"
    curl -s -H "Authorization: Api-Token ${ALLURE_TOKEN}" \
        "${ALLURE_ENDPOINT}/api/rs/launch?projectId=${ALLURE_PROJECT_ID}&size=${limit}" > "${temp_file}"
    
    echo ""
    echo "=== Success Rate Trend ==="
    echo "Launch | Name                 | Passed | Failed | Broken | Success Rate"
    echo "-------|----------------------|--------|--------|--------|-------------"
    
    local total_success_rate=0
    local launch_count=0
    
    # Get launch IDs from file
    local launch_ids
    launch_ids=$(jq -r '.content[] | .id' "${temp_file}")
    
    # Process each launch
    for launch_id in ${launch_ids}; do
        if [[ -n "${launch_id}" ]]; then
            local launch_name
            launch_name=$(jq -r ".content[] | select(.id==${launch_id}) | .name" "${temp_file}")
            
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
    
    # Clean up
    rm -f "${temp_file}"
    
    if [[ "${launch_count}" -gt 0 ]]; then
        local avg_success_rate=$((total_success_rate / launch_count))
        
        echo ""
        echo "📊 Average Success Rate: ${avg_success_rate}%"
        echo "📈 Total Launches Analyzed: ${launch_count}"
        
        if [[ "${avg_success_rate}" -gt 90 ]]; then
            log_success "Excellent quality! Success rate > 90%"
        elif [[ "${avg_success_rate}" -gt 80 ]]; then
            log_warning "Good quality, but room for improvement (80-90%)"
        else
            log_warning "Quality needs attention! Success rate < 80%"
        fi
    fi
}

# Function to find unstable tests
find_unstable_tests() {
    local limit="${1:-5}"
    
    log_trend "Finding unstable tests in last ${limit} launches"
    
    # Get launches
    local temp_file="/tmp/launches_$$.json"
    curl -s -H "Authorization: Api-Token ${ALLURE_TOKEN}" \
        "${ALLURE_ENDPOINT}/api/rs/launch?projectId=${ALLURE_PROJECT_ID}&size=${limit}" > "${temp_file}"
    
    local launch_ids
    launch_ids=$(jq -r '.content[] | .id' "${temp_file}")
    
    echo ""
    echo "=== Most Unstable Tests ==="
    
    # Create temp file for failures
    local failures_file="/tmp/failures_$$.txt"
    
    # Collect failed tests
    for launch_id in ${launch_ids}; do
        curl -s -H "Authorization: Api-Token ${ALLURE_TOKEN}" \
            "${ALLURE_ENDPOINT}/api/rs/testresult?launchId=${launch_id}&size=100" | \
            jq -r '.content[] | select(.status=="failed" or .status=="broken") | .name' >> "${failures_file}" 2>/dev/null || true
    done
    
    if [[ -f "${failures_file}" && -s "${failures_file}" ]]; then
        echo "Test Name                      | Failure Count"
        echo "-------------------------------|-------------"
        sort "${failures_file}" | uniq -c | sort -nr | head -10 | \
        awk '{printf "%-30s | %d\n", substr($0, 9), $1}'
        
        local most_unstable
        most_unstable=$(sort "${failures_file}" | uniq -c | sort -nr | head -1 | awk '{print substr($0, 9)}' 2>/dev/null || echo "none")
        local failure_count
        failure_count=$(sort "${failures_file}" | uniq -c | sort -nr | head -1 | awk '{print $1}' 2>/dev/null || echo "0")
        
        echo ""
        if [[ "${most_unstable}" != "none" ]]; then
            log_warning "Most unstable: ${most_unstable} (${failure_count} failures)"
        else
            log_success "No unstable tests found!"
        fi
    else
        log_success "No failed tests found!"
    fi
    
    # Clean up
    rm -f "${temp_file}" "${failures_file}"
}

# Function to show defects
show_defects() {
    log_trend "Analyzing defect trends"
    
    local defects_data
    defects_data=$(curl -s -H "Authorization: Api-Token ${ALLURE_TOKEN}" \
        "${ALLURE_ENDPOINT}/api/rs/defect?projectId=${ALLURE_PROJECT_ID}&size=20")
    
    local total_defects open_defects closed_defects
    total_defects=$(echo "${defects_data}" | jq '.totalElements // 0')
    open_defects=$(echo "${defects_data}" | jq '[.content[]? | select(.closed == false)] | length')
    closed_defects=$(echo "${defects_data}" | jq '[.content[]? | select(.closed == true)] | length')
    
    echo ""
    echo "=== Defect Summary ==="
    echo "📊 Total Defects: ${total_defects}"
    echo "🔴 Open Defects: ${open_defects}"
    echo "✅ Closed Defects: ${closed_defects}"
    
    if [[ "${total_defects}" -gt 0 ]]; then
        local resolution_rate
        resolution_rate=$(( closed_defects * 100 / total_defects ))
        echo "📈 Resolution Rate: ${resolution_rate}%"
        
        if [[ "${resolution_rate}" -gt 80 ]]; then
            log_success "Good defect resolution rate!"
        else
            log_warning "Consider improving defect resolution"
        fi
    fi
    
    # Show recent defects
    if [[ "${total_defects}" -gt 0 ]]; then
        echo ""
        echo "Recent Defects:"
        echo "ID | Name                           | Status"
        echo "---|--------------------------------|-------"
        echo "${defects_data}" | jq -r '.content[]? | 
            "\(.id) | \(.name[0:30]) | \(if .closed then "Closed" else "Open" end)"' | head -5
    fi
}

# Function to generate dashboard
generate_dashboard() {
    local limit="${1:-5}"
    
    echo ""
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║                    📊 QA Quality Dashboard                     ║"
    echo "║                   Last ${limit} launches analysis                      ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    
    analyze_trends "${limit}"
    echo ""
    find_unstable_tests "${limit}"
    echo ""
    show_defects
    
    echo ""
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║                       📈 Summary                               ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo "🔗 TestOps Project: ${ALLURE_ENDPOINT}/project/${ALLURE_PROJECT_ID}"
    echo "📅 Generated: $(date '+%d.%m.%Y %H:%M:%S')"
}

# Main function
main() {
    local action="${1:-dashboard}"
    local limit="${2:-5}"
    
    case "${action}" in
        "dashboard")
            generate_dashboard "${limit}"
            ;;
        "trends")
            analyze_trends "${limit}"
            ;;
        "unstable")
            find_unstable_tests "${limit}"
            ;;
        "defects")
            show_defects
            ;;
        "help"|*)
            echo "Usage: $0 {dashboard|trends|unstable|defects} [limit]"
            echo ""
            echo "Commands:"
            echo "  dashboard [limit]  - Full quality dashboard (default: 5 launches)"
            echo "  trends [limit]     - Success rate trends"
            echo "  unstable [limit]   - Most unstable tests"
            echo "  defects           - Defect analysis"
            echo ""
            echo "Examples:"
            echo "  $0 dashboard 10   - Dashboard for last 10 launches"
            echo "  $0 trends 20      - Trends for last 20 launches"
            exit 1
            ;;
    esac
}

# Check dependencies
if ! command -v jq &> /dev/null; then
    echo "Error: jq is required but not installed"
    exit 1
fi

if ! command -v curl &> /dev/null; then
    echo "Error: curl is required but not installed"
    exit 1
fi

# Run
main "$@"
