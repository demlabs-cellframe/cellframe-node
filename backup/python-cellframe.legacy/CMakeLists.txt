cmake_minimum_required(VERSION 3.10)

project(CellFrame C)

set(CMAKE_VERBOSE_MAKEFILE ON)
set(CMAKE_COLOR_MAKEFILE   ON)
set(CMAKE_C_STANDARD 11)


#set(Python_ADDITIONAL_VERSIONS 3.9 3.8 3.7 3.6 3.5 3.4)
#find_package (PythonLibs REQUIRED)

file(GLOB PYTHON_CELLFRAME_SRCS CellFrame/*.c)
file(GLOB PYTHON_CELLFRAME_HEADERS include/*.h)

set(SUBMODULES_NO_BUILD ON)

if (SUPPORT_PYTHON_PLUGINS)
    file (GLOB APP_CONTEXT_HEADER
        modules/plugins/include/dap_plugins_python_app_context.h)

    add_definitions("-fpic")
     
    add_definitions("-DDAP_SUPPORT_PYTHON_PLUGINS")
    add_library(${PROJECT_NAME} STATIC ${PYTHON_CELLFRAME_SRCS} ${APP_CONTEXT_HEADER} ${PYTHON_CELLFRAME_HEADERS})
    target_include_directories(${PROJECT_NAME} INTERFACE include/)
    
    include_directories(${PYTHON_INCLUDE_DIR})
else()

    SET( CPACK_GENERATOR "DEB")
    SET( CPACK_PACKAGE_NAME  "${PROJECT_NAME}")
    SET( CPACK_PACKAGE_VERSION_MAJOR 3)
    SET( CPACK_PACKAGE_VERSION_MINOR 0)
    SET( CPACK_PACKAGE_VERSION_PATCH 0)

    add_definitions("-DDAP_VERSION_MAJOR=\"${CPACK_PACKAGE_VERSION_MAJOR}\"")
    add_definitions("-DDAP_VERSION_MINOR=\"${CPACK_PACKAGE_VERSION_MINOR}\"")
    add_definitions("-DDAP_VERSION_PATCH=\"${CPACK_PACKAGE_VERSION_PATCH}\"")
    add_definitions("-DDAP_VERSION=\"${CPACK_PACKAGE_VERSION_MAJOR}.${CPACK_PACKAGE_VERSION_MINOR}-${CPACK_PACKAGE_VERSION_PATCH}\"")
    set(SUBMODULES_NO_BUILD ON)


    #if (SKBUILD)
    message(STATUS "Make python extension")
    #find_package(PythonExtensions REQUIRED)
    add_library(CellFrame MODULE ${PYTHON_CELLFRAME_SRCS} ${PYTHON_CELLFRAME_HEADERS})
    add_library(python_static STATIC IMPORTED GLOBAL)
    target_include_directories(CellFrame INTERFACE include/)

    install(TARGETS ${PROJECT_NAME} LIBRARY DESTINATION ${PROJECT_NAME})
    install(FILES CellFrame/__init__.py DESTINATION ${PROJECT_NAME})
    install(FILES CellFrame/PublicNetworks/* DESTINATION ${PROJECT_NAME})

endif()


if (NOT (SUPPORT_PYTHON_PLUGINS))
    set(CELLFRAME_MODULES "core chains network cs-none srv")
    include(dap-sdk/cmake/OS_Detection.cmake)
    add_subdirectory(dap-sdk)
    add_subdirectory(cellframe-sdk)
else()
    add_subdirectory(modules/plugins)
    target_compile_options(dap_plugins_python PRIVATE "-fpic")
endif()

include_directories(${CMAKE_CURRENT_SOURCE_DIR}/include)

add_subdirectory(modules/dap-sdk/core)
add_subdirectory(modules/dap-sdk/crypto)
add_subdirectory(modules/dap-sdk/io)
add_subdirectory(modules/dap-sdk/net/client)
add_subdirectory(modules/dap-sdk/net/server/enc)
add_subdirectory(modules/dap-sdk/net/server/http)
add_subdirectory(modules/dap-sdk/net/server/json_rpc)
add_subdirectory(modules/dap-sdk/net/stream/stream)
add_subdirectory(modules/dap-sdk/global-db)
add_subdirectory(modules/cellframe-sdk/common)
add_subdirectory(modules/cellframe-sdk/mempool)
add_subdirectory(modules/cellframe-sdk/net)
add_subdirectory(modules/cellframe-sdk/net/srv)
add_subdirectory(modules/cellframe-sdk/chain)
add_subdirectory(modules/cellframe-sdk/app-cli)
add_subdirectory(modules/cellframe-sdk/wallet)
add_subdirectory(modules/cellframe-sdk/type/dag)
add_subdirectory(modules/cellframe-sdk/type/blocks)
add_subdirectory(modules/cellframe-sdk/consensus/dag_poa)
add_subdirectory(modules/cellframe-sdk/services/pos_delegate)
add_subdirectory(modules/cellframe-sdk/services/xchange)
add_subdirectory(modules/cellframe-sdk/services/vote)
add_subdirectory(modules/cellframe-sdk/channel/chain-net)

    target_compile_options(dap_chain_common_python_module PRIVATE "-fpic")
    target_compile_options(dap_python_module PRIVATE "-fpic" )
    target_compile_options(dap_crypto_python_module PRIVATE "-fpic" )
    target_compile_options(dap_chain_net_python_module PRIVATE "-fpic")
    target_compile_options(dap_chain_net_srv_python_module PRIVATE "-fpic")
    target_compile_options(dap_chain_python_module PRIVATE "-fpic")
    target_compile_options(dap_app_cli_python_module PRIVATE "-fpic")
    target_compile_options(dap_client_python_module PRIVATE "-fpic")
    target_compile_options(dap_chain_wallet_python_module PRIVATE "-fpic")


target_compile_options(dap_core PRIVATE "-fpic")
if (NOT WIN32)
    target_compile_options(dap_core_unix PRIVATE "-fpic")
endif()
target_compile_options(dap_app_cli PRIVATE "-fpic")
target_compile_options(dap_crypto PRIVATE "-fpic")
target_compile_options(dap_chain PRIVATE "-fpic")
target_compile_options(dap_chain_wallet PRIVATE "-fpic" )
target_compile_options(dap_chain_net PRIVATE "-fpic" )
target_compile_options(dap_io PRIVATE "-fpic" )
target_compile_options(dap_global_db PRIVATE "-fpic" )
target_compile_options(dap_client PRIVATE "-fpic" )
target_compile_options(dap_stream PRIVATE "-fpic" )
target_compile_options(dap_stream_ch PRIVATE "-fpic" )
target_compile_options(dap_enc_server PRIVATE "-fpic")
target_compile_options(dap_http_server PRIVATE "-fpic")
target_compile_options(dap_session PRIVATE "-fpic")
target_compile_options(dap_core PRIVATE "-fpic")
target_compile_options(dap_app_cli PRIVATE "-fpic")
target_compile_options(dap_crypto PRIVATE "-fpic")
target_compile_options(dap_chain PRIVATE "-fpic")
target_compile_options(dap_chain_wallet PRIVATE "-fpic" )
target_compile_options(dap_chain_net PRIVATE "-fpic" )
target_compile_options(dap_io PRIVATE "-fpic" )
target_compile_options(dap_global_db PRIVATE "-fpic" )
target_compile_options(dap_client PRIVATE "-fpic" )
target_compile_options(dap_stream PRIVATE "-fpic" )
target_compile_options(dap_stream_ch PRIVATE "-fpic" )
target_compile_options(dap_enc_server PRIVATE "-fpic")
target_compile_options(dap_http_server PRIVATE "-fpic")
target_compile_options(dap_session PRIVATE "-fpic")
target_compile_options(dap_io_python_module PRIVATE "-fpic")


if (WIN32)
    set_target_properties(${PROJECT_NAME} PROPERTIES SUFFIX ".pyd")
endif()


target_link_libraries(${PROJECT_NAME} cellframe-sdk dap_python_module
                      dap_crypto_python_module
                      dap_io_python_module
                      dap_enc_server_python_module
                      dap_server_http_python_module
                      dap_stream_python_module
                      dap_chain_python_module
                      dap_chain_net_python_module
                      dap_chain_net_srv_python_module
                      dap_mempool_python_module
                      dap_app_cli_python_module
                      dap_chain_wallet_python_module
                      dap_server_json_rpc_python_module
                      dap_chain_cs_dag_poa_python_module
                      dap_chain_cs_blocks_python_module
                      dap_global_db_python_module
                      dap_chain_net_srv_stake_pos_delegate_python_module
                      wrapping_dap_chain_net_srv_xchange
                      dap_chain_net_srv_vote_python
                      dap_chain_net_ch_python_module
                      ${PYTHON_LIBRARIES}
                     )

