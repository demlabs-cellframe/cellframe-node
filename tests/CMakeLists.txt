cmake_minimum_required(VERSION 3.16)

# ────────────────────────────────────────────────────────────────
#  Cellframe unit-tests
# ────────────────────────────────────────────────────────────────
project(cellframe_tests LANGUAGES CXX)

enable_testing()

#-----------------------------------------------------------------
#  1.  Include-директории SDK
#-----------------------------------------------------------------
set(DAP_ROOT ${CMAKE_CURRENT_SOURCE_DIR}/..)     # ← корень cellframe-node

set(DAP_CORE_INC   ${DAP_ROOT}/dap-sdk/core/include)
set(DAP_CRYPTO_INC ${DAP_ROOT}/dap-sdk/crypto/include)
set(DAP_XKCP_INC
        ${DAP_ROOT}/dap-sdk/crypto/external/xkcp/Standalone
        ${DAP_ROOT}/dap-sdk/crypto/external/xkcp/Standalone/CompactFIPS202
        ${DAP_ROOT}/dap-sdk/crypto/external/xkcp/Keccak)

include_directories(
        ${DAP_CORE_INC}
        ${DAP_CRYPTO_INC}
        ${DAP_XKCP_INC}
)

#-----------------------------------------------------------------
#  2.  GTest
#      Debian-пакет libgtest-dev не содержит .so и конфиг-файла,
#      поэтому ищем вручную то, что собрали в job-e.
#-----------------------------------------------------------------
find_path(GTEST_INCLUDE_DIR gtest/gtest.h
          HINTS /usr/include /usr/local/include REQUIRED)

find_library(GTEST_LIBRARY       NAMES gtest       HINTS /usr/lib /usr/local/lib REQUIRED)
find_library(GTEST_MAIN_LIBRARY  NAMES gtest_main  HINTS /usr/lib /usr/local/lib REQUIRED)

add_library(GTest::gtest       UNKNOWN IMPORTED)
add_library(GTest::gtest_main  UNKNOWN IMPORTED)

set_target_properties(GTest::gtest
        PROPERTIES IMPORTED_LOCATION "${GTEST_LIBRARY}")
set_target_properties(GTest::gtest_main
        PROPERTIES IMPORTED_LOCATION "${GTEST_MAIN_LIBRARY}")

include_directories(${GTEST_INCLUDE_DIR})

#-----------------------------------------------------------------
#  3.  SDK библиотеки
#      При конфигурировании всего проекта цели «dap» и «dap-crypto»
#      уже объявлены, просто делаем алиасы чтобы использовать их здесь.
#-----------------------------------------------------------------
if(NOT TARGET dap)
    message(FATAL_ERROR
            "Target 'dap' not found. Конфигурируйте ВСЮ репу (cmake -S . -B build -DBUILD_TESTS=ON) "
            "— тогда dap/dap-crypto будут собраны до unit-тестов.")
endif()

add_library(dap_core   ALIAS dap)
add_library(dap_crypto ALIAS dap-crypto)

#-----------------------------------------------------------------
#  4.  Собираем каждый *.cpp в tests/ в отдельный исполняемый файл
#-----------------------------------------------------------------
file(GLOB TEST_SRC LIST_DIRECTORIES false
     "${CMAKE_CURRENT_SOURCE_DIR}/*.cpp")

foreach(test_file IN LISTS TEST_SRC)
    get_filename_component(test_name "${test_file}" NAME_WE)

    add_executable(${test_name} "${test_file}")

    target_link_libraries(${test_name}
            PRIVATE
                GTest::gtest_main
                dap_core
                dap_crypto
    )

    add_test(NAME ${test_name}
             COMMAND ${test_name})
endforeach()

#-----------------------------------------------------------------
#  5.  Удобный вывод
#-----------------------------------------------------------------
message(STATUS "➤  Unit-tests: ${TEST_SRC}")
