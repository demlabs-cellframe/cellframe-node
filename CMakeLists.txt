project(kelvin-node C)
cmake_minimum_required(VERSION 2.8)

set(CMAKE_VERBOSE_MAKEFILE ON)
set(CMAKE_COLOR_MAKEFILE   ON)
set (CMAKE_CXX_STANDARD 11)

add_definitions ("-DDAP_SERVER")

add_subdirectory(libdap-server)
add_subdirectory(libdap)
#add_subdirectory(libdap-chain)
add_subdirectory(libdap-stream)


include_directories("${INCLUDE_DIRECTORIES} ${dap_core_INCLUDE_DIRS}")
include_directories("${INCLUDE_DIRECTORIES} ${dap_http_INCLUDE_DIRS}")
include_directories("${INCLUDE_DIRECTORIES} ${dap_crypto_INCLUDE_DIRS}")
include_directories("${INCLUDE_DIRECTORIES} ${dap_enc_server_INCLUDE_DIRS}")
include_directories("${INCLUDE_DIRECTORIES} ${dap_http_server_INCLUDE_DIRS}")
include_directories("${INCLUDE_DIRECTORIES} ${dap_client_INCLUDE_DIRS}")
#include_directories("${INCLUDE_DIRECTORIES} ${dap-chain_INCLUDE_DIRS}")
include_directories("${INCLUDE_DIRECTORIES} ${dap_core_server_INCLUDE_DIRS}")
include_directories("${INCLUDE_DIRECTORIES} ${dap_udp_server_INCLUDE_DIRS}")
include_directories("${INCLUDE_DIRECTORIES} ${dap_session_INCLUDE_DIRS}")
include_directories("${INCLUDE_DIRECTORIES} ${dap_stream_INCLUDE_DIRS}")

add_definitions ("${dap_core_DEFINITIONS}")
add_definitions ("${dap_crypto_DEFINITIONS}")
add_definitions ("${dap_client_DEFINITIONS}")
add_definitions ("${dap_enc_server_DEFINITIONS}")
add_definitions ("${dap_http_server_DEFINITIONS}")
add_definitions ("${dap_http_DEFINITIONS}")
#add_definitions ("${dap-chain_DEFINITIONS}")
add_definitions ("${dap_core_server_DEFINITIONS}")
add_definitions ("${dap_udp_server_DEFINITIONS}")
add_definitions ("${dap_session_DEFINITIONS}")
add_definitions ("${dap_stream_DEFINITIONS}")

set(SOURCES sources/kelvin-node.c sources/node_manager.c )
set(HEADERS sources/node_manager.h)


set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} ")
add_executable(${PROJECT_NAME} "sources/kelvin-node.c" ${HEADERS} ${SOURCES} ${CRYPTO_SRCS})
target_link_libraries(${PROJECT_NAME} dap_http_server dap_core_server dap_udp_server dap_session dap_crypto  dap_client dap_core dap_http dap_enc_server dap_stream  m pthread)