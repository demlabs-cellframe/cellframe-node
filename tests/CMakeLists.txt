cmake_minimum_required(VERSION 3.13)
project(cellframe_tests LANGUAGES C CXX)

# ─────────── GoogleTest ───────────
include(FetchContent)
FetchContent_Declare(
    googletest
    URL https://github.com/google/googletest/archive/refs/tags/v1.14.0.zip
)
FetchContent_MakeAvailable(googletest)

# ─────────── test_base58 ──────────
add_executable(test_base58 test_base58.cpp)

target_include_directories(test_base58 PRIVATE
    ${PROJECT_SOURCE_DIR}/dap-sdk/crypto/include
    ${PROJECT_SOURCE_DIR}/dap-sdk/core/include
)

target_link_libraries(test_base58 PRIVATE
    dap
    dap-crypto
    gtest
    gtest_main
)

add_test(
    NAME base58_roundtrip
    COMMAND test_base58 --gtest_output=xml:${CMAKE_BINARY_DIR}/unit_tests.xml
)
