#!/bin/bash

# Create New Task Script for DAP SDK Smart Context
# Creates a new task from template and manages task lifecycle
# Version 2.0

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

CONTEXT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
TEMPLATE_FILE="$CONTEXT_DIR/tasks/templates/task_template.json"
ACTIVE_FILE="$CONTEXT_DIR/tasks/active.json"
HISTORY_FILE="$CONTEXT_DIR/tasks/history.json"

usage() {
    echo "Usage: $0 [OPTIONS] \"Task Title\""
    echo
    echo "Create a new task from template"
    echo
    echo "Options:"
    echo "  -c, --category    Task category (crypto_development|performance_optimization|infrastructure|testing|documentation)"
    echo "  -p, --priority    Priority (LOW|MEDIUM|HIGH|CRITICAL)"
    echo "  -a, --archive     Archive current active task to history first"
    echo "  -f, --force       Overwrite existing active task without archiving"
    echo "  -h, --help        Show this help message"
    echo
    echo "Examples:"
    echo "  $0 \"Optimize Chipmunk Phase 3\""
    echo "  $0 --category crypto_development --priority HIGH \"SIMD Optimization\""
    echo "  $0 --archive \"New networking feature\""
}

log_info() {
    echo -e "${CYAN}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

archive_current_task() {
    if [[ -f "$ACTIVE_FILE" ]]; then
        log_info "Archiving current active task..."
        
        # Add completion timestamp to current task
        local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
        local temp_file=$(mktemp)
        
        # Add completion info to current task
        jq --arg timestamp "$timestamp" '. + {"completion_date": $timestamp, "status": "COMPLETED"}' "$ACTIVE_FILE" > "$temp_file"
        
        # Append to history
        echo "," >> "$HISTORY_FILE" 2>/dev/null || echo "[" > "$HISTORY_FILE"
        cat "$temp_file" >> "$HISTORY_FILE"
        echo "]" >> "$HISTORY_FILE"
        
        # Fix JSON formatting
        jq '.' "$HISTORY_FILE" > "$temp_file" && mv "$temp_file" "$HISTORY_FILE"
        
        rm -f "$temp_file"
        log_success "Current task archived to history"
    else
        log_info "No active task to archive"
    fi
}

create_new_task() {
    local title="$1"
    local category="$2"
    local priority="$3"
    
    if [[ ! -f "$TEMPLATE_FILE" ]]; then
        log_error "Template file not found: $TEMPLATE_FILE"
        return 1
    fi
    
    log_info "Creating new task: $title"
    
    # Generate task ID
    local task_id="TASK_$(date +%Y%m%d_%H%M%S)"
    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    
    # Create new task from template
    jq --arg id "$task_id" \
       --arg title "$title" \
       --arg category "$category" \
       --arg priority "$priority" \
       --arg timestamp "$timestamp" \
       '.task_template.id = $id |
        .task_template.title = $title |
        .task_template.category = $category |
        .task_template.priority = $priority |
        .task_template.metadata.created = $timestamp |
        .task_template.metadata.updated = $timestamp' \
       "$TEMPLATE_FILE" > "$ACTIVE_FILE"
    
    log_success "New task created: $ACTIVE_FILE"
    log_info "Task ID: $task_id"
    log_info "Category: $category"
    log_info "Priority: $priority"
}

# Parse arguments
TITLE=""
CATEGORY="crypto_development"
PRIORITY="MEDIUM"
ARCHIVE=false
FORCE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -c|--category)
            CATEGORY="$2"
            shift 2
            ;;
        -p|--priority)
            PRIORITY="$2"
            shift 2
            ;;
        -a|--archive)
            ARCHIVE=true
            shift
            ;;
        -f|--force)
            FORCE=true
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            TITLE="$1"
            shift
            ;;
    esac
done

if [[ -z "$TITLE" ]]; then
    log_error "Task title is required"
    usage
    exit 1
fi

# Check if active task exists
if [[ -f "$ACTIVE_FILE" ]] && [[ "$FORCE" != true ]] && [[ "$ARCHIVE" != true ]]; then
    log_error "Active task already exists: $ACTIVE_FILE"
    log_error "Use --archive to archive current task or --force to overwrite"
    exit 1
fi

echo -e "${PURPLE}🆕 Creating New Task${NC}"
echo -e "${PURPLE}===================${NC}"
echo

# Archive current task if requested
if [[ "$ARCHIVE" == true ]]; then
    archive_current_task
fi

# Create new task
create_new_task "$TITLE" "$CATEGORY" "$PRIORITY"

echo
log_success "🎉 New task created successfully!"
echo
log_info "Next steps:"
echo "  1. Edit $ACTIVE_FILE to add task details"
echo "  2. Load the task context: ./tools/scripts/smart_context_loader.sh --auto \"task progress\""
echo "  3. Start working on your task!" 