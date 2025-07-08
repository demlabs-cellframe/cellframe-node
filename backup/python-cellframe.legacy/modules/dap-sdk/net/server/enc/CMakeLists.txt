project(dap_enc_server_python_module C)
cmake_minimum_required(VERSION 3.10)

set(CMAKE_VERBOSE_MAKEFILE ON)
set(CMAKE_COLOR_MAKEFILE   ON)
set(CMAKE_C_STANDARD 11)
add_definitions("-fpic")

if(NOT (${SUBMODULES_NO_BUILD} MATCHES ON))
    if (NOT (TARGET dap_core))
        add_subdirectory(libdap)
        target_compile_options(
            dap_core PRIVATE 
            "-fpic"
        )
    endif()
endif()

file(GLOB ENC_SERVER_SRCS src/*.c)
file(GLOB ENC_SERVER_HEADERS include/*.h)

include_directories(${PYTHON_INCLUDE_DIR} include/ )

add_library(${PROJECT_NAME} STATIC ${ENC_SERVER_SRCS} ${ENC_SERVER_HEADERS})

target_link_libraries(${PROJECT_NAME} ${PYTHON_LIBRARIES})

target_compile_options(
    dap_core PRIVATE
    "-fpic"
)

target_link_libraries(${PROJECT_NAME} dap_core dap_http_server dap_enc_server dap_io_python_module dap_server_http_python_module ${PYTHON_LIBRARIES})

target_include_directories(${PROJECT_NAME} PUBLIC include/ )

#if(BUILD_DAP_PYTHON_TESTS)
#    add_subdirectory(test)
#    file(COPY ${CMAKE_CURRENT_SOURCE_DIR}/test/main_test.py
#                DESTINATION ${CMAKE_CURRENT_BINARY_DIR}/test/)
#endif()

