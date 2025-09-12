#!/bin/bash

# DAP SDK Documentation Validation Script
# Автоматическая валидация документации на корректность

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Конфигурация
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
DOCS_DIR="$PROJECT_ROOT/docs"
REPORTS_DIR="$SCRIPT_DIR/reports"
LOGS_DIR="$SCRIPT_DIR/logs"

# Создание директорий
mkdir -p "$REPORTS_DIR" "$LOGS_DIR"

# Счетчики результатов
TOTAL_FILES=0
PASSED_FILES=0
FAILED_FILES=0
WARNINGS=0

# Функции логирования
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
    ((WARNINGS++))
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
    ((FAILED_FILES++))
}

log_header() {
    echo -e "${PURPLE}================================================================${NC}"
    echo -e "${PURPLE}$1${NC}"
    echo -e "${PURPLE}================================================================${NC}"
}

# Проверка зависимостей
check_dependencies() {
    local missing_deps=()

    if ! command -v markdownlint &> /dev/null; then
        missing_deps+=("markdownlint")
    fi

    if ! command -v grep &> /dev/null; then
        missing_deps+=("grep")
    fi

    if ! command -v find &> /dev/null; then
        missing_deps+=("find")
    fi

    if [ ${#missing_deps[@]} -ne 0 ]; then
        log_warning "Missing optional dependencies: ${missing_deps[*]}"
        log_info "Some checks will be skipped"
    fi
}

# Поиск всех Markdown файлов
find_markdown_files() {
    local search_dir="$1"
    find "$search_dir" -name "*.md" -type f | sort
}

# Валидация базового синтаксиса Markdown
validate_markdown_syntax() {
    local file="$1"
    local filename=$(basename "$file")

    log_info "Validating syntax: $filename"

    # Проверка на незакрытые блоки кода
    if grep -n "```" "$file" | grep -v "bash\|c\|cpp\|python\|json\|javascript" | head -5 > /dev/null; then
        log_warning "Found potential unclosed code blocks in $filename"
    fi

    # Проверка на битые ссылки (базовая проверка)
    if grep -n "\[.*\](\s*)" "$file" > /dev/null; then
        log_warning "Found empty links in $filename"
    fi

    # Проверка на несогласованные заголовки
    local h1_count=$(grep -c "^# " "$file")
    if [ "$h1_count" -gt 1 ]; then
        log_warning "Multiple H1 headers found in $filename (should have only one)"
    fi

    log_success "Syntax validation passed for $filename"
    ((PASSED_FILES++))
}

# Проверка соответствия кода документации
validate_code_references() {
    local file="$1"
    local filename=$(basename "$file")

    log_info "Validating code references: $filename"

    # Извлечение имен функций из документации
    local functions_in_docs=$(grep -o "dap_[a-zA-Z_][a-zA-Z0-9_]*(" "$file" | sed 's/(.*//' | sort | uniq)

    if [ -n "$functions_in_docs" ]; then
        log_info "Found $(echo "$functions_in_docs" | wc -l) function references in $filename"

        # Здесь можно добавить проверку существования функций в коде
        # Пока просто логируем найденные функции
        echo "$functions_in_docs" | while read -r func; do
            log_info "  Referenced function: $func"
        done
    fi
}

# Проверка структуры документации
validate_document_structure() {
    local file="$1"
    local filename=$(basename "$file")

    log_info "Validating structure: $filename"

    # Проверка наличия заголовка
    if ! head -5 "$file" | grep -q "^# "; then
        log_warning "No H1 header found in $filename"
    fi

    # Проверка наличия описания
    if ! head -10 "$file" | grep -q "^## "; then
        log_warning "No H2 sections found in $filename"
    fi

    # Проверка на слишком длинные строки
    local long_lines=$(awk 'length > 120 {print NR ": " $0}' "$file" | wc -l)
    if [ "$long_lines" -gt 0 ]; then
        log_warning "Found $long_lines lines longer than 120 characters in $filename"
    fi
}

# Проверка специфичных для DAP SDK элементов
validate_dap_specific() {
    local file="$1"
    local filename=$(basename "$file")

    log_info "Validating DAP-specific content: $filename"

    # Проверка на наличие ссылок на другие модули
    if grep -q "dap_[a-zA-Z_]*\.h" "$file"; then
        log_info "Found header file references in $filename"
    fi

    # Проверка на упоминание структур данных
    if grep -q "typedef struct" "$file"; then
        log_info "Found structure definitions in $filename"
    fi

    # Проверка на наличие примеров кода
    if grep -q "```c" "$file" || grep -q "```cpp" "$file"; then
        log_info "Found C/C++ code examples in $filename"
    fi
}

# Генерация отчета по модулям
generate_module_report() {
    local docs_dir="$1"
    local report_file="$REPORTS_DIR/module_report_$(date +%Y%m%d_%H%M%S).txt"

    log_header "Генерация отчета по модулям"

    {
        echo "DAP SDK Documentation Module Report"
        echo "Generated: $(date)"
        echo "=========================================="
        echo ""

        # DAP SDK модули
        echo "DAP SDK Core Modules:"
        echo "---------------------"
        if [ -d "$docs_dir/dap-sdk/docs/modules/core" ]; then
            find "$docs_dir/dap-sdk/docs/modules/core" -name "*.md" | while read -r file; do
                local module_name=$(basename "$file" .md)
                local line_count=$(wc -l < "$file")
                echo "  • $module_name ($line_count lines)"
            done
        fi

        echo ""
        echo "DAP SDK Crypto Modules:"
        echo "-----------------------"
        if [ -d "$docs_dir/dap-sdk/docs/modules/crypto" ]; then
            find "$docs_dir/dap-sdk/docs/modules/crypto" -name "*.md" | while read -r file; do
                local module_name=$(basename "$file" .md)
                local line_count=$(wc -l < "$file")
                echo "  • $module_name ($line_count lines)"
            done
        fi

        echo ""
        echo "CellFrame SDK Modules:"
        echo "----------------------"
        if [ -d "$docs_dir/cellframe-sdk/docs/modules" ]; then
            find "$docs_dir/cellframe-sdk/docs/modules" -name "*.md" | wc -l | xargs echo "Total module files:"
            find "$docs_dir/cellframe-sdk/docs/modules" -name "*.md" | head -5 | while read -r file; do
                local module_name=$(basename "$file" .md)
                echo "  • $module_name"
            done
            if [ $(find "$docs_dir/cellframe-sdk/docs/modules" -name "*.md" | wc -l) -gt 5 ]; then
                echo "  ... and $(($(find "$docs_dir/cellframe-sdk/docs/modules" -name "*.md" | wc -l) - 5)) more"
            fi
        fi

        echo ""
        echo "Summary:"
        echo "--------"
        local total_md_files=$(find "$docs_dir" -name "*.md" | wc -l)
        local total_lines=$(find "$docs_dir" -name "*.md" -exec wc -l {} \; | awk '{sum += $1} END {print sum}')
        echo "Total Markdown files: $total_md_files"
        echo "Total lines of documentation: $total_lines"
        echo "Average lines per file: $((total_lines / total_md_files))"

    } > "$report_file"

    log_success "Module report generated: $report_file"
}

# Генерация сводного отчета
generate_summary_report() {
    local report_file="$REPORTS_DIR/validation_summary_$(date +%Y%m%d_%H%M%S).txt"

    {
        echo "DAP SDK Documentation Validation Summary"
        echo "Generated: $(date)"
        echo "=========================================="
        echo ""
        echo "Validation Results:"
        echo "-------------------"
        echo "Total files processed: $TOTAL_FILES"
        echo "Files passed: $PASSED_FILES"
        echo "Files failed: $FAILED_FILES"
        echo "Warnings: $WARNINGS"
        echo ""
        echo "Success rate: $(( (PASSED_FILES * 100) / TOTAL_FILES ))%"
        echo ""
        echo "Status: $([ $FAILED_FILES -eq 0 ] && echo "PASSED" || echo "FAILED")"
        echo ""
        echo "Recommendations:"
        echo "----------------"

        if [ $WARNINGS -gt 0 ]; then
            echo "• Review $WARNINGS warnings for potential improvements"
        fi

        if [ $FAILED_FILES -gt 0 ]; then
            echo "• Address $FAILED_FILES failed validations"
        fi

        if [ $PASSED_FILES -eq $TOTAL_FILES ]; then
            echo "• All validations passed! Documentation is in good shape."
        fi

    } > "$report_file"

    log_success "Summary report generated: $report_file"
}

# Функция для быстрой проверки
quick_check() {
    local file="$1"

    if [ ! -f "$file" ]; then
        log_error "File not found: $file"
        return 1
    fi

    log_info "Quick check for: $(basename "$file")"

    # Базовые проверки
    if head -5 "$file" | grep -q "^# "; then
        log_success "Has H1 header"
    else
        log_error "Missing H1 header"
    fi

    if grep -q "```" "$file"; then
        log_success "Has code examples"
    else
        log_warning "No code examples found"
    fi

    if grep -q "dap_[a-zA-Z_]" "$file"; then
        log_success "Has DAP-specific content"
    else
        log_warning "No DAP-specific content found"
    fi
}

# Основная функция валидации
validate_documentation() {
    local docs_dir="$1"

    log_header "Запуск валидации документации DAP SDK"

    if [ ! -d "$docs_dir" ]; then
        log_error "Documentation directory not found: $docs_dir"
        exit 1
    fi

    check_dependencies

    # Поиск всех Markdown файлов
    local md_files=$(find_markdown_files "$docs_dir")

    if [ -z "$md_files" ]; then
        log_warning "No Markdown files found in $docs_dir"
        return
    fi

    TOTAL_FILES=$(echo "$md_files" | wc -l)
    log_info "Found $TOTAL_FILES Markdown files to validate"

    # Валидация каждого файла
    echo "$md_files" | while read -r file; do
        if [ -f "$file" ]; then
            validate_markdown_syntax "$file"
            validate_document_structure "$file"
            validate_code_references "$file"
            validate_dap_specific "$file"
        fi
    done

    # Генерация отчетов
    generate_module_report "$docs_dir"
    generate_summary_report
}

# Отображение справки
show_help() {
    cat << EOF
DAP SDK Documentation Validator

USAGE:
    $0 [COMMAND] [OPTIONS]

COMMANDS:
    validate [DIR]    Validate all documentation in directory
                     Default: ../docs
    quick FILE       Quick validation of single file
    report           Generate module report only
    help             Show this help

EXAMPLES:
    $0 validate                    # Validate all docs in default location
    $0 validate /path/to/docs      # Validate docs in specific directory
    $0 quick file.md              # Quick check single file
    $0 report                     # Generate module report only

REPORTS:
    Reports are saved to: scripts/reports/
    Logs are saved to: scripts/logs/

EOF
}

# Основная функция
main() {
    local command="$1"
    local target="$2"

    case "$command" in
        "validate")
            if [ -z "$target" ]; then
                target="$DOCS_DIR"
            fi
            validate_documentation "$target"
            ;;
        "quick")
            if [ -z "$target" ]; then
                log_error "Please specify file for quick check"
                exit 1
            fi
            quick_check "$target"
            ;;
        "report")
            generate_module_report "$DOCS_DIR"
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

    # Финальная статистика
    if [ "$command" = "validate" ]; then
        log_header "Результаты валидации"
        echo -e "${CYAN}Обработано файлов:${NC} $TOTAL_FILES"
        echo -e "${GREEN}Прошло проверку:${NC} $PASSED_FILES"
        echo -e "${RED}Не прошло проверку:${NC} $FAILED_FILES"
        echo -e "${YELLOW}Предупреждений:${NC} $WARNINGS"

        if [ $FAILED_FILES -eq 0 ]; then
            log_success "Все проверки пройдены успешно!"
        else
            log_warning "Найдены проблемы, требующие внимания"
        fi
    fi
}

# Запуск основной функции
main "$@"
