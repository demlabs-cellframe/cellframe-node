project(cellframe-node C)
cmake_minimum_required(VERSION 3.1)

include(scripts/OS_Detection.cmake)

if(DAP_DEBUG_BUILD)
    set(DAP_RELEASE 0)
    message(STATUS "Debug build")
else()
    set(DAP_RELEASE 1)
    message(STATUS "Release build")
endif()

if(WIN32)
  message(STATUS "Building for Windows")
endif()

# Check whether we're on a 32-bit or 64-bit system
if(CMAKE_SIZEOF_VOID_P EQUAL "8")
  set(DEFAULT_BUILD_64 ON)
else()
  set(DEFAULT_BUILD_64 OFF)
endif()
option(BUILD_64 "Build for 64-bit? 'OFF' builds for 32-bit." ${DEFAULT_BUILD_64})

if(BUILD_64)
  set(ARCH_WIDTH "64")
else()
  set(ARCH_WIDTH "32")
endif()
message(STATUS "Building for a ${ARCH_WIDTH}-bit system")

if(DAP_RELEASE)
  message(STATUS "Building type RELEASE")
else()
  message(STATUS "Building type DEBUG")
endif()

set(CMAKE_VERBOSE_MAKEFILE ON)
set(CMAKE_COLOR_MAKEFILE   ON)
set(CMAKE_CXX_STANDARD 11)

SET(CMAKE_INSTALL_PREFIX "/opt/${PROJECT_NAME}")
SET(CPACK_INSTALL_PREFIX "/opt/${PROJECT_NAME}")
SET(DESTDIR "/opt/${PROJECT_NAME}")

SET( CPACK_GENERATOR "DEB")
SET( CPACK_PACKAGE_NAME  "${PROJECT_NAME}")
SET( CPACK_PACKAGE_VERSION_MAJOR 2)
SET( CPACK_PACKAGE_VERSION_MINOR 8)
SET( CPACK_PACKAGE_VERSION_PATCH 7)

SET( CPACK_SYSTEM_NAME "debian-9.9-amd64")
SET( CPACK_PACKAGE_VERSION "${CPACK_PACKAGE_VERSION_MAJOR}.${CPACK_PACKAGE_VERSION_MINOR}-${CPACK_PACKAGE_VERSION_PATCH}")
SET( CPACK_DEBIAN_PACKAGE_MAINTAINER "Dmitriy Gerasimov <naeper@demlabs.net>" )
SET( CPACK_DEBIAN_PACKAGE_DESCRIPTION_SUMMARY "CellFrame Node software https://cellframe.net" )
SET( CPACK_DEBIAN_PACKAGE_DESCRIPTION   "CellFrame Node" )
SET( CPACK_DEBIAN_PACKAGE_SECTION "extra")
SET( CPACK_DEBIAN_PACKAGE_DEPENDS "debconf (>=1.5), dpkg (>=1.17), bash (>=4), debconf-utils, dconf-cli, less, pv, psmisc")
SET( CPACK_DEBIAN_PACKAGE_SHLIBDEPS ON)
SET( CPACK_DEBIAN_PACKAGE_CONTROL_EXTRA
    "${CMAKE_CURRENT_SOURCE_DIR}/debian/postinst;${CMAKE_CURRENT_SOURCE_DIR}/debian/postrm;${CMAKE_CURRENT_SOURCE_DIR}/debian/templates;${CMAKE_CURRENT_SOURCE_DIR}/debian/config;")

set(CMAKE_VERBOSE_MAKEFILE ON)
set(CMAKE_COLOR_MAKEFILE   ON)
set(CMAKE_C_STANDARD 11)
set(SUBMODULES_NO_BUILD ON)

add_definitions("-DDAP_VERSION=\"${CPACK_PACKAGE_VERSION_MAJOR}\"")
add_definitions ("-DDAP_SERVER -DDAP_LOG_MT")
add_definitions ("-DNODE_NETNAME=\"cellframe\"")

if(WIN32)

  add_definitions ("-DUNDEBUG")
  add_definitions ("-DNDEBUG")
  add_definitions ("-DWIN32")
  add_definitions ("-D_WINDOWS")
  add_definitions ("-D__WINDOWS__")
  add_definitions ("-D_CRT_SECURE_NO_WARNINGS")
  add_definitions ("-DCURL_STATICLIB")
  add_definitions("-DHAVE_PREAD")
  add_definitions("-DHAVE_MMAP")
  add_definitions("-DHAVE_STRNDUP")
  add_compile_definitions(WINVER=0x0600 _WIN32_WINNT=0x0600)

  if(DAP_RELEASE)
    set(_CCOPT "-static -std=gnu11 -Wall -O3 -fno-ident -ffast-math -ftree-vectorize -mfpmath=sse -mmmx -msse2 -fno-asynchronous-unwind-tables -ffunction-sections -Wl,--gc-sections -Wl,--strip-all")
  else()
    set(_CCOPT "-mconsole -static -Wall -pg")
    set(_LOPT "-mconsole -static -pg")
  endif()

  set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} ${_CCOPT}")
  set(CMAKE_LINKER_FLAGS "${CMAKE_LINKER_FLAGS} ${_LOPT}")

  include_directories(libdap/src/win32/)
  include_directories(3rdparty/uthash/src/)
  include_directories(3rdparty/libjson-c/)
  include_directories(3rdparty/curl/include/)
  include_directories(3rdparty/libsqlite3/)
  include_directories(sources/wepoll/)
  include_directories(libdap-server-http-db-auth/)
  include_directories(libdap-chain-net-srv-vpn/)
endif()

if(UNIX)
  add_definitions ("-DDAP_OS_LINUX -DDAP_OS_UNIX")
# add_definitions ("-DDAP_LOG_MT")
  if(DAP_RELEASE)
    set(_CCOPT " -Wall -O3 -fPIC -fno-ident -ffast-math -ftree-vectorize -fno-asynchronous-unwind-tables -ffunction-sections -Wl,--gc-sections -Wl,--strip-all -std=gnu11")
  else()
    set(_CCOPT "-Wall -pg -g3 -ggdb -fno-eliminate-unused-debug-symbols")
    set(_LOPT "-pg")
    SET(CMAKE_SHARED_LINKER_FLAGS "${CMAKE_SHARED_LINKER_FLAGS} -pg")
  endif()

  if (ANDROID)
      set(_CCOPT "${_CCOPT} -fforce-enable-int128 -std=gnu11")
  endif()

  set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} ${_CCOPT}")
  set(CMAKE_LINKER_FLAGS "${CMAKE_LINKER_FLAGS} ${_LOPT}")

  if (ANDROID)
    add_subdirectory(lib/json-c)
    add_subdirectory(lib/sqlite3)
    add_subdirectory(lib/libev)
    include_directories(lib/)
  else()
    add_subdirectory(libdap-server-http-db)
    add_subdirectory(libdap-server-http-db-auth)
  endif(ANDROID)

endif()

add_subdirectory(libdap)
add_subdirectory(libdap-crypto)
add_subdirectory(libdap-server-core)
add_subdirectory(libdap-server-udp)
add_subdirectory(libdap-server)


add_subdirectory(libdap-chain-crypto)
add_subdirectory(libdap-chain-common)
add_subdirectory(libdap-chain)
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

add_subdirectory(libdap-stream-ch-chain)
#add_subdirectory(libdap-stream-ch-chat)
add_subdirectory(libdap-stream-ch-chain-net)
add_subdirectory(libdap-stream-ch-chain-net-srv)

add_subdirectory(libdap-chain-global-db)
#add_subdirectory(libdap-stream-ch-chat)

if(BUILD_CELLFRAME_NODE_TESTS)
    enable_testing()
    add_subdirectory(test)
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
    ${CMAKE_CURRENT_SOURCE_DIR}/lib/[x86_64CLANG]/libjson-c[x86_64CLANG].a
    ${CMAKE_CURRENT_SOURCE_DIR}/lib/[x86_64CLANG]/libsqlite3[x86_64CLANG].a
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
    userenv
  )
  set_property(TARGET ${PROJECT_NAME}-cli APPEND_STRING PROPERTY LINK_FLAGS "-mconsole")
    target_link_libraries(${PROJECT_NAME}-tool dap_core dap_crypto dap_server_core dap_enc_server dap_udp_server dap_session
    dap_enc_server dap_stream dap_stream_ch_chain dap_stream_ch_chain_net
    dap_stream_ch_chain_net_srv dap_chain dap_chain_crypto dap_client
    dap_chain_cs_dag dap_chain_cs_dag_poa dap_chain_cs_dag_pos
    dap_chain_net dap_chain_net_srv dap_chain_net_srv_app dap_chain_net_srv_app_db
    dap_chain_net_srv_datum dap_chain_net_srv_datum_pool
    dap_chain_wallet dap_chain_global_db dap_chain_mempool dap_cuttdb

    ${CMAKE_CURRENT_SOURCE_DIR}/lib/[x86_64CLANG]/libjson-c[x86_64CLANG].a
    ${CMAKE_CURRENT_SOURCE_DIR}/lib/[x86_64CLANG]/libsqlite3[x86_64CLANG].a
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
    userenv
  )
  set_property(TARGET ${PROJECT_NAME}-tool APPEND_STRING PROPERTY LINK_FLAGS "-mconsole")

  target_link_libraries(${PROJECT_NAME} dap_core dap_crypto dap_server_core dap_enc_server dap_udp_server dap_session
    dap_enc_server dap_stream dap_stream_ch_chain dap_stream_ch_chain_net
    dap_stream_ch_chain_net_srv dap_chain dap_chain_crypto dap_client
    dap_chain_cs_dag dap_chain_cs_dag_poa dap_chain_cs_dag_pos
    dap_chain_net dap_chain_net_srv dap_chain_net_srv_app dap_chain_net_srv_app_db
    dap_chain_net_srv_datum dap_chain_net_srv_datum_pool
    dap_chain_wallet dap_chain_global_db dap_chain_mempool dap_chain_gdb
    ${CMAKE_CURRENT_SOURCE_DIR}/lib/[x86_64CLANG]/libjson-c[x86_64CLANG].a
    ${CMAKE_CURRENT_SOURCE_DIR}/lib/[x86_64CLANG]/libsqlite3[x86_64CLANG].a
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
    userenv
  )
    set_property(TARGET ${PROJECT_NAME} APPEND_STRING PROPERTY LINK_FLAGS "-mwindows")

#dap_chain_net_srv_vpn dap_server_http_db_auth

endif()

#add_executable(${PROJECT_NAME}-cli "sources/main_node_cli.c" "sources/main_node_cli_shell.c" "sources/main_node_cli_net.c" )
#add_executable(${PROJECT_NAME}-tool "sources/main_node_tool.c" )

if(UNIX)
    target_link_libraries(${PROJECT_NAME} dap_core dap_crypto dap_crypto dap_server_core dap_enc_server dap_udp_server dap_session
        dap_enc_server dap_stream dap_stream_ch_chain dap_stream_ch_chain_net
        dap_stream_ch_chain_net_srv dap_chain dap_chain_crypto dap_client
        dap_chain_cs_dag dap_chain_cs_dag_poa dap_chain_cs_dag_pos
        dap_chain_net dap_chain_net_srv dap_chain_net_srv_app dap_chain_net_srv_app_db
        dap_chain_net_srv_datum dap_chain_net_srv_datum_pool dap_chain_net_srv_vpn
        dap_chain_wallet dap_chain_global_db dap_chain_mempool dap_chain_gdb m magic
        dap_cuttdb
        #dap_server_http_db
    )

    target_link_libraries(${PROJECT_NAME}-cli m dap_chain_net curl dap_cuttdb )

    target_link_libraries(${PROJECT_NAME}-tool dap_core dap_crypto dap_server_core dap_enc_server  dap_udp_server dap_session
        dap_enc_server dap_stream dap_stream_ch_chain dap_stream_ch_chain_net
        dap_stream_ch_chain_net_srv dap_chain dap_chain_crypto dap_client
        dap_chain_cs_dag dap_chain_cs_dag_poa dap_chain_cs_dag_pos
        dap_chain_net dap_chain_net_srv dap_chain_net_srv_app dap_chain_net_srv_app_db
        dap_chain_net_srv_datum dap_chain_net_srv_datum_pool dap_chain_net_srv_vpn
        dap_chain_wallet dap_chain_global_db dap_chain_mempool m magic
        dap_core
    )

    if(NOT ANDROID)
        target_link_libraries(${PROJECT_NAME}
            pthread
            dap_server_http_db_auth
            dap_cuttdb
            )
        target_link_libraries(${PROJECT_NAME}-cli pthread)
        target_link_libraries(${PROJECT_NAME}-tool pthread)

    endif()
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
