project(kelvin-node C)
cmake_minimum_required(VERSION 2.8)

set(CMAKE_VERBOSE_MAKEFILE ON)
set(CMAKE_COLOR_MAKEFILE   ON)
set (CMAKE_CXX_STANDARD 11)

SET (CMAKE_INSTALL_PREFIX "/opt/${PROJECT_NAME}")
SET (CPACK_INSTALL_PREFIX "/opt/${PROJECT_NAME}")
SET (DESTDIR "/opt/${PROJECT_NAME}")

SET( CPACK_GENERATOR "DEB")
SET( CPACK_PACKAGE_NAME  "${PROJECT_NAME}")
SET( CPACK_PACKAGE_VERSION_MAJOR 0)
SET( CPACK_PACKAGE_VERSION_MINOR 1)
SET( CPACK_PACKAGE_VERSION_PATCH 1)

SET( CPACK_SYSTEM_NAME "debian-9.5-amd64")

SET( CPACK_DEBIAN_PACKAGE_MAINTAINER "Dmitriy Gerasimov  <naeper@ldemlabs.net>" )
SET( CPACK_DEBIAN_PACKAGE_DESCRIPTION_SUMMARY "Kelvin Blockchain Node software" )
SET( CPACK_DEBIAN_PACKAGE_DESCRIPTION 	"DAP server" )
SET( CPACK_DEBIAN_PACKAGE_SECTION "extra")
SET( CPACK_DEBIAN_PACKAGE_ARCHITECTURE "amd64" )
SET( CPACK_DEBIAN_PACKAGE_DEPENDS "debconf (>=1.5), dpkg (>=1.17), bash (>=4)")
SET( CPACK_DEBIAN_PACKAGE_SHLIBDEPS ON)
SET( CPACK_DEBIAN_PACKAGE_CONTROL_EXTRA
    "${CMAKE_CURRENT_SOURCE_DIR}/../debian/postinst;${CMAKE_CURRENT_SOURCE_DIR}/../debian/postrm;${CMAKE_CURRENT_SOURCE_DIR}/../debian/templates;${CMAKE_CURRENT_SOURCE_DIR}/../debian/config;")


set(CMAKE_VERBOSE_MAKEFILE ON)
set(CMAKE_COLOR_MAKEFILE   ON)
set(CMAKE_C_STANDARD 11)
set(SUBMODULES_NO_BUILD ON)


add_definitions ("-DDAP_SERVER")
add_definitions ("-DNODE_NETNAME=\"kelvin\"")

add_subdirectory(libdap)
add_subdirectory(libdap-server-core)
add_subdirectory(libdap-server-udp)
add_subdirectory(libdap-server)

add_subdirectory(libdap-chain)
add_subdirectory(libdap-chain-crypto)
add_subdirectory(libdap-chain-wallet)
add_subdirectory(libdap-chain-block)
add_subdirectory(libdap-chain-block-cs)
add_subdirectory(libdap-chain-block-cs-poa)
add_subdirectory(libdap-chain-dag)
add_subdirectory(libdap-chain-dag-cs)
add_subdirectory(libdap-chain-dag-cs-poa)
add_subdirectory(libdap-chain-dag-cs-hashgraph)
add_subdirectory(libdap-chain-dag-cs-poh)
add_subdirectory(libdap-chain-net)
add_subdirectory(libdap-chain-net-srv)
add_subdirectory(libdap-chain-net-srv-app)
add_subdirectory(libdap-chain-net-srv-app-db)
add_subdirectory(libdap-chain-net-srv-datum)
add_subdirectory(libdap-chain-net-srv-datum-pool)
add_subdirectory(libdap-chain-net-srv-vpn)
add_subdirectory(libdap-chain-mempool)

add_subdirectory(libdap-stream)
add_subdirectory(libdap-stream-ch)
add_subdirectory(libdap-client)

add_subdirectory(libdap-stream-ch-vpn)
add_subdirectory(libdap-stream-ch-chain)
add_subdirectory(libdap-stream-ch-chain-net)
add_subdirectory(libdap-stream-ch-chain-net-srv)
add_subdirectory(libdap-chain-global-db)
#add_subdirectory(libdap-stream-ch-chat)

if(BUILD_KELVIN_NODE_TESTS)
    enable_testing()
    add_subdirectory(test)
endif()

include_directories("${INCLUDE_DIRECTORIES} ${monero_crypto_INCLUDE_DIRS}")
include_directories("${INCLUDE_DIRECTORIES} ${dap_core_INCLUDE_DIRS}")
include_directories("${INCLUDE_DIRECTORIES} ${dap_core_unix_INCLUDE_DIRS}")
include_directories("${INCLUDE_DIRECTORIES} ${dap_http_INCLUDE_DIRS}")
include_directories("${INCLUDE_DIRECTORIES} ${dap_crypto_INCLUDE_DIRS}")
include_directories("${INCLUDE_DIRECTORIES} ${dap_enc_server_INCLUDE_DIRS}")
include_directories("${INCLUDE_DIRECTORIES} ${dap_http_server_INCLUDE_DIRS}")
include_directories("${INCLUDE_DIRECTORIES} ${dap_core_server_INCLUDE_DIRS}")
include_directories("${INCLUDE_DIRECTORIES} ${dap_server_INCLUDE_DIRS}")
include_directories("${INCLUDE_DIRECTORIES} ${dap_client_INCLUDE_DIRS}")
include_directories("${INCLUDE_DIRECTORIES} ${dap_stream_INCLUDE_DIRS}")
include_directories("${INCLUDE_DIRECTORIES} ${dap_stream_ch_INCLUDE_DIRS}")
include_directories("${INCLUDE_DIRECTORIES} ${dap_stream_ch_chain_INCLUDE_DIRS}")
include_directories("${INCLUDE_DIRECTORIES} ${dap_stream_ch_chain_net_INCLUDE_DIRS}")
include_directories("${INCLUDE_DIRECTORIES} ${dap_stream_ch_chain_net_srv_INCLUDE_DIRS}")
include_directories("${INCLUDE_DIRECTORIES} ${dap_stream_ch_vpn_INCLUDE_DIRS}")
include_directories("${INCLUDE_DIRECTORIES} ${dap_udp_server_INCLUDE_DIRS}")
include_directories("${INCLUDE_DIRECTORIES} ${dap_session_INCLUDE_DIRS}")
include_directories("${INCLUDE_DIRECTORIES} ${dap_chain_INCLUDE_DIRS}")
include_directories("${INCLUDE_DIRECTORIES} ${dap_chain_block_INCLUDE_DIRS}")
include_directories("${INCLUDE_DIRECTORIES} ${dap_chain_block_cs_INCLUDE_DIRS}")
include_directories("${INCLUDE_DIRECTORIES} ${dap_chain_block_cs_poa_INCLUDE_DIRS}")
include_directories("${INCLUDE_DIRECTORIES} ${dap_chain_crypto_INCLUDE_DIRS}")
include_directories("${INCLUDE_DIRECTORIES} ${dap_chain_dag_INCLUDE_DIRS}")
include_directories("${INCLUDE_DIRECTORIES} ${dap_chain_dag_cs_INCLUDE_DIRS}")
include_directories("${INCLUDE_DIRECTORIES} ${dap_chain_dag_cs_hashgraph_INCLUDE_DIRS}")
include_directories("${INCLUDE_DIRECTORIES} ${dap_chain_dag_cs_poa_INCLUDE_DIRS}")
include_directories("${INCLUDE_DIRECTORIES} ${dap_chain_dag_cs_poh_INCLUDE_DIRS}")
include_directories("${INCLUDE_DIRECTORIES} ${dap_chain_net_INCLUDE_DIRS}")
include_directories("${INCLUDE_DIRECTORIES} ${dap_chain_net_srv_INCLUDE_DIRS}")
include_directories("${INCLUDE_DIRECTORIES} ${dap_chain_net_srv_app_INCLUDE_DIRS}")
include_directories("${INCLUDE_DIRECTORIES} ${dap_chain_net_srv_app_db_INCLUDE_DIRS}")
include_directories("${INCLUDE_DIRECTORIES} ${dap_chain_net_srv_datum_INCLUDE_DIRS}")
include_directories("${INCLUDE_DIRECTORIES} ${dap_chain_net_srv_datum_pool_INCLUDE_DIRS}")
include_directories("${INCLUDE_DIRECTORIES} ${dap_chain_net_srv_vpn_INCLUDE_DIRS}")
include_directories("${INCLUDE_DIRECTORIES} ${dap_chain_wallet_INCLUDE_DIRS}")
include_directories("${INCLUDE_DIRECTORIES} ${dap_chain_global_db_INCLUDE_DIRS}")
include_directories("${INCLUDE_DIRECTORIES} ${dap_chain_mempool_INCLUDE_DIRS}")

add_definitions ("${monero_crypto_DEFINITIONS}")
add_definitions(" ${dap_core_DEFINITIONS}")
add_definitions(" ${dap_core_unix_DEFINITIONS}")
add_definitions(" ${dap_http_DEFINITIONS}")
add_definitions(" ${dap_crypto_DEFINITIONS}")
add_definitions(" ${dap_enc_server_DEFINITIONS}")
add_definitions(" ${dap_http_server_DEFINITIONS}")
add_definitions(" ${dap_core_server_DEFINITIONS}")
add_definitions(" ${dap_server_DEFINITIONS}")
add_definitions(" ${dap_client_DEFINITIONS}")
add_definitions(" ${dap_stream_DEFINITIONS}")
add_definitions(" ${dap_stream_ch_DEFINITIONS}")
add_definitions(" ${dap_stream_ch_chain_DEFINITIONS}")
add_definitions(" ${dap_stream_ch_chain_net_DEFINITIONS}")
add_definitions(" ${dap_stream_ch_chain_net_srv_DEFINITIONS}")
add_definitions(" ${dap_stream_ch_vpn_DEFINITIONS}")
add_definitions(" ${dap_udp_server_DEFINITIONS}")
add_definitions(" ${dap_session_DEFINITIONS}")
add_definitions(" ${dap_chain_DEFINITIONS}")
add_definitions(" ${dap_chain_block_DEFINITIONS}")
add_definitions(" ${dap_chain_block_cs_DEFINITIONS}")
add_definitions(" ${dap_chain_block_cs_poa_DEFINITIONS}")
add_definitions(" ${dap_chain_crypto_DEFINITIONS}")
add_definitions(" ${dap_chain_dag_DEFINITIONS}")
add_definitions(" ${dap_chain_dag_cs_DEFINITIONS}")
add_definitions(" ${dap_chain_dag_cs_hashgraph_DEFINITIONS}")
add_definitions(" ${dap_chain_dag_cs_poa_DEFINITIONS}")
add_definitions(" ${dap_chain_dag_cs_poh_DEFINITIONS}")
add_definitions(" ${dap_chain_net_DEFINITIONS}")
add_definitions(" ${dap_chain_net_srv_DEFINITIONS}")
add_definitions(" ${dap_chain_net_srv_app_DEFINITIONS}")
add_definitions(" ${dap_chain_net_srv_app_db_DEFINITIONS}")
add_definitions(" ${dap_chain_net_srv_datum_DEFINITIONS}")
add_definitions(" ${dap_chain_net_srv_datum_pool_DEFINITIONS}")
add_definitions(" ${dap_chain_net_srv_vpn_DEFINITIONS}")
add_definitions(" ${dap_chain_wallet_DEFINITIONS}")
add_definitions(" ${dap_chain_global_db_DEFINITIONS}")
add_definitions(" ${dap_chain_mempool_DEFINITIONS}")


#file(GLOB SERVER_SRCS *.c)

set(SOURCES sources/main.c )


if(UNIX)
    add_definitions ("-DDAP_OS_LINUX")
endif()

set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} ")
add_executable(${PROJECT_NAME} "sources/main.c" "sources/sig_unix_handler.c" ${HEADERS} ${SOURCES} )
add_executable(${PROJECT_NAME}-cli "sources/main_node_cli.c" "sources/main_node_cli_shell.c" "sources/main_node_cli_net.c" )
add_executable(${PROJECT_NAME}-tool "sources/main_node_tool.c" )

target_link_libraries(${PROJECT_NAME} dap_core dap_crypto dap_core_server dap_enc_server  dap_udp_server dap_session
    dap_enc_server dap_stream dap_stream_ch_vpn dap_stream_ch_chain dap_stream_ch_chain_net
    dap_stream_ch_chain_net_srv dap_chain dap_chain_crypto dap_client
    dap_chain_block dap_chain_block_cs dap_chain_block_cs_poa
    dap_chain_dag dap_chain_dag_cs dap_chain_dag_cs_poa dap_chain_dag_cs_hashgraph dap_chain_dag_cs_poh
    dap_chain_net dap_chain_net_srv dap_chain_net_srv_app dap_chain_net_srv_app_db
    dap_chain_net_srv_datum dap_chain_net_srv_datum_pool dap_chain_net_srv_vpn
    dap_chain_wallet dap_chain_global_db  dap_chain_mempool m pthread magic )
target_link_libraries(${PROJECT_NAME}-cli m dap_chain_net curl) 
target_link_libraries(${PROJECT_NAME}-tool dap_core dap_crypto dap_core_server dap_enc_server  dap_udp_server dap_session
    dap_enc_server dap_stream dap_stream_ch_vpn dap_stream_ch_chain dap_stream_ch_chain_net
    dap_stream_ch_chain_net_srv dap_chain dap_chain_crypto dap_client
    dap_chain_block dap_chain_block_cs dap_chain_block_cs_poa
    dap_chain_dag dap_chain_dag_cs dap_chain_dag_cs_poa dap_chain_dag_cs_hashgraph dap_chain_dag_cs_poh
    dap_chain_net dap_chain_net_srv dap_chain_net_srv_app dap_chain_net_srv_app_db
    dap_chain_net_srv_datum dap_chain_net_srv_datum_pool dap_chain_net_srv_vpn
    dap_chain_wallet dap_chain_global_db dap_chain_mempool m pthread magic )

target_include_directories(${PROJECT_NAME} INTERFACE .)
target_include_directories(${PROJECT_NAME}-cli INTERFACE .)
target_include_directories(${PROJECT_NAME}-tool INTERFACE .)

INSTALL(DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/../dist/ DESTINATION ${CMAKE_INSTALL_PREFIX} FILES_MATCHING PATTERN "*"  PATTERN "*")
INSTALL(TARGETS ${PROJECT_NAME} DESTINATION ${CMAKE_INSTALL_PREFIX}/bin )
INSTALL(TARGETS ${PROJECT_NAME}-cli DESTINATION ${CMAKE_INSTALL_PREFIX}/bin )
INSTALL(TARGETS ${PROJECT_NAME}-tool DESTINATION ${CMAKE_INSTALL_PREFIX}/bin )
INSTALL(DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/../scripts/ DESTINATION ${CMAKE_INSTALL_PREFIX}/bin FILES_MATCHING PATTERN "*"  PATTERN "*" PERMISSIONS OWNER_EXECUTE;OWNER_READ;OWNER_WRITE;WORLD_READ;GROUP_READ )
INCLUDE(CPack)
