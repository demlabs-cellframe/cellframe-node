#!/bin/bash
set -e

PROJECT_ROOT=$(git rev-parse --show-toplevel)
MCP_DIR="$PROJECT_ROOT/.mcp"

echo "Updating MCP context for cellframe-node..."

# Function to update timestamp in JSON file
update_timestamp() {
    local file="$1"
    local timestamp=$(date -Iseconds)
    
    if [ -f "$file" ]; then
        # Use jq if available, otherwise sed
        if command -v jq >/dev/null 2>&1; then
            tmp=$(mktemp)
            jq ".current_context.last_updated = \"$timestamp\"" "$file" > "$tmp"
            mv "$tmp" "$file"
        else
            sed -i.bak "s/\"last_updated\": \"[^\"]*\"/\"last_updated\": \"$timestamp\"/" "$file"
        fi
    fi
}

# Function to update git info
update_git_info() {
    local file="$1"
    local git_hash=$(git rev-parse HEAD)
    local modified_files=$(git status --porcelain | wc -l)
    
    if [ -f "$file" ] && command -v jq >/dev/null 2>&1; then
        tmp=$(mktemp)
        jq ".development.current_commit = \"$git_hash\" | .development.modified_files = $modified_files" "$file" > "$tmp"
        mv "$tmp" "$file"
    fi
}

# Update main project context
echo "Updating main project context..."
update_timestamp "$MCP_DIR/project_metadata.json"
update_git_info "$MCP_DIR/project_metadata.json"

# Update module contexts
for module in dap-sdk cellframe-sdk python-cellframe; do
    if [ -d "$PROJECT_ROOT/$module/.mcp" ]; then
        echo "Updating $module context..."
        module_mcp_file=$(find "$PROJECT_ROOT/$module/.mcp" -name "*.json" | head -1)
        if [ -f "$module_mcp_file" ]; then
            update_timestamp "$module_mcp_file"
        fi
    fi
done

# Generate file structure snapshot
echo "Generating file structure snapshot..."
cat > "$MCP_DIR/cache/file_structure.txt" << EOF
# Generated at $(date)
# Key project files and directories

## Root level
$(find "$PROJECT_ROOT" -maxdepth 1 -type f -name "*.md" -o -name "*.txt" -o -name "*.yml" -o -name "CMakeLists.txt" | sort)

## DAP SDK structure  
$(find "$PROJECT_ROOT/dap-sdk" -name "*.h" | head -20 | sort)

## Cellframe SDK structure
$(find "$PROJECT_ROOT/cellframe-sdk" -name "*.h" | head -20 | sort)

## Python bindings
$(find "$PROJECT_ROOT/python-cellframe" -name "*.py" | head -10 | sort)
EOF

# Generate recent changes summary
echo "Generating recent changes summary..."
git log --oneline -10 --pretty=format:'{"commit": "%H", "date": "%ai", "message": "%s"}' > "$MCP_DIR/cache/recent_commits.jsonl" 2>/dev/null || true

echo "MCP context update completed successfully!"
echo "Updated files:"
echo "  - $MCP_DIR/project_metadata.json"
echo "  - Module-specific MCP files"
echo "  - $MCP_DIR/cache/file_structure.txt"
echo "  - $MCP_DIR/cache/recent_commits.jsonl" 