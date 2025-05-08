cmake_minimum_required(VERSION 3.16)
project(cellframe_tests LANGUAGES CXX)

enable_testing()

# ---------- googletest ----------
include(FetchContent)
FetchContent_Declare(
    googletest
    URL https://github.com/google/googletest/archive/release-1.14.0.zip
)
FetchContent_MakeAvailable(googletest)

# ---------- SDK include-dirs ----------
set(DAP_ROOT ${CMAKE_SOURCE_DIR})        # корень cellframe-node
set(DAP_CORE_INC    ${DAP_ROOT}/dap-sdk/core/include)
set(DAP_CRYPTO_INC  ${DAP_ROOT}/dap-sdk/crypto/include)
set(DAP_XKCP_INC
    ${DAP_ROOT}/dap-sdk/crypto/external/xkcp/Standalone       # ← KeccakHash.h здесь
    ${DAP_ROOT}/dap-sdk/crypto/external/xkcp/Standalone/CompactFIPS202
    ${DAP_ROOT}/dap-sdk/crypto/external/xkcp/Keccak)

include_directories(
    ${DAP_CORE_INC}
    ${DAP_CRYPTO_INC}
    ${DAP_XKCP_INC}
)

# ---------- импортируем готовые libdap*.so ----------
# основной SDK кладёт .so в ${DAP_ROOT}/build/lib
find_library(DAP_CORE_LIB   NAMES dap dap-core   PATHS ${DAP_ROOT}/build/lib NO_DEFAULT_PATH)
find_library(DAP_CRYPTO_LIB NAMES dap-crypto dac_crypto dap_crypto PATHS ${DAP_ROOT}/build/lib NO_DEFAULT_PATH)

if(NOT TARGET dap_core)
    add_library(dap_core UNKNOWN IMPORTED)
    set_target_properties(dap_core PROPERTIES IMPORTED_LOCATION "${DAP_CORE_LIB}")
endif()

if(NOT TARGET dap_crypto)
    add_library(dap_crypto UNKNOWN IMPORTED)
    set_target_properties(dap_crypto PROPERTIES IMPORTED_LOCATION "${DAP_CRYPTO_LIB}")
endif()

# ---------- unit-test ----------
add_executable(test_base58 test_base58.cpp)
target_link_libraries(test_base58 PRIVATE gtest_main dap_core dap_crypto)

add_test(NAME base58 COMMAND test_base58)
