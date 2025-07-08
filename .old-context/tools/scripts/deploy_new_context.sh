#!/bin/bash

# DAP SDK Smart Context Deployment Script
# Deploys the new Smart Layered Context architecture to other projects
# Version 2.0

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SOURCE_CONTEXT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
TARGET_DIR=""
PROJECT_NAME=""
DRY_RUN=false
BACKUP=true
FORCE=false

usage() {
    echo "Usage: $0 [OPTIONS] TARGET_DIRECTORY PROJECT_NAME"
    echo
    echo "Deploy DAP SDK Smart Layered Context architecture to another project"
    echo
    echo "Arguments:"
    echo "  TARGET_DIRECTORY  Target directory to deploy context"
    echo "  PROJECT_NAME      Name of the target project"
    echo
    echo "Options:"
    echo "  -d, --dry-run     Show what would be done without making changes"
    echo "  -n, --no-backup   Don't create backup of existing context"
    echo "  -f, --force       Overwrite existing context without confirmation"
    echo "  -h, --help        Show this help message"
    echo
    echo "Examples:"
    echo "  $0 /path/to/project \"My Project\""
    echo "  $0 --dry-run /path/to/project \"Test Project\""
    echo "  $0 --force --no-backup /path/to/project \"Quick Deploy\""
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

log_step() {
    echo -e "${PURPLE}🔧 $1${NC}"
}

check_prerequisites() {
    log_step "Checking prerequisites..."
    
    # Check if source context exists
    if [[ ! -d "$SOURCE_CONTEXT_DIR" ]]; then
        log_error "Source context directory not found: $SOURCE_CONTEXT_DIR"
        return 1
    fi
    
    # Check if manifest exists
    if [[ ! -f "$SOURCE_CONTEXT_DIR/core/manifest.json" ]]; then
        log_error "Source manifest not found: $SOURCE_CONTEXT_DIR/core/manifest.json"
        log_error "This doesn't appear to be a valid Smart Layered Context"
        return 1
    fi
    
    # Check target directory
    if [[ ! -d "$TARGET_DIR" ]]; then
        log_error "Target directory does not exist: $TARGET_DIR"
        return 1
    fi
    
    # Check if target is writable
    if [[ ! -w "$TARGET_DIR" ]]; then
        log_error "Target directory is not writable: $TARGET_DIR"
        return 1
    fi
    
    log_success "Prerequisites check passed"
    return 0
}

create_backup() {
    local target_context="$TARGET_DIR/context"
    
    if [[ -d "$target_context" ]]; then
        local backup_dir="$target_context.backup.$(date +%Y%m%d_%H%M%S)"
        
        if [[ "$DRY_RUN" == true ]]; then
            log_info "Would create backup: $backup_dir"
        else
            log_step "Creating backup of existing context..."
            cp -r "$target_context" "$backup_dir"
            log_success "Backup created: $backup_dir"
        fi
    else
        log_info "No existing context to backup"
    fi
}

customize_for_project() {
    local file="$1"
    local project_name="$2"
    
    if [[ "$DRY_RUN" == true ]]; then
        log_info "Would customize $file for project: $project_name"
        return 0
    fi
    
    # Customize project.json
    if [[ "$file" == *"/core/project.json" ]]; then
        log_step "Customizing project.json for $project_name..."
        
        # Replace project information
        sed -i.tmp "s/\"name\": \"DAP SDK\"/\"name\": \"$project_name\"/" "$file"
        sed -i.tmp "s/\"full_name\": \"Cellframe DAP SDK\"/\"full_name\": \"$project_name\"/" "$file"
        sed -i.tmp "s/\"project\": \"DAP SDK - Cellframe\"/\"project\": \"$project_name\"/" "$file"
        
        # Update timestamps
        local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
        sed -i.tmp "s/\"created\": \".*\"/\"created\": \"$timestamp\"/" "$file"
        sed -i.tmp "s/\"updated\": \".*\"/\"updated\": \"$timestamp\"/" "$file"
        
        # Remove temporary file
        rm -f "$file.tmp"
        
        log_success "Project.json customized"
    fi
    
    # Customize manifest.json
    if [[ "$file" == *"/core/manifest.json" ]]; then
        log_step "Customizing manifest.json for $project_name..."
        
        # Replace project name
        sed -i.tmp "s/\"project\": \"DAP SDK - Cellframe\"/\"project\": \"$project_name\"/" "$file"
        
        # Update timestamps
        local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
        sed -i.tmp "s/\"created\": \".*\"/\"created\": \"$timestamp\"/" "$file"
        sed -i.tmp "s/\"updated\": \".*\"/\"updated\": \"$timestamp\"/" "$file"
        
        # Remove temporary file
        rm -f "$file.tmp"
        
        log_success "Manifest.json customized"
    fi
    
    # Update other files with timestamps
    if [[ "$file" == *".json" ]]; then
        local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
        sed -i.tmp "s/\"created\": \".*\"/\"created\": \"$timestamp\"/" "$file" 2>/dev/null || true
        sed -i.tmp "s/\"updated\": \".*\"/\"updated\": \"$timestamp\"/" "$file" 2>/dev/null || true
        rm -f "$file.tmp" 2>/dev/null || true
    fi
}

deploy_context() {
    local target_context="$TARGET_DIR/context"
    
    log_step "Deploying Smart Layered Context architecture..."
    
    if [[ "$DRY_RUN" == true ]]; then
        log_info "DRY RUN - Would deploy to: $target_context"
        log_info "Source structure:"
        find "$SOURCE_CONTEXT_DIR" -type f -name "*.json" -o -name "*.sh" | head -20
        return 0
    fi
    
    # Create target context directory
    mkdir -p "$target_context"
    
    # Copy core architecture
    log_step "Copying core architecture..."
    cp -r "$SOURCE_CONTEXT_DIR/core" "$target_context/"
    cp -r "$SOURCE_CONTEXT_DIR/modules" "$target_context/"
    cp -r "$SOURCE_CONTEXT_DIR/tasks" "$target_context/"
    cp -r "$SOURCE_CONTEXT_DIR/tools" "$target_context/"
    cp -r "$SOURCE_CONTEXT_DIR/docs" "$target_context/"
    
    # Copy documentation
    for doc in new_context_architecture.md reorganization_plan.md summary_new_architecture.md; do
        if [[ -f "$SOURCE_CONTEXT_DIR/$doc" ]]; then
            cp "$SOURCE_CONTEXT_DIR/$doc" "$target_context/"
        fi
    done
    
    log_success "Architecture deployed"
    
    # Customize for target project
    log_step "Customizing for project: $PROJECT_NAME"
    
    find "$target_context" -name "*.json" | while read -r file; do
        customize_for_project "$file" "$PROJECT_NAME"
    done
    
    log_success "Project customization complete"
}

make_executable() {
    local target_context="$TARGET_DIR/context"
    
    if [[ "$DRY_RUN" == true ]]; then
        log_info "Would make scripts executable in: $target_context/tools/scripts/"
        return 0
    fi
    
    log_step "Making scripts executable..."
    
    find "$target_context/tools/scripts" -name "*.sh" -exec chmod +x {} \; 2>/dev/null || true
    find "$target_context/tools/deployment" -name "*.sh" -exec chmod +x {} \; 2>/dev/null || true
    
    log_success "Scripts made executable"
}

create_deployment_report() {
    local target_context="$TARGET_DIR/context"
    local report_file="$target_context/deployment_report.md"
    
    if [[ "$DRY_RUN" == true ]]; then
        log_info "Would create deployment report: $report_file"
        return 0
    fi
    
    log_step "Creating deployment report..."
    
    cat > "$report_file" << EOF
# Smart Layered Context Deployment Report

**Project:** $PROJECT_NAME  
**Deployed to:** $target_context  
**Deployment date:** $(date)  
**Architecture version:** 2.0  

## Deployment Summary

✅ **Successfully deployed Smart Layered Context architecture**

### Components Deployed

#### Core Layer (Always Loaded)
- 📋 core/manifest.json - Smart navigator
- 📐 core/standards.json - Development standards  
- 🎯 core/project.json - Project information

#### Modules Layer (On-Demand)
- 🔐 modules/crypto.json - Cryptographic components
- 🏗️ modules/build.json - Build system and testing
- ⚙️ modules/core.json - Framework components  
- 🌐 modules/net.json - Network components

#### Tasks Layer
- 🎯 tasks/active.json - Current task tracking
- 📚 tasks/history.json - Completed tasks
- 📝 tasks/templates/ - Task templates

#### Tools Layer
- 🔧 tools/scripts/ - Automation scripts
- 🚀 tools/deployment/ - Deployment tools
- 📋 tools/templates/ - Project templates

#### Documentation
- 📖 docs/ - User guides and documentation

### Next Steps

1. **Initialize your project context:**
   \`\`\`bash
   cd $target_context
   ./tools/scripts/smart_context_loader.sh --list
   \`\`\`

2. **Load context for your work:**
   \`\`\`bash
   ./tools/scripts/smart_context_loader.sh "your work description"
   \`\`\`

3. **Customize for your project needs:**
   - Update tasks/active.json with your current task
   - Modify modules to match your project structure
   - Customize tools/scripts for your workflow

4. **Use with AI coding assistants:**
   - Load core context: manifest.json + standards.json + project.json
   - Add relevant modules based on your work
   - Keep context files updated as project evolves

### Architecture Benefits

- 📉 **Reduced context size:** ~60% reduction vs old structure  
- 🧠 **Smart loading:** AI gets relevant context automatically
- 🔄 **No duplication:** Single source of truth for all information
- 📱 **Scalable:** Add modules without breaking existing workflow
- 🚀 **Deployment ready:** Ready for immediate use

For detailed information, see: new_context_architecture.md

---
*Generated by DAP SDK Smart Context Deployment Script v2.0*
EOF

    log_success "Deployment report created: $report_file"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -d|--dry-run)
            DRY_RUN=true
            shift
            ;;
        -n|--no-backup)
            BACKUP=false
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
            if [[ -z "$TARGET_DIR" ]]; then
                TARGET_DIR="$1"
            elif [[ -z "$PROJECT_NAME" ]]; then
                PROJECT_NAME="$1"
            else
                log_error "Unknown argument: $1"
                usage
                exit 1
            fi
            shift
            ;;
    esac
done

# Validate arguments
if [[ -z "$TARGET_DIR" ]] || [[ -z "$PROJECT_NAME" ]]; then
    log_error "Missing required arguments"
    usage
    exit 1
fi

# Convert to absolute path
TARGET_DIR=$(cd "$TARGET_DIR" && pwd)

# Main deployment process
echo -e "${PURPLE}🚀 DAP SDK Smart Context Deployment${NC}"
echo -e "${PURPLE}====================================${NC}"
echo
echo -e "${CYAN}Source:${NC} $SOURCE_CONTEXT_DIR"
echo -e "${CYAN}Target:${NC} $TARGET_DIR/context"
echo -e "${CYAN}Project:${NC} $PROJECT_NAME"
echo -e "${CYAN}Mode:${NC} $(if [[ "$DRY_RUN" == true ]]; then echo "DRY RUN"; else echo "LIVE DEPLOYMENT"; fi)"
echo

# Check if target context exists and handle accordingly
if [[ -d "$TARGET_DIR/context" ]] && [[ "$FORCE" != true ]] && [[ "$DRY_RUN" != true ]]; then
    log_error "Target context directory already exists: $TARGET_DIR/context"
    log_error "Use --force to overwrite or --dry-run to preview changes"
    log_error "Or manually remove the existing context directory"
    exit 1
fi

# Execute deployment steps
if ! check_prerequisites; then
    exit 1
fi

if [[ "$BACKUP" == true ]]; then
    create_backup
fi

deploy_context
make_executable
create_deployment_report

echo
if [[ "$DRY_RUN" == true ]]; then
    log_info "DRY RUN completed. Use without --dry-run to execute actual deployment."
else
    log_success "🎉 Smart Layered Context deployment completed successfully!"
    echo
    log_info "Next steps:"
    echo "  1. cd $TARGET_DIR/context"
    echo "  2. ./tools/scripts/smart_context_loader.sh --list"
    echo "  3. Start using the new context architecture!"
fi 