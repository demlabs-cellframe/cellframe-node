project(cellframe-node C)
cmake_minimum_required(VERSION 3.10)
set(CMAKE_ENABLE_EXPORTS ON)
set(CMAKE_VERBOSE_MAKEFILE ON)
set(CMAKE_COLOR_MAKEFILE   ON)
set(CMAKE_C_STANDARD 11)

# Predefine project
SET( CPACK_PACKAGE_NAME  "${PROJECT_NAME}")
SET( CPACK_PACKAGE_VERSION_MAJOR 5)
SET( CPACK_PACKAGE_VERSION_MINOR 0)
SET( CPACK_PACKAGE_VERSION_PATCH 53)

if (CMAKE_TARGET_ARCH MATCHES arm)
    SET( CPACK_PACKAGE_ARCHITECTURE "${CMAKE_TARGET_ARCH}")
    SET( CPACK_DEBIAN_PACKAGE_ARCHITECTURE "${CMAKE_TARGET_ARCH}")
endif()

# Crossbuild configs

if (CMAKE_TARGET_ARCH MATCHES arm)
set(CMAKE_SYSTEM_PROCESSOR arm)
    if (CMAKE_TARGET_ARCH MATCHES armhf)
        set(CMAKE_C_COMPILER "/usr/bin/arm-linux-gnueabihf-gcc")
        set(CMAKE_CXX_COMPILER "/usr/bin/arm-linux-gnueabihf-g++")
        set(CMAKE_SYSROOT "/raspi-sysroot/")
    else()
        set(CMAKE_C_COMPILER "/usr/bin/aarch64-linux-gnu-gcc")
        set(CMAKE_CXX_COMPILER "/usr/bin/aarch64-linux-gnu-g++")
        set(CMAKE_SYSROOT "/arm64-sysroot/")
    endif()
endif()

# init CellFrame SDK
add_definitions("-DDAP_VERSION=\"${CPACK_PACKAGE_VERSION_MAJOR}-${CPACK_PACKAGE_VERSION_MINOR}.${CPACK_PACKAGE_VERSION_PATCH}\"")
set(SUBMODULES_NO_BUILD ON)
include (cellframe-sdk/cmake/OS_Detection.cmake)

#set(BUILD_WITH_GDB_DRIVER_PGSQL ON)
#set(BUILD_CRYPTO_TESTS ON)
#set(BUILD_WITH_PYTHON_ENV ON)

if(BUILD_WITH_GDB_DRIVER_MDBX)
add_subdirectory(3rdparty/libmdbx)
endif()

if(LINUX)
set(SUPPORT_PYTHON_PLUGINS ON)
endif()


if (WIN32)
    set(CELLFRAME_MODULES "core chains mining network srv cs-dag-poa cs-block-poa cs-dag-pos cs-block-pos cs-none srv-app srv-app-db srv-datum srv-stake srv-xchange")
elseif(BSD)
    set(CELLFRAME_MODULES "core chains mining network srv cs-dag-poa cs-block-poa cs-dag-pos cs-block-pos cs-none srv-app srv-app-db srv-datum srv-stake srv-xchange")
elseif(DARWIN)
    set(CELLFRAME_MODULES "core chains mining network srv cs-dag-poa cs-block-poa cs-dag-pos cs-block-pos cs-none srv-app srv-app-db srv-datum srv-stake srv-xchange")
elseif(ANDROID)
    set(CELLFRAME_MODULES "core chains mining network srv cs-dag-poa cs-block-poa cs-dag-pos cs-block-pos cs-none srv-app srv-app-db srv-datum srv-stake srv-xchange")
elseif(LINUX)
    set(CELLFRAME_MODULES "core chains mining network srv cs-dag-poa cs-block-poa cs-dag-pos cs-block-pos cs-none srv-app srv-app-db srv-datum srv-stake srv-xchange modules-dynamic srv-vpn")
endif()

if (CELLFRAME_MODULES MATCHES "modules-dynamic")
    add_definitions("-DDAP_MODULES_DYNAMIC")
endif()

add_subdirectory(cellframe-sdk)

if(UNIX)
    if(DARWIN)
        SET(CMAKE_INSTALL_PREFIX "${USERDIR_PATH}/Applications/Cellframe.app")
        SET(CPACK_INSTALL_PREFIX "${USERDIR_PATH}/Applications/Cellframe.app")
        SET(DESTDIR "${USERDIR_PATH}/Applications/Cellframe.app")

        set(BUNDLE_NAME "Cellframe.app")
        set(BUNDLE_PATH "${CMAKE_INSTALL_PREFIX}")
        set(BINDIR ${BUNDLE_PATH}/Contents/MacOS)
        set(LIBDIR ${BUNDLE_PATH})
        set(RLIBDIR ${BUNDLE_PATH}/Contents/Frameworks)
        set(SHAREDIR ${BUNDLE_PATH}/Contents/Resources)
        set(PLUGINSDIR ${BUNDLE_PATH}/Contents/PlugIns)
        set(IMPORTSDIR ${BINDIR})

        add_definitions("-DDAP_DARWIN_LIBRARY")
    else()
        SET(CMAKE_INSTALL_PREFIX "/opt/${PROJECT_NAME}")
        SET(CPACK_INSTALL_PREFIX "/opt/${PROJECT_NAME}")
        SET(DESTDIR "/opt/${PROJECT_NAME}")
    endif()



  if(LINUX)
    message("[*] Linux package setup")

    SET( CPACK_GENERATOR "DEB")

    SET( CPACK_SYSTEM_TYPE "Debian")
    SET( CPACK_SYSTEM_VERSION "${DEBIAN_OS_VERSION}")
    if (CMAKE_TARGET_ARCH MATCHES arm)
        SET( CPACK_SYSTEM_ARCH ${CMAKE_TARGET_ARCH})
    else()
        SET( CPACK_SYSTEM_ARCH "amd64")
    endif()
    SET( CPACK_SYSTEM_CODENAME "${DEBIAN_OS_NAME}")
    SET( CPACK_SYSTEM_NAME "${CPACK_SYSTEM_TYPE}-${CPACK_SYSTEM_VERSION}-${CPACK_SYSTEM_ARCH}")
    if(BUILD_WITH_GDB_DRIVER_PGSQL)
        SET( CPACK_SYSTEM_NAME "${CPACK_SYSTEM_NAME}-pgsql" )
    endif()
    if(CMAKE_BUILD_TYPE MATCHES Debug)
        SET( CPACK_SYSTEM_NAME "${CPACK_SYSTEM_NAME}-dbg" )
    endif()
    SET( CPACK_PACKAGE_VERSION "${CPACK_PACKAGE_VERSION_MAJOR}.${CPACK_PACKAGE_VERSION_MINOR}-${CPACK_PACKAGE_VERSION_PATCH}")
    SET( CPACK_DEBIAN_PACKAGE_MAINTAINER "Dmitriy Gerasimov <naeper@demlabs.net>" )
    SET( CPACK_DEBIAN_PACKAGE_DESCRIPTION_SUMMARY "CellFrame Node software https://cellframe.net" )
    SET( CPACK_DEBIAN_PACKAGE_DESCRIPTION   "CellFrame Node" )
    SET( CPACK_DEBIAN_PACKAGE_SECTION "extra")
    SET( CPACK_DEBIAN_PACKAGE_DEPENDS "debconf (>=1.5), dpkg (>=1.17), bash (>=4), debconf-utils, dconf-cli, less, pv, psmisc, logrotate, irqbalance, xz-utils")
    if (CMAKE_TARGET_ARCH MATCHES arm)
        SET( CPACK_DEBIAN_PACKAGE_DEPENDS "${CPACK_DEBIAN_PACKAGE_DEPENDS}, libmagic1, libpython3.9" )
    endif()
    SET( CPACK_DEBIAN_PACKAGE_SHLIBDEPS ON)
    SET( CPACK_DEBIAN_PACKAGE_CONTROL_EXTRA
    "${CMAKE_CURRENT_SOURCE_DIR}/debian/postinst;${CMAKE_CURRENT_SOURCE_DIR}/debian/postrm;${CMAKE_CURRENT_SOURCE_DIR}/debian/templates;${CMAKE_CURRENT_SOURCE_DIR}/debian/config;")
    elseif(BSD)
        message("[*] BSD family system ${CMAKE_SYSTEM} ")
    elseif(DARWIN)
	message("[*] Darwin kernel (MacOS/iOS) ")
    else()
        message("[!] Unknown UNIX")
    endif()
else()
    message("[ ] Not UNIX")
endif()

set(NODE_TARGET      "${PROJECT_NAME}"     )
set(NODE_CLI_TARGET  "${PROJECT_NAME}-cli" )
set(NODE_TOOL_TARGET "${PROJECT_NAME}-tool")



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
  if(ANDROID)
    add_library(${PROJECT_NAME} SHARED
        ${NODE_SOURCES}
        ${NODE_CLI_SOURCES}
        ${NODE_TOOL_SOURCES}
        sources/cellframe_node.h
    )
  else()
    add_executable(${PROJECT_NAME} ${NODE_SOURCES})
    add_executable(${NODE_CLI_TARGET} ${NODE_CLI_SOURCES})
    add_executable(${NODE_TOOL_TARGET} ${NODE_TOOL_SOURCES})
  endif()
endif()

if(WIN32)
    add_executable(${PROJECT_NAME} "sources/main.c" "sources/exh_win32.c" "sources/sig_win32_handler.c")
    add_executable(${NODE_CLI_TARGET} "sources/main_node_cli.c" )
    add_executable(${NODE_TOOL_TARGET} "sources/main_node_tool.c" )

    target_link_libraries(${NODE_CLI_TARGET} dap_chain_net dap_app_cli z pthread
			KERNEL32 USER32 SHELL32 WINMM GDI32 ADVAPI32 Ole32 Version Imm32
			OleAut32 ws2_32 ntdll psapi Shlwapi Bcrypt Crypt32 Secur32 userenv )
    set_property(TARGET ${NODE_CLI_TARGET} APPEND_STRING PROPERTY LINK_FLAGS "-mconsole")
    target_link_libraries(${NODE_TOOL_TARGET} cellframe-sdk )
    set_property(TARGET ${NODE_TOOL_TARGET} APPEND_STRING PROPERTY LINK_FLAGS "-mconsole")

    target_link_libraries(${PROJECT_NAME} cellframe-sdk json-c )
    set_property(TARGET ${PROJECT_NAME} APPEND_STRING PROPERTY LINK_FLAGS "-mwindows")

#dap_chain_net_srv_vpn dap_server_http_db_auth

endif()
if(BSD)
    set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -L /usr/local/lib ")
    set(CMAKE_LINKER_FLAGS "${CMAKE_LINKER_FLAGS} -L /usr/local/lib")
endif()

#if(DARWIN)
## 3rd party
#    include_directories(cellframe-sdk/3rdparty/cuttdb/src)
#    include_directories(cellframe-sdk/3rdparty/json-c/)
#    include_directories(cellframe-sdk/3rdparty/libmagic/file)
#    include_directories(cellframe-sdk/3rdparty/uthash/src)
#    include_directories(cellframe-sdk/dap-sdk/crypto/src/XKCP/lib/high/Keccak/FIPS202)

## DAP SDK
#    include_directories(cellframe-sdk/dap-sdk/core/include)
#    include_directories(cellframe-sdk/dap-sdk/crypto/include)
#    include_directories(cellframe-sdk/dap-sdk/net/include)
#    include_directories(cellframe-sdk/dap-sdk/core/src/common)
#    include_directories(cellframe-sdk/dap-sdk/core/src/darwin/macos)
#    include_directories(cellframe-sdk/dap-sdk/core/src/unix)
#    include_directories(cellframe-sdk/dap-sdk/net/core/include)
#    include_directories(cellframe-sdk/dap-sdk/net/client/include)
#    include_directories(cellframe-sdk/dap-sdk/net/server/enc_server/include)
#    include_directories(cellframe-sdk/dap-sdk/net/server/http_server/include)
#    include_directories(cellframe-sdk/dap-sdk/net/server/http_server/http_client/include)
#    include_directories(cellframe-sdk/dap-sdk/net/server/json_rpc/)
#    include_directories(cellframe-sdk/dap-sdk/net/server/notify_server/include)
#    include_directories(cellframe-sdk/dap-sdk/stream/ch/include)
#    include_directories(cellframe-sdk/dap-sdk/stream/session/include)
#    include_directories(cellframe-sdk/dap-sdk/stream/stream/include)
##CellFrame SDK
#    include_directories(cellframe-sdk/modules/app-cli/include)
#    include_directories(cellframe-sdk/modules/chain/include)
#    include_directories(cellframe-sdk/modules/chain/btc_rpc/include)
#    include_directories(cellframe-sdk/modules/channel/chain/include)
#    include_directories(cellframe-sdk/modules/channel/chain-net/include)
#    include_directories(cellframe-sdk/modules/channel/chain-net-srv/include)
#    include_directories(cellframe-sdk/modules/common/include)
#    include_directories(cellframe-sdk/modules/consensus/block-poa/include)
#    include_directories(cellframe-sdk/modules/consensus/block-pow/include)
#    include_directories(cellframe-sdk/modules/consensus/dag-poa/include)
#    include_directories(cellframe-sdk/modules/consensus/dag-pos/include)
#    include_directories(cellframe-sdk/modules/consensus/none/include)
#    include_directories(cellframe-sdk/modules/global-db/include)
#    include_directories(cellframe-sdk/modules/mempool/include)
#    include_directories(cellframe-sdk/modules/mining/include)
#    include_directories(cellframe-sdk/modules/modules_dynamic/cdb/include)
#    include_directories(cellframe-sdk/modules/net/include)
#    include_directories(cellframe-sdk/modules/net/srv/include)
#    include_directories(cellframe-sdk/modules/service/app/include)
#    include_directories(cellframe-sdk/modules/service/app-db/include)
#    include_directories(cellframe-sdk/modules/service/datum/include)
#    include_directories(cellframe-sdk/modules/service/mining-pool/include)
#    include_directories(cellframe-sdk/modules/service/stake/include)
#    include_directories(cellframe-sdk/modules/service/vpn/include)
#    include_directories(cellframe-sdk/modules/service/xchange/include)
#    include_directories(cellframe-sdk/modules/service/type/blocks/include)
#    include_directories(cellframe-sdk/modules/service/type/dag/include)
#    include_directories(cellframe-sdk/modules/service/wallet/include)
#endif()

#add_executable(${PROJECT_NAME}-cli "sources/main_node_cli.c" "sources/main_node_cli_shell.c" "sources/main_node_cli_net.c" )
#add_executable(${PROJECT_NAME}-tool "sources/main_node_tool.c" )

if(UNIX AND NOT WIN32)
    message ("[*] Unix library set")
    set_property(TARGET ${PROJECT_NAME} APPEND_STRING PROPERTY LINK_FLAGS "-D_GNU_SOURCE")
    set(NODE_LIBRARIES cellframe-sdk )

    set(NODE_CLI_LIBRARIES m cellframe-sdk)

    set(NODE_TOOL_LIBRARIES m cellframe-sdk)

    if (SUPPORT_PYTHON_PLUGINS)
        add_definitions("-DDAP_SUPPORT_PYTHON_PLUGINS")
        if (BUILD_WITH_PYTHON_ENV)
            add_definitions("-DDAP_BUILD_WITH_PYTHON_ENV")
        endif()

        set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -DDAP_SUPPORT_PYTHON_PLUGINS")
         if (BUILD_WITH_PYTHON_ENV)
            message("[+] Build with python environment")
            set(CMAKE_PREFIX_PATH "/opt/cellframe-node")
        endif()
        message("[+] Build with python plugins support")
            set(Python_ADDITIONAL_VERSION 3.9 3.8 3.7 3.6 3.5 3.4)
        find_package(PythonLibs REQUIRED)
        include_directories(${PYTHON_INCLUDE_DIR} include/)
	add_subdirectory(python-cellframe)
        if (BUILD_WITH_PYTHON_ENV)
            set(PYTHON_LIBRARIES -lssl -lcrypto -lcrypt -lnsl ${PYTHON_LIBRARIES} -lz -lutil -lexpat )
        endif()

        set(NODE_LIBRARIES ${NODE_LIBRARIES} ${PYTHON_LIBRARIES} dap_plugins_python)
    endif()

    if(ANDROID )
        set(ALL_LIBRARIES ${NODE_LIBRARIES} ${NODE_CLI_LIBRARIES} ${NODE_TOOL_LIBRARIES} log)

        list(REMOVE_DUPLICATES ALL_LIBRARIES)

        target_link_libraries(${NODE_TARGET} ${ALL_LIBRARIES})
    else()
        target_link_libraries(${NODE_TARGET}      ${NODE_LIBRARIES} pthread )
        target_link_libraries(${NODE_CLI_TARGET}  ${NODE_CLI_LIBRARIES} pthread )
        target_link_libraries(${NODE_TOOL_TARGET} ${NODE_TOOL_LIBRARIES} pthread )
    endif()
endif()

target_include_directories(${PROJECT_NAME} INTERFACE .)

if(NOT ANDROID)
    target_include_directories(${NODE_CLI_TARGET} INTERFACE .)
    target_include_directories(${NODE_TOOL_TARGET} INTERFACE .)
endif()

if(DARWIN)
    INSTALL(DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/dist/ DESTINATION ${SHAREDIR} FILES_MATCHING PATTERN "*"  PATTERN "*")
    INSTALL(DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/dist.darwin/ DESTINATION ${SHAREDIR} FILES_MATCHING PATTERN "*"  PATTERN "*")
    INSTALL(TARGETS ${PROJECT_NAME} DESTINATION ${BINDIR} )
    INSTALL(TARGETS ${NODE_CLI_TARGET} DESTINATION ${BINDIR} )
    INSTALL(TARGETS ${NODE_TOOL_TARGET} DESTINATION ${BINDIR} )

    INSTALL(DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/scripts/ DESTINATION ${BINDIR} FILES_MATCHING PATTERN "*"  PATTERN "*" PERMISSIONS OWNER_EXECUTE;OWNER_READ;OWNER_WRITE;WORLD_READ;GROUP_READ )
    INSTALL(DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/scripts.darwin/ DESTINATION ${BINDIR} FILES_MATCHING PATTERN "*"  PATTERN "*" PERMISSIONS OWNER_EXECUTE;OWNER_READ;OWNER_WRITE;WORLD_READ;GROUP_READ )

else()
    if(BUILD_WITH_PYTHON_ENV)
       INSTALL(FILES /cpython.tar.xz DESTINATION ${CMAKE_INSTALL_PREFIX}/share )
    endif()

    INSTALL(DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/dist/ DESTINATION ${CMAKE_INSTALL_PREFIX} FILES_MATCHING PATTERN "*"  PATTERN "*")
    if(LINUX)
	INSTALL(DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/dist.linux/ DESTINATION ${CMAKE_INSTALL_PREFIX} FILES_MATCHING PATTERN "*"  PATTERN "*")
    elseif(DARWIN)
	INSTALL(DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/dist.darwin/ DESTINATION ${CMAKE_INSTALL_PREFIX} FILES_MATCHING PATTERN "*"  PATTERN "*")
    elseif(BSD)
	INSTALL(DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/dist.bsd/ DESTINATION ${CMAKE_INSTALL_PREFIX} FILES_MATCHING PATTERN "*"  PATTERN "*")
    endif()

    INSTALL(TARGETS ${PROJECT_NAME} DESTINATION ${CMAKE_INSTALL_PREFIX}/bin )

    if(UNIX AND NOT ANDROID)
	INSTALL(TARGETS ${NODE_CLI_TARGET} DESTINATION ${CMAKE_INSTALL_PREFIX}/bin )
	INSTALL(TARGETS ${NODE_TOOL_TARGET} DESTINATION ${CMAKE_INSTALL_PREFIX}/bin )
    endif()

    INSTALL(DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/scripts/ DESTINATION ${CMAKE_INSTALL_PREFIX}/sbin FILES_MATCHING PATTERN "*"  PATTERN "*" PERMISSIONS OWNER_EXECUTE;OWNER_READ;OWNER_WRITE;WORLD_READ;GROUP_READ )
endif()
INCLUDE(CPack)
