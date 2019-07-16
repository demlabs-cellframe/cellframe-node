project(kelvin-node C)
cmake_minimum_required(VERSION 2.8)

if(WIN32)
  message(STATUS "Building for Windows")
endif()

set(CMAKE_VERBOSE_MAKEFILE ON)
set(CMAKE_COLOR_MAKEFILE   ON)
set(CMAKE_CXX_STANDARD 11)

SET(CMAKE_INSTALL_PREFIX "/opt/${PROJECT_NAME}")
SET(CPACK_INSTALL_PREFIX "/opt/${PROJECT_NAME}")
SET(DESTDIR "/opt/${PROJECT_NAME}")

SET( CPACK_GENERATOR "DEB")
SET( CPACK_PACKAGE_NAME  "${PROJECT_NAME}")
SET( CPACK_PACKAGE_VERSION_MAJOR 1)
SET( CPACK_PACKAGE_VERSION_MINOR 0)
SET( CPACK_PACKAGE_VERSION_PATCH 5)

SET( CPACK_SYSTEM_NAME "debian-9.7-amd64")
SET( CPACK_PACKAGE_VERSION "${CPACK_PACKAGE_VERSION_MAJOR}.${CPACK_PACKAGE_VERSION_MINOR}-${CPACK_PACKAGE_VERSION_PATCH}")
SET( CPACK_DEBIAN_PACKAGE_MAINTAINER "Dmitriy Gerasimov  <naeper@ldemlabs.net>" )
SET( CPACK_DEBIAN_PACKAGE_DESCRIPTION_SUMMARY "Kelvin Blockchain Node software" )
SET( CPACK_DEBIAN_PACKAGE_DESCRIPTION   "Kelvin Node" )
SET( CPACK_DEBIAN_PACKAGE_SECTION "extra")
#SET( CPACK_DEBIAN_PACKAGE_ARCHITECTURE "debian-9.7-amd64" )
#SET( CPACK_PACKAGE_FILE_NAME "${CPACK_DEBIAN_PACKAGE_NAME}-${CPACK_DEBIAN_PACKAGE_VERSION}-${CPACK_DEBIAN_PACKAGE_ARCHITECTURE}")
#SET( CPACK_DEBIAN_PACKAGE_ARCHITECTURE "amd64" )
SET( CPACK_DEBIAN_PACKAGE_DEPENDS "debconf (>=1.5), dpkg (>=1.17), bash (>=4), debconf-utils, dconf-cli, less, pv, psmisc")
SET( CPACK_DEBIAN_PACKAGE_SHLIBDEPS ON)
SET( CPACK_DEBIAN_PACKAGE_CONTROL_EXTRA
    "${CMAKE_CURRENT_SOURCE_DIR}/debian/postinst;${CMAKE_CURRENT_SOURCE_DIR}/debian/postrm;${CMAKE_CURRENT_SOURCE_DIR}/debian/templates;${CMAKE_CURRENT_SOURCE_DIR}/debian/config;")

set(CMAKE_VERBOSE_MAKEFILE ON)
set(CMAKE_COLOR_MAKEFILE   ON)
set(CMAKE_C_STANDARD 11)
set(SUBMODULES_NO_BUILD ON)

add_definitions ("-DDAP_SERVER")
add_definitions ("-DNODE_NETNAME=\"kelvin\"")

if(WIN32)
  add_definitions ("-DUNDEBUG")
  add_definitions ("-DNDEBUG")
  add_definitions ("-DWIN32")
  add_definitions ("-D_WINDOWS")
  add_definitions ("-D__WINDOWS__")
  add_definitions ("-D_CRT_SECURE_NO_WARNINGS")
  add_definitions ("-DCURL_STATICLIB")
#  add_definitions ("-DDAP_SERVER NODE_NETNAME=\"kelvin\"")
  set(_CCOPT "-mconsole -static -Wall -O3 -fno-ident -ffast-math -ftree-vectorize -mfpmath=sse -mmmx -msse2 -fno-asynchronous-unwind-tables -ffunction-sections -Wl,--gc-sections -Wl,--strip-all")
  set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} ${_CCOPT}")
  set(CMAKE_LINKER_FLAGS "${CMAKE_LINKER_FLAGS} ${_LOPT}")
endif()

if(UNIX)
    add_definitions ("-DDAP_OS_LINUX")
endif()

if(DAP_RELEASE)
  add_definitions ("-DUNDEBUG")
  add_definitions ("-DNDEBUG")

  if(UNIX)
    set(_CCOPT "-static -Wall -O3 -fno-ident -ffast-math -ftree-vectorize -mfpmath=sse -mmmx -msse2 -fno-asynchronous-unwind-tables -ffunction-sections -Wl,--gc-sections -Wl,--strip-all")
    set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} ${_CCOPT}")
  endif()

else()
  if(UNIX)
    SET(CMAKE_C_FLAGS "${CMAKE_CXX_FLAGS} -pg")
    SET(CMAKE_LINKER_FLAGS "${CMAKE_LINKER_FLAGS} -pg")
    SET(CMAKE_SHARED_LINKER_FLAGS "${CMAKE_SHARED_LINKER_FLAGS} -pg")
  endif()
endif()


add_subdirectory(libdap)
add_subdirectory(libdap-crypto)
add_subdirectory(libdap-server-core)
add_subdirectory(libdap-server-udp)
add_subdirectory(libdap-server)

if(NOT (WIN32))
  add_subdirectory(libdap-server-http-db-auth)
endif()

add_subdirectory(libdap-chain)
add_subdirectory(libdap-chain-crypto)
add_subdirectory(libdap-chain-wallet)
add_subdirectory(libdap-chain-cs-dag)
add_subdirectory(libdap-chain-cs-dag-poa)
add_subdirectory(libdap-chain-cs-dag-pos)
add_subdirectory(libdap-chain-net)
add_subdirectory(libdap-chain-net-srv)
add_subdirectory(libdap-chain-net-srv-app)
add_subdirectory(libdap-chain-net-srv-app-db)
add_subdirectory(libdap-chain-net-srv-datum)
add_subdirectory(libdap-chain-net-srv-datum-pool)

if(NOT (WIN32))
  add_subdirectory(libdap-chain-net-srv-vpn)
endif()

add_subdirectory(libdap-chain-mempool)
add_subdirectory(libdap-chain-gdb)

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


if(WIN32)
  include_directories(libdap/src/win32/)
  include_directories(3rdparty/libmemcached/)
  include_directories(3rdparty/libmemcached/win32/)
  include_directories(3rdparty/wepoll/include/)
  include_directories(3rdparty/uthash/src/)
  include_directories(3rdparty/libjson-c/)
  include_directories(3rdparty/libmagic/src/)
  include_directories(3rdparty/curl/include/)
  include_directories(3rdparty/libsqlite3/)
endif()

if(WIN32)
  include_directories(libdap-server-http-db-auth/)
  include_directories(libdap-chain-net-srv-vpn/)
endif()

if(UNIX)
  add_executable(${PROJECT_NAME} "sources/main.c" "sources/sig_unix_handler.c")
  add_executable(${PROJECT_NAME}-cli "sources/main_node_cli.c" "sources/main_node_cli_shell.c" "sources/main_node_cli_net.c" )
  add_executable(${PROJECT_NAME}-tool "sources/main_node_tool.c" )
endif()

if(WIN32)
  add_executable(${PROJECT_NAME} "sources/main.c" "sources/exh_win32.c" "sources/sig_win32_handler.c")
  add_executable(${PROJECT_NAME}-cli "sources/main_node_cli.c" "sources/main_node_cli_shell.c" "sources/main_node_cli_net.c" )
  add_executable(${PROJECT_NAME}-tool "sources/main_node_tool.c" )

  target_link_libraries(${PROJECT_NAME}-cli dap_chain_net 
  ${CMAKE_CURRENT_SOURCE_DIR}/lib/[x86_64CLANG]/curl[x86_64CLANG].a
  )

  target_link_libraries(${PROJECT_NAME}-tool dap_core dap_crypto dap_server_core dap_enc_server dap_udp_server dap_session
    dap_enc_server dap_stream dap_stream_ch_vpn dap_stream_ch_chain dap_stream_ch_chain_net
    dap_stream_ch_chain_net_srv dap_chain dap_chain_crypto dap_client
    dap_chain_cs_dag dap_chain_cs_dag_poa dap_chain_cs_dag_pos
    dap_chain_net dap_chain_net_srv dap_chain_net_srv_app dap_chain_net_srv_app_db
    dap_chain_net_srv_datum dap_chain_net_srv_datum_pool
    dap_chain_wallet dap_chain_global_db dap_chain_mempool 

    ${CMAKE_CURRENT_SOURCE_DIR}/lib/[x86_64CLANG]/libjson-c[x86_64CLANG].a
    ${CMAKE_CURRENT_SOURCE_DIR}/lib/[x86_64CLANG]/libmemcached[x86_64CLANG].a
    ${CMAKE_CURRENT_SOURCE_DIR}/lib/[x86_64CLANG]/wepoll[x86_64CLANG].a
    ${CMAKE_CURRENT_SOURCE_DIR}/lib/[x86_64CLANG]/libmagic[x86_64CLANG].a
    ${CMAKE_CURRENT_SOURCE_DIR}/lib/[x86_64CLANG]/cuttdb[x86_64CLANG].a
    ${CMAKE_CURRENT_SOURCE_DIR}/lib/[x86_64CLANG]/libsqlite3[x86_64CLANG].a
    ${CMAKE_CURRENT_SOURCE_DIR}/lib/[x86_64CLANG]/regex[x86_64CLANG].a
    ${CMAKE_CURRENT_SOURCE_DIR}/lib/[x86_64CLANG]/libmongoc[x86_64CLANG].a
    ${CMAKE_CURRENT_SOURCE_DIR}/lib/[x86_64CLANG]/libbson[x86_64CLANG].a
    ${CMAKE_CURRENT_SOURCE_DIR}/lib/[x86_64CLANG]/curl[x86_64CLANG].a
    ${CMAKE_CURRENT_SOURCE_DIR}/lib/[x86_64CLANG]/nghttp2[x86_64CLANG].a
    ${CMAKE_CURRENT_SOURCE_DIR}/lib/[x86_64CLANG]/libssl[x86_64CLANG].a
    ${CMAKE_CURRENT_SOURCE_DIR}/lib/[x86_64CLANG]/c-ares[x86_64CLANG].a
    ${CMAKE_CURRENT_SOURCE_DIR}/lib/[x86_64CLANG]/misc[x86_64CLANG].a
    ${CMAKE_CURRENT_SOURCE_DIR}/lib/[x86_64CLANG]/zlib[x86_64CLANG].a
    ${CMAKE_CURRENT_SOURCE_DIR}/lib/[x86_64CLANG]/libssh2[x86_64CLANG].a
    ${CMAKE_CURRENT_SOURCE_DIR}/lib/[x86_64CLANG]/libcrypto[x86_64CLANG].a
    KERNEL32
    USER32
    SHELL32
    WINMM
    GDI32
    ADVAPI32
    Ole32
    Version
    Imm32
    OleAut32
    ws2_32
    ntdll
    psapi
    Shlwapi
    Bcrypt
    Crypt32
    Secur32
)


  target_link_libraries(${PROJECT_NAME} dap_core dap_crypto dap_server_core dap_enc_server dap_udp_server dap_session
    dap_enc_server dap_stream dap_stream_ch_vpn dap_stream_ch_chain dap_stream_ch_chain_net
    dap_stream_ch_chain_net_srv dap_chain dap_chain_crypto dap_client
    dap_chain_cs_dag dap_chain_cs_dag_poa dap_chain_cs_dag_pos
    dap_chain_net dap_chain_net_srv dap_chain_net_srv_app dap_chain_net_srv_app_db
    dap_chain_net_srv_datum dap_chain_net_srv_datum_pool
    dap_chain_wallet dap_chain_global_db dap_chain_mempool dap_chain_gdb 
    ${CMAKE_CURRENT_SOURCE_DIR}/lib/[x86_64CLANG]/libjson-c[x86_64CLANG].a
    ${CMAKE_CURRENT_SOURCE_DIR}/lib/[x86_64CLANG]/libmemcached[x86_64CLANG].a
    ${CMAKE_CURRENT_SOURCE_DIR}/lib/[x86_64CLANG]/wepoll[x86_64CLANG].a
    ${CMAKE_CURRENT_SOURCE_DIR}/lib/[x86_64CLANG]/libmagic[x86_64CLANG].a
    ${CMAKE_CURRENT_SOURCE_DIR}/lib/[x86_64CLANG]/cuttdb[x86_64CLANG].a
    ${CMAKE_CURRENT_SOURCE_DIR}/lib/[x86_64CLANG]/libsqlite3[x86_64CLANG].a
    ${CMAKE_CURRENT_SOURCE_DIR}/lib/[x86_64CLANG]/regex[x86_64CLANG].a
    ${CMAKE_CURRENT_SOURCE_DIR}/lib/[x86_64CLANG]/libmongoc[x86_64CLANG].a
    ${CMAKE_CURRENT_SOURCE_DIR}/lib/[x86_64CLANG]/libbson[x86_64CLANG].a
    ${CMAKE_CURRENT_SOURCE_DIR}/lib/[x86_64CLANG]/curl[x86_64CLANG].a
    ${CMAKE_CURRENT_SOURCE_DIR}/lib/[x86_64CLANG]/nghttp2[x86_64CLANG].a
    ${CMAKE_CURRENT_SOURCE_DIR}/lib/[x86_64CLANG]/libssl[x86_64CLANG].a
    ${CMAKE_CURRENT_SOURCE_DIR}/lib/[x86_64CLANG]/c-ares[x86_64CLANG].a
    ${CMAKE_CURRENT_SOURCE_DIR}/lib/[x86_64CLANG]/misc[x86_64CLANG].a
    ${CMAKE_CURRENT_SOURCE_DIR}/lib/[x86_64CLANG]/zlib[x86_64CLANG].a
    ${CMAKE_CURRENT_SOURCE_DIR}/lib/[x86_64CLANG]/libssh2[x86_64CLANG].a
    ${CMAKE_CURRENT_SOURCE_DIR}/lib/[x86_64CLANG]/libcrypto[x86_64CLANG].a
    KERNEL32
    USER32
    SHELL32
    WINMM
    GDI32
    ADVAPI32
    Ole32
    Version
    Imm32
    OleAut32
    ws2_32
    ntdll
    psapi
    Shlwapi
    Bcrypt
    Crypt32
    Secur32
)

#dap_chain_net_srv_vpn dap_server_http_db_auth

endif()

#add_executable(${PROJECT_NAME}-cli "sources/main_node_cli.c" "sources/main_node_cli_shell.c" "sources/main_node_cli_net.c" )
#add_executable(${PROJECT_NAME}-tool "sources/main_node_tool.c" )

if(UNIX)

target_link_libraries(${PROJECT_NAME} dap_core dap_crypto dap_crypto dap_server_core dap_enc_server dap_udp_server dap_session
    dap_enc_server dap_stream dap_stream_ch_vpn dap_stream_ch_chain dap_stream_ch_chain_net
    dap_stream_ch_chain_net_srv dap_chain dap_chain_crypto dap_client
    dap_chain_cs_dag dap_chain_cs_dag_poa dap_chain_cs_dag_pos
    dap_chain_net dap_chain_net_srv dap_chain_net_srv_app dap_chain_net_srv_app_db
    dap_chain_net_srv_datum dap_chain_net_srv_datum_pool dap_chain_net_srv_vpn
    dap_chain_wallet dap_chain_global_db dap_chain_mempool dap_chain_gdb m pthread magic dap_server_http_db_auth)

target_link_libraries(${PROJECT_NAME}-cli m dap_chain_net curl) 

target_link_libraries(${PROJECT_NAME}-tool dap_core dap_crypto dap_server_core dap_enc_server  dap_udp_server dap_session
    dap_enc_server dap_stream dap_stream_ch_vpn dap_stream_ch_chain dap_stream_ch_chain_net
    dap_stream_ch_chain_net_srv dap_chain dap_chain_crypto dap_client
    dap_chain_cs_dag dap_chain_cs_dag_poa dap_chain_cs_dag_pos
    dap_chain_net dap_chain_net_srv dap_chain_net_srv_app dap_chain_net_srv_app_db
    dap_chain_net_srv_datum dap_chain_net_srv_datum_pool dap_chain_net_srv_vpn
    dap_chain_wallet dap_chain_global_db dap_chain_mempool m pthread magic )
endif()

target_include_directories(${PROJECT_NAME} INTERFACE .)

if(UNIX)
target_include_directories(${PROJECT_NAME}-cli INTERFACE .)
target_include_directories(${PROJECT_NAME}-tool INTERFACE .)
endif()

INSTALL(DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/dist/ DESTINATION ${CMAKE_INSTALL_PREFIX} FILES_MATCHING PATTERN "*"  PATTERN "*")
INSTALL(TARGETS ${PROJECT_NAME} DESTINATION ${CMAKE_INSTALL_PREFIX}/bin )

if(UNIX)
INSTALL(TARGETS ${PROJECT_NAME}-cli DESTINATION ${CMAKE_INSTALL_PREFIX}/bin )
INSTALL(TARGETS ${PROJECT_NAME}-tool DESTINATION ${CMAKE_INSTALL_PREFIX}/bin )
endif()

INSTALL(DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/scripts/ DESTINATION ${CMAKE_INSTALL_PREFIX}/bin FILES_MATCHING PATTERN "*"  PATTERN "*" PERMISSIONS OWNER_EXECUTE;OWNER_READ;OWNER_WRITE;WORLD_READ;GROUP_READ )
INCLUDE(CPack)
