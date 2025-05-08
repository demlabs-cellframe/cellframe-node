cmake_minimum_required(VERSION 3.13)

project(cellframe-tests)

# Генерация заглушки KeccakHash.h, если он не найден
if(NOT EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/../dap-sdk/crypto/external/xkcp/KeccakHash.h")
    message(WARNING "KeccakHash.h не найден в XKCP; сгенерирована заглушка")
    file(WRITE ${CMAKE_BINARY_DIR}/generated/KeccakHash.h "// stub header\n")
    include_directories(${CMAKE_BINARY_DIR}/generated)
else()
    include_directories(${CMAKE_CURRENT_SOURCE_DIR}/../dap-sdk/crypto/external/xkcp)
endif()

# Подключаем GTest
enable_testing()
include_directories(/usr/src/gtest /usr/include)
add_library(gtest STATIC /usr/src/gtest/src/gtest-all.cc)
add_library(gtest_main STATIC /usr/src/gtest/src/gtest_main.cc)
target_include_directories(gtest PUBLIC /usr/src/gtest/include)
find_package(Threads REQUIRED)
target_link_libraries(gtest PUBLIC Threads::Threads)

# Общие include-пути
include_directories(
    ${CMAKE_SOURCE_DIR}/tests
    ${CMAKE_SOURCE_DIR}/dap-sdk/core/include
    ${CMAKE_SOURCE_DIR}/dap-sdk/crypto/include
)

# test_base58
add_executable(test_base58 test_base58.cpp)
target_link_libraries(test_base58 gtest_main dap-crypto)
add_test(NAME base58 COMMAND test_base58)

# test_network_status
add_executable(test_network_status test_network_status.cpp)
target_link_libraries(test_network_status gtest_main dap-network)
add_test(NAME network_status COMMAND test_network_status)
