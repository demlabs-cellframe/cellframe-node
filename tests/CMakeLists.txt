# tests/CMakeLists.txt
cmake_minimum_required(VERSION 3.16)
project(cellframe_tests LANGUAGES CXX)

# ------------------------------------------------------------
# 1.  Настройки компилятора/линковщика для всех тестов
# ------------------------------------------------------------
enable_testing()
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

# ------------------------------------------------------------
# 2.  Пути до SDK (ищем ОДИН раз ― от корня репозитория)
# ------------------------------------------------------------
get_filename_component(PROJECT_ROOT "${CMAKE_CURRENT_LIST_DIR}/.." ABSOLUTE)
set(DAP_ROOT         "${PROJECT_ROOT}")                       # = cellframe-node
set(DAP_CORE_INC     "${DAP_ROOT}/dap-sdk/core/include")
set(DAP_CRYPTO_INC   "${DAP_ROOT}/dap-sdk/crypto/include")
set(XKCP_ROOT        "${DAP_ROOT}/dap-sdk/crypto/external/xkcp")

# — в XKCP заголовок KeccakHash.h может лежать в разных подпапках,
#   поэтому найдём его динамически ― и потом добавим нужный include-dir.
file(GLOB_RECURSE _KECCAK_HDR "${XKCP_ROOT}/**/KeccakHash.h")
if(NOT _KECCAK_HDR)
    message(FATAL_ERROR "KeccakHash.h not found inside ${XKCP_ROOT}")
endif()
get_filename_component(XKCP_KHASH_DIR "${_KECCAK_HDR}" DIRECTORY)

include_directories(
    ${DAP_CORE_INC}
    ${DAP_CRYPTO_INC}
    ${XKCP_KHASH_DIR}                 # <- гарантируем видимость KeccakHash.h
)

# ------------------------------------------------------------
# 3.  GoogleTest: system → vendored → fatal
# ------------------------------------------------------------
# 3.1 Пытаемся взять готовые .so, которые ставит `apt install libgtest-dev`
find_package(GTest CONFIG QUIET)
if (GTest_FOUND)
    message(STATUS "Using system GTest: ${GTest_VERSION}")
    set(GTEST_LIBRARIES GTest::gtest GTest::gtest_main)
else()
    # 3.2  Если системного нет ― берём копию, идущую в под-модуле third_party
    set(VENDORED_GTEST_DIR "${PROJECT_ROOT}/third_party/googletest")
    if (EXISTS "${VENDORED_GTEST_DIR}/CMakeLists.txt")
        add_subdirectory(${VENDORED_GTEST_DIR} EXCLUDE_FROM_ALL)
        set(GTEST_LIBRARIES gtest gtest_main)
        message(STATUS "Using vendored GTest from ${VENDORED_GTEST_DIR}")
    else()
        message(FATAL_ERROR "GoogleTest not found (neither system nor vendored)")
    endif()
endif()

# ------------------------------------------------------------
# 4.  Библиотеки SDK
# ------------------------------------------------------------
# В обычной сборке targets `dap` / `dap-crypto` уже существуют.
# Но при локальной разработке их может ещё не быть ⇒ сделаем
#   fallback на IMPORTED ‐ .so из каталога сборки.
function(_import_if_missing target libname)
    if(NOT TARGET ${target})
        find_library(_lib NAMES ${libname} PATHS
                     "${PROJECT_BINARY_DIR}/lib"
                     "${DAP_ROOT}/build/lib"
                     NO_DEFAULT_PATH)
        if(NOT _lib)
            message(FATAL_ERROR "Neither target '${target}' nor library '${libname}' found")
        endif()
        add_library(${target} UNKNOWN IMPORTED)
        set_target_properties(${target} PROPERTIES IMPORTED_LOCATION "${_lib}")
        message(STATUS "Imported ${target} from ${_lib}")
    endif()
endfunction()

_import_if_missing(dap_core   dap-core)
_import_if_missing(dap_crypto dap-crypto)

# ------------------------------------------------------------
# 5.  Сканируем *.cpp / *_test.cpp и готовим исполняемые файлы
# ------------------------------------------------------------
file(GLOB TEST_SOURCES CONFIGURE_DEPENDS "${PROJECT_ROOT}/tests/*.cpp")

if(TEST_SOURCES STREQUAL "")
    message(STATUS "No unit-test sources (*.cpp) found, skipping tests")
    return()
endif()

foreach(src ${TEST_SOURCES})
    get_filename_component(fname "${src}" NAME_WE)      # test_base58 …
    add_executable(${fname} ${src})

    target_link_libraries(${fname}
        PRIVATE
            ${GTEST_LIBRARIES}
            dap_core
            dap_crypto
    )

    add_test(NAME ${fname} COMMAND ${fname})
endforeach()

# ------------------------------------------------------------
# 6.  Красивая сводка
# ------------------------------------------------------------
message(STATUS "✓ Unit-tests configured:  ${TEST_SOURCES}")
