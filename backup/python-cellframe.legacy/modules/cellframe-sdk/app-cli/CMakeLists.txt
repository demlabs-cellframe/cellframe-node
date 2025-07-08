project(dap_app_cli_python_module C)
cmake_minimum_required(VERSION 3.10)

set(CMAKE_VERBOSE_MAKEFILE ON)
set(CMAKE_COLOR_MAKEFILE   ON)
set(CMAKE_C_STANDARD 11)
#set(SUBMODULES_NO_BUILD ON)
add_definitions("-fpic")
add_definitions("-DDAP_LOG_MT")

if(NOT (${SUBMODULES_NO_BUILD} MATCHES ON))
    if (NOT (TARGET dap_core))
        add_subdirectory(libdap)
        target_compile_options(
            dap_core PRIVATE
            "-fpic"
        )
    endif()
endif()

file(GLOB APP_CLI_PYTHON_SRCS src/*.c)
file(GLOB APP_CLI_PYTHON_HEADERS include/*.h)

include_directories(${PYTHON_INCLUDE_DIR} include/)

add_library(${PROJECT_NAME} STATIC ${APP_CLI_PYTHON_SRCS} ${APP_CLI_PYTHON_HEADERS})

target_link_libraries(${PROJECT_NAME})

target_link_libraries(${PROJECT_NAME} dap_core dap_app_cli dap_python_module)

target_include_directories(${PROJECT_NAME} PUBLIC include/ )

