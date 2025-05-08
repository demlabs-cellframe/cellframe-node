cmake_minimum_required(VERSION 3.16)

# ────────────────────────────────────────────────────────────────
#  Cellframe unit-tests
# ────────────────────────────────────────────────────────────────
project(cellframe_tests LANGUAGES CXX)

enable_testing()

#-----------------------------------------------------------------
#  1.  SDK include-директории
#-----------------------------------------------------------------
set(DAP_SRC_ROOT  ${CMAKE_CURRENT_SOURCE_DIR}/..)          # репозиторий
set(DAP_CORE_INC  ${DAP_SRC_ROOT}/dap-sdk/core/include)
set(DAP_CRYPTO_INC ${DAP_SRC_ROOT}/dap-sdk/crypto/include)
set(DAP_XKCP_INC
        ${DAP_SRC_ROOT}/dap-sdk/crypto/external/xkcp/Standalone
        ${DAP_SRC_ROOT}/dap-sdk/crypto/external/xkcp/Standalone/CompactFIPS202
        ${DAP_SRC_ROOT}/dap-sdk/crypto/external/xkcp/Keccak)

include_directories(
        ${DAP_CORE_INC}
        ${DAP_CRYPTO_INC}
        ${DAP_XKCP_INC}
)

#-----------------------------------------------------------------
#  2.  GoogleTest, собранный в job-е из libgtest-dev
#-----------------------------------------------------------------
find_path(GTEST_INCLUDE_DIR gtest/gtest.h
          HINTS /usr/include /usr/local/include REQUIRED)

find_library(GTEST_LIBRARY      NAMES gtest       HINTS /usr/lib /usr/local/lib REQUIRED)
find_library(GTEST_MAIN_LIBRARY NAMES gtest_main  HINTS /usr/lib /usr/local/lib REQUIRED)

add_library(GTest::gtest       UNKNOWN IMPORTED)
add_library(GTest::gtest_main  UNKNOWN IMPORTED)

set_target_properties(GTest::gtest
    PROPERTIES IMPORTED_LOCATION "${GTEST_LIBRARY}")
set_target_properties(GTest::gtest_main
    PROPERTIES IMPORTED_LOCATION "${GTEST_MAIN_LIBRARY}")

include_directories(${GTEST_INCLUDE_DIR})

#-----------------------------------------------------------------
#  3.  Автопоиск тестовых исходников
#      Каждый *.cpp ⇒ свой executable + ctest
#-----------------------------------------------------------------
file(GLOB TEST_SOURCES
     LIST_DIRECTORIES FALSE
     "${CMAKE_CURRENT_SOURCE_DIR}/*.cpp")

foreach(src IN LISTS TEST_SOURCES)
    get_filename_component(test_name "${src}" NAME_WE)

    add_executable(${test_name} "${src}")

    # NB: цели ‘dap’ и ‘dap-crypto’ объявляются в корневом CMakeLists
    #     CMake спокойно разрешит их позже, поэтому можно ссылаться
    #     напрямую, не создавая ALIAS заранее.
    target_link_libraries(${test_name}
        PRIVATE
            GTest::gtest_main
            dap
            dap-crypto
    )

    add_test(NAME ${test_name}
             COMMAND ${test_name})

endforeach()

#-----------------------------------------------------------------
#  4.  Информативный вывод
#-----------------------------------------------------------------
message(STATUS "➤  Unit-tests, найденные файлы: ${TEST_SOURCES}")
