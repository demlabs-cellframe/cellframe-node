project(dap_chain_wallet_python_module C)
cmake_minimum_required(VERSION 3.10)

set(CMAKE_VERBOSE_MAKEFILE ON)
set(CMAKE_COLOR_MAKEFILE   ON)
set(CMAKE_C_STANDARD 11)
add_definitions("-fpic")
add_definitions("-DDAP_LOG_MT")

file(GLOB CHAIN_WALLET_PYTHON_SRCS src/*.c)
file(GLOB CHAIN_WALLET_PYTHON_HEADERS include/*.h)

include_directories(${PYTHON_INCLUDE_DIR} include/)

add_library(${PROJECT_NAME} STATIC ${CHAIN_WALLET_PYTHON_SRCS} ${CHAIN_WALLET_PYTHON_HEADERS})

target_link_libraries(${PROJECT_NAME})

target_link_libraries(${PROJECT_NAME} dap_core
                        dap_crypto
                        dap_crypto_python_module
                        dap_chain
                        dap_chain_python_module
                        dap_chain_net
                        dap_chain_wallet )

target_include_directories(${PROJECT_NAME} PUBLIC include/ )

