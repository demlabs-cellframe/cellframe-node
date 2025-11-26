cmake_minimum_required(VERSION 3.10)

project(cellframe-node C)
include(cellframe-sdk/cmake/ReadMKFile.cmake)
include(FetchContent)

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

# Option for weel download on-build
option(PYTHON_WHEELS_PREBUILD "Download wheels on build" OFF)
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
                -I ${CMAKE_SOURCE_DIR}/python-cellframe/include
                ${CMAKE_SOURCE_DIR}/conftool
                ${CMAKE_SOURCE_DIR}/dist.linux
                ${CMAKE_SOURCE_DIR}/dist
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

set(BUILD_WITH_GDB_DRIVER_MDBX ON)
if (NOT ANDROID)
    set(BUILD_WITH_GDB_DRIVER_SQLITE ON)
    #set(BUILD_WITH_GDB_DRIVER_PGSQL ON)
endif()
#set(BUILD_CELLFRAME_NODE_TESTS ON)
#set (BUILD_WITH_TPS_TEST ON)
if (BUILD_WITH_TPS_TEST)
    add_definitions("-DDAP_TPS_TEST")
endif()

set(BUILD_WITH_ZIP OFF)
option(SUPPORT_PYTHON_PLUGINS DEFAULT OFF)
option(ADD_UPDATER OFF)
#if(MACOS)
#    if(SUPPORT_PYTHON_PLUGINS)
#        set(BUILD_WITH_PYTHON_ENV ON)
#    endif()
#endif()

option(DAP_USE_RPMALLOC "Use 'rpmalloc' instead of std allocator" OFF)

if(LINUX)
    set(BUILD_WITH_PYTHON_ENV ON)
    set(SUPPORT_PYTHON_PLUGINS ON)
endif()


set(CELLFRAME_MODULES "core chains mining network srv cs-dag-poa cs-esbocs cs-none
                      srv-app srv-app-db srv-datum srv-stake srv-xchange srv-bridge srv-voting srv-stake-ext compose")

if(LINUX OR DARWIN)
    set(CELLFRAME_MODULES "${CELLFRAME_MODULES} srv-vpn")
endif()

if(BUILD_CELLFRAME_NODE_TESTS)
    set(DAPSDK_MODULES ${DAPSDK_MODULES} "test-framework")
    set(BUILD_CELLFRAME_SDK_TESTS ON)
endif()

# Enable DAP SDK tests when Cellframe SDK tests are enabled
if(BUILD_CELLFRAME_SDK_TESTS)
    set(BUILD_TESTS ON)
    set(DAPSDK_MODULES ${DAPSDK_MODULES} "test-framework")
    enable_testing()
    message(STATUS "Cellframe SDK tests enabled - CTest configured")
endif()

# activate sphincsplus flexible option
set(SPHINCSPLUS_FLEX ON)

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

    #if ( CPACK_DEBIAN_PACKAGE_ARCHITECTURE MATCHES "arm")
    #    SET( BUILD_WITH_PYTHON_ENV OFF )
    #endif()

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
    SET( CPACK_DEBIAN_PACKAGE_DEPENDS "dpkg (>=1.17), bash (>=4), less, pv, psmisc, logrotate, irqbalance, xz-utils")        
    #have to figure out how to use it properly with custom RPATH for python plugins...
    if (NOT SUPPORT_PYTHON_PLUGINS)
        SET( CPACK_DEBIAN_PACKAGE_SHLIBDEPS ON)
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

# Python support for armhf now available via python-build-standalone

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

    target_link_libraries(${NODE_CLI_TARGET} dap_chain_net dap_app_cli z pthread
            kernel32 user32 shell32 winmm gdi32 advapi32 ole32 version imm32
            oleaut32 ws2_32 ntdll psapi shlwapi bcrypt crypt32 secur32 userenv )
    set_property(TARGET ${NODE_CLI_TARGET} APPEND_STRING PROPERTY LINK_FLAGS "-mconsole")
    target_link_libraries(${NODE_TOOL_TARGET} cellframe-sdk )
    set_property(TARGET ${NODE_TOOL_TARGET} APPEND_STRING PROPERTY LINK_FLAGS "-mconsole")

    target_link_libraries(${PROJECT_NAME} cellframe-sdk dap_json-c )
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


add_subdirectory(conftool)

if(UNIX AND NOT WIN32)
    message ("[*] Unix library set")
    set_property(TARGET ${PROJECT_NAME} APPEND_STRING PROPERTY LINK_FLAGS "-D_GNU_SOURCE")
    set(NODE_LIBRARIES cellframe-sdk )

    set(NODE_CLI_LIBRARIES m cellframe-sdk)

    set(NODE_TOOL_LIBRARIES m cellframe-sdk)

    if (SUPPORT_PYTHON_PLUGINS)
        message("[+] Build with python plugins support")

        set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -DDAP_SUPPORT_PYTHON_PLUGINS")
        add_definitions("-DDAP_SUPPORT_PYTHON_PLUGINS")

        if (BUILD_WITH_PYTHON_ENV)
            
            set(PYTHON_URL "https://pub.cellframe.net/3rdparty/python/cpython310.tar.xz")

            if (CPACK_DEBIAN_PACKAGE_ARCHITECTURE STREQUAL "arm64")
                # python-build-standalone for ARM64 - requires only GLIBC 2.17, includes pip
                set(PYTHON_URL "https://pub.cellframe.net/3rdparty/python/cpython-3.10.9%2B20221220-aarch64-unknown-linux-gnu-install_only.tar.gz")
            elseif (CPACK_DEBIAN_PACKAGE_ARCHITECTURE STREQUAL "armhf")
                # python-build-standalone for ARM32 (armv7) - includes pip
                set(PYTHON_URL "https://pub.cellframe.net/3rdparty/python/cpython-3.10.19%2B20251031-armv7-unknown-linux-gnueabi-install_only.tar.gz")
            endif()
            add_definitions("-DPYTHON_VERSION=\"python3.10\"")

            if (DARWIN)
                if (CMAKE_SYSTEM_PROCESSOR MATCHES "arm")
                    set(PYTHON_URL "https://pub.cellframe.net/3rdparty/python/cpython-3.10.16+20250212-aarch64-apple-darwin-install_only.tar.gz")
                else ()
                    set(PYTHON_URL "https://pub.cellframe.net/3rdparty/python/cpython-3.10.16%2B20250205-x86_64-apple-darwin-install_only.tar.gz")
                endif()
                add_definitions("-DPYTHON_VERSION=\"python3.10\"")
            endif()

            message("[+] Build with python environment")
            message("    Downloading static prebuild cpython  ${PYTHON_URL}")
            #this python was build by compiling and installing static python distrip to /opt/cellframe-node/ and
            # installing pip in it, then tared all back.
            if(${CMAKE_VERSION} VERSION_GREATER_EQUAL "3.24")
                cmake_policy(SET CMP0135 NEW)
            endif()

            
            FetchContent_Declare(
                CPythonStatic
                URL ${PYTHON_URL}
            )
            FetchContent_MakeAvailable(CPythonStatic)
            set(cpythonstatic_SOURCE_DIR ${cpythonstatic_SOURCE_DIR})
            
            set(SAVED_CMAKE_MESSAGE_LOG_LEVEL ${CMAKE_MESSAGE_LOG_LEVEL})
            set(CMAKE_MESSAGE_LOG_LEVEL ERROR)
            set(CMAKE_MESSAGE_LOG_LEVEL ${SAVED_CMAKE_MESSAGE_LOG_LEVEL})

            # Determine the actual Python root directory (tarball may extract to nested path)
            # FetchContent may strip top-level dir or keep nested structure
            if(EXISTS "${cpythonstatic_SOURCE_DIR}/lib/libpython3.10.so")
                # Direct extraction (FetchContent strips top-level dir)
                set(PYTHON_ACTUAL_ROOT "${cpythonstatic_SOURCE_DIR}")
            elseif(EXISTS "${cpythonstatic_SOURCE_DIR}/python/lib/libpython3.10.so")
                # python-build-standalone nested structure
                set(PYTHON_ACTUAL_ROOT "${cpythonstatic_SOURCE_DIR}/python")
            elseif(EXISTS "${cpythonstatic_SOURCE_DIR}/opt/cellframe-node/python")
                set(PYTHON_ACTUAL_ROOT "${cpythonstatic_SOURCE_DIR}/opt/cellframe-node/python")
            else()
                set(PYTHON_ACTUAL_ROOT "${cpythonstatic_SOURCE_DIR}")
            endif()
            
            message("[*] Python extracted to: ${cpythonstatic_SOURCE_DIR}")
            message("[*] Python root dir set to: ${PYTHON_ACTUAL_ROOT}")
            message("[*] Host processor: ${CMAKE_HOST_SYSTEM_PROCESSOR}, Target processor: ${CMAKE_SYSTEM_PROCESSOR}")
            
            # Detect cross-compilation: compare host and target architectures
            set(IS_CROSS_COMPILING FALSE)
            if(CMAKE_CROSSCOMPILING)
                set(IS_CROSS_COMPILING TRUE)
            elseif(NOT CMAKE_HOST_SYSTEM_PROCESSOR STREQUAL CMAKE_SYSTEM_PROCESSOR)
                set(IS_CROSS_COMPILING TRUE)
            endif()
            
            if(IS_CROSS_COMPILING)
                # For cross-compilation, manually set Python paths (find_package fails to run target interpreter)
                message("[*] Cross-compilation detected - setting Python paths manually")
                set(Python_VERSION "3.10")
                set(Python_VERSION_MAJOR "3")
                set(Python_VERSION_MINOR "10")
                set(Python_INCLUDE_DIRS "${PYTHON_ACTUAL_ROOT}/include/python3.10")
                set(Python_LIBRARY_DIRS "${PYTHON_ACTUAL_ROOT}/lib")
                set(Python_LIBRARIES "${PYTHON_ACTUAL_ROOT}/lib/libpython3.10.so")
                
                if(NOT EXISTS "${Python_INCLUDE_DIRS}/Python.h")
                    message(FATAL_ERROR "Python.h not found at ${Python_INCLUDE_DIRS}/Python.h")
                endif()
                if(NOT EXISTS "${Python_LIBRARIES}")
                    message(FATAL_ERROR "Python library not found at ${Python_LIBRARIES}")
                endif()
                
                message("[*] Cross-compile: Using Python ${Python_VERSION} from ${PYTHON_ACTUAL_ROOT}")
            else()
                # Native build - use find_package
                message("[*] Native build detected - using find_package(Python)")
                list(APPEND CMAKE_PREFIX_PATH ${PYTHON_ACTUAL_ROOT})
                set(Python_ROOT_DIR ${PYTHON_ACTUAL_ROOT})
                set(Python_FIND_STRATEGY LOCATION)
                find_package(Python EXACT 3.10 COMPONENTS Development REQUIRED)
            endif()

            target_link_options(${NODE_TARGET} PUBLIC "-Wl,-rpath,${CMAKE_INSTALL_PREFIX}/python/lib/")

            add_definitions("-DDAP_BUILD_WITH_PYTHON_ENV")
        else()
            if(${CMAKE_VERSION} VERSION_GREATER_EQUAL "3.15")
                cmake_policy(SET CMP0094 NEW)
            endif()
            find_package(Python 3.8 COMPONENTS Interpreter Development REQUIRED)
            if(MACOS OR IOS)
                list(APPEND Python_LIBRARIES ssl crypto z util expat)
            elseif(LINUX OR BSD)
                if ( CPACK_DEBIAN_PACKAGE_ARCHITECTURE MATCHES "arm")
                    list(APPEND Python_LIBRARIES crypt nsl z util expat)
                else()
                    list(APPEND Python_LIBRARIES ssl crypto crypt nsl z util expat)
                endif()
            endif()
        endif()

        message("[*] Python version: " ${Python_VERSION})
        message("[*] Python path: " ${Python_EXECUTABLE})
        message("[*] Python includes path: " ${Python_INCLUDE_DIRS})
        message("[*] Python library path: " ${Python_LIBRARY_DIRS})
        message("[*] Python libraries: " "${Python_LIBRARIES}")

        include_directories(${Python_INCLUDE_DIRS} include/)
        add_subdirectory(python-cellframe)
#this helps
        #install_name_tool -change /install/lib/libpython3.10.dylib @executable_path/../../python/lib/libpython3.10.dylib ./build_osx_rwd/dist/Applications/CellframeNode.app/Contents/MacOS/cellframe-node
        list(APPEND NODE_LIBRARIES dap_plugins_python ${Python_LIBRARIES})
        if (DARWIN)
        add_custom_command(TARGET ${NODE_TARGET} 
            POST_BUILD COMMAND 
            ${CMAKE_INSTALL_NAME_TOOL} -change /install/lib/libpython3.10.dylib @executable_path/../Frameworks/python/lib/libpython3.10.dylib 
            ${NODE_TARGET})
        endif()
    endif()

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

if(WIN32 AND SUPPORT_PYTHON_PLUGINS)
    message("[+] Build with python plugins support (Windows)")

    set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -DDAP_SUPPORT_PYTHON_PLUGINS")
    add_definitions("-DDAP_SUPPORT_PYTHON_PLUGINS")

    if (BUILD_WITH_PYTHON_ENV)
        # python-build-standalone runtime provided by user
        set(PYTHON_URL "https://github.com/astral-sh/python-build-standalone/releases/download/20251120/cpython-3.10.19+20251120-x86_64-pc-windows-msvc-install_only.tar.gz")
        add_definitions("-DPYTHON_VERSION=\"python3.10\"")

        if(${CMAKE_VERSION} VERSION_GREATER_EQUAL "3.24")
            cmake_policy(SET CMP0135 NEW)
        endif()

        FetchContent_Declare(
            CPythonStaticWin
            URL ${PYTHON_URL}
        )
        FetchContent_MakeAvailable(CPythonStaticWin)
        set(cpythonstatic_SOURCE_DIR ${cpythonstaticwin_SOURCE_DIR})

        # Detect actual root in case of nested structure
        if(EXISTS "${cpythonstatic_SOURCE_DIR}/python")
            set(PYTHON_ACTUAL_ROOT "${cpythonstatic_SOURCE_DIR}/python")
        elseif(EXISTS "${cpythonstatic_SOURCE_DIR}/lib/python3.10")
            set(PYTHON_ACTUAL_ROOT "${cpythonstatic_SOURCE_DIR}")
        else()
            set(PYTHON_ACTUAL_ROOT "${cpythonstatic_SOURCE_DIR}")
        endif()

        message("[*] Python extracted to: ${cpythonstatic_SOURCE_DIR}")
        message("[*] Python root dir set to: ${PYTHON_ACTUAL_ROOT}")

        set(Python_VERSION "3.10")
        set(Python_VERSION_MAJOR "3")
        set(Python_VERSION_MINOR "10")
        set(Python_INCLUDE_DIRS "${PYTHON_ACTUAL_ROOT}/include")
        set(Python_LIBRARY_DIRS "${PYTHON_ACTUAL_ROOT}/libs")
        set(Python_LIBRARIES "${Python_LIBRARY_DIRS}/python310.lib")
        set(PYTHON_INCLUDE_DIR ${Python_INCLUDE_DIRS})
        set(PYTHON_LIBRARIES ${Python_LIBRARIES})

        add_definitions("-DDAP_BUILD_WITH_PYTHON_ENV")
    else()
        if(${CMAKE_VERSION} VERSION_GREATER_EQUAL "3.15")
            cmake_policy(SET CMP0094 NEW)
        endif()
        find_package(Python 3.10 COMPONENTS Interpreter Development REQUIRED)
        set(PYTHON_INCLUDE_DIR ${Python_INCLUDE_DIRS})
        set(PYTHON_LIBRARIES ${Python_LIBRARIES})
    endif()

    message("[*] Python version: " ${Python_VERSION})
    message("[*] Python includes path: " ${Python_INCLUDE_DIRS})
    message("[*] Python library path: " ${Python_LIBRARY_DIRS})
    message("[*] Python libraries: " "${Python_LIBRARIES}")

    include_directories(${Python_INCLUDE_DIRS} include/)
    add_subdirectory(python-cellframe)
    list(APPEND NODE_LIBRARIES dap_plugins_python ${Python_LIBRARIES})

    target_link_libraries(${PROJECT_NAME} dap_plugins_python ${Python_LIBRARIES})
    target_link_libraries(${NODE_CLI_TARGET} dap_plugins_python ${Python_LIBRARIES})
    target_link_libraries(${NODE_TOOL_TARGET} dap_plugins_python ${Python_LIBRARIES})
endif()

target_include_directories(${PROJECT_NAME} INTERFACE .)

if(NOT ANDROID)
    target_include_directories(${NODE_CLI_TARGET} INTERFACE .)
    target_include_directories(${NODE_TOOL_TARGET} INTERFACE .)
endif()

if(DARWIN)
    INSTALL(DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/dist/ DESTINATION ${SHAREDIR} FILES_MATCHING PATTERN "*"  PATTERN "*")
    INSTALL(TARGETS ${PROJECT_NAME} DESTINATION ${BINDIR} )
    INSTALL(TARGETS ${NODE_CLI_TARGET} DESTINATION ${BINDIR} )
    INSTALL(TARGETS ${NODE_TOOL_TARGET} DESTINATION ${BINDIR} )
    INSTALL(TARGETS cellframe-node-config DESTINATION ${BINDIR} )

    INSTALL(FILES ${CMAKE_CURRENT_SOURCE_DIR}/os/macos/com.demlabs.cellframe-node.plist DESTINATION ${SHAREDIR} )
    INSTALL(FILES ${CMAKE_CURRENT_SOURCE_DIR}/os/macos/Info.plist DESTINATION ${CONTENTSDIR} )

    if (BUILD_WITH_PYTHON_ENV)
    set(PYTHON_PIP "${cpythonstatic_SOURCE_DIR}/bin/pip3")
    set(PYTHON_BIN "${cpythonstatic_SOURCE_DIR}/bin/python3.10")
    set(PYTHON_LIB "${cpythonstatic_SOURCE_DIR}/lib/libpython3.10.dylib")
    set(PYTHON_LIB_DIR "${cpythonstatic_SOURCE_DIR}/lib/python3.10")
    set(PYTHON_LIB_DIR_PRFX "python3.10")
    
    INSTALL(FILES ${PYTHON_PIP} DESTINATION ${RLIBDIR}/python/bin/ )
    INSTALL(FILES ${PYTHON_BIN} DESTINATION ${RLIBDIR}/python/bin/ )
    INSTALL(FILES ${PYTHON_LIB} DESTINATION ${RLIBDIR}/python/lib/ )
    
    INSTALL(DIRECTORY ${PYTHON_LIB_DIR} DESTINATION ${RLIBDIR}/python/lib/ USE_SOURCE_PERMISSIONS)
    
    # Note: pycfhelpers and pycftools are installed as source packages on macOS
    # Wheel packages are not yet supported on macOS
    INSTALL(DIRECTORY python-cellframe/dists/python-modules/pycfhelpers DESTINATION ${RLIBDIR}/python/lib/${PYTHON_LIB_DIR_PRFX}/site-packages USE_SOURCE_PERMISSIONS)
    INSTALL(DIRECTORY python-cellframe/dists/python-modules/pycftools DESTINATION ${RLIBDIR}/python/lib/${PYTHON_LIB_DIR_PRFX}/site-packages USE_SOURCE_PERMISSIONS)
    INSTALL(DIRECTORY python-cellframe/dists/interfaces DESTINATION ${RLIBDIR}/python/lib/ USE_SOURCE_PERMISSIONS)
    endif()



else()

    INSTALL(DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/dist/ DESTINATION ${CMAKE_INSTALL_PREFIX} FILES_MATCHING PATTERN "*"  PATTERN "*")
    if(LINUX)
        
        #install all from dist.linux/share except updater files and node-serivice
        if(NOT ADD_UPDATER)
            INSTALL(DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/dist.linux/ DESTINATION ${CMAKE_INSTALL_PREFIX} PATTERN "*cellframe-updater*" EXCLUDE PATTERN "*cellframe-node*service*" EXCLUDE )
        else()
            INSTALL(DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/dist.linux/ DESTINATION ${CMAKE_INSTALL_PREFIX} PATTERN "*cellframe-node*service*" EXCLUDE)
        endif()

        #install node service depends on sanitasizes values
        if (DEFINED ENV{DAP_ASAN})
            INSTALL(FILES ${CMAKE_CURRENT_SOURCE_DIR}/dist.linux/share/cellframe-node.asan.service DESTINATION ${CMAKE_INSTALL_PREFIX}/share/ RENAME cellframe-node.service )
        elseif(DEFINED ENV{DAP_UBSAN})
            INSTALL(FILES ${CMAKE_CURRENT_SOURCE_DIR}/dist.linux/share/cellframe-node.ubsan.service DESTINATION ${CMAKE_INSTALL_PREFIX}/share/ RENAME cellframe-node.service )
        elseif(DEFINED ENV{DAP_TSAN})
            INSTALL(FILES ${CMAKE_CURRENT_SOURCE_DIR}/dist.linux/share/cellframe-node.tsan.service DESTINATION ${CMAKE_INSTALL_PREFIX}/share/ RENAME cellframe-node.service )
        else()
            INSTALL(FILES ${CMAKE_CURRENT_SOURCE_DIR}/dist.linux/share/cellframe-node.service DESTINATION ${CMAKE_INSTALL_PREFIX}/share/ RENAME cellframe-node.service )
        endif()
        
    elseif(BSD)
        INSTALL(DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/dist.bsd/ DESTINATION ${CMAKE_INSTALL_PREFIX} )
    endif()

    if(WIN32)
        INSTALL(FILES os/windows/cellframe-node.nsis DESTINATION . )
        INSTALL(FILES resources/cellframe.ico DESTINATION . )
        INSTALL(FILES resources/cellframe.bmp DESTINATION . )
    endif()

    if (NOT ANDROID)
        INSTALL(TARGETS ${PROJECT_NAME} DESTINATION ${CMAKE_INSTALL_PREFIX}/bin )
        INSTALL(TARGETS ${NODE_CLI_TARGET} DESTINATION ${CMAKE_INSTALL_PREFIX}/bin )
        INSTALL(TARGETS ${NODE_TOOL_TARGET} DESTINATION ${CMAKE_INSTALL_PREFIX}/bin )
    endif()

    if (NOT ANDROID)
    INSTALL(TARGETS cellframe-node-config DESTINATION ${CMAKE_INSTALL_PREFIX}/bin )
    endif()
    if(NOT ANDROID)
        #install all python-specific files back to its original location
        if (SUPPORT_PYTHON_PLUGINS AND BUILD_WITH_PYTHON_ENV)
            if(WIN32)
                set(PYTHON_BIN_DIR "${PYTHON_ACTUAL_ROOT}")
                set(PYTHON_STD_LIB "${PYTHON_ACTUAL_ROOT}/Lib")
                set(PYTHON_DLLS "${PYTHON_ACTUAL_ROOT}/DLLs")
                set(PYTHON_LIBS_DIR "${PYTHON_ACTUAL_ROOT}/libs")
                set(PYTHON_INCLUDE_DIR_WIN "${PYTHON_ACTUAL_ROOT}/include")
                set(PYTHON_ZIP "${PYTHON_ACTUAL_ROOT}/python310.zip")

                # Binaries and runtime DLLs (Windows layout expects DLLs next to exe)
                if(EXISTS "${PYTHON_BIN_DIR}/python.exe")
                    INSTALL(FILES "${PYTHON_BIN_DIR}/python.exe" DESTINATION ${CMAKE_INSTALL_PREFIX}/python/ RENAME python3.10.exe)
                    INSTALL(FILES "${PYTHON_BIN_DIR}/python.exe" DESTINATION ${CMAKE_INSTALL_PREFIX}/python/ RENAME python.exe)
                endif()
                if(EXISTS "${PYTHON_BIN_DIR}/python3.exe")
                    INSTALL(FILES "${PYTHON_BIN_DIR}/python3.exe" DESTINATION ${CMAKE_INSTALL_PREFIX}/python/)
                endif()
                if(EXISTS "${PYTHON_BIN_DIR}/pythonw.exe")
                    INSTALL(FILES "${PYTHON_BIN_DIR}/pythonw.exe" DESTINATION ${CMAKE_INSTALL_PREFIX}/python/)
                endif()

                if(EXISTS "${PYTHON_BIN_DIR}/python310.dll")
                    INSTALL(FILES "${PYTHON_BIN_DIR}/python310.dll" DESTINATION ${CMAKE_INSTALL_PREFIX}/bin/)
                    INSTALL(FILES "${PYTHON_BIN_DIR}/python310.dll" DESTINATION ${CMAKE_INSTALL_PREFIX}/python/)
                endif()
                if(EXISTS "${PYTHON_BIN_DIR}/python3.dll")
                    INSTALL(FILES "${PYTHON_BIN_DIR}/python3.dll" DESTINATION ${CMAKE_INSTALL_PREFIX}/bin/)
                    INSTALL(FILES "${PYTHON_BIN_DIR}/python3.dll" DESTINATION ${CMAKE_INSTALL_PREFIX}/python/)
                endif()
                if(EXISTS "${PYTHON_BIN_DIR}/vcruntime140.dll")
                    INSTALL(FILES "${PYTHON_BIN_DIR}/vcruntime140.dll" DESTINATION ${CMAKE_INSTALL_PREFIX}/bin/)
                    INSTALL(FILES "${PYTHON_BIN_DIR}/vcruntime140.dll" DESTINATION ${CMAKE_INSTALL_PREFIX}/python/)
                endif()
                if(EXISTS "${PYTHON_BIN_DIR}/vcruntime140_1.dll")
                    INSTALL(FILES "${PYTHON_BIN_DIR}/vcruntime140_1.dll" DESTINATION ${CMAKE_INSTALL_PREFIX}/bin/)
                    INSTALL(FILES "${PYTHON_BIN_DIR}/vcruntime140_1.dll" DESTINATION ${CMAKE_INSTALL_PREFIX}/python/)
                endif()
                if(EXISTS "${PYTHON_BIN_DIR}/vcruntime140_threads.dll")
                    INSTALL(FILES "${PYTHON_BIN_DIR}/vcruntime140_threads.dll" DESTINATION ${CMAKE_INSTALL_PREFIX}/bin/)
                    INSTALL(FILES "${PYTHON_BIN_DIR}/vcruntime140_threads.dll" DESTINATION ${CMAKE_INSTALL_PREFIX}/python/)
                endif()

                if(EXISTS "${PYTHON_LIBS_DIR}")
                    INSTALL(DIRECTORY ${PYTHON_LIBS_DIR}/ DESTINATION ${CMAKE_INSTALL_PREFIX}/python/libs/ USE_SOURCE_PERMISSIONS)
                endif()
                if(EXISTS "${PYTHON_INCLUDE_DIR_WIN}")
                    INSTALL(DIRECTORY ${PYTHON_INCLUDE_DIR_WIN}/ DESTINATION ${CMAKE_INSTALL_PREFIX}/python/include/ USE_SOURCE_PERMISSIONS)
                endif()

                if(EXISTS "${PYTHON_STD_LIB}")
                    INSTALL(DIRECTORY ${PYTHON_STD_LIB}/ DESTINATION ${CMAKE_INSTALL_PREFIX}/python/Lib/ USE_SOURCE_PERMISSIONS)
                endif()

                if(EXISTS "${PYTHON_DLLS}")
                    INSTALL(DIRECTORY ${PYTHON_DLLS}/ DESTINATION ${CMAKE_INSTALL_PREFIX}/python/DLLs/ USE_SOURCE_PERMISSIONS)
                endif()

                if(EXISTS "${PYTHON_ZIP}")
                    INSTALL(FILES "${PYTHON_ZIP}" DESTINATION ${CMAKE_INSTALL_PREFIX}/python/)
                endif()

                INSTALL(DIRECTORY python-cellframe/dists/interfaces DESTINATION ${CMAKE_INSTALL_PREFIX}/python/Lib/ USE_SOURCE_PERMISSIONS)

            else()

                # Use PYTHON_ACTUAL_ROOT which auto-detects correct path for any Python distribution
                set(PYTHON_PIP "${PYTHON_ACTUAL_ROOT}/bin/pip3")
                set(PYTHON_BIN "${PYTHON_ACTUAL_ROOT}/bin/python3.10")
                set(PYTHON_LIB "${PYTHON_ACTUAL_ROOT}/lib/libpython3.10.so.1.0")
                set(PYTHON_LIB_DIR "${PYTHON_ACTUAL_ROOT}/lib/python3.10")
                set(PYTHON_LIB_DIR_PRFX "python3.10")

                INSTALL(FILES ${PYTHON_PIP} DESTINATION ${CMAKE_INSTALL_PREFIX}/python/bin/ )
                INSTALL(FILES ${PYTHON_BIN} DESTINATION ${CMAKE_INSTALL_PREFIX}/python/bin/ )
                INSTALL(FILES ${PYTHON_LIB} DESTINATION ${CMAKE_INSTALL_PREFIX}/python/lib/ )
                
                INSTALL(DIRECTORY ${PYTHON_LIB_DIR} DESTINATION ${CMAKE_INSTALL_PREFIX}/python/lib/ USE_SOURCE_PERMISSIONS)
                
                # Download Python wheel files
                if(${CMAKE_VERSION} VERSION_GREATER_EQUAL "3.24")
                    cmake_policy(SET CMP0135 NEW)
                endif()
                
                
                            # Function to download and install wheel packages
                function(download_wheel_package PACKAGE_NAME PACKAGE_URL SUCCESS_VAR)
                    # Download wheel file with temporary name first
                    set(TEMP_WHEEL_PATH "${CMAKE_BINARY_DIR}/${PACKAGE_NAME}_temp.whl")
                    
                    message(STATUS "Downloading ${PACKAGE_NAME} from ${PACKAGE_URL}")
                    
                    # Download the wheel file (CMake will handle redirects automatically)
                    file(DOWNLOAD 
                        "${PACKAGE_URL}"
                        "${TEMP_WHEEL_PATH}"
                        SHOW_PROGRESS
                        INACTIVITY_TIMEOUT 30
                        TIMEOUT 300
                        STATUS DOWNLOAD_STATUS
                    )
                    
                    # Check download result
                    list(GET DOWNLOAD_STATUS 0 DOWNLOAD_RESULT)
                    if(DOWNLOAD_RESULT EQUAL 0)
                        # Read first few bytes to check if it's a valid wheel file
                        file(READ "${TEMP_WHEEL_PATH}" WHEEL_HEADER LIMIT 100)
                        
                        # Check if it starts with PK (zip file signature)
                        if(WHEEL_HEADER MATCHES "^PK")
                            # Extract filename from URL
                            string(REGEX MATCH "([^/]+\\.[^/]+)$" FILENAME_MATCH "${PACKAGE_URL}")
                            if(FILENAME_MATCH)
                                set(REAL_FILENAME "${FILENAME_MATCH}")
                                
                                # Check if filename matches pip wheel format (package-version-python-tag-platform.whl)
                                if(NOT "${REAL_FILENAME}" MATCHES "^[a-zA-Z0-9_-]+-[0-9]+\\.[0-9]+\\.[0-9]+.*\\.whl$")
                                    message(FATAL_ERROR "Wheel filename '${REAL_FILENAME}' does not match pip format. Expected: package-version-python-tag-platform.whl")
                                endif()
                            else()
                                message(FATAL_ERROR "Could not extract wheel filename from URL: ${PACKAGE_URL}")
                            endif()
                            
                            # Rename to final filename
                            set(FINAL_WHEEL_PATH "${CMAKE_BINARY_DIR}/${REAL_FILENAME}")
                            file(RENAME "${TEMP_WHEEL_PATH}" "${FINAL_WHEEL_PATH}")
                            
                            message(STATUS "Using filename: ${REAL_FILENAME}")
                            
                            # Install wheel file to wheels directory
                            INSTALL(FILES ${FINAL_WHEEL_PATH} DESTINATION ${CMAKE_INSTALL_PREFIX}/share/wheels/)
                            message(STATUS "Successfully downloaded and installed ${PACKAGE_NAME} as ${REAL_FILENAME}")
                            set(${SUCCESS_VAR} TRUE PARENT_SCOPE)
                        else()
                            message(WARNING "Downloaded file is not a valid wheel file (doesn't start with PK)")
                            file(REMOVE "${TEMP_WHEEL_PATH}")
                            set(${SUCCESS_VAR} FALSE PARENT_SCOPE)
                        endif()
                    else()
                        message(WARNING "Failed to download ${PACKAGE_NAME}")
                        set(${SUCCESS_VAR} FALSE PARENT_SCOPE)
                    endif()
                endfunction()

                # Download pycfhelpers wheel file/
                if(PYTHON_WHEELS_PREBUILD)
                   # Try to download wheel packages
                    message(STATUS "[WHEEL] Attempting to download Python wheel packages...")
                    download_wheel_package("pycfhelpers" "https://pub.cellframe.net/python/python-cellframe/pycfhelpers/master/pycfhelpers-1.0.3-py3-none-any.whl" PYCFHELPERS_SUCCESS)
                    # Download pycftools wheel file
                    download_wheel_package("pycftools" "https://pub.cellframe.net/python/python-cellframe/pycftools/master/pycftools-1.0.0-py3-none-any.whl" PYCFTOOLS_SUCCESS)
                            # Check if both packages downloaded successfully
                    if(PYCFHELPERS_SUCCESS AND PYCFTOOLS_SUCCESS)
                        message(STATUS "[WHEEL] All wheel packages downloaded successfully")
                    else()
                        message(FATAL_ERROR "[WHEEL] Failed to download required wheel packages. Build cannot continue.")
                    endif()
                else()
                    message(STATUS "[WHEEL] Skipping wheel packages download")
                endif()
                
                INSTALL(DIRECTORY python-cellframe/dists/interfaces DESTINATION ${CMAKE_INSTALL_PREFIX}/python/lib/ USE_SOURCE_PERMISSIONS)
            endif()

        endif()
    endif()


endif()
INCLUDE(CPack)
