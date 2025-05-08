cmake_minimum_required(VERSION 3.16)
project(cellframe_tests LANGUAGES CXX)
enable_testing()

# ---------- googletest ----------
include(FetchContent)

FetchContent_Declare(
    googletest
    GIT_REPOSITORY https://github.com/google/googletest.git
    GIT_TAG        v1.14.0       # актуальный релиз
)
# при желании можно запретить автоматическое обновление тегов
#   GIT_SHALLOW    TRUE
FetchContent_MakeAvailable(googletest)

# ---------- SDK include-dirs ----------
set(DAP_ROOT ${CMAKE_SOURCE_DIR})
include_directories(
  ${DAP_ROOT}/dap-sdk/core/include
  ${DAP_ROOT}/dap-sdk/crypto/include
  ${DAP_ROOT}/dap-sdk/crypto/external/xkcp/Standalone
  ${DAP_ROOT}/dap-sdk/crypto/external/xkcp/Standalone/CompactFIPS202
  ${DAP_ROOT}/dap-sdk/crypto/external/xkcp/Keccak
)

# ---------- берём готовые цели, если они уже существуют ----------
if(TARGET dap_core OR TARGET dap-core)
  # одна из них точно есть после сборки SDK
  set(DAP_CORE_TARGET $<IF:$<TARGET_EXISTS:dap_core>,dap_core,dap-core>)
else()
  # fallback: импортируем собранную .so
  find_library(DAP_CORE_LIB NAMES dap dap-core PATHS ${DAP_ROOT}/build/lib NO_DEFAULT_PATH)
  if(NOT DAP_CORE_LIB)
    message(FATAL_ERROR "libdap(.so) не найден — убедитесь, что SDK собран до unit-тестов")
  endif()
  add_library(dap_core UNKNOWN IMPORTED)
  set_target_properties(dap_core PROPERTIES IMPORTED_LOCATION "${DAP_CORE_LIB}")
  set(DAP_CORE_TARGET dap_core)
endif()

if(TARGET dap_crypto OR TARGET dap-crypto)
  set(DAP_CRYPTO_TARGET $<IF:$<TARGET_EXISTS:dap_crypto>,dap_crypto,dap-crypto>)
else()
  find_library(DAP_CRYPTO_LIB NAMES dap-crypto dap_crypto PATHS ${DAP_ROOT}/build/lib NO_DEFAULT_PATH)
  if(NOT DAP_CRYPTO_LIB)
    message(FATAL_ERROR "libdap-crypto(.so) не найден — убедитесь, что SDK собран")
  endif()
  add_library(dap_crypto UNKNOWN IMPORTED)
  set_target_properties(dap_crypto PROPERTIES IMPORTED_LOCATION "${DAP_CRYPTO_LIB}")
  set(DAP_CRYPTO_TARGET dap_crypto)
endif()

# ---------- unit-test ----------
add_executable(test_base58 test_base58.cpp)
target_link_libraries(test_base58 PRIVATE gtest_main ${DAP_CORE_TARGET} ${DAP_CRYPTO_TARGET})
add_test(NAME base58 COMMAND test_base58)
