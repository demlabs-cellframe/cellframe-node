project(cellframe-node C)
cmake_minimum_required(VERSION 3.1)
SET(CMAKE_INSTALL_PREFIX "/opt/${PROJECT_NAME}")
SET(CPACK_INSTALL_PREFIX "/opt/${PROJECT_NAME}")
SET(DESTDIR "/opt/${PROJECT_NAME}")

SET( CPACK_GENERATOR "DEB")
SET( CPACK_PACKAGE_NAME  "${PROJECT_NAME}")
SET( CPACK_PACKAGE_VERSION_MAJOR 2)
SET( CPACK_PACKAGE_VERSION_MINOR 13)
SET( CPACK_PACKAGE_VERSION_PATCH 1)

SET( CPACK_SYSTEM_TYPE "debian")
SET( CPACK_SYSTEM_VERSION "10.0")
SET( CPACK_SYSTEM_ARCH "amd64")
SET( CPACK_SYSTEM_CODENAME "buster")
SET( CPACK_SYSTEM_NAME "${CPACK_SYSTEM_TYPE}-${CPACK_SYSTEM_VERSION}-${CPACK_SYSTEM_ARCH}-${CPACK_SYSTEM_CODENAME}")
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

if((CMAKE_BUILD_TYPE STREQUAL "Debug") OR (DAP_DEBUG))
    message("Debug build")
    SET(DAP_DEBUG ON)
else()
    message("Release build")
    SET(DAP_RELEASE ON)
endif()

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

if(UNIX)
  add_definitions ("-DDAP_OS_LINUX -DDAP_OS_UNIX")
# add_definitions ("-DDAP_LOG_MT")
  if(DAP_DEBUG)
      set(_CCOPT "-DDAP_DEBUG -Wall -Wno-unused-function -Wno-implicit-fallthrough -Wno-unused-variable -Wno-unused-parameter -Wno-unused-but-set-variable -pg -g3 -ggdb -fno-eliminate-unused-debug-symbols")
      set(_LOPT "-pg")
      SET(CMAKE_SHARED_LINKER_FLAGS "${CMAKE_SHARED_LINKER_FLAGS} -pg")
  else()
    set(_CCOPT "-Wno-unused-function -Wno-implicit-fallthrough -Wno-unused-variable -Wno-unused-parameter -Wno-unused-but-set-variable -O3 -fPIC -fno-ident -ffast-math -ftree-vectorize -fno-asynchronous-unwind-tables -ffunction-sections -Wl,--gc-sections -Wl,--strip-all -std=gnu11")
  endif()

  if (ANDROID)
      set(_CCOPT "${_CCOPT} -fforce-enable-int128 -std=gnu11")
      add_definitions ("-DDAP_OS_ANDROID -DDAP_OS_UNIX")
  endif()

  set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} ${_CCOPT}")
  set(CMAKE_LINKER_FLAGS "${CMAKE_LINKER_FLAGS} ${_LOPT}")

  if (ANDROID)
    add_subdirectory(lib/json-c)
    add_subdirectory(lib/sqlite3)
    #add_subdirectory(lib/libev)
    include_directories(lib/)
  else()
  endif(ANDROID)

endif()



if(WIN32)
  message(STATUS "Building for Windows")

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
  add_definitions("-DNGHTTP2_STATICLIB")
  add_compile_definitions(WINVER=0x0600 _WIN32_WINNT=0x0600)

  if(DAP_DEBUG)
      set(_CCOPT "-mconsole -static -Wall -std=gnu11 -Wextra -Wno-unused-function -Wno-implicit-fallthrough -Wno-unused-variable -Wno-unused-parameter -Wno-unused-but-set-variable -g3 -ggdb -fno-eliminate-unused-debug-symbols -pg")
      set(_LOPT "-mconsole -static -pg")
  else()
      set(_CCOPT "-static -std=gnu11 -Wall -Wextra -Wno-unused-function -Wno-implicit-fallthrough -Wno-unused-variable -Wno-unused-parameter -Wno-unused-but-set-variable -O3 -fno-ident -ffast-math -ftree-vectorize -mfpmath=sse -mmmx -msse2 -fno-asynchronous-unwind-tables -ffunction-sections -Wl,--gc-sections -Wl,--strip-all")
  endif()

  set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} ${_CCOPT} ")
  set(CMAKE_LINKER_FLAGS "${CMAKE_LINKER_FLAGS} ${_LOPT}")

  include_directories(3rdparty/uthash/src/)
  include_directories(3rdparty/wepoll/)
  #include_directories(libdap-chain-net-srv-vpn/)
endif()

add_definitions("-DDAP_VERSION=\"${CPACK_PACKAGE_VERSION_MAJOR}\"")
add_definitions ("-DDAP_SERVER -DDAP_LOG_MT")
add_definitions ("-DNODE_NETNAME=\"cellframe\"")

set(NODE_TARGET      "${PROJECT_NAME}"     )
set(NODE_CLI_TARGET  "${PROJECT_NAME}-cli" )
set(NODE_TOOL_TARGET "${PROJECT_NAME}-tool")

include(scripts/OS_Detection.cmake)

set(SUBMODULES_NO_BUILD ON)
set(SUPPORT_PYTHON_PLUGINS OFF)

add_subdirectory(cellframe-sdk)

if(BUILD_CELLFRAME_NODE_TESTS)
    enable_testing()
    add_subdirectory(test)
endif()

set( NODE_SOURCES
  sources/main.c
  sources/sig_unix_handler.c
)
set( NODE_CLI_SOURCES
  sources/main_node_cli.c
)
set( NODE_TOOL_SOURCES
  sources/main_node_tool.c
)

if(UNIX)
   add_definitions ("-DDAP_OS_UNIX")
  if(ANDROID)
    add_definitions ("-DDAP_OS_LINUX")
    add_definitions ("-DDAP_OS_ANDROID")
    add_library(${PROJECT_NAME} SHARED
        ${NODE_SOURCES}
        ${NODE_CLI_SOURCES}
        ${NODE_TOOL_SOURCES}
        sources/cellframe_node.h
    )
  else()
    add_definitions ("-DDAP_OS_LINUX")
    add_executable(${PROJECT_NAME} ${NODE_SOURCES})
    add_executable(${NODE_CLI_TARGET} ${NODE_CLI_SOURCES})
    add_executable(${NODE_TOOL_TARGET} ${NODE_TOOL_SOURCES})
  endif()
endif()

if(WIN32)
   add_definitions ("-DDAP_OS_WINDOWS")
  add_executable(${PROJECT_NAME} "sources/main.c" "sources/exh_win32.c" "sources/sig_win32_handler.c")
  add_executable(${NODE_CLI_TARGET} "sources/main_node_cli.c" )
  add_executable(${NODE_TOOL_TARGET} "sources/main_node_tool.c" )
  target_link_libraries(${NODE_CLI_TARGET} dap_chain_net dap_app_cli nghttp2 ssl cares ssh2 crypto z pthread # curl
    #${CMAKE_CURRENT_SOURCE_DIR}/lib/[x86_64CLANG]/nghttp2[x86_64CLANG].a
    ${CMAKE_CURRENT_SOURCE_DIR}/lib/[x86_64CLANG]/curl[x86_64CLANG].a
    #${CMAKE_CURRENT_SOURCE_DIR}/lib/[x86_64CLANG]/libssl[x86_64CLANG].a
    #${CMAKE_CURRENT_SOURCE_DIR}/lib/[x86_64CLANG]/c-ares[x86_64CLANG].a
    #${CMAKE_CURRENT_SOURCE_DIR}/lib/[x86_64CLANG]/misc[x86_64CLANG].a
    #${CMAKE_CURRENT_SOURCE_DIR}/lib/[x86_64CLANG]/zlib[x86_64CLANG].a
    #${CMAKE_CURRENT_SOURCE_DIR}/lib/[x86_64CLANG]/libssh2[x86_64CLANG].a
    #${CMAKE_CURRENT_SOURCE_DIR}/lib/[x86_64CLANG]/libcrypto[x86_64CLANG].a
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
  set_property(TARGET ${NODE_CLI_TARGET} APPEND_STRING PROPERTY LINK_FLAGS "-mconsole")
    target_link_libraries(${NODE_TOOL_TARGET} dap_core dap_crypto dap_server_core dap_enc_server dap_udp_server dap_session
    dap_enc_server dap_stream dap_stream_ch_chain dap_stream_ch_chain_net
    dap_stream_ch_chain_net_srv dap_chain dap_chain_crypto dap_client
    dap_chain_cs_dag dap_chain_cs_dag_poa dap_chain_cs_dag_pos
    dap_chain_net dap_chain_net_srv dap_chain_net_srv_app dap_chain_net_srv_app_db
    dap_chain_net_srv_datum dap_chain_net_srv_datum_pool
    dap_chain_wallet dap_chain_global_db dap_chain_mempool dap_cuttdb nghttp2 ssl cares ssh2 crypto z pthread # curl

    #${CMAKE_CURRENT_SOURCE_DIR}/lib/[x86_64CLANG]/nghttp2[x86_64CLANG].a
    ${CMAKE_CURRENT_SOURCE_DIR}/lib/[x86_64CLANG]/curl[x86_64CLANG].a
    #${CMAKE_CURRENT_SOURCE_DIR}/lib/[x86_64CLANG]/libssl[x86_64CLANG].a
    #${CMAKE_CURRENT_SOURCE_DIR}/lib/[x86_64CLANG]/c-ares[x86_64CLANG].a
    #${CMAKE_CURRENT_SOURCE_DIR}/lib/[x86_64CLANG]/misc[x86_64CLANG].a
    #${CMAKE_CURRENT_SOURCE_DIR}/lib/[x86_64CLANG]/zlib[x86_64CLANG].a
    #${CMAKE_CURRENT_SOURCE_DIR}/lib/[x86_64CLANG]/libssh2[x86_64CLANG].a
    #${CMAKE_CURRENT_SOURCE_DIR}/lib/[x86_64CLANG]/libcrypto[x86_64CLANG].a
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
  set_property(TARGET ${NODE_TOOL_TARGET} APPEND_STRING PROPERTY LINK_FLAGS "-mconsole")
  target_link_libraries(${PROJECT_NAME}



      cellframe-sdk



      json-c sqlite3 nghttp2 ssl cares z ssh2 crypto m # curl
    #${CMAKE_CURRENT_SOURCE_DIR}/lib/[x86_64CLANG]/nghttp2[x86_64CLANG].a
    ${CMAKE_CURRENT_SOURCE_DIR}/lib/[x86_64CLANG]/curl[x86_64CLANG].a
    #${CMAKE_CURRENT_SOURCE_DIR}/lib/[x86_64CLANG]/libssl[x86_64CLANG].a
    #${CMAKE_CURRENT_SOURCE_DIR}/lib/[x86_64CLANG]/c-ares[x86_64CLANG].a
    #${CMAKE_CURRENT_SOURCE_DIR}/lib/[x86_64CLANG]/misc[x86_64CLANG].a
    #${CMAKE_CURRENT_SOURCE_DIR}/lib/[x86_64CLANG]/zlib[x86_64CLANG].a
    #${CMAKE_CURRENT_SOURCE_DIR}/lib/[x86_64CLANG]/libssh2[x86_64CLANG].a
    #${CMAKE_CURRENT_SOURCE_DIR}/lib/[x86_64CLANG]/libcrypto[x86_64CLANG].a
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

if(UNIX AND NOT WIN32)
    set_property(TARGET ${PROJECT_NAME} APPEND_STRING PROPERTY LINK_FLAGS "-D_GNU_SOURCE")
    add_definitions("-DDAP_SUPPORT_PYTHON_PLUGINS")
    set(NODE_LIBRARIES
        cellframe-sdk )

    set(NODE_CLI_LIBRARIES
        m dap_chain_net curl dap_cuttdb dap_app_cli)

    set(NODE_TOOL_LIBRARIES
        dap_core dap_crypto dap_server_core dap_enc_server  dap_udp_server dap_session
        dap_enc_server dap_stream dap_chain_net_srv_vpn dap_stream_ch_chain dap_stream_ch_chain_net
        dap_stream_ch_chain_net_srv dap_chain dap_chain_crypto dap_client
        dap_chain_cs_dag dap_chain_cs_dag_poa dap_chain_cs_dag_pos
        dap_chain_net dap_chain_net_srv dap_chain_net_srv_app dap_chain_net_srv_app_db
        dap_chain_net_srv_datum dap_chain_net_srv_datum_pool dap_chain_net_srv_vpn
        dap_chain_wallet dap_chain_global_db dap_chain_mempool m magic
        dap_core
    )

    if (SUPPORT_PYTHON_PLUGINS)
        set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -DDAP_SUPPORT_PYTHON_PLUGINS")
        message("Build with support python plugins")
        set(Python_ADDITIONAL_VERSION 3.7 3.6 3.5 3.4)
        find_package(PythonLibs REQUIRED)
        include_directories(${PYTHON_INCLUDE_DIR} include/)

        add_subdirectory(cellframe-sdk-python/libdap-python)
        add_subdirectory(cellframe-sdk-python/libdap-server-core-python)
        add_subdirectory(cellframe-sdk-python/libdap-crypto-python)
        add_subdirectory(cellframe-sdk-python/libdap-chain-common-python)
        add_subdirectory(cellframe-sdk-python/libdap-chain-net-python)
        add_subdirectory(cellframe-sdk-python/libdap-chain-gdb-python)
        add_subdirectory(cellframe-sdk-python/libdap-chain-python)
        add_subdirectory(cellframe-sdk-python/libdap-app-cli-python)
        add_subdirectory(cellframe-sdk-python/libdap-client-python)
	add_subdirectory(python-cellframe)
        add_subdirectory(libdap-plugins-python)
        set(NODE_LIBRARIES ${NODE_LIBRARIES} ${PYTHON_LIBRARIES} dap_plugins_python)
    endif()

    if(ANDROID )
        set(ALL_LIBRARIES ${NODE_LIBRARIES} ${NODE_CLI_LIBRARIES} ${NODE_TOOL_LIBRARIES} log)

        list(REMOVE_DUPLICATES ALL_LIBRARIES)

        target_link_libraries(${NODE_TARGET} ${ALL_LIBRARIES})

    else()
        target_link_libraries(${NODE_TARGET}      ${NODE_LIBRARIES} pthread dap_cuttdb )
        target_link_libraries(${NODE_CLI_TARGET}  ${NODE_CLI_LIBRARIES} pthread )
        target_link_libraries(${NODE_TOOL_TARGET} ${NODE_TOOL_LIBRARIES} pthread )
    endif()
endif()

target_include_directories(${PROJECT_NAME} INTERFACE .)

if(NOT ANDROID)
    target_include_directories(${NODE_CLI_TARGET} INTERFACE .)
    target_include_directories(${NODE_TOOL_TARGET} INTERFACE .)
endif()

INSTALL(DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/dist/ DESTINATION ${CMAKE_INSTALL_PREFIX} FILES_MATCHING PATTERN "*"  PATTERN "*")
INSTALL(TARGETS ${PROJECT_NAME} DESTINATION ${CMAKE_INSTALL_PREFIX}/bin )

if(UNIX AND NOT ANDROID)
    INSTALL(TARGETS ${NODE_CLI_TARGET} DESTINATION ${CMAKE_INSTALL_PREFIX}/bin )
    INSTALL(TARGETS ${NODE_TOOL_TARGET} DESTINATION ${CMAKE_INSTALL_PREFIX}/bin )
endif()

INSTALL(DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/scripts/ DESTINATION ${CMAKE_INSTALL_PREFIX}/bin FILES_MATCHING PATTERN "*"  PATTERN "*" PERMISSIONS OWNER_EXECUTE;OWNER_READ;OWNER_WRITE;WORLD_READ;GROUP_READ )
INCLUDE(CPack)
