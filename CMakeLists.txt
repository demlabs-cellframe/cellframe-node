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



add_definitions ("-DDAP_SERVER")
add_definitions ("-DNODE_NETNAME=\"kelvin\"")


add_subdirectory(libdap)
add_subdirectory(libdap-server-core)
add_subdirectory(libdap-server)
add_subdirectory(libdap-chain)
add_subdirectory(libdap-chain-crypto)
add_subdirectory(libdap-chain-wallet)
add_subdirectory(libdap-chain-mine)
add_subdirectory(libdap-chain-block)
add_subdirectory(libdap-chain-block-cs)
add_subdirectory(libdap-chain-block-cs-poa)
add_subdirectory(libdap-chain-block-cs-pow)
add_subdirectory(libdap-chain-dag)
add_subdirectory(libdap-chain-dag-cs)
add_subdirectory(libdap-chain-dag-cs-poa)
add_subdirectory(libdap-chain-dag-cs-hashgraph)
add_subdirectory(libdap-chain-dag-cs-poh)
add_subdirectory(libdap-chain-net)
add_subdirectory(libdap-chain-net-srv)
add_subdirectory(libdap-chain-net-srv-app)
add_subdirectory(libdap-chain-net-srv-app-db)
add_subdirectory(libdap-chain-net-srv-tx)
add_subdirectory(libdap-chain-net-srv-vpn)
add_subdirectory(libdap-chain-net-srv-mining)
#add_subdirectory(libdap-chain-net-srv-mining-pool)
add_subdirectory(libdap-stream)
add_subdirectory(libdap-stream-ch)
add_subdirectory(libdap-stream-ch-vpn)
add_subdirectory(libdap-stream-ch-chain)
add_subdirectory(libdap-stream-ch-chain-net)
add_subdirectory(libdap-stream-ch-chain-net-srv)
#add_subdirectory(libdap-stream-ch-chat)


#include_directories("${INCLUDE_DIRECTORIES} ${dap_core_INCLUDE_DIRS}")
#include_directories("${INCLUDE_DIRECTORIES} ${dap_http_INCLUDE_DIRS}")
#include_directories("${INCLUDE_DIRECTORIES} ${dap_crypto_INCLUDE_DIRS}")
#include_directories("${INCLUDE_DIRECTORIES} ${dap_enc_server_INCLUDE_DIRS}")
#include_directories("${INCLUDE_DIRECTORIES} ${dap_http_server_INCLUDE_DIRS}")

#include_directories("${INCLUDE_DIRECTORIES} ${dap-chain_INCLUDE_DIRS}")

#include_directories("${INCLUDE_DIRECTORIES} ${dap_core_server_INCLUDE_DIRS}")
#include_directories("${INCLUDE_DIRECTORIES} ${dap_udp_server_INCLUDE_DIRS}")
#include_directories("${INCLUDE_DIRECTORIES} ${dap_session_INCLUDE_DIRS}")
#include_directories("${INCLUDE_DIRECTORIES} ${dap_stream_INCLUDE_DIRS}")

#add_definitions ("${dap_core_DEFINITIONS}")
#add_definitions ("${dap_crypto_DEFINITIONS}")
#add_definitions ("${dap_enc_server_DEFINITIONS}")
#add_definitions ("${dap_http_server_DEFINITIONS}")
#add_definitions ("${dap_http_DEFINITIONS}")

#add_definitions ("${dap-chain_DEFINITIONS}")

#add_definitions ("${dap_core_server_DEFINITIONS}")
#add_definitions ("${dap_udp_server_DEFINITIONS}")
#add_definitions ("${dap_session_DEFINITIONS}")
#add_definitions ("${dap_stream_DEFINITIONS}")
file(GLOB SERVER_SRCS *.c)

set(SOURCES sources/main.c )


set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} ")
add_executable(${PROJECT_NAME} "sources/main.c" "sources/sig_unix_handler.c" ${HEADERS} ${SOURCES} ${SERVER_SRCS} )

target_link_libraries(${PROJECT_NAME} dap_core_server dap_http_server  dap_udp_server dap_session dap_crypto  dap_core dap_enc_server dap_stream dap_stream_ch_vpn dap_stream_ch_chain m pthread magic)

INSTALL(DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/../dist/ DESTINATION ${CMAKE_INSTALL_PREFIX} FILES_MATCHING PATTERN "*"  PATTERN "*")
INSTALL(TARGETS ${PROJECT_NAME} DESTINATION ${CMAKE_INSTALL_PREFIX}/bin )
INSTALL(DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/../scripts/ DESTINATION ${CMAKE_INSTALL_PREFIX}/bin FILES_MATCHING PATTERN "*"  PATTERN "*" PERMISSIONS OWNER_EXECUTE;OWNER_READ;OWNER_WRITE;WORLD_READ;GROUP_READ )
INCLUDE(CPack)
