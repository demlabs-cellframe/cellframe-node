#!/bin/bash

# DAP SDK MCP Server Launcher
# Скрипт для запуска Model Context Protocol серверов для DAP SDK

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Конфигурация
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
MCP_CONFIG_DIR="$SCRIPT_DIR/config"
MCP_LOG_DIR="$SCRIPT_DIR/logs"
MCP_PID_DIR="$SCRIPT_DIR/pids"

# Создание необходимых директорий
mkdir -p "$MCP_CONFIG_DIR" "$MCP_LOG_DIR" "$MCP_PID_DIR"

# Функции логирования
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1" >&2
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" >&2
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" >&2
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

# Проверка зависимостей
check_dependencies() {
    local missing_deps=()

    if ! command -v node &> /dev/null; then
        missing_deps+=("node")
    fi

    if ! command -v python3 &> /dev/null; then
        missing_deps+=("python3")
    fi

    if ! command -v npm &> /dev/null; then
        missing_deps+=("npm")
    fi

    if [ ${#missing_deps[@]} -ne 0 ]; then
        log_error "Missing dependencies: ${missing_deps[*]}"
        log_info "Please install missing dependencies and try again"
        exit 1
    fi
}

# Создание MCP конфигурации
create_mcp_config() {
    local config_file="$MCP_CONFIG_DIR/mcp-config.json"

    if [ ! -f "$config_file" ]; then
        log_info "Creating MCP configuration..."

        cat > "$config_file" << 'EOF'
{
  "mcpServers": {
    "dap-sdk-docs": {
      "command": "node",
      "args": ["scripts/mcp/servers/dap-sdk-docs-server.js"],
      "env": {
        "PROJECT_ROOT": "'"$PROJECT_ROOT"'",
        "LOG_LEVEL": "info"
      }
    },
    "dap-sdk-code": {
      "command": "python3",
      "args": ["scripts/mcp/servers/dap-sdk-code-server.py"],
      "env": {
        "PROJECT_ROOT": "'"$PROJECT_ROOT"'",
        "PYTHONPATH": "'"$PROJECT_ROOT"'"
      }
    },
    "dap-sdk-validation": {
      "command": "node",
      "args": ["scripts/mcp/servers/dap-sdk-validation-server.js"],
      "env": {
        "PROJECT_ROOT": "'"$PROJECT_ROOT"'",
        "VALIDATION_MODE": "strict"
      }
    }
  },
  "global": {
    "logLevel": "info",
    "timeout": 30000,
    "retryAttempts": 3
  }
}
EOF

        log_success "MCP configuration created at $config_file"
    else
        log_info "MCP configuration already exists"
    fi
}

# Запуск MCP сервера
start_mcp_server() {
    local server_name="$1"
    local server_type="${2:-node}"
    local log_file="$MCP_LOG_DIR/${server_name}.log"
    local pid_file="$MCP_PID_DIR/${server_name}.pid"

    # Проверка, не запущен ли уже сервер
    if [ -f "$pid_file" ]; then
        local old_pid=$(cat "$pid_file")
        if kill -0 "$old_pid" 2>/dev/null; then
            log_warning "MCP server '$server_name' is already running (PID: $old_pid)"
            return 1
        else
            log_warning "Removing stale PID file for '$server_name'"
            rm -f "$pid_file"
        fi
    fi

    log_info "Starting MCP server: $server_name"

    # Определение скрипта сервера
    local server_script
    case "$server_name" in
        "dap-sdk-docs")
            server_script="$SCRIPT_DIR/servers/dap-sdk-docs-server.js"
            ;;
        "dap-sdk-code")
            server_script="$SCRIPT_DIR/servers/dap-sdk-code-server.py"
            ;;
        "dap-sdk-validation")
            server_script="$SCRIPT_DIR/servers/dap-sdk-validation-server.js"
            ;;
        *)
            log_error "Unknown server: $server_name"
            return 1
            ;;
    esac

    if [ ! -f "$server_script" ]; then
        log_error "Server script not found: $server_script"
        return 1
    fi

    # Запуск сервера в фоне
    case "$server_type" in
        "node")
            nohup node "$server_script" > "$log_file" 2>&1 &
            ;;
        "python")
            nohup python3 "$server_script" > "$log_file" 2>&1 &
            ;;
        *)
            log_error "Unsupported server type: $server_type"
            return 1
            ;;
    esac

    local server_pid=$!
    echo $server_pid > "$pid_file"

    # Ожидание запуска сервера
    sleep 2

    if kill -0 "$server_pid" 2>/dev/null; then
        log_success "MCP server '$server_name' started (PID: $server_pid)"
        log_info "Logs: $log_file"
        return 0
    else
        log_error "Failed to start MCP server '$server_name'"
        rm -f "$pid_file"
        log_info "Check logs: $log_file"
        return 1
    fi
}

# Остановка MCP сервера
stop_mcp_server() {
    local server_name="$1"
    local pid_file="$MCP_PID_DIR/${server_name}.pid"

    if [ ! -f "$pid_file" ]; then
        log_warning "PID file not found for server '$server_name'"
        return 0
    fi

    local server_pid=$(cat "$pid_file")

    if kill -0 "$server_pid" 2>/dev/null; then
        log_info "Stopping MCP server '$server_name' (PID: $server_pid)"
        kill "$server_pid"

        # Ожидание завершения
        local timeout=10
        while [ $timeout -gt 0 ] && kill -0 "$server_pid" 2>/dev/null; do
            sleep 1
            timeout=$((timeout - 1))
        done

        if kill -0 "$server_pid" 2>/dev/null; then
            log_warning "Force killing MCP server '$server_name'"
            kill -9 "$server_pid"
        fi

        log_success "MCP server '$server_name' stopped"
    else
        log_warning "MCP server '$server_name' is not running"
    fi

    rm -f "$pid_file"
}

# Проверка статуса MCP серверов
status_mcp_servers() {
    log_info "MCP Server Status:"

    for pid_file in "$MCP_PID_DIR"/*.pid; do
        if [ -f "$pid_file" ]; then
            local server_name=$(basename "$pid_file" .pid)
            local server_pid=$(cat "$pid_file")

            if kill -0 "$server_pid" 2>/dev/null; then
                echo -e "  ${GREEN}●${NC} $server_name (PID: $server_pid)"
            else
                echo -e "  ${RED}●${NC} $server_name (PID: $server_pid - dead)"
            fi
        fi
    done

    if [ -z "$(ls -A "$MCP_PID_DIR"/*.pid 2>/dev/null)" ]; then
        log_info "No MCP servers are running"
    fi
}

# Остановка всех MCP серверов
stop_all_mcp_servers() {
    log_info "Stopping all MCP servers..."

    for pid_file in "$MCP_PID_DIR"/*.pid; do
        if [ -f "$pid_file" ]; then
            local server_name=$(basename "$pid_file" .pid)
            stop_mcp_server "$server_name"
        fi
    done

    log_success "All MCP servers stopped"
}

# Запуск всех MCP серверов
start_all_mcp_servers() {
    log_info "Starting all MCP servers..."

    start_mcp_server "dap-sdk-docs" "node"
    start_mcp_server "dap-sdk-code" "python"
    start_mcp_server "dap-sdk-validation" "node"

    log_success "All MCP servers started"
}

# Отображение справки
show_help() {
    cat << EOF
DAP SDK MCP Server Manager

USAGE:
    $0 [COMMAND] [OPTIONS]

COMMANDS:
    start [SERVER]     Start MCP server(s)
                       Available: dap-sdk-docs, dap-sdk-code, dap-sdk-validation, all
    stop [SERVER]      Stop MCP server(s)
                       Available: dap-sdk-docs, dap-sdk-code, dap-sdk-validation, all
    restart [SERVER]   Restart MCP server(s)
    status             Show status of all MCP servers
    logs [SERVER]      Show logs for specific server
    config             Show MCP configuration
    setup              Setup MCP environment (install dependencies)

SERVERS:
    dap-sdk-docs       Documentation server for DAP SDK
    dap-sdk-code       Code analysis server for DAP SDK
    dap-sdk-validation Validation server for documentation and code

EXAMPLES:
    $0 start all                    # Start all MCP servers
    $0 start dap-sdk-docs           # Start documentation server
    $0 stop dap-sdk-validation      # Stop validation server
    $0 restart all                  # Restart all servers
    $0 status                       # Show server status
    $0 logs dap-sdk-docs            # Show logs for docs server

EOF
}

# Настройка MCP окружения
setup_mcp_environment() {
    log_info "Setting up MCP environment..."

    # Создание конфигурации
    create_mcp_config

    # Создание директорий для серверов
    mkdir -p "$SCRIPT_DIR/servers"

    log_success "MCP environment setup complete"
}

# Основная функция
main() {
    local command="$1"
    local server="$2"

    case "$command" in
        "start")
            check_dependencies
            case "$server" in
                "all"|"")
                    start_all_mcp_servers
                    ;;
                "dap-sdk-docs"|"dap-sdk-code"|"dap-sdk-validation")
                    start_mcp_server "$server"
                    ;;
                *)
                    log_error "Unknown server: $server"
                    show_help
                    exit 1
                    ;;
            esac
            ;;
        "stop")
            case "$server" in
                "all"|"")
                    stop_all_mcp_servers
                    ;;
                "dap-sdk-docs"|"dap-sdk-code"|"dap-sdk-validation")
                    stop_mcp_server "$server"
                    ;;
                *)
                    log_error "Unknown server: $server"
                    show_help
                    exit 1
                    ;;
            esac
            ;;
        "restart")
            case "$server" in
                "all"|"")
                    stop_all_mcp_servers
                    sleep 2
                    start_all_mcp_servers
                    ;;
                "dap-sdk-docs"|"dap-sdk-code"|"dap-sdk-validation")
                    stop_mcp_server "$server"
                    sleep 2
                    start_mcp_server "$server"
                    ;;
                *)
                    log_error "Unknown server: $server"
                    show_help
                    exit 1
                    ;;
            esac
            ;;
        "status")
            status_mcp_servers
            ;;
        "logs")
            if [ -z "$server" ]; then
                log_error "Please specify server name for logs"
                exit 1
            fi
            local log_file="$MCP_LOG_DIR/${server}.log"
            if [ -f "$log_file" ]; then
                tail -f "$log_file"
            else
                log_error "Log file not found: $log_file"
                exit 1
            fi
            ;;
        "config")
            if [ -f "$MCP_CONFIG_DIR/mcp-config.json" ]; then
                cat "$MCP_CONFIG_DIR/mcp-config.json"
            else
                log_error "MCP configuration not found"
                exit 1
            fi
            ;;
        "setup")
            setup_mcp_environment
            ;;
        "help"|"-h"|"--help"|"")
            show_help
            ;;
        *)
            log_error "Unknown command: $command"
            show_help
            exit 1
            ;;
    esac
}

# Запуск основной функции
main "$@"
