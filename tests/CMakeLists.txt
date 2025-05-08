# tests/CMakeLists.txt
cmake_minimum_required(VERSION 3.16)
project(cellframe_tests LANGUAGES C CXX)

enable_testing()

# ──────────────────────────────────────────────────────────────
# 🥇  Попытка №1 ― системный GoogleTest
# ──────────────────────────────────────────────────────────────
find_package(GTest QUIET CONFIG)     # ищет GTest::gtest и GTest::gtest_main
set(GTEST_OK FALSE)

if (GTest_FOUND)
    # На Debian/Ubuntu нужно собрать библиотеку вручную,
    # потому что пакет ставит ТОЛЬКО исходники:
    #   sudo apt-get install --yes libgtest-dev && \
    #   cd /usr/src/gtest && sudo cmake -DBUILD_SHARED_LIBS=ON . && \
    #   sudo make -j$(nproc) && sudo cp *.so /usr/lib
    #
    # Но в Docker-образе, который вы уже используете, мы можем
    # сделать это несколькими командами (см. .gitlab-ci.yml).
    #
    message(STATUS "Use system GTest found at ${GTEST_ROOT}")
    set(GTEST_OK TRUE)
else()
    message(STATUS "System GTest **NOT** found — fall back to vendored copy")
endif()

# ──────────────────────────────────────────────────────────────
# 🥈  Попытка №2 ― вендорная копия в репозитории
# ──────────────────────────────────────────────────────────────
if (NOT GTEST_OK)
    # third_party/googletest               ← clone или submodule
    add_subdirectory(${CMAKE_CURRENT_SOURCE_DIR}/../third_party/googletest
                     ${CMAKE_BINARY_DIR}/_gtest_build
                     EXCLUDE_FROM_ALL)

    # Внутри googletest уже создаётся target gtest и gtest_main
    # Синхронизируем имена с вариантами find_package()
    add_library(GTest::gtest       ALIAS gtest)
    add_library(GTest::gtest_main  ALIAS gtest_main)
endif()

# ──────────────────────────────────────────────────────────────
#  Путь к Cellframe-SDK
# ──────────────────────────────────────────────────────────────
set(DAP_ROOT         ${CMAKE_SOURCE_DIR})                      # корень cellframe-node
set(DAP_CORE_INC     ${DAP_ROOT}/dap-sdk/core/include)
set(DAP_CRYPTO_INC   ${DAP_ROOT}/dap-sdk/crypto/include)
set(DAP_XKCP_INC
    ${DAP_ROOT}/dap-sdk/crypto/external/xkcp/Standalone
    ${DAP_ROOT}/dap-sdk/crypto/external/xkcp/Standalone/CompactFIPS202
    ${DAP_ROOT}/dap-sdk/crypto/external/xkcp/Keccak)

include_directories(
    ${DAP_CORE_INC}
    ${DAP_CRYPTO_INC}
    ${DAP_XKCP_INC}
)

# ──────────────────────────────────────────────────────────────
#  Импорт уже собранных .so из основного билда
# ──────────────────────────────────────────────────────────────
find_library(DAP_CORE_LIB
             NAMES dap dap-core
             PATHS ${DAP_ROOT}/build/lib NO_DEFAULT_PATH REQUIRED)

find_library(DAP_CRYPTO_LIB
             NAMES dap_crypto dap-crypto
             PATHS ${DAP_ROOT}/build/lib NO_DEFAULT_PATH REQUIRED)

if(NOT TARGET dap_core)
    add_library(dap_core SHARED IMPORTED)
    set_target_properties(dap_core PROPERTIES IMPORTED_LOCATION "${DAP_CORE_LIB}")
endif()

if(NOT TARGET dap_crypto)
    add_library(dap_crypto SHARED IMPORTED)
    set_target_properties(dap_crypto PROPERTIES IMPORTED_LOCATION "${DAP_CRYPTO_LIB}")
endif()

# ──────────────────────────────────────────────────────────────
#  Тесты
# ──────────────────────────────────────────────────────────────
add_executable(test_base58 test_base58.cpp)
target_link_libraries(test_base58
    PRIVATE
        GTest::gtest_main          # всегда присутствует благодаря шагам выше
        dap_core
        dap_crypto
)

add_test(NAME base58 COMMAND test_base58)
