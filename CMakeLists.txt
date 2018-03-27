project(kelvin-node C)
cmake_minimum_required(VERSION 2.8)

set(CMAKE_VERBOSE_MAKEFILE ON)
set(CMAKE_COLOR_MAKEFILE   ON)
set (CMAKE_CXX_STANDARD 11)

add_subdirectory(libdap)
add_subdirectory(libdap-chain)
#add_subdirectory(libdap-server)
#add_subdirectory(libdap-stream)

include_directories("${INCLUDE_DIRECTORIES} ${dap_core_INCLUDE_DIRS}")
include_directories("${INCLUDE_DIRECTORIES} ${dap-chain_INCLUDE_DIRS}")
#include_directories("${INCLUDE_DIRECTORIES} ${dap-server_INCLUDE_DIRS}")
#include_directories("${INCLUDE_DIRECTORIES} ${dap-stream_INCLUDE_DIRS}")
add_definitions ("${dap_core_DEFINITIONS}")
add_definitions ("${dap-chain_DEFINITIONS}")
#add_definitions ("${dap-server_DEFINITIONS}")
#add_definitions ("${dap-stream_DEFINITIONS}")


set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} ")
add_executable(${PROJECT_NAME} "sources/kelvin-node.c" )
target_link_libraries(${PROJECT_NAME} dap_core dap-chain m pthread)
