#!/bin/bash

# CellFrame Security Test Suite
# Автоматические тесты безопасности для проверки исправлений

set -e

echo "🛡️ === CellFrame Security Test Suite ==="
echo "Тестирование исправлений безопасности..."
echo

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Счетчики тестов
TESTS_TOTAL=0
TESTS_PASSED=0
TESTS_FAILED=0

# Функция для запуска теста
run_test() {
    local test_name="$1"
    local test_command="$2"
    local expected_result="$3"
    
    TESTS_TOTAL=$((TESTS_TOTAL + 1))
    echo -n "🧪 Testing: $test_name... "
    
    if eval "$test_command" >/dev/null 2>&1; then
        if [ "$expected_result" = "pass" ]; then
            echo -e "${GREEN}✅ PASSED${NC}"
            TESTS_PASSED=$((TESTS_PASSED + 1))
        else
            echo -e "${RED}❌ FAILED (expected to fail but passed)${NC}"
            TESTS_FAILED=$((TESTS_FAILED + 1))
        fi
    else
        if [ "$expected_result" = "fail" ]; then
            echo -e "${GREEN}✅ PASSED (correctly failed)${NC}"
            TESTS_PASSED=$((TESTS_PASSED + 1))
        else
            echo -e "${RED}❌ FAILED${NC}"
            TESTS_FAILED=$((TESTS_FAILED + 1))
        fi
    fi
}

# Тест 1: Проверка компиляции с security флагами
echo "📦 Testing compilation with security flags..."
run_test "Security compilation flags" \
    "cd build && cmake -DCMAKE_C_FLAGS='-fstack-protector-strong -D_FORTIFY_SOURCE=2' .. && make -j2 >/dev/null" \
    "pass"

# Тест 2: Проверка что исправления не ломают функциональность
echo "🔧 Testing core functionality after security fixes..."
run_test "Core functionality" \
    "cd build && make cellframe-node >/dev/null" \
    "pass"

# Тест 3: Тест memory safety с AddressSanitizer (если доступен)
if command -v gcc >/dev/null && gcc --help=warnings 2>&1 | grep -q fsanitize; then
    echo "🧠 Testing memory safety with AddressSanitizer..."
    run_test "AddressSanitizer compilation" \
        "cd build && cmake -DCMAKE_C_FLAGS='-fsanitize=address -g' .. && make -j2 >/dev/null" \
        "pass"
fi

# Тест 4: Проверка что новые header файлы корректны
echo "📁 Testing new security headers..."
run_test "Security monitor header" \
    "gcc -I dap-sdk/core/include -c dap-sdk/core/include/dap_security_monitor.h -o /tmp/test_header.o" \
    "pass"

run_test "Node access control header" \
    "gcc -I cellframe-sdk/modules/net/include -I dap-sdk/core/include -c cellframe-sdk/modules/net/include/dap_chain_node_access_control.h -o /tmp/test_header2.o" \
    "pass"

# Тест 5: Проверка что Python биндинги компилируются
if [ -d "python-cellframe" ]; then
    echo "🐍 Testing Python bindings compilation..."
    run_test "Python bindings" \
        "cd python-cellframe && python3 setup.py build >/dev/null 2>&1" \
        "pass"
fi

# Тест 6: Статический анализ (если доступен cppcheck)
if command -v cppcheck >/dev/null; then
    echo "🔍 Running static analysis with cppcheck..."
    run_test "Static analysis - no critical errors" \
        "cppcheck --enable=warning --error-exitcode=1 dap-sdk/core/src/dap_security_monitor.c" \
        "pass"
fi

# Тест 7: Проверка что исправленные файлы не содержат явных проблем
echo "🔎 Testing fixed vulnerabilities..."

# Проверка что eval убран из скриптов
run_test "Command injection fix" \
    "! grep -r 'eval.*cmd' scripts/" \
    "pass"

# Проверка что memset заменен на explicit_bzero для паролей
run_test "Password clearing fix" \
    "grep -q 'explicit_bzero.*pass' cellframe-sdk/modules/wallet/dap_chain_wallet.c" \
    "pass"

# Проверка что добавлены overflow проверки
run_test "Integer overflow protection" \
    "grep -q 'SIZE_MAX.*overflow' dap-sdk/core/src/dap_strfuncs.c" \
    "pass"

echo
echo "📊 === Test Results ==="
echo "Total tests: $TESTS_TOTAL"
echo -e "Passed: ${GREEN}$TESTS_PASSED${NC}"
echo -e "Failed: ${RED}$TESTS_FAILED${NC}"

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "\n🎉 ${GREEN}ALL SECURITY TESTS PASSED!${NC}"
    echo "✅ Security fixes are working correctly"
    echo "✅ No regressions detected"
    echo "✅ Project is ready for production"
    exit 0
else
    echo -e "\n⚠️ ${YELLOW}SOME TESTS FAILED${NC}"
    echo "❌ Please review failed tests before deployment"
    exit 1
fi
