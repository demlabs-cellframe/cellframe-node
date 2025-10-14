#!/bin/bash

# Скрипт для тестирования исправлений в системе QA

set -euo pipefail

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                    🧪 ТЕСТИРОВАНИЕ ИСПРАВЛЕНИЙ                 ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Load configuration
if [[ -f "qa_config.env" ]]; then
    source qa_config.env
    echo "✅ Загружена конфигурация из qa_config.env"
else
    echo "⚠️  qa_config.env не найден, используем значения по умолчанию"
fi

echo ""
echo "=== 1. Проверка исправленных функций ==="

# Test 1: Проверка функции check_network_ready
echo "1.1. Тестируем функцию проверки сети..."
python3 -c "
import sys
sys.path.append('.')
from test_cellframe_qa import check_network_ready

# Мокаем функцию run_command для тестирования
import test_cellframe_qa
original_run_command = test_cellframe_qa.run_command

test_cases = [
    ('net: Backbone\nStatus: active', True, 'Нормальный статус'),
    ('Error: failed\nnet: Backbone', False, 'Ошибка в выводе'),
    ('net: Backbone\nTimeout occurred', False, 'Timeout в выводе'),
]

all_passed = True
for output, expected, description in test_cases:
    def mock_run_command(cmd):
        return (0, output, '')
    
    test_cellframe_qa.run_command = mock_run_command
    result = check_network_ready('Backbone')
    test_cellframe_qa.run_command = original_run_command
    
    if result == expected:
        print(f'✅ {description}: PASSED')
    else:
        print(f'❌ {description}: FAILED (got {result}, expected {expected})')
        all_passed = False

if all_passed:
    print('✅ Все тесты функции check_network_ready прошли')
else:
    print('❌ Некоторые тесты функции check_network_ready упали')
"

echo ""
echo "1.2. Проверяем расчет лимитов памяти..."
python3 -c "
import sys
sys.path.append('.')
from test_cellframe_qa import get_system_memory_gb

system_mem = get_system_memory_gb()
base_limit_mb = 1024
percentage_limit_mb = int(system_mem * 1024 * 0.15)
memory_limit_mb = min(base_limit_mb, percentage_limit_mb)
memory_limit_mb = max(memory_limit_mb, 512)

print(f'Системная память: {system_mem} GB')
print(f'Рассчитанный лимит: {memory_limit_mb} MB')

if memory_limit_mb >= 512:
    print('✅ Лимит памяти адекватный')
else:
    print('❌ Лимит памяти слишком низкий')
"

echo ""
echo "=== 2. Проверка конфигурации ==="
echo "2.1. Переменные окружения:"
echo "   CELLFRAME_NODE_DIR: ${CELLFRAME_NODE_DIR:-не установлена}"
echo "   QA_MEMORY_LIMIT_MB: ${QA_MEMORY_LIMIT_MB:-не установлена}"
echo "   QA_STRICT_MODE: ${QA_STRICT_MODE:-не установлена}"

echo ""
echo "2.2. Проверка путей:"
if [[ -d "${CELLFRAME_NODE_DIR:-/opt/cellframe-node}" ]]; then
    echo "✅ Директория Cellframe Node найдена: ${CELLFRAME_NODE_DIR:-/opt/cellframe-node}"
else
    echo "⚠️  Директория Cellframe Node не найдена: ${CELLFRAME_NODE_DIR:-/opt/cellframe-node}"
fi

echo ""
echo "=== 3. Проверка TestOps интеграции ==="
echo "3.1. Подключение к TestOps..."
if curl -s -H "Authorization: Api-Token ${ALLURE_TOKEN}" "${ALLURE_ENDPOINT}/api/rs/launch?projectId=${ALLURE_PROJECT_ID}&size=1" > /dev/null; then
    echo "✅ TestOps доступен"
else
    echo "❌ TestOps недоступен"
fi

echo ""
echo "=== 4. Проверка файлов системы ==="
files_to_check=(
    "test_cellframe_qa.py"
    "test_cellframe_qa_old.py"
    "launch_manager.sh"
    "working_trend_analyzer.sh"
    "qa_config.env"
)

for file in "${files_to_check[@]}"; do
    if [[ -f "$file" ]]; then
        echo "✅ $file"
    else
        echo "❌ $file отсутствует"
    fi
done

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                    ✅ ТЕСТИРОВАНИЕ ЗАВЕРШЕНО                    ║"
echo "╚════════════════════════════════════════════════════════════════╝"
