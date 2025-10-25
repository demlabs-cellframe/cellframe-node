#!/bin/bash

# Smart Context Loader for DAP SDK
# Analyzes user query and suggests appropriate context modules to load
# Version 2.0 - Compatible with new Smart Layered Context architecture

CONTEXT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
MANIFEST_FILE="$CONTEXT_DIR/core/manifest.json"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

usage() {
    echo "Usage: $0 [OPTIONS] \"user query\""
    echo
    echo "Smart Context Loader - analyzes your query and suggests relevant modules"
    echo
    echo "Options:"
    echo "  -a, --auto        Auto-load suggested modules without confirmation"
    echo "  -l, --list        List available modules and exit"
    echo "  -v, --verbose     Show detailed analysis"
    echo "  -h, --help        Show this help message"
    echo
    echo "Examples:"
    echo "  $0 \"need to optimize chipmunk performance\""
    echo "  $0 \"working on http server functionality\""
    echo "  $0 \"building and testing the project\""
    echo "  $0 -a \"crypto debugging issue\""
}

list_modules() {
    echo -e "${CYAN}📁 Available Context Modules:${NC}"
    echo
    echo -e "${GREEN}CORE (always loaded):${NC}"
    echo "  📋 core/manifest.json - Smart navigator"
    echo "  📐 core/standards.json - Development standards"
    echo "  🎯 core/project.json - Project information"
    echo
    echo -e "${YELLOW}MODULES (load on demand):${NC}"
    echo "  🔐 modules/crypto.json - Cryptographic components"
    echo "  🏗️  modules/build.json - Build system and testing"
    echo "  ⚙️  modules/core.json - Framework components"
    echo "  🌐 modules/net.json - Network components"
    echo
    echo -e "${BLUE}TASKS:${NC}"
    echo "  🎯 tasks/active.json - Current active task"
    echo "  📚 tasks/history.json - Completed tasks"
    echo
    echo -e "${PURPLE}TOOLS:${NC}"
    echo "  🔧 tools/scripts/ - Automation scripts"
    echo "  🚀 tools/deployment/ - Deployment tools"
}

analyze_query() {
    local query="$1"
    local suggestions=()
    local confidence=()
    local explanations=()
    
    # Convert to lowercase for analysis
    local query_lower=$(echo "$query" | tr '[:upper:]' '[:lower:]')
    
    # Always suggest core files
    suggestions+=("core/manifest.json" "core/standards.json" "core/project.json")
    confidence+=(100 100 100)
    explanations+=("Smart navigator - always needed" "Development standards - always needed" "Project info - always needed")
    
    # Crypto-related keywords
    if echo "$query_lower" | grep -qE "(crypto|chipmunk|signature|encryption|hash|ecdsa|post.?quantum|lattice|multi.?signature|hots)"; then
        suggestions+=("modules/crypto.json")
        confidence+=(95)
        explanations+=("Detected crypto-related work")
        
        # Chipmunk-specific
        if echo "$query_lower" | grep -qE "(chipmunk|post.?quantum|lattice|multi.?signature|hots)"; then
            suggestions+=("tasks/active.json")
            confidence+=(90)
            explanations+=("Chipmunk work detected - current task relevant")
        fi
    fi
    
    # Performance/optimization keywords
    if echo "$query_lower" | grep -qE "(performance|optimization|speed|benchmark|profiling|simd|vectorization|slow|fast)"; then
        suggestions+=("modules/build.json")
        confidence+=(90)
        explanations+=("Performance work detected - build tools needed")
        
        if echo "$query_lower" | grep -qE "(chipmunk|crypto)"; then
            suggestions+=("modules/crypto.json" "tasks/active.json")
            confidence+=(95 85)
            explanations+=("Crypto performance optimization" "Current optimization task")
        fi
    fi
    
    # Build-related keywords
    if echo "$query_lower" | grep -qE "(build|cmake|test|compile|link|debug|release|config)"; then
        suggestions+=("modules/build.json")
        confidence+=(90)
        explanations+=("Build system work detected")
    fi
    
    # Network-related keywords
    if echo "$query_lower" | grep -qE "(network|http|server|client|communication|protocol|json.?rpc|websocket)"; then
        suggestions+=("modules/net.json")
        confidence+=(90)
        explanations+=("Network-related work detected")
    fi
    
    # Core framework keywords
    if echo "$query_lower" | grep -qE "(core|framework|api|structure|architecture|memory|logging)"; then
        suggestions+=("modules/core.json")
        confidence+=(85)
        explanations+=("Core framework work detected")
    fi
    
    # Task management keywords
    if echo "$query_lower" | grep -qE "(task|progress|current|active|working on|status)"; then
        suggestions+=("tasks/active.json")
        confidence+=(80)
        explanations+=("Task-related query detected")
    fi
    
    # Debugging keywords
    if echo "$query_lower" | grep -qE "(debug|error|crash|segfault|memory|gdb|lldb)"; then
        suggestions+=("modules/build.json")
        confidence+=(85)
        explanations+=("Debugging work - build tools needed")
    fi
    
    # Print suggestions to stderr so they don't interfere with file list output
    echo -e "${CYAN}🧠 Smart Analysis Results:${NC}" >&2
    echo >&2
    echo -e "${YELLOW}Query:${NC} \"$query\"" >&2
    echo >&2
    echo -e "${GREEN}📋 Suggested modules to load:${NC}" >&2
    
    local unique_suggestions=()
    local unique_confidence=()
    local unique_explanations=()
    
    # Remove duplicates while preserving order and taking highest confidence
    for i in "${!suggestions[@]}"; do
        local suggestion="${suggestions[$i]}"
        local found=false
        
        for j in "${!unique_suggestions[@]}"; do
            if [[ "${unique_suggestions[$j]}" == "$suggestion" ]]; then
                # Update confidence if higher
                if [[ ${confidence[$i]} -gt ${unique_confidence[$j]} ]]; then
                    unique_confidence[$j]=${confidence[$i]}
                    unique_explanations[$j]="${explanations[$i]}"
                fi
                found=true
                break
            fi
        done
        
        if [[ "$found" == false ]]; then
            unique_suggestions+=("$suggestion")
            unique_confidence+=("${confidence[$i]}")
            unique_explanations+=("${explanations[$i]}")
        fi
    done
    
    # Sort by confidence (descending)
    for i in "${!unique_suggestions[@]}"; do
        for j in $((i+1)) $((${#unique_suggestions[@]}-1)); do
            if [[ ${unique_confidence[$i]} -lt ${unique_confidence[$j]} ]]; then
                # Swap suggestions
                local temp_s="${unique_suggestions[$i]}"
                unique_suggestions[$i]="${unique_suggestions[$j]}"
                unique_suggestions[$j]="$temp_s"
                
                # Swap confidence
                local temp_c=${unique_confidence[$i]}
                unique_confidence[$i]=${unique_confidence[$j]}
                unique_confidence[$j]=$temp_c
                
                # Swap explanations
                local temp_e="${unique_explanations[$i]}"
                unique_explanations[$i]="${unique_explanations[$j]}"
                unique_explanations[$j]="$temp_e"
            fi
        done
    done
    
    # Print sorted results
    for i in "${!unique_suggestions[@]}"; do
        local conf=${unique_confidence[$i]}
        local suggestion="${unique_suggestions[$i]}"
        local explanation="${unique_explanations[$i]}"
        
        if [[ $conf -ge 90 ]]; then
            echo -e "  ${GREEN}🔥 HIGH${NC} ($conf%): $suggestion - $explanation" >&2
        elif [[ $conf -ge 80 ]]; then
            echo -e "  ${YELLOW}⚡ MED${NC}  ($conf%): $suggestion - $explanation" >&2
        else
            echo -e "  ${BLUE}💡 LOW${NC}  ($conf%): $suggestion - $explanation" >&2
        fi
    done
    
    # Return the unique suggestions for loading
    printf '%s\n' "${unique_suggestions[@]}"
}

load_context_files() {
    local files=("$@")
    
    echo
    echo -e "${CYAN}📂 Loading suggested context files...${NC}"
    echo
    
    for file in "${files[@]}"; do
        local full_path="$CONTEXT_DIR/$file"
        if [[ -f "$full_path" ]]; then
            echo -e "${GREEN}✅ Loaded:${NC} $file"
            # In real implementation, this would load the file into your context
            # For now, we just show what would be loaded
        else
            echo -e "${RED}❌ Not found:${NC} $file"
        fi
    done
    
    echo
    echo -e "${GREEN}🎉 Context loading complete!${NC}"
    echo -e "${BLUE}💡 Pro tip:${NC} Use these files in your AI coding assistant for optimal results"
}

# Parse command line arguments
AUTO_LOAD=false
VERBOSE=false
QUERY=""

while [[ $# -gt 0 ]]; do
    case $1 in
        -a|--auto)
            AUTO_LOAD=true
            shift
            ;;
        -l|--list)
            list_modules
            exit 0
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            QUERY="$1"
            shift
            ;;
    esac
done

if [[ -z "$QUERY" ]]; then
    echo -e "${RED}Error: No query provided${NC}"
    echo
    usage
    exit 1
fi

# Check if manifest file exists
if [[ ! -f "$MANIFEST_FILE" ]]; then
    echo -e "${RED}Error: Manifest file not found at $MANIFEST_FILE${NC}"
    echo "Make sure you're running this from the correct directory"
    exit 1
fi

# Analyze query and get suggestions
echo -e "${PURPLE}🎯 DAP SDK Smart Context Loader v2.0${NC}"
echo -e "${PURPLE}======================================${NC}"
echo

# Use portable approach instead of mapfile (which is not available in macOS bash)
suggested_files=()
while IFS= read -r line; do
    suggested_files+=("$line")
done < <(analyze_query "$QUERY")

if [[ ${#suggested_files[@]} -eq 0 ]]; then
    echo -e "${YELLOW}⚠️  No specific suggestions found. Loading core files only.${NC}"
    suggested_files=("core/manifest.json" "core/standards.json" "core/project.json")
fi

# Auto-load suggestions (no interactive prompts)
if [[ "$AUTO_LOAD" == true ]]; then
    load_context_files "${suggested_files[@]}"
else
    echo
    echo -e "${CYAN}💡 Use --auto flag to load automatically${NC}"
    echo -e "${YELLOW}📋 Suggested files listed above - copy paths to load manually${NC}"
    echo
    echo -e "${BLUE}Example with auto-load:${NC}"
    echo "  $0 --auto \"$QUERY\""
fi 