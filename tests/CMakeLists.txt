cmake_minimum_required(VERSION 3.13)
project(cellframe_tests LANGUAGES C CXX)

# ─────────────────────── GoogleTest ────────────────────────
include(FetchContent)
FetchContent_Declare(googletest
    URL https://github.com/google/googletest/archive/refs/tags/v1.14.0.zip)
FetchContent_MakeAvailable(googletest)

# ─────────────────────── Исходник теста ─────────────────────
add_executable(test_base58 test_base58.cpp)

target_include_directories(test_base58 PRIVATE
    ${CMAKE_SOURCE_DIR}/dap-sdk/crypto/include
    ${CMAKE_SOURCE_DIR}/dap-sdk/core/include
    ${CMAKE_SOURCE_DIR}/dap-sdk/crypto/external/xkcp/Keccak   # KeccakHash.h
)

# ─────────────────── Библиотеки SDK (core + crypto) ────────
# 1) Если таргеты уже экспортированы SDK-ом, просто используем их.
# 2) Если нет — создаём IMPORTED-обёртки и указываем будущий путь
#    (build/lib/libdap*.{a,so} появятся к моменту линковки).

# --- CORE ---
if(TARGET dap)
    set(DAP_CORE_TGT dap)
elseif(NOT TARGET dap_core)       # чтобы не переопределить, если уже есть
    set(_core_path_a  ${CMAKE_BINARY_DIR}/lib/libdap.a)
    set(_core_path_so ${CMAKE_BINARY_DIR}/lib/libdap.so)
    add_library(dap_core UNKNOWN IMPORTED)
    set_target_properties(dap_core PROPERTIES
        IMPORTED_LOCATION "${_core_path_a}"
        IMPORTED_LOCATION_RELEASE "${_core_path_a}"
        IMPORTED_LOCATION_RELWITHDEBINFO "${_core_path_a}"
        IMPORTED_LOCATION_MINSIZEREL "${_core_path_a}"
        IMPORTED_LOCATION_DEBUG "${_core_path_so}"
    )
    set(DAP_CORE_TGT dap_core)
endif()

# --- CRYPTO ---
if(TARGET dapcrypto)
    set(DAP_CRYPTO_TGT dapcrypto)         # встречается без тире
elseif(TARGET dap-crypto)
    set(DAP_CRYPTO_TGT dap-crypto)
elseif(NOT TARGET dap_crypto)
    set(_crypto_path_a  ${CMAKE_BINARY_DIR}/lib/libdap-crypto.a)
    set(_crypto_path_so ${CMAKE_BINARY_DIR}/lib/libdap-crypto.so)
    add_library(dap_crypto UNKNOWN IMPORTED)
    set_target_properties(dap_crypto PROPERTIES
        IMPORTED_LOCATION "${_crypto_path_a}"
        IMPORTED_LOCATION_RELEASE "${_crypto_path_a}"
        IMPORTED_LOCATION_RELWITHDEBINFO "${_crypto_path_a}"
        IMPORTED_LOCATION_MINSIZEREL "${_crypto_path_a}"
        IMPORTED_LOCATION_DEBUG "${_crypto_path_so}"
    )
    set(DAP_CRYPTO_TGT dap_crypto)
endif()

# ─────────────────────── Линковка ───────────────────────────
target_link_libraries(test_base58 PRIVATE
    ${DAP_CORE_TGT}
    ${DAP_CRYPTO_TGT}
    gtest gtest_main
)

# ─────────────────────── CTest + Allure ─────────────────────
enable_testing()
add_test(NAME base58_roundtrip
    COMMAND test_base58
            --gtest_output=xml:${CMAKE_BINARY_DIR}/unit_tests.xml)
