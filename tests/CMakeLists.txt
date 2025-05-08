cmake_minimum_required(VERSION 3.13)
project(cellframe_tests LANGUAGES C CXX)

# ── GoogleTest ───────────────────────────────────────────────────────────────
include(FetchContent)
FetchContent_Declare(
    googletest
    URL https://github.com/google/googletest/archive/refs/tags/v1.14.0.zip
)
FetchContent_MakeAvailable(googletest)

# ── Тестовый исполняемый файл ────────────────────────────────────────────────
add_executable(test_base58 test_base58.cpp)

# ── Подхватываем все include‑диры прямо из экспортированных таргетов SDK ─────
# dap-crypto тянет transitively core, Keccak и прочие заголовки —
# забираем их через get_target_property, чтобы не гадать путь вручную.
if(TARGET dap-crypto)
    get_target_property(DAPCRYPTO_INCS dap-crypto INTERFACE_INCLUDE_DIRECTORIES)
    target_include_directories(test_base58 PRIVATE ${DAPCRYPTO_INCS})
else()
    message(FATAL_ERROR "Target 'dap-crypto' not found — проверьте, как называется crypto‑библиотека в сборке SDK")
endif()

# ── Линкуем против SDK и GoogleTest ──────────────────────────────────────────
target_link_libraries(test_base58 PRIVATE
    dap             # основная libdap (ядро)
    dap-crypto      # crypto‑модуль (или dapcrypto, если у вас так называется)
    gtest gtest_main
)

# ── Регистрируем CTest + XML‑вывод для Allure ────────────────────────────────
enable_testing()
add_test(
    NAME base58_roundtrip
    COMMAND test_base58 --gtest_output=xml:${CMAKE_BINARY_DIR}/unit_tests.xml
)
