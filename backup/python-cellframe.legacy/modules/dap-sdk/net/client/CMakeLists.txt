project(dap_client_python_module C)
cmake_minimum_required(VERSION 3.10)

set(CMAKE_VERBOSE_MAKEFILE ON)
set(CMAKE_COLOR_MAKEFILE   ON)
set(CMAKE_C_STANDARD 11)
add_definitions("-fpic")

if(UNIX)
    add_definitions("-DDAP_OS_UNIX")
endif()

if (NOT (${SUBMODULES_NO_BUILD} MATCHES ON))
    set (SUBMODULES_NO_BUILD ON)
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
   if (NOT (TARGET dap_io))
       add_subdirectory(libdap-server-core)
       target_compile_options(
            dap_io PRIVATE
            "-fpic"
       )
   endif()
   if (NOT (TARGET libdap-server))
       add_subdirectory(libdap-server)
#       target_compile_options(
#            libdap-server PRIVATE
#            "-fpic"
#       )
   endif()
   if (NOT (TARGET dap_stream))
       add_subdirectory(libdap-stream)
       target_compile_options(
            dap_stream PRIVATE
            "-fpic"
       )
   endif()
   if (NOT (TARGET dap_stream_ch))
       add_subdirectory(libdap-stream-ch)
       target_compile_options(
            dap_stream_ch PRIVATE
             "-fpic"
       )
   endif()
   if (NOT (TARGET dap_udp_server))
       add_subdirectory(libdap-server-udp)
       target_compile_options(
            dap_udp_server PRIVATE
            "-fpic"
       )
   endif()
   if (NOT (TARGET dap_client))
       add_subdirectory(libdap-client)
       target_compile_options(
            dap_client PRIVATE
            "-fpic"
       )
   endif()
endif()
#add_definitions("-DDAP_APP_NAME=\"TestPRJ\" -DSYSTEM_CONFIGS_DIR=\"${CMAKE_CURRENT_BINARY_DIR}\"")

file(GLOB CLIENT_PYTHON_SRCS src/*.c)
file(GLOB CLIENT_PYTHON_HEADERS include/*.h)

include_directories(${PYTHON_INCLUDE_DIR} include/)

add_library(${PROJECT_NAME} STATIC ${CLIENT_PYTHON_SRCS} ${CLIENT_PYTHON_HEADERS})

target_link_libraries(${PROJECT_NAME})

target_link_libraries(${PROJECT_NAME} dap_core dap_crypto dap_client dap_python_module)

target_include_directories(${PROJECT_NAME} PUBLIC include/ )

