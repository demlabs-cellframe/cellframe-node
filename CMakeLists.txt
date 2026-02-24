cmake_minimum_required(VERSION 3.10)

project(cellframe-node C)
include(cellframe-sdk/cmake/ReadMKFile.cmake)

set(CMAKE_ENABLE_EXPORTS ON)
set(CMAKE_VERBOSE_MAKEFILE ON)
set(CMAKE_COLOR_MAKEFILE   ON)
set(CMAKE_C_STANDARD 11)

# Predefine project
SET( CPACK_PACKAGE_NAME  "${PROJECT_NAME}")
ReadVariables(version.mk)
SET( CPACK_PACKAGE_VERSION_MAJOR ${VERSION_MAJOR})
SET( CPACK_PACKAGE_VERSION_MINOR ${VERSION_MINOR})
SET( CPACK_PACKAGE_VERSION_PATCH ${VERSION_PATCH})

# Option to enable full cppcheck analysis
option(ENABLE_CPPCHECK_ANALYSIS "Enable full cppcheck static analysis" OFF)

# Cpp check
if(ENABLE_CPPCHECK_ANALYSIS)
    find_program(CPPCHECK cppcheck)
    if(CPPCHECK)
        message(STATUS "Found cppcheck: ${CPPCHECK}")
        add_custom_target(cppcheck_analysis
            COMMAND ${CPPCHECK}
                --std=c11
                --enable=warning,style,performance,portability
                --quiet
                --xml
                -I ${CMAKE_SOURCE_DIR}/dap-sdk/core/include
                -I ${CMAKE_SOURCE_DIR}/cellframe-sdk/modules/common/include
                ${CMAKE_SOURCE_DIR}/conftool
                ${CMAKE_SOURCE_DIR}/dist/linux
                ${CMAKE_SOURCE_DIR}/dist/common
                ${CMAKE_SOURCE_DIR}/os
                ${CMAKE_SOURCE_DIR}/resousrses
                ${CMAKE_SOURCE_DIR}/sourses
                2> ${CMAKE_BINARY_DIR}/cppcheck_report.xml
            COMMAND cppcheck-htmlreport
                --file ${CMAKE_BINARY_DIR}/cppcheck_report.xml
                --report-dir ${CMAKE_BINARY_DIR}/cppcheck_html_report
                --source-dir ${CMAKE_SOURCE_DIR}
            WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
            COMMENT "Running full cppcheck static analysis and generating HTML report in ${CMAKE_BINARY_DIR}/cppcheck_html_report"
        )
    else()
        message(WARNING "cppcheck not found, cppcheck_analysis target unavailable")
    endif()
endif()

find_program(CPPCHECK cppcheck)
if(CPPCHECK)
    message(STATUS "Found cppcheck: ${CPPCHECK}")
    add_custom_target(lint_cellframe_node
        COMMAND ${CPPCHECK} --enable=warning,style --std=c11 ${CMAKE_SOURCE_DIR}/sources
        WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
        COMMENT "Running cppcheck on source files"
    )
else()
    message(WARNING "cppcheck not found, lint_cellframe_node target unavailable")
endif()

#enable for diagtool 
#set(BUILD_DIAGTOOL OFF)

SET(CMAKE_INSTALL_PREFIX "/opt/${PROJECT_NAME}")
SET(CPACK_INSTALL_PREFIX "/opt/${PROJECT_NAME}")
SET(DESTDIR "/opt/${PROJECT_NAME}")

string(TIMESTAMP BUILD_TIMESTAMP "%d.%m.%Y")

execute_process(
    COMMAND git log -1 --format=%h
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
    OUTPUT_VARIABLE GIT_COMMIT_HASH
    OUTPUT_STRIP_TRAILING_WHITESPACE
    )
message("Build date: ${BUILD_TIMESTAMP}")
message("Git SHA: ${GIT_COMMIT_HASH}")


#SET(DAP_PQLR OFF)
#possible need be setted during crosscompily
#by default it uses dpkg --print-architecture
#we ok with it on native builds.
#SET( CPACK_PACKAGE_ARCHITECTURE "${CMAKE_SYSTEM_PROCESSOR}")
#SET( CPACK_DEBIAN_PACKAGE_ARCHITECTURE "${CMAKE_SYSTEM_PROCESSOR}")

# init CellFrame SDK

set(DAP_VERSION "${CPACK_PACKAGE_VERSION_MAJOR}.${CPACK_PACKAGE_VERSION_MINOR}-${CPACK_PACKAGE_VERSION_PATCH}")
set(BUILD_TS "${BUILD_TIMESTAMP}")
set(BUILD_HASH "${GIT_COMMIT_HASH}")

add_definitions("-DDAP_VERSION=\"${DAP_VERSION}\"")
add_definitions("-DBUILD_TS=\"${BUILD_TS}\"")
add_definitions("-DBUILD_HASH=\"${BUILD_HASH}\"")

set(SUBMODULES_NO_BUILD ON)
option(CELLFRAME_NO_OPTIMIZATION "Build without BMI BMI2 CPU instruction." ON)

if( CELLFRAME_NO_OPTIMIZATION )
    set(DAP_CRYPTO_XKCP_PLAINC ON)
endif()

include (dap-sdk/cmake/OS_Detection.cmake)

#set(BUILD_CELLFRAME_NODE_TESTS ON)
#option(BUILD_CELLFRAME_SDK_TESTS "Build Cellframe SDK tests" ON)
#set(BUILD_DAP_SDK_TESTS ON)
if (BUILD_CELLFRAME_NODE_TESTS OR BUILD_CELLFRAME_SDK_TESTS OR BUILD_DAP_SDK_TESTS)
    set(NEED_TEST_FRAMEWORK ON)
endif()

#set (BUILD_WITH_TPS_TEST ON)
if (BUILD_WITH_TPS_TEST)
    add_definitions("-DDAP_TPS_TEST")
endif()

set(BUILD_SHARED OFF CACHE BOOL "Build final library as shared" FORCE)
set(BUILD_WITH_ZIP OFF)

option(ADD_UPDATER OFF)
option(DAP_USE_RPMALLOC "Use 'rpmalloc' instead of std allocator" OFF)

set(CELLFRAME_MODULES "core chains ledger node-cli network srv cs-dag-poa cs-esbocs cs-none
                       srv-app srv-app-db srv-datum srv-stake srv-xchange srv-bridge srv-voting srv-stake-ext compose")

if(LINUX OR DARWIN)
    set(CELLFRAME_MODULES "${CELLFRAME_MODULES} srv-vpn")
endif()

if(NEED_TEST_FRAMEWORK)
    # Add test-framework to default modules if not defined
    if(NOT DEFINED DAPSDK_MODULES OR DAPSDK_MODULES STREQUAL "")
        set(DAPSDK_MODULES "crypto plugin io network-core network-server network-client network-link_manager global-db test-framework")
    else()
        set(DAPSDK_MODULES "${DAPSDK_MODULES} test-framework")
    endif()
endif()

# activate sphincsplus flexible option
set(SPHINCSPLUS_FLEX ON)

# Disable SDK installation - they are build-time dependencies only
# SDKs should not be installed into app bundle or system
set(INSTALL_DAP_SDK OFF CACHE BOOL "Disable DAP SDK installation (build-time dependency)" FORCE)
set(INSTALL_CELLFRAME_SDK OFF CACHE BOOL "Disable Cellframe SDK installation (build-time dependency)" FORCE)

set(DAP_TPL_DIR "${CMAKE_SOURCE_DIR}/tools/dap_tpl" CACHE PATH "Path to dap_tpl templating engine")

add_subdirectory(dap-sdk)
add_subdirectory(cellframe-sdk)
if(UNIX)
    if(DARWIN)
        SET(CMAKE_INSTALL_PREFIX "/Applications/CellframeNode.app")
        SET(CPACK_INSTALL_PREFIX "/Applications/CellframeNode.app")
        SET(DESTDIR "/Applications/CellframeNode.app")

        set(BUNDLE_NAME "CellframeNode.app")
        set(BUNDLE_PATH "${CMAKE_INSTALL_PREFIX}")
        set(BINDIR ${BUNDLE_PATH}/Contents/MacOS)
        set(CONTENTSDIR ${BUNDLE_PATH}/Contents/)
        set(LIBDIR ${BUNDLE_PATH})
        set(RLIBDIR ${BUNDLE_PATH}/Contents/Frameworks)
        set(SHAREDIR ${BUNDLE_PATH}/Contents/Resources)
        set(PLUGINSDIR ${BUNDLE_PATH}/Contents/PlugIns)
        set(IMPORTSDIR ${BINDIR})

        add_definitions("-DDAP_DARWIN_LIBRARY")

    endif()



  if(LINUX)
    message("[*] Linux package setup")

    SET( CPACK_GENERATOR "DEB")
    SET( CPACK_SYSTEM_TYPE "${DEBIAN_OS_RELEASE_NAME}")
    SET( CPACK_SYSTEM_VERSION "${DEBIAN_OS_VERSION}")
    SET( CPACK_SYSTEM_CODENAME "${DEBIAN_OS_NAME}")

    # set architecture
    find_program(DPKG_CMD dpkg)
    if(NOT CPACK_TARGET_ARCHITECTURE)
        if(NOT DPKG_CMD)
            message(WARNING "DEB Generator: Can't find dpkg in your path. Setting CPACK_DEBIAN_PACKAGE_ARCHITECTURE to amd64.")
            set(CPACK_DEBIAN_PACKAGE_ARCHITECTURE amd64)
        else()
            execute_process(COMMAND "${DPKG_CMD}" --print-architecture
                    OUTPUT_VARIABLE CPACK_DEBIAN_PACKAGE_ARCHITECTURE
                    OUTPUT_STRIP_TRAILING_WHITESPACE)
        endif()

    else()
        set (CPACK_DEBIAN_PACKAGE_ARCHITECTURE ${CPACK_TARGET_ARCHITECTURE})
    endif()

    if(NOT CPACK_SYSTEM_NAME)
        set(CPACK_SYSTEM_NAME ${CPACK_DEBIAN_PACKAGE_ARCHITECTURE})
    endif()

    SET( CPACK_PACKAGE_VERSION "${CPACK_PACKAGE_VERSION_MAJOR}.${CPACK_PACKAGE_VERSION_MINOR}-${CPACK_PACKAGE_VERSION_PATCH}")

    if(CMAKE_BUILD_TYPE MATCHES Debug)
        SET( CPACK_PACKAGE_VERSION "${CPACK_PACKAGE_VERSION}-dbg" )
    endif()

    if(CMAKE_BUILD_TYPE MATCHES RelWithDebInfo)
        if(ADD_UPDATER)
            SET( CPACK_PACKAGE_VERSION "${CPACK_PACKAGE_VERSION}-updtr" )
        elseif(BUILD_WITH_TPS_TEST)
            SET( CPACK_PACKAGE_VERSION "${CPACK_PACKAGE_VERSION}-tps" )
        else()
            SET( CPACK_PACKAGE_VERSION "${CPACK_PACKAGE_VERSION}-rwd" )
        endif()

        if (NOT CELLFRAME_NO_OPTIMIZATION)
            SET( CPACK_PACKAGE_VERSION "${CPACK_PACKAGE_VERSION}-opt" )
        endif()
    else() #to use -updtr postfix in rwd build without rwd
        if(ADD_UPDATER)
            set(CMAKE_BUILD_TYPE RelWithDebInfo) 
            SET( CPACK_PACKAGE_VERSION "${CPACK_PACKAGE_VERSION}-updtr" )
        elseif(BUILD_WITH_TPS_TEST)
            SET( CPACK_PACKAGE_VERSION "${CPACK_PACKAGE_VERSION}-tps" )
        endif()
    endif()

    if (DEFINED ENV{DAP_ASAN})
        SET( CPACK_PACKAGE_VERSION "${CPACK_PACKAGE_VERSION}-asan" )
    endif()
    if (DEFINED ENV{DAP_UBSAN})
        SET( CPACK_PACKAGE_VERSION "${CPACK_PACKAGE_VERSION}-ubsan" )
    endif()
    if (DEFINED ENV{DAP_TSAN})
        SET( CPACK_PACKAGE_VERSION "${CPACK_PACKAGE_VERSION}-tsan" )
    endif()


    SET( CPACK_DEBIAN_PACKAGE_MAINTAINER "Dmitriy Gerasimov <naeper@demlabs.net>" )
    SET( CPACK_DEBIAN_PACKAGE_DESCRIPTION_SUMMARY "CellFrame Node software https://cellframe.net" )
    SET( CPACK_DEBIAN_PACKAGE_DESCRIPTION   "CellFrame Node" )
    SET( CPACK_DEBIAN_PACKAGE_SECTION "extra")
    SET( CPACK_DEBIAN_PACKAGE_DEPENDS "dpkg (>=1.17), bash (>=4), less, pv, psmisc, logrotate, irqbalance, xz-utils, libsqlite3-0")
    SET( CPACK_DEBIAN_PACKAGE_SHLIBDEPS ON)
    if (CMAKE_CROSSCOMPILING AND CMAKE_SYSROOT)
        SET( CPACK_DEBIAN_PACKAGE_SHLIBDEPS_PRIVATE_DIRS 
            "${CMAKE_SYSROOT}/lib;${CMAKE_SYSROOT}/usr/lib;${CMAKE_SYSROOT}/lib/aarch64-linux-gnu;${CMAKE_SYSROOT}/usr/lib/aarch64-linux-gnu;${CMAKE_SYSROOT}/lib/arm-linux-gnueabihf;${CMAKE_SYSROOT}/usr/lib/arm-linux-gnueabihf")
    endif()

    message("[*] Debian package setup pkgarch=${CPACK_DEBIAN_PACKAGE_ARCHITECTURE} version=${CPACK_PACKAGE_VERSION}")

    SET( CPACK_DEBIAN_PACKAGE_CONTROL_EXTRA
    "${CMAKE_CURRENT_SOURCE_DIR}/os/debian/postinst;${CMAKE_CURRENT_SOURCE_DIR}/os/debian/prerm;${CMAKE_CURRENT_SOURCE_DIR}/os/debian/postrm;${CMAKE_CURRENT_SOURCE_DIR}/os/debian/templates;${CMAKE_CURRENT_SOURCE_DIR}/os/debian/config;")
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

set( NODE_SOURCES
        sources/cellframe-node.c
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
    )
    add_subdirectory(sources/android)

  else()
    add_executable(${PROJECT_NAME} ${NODE_SOURCES})
    add_executable(${NODE_CLI_TARGET} ${NODE_CLI_SOURCES})
    add_executable(${NODE_TOOL_TARGET} ${NODE_TOOL_SOURCES})
  endif()
endif()

if(WIN32)
    add_executable(${PROJECT_NAME} "sources/cellframe-node.c" "sources/exh_win32.c" "sources/sig_win32_handler.c")
    add_executable(${NODE_CLI_TARGET} "sources/main_node_cli.c" )
    add_executable(${NODE_TOOL_TARGET} "sources/main_node_tool.c" )

    target_link_libraries(${NODE_CLI_TARGET} cellframe_sdk z pthread
            kernel32 user32 shell32 winmm gdi32 advapi32 ole32 version imm32
            oleaut32 ws2_32 ntdll psapi shlwapi bcrypt crypt32 secur32 userenv )
    set_property(TARGET ${NODE_CLI_TARGET} APPEND_STRING PROPERTY LINK_FLAGS "-mconsole")
    target_link_libraries(${NODE_TOOL_TARGET} cellframe_sdk )
    set_property(TARGET ${NODE_TOOL_TARGET} APPEND_STRING PROPERTY LINK_FLAGS "-mconsole")

    target_link_libraries(${PROJECT_NAME} cellframe_sdk dap_json-c )
    if ((CMAKE_BUILD_TYPE STREQUAL "Debug") OR (DAP_DEBUG))
        set_property(TARGET ${PROJECT_NAME} APPEND_STRING PROPERTY LINK_FLAGS "-mconsole")
    else()
        set_property(TARGET ${PROJECT_NAME} APPEND_STRING PROPERTY LINK_FLAGS "-mwindows")
    endif()

endif()
if(BSD)
    set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -L /usr/local/lib ")
    set(CMAKE_LINKER_FLAGS "${CMAKE_LINKER_FLAGS} -L /usr/local/lib")
endif()

if(BUILD_DIAGTOOL)
    message("[*] Diagtool build on")
    add_subdirectory(diagtool)
endif()

add_subdirectory(tools/conftool)

if(UNIX AND NOT WIN32)
    message ("[*] Unix library set")
    set_property(TARGET ${PROJECT_NAME} APPEND_STRING PROPERTY LINK_FLAGS "-D_GNU_SOURCE")
    
    # Collect all DAP SDK OBJECT modules for direct linking (bypass static library issues)
    set(DAP_SDK_OBJECTS "")
    if(DEFINED DAP_INTERNAL_MODULES)
        foreach(MODULE ${DAP_INTERNAL_MODULES})
            if(TARGET ${MODULE})
                list(APPEND DAP_SDK_OBJECTS $<TARGET_OBJECTS:${MODULE}>)
            endif()
        endforeach()
        list(LENGTH DAP_INTERNAL_MODULES DAP_MOD_COUNT)
        message("[*] Using ${DAP_MOD_COUNT} DAP SDK OBJECT modules directly")
    endif()
    
    # Collect all Cellframe SDK OBJECT modules for direct linking
    set(CELLFRAME_SDK_OBJECTS "")
    if(DEFINED CELLFRAME_INTERNAL_MODULES)
        foreach(MODULE ${CELLFRAME_INTERNAL_MODULES})
            if(TARGET ${MODULE})
                list(APPEND CELLFRAME_SDK_OBJECTS $<TARGET_OBJECTS:${MODULE}>)
            endif()
        endforeach()
        message("[*] Using Cellframe SDK OBJECT modules directly")
    endif()
    
    set(NODE_LIBRARIES ${CELLFRAME_SDK_OBJECTS} ${DAP_SDK_OBJECTS} cellframe_sdk dap_sdk)
    set(NODE_CLI_LIBRARIES m ${CELLFRAME_SDK_OBJECTS} ${DAP_SDK_OBJECTS} cellframe_sdk dap_sdk)
    set(NODE_TOOL_LIBRARIES m ${CELLFRAME_SDK_OBJECTS} ${DAP_SDK_OBJECTS} cellframe_sdk dap_sdk)

    if(ANDROID )
        set(ALL_LIBRARIES ${NODE_LIBRARIES} ${NODE_CLI_LIBRARIES} ${NODE_TOOL_LIBRARIES} log  )
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
    INSTALL(DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/dist/common/ DESTINATION ${SHAREDIR} FILES_MATCHING PATTERN "*"  PATTERN "*")
    INSTALL(TARGETS ${PROJECT_NAME} DESTINATION ${BINDIR} )
    INSTALL(TARGETS ${NODE_CLI_TARGET} DESTINATION ${BINDIR} )
    INSTALL(TARGETS ${NODE_TOOL_TARGET} DESTINATION ${BINDIR} )
    INSTALL(TARGETS cellframe-node-config DESTINATION ${BINDIR} )
    if(BUILD_DIAGTOOL)
        INSTALL(TARGETS cellframe-diagtool DESTINATION ${BINDIR})
    endif()
    INSTALL(FILES ${CMAKE_CURRENT_SOURCE_DIR}/os/macos/com.demlabs.cellframe-node.plist DESTINATION ${SHAREDIR} )
    INSTALL(FILES ${CMAKE_CURRENT_SOURCE_DIR}/os/macos/Info.plist DESTINATION ${CONTENTSDIR} )

else()

    INSTALL(DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/dist/common/ DESTINATION ${CMAKE_INSTALL_PREFIX} FILES_MATCHING PATTERN "*"  PATTERN "*")
    if(LINUX)
        
        #install all from dist/linux/share except updater files and node-serivice
        if(NOT ADD_UPDATER)
            INSTALL(DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/dist/linux/ DESTINATION ${CMAKE_INSTALL_PREFIX} PATTERN "*cellframe-updater*" EXCLUDE PATTERN "*cellframe-node*service*" EXCLUDE )
        else()
            INSTALL(DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/dist/linux/ DESTINATION ${CMAKE_INSTALL_PREFIX} PATTERN "*cellframe-node*service*" EXCLUDE)
        endif()

        #install node service depends on sanitasizes values
        if (DEFINED ENV{DAP_ASAN})
            INSTALL(FILES ${CMAKE_CURRENT_SOURCE_DIR}/dist/linux/share/cellframe-node.asan.service DESTINATION ${CMAKE_INSTALL_PREFIX}/share/ RENAME cellframe-node.service )
        elseif(DEFINED ENV{DAP_UBSAN})
            INSTALL(FILES ${CMAKE_CURRENT_SOURCE_DIR}/dist/linux/share/cellframe-node.ubsan.service DESTINATION ${CMAKE_INSTALL_PREFIX}/share/ RENAME cellframe-node.service )
        elseif(DEFINED ENV{DAP_TSAN})
            INSTALL(FILES ${CMAKE_CURRENT_SOURCE_DIR}/dist/linux/share/cellframe-node.tsan.service DESTINATION ${CMAKE_INSTALL_PREFIX}/share/ RENAME cellframe-node.service )
        else()
            INSTALL(FILES ${CMAKE_CURRENT_SOURCE_DIR}/dist/linux/share/cellframe-node.service DESTINATION ${CMAKE_INSTALL_PREFIX}/share/ RENAME cellframe-node.service )
        endif()
        
    elseif(BSD)
        INSTALL(DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/dist/bsd/ DESTINATION ${CMAKE_INSTALL_PREFIX} )
    endif()

    if(WIN32)
        INSTALL(FILES os/windows/cellframe-node.nsis DESTINATION ${CMAKE_INSTALL_ROOT}/ )
        INSTALL(FILES resources/cellframe.ico DESTINATION ${CMAKE_INSTALL_ROOT}/ )
        INSTALL(FILES resources/cellframe.bmp DESTINATION ${CMAKE_INSTALL_ROOT}/ )
    endif()

    if (NOT ANDROID)
        INSTALL(TARGETS ${PROJECT_NAME} DESTINATION ${CMAKE_INSTALL_PREFIX}/bin )
        INSTALL(TARGETS ${NODE_CLI_TARGET} DESTINATION ${CMAKE_INSTALL_PREFIX}/bin )
        INSTALL(TARGETS ${NODE_TOOL_TARGET} DESTINATION ${CMAKE_INSTALL_PREFIX}/bin )
    endif()
    if (BUILD_DIAGTOOL)
            INSTALL(TARGETS cellframe-diagtool DESTINATION ${CMAKE_INSTALL_PREFIX}/bin )
    endif()

    if (NOT ANDROID)
    INSTALL(TARGETS cellframe-node-config DESTINATION ${CMAKE_INSTALL_PREFIX}/bin )
    endif()
endif()
INCLUDE(CPack)


