#!/bin/bash

# CellFrame Python SDK - Environment Setup Script
# Version: 1.0.0
# Description: Prepare production environment for CellFrame Python SDK

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

# Default values
ENVIRONMENT=${ENVIRONMENT:-production}
INSTALL_PREFIX=${INSTALL_PREFIX:-/opt/cellframe}
SERVICE_USER=${SERVICE_USER:-cellframe}
SERVICE_GROUP=${SERVICE_GROUP:-cellframe}
PYTHON_VERSION=${PYTHON_VERSION:-3.9}
SETUP_MONITORING=${SETUP_MONITORING:-true}
SETUP_SECURITY=${SETUP_SECURITY:-true}
SETUP_DOCKER=${SETUP_DOCKER:-false}
SETUP_FIREWALL=${SETUP_FIREWALL:-true}

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

# Detect OS
detect_os() {
    if [[ -f /etc/os-release ]]; then
        . /etc/os-release
        OS=$ID
        VER=$VERSION_ID
    elif [[ -f /etc/redhat-release ]]; then
        OS="centos"
        VER=$(cat /etc/redhat-release | grep -oE '[0-9]+' | head -1)
    elif [[ -f /etc/debian_version ]]; then
        OS="debian"
        VER=$(cat /etc/debian_version)
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
        VER=$(sw_vers -productVersion)
    else
        error "Cannot detect operating system"
    fi
    
    log "Detected OS: $OS $VER"
}

# Check if running as root
check_root() {
    if [[ $EUID -ne 0 ]]; then
        error "This script must be run as root"
    fi
}

# Update package manager
update_packages() {
    log "Updating package manager..."
    
    case $OS in
        ubuntu|debian)
            apt-get update -y
            apt-get upgrade -y
            ;;
        centos|rhel|fedora)
            yum update -y
            ;;
        arch)
            pacman -Syu --noconfirm
            ;;
        macos)
            if command -v brew &> /dev/null; then
                brew update
                brew upgrade
            else
                warn "Homebrew not found. Please install Homebrew first."
            fi
            ;;
        *)
            warn "Package manager update not implemented for $OS"
            ;;
    esac
    
    log "Package manager updated"
}

# Install system dependencies
install_system_dependencies() {
    log "Installing system dependencies..."
    
    case $OS in
        ubuntu|debian)
            apt-get install -y \
                python3 \
                python3-dev \
                python3-pip \
                python3-venv \
                build-essential \
                cmake \
                make \
                gcc \
                g++ \
                libc6-dev \
                libssl-dev \
                libffi-dev \
                libsqlite3-dev \
                libreadline-dev \
                zlib1g-dev \
                libbz2-dev \
                libncurses5-dev \
                libgdbm-dev \
                libnss3-dev \
                liblzma-dev \
                curl \
                wget \
                git \
                ca-certificates \
                sudo \
                systemd \
                logrotate \
                rsyslog \
                fail2ban \
                ufw \
                htop \
                vim \
                nano
            ;;
        centos|rhel|fedora)
            yum install -y \
                python3 \
                python3-devel \
                python3-pip \
                gcc \
                gcc-c++ \
                make \
                cmake \
                openssl-devel \
                libffi-devel \
                sqlite-devel \
                readline-devel \
                zlib-devel \
                bzip2-devel \
                ncurses-devel \
                gdbm-devel \
                nss-devel \
                xz-devel \
                curl \
                wget \
                git \
                ca-certificates \
                sudo \
                systemd \
                logrotate \
                rsyslog \
                fail2ban \
                firewalld \
                htop \
                vim \
                nano
            ;;
        arch)
            pacman -S --noconfirm \
                python \
                python-pip \
                base-devel \
                cmake \
                openssl \
                libffi \
                sqlite \
                readline \
                zlib \
                bzip2 \
                ncurses \
                gdbm \
                nss \
                xz \
                curl \
                wget \
                git \
                ca-certificates \
                sudo \
                systemd \
                logrotate \
                rsyslog \
                fail2ban \
                ufw \
                htop \
                vim \
                nano
            ;;
        macos)
            if command -v brew &> /dev/null; then
                brew install \
                    python@3.9 \
                    cmake \
                    openssl \
                    libffi \
                    sqlite \
                    readline \
                    zlib \
                    bzip2 \
                    ncurses \
                    gdbm \
                    xz \
                    curl \
                    wget \
                    git \
                    htop \
                    vim \
                    nano
            else
                error "Homebrew is required for macOS installation"
            fi
            ;;
        *)
            error "System dependencies installation not implemented for $OS"
            ;;
    esac
    
    log "System dependencies installed"
}

# Install Python dependencies
install_python_dependencies() {
    log "Installing Python dependencies..."
    
    # Upgrade pip
    python3 -m pip install --upgrade pip setuptools wheel
    
    # Install common dependencies
    python3 -m pip install \
        virtualenv \
        pytest \
        pytest-cov \
        pytest-benchmark \
        black \
        flake8 \
        mypy \
        pre-commit \
        requests \
        click \
        pyyaml \
        jinja2 \
        cryptography \
        sqlalchemy \
        redis \
        prometheus-client \
        psutil
    
    log "Python dependencies installed"
}

# Setup system user and group
setup_system_user() {
    log "Setting up system user and group..."
    
    # Create group if it doesn't exist
    if ! getent group $SERVICE_GROUP > /dev/null 2>&1; then
        groupadd --system $SERVICE_GROUP
        info "Created group: $SERVICE_GROUP"
    else
        info "Group $SERVICE_GROUP already exists"
    fi
    
    # Create user if it doesn't exist
    if ! id $SERVICE_USER > /dev/null 2>&1; then
        useradd --system --no-create-home --shell /bin/false --gid $SERVICE_GROUP $SERVICE_USER
        info "Created user: $SERVICE_USER"
    else
        info "User $SERVICE_USER already exists"
    fi
    
    # Add user to necessary groups
    usermod -a -G sudo $SERVICE_USER 2>/dev/null || true
    usermod -a -G adm $SERVICE_USER 2>/dev/null || true
    
    log "System user and group configured"
}

# Setup directory structure
setup_directories() {
    log "Setting up directory structure..."
    
    # Create main directories
    mkdir -p $INSTALL_PREFIX/{bin,lib,etc,var/{log,run,lib},share/{doc,man}}
    
    # Create Python SDK specific directories
    mkdir -p $INSTALL_PREFIX/lib/python-sdk/{plugins,config,cache}
    mkdir -p $INSTALL_PREFIX/var/log/python-sdk
    mkdir -p $INSTALL_PREFIX/var/run/python-sdk
    mkdir -p $INSTALL_PREFIX/var/lib/python-sdk/{data,keys,backups}
    mkdir -p $INSTALL_PREFIX/etc/{python-sdk,ssl,monitoring,security}
    
    # Create log directories
    mkdir -p /var/log/cellframe-python-sdk
    
    # Set ownership
    chown -R $SERVICE_USER:$SERVICE_GROUP $INSTALL_PREFIX/var
    chown -R $SERVICE_USER:$SERVICE_GROUP /var/log/cellframe-python-sdk
    
    # Set permissions
    chmod 755 $INSTALL_PREFIX/{bin,lib,etc,share}
    chmod 750 $INSTALL_PREFIX/var/{log,run,lib}
    chmod 700 $INSTALL_PREFIX/var/lib/python-sdk/keys
    chmod 750 $INSTALL_PREFIX/etc
    chmod 600 $INSTALL_PREFIX/etc/security/* 2>/dev/null || true
    
    log "Directory structure created"
}

# Setup logging
setup_logging() {
    log "Setting up logging..."
    
    # Create logrotate configuration
    cat > /etc/logrotate.d/cellframe-python-sdk << EOF
/var/log/cellframe-python-sdk/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 0640 $SERVICE_USER $SERVICE_GROUP
    postrotate
        systemctl reload cellframe-python-sdk.service > /dev/null 2>&1 || true
    endscript
}

$INSTALL_PREFIX/var/log/python-sdk/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 0640 $SERVICE_USER $SERVICE_GROUP
    postrotate
        systemctl reload cellframe-python-sdk.service > /dev/null 2>&1 || true
    endscript
}
EOF
    
    # Create rsyslog configuration
    cat > /etc/rsyslog.d/50-cellframe-python-sdk.conf << EOF
# CellFrame Python SDK logging
if \$programname == 'cellframe-python-sdk' then /var/log/cellframe-python-sdk/runtime.log
& stop
EOF
    
    # Restart rsyslog
    systemctl restart rsyslog
    
    log "Logging configured"
}

# Setup firewall
setup_firewall() {
    if [[ "$SETUP_FIREWALL" == "true" ]]; then
        log "Setting up firewall..."
        
        case $OS in
            ubuntu|debian)
                # UFW configuration
                ufw --force reset
                ufw default deny incoming
                ufw default allow outgoing
                
                # Allow SSH
                ufw allow 22/tcp
                
                # Allow Python SDK ports
                ufw allow 8080/tcp
                ufw allow 8443/tcp
                
                # Allow monitoring ports (if enabled)
                if [[ "$SETUP_MONITORING" == "true" ]]; then
                    ufw allow 9090/tcp
                    ufw allow 9091/tcp
                    ufw allow 9092/tcp
                    ufw allow 9093/tcp
                    ufw allow 9094/tcp
                fi
                
                # Enable UFW
                ufw --force enable
                ;;
            centos|rhel|fedora)
                # Firewalld configuration
                systemctl enable firewalld
                systemctl start firewalld
                
                # Allow Python SDK ports
                firewall-cmd --permanent --add-port=8080/tcp
                firewall-cmd --permanent --add-port=8443/tcp
                
                # Allow monitoring ports (if enabled)
                if [[ "$SETUP_MONITORING" == "true" ]]; then
                    firewall-cmd --permanent --add-port=9090/tcp
                    firewall-cmd --permanent --add-port=9091/tcp
                    firewall-cmd --permanent --add-port=9092/tcp
                    firewall-cmd --permanent --add-port=9093/tcp
                    firewall-cmd --permanent --add-port=9094/tcp
                fi
                
                # Reload firewall
                firewall-cmd --reload
                ;;
            *)
                warn "Firewall setup not implemented for $OS"
                ;;
        esac
        
        log "Firewall configured"
    fi
}

# Setup security
setup_security() {
    if [[ "$SETUP_SECURITY" == "true" ]]; then
        log "Setting up security..."
        
        # Install and configure fail2ban
        case $OS in
            ubuntu|debian)
                # Create fail2ban jail for Python SDK
                cat > /etc/fail2ban/jail.d/cellframe-python-sdk.conf << EOF
[cellframe-python-sdk]
enabled = true
port = 8080,8443
filter = cellframe-python-sdk
logpath = /var/log/cellframe-python-sdk/runtime.log
maxretry = 5
bantime = 3600
findtime = 600
EOF
                
                # Create fail2ban filter
                cat > /etc/fail2ban/filter.d/cellframe-python-sdk.conf << EOF
[Definition]
failregex = ^.*\[ERROR\].*Authentication failed.*<HOST>.*$
            ^.*\[ERROR\].*Rate limit exceeded.*<HOST>.*$
            ^.*\[ERROR\].*Security violation.*<HOST>.*$
ignoreregex =
EOF
                
                # Restart fail2ban
                systemctl restart fail2ban
                ;;
            centos|rhel|fedora)
                # Similar configuration for CentOS/RHEL
                systemctl enable fail2ban
                systemctl start fail2ban
                ;;
            *)
                warn "Security setup not implemented for $OS"
                ;;
        esac
        
        # Generate SSL certificates
        if [[ ! -f "$INSTALL_PREFIX/etc/ssl/cert.pem" ]]; then
            mkdir -p $INSTALL_PREFIX/etc/ssl
            
            # Generate private key
            openssl genrsa -out $INSTALL_PREFIX/etc/ssl/key.pem 2048
            
            # Generate certificate signing request
            openssl req -new -key $INSTALL_PREFIX/etc/ssl/key.pem -out $INSTALL_PREFIX/etc/ssl/csr.pem -subj "/CN=cellframe-python-sdk"
            
            # Generate self-signed certificate
            openssl x509 -req -days 365 -in $INSTALL_PREFIX/etc/ssl/csr.pem -signkey $INSTALL_PREFIX/etc/ssl/key.pem -out $INSTALL_PREFIX/etc/ssl/cert.pem
            
            # Clean up
            rm $INSTALL_PREFIX/etc/ssl/csr.pem
            
            # Set permissions
            chmod 600 $INSTALL_PREFIX/etc/ssl/key.pem
            chmod 644 $INSTALL_PREFIX/etc/ssl/cert.pem
            chown root:$SERVICE_GROUP $INSTALL_PREFIX/etc/ssl/*
            
            info "SSL certificates generated"
        fi
        
        log "Security configured"
    fi
}

# Setup monitoring
setup_monitoring() {
    if [[ "$SETUP_MONITORING" == "true" ]]; then
        log "Setting up monitoring..."
        
        # Install monitoring tools
        case $OS in
            ubuntu|debian)
                # Install Node Exporter
                if [[ ! -f /usr/local/bin/node_exporter ]]; then
                    wget -O /tmp/node_exporter.tar.gz https://github.com/prometheus/node_exporter/releases/download/v1.3.1/node_exporter-1.3.1.linux-amd64.tar.gz
                    tar -xzf /tmp/node_exporter.tar.gz -C /tmp
                    cp /tmp/node_exporter-1.3.1.linux-amd64/node_exporter /usr/local/bin/
                    rm -rf /tmp/node_exporter*
                    
                    # Create systemd service
                    cat > /etc/systemd/system/node_exporter.service << EOF
[Unit]
Description=Node Exporter
After=network.target

[Service]
Type=simple
User=nobody
ExecStart=/usr/local/bin/node_exporter
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF
                    
                    systemctl daemon-reload
                    systemctl enable node_exporter
                    systemctl start node_exporter
                    
                    info "Node Exporter installed"
                fi
                ;;
            *)
                warn "Monitoring setup not implemented for $OS"
                ;;
        esac
        
        log "Monitoring configured"
    fi
}

# Setup Docker (if requested)
setup_docker() {
    if [[ "$SETUP_DOCKER" == "true" ]]; then
        log "Setting up Docker..."
        
        case $OS in
            ubuntu|debian)
                # Install Docker
                curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
                echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
                apt-get update
                apt-get install -y docker-ce docker-ce-cli containerd.io
                
                # Install Docker Compose
                curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
                chmod +x /usr/local/bin/docker-compose
                
                # Add service user to docker group
                usermod -aG docker $SERVICE_USER
                
                # Start and enable Docker
                systemctl start docker
                systemctl enable docker
                ;;
            centos|rhel|fedora)
                # Install Docker for CentOS/RHEL
                yum install -y yum-utils
                yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
                yum install -y docker-ce docker-ce-cli containerd.io
                
                # Install Docker Compose
                curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
                chmod +x /usr/local/bin/docker-compose
                
                # Add service user to docker group
                usermod -aG docker $SERVICE_USER
                
                # Start and enable Docker
                systemctl start docker
                systemctl enable docker
                ;;
            *)
                warn "Docker setup not implemented for $OS"
                ;;
        esac
        
        log "Docker configured"
    fi
}

# Generate environment report
generate_report() {
    log "Generating environment setup report..."
    
    REPORT_FILE="$INSTALL_PREFIX/var/log/python-sdk/environment-setup-$(date +%Y%m%d-%H%M%S).log"
    
    cat > "$REPORT_FILE" << EOF
CellFrame Python SDK Environment Setup Report
=============================================

Date: $(date)
Environment: $ENVIRONMENT
OS: $OS $VER
Install Prefix: $INSTALL_PREFIX
Service User: $SERVICE_USER
Python Version: $(python3 --version)

Setup Configuration:
- Monitoring: $SETUP_MONITORING
- Security: $SETUP_SECURITY
- Docker: $SETUP_DOCKER
- Firewall: $SETUP_FIREWALL

Installed Components:
- System Dependencies: ✓
- Python Dependencies: ✓
- System User: ✓
- Directory Structure: ✓
- Logging: ✓
- Firewall: $([ "$SETUP_FIREWALL" == "true" ] && echo "✓" || echo "Disabled")
- Security: $([ "$SETUP_SECURITY" == "true" ] && echo "✓" || echo "Disabled")
- Monitoring: $([ "$SETUP_MONITORING" == "true" ] && echo "✓" || echo "Disabled")
- Docker: $([ "$SETUP_DOCKER" == "true" ] && echo "✓" || echo "Disabled")

Directory Structure:
$(find $INSTALL_PREFIX -type d | head -20)

Services:
$(systemctl list-unit-files | grep -E "(cellframe|node_exporter|docker)" | head -10)

Next Steps:
1. Run the deployment script: $DEPLOY_DIR/scripts/deploy.sh
2. Configure the service: $INSTALL_PREFIX/etc/python-sdk.conf
3. Start the service: systemctl start cellframe-python-sdk
4. Monitor logs: tail -f /var/log/cellframe-python-sdk/runtime.log

EOF
    
    info "Environment setup report saved to: $REPORT_FILE"
}

# Show usage
show_usage() {
    cat << EOF
CellFrame Python SDK - Environment Setup Script

Usage: $0 [OPTIONS]

Options:
  -e, --environment ENV     Set environment (default: production)
  -p, --prefix PREFIX       Set installation prefix (default: /opt/cellframe)
  -u, --user USER           Set service user (default: cellframe)
  -g, --group GROUP         Set service group (default: cellframe)
  -v, --python-version VER  Set Python version (default: 3.9)
  --enable-monitoring       Enable monitoring setup (default: true)
  --disable-monitoring      Disable monitoring setup
  --enable-security         Enable security setup (default: true)
  --disable-security        Disable security setup
  --enable-docker           Enable Docker setup (default: false)
  --disable-docker          Disable Docker setup
  --enable-firewall         Enable firewall setup (default: true)
  --disable-firewall        Disable firewall setup
  -h, --help                Show this help message

Examples:
  $0                        # Default production setup
  $0 -e staging --disable-security
  $0 --enable-docker --disable-firewall
  
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
                SETUP_MONITORING="true"
                shift
                ;;
            --disable-monitoring)
                SETUP_MONITORING="false"
                shift
                ;;
            --enable-security)
                SETUP_SECURITY="true"
                shift
                ;;
            --disable-security)
                SETUP_SECURITY="false"
                shift
                ;;
            --enable-docker)
                SETUP_DOCKER="true"
                shift
                ;;
            --disable-docker)
                SETUP_DOCKER="false"
                shift
                ;;
            --enable-firewall)
                SETUP_FIREWALL="true"
                shift
                ;;
            --disable-firewall)
                SETUP_FIREWALL="false"
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

# Main function
main() {
    log "Starting CellFrame Python SDK environment setup..."
    
    parse_args "$@"
    check_root
    detect_os
    update_packages
    install_system_dependencies
    install_python_dependencies
    setup_system_user
    setup_directories
    setup_logging
    setup_firewall
    setup_security
    setup_monitoring
    setup_docker
    generate_report
    
    log "Environment setup completed successfully!"
    log "Check the setup report for details: $INSTALL_PREFIX/var/log/python-sdk/environment-setup-*.log"
    log "Next step: Run the deployment script: $DEPLOY_DIR/scripts/deploy.sh"
}

# Run main function with all arguments
main "$@" 