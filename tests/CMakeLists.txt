cmake_minimum_required(VERSION 3.13)
project(cellframe_tests LANGUAGES C CXX)

# ─────────────── GoogleTest ───────────────
include(FetchContent)
FetchContent_Declare(googletest
    URL https://github.com/google/googletest/archive/refs/tags/v1.14.0.zip)
FetchContent_MakeAvailable(googletest)

add_executable(test_base58 test_base58.cpp)

# ─────────────── include-диры ─────────────
target_include_directories(test_base58 PRIVATE
    ${CMAKE_SOURCE_DIR}/dap-sdk/crypto/include
    ${CMAKE_SOURCE_DIR}/dap-sdk/core/include
    ${CMAKE_SOURCE_DIR}/dap-sdk/crypto/external/xkcp/Keccak          # KeccakHash.h
)

# ─────────────── ищем готовые .so / .a ────
# core
find_library(DAP_CORE_LIB NAMES dap
             PATHS ${CMAKE_BINARY_DIR} ${CMAKE_SOURCE_DIR}/build
             PATH_SUFFIXES lib)
# crypto (встречаются три варианта имён)
find_library(DAP_CRYPTO_LIB NAMES dap-crypto dapcrypto dap_crypto
             PATHS ${CMAKE_BINARY_DIR} ${CMAKE_SOURCE_DIR}/build
             PATH_SUFFIXES lib)

if(NOT DAP_CORE_LIB OR NOT DAP_CRYPTO_LIB)
    message(FATAL_ERROR "Не нашёлся libdap или libdap-crypto. "
                        "Проверьте, что основной SDK собран до unit-теста.")
endif()

# ─────────────── линковка ────────────────
target_link_libraries(test_base58 PRIVATE
    ${DAP_CORE_LIB}
    ${DAP_CRYPTO_LIB}
    gtest gtest_main
)

# ─────────────── CTest + отчёт ────────────
enable_testing()
add_test(NAME base58_roundtrip
         COMMAND test_base58
                 --gtest_output=xml:${CMAKE_BINARY_DIR}/unit_tests.xml)
