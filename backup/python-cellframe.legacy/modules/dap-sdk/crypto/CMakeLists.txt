project(dap_crypto_python_module C)
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
    if (NOT (TARGET dap_crypto))
        add_subdirectory(libdap-crypto)
        target_compile_options(
            dap_crypto PRIVATE 
            "-fpic"
        )
    endif()
endif()

file(GLOB CRYPTO_PYTHON_SRCS src/*.c)
file(GLOB CRYPTO_PYTHON_HEADERS include/*.h)

include_directories(${PYTHON_INCLUDE_DIR} include/)

add_library(${PROJECT_NAME} STATIC ${CRYPTO_PYTHON_SRCS} ${CRYPTO_PYTHON_HEADERS})

target_link_libraries(${PROJECT_NAME})

target_link_libraries(${PROJECT_NAME}
        dap_core
        dap_crypto
        dap_chain_common_python_module
        dap_chain_net_python_module)

target_include_directories(${PROJECT_NAME} PUBLIC include/ )

if(BUILD_DAP_CRYPTO_PYTHON_TESTS)
    add_subdirectory(test)
    file(COPY ${CMAKE_CURRENT_SOURCE_DIR}/test/test_b58.py 
                    DESTINATION ${CMAKE_CURRENT_BINARY_DIR}/test/)
    file(COPY ${CMAKE_CURRENT_SOURCE_DIR}/test/test_b64.py
                    DESTINATION ${CMAKE_CURRENT_BINARY_DIR}/test/)
    file(COPY ${CMAKE_CURRENT_SOURCE_DIR}/test/test_iaes256_cbc.py
                    DESTINATION ${CMAKE_CURRENT_BINARY_DIR}/test/)
    file(COPY ${CMAKE_CURRENT_SOURCE_DIR}/test/test_iaes256_cbc.py
                    DESTINATION ${CMAKE_CURRENT_BINARY_DIR}/test/)
    file(COPY ${CMAKE_CURRENT_SOURCE_DIR}/test/test_oaes.py
                    DESTINATION ${CMAKE_CURRENT_BINARY_DIR}/test/)


endif()

