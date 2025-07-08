cmake_minimum_required(VERSION 3.10)
project (dap_chain_net_srv_stake_pos_delegate_python_module C)

set(CMAKE_VERBOSE_MAKEFILE ON)
set(CMAKE_COLOR_MAKEFILE   ON)
set(CMAKE_C_STANDARD 11)
add_definitions("-fpic")
add_definitions("-DDAP_LOG_MT")

file (GLOB DAP_SRV_STAKE_POS_DELEGATE_PYTHON_SRCS src/*.c)
file (GLOB DAP_SRV_STAKE_POS_DELEGATE_PYTHON_HEADERS include/*.h)

include_directories(${PYTHON_INCLUDE_DIR} include/)

add_library(${PROJECT_NAME} STATIC ${DAP_SRV_STAKE_POS_DELEGATE_PYTHON_SRCS} ${DAP_SRV_STAKE_POS_DELEGATE_PYTHON_HEADERS})

target_link_libraries(${PROJECT_NAME} dap_chain_python_module)

target_include_directories(${PROJECT_NAME} PUBLIC include/)
