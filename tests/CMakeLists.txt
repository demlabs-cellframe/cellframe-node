cmake_minimum_required(VERSION 3.13)          # в образе demlabs/debian/qt5 CMake 3.13.4
project(cellframe_tests LANGUAGES C CXX)

# ───────────────────────────────── GoogleTest ────────────────────────────────
include(FetchContent)
FetchContent_Declare(
    googletest
    URL https://github.com/google/googletest/archive/refs/tags/v1.14.0.zip
)
FetchContent_MakeAvailable(googletest)

# ───────────────────────────────── test_base58 ───────────────────────────────
add_executable(test_base58 test_base58.cpp)

# заголовочные файлы SDK
target_include_directories(test_base58 PRIVATE
    ${PROJECT_SOURCE_DIR}/dap-sdk/crypto/include
    ${PROJECT_SOURCE_DIR}/dap-sdk/core/include
)

# линки против SDK и GoogleTest
target_link_libraries(test_base58 PRIVATE
    dap             # основная библиотека (static/shared — как собирает SDK)
    dap-crypto      # модуль crypto
    gtest gtest_main
)

# регистрируем CTest + вывод в XML для Allure
add_test(
    NAME base58_roundtrip
    COMMAND test_base58 --gtest_output=xml:${CMAKE_BINARY_DIR}/unit_tests.xml
)
