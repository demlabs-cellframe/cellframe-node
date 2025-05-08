cmake_minimum_required(VERSION 3.16)
project(cellframe_tests LANGUAGES CXX)

enable_testing()
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

# ---------- 1.  Пути до SDK ----------
get_filename_component(PROJECT_ROOT "${CMAKE_CURRENT_LIST_DIR}/.." ABSOLUTE)
set(DAP_ROOT "${PROJECT_ROOT}")

set(DAP_CORE_INC   "${DAP_ROOT}/dap-sdk/core/include")
set(DAP_CRYPTO_INC "${DAP_ROOT}/dap-sdk/crypto/include")
set(XKCP_ROOT      "${DAP_ROOT}/dap-sdk/crypto/external/xkcp")

# ---------- 2.  KeccakHash.h ----------
file(GLOB_RECURSE _KHASH "${XKCP_ROOT}/**/KeccakHash.h")

if(_KHASH)
    get_filename_component(XKCP_KHASH_DIR "${_KHASH}" DIRECTORY)
else()
    # ── файла нет — делаем заглушку ───────────────────────────────
    set(GEN_DIR "${CMAKE_BINARY_DIR}/generated")
    file(MAKE_DIRECTORY "${GEN_DIR}")

    set(STUB "${GEN_DIR}/KeccakHash.h")
    file(WRITE "${STUB}" "/* auto-generated stub */\n#pragma once\n\n#include <stdint.h>\n#ifdef __cplusplus\nextern \"C\" {\n#endif\n\nvoid Keccak_HashInitialize_SHA3_256(void *state);\nvoid Keccak_HashUpdate(void *state, const unsigned char *data, size_t len);\nvoid Keccak_HashFinal(void *state, unsigned char *hash);\n\n#ifdef __cplusplus\n}\n#endif\n")

    set(XKCP_KHASH_DIR "${GEN_DIR}")
    message(WARNING "KeccakHash.h не найден в XKCP; сгенерирована заглушка ${STUB}")
endif()

include_directories(
    ${DAP_CORE_INC}
    ${DAP_CRYPTO_INC}
    ${XKCP_KHASH_DIR}   # ←  оригинал или stub
)

# ---------- 3.  GoogleTest ----------
find_package(GTest CONFIG QUIET)
if (GTest_FOUND)
    message(STATUS "System GTest: ${GTest_VERSION}")
    set(GTEST_LIBS GTest::gtest GTest::gtest_main)
else()
    set(VENDORED "${PROJECT_ROOT}/third_party/googletest")
    if(EXISTS "${VENDORED}/CMakeLists.txt")
        add_subdirectory(${VENDORED} EXCLUDE_FROM_ALL)
        set(GTEST_LIBS gtest gtest_main)
        message(STATUS "Vendored GTest из ${VENDORED}")
    else()
        message(FATAL_ERROR "GoogleTest not found")
    endif()
endif()

# ---------- 4.  Импортируем libdap(.so) при необходимости ----------
function(import_if_missing tgt name)
    if(NOT TARGET ${tgt})
        find_library(lib NAMES ${name} PATHS
                     "${DAP_ROOT}/build/lib" "${PROJECT_BINARY_DIR}/lib"
                     NO_DEFAULT_PATH)
        if(NOT lib)
            message(FATAL_ERROR "Ни target '${tgt}', ни библиотека '${name}' не найдены")
        endif()
        add_library(${tgt} UNKNOWN IMPORTED)
        set_target_properties(${tgt} PROPERTIES IMPORTED_LOCATION "${lib}")
        message(STATUS "Imported ${tgt} → ${lib}")
    endif()
endfunction()

import_if_missing(dap_core   dap-core)
import_if_missing(dap_crypto dap-crypto)

# ---------- 5.  Собираем каждую *.cpp в отдельный тест ----------
file(GLOB TEST_SRC CONFIGURE_DEPENDS "${PROJECT_ROOT}/tests/*.cpp")

if(TEST_SRC STREQUAL "")
    message(STATUS "Нет *.cpp в tests/, пропускаем unit-tests")
    return()
endif()

foreach(src ${TEST_SRC})
    get_filename_component(bin "${src}" NAME_WE)
    add_executable(${bin} ${src})

    target_link_libraries(${bin}
        PRIVATE
            ${GTEST_LIBS}
            dap_core
            dap_crypto)

    add_test(NAME ${bin} COMMAND ${bin})
endforeach()

message(STATUS "✓ Unit-tests configured: ${TEST_SRC}")
