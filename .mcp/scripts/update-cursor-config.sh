#!/bin/bash

# Скрипт для автоматического обновления конфигурации Cursor для MCP-файлов
# Автор: AI Assistant
# Дата: $(date +%Y-%m-%d)

set -e

LOG_TAG="update-cursor-config"
WORKSPACE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
MCP_ROOT="$WORKSPACE_ROOT/.mcp"
CURSOR_CONFIG="$WORKSPACE_ROOT/.cursor/config.json"
VSCODE_SETTINGS="$WORKSPACE_ROOT/.vscode/settings.json"

log_info() {
    echo "[$LOG_TAG] INFO: $1"
}

log_error() {
    echo "[$LOG_TAG] ERROR: $1" >&2
}

# Функция для поиска всех MCP-файлов
find_mcp_files() {
    find "$WORKSPACE_ROOT" -name "*.mcp" -o -path "*/.mcp/*.json" 2>/dev/null | \
    grep -v "/cache/" | \
    grep -v "/temp/" | \
    sort
}

# Функция для обновления конфигурации Cursor
update_cursor_config() {
    local l_mcp_files=($(find_mcp_files))
    local l_config_updated=false
    
    log_info "Найдено ${#l_mcp_files[@]} MCP-файлов"
    
    # Проверяем, нужно ли обновить конфигурацию
    for l_file in "${l_mcp_files[@]}"; do
        local l_relative_path="${l_file#$WORKSPACE_ROOT/}"
        
        if ! grep -q "$l_relative_path" "$CURSOR_CONFIG" 2>/dev/null; then
            log_info "Добавляем новый MCP-файл в конфигурацию: $l_relative_path"
            l_config_updated=true
        fi
    done
    
    if [ "$l_config_updated" = true ]; then
        log_info "Обновляем конфигурацию Cursor..."
        # Проверяем существование скрипта обновления MCP-контекста
        if [ -f "$MCP_ROOT/scripts/update-mcp-context.sh" ]; then
            "$MCP_ROOT/scripts/update-mcp-context.sh"
        else  
            log_info "Скрипт update-mcp-context.sh не найден, пропускаем"
        fi
        log_info "Конфигурация обновлена успешно"
    else
        log_info "Конфигурация актуальна, обновление не требуется"
    fi
}

# Функция для создания watcher'а для автоматического обновления
setup_file_watcher() {
    if command -v inotifywait >/dev/null 2>&1; then
        log_info "Настраиваем автоматическое отслеживание изменений MCP-файлов..."
        
        # Запускаем watcher в фоне
        {
            inotifywait -m -r --exclude='/cache/|/temp/' -e modify,create,delete "$MCP_ROOT" "$WORKSPACE_ROOT/dap-sdk/.mcp" "$WORKSPACE_ROOT/cellframe-sdk/.mcp" "$WORKSPACE_ROOT/python-cellframe/.mcp" 2>/dev/null | \
            while read l_path l_action l_file; do
                if [[ "$l_file" == *.json ]] || [[ "$l_file" == *.mcp ]]; then
                    log_info "Обнаружено изменение: $l_path$l_file ($l_action)"
                    sleep 1  # Небольшая задержка для завершения записи
                    update_cursor_config
                fi
            done
        } &
        
        echo $! > "$MCP_ROOT/cache/file_watcher.pid"
        log_info "File watcher запущен (PID: $(cat "$MCP_ROOT/cache/file_watcher.pid"))"
    else
        log_info "inotifywait недоступен, автоматическое отслеживание отключено"
    fi
}

# Основная логика
main() {
    log_info "Запуск обновления конфигурации Cursor для MCP-файлов"
    
    # Создаем необходимые директории
    mkdir -p "$MCP_ROOT/cache"
    mkdir -p "$(dirname "$CURSOR_CONFIG")"
    
    # Обновляем конфигурацию
    update_cursor_config
    
    # Настраиваем автоматическое отслеживание, если запрошено
    if [ "$1" = "--watch" ]; then
        setup_file_watcher
        log_info "Скрипт работает в режиме отслеживания. Нажмите Ctrl+C для остановки."
        wait
    fi
    
    log_info "Обновление конфигурации завершено"
}

# Обработка сигналов для корректного завершения
cleanup() {
    if [ -f "$MCP_ROOT/cache/file_watcher.pid" ]; then
        local l_pid=$(cat "$MCP_ROOT/cache/file_watcher.pid")
        if kill -0 "$l_pid" 2>/dev/null; then
            log_info "Останавливаем file watcher (PID: $l_pid)"
            kill "$l_pid"
        fi
        rm -f "$MCP_ROOT/cache/file_watcher.pid"
    fi
}

trap cleanup EXIT INT TERM

# Запуск
main "$@" 