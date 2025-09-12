#!/bin/bash

# Скрипт для тестирования компиляции примеров CellFrame DAP SDK
# Проверяет, что все примеры компилируются без ошибок

set -e

echo "=== CellFrame DAP SDK Examples Compilation Test ==="
echo

# Функция для тестирования примера
test_example() {
    local example_path=$1
    local example_name=$(basename "$example_path")

    echo "Testing: $example_name"

    if [ ! -d "$example_path" ]; then
        echo "  ❌ Directory not found: $example_path"
        return 1
    fi

    if [ ! -f "$example_path/CMakeLists.txt" ]; then
        echo "  ❌ CMakeLists.txt not found in $example_path"
        return 1
    fi

    # Создание директории сборки
    local build_dir="$example_path/build"
    mkdir -p "$build_dir"

    # Переход в директорию сборки
    cd "$build_dir"

    # Конфигурация с CMake
    echo "  📦 Configuring with CMake..."
    if ! cmake .. -DCMAKE_BUILD_TYPE=Release >/dev/null 2>&1; then
        echo "  ❌ CMake configuration failed for $example_name"
        cd - >/dev/null
        return 1
    fi

    # Сборка
    echo "  🔨 Building..."
    if ! make -j$(nproc) >/dev/null 2>&1; then
        echo "  ❌ Build failed for $example_name"
        cd - >/dev/null
        return 1
    fi

    # Проверка наличия исполняемого файла
    local exe_name=$(basename "$example_path")
    if [ ! -f "$exe_name" ]; then
        echo "  ❌ Executable not found: $exe_name"
        cd - >/dev/null
        return 1
    fi

    echo "  ✅ $example_name compiled successfully"
    cd - >/dev/null
    return 0
}

# Тестирование примеров DAP SDK
echo "Testing DAP SDK examples..."
echo

# DAP SDK Hello World
test_example "/home/naeper/work/cellframe-node/dap-sdk/docs/examples/hello_world"
dap_hello_result=$?

echo

# Тестирование примеров CellFrame SDK
echo "Testing CellFrame SDK examples..."
echo

# CellFrame Hello World
test_example "/home/naeper/work/cellframe-node/cellframe-sdk/docs/examples/hello_cellframe"
cellframe_hello_result=$?

# CellFrame Simple Wallet
test_example "/home/naeper/work/cellframe-node/cellframe-sdk/docs/examples/simple_wallet"
simple_wallet_result=$?

# CellFrame Complex Wallet
test_example "/home/naeper/work/cellframe-node/cellframe-sdk/docs/examples/complex_wallet"
complex_wallet_result=$?

echo
echo "=== Compilation Test Results ==="
echo

# Вывод результатов
echo "DAP SDK Examples:"
echo "  hello_world: $([ $dap_hello_result -eq 0 ] && echo "✅ PASS" || echo "❌ FAIL")"

echo
echo "CellFrame SDK Examples:"
echo "  hello_cellframe: $([ $cellframe_hello_result -eq 0 ] && echo "✅ PASS" || echo "❌ FAIL")"
echo "  simple_wallet: $([ $simple_wallet_result -eq 0 ] && echo "✅ PASS" || echo "❌ FAIL")"
echo "  complex_wallet: $([ $complex_wallet_result -eq 0 ] && echo "✅ PASS" || echo "❌ FAIL")"

echo
echo "=== Summary ==="

# Подсчет результатов
total_tests=4
passed_tests=$(( (dap_hello_result == 0 ? 1 : 0) + (cellframe_hello_result == 0 ? 1 : 0) + (simple_wallet_result == 0 ? 1 : 0) + (complex_wallet_result == 0 ? 1 : 0) ))

echo "Total tests: $total_tests"
echo "Passed: $passed_tests"
echo "Failed: $((total_tests - passed_tests))"
echo "Success rate: $((passed_tests * 100 / total_tests))%"

if [ $passed_tests -eq $total_tests ]; then
    echo
    echo "🎉 ALL EXAMPLES COMPILE SUCCESSFULLY! 🎉"
    echo "100% compilation success rate achieved!"
    exit 0
else
    echo
    echo "❌ Some examples failed to compile"
    echo "Please check the errors above and fix them"
    exit 1
fi


