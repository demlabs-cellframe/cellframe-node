cmake_minimum_required(VERSION 3.10)
project(dap_plugins_python C)

set(CMAKE_VERBOSE_MAKEFILE ON)
set(CMAKE_COLOR_MAKEFILE   ON)
set(CMAKE_C_STANDARD 11)
add_definitions("-fpic")
add_definitions("-DDAP_LOG_MT")
#add_subdirectory(python-cellframe)
#target_compile_options(API_CellFrame PRIVATE "-fpic")

if(UNIX)
    add_definitions("-DDAP_OS_UNIX")
endif()

file(GLOB DAP_PLUGINS_PYTHON_SRCS src/*.c)
file(GLOB DAP_PLUGINS_PYTHON_HEADERS include/*.h)

include_directories(${PYTHON_INCLUDE_DIR} include/)

add_library(${PROJECT_NAME} STATIC ${DAP_PLUGINS_PYTHON_SRCS} ${DAP_PLUGINS_PYTHON_HEADERS})

target_link_libraries(${PROJECT_NAME})

target_link_libraries(${PROJECT_NAME} dap_core CellFrame)

target_include_directories(${PROJECT_NAME} PUBLIC include/ )

