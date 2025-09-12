#!/bin/bash

# Простой скрипт для компиляции примеров без CMake
# Используется для быстрого тестирования

set -e

echo "=== Simple Example Compilation Test ==="
echo

# Функция для компиляции примера
compile_example() {
    local example_name=$1
    local source_file=$2
    local include_dirs=$3
    local libraries=$4

    echo "Compiling $example_name..."

    # Компиляция
    local cmd="gcc -o $example_name $source_file -I$include_dirs $libraries -Wall -Wextra -O2 -DDAP_OS_LINUX"
    echo "  Command: $cmd"

    # Security fix: avoid eval with user data, use direct execution
    if $cmd 2>/dev/null; then
        echo "  ✅ $example_name compiled successfully"
        echo "  📍 Executable: $(pwd)/$example_name"
        return 0
    else
        echo "  ❌ $example_name compilation failed"
        return 1
    fi
}

# Компиляция DAP SDK Hello World
echo "Testing DAP SDK Hello World..."
cd /home/naeper/work/cellframe-node/dap-sdk/docs/examples/hello_world

if compile_example "dap_hello_world" "main.c" \
    "../../../core/include:../../../crypto/include" \
    "-L../../../build/core -ldap_common -ldap_core -lpthread -lm"; then
    dap_result=0
else
    dap_result=1
fi

echo

# Компиляция CellFrame Simple Wallet
echo "Testing CellFrame Simple Wallet..."
cd /home/naeper/work/cellframe-node/cellframe-sdk/docs/examples/simple_wallet

if compile_example "simple_wallet" "main.c" \
    "../../../modules/common/include:../../../modules/wallet/include:../../../dap-sdk/core/include:../../../dap-sdk/crypto/include" \
    "-L../../../build/modules/wallet -L../../../build/dap-sdk/core -L../../../build/dap-sdk/crypto -ldap_common -ldap_crypto -ldap_core -lcellframe-wallet -lpthread -lm -ljson-c"; then
    cellframe_result=0
else
    cellframe_result=1
fi

echo
echo "=== Compilation Results ==="
echo
echo "DAP SDK Hello World: $([ $dap_result -eq 0 ] && echo "✅ SUCCESS" || echo "❌ FAILED")"
echo "CellFrame Simple Wallet: $([ $cellframe_result -eq 0 ] && echo "✅ SUCCESS" || echo "❌ FAILED")"

echo
echo "=== Summary ==="
total=$((dap_result + cellframe_result))
if [ $total -eq 0 ]; then
    echo "🎉 All examples compiled successfully!"
    echo "100% compilation success rate!"
    exit 0
else
    echo "Some examples failed to compile"
    exit 1
fi



