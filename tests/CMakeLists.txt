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

# ─────────────── объявляем будущие библиотеки ───────────────
# Предполагаем стандартный вывод SDK: build/lib/libdap*.{a,so}
set(_dap_core_path    ${CMAKE_BINARY_DIR}/lib/libdap.a)
set(_dap_crypto_path  ${CMAKE_BINARY_DIR}/lib/libdap-crypto.a)

# если SDK собирает .so, переключаемся на них
if(NOT EXISTS ${_dap_core_path})
    set(_dap_core_path    ${CMAKE_BINARY_DIR}/lib/libdap.so)
endif()
if(NOT EXISTS ${_dap_crypto_path})
    set(_dap_crypto_path  ${CMAKE_BINARY_DIR}/lib/libdap-crypto.so)
endif()

add_library(dap_core   UNKNOWN IMPORTED)
set_target_properties(dap_core   PROPERTIES IMPORTED_LOCATION ${_dap_core_path})

add_library(dap_crypto UNKNOWN IMPORTED)
set_target_properties(dap_crypto PROPERTIES IMPORTED_LOCATION ${_dap_crypto_path})

# ─────────────── линковка ───────────────────────────────────
target_link_libraries(test_base58 PRIVATE
    dap_core
    dap_crypto
    gtest gtest_main
)


# ─────────────── CTest + отчёт ────────────
enable_testing()
add_test(NAME base58_roundtrip
         COMMAND test_base58
                 --gtest_output=xml:${CMAKE_BINARY_DIR}/unit_tests.xml)
