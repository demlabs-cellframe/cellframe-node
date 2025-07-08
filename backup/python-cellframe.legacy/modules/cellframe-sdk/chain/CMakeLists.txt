project(dap_chain_python_module C)
cmake_minimum_required(VERSION 3.10)

set(CMAKE_VERBOSE_MAKEFILE ON)
set(CMAKE_COLOR_MAKEFILE   ON)
set(CMAKE_C_STANDARD 11)
add_definitions("-fpic")
add_definitions("-DDAP_LOG_MT")

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
   if (NOT (TARGET dap_chain))
       add_subdirectory(libdap-chain)
       target_compile_options(
            dap_chain PRIVATE
            "-fpic"
       )
   endif()
   if (NOT (TARGET dap_chain_crypto))
       add_subdirectory(libdap-chain-crypto)
       target_compile_options(
            dap_chain_crypto PRIVATE
            "-fpic"  
       )
   endif()
   if (NOT (TARGET dap_chain_mempool))
       add_subdirectory(libdap-chain-mempool)
       target_compile_options(
            dap_chain_mempool PRIVATE
            "-fpic"  
       )
   endif()
   if (NOT (TARGET dap_chain_net))
       add_subdirectory(libdap-chain-net)
       target_compile_options(
            dap_chain_net PRIVATE
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
   if (NOT (TARGET dap_global_db))
       add_subdirectory(libdap-chain-global-db)
       target_compile_options(
            dap_global_db PRIVATE
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
   if (NOT (TARGET dap_chain_ch))
       add_subdirectory(libdap-stream-ch-chain)
       target_compile_options(
            dap_chain_ch PRIVATE
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
   if (NOT (TARGET dap_chain_wallet))
       add_subdirectory(libdap-chain-wallet)
       target_compile_options(
            dap_chain_wallet PRIVATE
            "-fpic"   
       ) 
   endif()
   if (NOT (TARGET dap_chain_net_srv))
       add_subdirectory(libdap-chain-net-srv)
       target_compile_options(
            dap_chain_net_srv PRIVATE
            "-fpic"   
       ) 
   endif()
   if (NOT (TARGET dap_server_http_db_auth))
       add_subdirectory(libdap-server-http-db-auth)
       target_compile_options(
            dap_server_http_db_auth PRIVATE
            "-fpic"   
       ) 
   endif()
   if (NOT (TARGET dap_chain_gdb))
       add_subdirectory(libdap-chain-gdb)
       target_compile_options(
            dap_chain_gdb PRIVATE
            "-fpic"   
       ) 
   endif()
   if (NOT (TARGET dap_python_module))
       add_subdirectory(libdap-python)
       target_compile_options(
            dap_python_module PRIVATE
            "-fpic"
       )
   endif()
   if (NOT (TARGET dap_crypto_python_module))
       add_subdirectory(libdap-crypto-python)
       target_compile_options(
            dap_crypto_python_module PRIVATE
            "-fpic"
       )
   endif()
    if (NOT (TARGET dap_chain_net_srv_vpn))
        add_subdirectory(libdap-chain-net-srv-vpn)
        target_compile_options(
             dap_chain_net_srv_vpn PRIVATE
             "-fpic"
        )
    endif()
    if (NOT (TARGET dap_server_http_db))
        add_subdirectory(libdap-server-http-db)
        target_compile_options(
             dap_server_http_db PRIVATE
             "-fpic"
        )
    endif()
    if (NOT (TARGET dap_chain_common_python_module))
       add_subdirectory(libdap-chain-common-python)
       target_compile_options(
            dap_chain_common_python_module PRIVATE
            "-fpic"
       )
    endif()
endif()
#add_definitions("-DDAP_APP_NAME=\"TestPRJ\" -DSYSTEM_CONFIGS_DIR=\"${CMAKE_CURRENT_BINARY_DIR}\"")

file(GLOB CHAIN_PYTHON_SRCS src/*.c)
file(GLOB CHAIN_PYTHON_HEADERS include/*.h)

include_directories(${PYTHON_INCLUDE_DIR} include/)

add_library(${PROJECT_NAME} STATIC ${CHAIN_PYTHON_SRCS} ${CHAIN_PYTHON_HEADERS})

target_link_libraries(${PROJECT_NAME})

target_link_libraries(${PROJECT_NAME} dap_core
        dap_crypto
        dap_chain
        dap_io
        dap_chain_net
        dap_crypto_python_module
        dap_python_module
        dap_chain_common_python_module
        dap_chain_cs_dag_python_module)

target_include_directories(${PROJECT_NAME} PUBLIC include/ )

