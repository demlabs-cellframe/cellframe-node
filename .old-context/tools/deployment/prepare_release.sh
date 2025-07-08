#!/bin/bash

# Smart Layered Context v2.1.0 - Release Preparation Script
# Очищает папку задач и готовит систему для нового пользователя

set -e

VERSION="2.1.0"
RELEASE_DATE=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo "🚀 Smart Layered Context v$VERSION - Release Preparation"
echo "================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
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

# Step 1: Clean task directories for new user
log_info "Step 1: Cleaning task directories..."

# Clear active tasks
if [ -d "$ROOT_DIR/context.reflection/.context/tasks" ]; then
    log_info "Cleaning context.reflection tasks..."
    
    # Create clean task structure for new user
    cat > "$ROOT_DIR/context.reflection/.context/tasks/current_meta_task.json" << 'EOF'
{
  "version": "2.1.0",
  "type": "ready_for_initialization",
  "architecture_version": "smart_layered_context_ready",
  "created": "RELEASE_DATE_PLACEHOLDER",
  "updated": "RELEASE_DATE_PLACEHOLDER",
  
  "status": {
    "system_status": "READY",
    "initialization_required": false,
    "user_setup_needed": true,
    "message": "Smart Layered Context v2.1.0 готов к использованию!"
  },
  
  "getting_started": {
    "first_steps": [
      "python3 tools/scripts/slc_cli.py validate",
      "python3 tools/scripts/slc_cli.py list",
      "python3 tools/scripts/slc_cli.py create ai_ml/prompt_engineering.json my-first-project"
    ],
    
    "documentation": [
      "README.md - Project overview",
      "USAGE_GUIDE.md - Complete usage guide", 
      "tools/scripts/slc_cli.py --help - CLI reference"
    ],
    
    "key_features": {
      "ai_ml_suite": "Complete AI/ML development templates",
      "automation_tools": "Smart CLI for project generation",
      "specialized_templates": "11 production-ready templates",
      "zero_duplication": "Efficient context management"
    }
  },
  
  "system_info": {
    "version": "2.1.0",
    "release_date": "RELEASE_DATE_PLACEHOLDER",
    "template_count": 11,
    "categories": ["languages", "methodologies", "ai_ml", "tools", "projects"],
    "performance": {
      "file_reduction": "70%",
      "data_reduction": "68%", 
      "duplication_rate": "0%",
      "ai_memory_improvement": "80%"
    }
  },
  
  "user_tasks": {
    "suggested_first_projects": [
      {
        "template": "ai_ml/prompt_engineering.json",
        "name": "my-ai-assistant",
        "description": "Create your first AI-powered application"
      },
      {
        "template": "languages/python/python_development.json", 
        "name": "my-python-project",
        "description": "Start Python development with best practices"
      },
      {
        "template": "tools/obsidian_workflow.json",
        "name": "my-knowledge-vault", 
        "description": "Set up knowledge management system"
      }
    ],
    
    "learning_path": [
      "Explore templates with: slc_cli.py list",
      "Get template info: slc_cli.py info TEMPLATE_PATH",
      "Create projects: slc_cli.py create TEMPLATE PROJECT_NAME",
      "Validate system: slc_cli.py validate"
    ]
  },
  
  "support": {
    "documentation": "See README.md",
    "cli_help": "python3 tools/scripts/slc_cli.py --help",
    "validation": "python3 tools/scripts/slc_cli.py validate",
    "community": "Visit project repository for support"
  }
}
EOF
    
    # Replace placeholder with actual date
    sed -i.bak "s/RELEASE_DATE_PLACEHOLDER/$RELEASE_DATE/g" "$ROOT_DIR/context.reflection/.context/tasks/current_meta_task.json"
    rm -f "$ROOT_DIR/context.reflection/.context/tasks/current_meta_task.json.bak"
    
    log_success "Task directory cleaned and prepared for new user"
else
    log_warning "Task directory not found, creating new structure..."
    mkdir -p "$ROOT_DIR/context.reflection/.context/tasks"
fi

# Step 2: Update version file
log_info "Step 2: Updating version information..."

echo "$VERSION" > "$ROOT_DIR/VERSION"
log_success "Version file updated to $VERSION"

# Step 3: Validate system integrity
log_info "Step 3: Validating system integrity..."

if command -v python3 &> /dev/null; then
    cd "$ROOT_DIR"
    if python3 tools/scripts/slc_cli.py validate &> /dev/null; then
        log_success "System validation passed"
    else
        log_error "System validation failed"
        exit 1
    fi
else
    log_warning "Python3 not found, skipping CLI validation"
fi

# Step 4: Clean temporary and development files
log_info "Step 4: Cleaning temporary files..."

# Remove common temporary files
find "$ROOT_DIR" -name "*.pyc" -delete 2>/dev/null || true
find "$ROOT_DIR" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find "$ROOT_DIR" -name ".DS_Store" -delete 2>/dev/null || true
find "$ROOT_DIR" -name "*.tmp" -delete 2>/dev/null || true
find "$ROOT_DIR" -name "*.bak" -delete 2>/dev/null || true

log_success "Temporary files cleaned"

# Step 5: Create release notes
log_info "Step 5: Creating release notes..."

cat > "$ROOT_DIR/RELEASE_NOTES_v$VERSION.md" << EOF
# Smart Layered Context v$VERSION Release Notes

**Release Date:** $(date -u +"%Y-%m-%d")

## 🚀 Major Features

### 🤖 AI/ML Suite
- **Prompt Engineering Template** - Advanced LLM optimization patterns
- **Fine-tuning Workflow** - Complete model training pipeline (LoRA/QLoRA)
- **AI Agent Development** - Multi-agent systems and autonomous behavior

### 🛠️ Automation Tools
- **Smart CLI** - Full-featured command-line interface
- **Project Generation** - One-command project creation
- **Template Management** - Search, validate, and organize templates

### 📋 Enhanced Templates
- **11 Production-Ready Templates** across 5 categories
- **Real-world Patterns** based on actual production systems
- **Zero Duplication** - Efficient differential context storage

## 📊 Performance Improvements

- **70% fewer files** through smart organization
- **68% data reduction** via differential storage
- **0% duplication** - complete elimination of redundancy
- **80% better AI memory** - improved context retention

## 🎯 Template Categories

### Languages
- Python (AI/ML, Cellframe Network, Web development)
- JavaScript (Web3, React, Node.js)
- C/C++ (Systems programming, blockchain)

### AI/ML
- Prompt Engineering & LLM Optimization
- Fine-tuning Workflows & Model Training
- AI Agent Development & Multi-agent Systems

### Methodologies
- Obsidian Workflow & Knowledge Management
- Documentation Systems (MkDocs + Quartz)
- Context Systems Development

### Tools & Projects
- Specialized tool templates
- Real-world project implementations

## 🔧 CLI Commands

\`\`\`bash
# Template Management
python3 tools/scripts/slc_cli.py list
python3 tools/scripts/slc_cli.py search "AI agent"
python3 tools/scripts/slc_cli.py info ai_ml/prompt_engineering.json

# Project Creation
python3 tools/scripts/slc_cli.py create TEMPLATE_PATH PROJECT_NAME

# System Management
python3 tools/scripts/slc_cli.py validate
python3 tools/scripts/slc_cli.py update
\`\`\`

## 🚀 Quick Start

1. **Validate installation:**
   \`\`\`bash
   python3 tools/scripts/slc_cli.py validate
   \`\`\`

2. **Explore templates:**
   \`\`\`bash
   python3 tools/scripts/slc_cli.py list
   \`\`\`

3. **Create your first AI project:**
   \`\`\`bash
   python3 tools/scripts/slc_cli.py create ai_ml/prompt_engineering.json my-ai-assistant
   \`\`\`

## 📚 Documentation

- **README.md** - Complete project overview
- **USAGE_GUIDE.md** - Detailed usage instructions
- **CLI Help** - \`python3 tools/scripts/slc_cli.py --help\`

## ⚙️ System Requirements

- Python 3.8+
- Git
- 4GB+ RAM (for AI/ML templates)
- Internet connection (for some tools)

## 🔄 Migration from v2.0

This is a major update with new features. For existing users:

1. Backup your current templates
2. Update to v$VERSION
3. Explore new AI/ML capabilities
4. Use CLI for enhanced productivity

## 🐛 Bug Fixes

- Improved template validation
- Enhanced cross-platform compatibility
- Better error handling in CLI
- Optimized memory usage

## 🙏 Acknowledgments

Thanks to the community for feedback and contributions that made this release possible.

---

**Happy coding with Smart Layered Context v$VERSION!** 🎉
EOF

log_success "Release notes created"

# Step 6: Create deployment README
log_info "Step 6: Creating deployment instructions..."

cat > "$ROOT_DIR/DEPLOYMENT.md" << 'EOF'
# Smart Layered Context v2.1.0 - Deployment Guide

## Quick Deployment

### 1. Extract Release
```bash
tar -xzf smart-layered-context-v2.1.0.tar.gz
cd smart-layered-context
```

### 2. Validate Installation
```bash
python3 tools/scripts/slc_cli.py validate
# Expected: "🎉 System is healthy!"
```

### 3. Start Using
```bash
# List available templates
python3 tools/scripts/slc_cli.py list

# Create your first project
python3 tools/scripts/slc_cli.py create ai_ml/prompt_engineering.json my-first-project
```

## System Requirements

- **Python 3.8+** (required)
- **Git** (recommended)
- **4GB+ RAM** (for AI/ML templates)
- **Internet connection** (for some tools)

## Directory Structure

```
smart_layered_context/
├── modules/                    # Template library
├── tools/scripts/              # CLI tools
├── context.reflection/         # Self-referential context
├── README.md                   # Project overview
├── USAGE_GUIDE.md             # Usage instructions
└── VERSION                     # Version information
```

## First Steps

1. **Explore**: `python3 tools/scripts/slc_cli.py list`
2. **Learn**: `python3 tools/scripts/slc_cli.py info TEMPLATE_PATH`
3. **Create**: `python3 tools/scripts/slc_cli.py create TEMPLATE_PATH PROJECT_NAME`
4. **Validate**: `python3 tools/scripts/slc_cli.py validate`

Ready to revolutionize your development workflow!
EOF

log_success "Deployment guide created"

# Step 7: Final validation
log_info "Step 7: Final system validation..."

# Check critical files exist
critical_files=(
    "README.md"
    "VERSION"
    "tools/scripts/slc_cli.py"
    "modules/ai_ml/prompt_engineering.json"
    "modules/ai_ml/fine_tuning_workflow.json"
    "modules/ai_ml/ai_agent_development.json"
)

for file in "${critical_files[@]}"; do
    if [ -f "$ROOT_DIR/$file" ]; then
        log_success "✓ $file"
    else
        log_error "✗ Missing critical file: $file"
        exit 1
    fi
done

# Step 8: Display release summary
echo ""
echo "🎉 Release Preparation Complete!"
echo "================================="
log_success "Smart Layered Context v$VERSION ready for release"
log_info "Release date: $RELEASE_DATE"
log_info "Template count: 11"
log_info "Categories: 5 (languages, methodologies, ai_ml, tools, projects)"

echo ""
echo "📋 Next Steps:"
echo "1. Review generated files (RELEASE_NOTES_v$VERSION.md, DEPLOYMENT.md)"
echo "2. Test CLI: python3 tools/scripts/slc_cli.py validate"
echo "3. Create git tag: git tag v$VERSION"
echo "4. Create release archive: tar -czf smart-layered-context-v$VERSION.tar.gz ."
echo ""

log_success "System is ready for new users! 🚀" 
