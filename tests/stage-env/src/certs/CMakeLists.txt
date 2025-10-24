# Certificate Tools for Cellframe Node E2E Testing
cmake_minimum_required(VERSION 3.10)
project(CellframeCertTools C)

# Allow overriding paths via command-line (for Docker builds)
if(NOT DEFINED CELLFRAME_SDK_BUILD)
    # Default: relative path from tests/stage-env/src/certs
    set(CELLFRAME_SDK_BUILD "${CMAKE_CURRENT_SOURCE_DIR}/../../../../cellframe-sdk/build")
endif()

if(NOT DEFINED CELLFRAME_SDK_SRC)
    # Default: relative path from tests/stage-env/src/certs
    set(CELLFRAME_SDK_SRC "${CMAKE_CURRENT_SOURCE_DIR}/../../../../cellframe-sdk")
endif()

set(DAP_SDK_SRC "${CELLFRAME_SDK_SRC}/dap-sdk")

message(STATUS "Cellframe SDK Build: ${CELLFRAME_SDK_BUILD}")
message(STATUS "Cellframe SDK Source: ${CELLFRAME_SDK_SRC}")
message(STATUS "DAP SDK Source: ${DAP_SDK_SRC}")

# Detect target architecture (same way as DAP SDK does)
include(${DAP_SDK_SRC}/cmake/TargetArch_Detection.cmake)
target_architecture(TARGET_ARCH)

# Determine XKCP target based on architecture
if (${TARGET_ARCH} MATCHES "x86_64")
    set(XKCP_SUFFIX "x8664")
elseif(${TARGET_ARCH} MATCHES "armv7")
    set(XKCP_SUFFIX "armv7")
elseif(${TARGET_ARCH} MATCHES "armv8")
    set(XKCP_SUFFIX "armv8")
else()
    set(XKCP_SUFFIX "ref")
    message(WARNING "Unknown architecture ${TARGET_ARCH}, using reference XKCP implementation")
endif()

# Check if compiler supports -march=native
include(CheckCCompilerFlag)
CHECK_C_COMPILER_FLAG(-march=native COMPILER_SUPPORTS_MARCH_NATIVE)
if(COMPILER_SUPPORTS_MARCH_NATIVE)
    set(TARGET_POSTFIX "-native")
else()
    set(TARGET_POSTFIX "")
endif()

# Set XKCP paths
set(XKCP_TARGET "libdap-XKCP-${XKCP_SUFFIX}${TARGET_POSTFIX}.a")
set(XKCP_BUILD_DIR "${CELLFRAME_SDK_BUILD}/dap-sdk/crypto/XKCP/xkcp_build_src")
set(XKCP_BUILD_INCLUDES "${XKCP_BUILD_DIR}/bin/${XKCP_TARGET}.headers")

message(STATUS "Target architecture: ${TARGET_ARCH}")
message(STATUS "XKCP target: ${XKCP_TARGET}")
message(STATUS "XKCP headers: ${XKCP_BUILD_INCLUDES}")

# Include directories
include_directories(
    ${DAP_SDK_SRC}/core/include
    ${DAP_SDK_SRC}/crypto/include
    ${DAP_SDK_SRC}/crypto/include/liboqs
    ${DAP_SDK_SRC}/crypto/include/oqs
    ${DAP_SDK_SRC}/crypto/include/sig_newhope
    ${DAP_SDK_SRC}/crypto/include/sig_sphincs
    ${DAP_SDK_SRC}/crypto/include/sig_dilithium
    ${DAP_SDK_SRC}/crypto/include/sig_falcon
    ${DAP_SDK_SRC}/crypto/include/seed
    ${XKCP_BUILD_INCLUDES}
    ${DAP_SDK_SRC}/3rdparty/uthash/src
    ${CELLFRAME_SDK_BUILD}/dap-sdk/core/json-c
    ${DAP_SDK_SRC}/3rdparty/json-c
    ${CELLFRAME_SDK_SRC}/modules/common/include
    ${DAP_SDK_SRC}/net/stream/stream/include
    ${DAP_SDK_SRC}/net/stream/session/include
    ${DAP_SDK_SRC}/net/stream/ch/include
    ${DAP_SDK_SRC}/net/server/http_server/include
    ${DAP_SDK_SRC}/net/server/http_server/http_client/include
    ${DAP_SDK_SRC}/net/server/notify_server/include
    ${DAP_SDK_SRC}/net/server/enc_server/include
    ${DAP_SDK_SRC}/net/server/json_rpc/include
    ${DAP_SDK_SRC}/net/client/include
    ${DAP_SDK_SRC}/net/common/http/include
    ${DAP_SDK_SRC}/net/common/include
    ${DAP_SDK_SRC}/io/include
    ${DAP_SDK_SRC}/core/src
    ${DAP_SDK_SRC}/core/src/unix
    ${CELLFRAME_SDK_BUILD}/dap-sdk/core
)

# Add necessary definitions
add_definitions(-DDAP_OS_UNIX -DDAP_OS_LINUX)

# Link directories
link_directories(
    ${CELLFRAME_SDK_BUILD}/dap-sdk/crypto
    ${CELLFRAME_SDK_BUILD}/dap-sdk/core
    ${CELLFRAME_SDK_BUILD}/dap-sdk/core/json-c
    ${CELLFRAME_SDK_BUILD}/modules/common
    ${CELLFRAME_SDK_BUILD}/dap-sdk/net/stream/stream
    ${CELLFRAME_SDK_BUILD}/dap-sdk/net/stream/ch
    ${CELLFRAME_SDK_BUILD}/dap-sdk/net/stream/session
    ${CELLFRAME_SDK_BUILD}/dap-sdk/net/link_manager
    ${CELLFRAME_SDK_BUILD}/dap-sdk/net/server/http_server
    ${CELLFRAME_SDK_BUILD}/dap-sdk/net/server/enc_server
    ${CELLFRAME_SDK_BUILD}/dap-sdk/net/client
    ${CELLFRAME_SDK_BUILD}/dap-sdk/net/common/http
    ${CELLFRAME_SDK_BUILD}/dap-sdk/io
    ${CELLFRAME_SDK_BUILD}/dap-sdk/global-db
)

# Build cf-cert-generator - multi-node certificate batch generator
add_executable(cf-cert-generator cert-generator.c)

target_link_libraries(cf-cert-generator
    # Chain layer
    dap_chain_common
    # Network layer (order matters - dependencies first)
    dap_stream
    dap_stream_ch
    dap_session
    dap_link_manager
    dap_http_server
    dap_http_common
    dap_enc_server
    dap_client
    dap_global_db
    dap_io
    # Core crypto
    dap_crypto
    dap_core
    dap_json-c
    ${XKCP_BUILD_DIR}/bin/${XKCP_TARGET}
    ${CELLFRAME_SDK_BUILD}/dap-sdk/crypto/src/Kyber/crypto_kem/kyber512/optimized/libdap_crypto_kyber512.a
    # System libraries
    pthread
    m
)

# Build dap-cert - single certificate management utility
add_executable(dap-cert dap-cert.c)

target_link_libraries(dap-cert
    dap_chain_common
    dap_crypto
    dap_core
    dap_json-c
    ${XKCP_BUILD_DIR}/bin/${XKCP_TARGET}
    ${CELLFRAME_SDK_BUILD}/dap-sdk/crypto/src/Kyber/crypto_kem/kyber512/optimized/libdap_crypto_kyber512.a
    pthread
    m
)