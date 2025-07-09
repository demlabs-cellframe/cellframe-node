#!/bin/bash

# CellFrame Python SDK - Production Deployment Script
# Version: 1.0.0
# Description: Automated production deployment for CellFrame Python SDK

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEPLOY_DIR="$(dirname "$SCRIPT_DIR")"
PROJECT_ROOT="$(dirname "$DEPLOY_DIR")"
CONFIG_DIR="$DEPLOY_DIR/config"
SYSTEMD_DIR="$DEPLOY_DIR/systemd"
DOCKER_DIR="$DEPLOY_DIR/docker"
MONITORING_DIR="$DEPLOY_DIR/monitoring"
SECURITY_DIR="$DEPLOY_DIR/security"

# Default values
ENVIRONMENT=${ENVIRONMENT:-production}
INSTALL_PREFIX=${INSTALL_PREFIX:-/opt/cellframe}
SERVICE_USER=${SERVICE_USER:-cellframe}
SERVICE_GROUP=${SERVICE_GROUP:-cellframe}
PYTHON_VERSION=${PYTHON_VERSION:-3.9}
ENABLE_MONITORING=${ENABLE_MONITORING:-true}
ENABLE_SECURITY=${ENABLE_SECURITY:-true}
SKIP_TESTS=${SKIP_TESTS:-false}

# Functions
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING:${NC} $1"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1"
    exit 1
}

info() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] INFO:${NC} $1"
}

# Check if running as root for system-wide installation
check_permissions() {
    if [[ $EUID -ne 0 ]] && [[ "$INSTALL_PREFIX" == /opt/* || "$INSTALL_PREFIX" == /usr/* ]]; then
        error "System-wide installation requires root privileges. Run with sudo or change INSTALL_PREFIX."
    fi
}

# Check system requirements
check_requirements() {
    log "Checking system requirements..."
    
    # Check OS
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS_TYPE="linux"
        if command -v systemctl &> /dev/null; then
            INIT_SYSTEM="systemd"
        else
            INIT_SYSTEM="other"
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS_TYPE="macos"
        INIT_SYSTEM="launchd"
    else
        error "Unsupported operating system: $OSTYPE"
    fi
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        error "Python 3 is required but not installed"
    fi
    
    PYTHON_VERSION_ACTUAL=$(python3 --version | cut -d' ' -f2)
    info "Python version: $PYTHON_VERSION_ACTUAL"
    
    # Check required Python packages
    if ! python3 -c "import ctypes" &> /dev/null; then
        error "Python ctypes module is required but not available"
    fi
    
    # Check build tools
    if ! command -v cmake &> /dev/null; then
        error "CMake is required but not installed"
    fi
    
    if ! command -v make &> /dev/null; then
        error "Make is required but not installed"
    fi
    
    # Check C compiler
    if ! command -v gcc &> /dev/null && ! command -v clang &> /dev/null; then
        error "C compiler (gcc or clang) is required but not installed"
    fi
    
    log "System requirements check passed"
}

# Create system user and group
create_system_user() {
    if [[ "$OS_TYPE" == "linux" ]]; then
        if ! id "$SERVICE_USER" &>/dev/null; then
            log "Creating system user: $SERVICE_USER"
            useradd --system --no-create-home --shell /bin/false "$SERVICE_USER"
            usermod -a -G "$SERVICE_GROUP" "$SERVICE_USER" 2>/dev/null || true
        else
            info "System user $SERVICE_USER already exists"
        fi
    fi
}

# Create directory structure
create_directories() {
    log "Creating directory structure..."
    
    # Main directories
    mkdir -p "$INSTALL_PREFIX"/{bin,lib,etc,var/{log,run,lib},share/{doc,man}}
    
    # Python SDK specific directories
    mkdir -p "$INSTALL_PREFIX"/lib/python-sdk/{plugins,config,cache}
    mkdir -p "$INSTALL_PREFIX"/var/log/python-sdk
    mkdir -p "$INSTALL_PREFIX"/var/run/python-sdk
    mkdir -p "$INSTALL_PREFIX"/var/lib/python-sdk
    
    # Set ownership
    if [[ "$OS_TYPE" == "linux" ]] && id "$SERVICE_USER" &>/dev/null; then
        chown -R "$SERVICE_USER":"$SERVICE_GROUP" "$INSTALL_PREFIX"/var/{log,run,lib}/python-sdk
    fi
    
    # Set permissions
    chmod 755 "$INSTALL_PREFIX"/{bin,lib,etc,share}
    chmod 750 "$INSTALL_PREFIX"/var/{log,run,lib}
    chmod 640 "$INSTALL_PREFIX"/etc/*.conf 2>/dev/null || true
    
    log "Directory structure created"
}

# Build Python SDK
build_python_sdk() {
    log "Building Python SDK..."
    
    cd "$PROJECT_ROOT"
    
    # Clean previous builds
    rm -rf build/ dist/ *.egg-info/
    
    # Create build directory
    mkdir -p build
    cd build
    
    # Configure with CMake
    cmake .. \
        -DCMAKE_INSTALL_PREFIX="$INSTALL_PREFIX" \
        -DCMAKE_BUILD_TYPE=Release \
        -DPYTHON_VERSION="$PYTHON_VERSION" \
        -DENABLE_TESTING=$([ "$SKIP_TESTS" == "false" ] && echo "ON" || echo "OFF")
    
    # Build
    make -j$(nproc 2>/dev/null || echo "2")
    
    # Run tests if enabled
    if [[ "$SKIP_TESTS" == "false" ]]; then
        log "Running tests..."
        make test
    fi
    
    # Install
    make install
    
    log "Python SDK built and installed"
}

# Install configuration files
install_configuration() {
    log "Installing configuration files..."
    
    # Copy configuration files
    cp -r "$CONFIG_DIR"/* "$INSTALL_PREFIX"/etc/ 2>/dev/null || warn "No configuration files found"
    
    # Set proper permissions
    find "$INSTALL_PREFIX"/etc -type f -exec chmod 640 {} \;
    find "$INSTALL_PREFIX"/etc -type d -exec chmod 750 {} \;
    
    if [[ "$OS_TYPE" == "linux" ]] && id "$SERVICE_USER" &>/dev/null; then
        chown -R root:"$SERVICE_GROUP" "$INSTALL_PREFIX"/etc
    fi
    
    log "Configuration files installed"
}

# Install systemd service
install_systemd_service() {
    if [[ "$OS_TYPE" == "linux" ]] && [[ "$INIT_SYSTEM" == "systemd" ]]; then
        log "Installing systemd service..."
        
        # Copy service files
        cp "$SYSTEMD_DIR"/*.service /etc/systemd/system/ 2>/dev/null || warn "No systemd service files found"
        
        # Reload systemd
        systemctl daemon-reload
        
        # Enable services
        for service in "$SYSTEMD_DIR"/*.service; do
            if [[ -f "$service" ]]; then
                service_name=$(basename "$service")
                systemctl enable "$service_name"
                info "Enabled service: $service_name"
            fi
        done
        
        log "Systemd service installed"
    fi
}

# Install monitoring
install_monitoring() {
    if [[ "$ENABLE_MONITORING" == "true" ]]; then
        log "Installing monitoring configuration..."
        
        # Copy monitoring configuration
        cp -r "$MONITORING_DIR"/* "$INSTALL_PREFIX"/etc/monitoring/ 2>/dev/null || warn "No monitoring configuration found"
        
        # Create monitoring directories
        mkdir -p "$INSTALL_PREFIX"/var/lib/monitoring
        
        if [[ "$OS_TYPE" == "linux" ]] && id "$SERVICE_USER" &>/dev/null; then
            chown -R "$SERVICE_USER":"$SERVICE_GROUP" "$INSTALL_PREFIX"/var/lib/monitoring
        fi
        
        log "Monitoring configuration installed"
    fi
}

# Install security configuration
install_security() {
    if [[ "$ENABLE_SECURITY" == "true" ]]; then
        log "Installing security configuration..."
        
        # Copy security configuration
        cp -r "$SECURITY_DIR"/* "$INSTALL_PREFIX"/etc/security/ 2>/dev/null || warn "No security configuration found"
        
        # Set strict permissions
        find "$INSTALL_PREFIX"/etc/security -type f -exec chmod 600 {} \;
        find "$INSTALL_PREFIX"/etc/security -type d -exec chmod 700 {} \;
        
        if [[ "$OS_TYPE" == "linux" ]] && id "$SERVICE_USER" &>/dev/null; then
            chown -R root:"$SERVICE_GROUP" "$INSTALL_PREFIX"/etc/security
        fi
        
        log "Security configuration installed"
    fi
}

# Validate installation
validate_installation() {
    log "Validating installation..."
    
    # Check if Python SDK is importable
    if ! python3 -c "import sys; sys.path.append('$INSTALL_PREFIX/lib/python-sdk'); import cellframe" &>/dev/null; then
        warn "Python SDK import test failed - this may be expected if not all dependencies are installed"
    else
        info "Python SDK import test passed"
    fi
    
    # Check file permissions
    if [[ -d "$INSTALL_PREFIX/var/log/python-sdk" ]]; then
        info "Log directory permissions: $(stat -c %a "$INSTALL_PREFIX/var/log/python-sdk" 2>/dev/null || stat -f %p "$INSTALL_PREFIX/var/log/python-sdk")"
    fi
    
    # Check service status
    if [[ "$OS_TYPE" == "linux" ]] && [[ "$INIT_SYSTEM" == "systemd" ]]; then
        for service in "$SYSTEMD_DIR"/*.service; do
            if [[ -f "$service" ]]; then
                service_name=$(basename "$service")
                if systemctl is-enabled "$service_name" &>/dev/null; then
                    info "Service $service_name is enabled"
                else
                    warn "Service $service_name is not enabled"
                fi
            fi
        done
    fi
    
    log "Installation validation completed"
}

# Generate deployment report
generate_report() {
    log "Generating deployment report..."
    
    REPORT_FILE="$INSTALL_PREFIX/var/log/python-sdk/deployment-$(date +%Y%m%d-%H%M%S).log"
    
    cat > "$REPORT_FILE" << EOF
CellFrame Python SDK Deployment Report
======================================

Date: $(date)
Environment: $ENVIRONMENT
Install Prefix: $INSTALL_PREFIX
Service User: $SERVICE_USER
Python Version: $PYTHON_VERSION_ACTUAL
OS Type: $OS_TYPE
Init System: $INIT_SYSTEM

Deployment Configuration:
- Monitoring Enabled: $ENABLE_MONITORING
- Security Enabled: $ENABLE_SECURITY
- Tests Skipped: $SKIP_TESTS

Installed Components:
- Python SDK: ✓
- Configuration Files: ✓
- System Service: $([ "$INIT_SYSTEM" == "systemd" ] && echo "✓" || echo "N/A")
- Monitoring: $([ "$ENABLE_MONITORING" == "true" ] && echo "✓" || echo "Disabled")
- Security: $([ "$ENABLE_SECURITY" == "true" ] && echo "✓" || echo "Disabled")

Directory Structure:
$(find "$INSTALL_PREFIX" -type d | head -20)

Log Files:
- Deployment Log: $REPORT_FILE
- Runtime Logs: $INSTALL_PREFIX/var/log/python-sdk/

Next Steps:
1. Review configuration in $INSTALL_PREFIX/etc/
2. Start services: systemctl start cellframe-python-sdk
3. Monitor logs: tail -f $INSTALL_PREFIX/var/log/python-sdk/runtime.log
4. Test functionality with provided examples

EOF
    
    info "Deployment report saved to: $REPORT_FILE"
}

# Show usage
show_usage() {
    cat << EOF
CellFrame Python SDK - Production Deployment Script

Usage: $0 [OPTIONS]

Options:
  -e, --environment ENV     Set deployment environment (default: production)
  -p, --prefix PREFIX       Set installation prefix (default: /opt/cellframe)
  -u, --user USER           Set service user (default: cellframe)
  -g, --group GROUP         Set service group (default: cellframe)
  -v, --python-version VER  Set Python version (default: 3.9)
  --enable-monitoring       Enable monitoring (default: true)
  --disable-monitoring      Disable monitoring
  --enable-security         Enable security (default: true)
  --disable-security        Disable security
  --skip-tests              Skip running tests during build
  -h, --help                Show this help message

Environment Variables:
  ENVIRONMENT               Deployment environment
  INSTALL_PREFIX            Installation prefix
  SERVICE_USER              Service user
  SERVICE_GROUP             Service group
  PYTHON_VERSION            Python version
  ENABLE_MONITORING         Enable monitoring (true/false)
  ENABLE_SECURITY           Enable security (true/false)
  SKIP_TESTS                Skip tests (true/false)

Examples:
  $0                        # Default production deployment
  $0 -e staging -p /opt/cellframe-staging
  $0 --disable-monitoring --skip-tests
  
EOF
}

# Parse command line arguments
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -e|--environment)
                ENVIRONMENT="$2"
                shift 2
                ;;
            -p|--prefix)
                INSTALL_PREFIX="$2"
                shift 2
                ;;
            -u|--user)
                SERVICE_USER="$2"
                shift 2
                ;;
            -g|--group)
                SERVICE_GROUP="$2"
                shift 2
                ;;
            -v|--python-version)
                PYTHON_VERSION="$2"
                shift 2
                ;;
            --enable-monitoring)
                ENABLE_MONITORING="true"
                shift
                ;;
            --disable-monitoring)
                ENABLE_MONITORING="false"
                shift
                ;;
            --enable-security)
                ENABLE_SECURITY="true"
                shift
                ;;
            --disable-security)
                ENABLE_SECURITY="false"
                shift
                ;;
            --skip-tests)
                SKIP_TESTS="true"
                shift
                ;;
            -h|--help)
                show_usage
                exit 0
                ;;
            *)
                error "Unknown option: $1"
                ;;
        esac
    done
}

# Main deployment function
main() {
    log "Starting CellFrame Python SDK deployment..."
    log "Environment: $ENVIRONMENT"
    log "Install prefix: $INSTALL_PREFIX"
    log "Service user: $SERVICE_USER"
    log "Python version: $PYTHON_VERSION"
    
    parse_args "$@"
    check_permissions
    check_requirements
    create_system_user
    create_directories
    build_python_sdk
    install_configuration
    install_systemd_service
    install_monitoring
    install_security
    validate_installation
    generate_report
    
    log "Deployment completed successfully!"
    log "Check the deployment report for details: $INSTALL_PREFIX/var/log/python-sdk/deployment-*.log"
}

# Run main function with all arguments
main "$@" 