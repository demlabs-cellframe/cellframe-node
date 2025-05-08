cmake_minimum_required(VERSION 3.16)

# --------------------------------------------------
#  Cellframe unit-tests (GoogleTest)
# --------------------------------------------------
project(cellframe_unit_tests LANGUAGES CXX)

# Build settings -------------------------------------------------------------
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# ---------------------------------------------------------------------------
# GoogleTest (we fetch it on-the-fly so the runner doesn’t need anything)
# ---------------------------------------------------------------------------
include(FetchContent)
FetchContent_Declare(
    googletest
    URL https://github.com/google/googletest/archive/refs/tags/v1.14.0.zip
)
set(gtest_force_shared_crt ON CACHE BOOL "" FORCE) # MSVC friendly, harmless here
FetchContent_MakeAvailable(googletest)

enable_testing()

# ---------------------------------------------------------------------------
# Paths to SDK artefacts produced by the main build
# ---------------------------------------------------------------------------
set(DAP_CORE_INC    ${CMAKE_SOURCE_DIR}/dap-sdk/core/include)
set(DAP_CRYPTO_INC  ${CMAKE_SOURCE_DIR}/dap-sdk/crypto/include)
set(XKCP_BASE       ${CMAKE_SOURCE_DIR}/dap-sdk/crypto/external/xkcp)

# ---------------------------------------------------------------------------
# Import the already-built static libraries (produced by the parent build)
# ---------------------------------------------------------------------------
# libdap
add_library(dap STATIC IMPORTED)
set_target_properties(dap PROPERTIES
    IMPORTED_LOCATION         ${CMAKE_BINARY_DIR}/lib/libdap.a
    INTERFACE_INCLUDE_DIRECTORIES "${DAP_CORE_INC}"
)

# libdap-crypto
add_library(dap_crypto STATIC IMPORTED)
set_target_properties(dap_crypto PROPERTIES
    IMPORTED_LOCATION         ${CMAKE_BINARY_DIR}/lib/libdap-crypto.a
    INTERFACE_INCLUDE_DIRECTORIES "${DAP_CRYPTO_INC}"
)

# ---------------------------------------------------------------------------
# Unit-test target
# ---------------------------------------------------------------------------
add_executable(test_base58 test_base58.cpp)

# Headers
 target_include_directories(test_base58 PRIVATE
    ${DAP_CORE_INC}
    ${DAP_CRYPTO_INC}
    ${XKCP_BASE}/Standalone              # KeccakHash.h lives here
    ${XKCP_BASE}/Standalone/CompactFIPS202
    ${XKCP_BASE}/Keccak
)

# Linkage
 target_link_libraries(test_base58
    PRIVATE
        dap
        dap_crypto
        gtest_main
)

# Register with CTest so `ctest` just works
add_test(NAME base58 COMMAND test_base58)