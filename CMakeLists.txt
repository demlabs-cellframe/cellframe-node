project(cellframe-node C)
cmake_minimum_required(VERSION 3.1)
set(CMAKE_VERBOSE_MAKEFILE ON)
set(CMAKE_COLOR_MAKEFILE   ON)
set(CMAKE_C_STANDARD 11)

# Predefine project
SET( CPACK_PACKAGE_NAME  "${PROJECT_NAME}")
SET( CPACK_PACKAGE_VERSION_MAJOR 4)
SET( CPACK_PACKAGE_VERSION_MINOR 1)
SET( CPACK_PACKAGE_VERSION_PATCH 18)

# init CellFrame SDK
add_definitions("-DDAP_VERSION=\"${CPACK_PACKAGE_VERSION_MAJOR}\"")
set(SUBMODULES_NO_BUILD ON)
set(SUPPORT_PYTHON_PLUGINS ON)

if (NOT WIN32)
    set(CELLFRAME_MODULES "core chains mining network srv cs-blocks cs-blocks-poa cs-dag-poa cs-dag-pos cs-none srv-app srv-app-db srv-datum srv-xchange srv-stake modules-dynamic srv-vpn")
else()
    set(CELLFRAME_MODULES "core chains mining network srv cs-blocks cs-blocks-poa cs-dag-poa cs-dag-pos cs-none srv-app srv-app-db srv-datum srv-xchange srv-stake modules-dynamic")
endif()

include (cellframe-sdk/cmake/OS_Detection.cmake)
add_subdirectory(cellframe-sdk)

if(UNIX)
  if(LINUX)
    message("[*] Linux package setup")
    SET(CMAKE_INSTALL_PREFIX "/opt/${PROJECT_NAME}")
    SET(CPACK_INSTALL_PREFIX "/opt/${PROJECT_NAME}")
    SET(DESTDIR "/opt/${PROJECT_NAME}")

    SET( CPACK_GENERATOR "DEB")

    SET( CPACK_SYSTEM_TYPE "Debian")
    SET( CPACK_SYSTEM_VERSION "${DEBIAN_OS_VERSION}")
    SET( CPACK_SYSTEM_ARCH "amd64")
    SET( CPACK_SYSTEM_CODENAME "${DEBIAN_OS_NAME}")
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

  else()
    message("[!] Unix but not linux")
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

#add_executable(${PROJECT_NAME}-cli "sources/main_node_cli.c" "sources/main_node_cli_shell.c" "sources/main_node_cli_net.c" )
#add_executable(${PROJECT_NAME}-tool "sources/main_node_tool.c" )

if(UNIX AND NOT WIN32)
    set_property(TARGET ${PROJECT_NAME} APPEND_STRING PROPERTY LINK_FLAGS "-D_GNU_SOURCE")
    set(NODE_LIBRARIES cellframe-sdk )

    set(NODE_CLI_LIBRARIES m dap_chain_net dap_cuttdb dap_app_cli)

    set(NODE_TOOL_LIBRARIES cellframe-sdk )

    if (SUPPORT_PYTHON_PLUGINS)
        add_definitions("-DDAP_SUPPORT_PYTHON_PLUGINS")
        set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -DDAP_SUPPORT_PYTHON_PLUGINS")
        message("[+] Build with support python plugins")
        set(Python_ADDITIONAL_VERSION 3.7 3.6 3.5 3.4)
        find_package(PythonLibs REQUIRED)
        include_directories(${PYTHON_INCLUDE_DIR} include/)

	add_subdirectory(python-cellframe)
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

INSTALL(DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/dist/ DESTINATION ${CMAKE_INSTALL_PREFIX} FILES_MATCHING PATTERN "*"  PATTERN "*")
INSTALL(TARGETS ${PROJECT_NAME} DESTINATION ${CMAKE_INSTALL_PREFIX}/bin )

if(UNIX AND NOT ANDROID)
    INSTALL(TARGETS ${NODE_CLI_TARGET} DESTINATION ${CMAKE_INSTALL_PREFIX}/bin )
    INSTALL(TARGETS ${NODE_TOOL_TARGET} DESTINATION ${CMAKE_INSTALL_PREFIX}/bin )
endif()

INSTALL(DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/scripts/ DESTINATION ${CMAKE_INSTALL_PREFIX}/sbin FILES_MATCHING PATTERN "*"  PATTERN "*" PERMISSIONS OWNER_EXECUTE;OWNER_READ;OWNER_WRITE;WORLD_READ;GROUP_READ )
INCLUDE(CPack)
