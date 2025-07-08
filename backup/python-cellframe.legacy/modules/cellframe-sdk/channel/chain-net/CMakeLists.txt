cmake_minimum_required(VERSION 3.10)
project (dap_chain_net_ch_python_module C)

set(CMAKE_VERBOSE_MAKEFILE ON)
set(CMAKE_COLOR_MAKEFILE   ON)
set(CMAKE_C_STANDARD 11)
add_definitions("-fpic")
add_definitions("-DDAP_LOG_MT")

file (GLOB DAP_STREAM_CH_CHAIN_NET_PYTHON_SRCS src/*.c)
file (GLOB DAP_STREAM_CH_CHAIN_NET_PYTHON_HEADERS include/*.h)

include_directories(${PYTHON_INCLUDE_DIR} include/)

add_library(${PROJECT_NAME} STATIC ${DAP_STREAM_CH_CHAIN_NET_PYTHON_SRCS} ${DAP_STREAM_CH_CHAIN_NET_PYTHON_HEADERS})

target_link_libraries(${PROJECT_NAME} dap_chain_python_module dap_chain_net)

target_include_directories(${PROJECT_NAME} PUBLIC include/)
