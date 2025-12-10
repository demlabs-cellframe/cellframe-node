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

if(LINUX OR WIN32 OR DARWIN)
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

# =============================================================================
# Python plugins support (all platforms)
# =============================================================================
if(SUPPORT_PYTHON_PLUGINS)
    message("[+] Build with python plugins support")

    set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -DDAP_SUPPORT_PYTHON_PLUGINS")
    add_definitions("-DDAP_SUPPORT_PYTHON_PLUGINS")

    if(BUILD_WITH_PYTHON_ENV)
        # Select Python URL based on platform
        if(WIN32)
            set(PYTHON_URL "https://pub.cellframe.net/3rdparty/python/cpython-3.10.19%2B20251120-x86_64-pc-windows-msvc-install_only.tar.gz")
        elseif(DARWIN)
            # Check if building universal binary (arm64 + x86_64)
            string(FIND "${CMAKE_OSX_ARCHITECTURES}" "arm64" _has_arm64)
            string(FIND "${CMAKE_OSX_ARCHITECTURES}" "x86_64" _has_x86_64)
            
            if(_has_arm64 GREATER -1 AND _has_x86_64 GREATER -1)
                # Universal build - download both architectures and combine with lipo
                message("[*] Universal build detected (arm64 + x86_64)")
                message("[*] Will download both Python architectures and combine with lipo")
                set(PYTHON_UNIVERSAL_BUILD ON)
                set(PYTHON_URL_ARM64 "https://pub.cellframe.net/3rdparty/python/cpython-3.10.19+20251120-aarch64-apple-darwin-install_only.tar.gz")
                set(PYTHON_URL_X86_64 "https://pub.cellframe.net/3rdparty/python/cpython-3.10.19+20251120-x86_64-apple-darwin-install_only.tar.gz")
                # Use arm64 as primary for headers/stdlib, will lipo the dylib
                set(PYTHON_URL "${PYTHON_URL_ARM64}")
            elseif(CMAKE_SYSTEM_PROCESSOR MATCHES "arm" OR CMAKE_OSX_ARCHITECTURES MATCHES "arm64")
                set(PYTHON_URL "https://pub.cellframe.net/3rdparty/python/cpython-3.10.19+20251120-aarch64-apple-darwin-install_only.tar.gz")
            else()
                set(PYTHON_URL "https://pub.cellframe.net/3rdparty/python/cpython-3.10.19+20251120-x86_64-apple-darwin-install_only.tar.gz")
            endif()
        else()
            # Linux default
            set(PYTHON_URL "https://pub.cellframe.net/3rdparty/python/cpython310.tar.xz")
            if(CPACK_DEBIAN_PACKAGE_ARCHITECTURE STREQUAL "arm64")
                set(PYTHON_URL "https://pub.cellframe.net/3rdparty/python/cpython-3.10.9%2B20221220-aarch64-unknown-linux-gnu-install_only.tar.gz")
            elseif(CPACK_DEBIAN_PACKAGE_ARCHITECTURE STREQUAL "armhf")
                set(PYTHON_URL "https://pub.cellframe.net/3rdparty/python/cpython-3.10.19%2B20251010-armv7-unknown-linux-gnueabihf-install_only.tar.gz")
            endif()
        endif()
        add_definitions("-DPYTHON_VERSION=\"python3.10\"")

        message("[+] Build with python environment")
        message("    Downloading static prebuild cpython: ${PYTHON_URL}")

        if(${CMAKE_VERSION} VERSION_GREATER_EQUAL "3.24")
            cmake_policy(SET CMP0135 NEW)
        endif()

        FetchContent_Declare(CPythonStatic URL ${PYTHON_URL})
        FetchContent_MakeAvailable(CPythonStatic)
        
        # For universal builds, also download x86_64 Python and create fat binary
        if(PYTHON_UNIVERSAL_BUILD)
            message("[*] Downloading x86_64 Python for universal build...")
            FetchContent_Declare(CPythonStaticX86 URL ${PYTHON_URL_X86_64})
            FetchContent_MakeAvailable(CPythonStaticX86)
            set(PYTHON_X86_ROOT "${cpythonstaticx86_SOURCE_DIR}")
            message("[*] x86_64 Python downloaded to: ${PYTHON_X86_ROOT}")
            
            # Create universal dylib immediately (needed for linking)
            set(PYTHON_ARM64_DYLIB "${cpythonstatic_SOURCE_DIR}/lib/libpython3.10.dylib")
            set(PYTHON_X86_DYLIB "${PYTHON_X86_ROOT}/lib/libpython3.10.dylib")
            set(PYTHON_UNIVERSAL_DYLIB "${cpythonstatic_SOURCE_DIR}/lib/libpython3.10.universal.dylib")
            
            # Check if universal dylib already exists (from previous build)
            execute_process(
                COMMAND lipo -info "${PYTHON_ARM64_DYLIB}"
                OUTPUT_VARIABLE ARM64_LIPO_INFO
                ERROR_QUIET
            )
            
            if(ARM64_LIPO_INFO MATCHES "x86_64 arm64" OR ARM64_LIPO_INFO MATCHES "arm64 x86_64")
                message("[*] Universal Python dylib already exists, skipping lipo")
            else()
                # Verify we have different architectures before lipo
                execute_process(
                    COMMAND lipo -info "${PYTHON_X86_DYLIB}"
                    OUTPUT_VARIABLE X86_LIPO_INFO
                    ERROR_QUIET
                )
                
                if(ARM64_LIPO_INFO MATCHES "x86_64" AND X86_LIPO_INFO MATCHES "x86_64")
                    message(FATAL_ERROR "Both Python dylibs are x86_64! CMake cache is stale. Please delete build/_deps and reconfigure.")
                endif()
                
                if(ARM64_LIPO_INFO MATCHES "arm64" AND X86_LIPO_INFO MATCHES "arm64")
                    message(FATAL_ERROR "Both Python dylibs are arm64! CMake cache is stale. Please delete build/_deps and reconfigure.")
                endif()
                
                message("[*] Creating universal Python dylib with lipo...")
                execute_process(
                    COMMAND lipo -create "${PYTHON_ARM64_DYLIB}" "${PYTHON_X86_DYLIB}" -output "${PYTHON_UNIVERSAL_DYLIB}"
                    RESULT_VARIABLE LIPO_RESULT
                )
                
                if(NOT LIPO_RESULT EQUAL 0)
                    message(FATAL_ERROR "Failed to create universal Python dylib with lipo")
                endif()
                
                # Replace the original dylib with universal one for linking
                file(RENAME "${PYTHON_ARM64_DYLIB}" "${cpythonstatic_SOURCE_DIR}/lib/libpython3.10.arm64.dylib")
                file(RENAME "${PYTHON_UNIVERSAL_DYLIB}" "${PYTHON_ARM64_DYLIB}")
                message("[*] Universal Python dylib created and installed for linking")
                
                # Also backup arm64 python executable for later lipo
                if(EXISTS "${cpythonstatic_SOURCE_DIR}/bin/python3.10")
                    file(RENAME "${cpythonstatic_SOURCE_DIR}/bin/python3.10" "${cpythonstatic_SOURCE_DIR}/bin/python3.10.arm64")
                endif()
            endif()
            
            # Verify it's universal
            execute_process(
                COMMAND lipo -info "${PYTHON_ARM64_DYLIB}"
                OUTPUT_VARIABLE LIPO_INFO
            )
            message("[*] Python dylib info: ${LIPO_INFO}")
            
            if(NOT LIPO_INFO MATCHES "x86_64" OR NOT LIPO_INFO MATCHES "arm64")
                message(WARNING "Python dylib may not be universal! Info: ${LIPO_INFO}")
            endif()
        endif()

        # Determine the actual Python root directory (tarball may extract to nested path)
        if(WIN32)
            if(EXISTS "${cpythonstatic_SOURCE_DIR}/python")
                set(PYTHON_ACTUAL_ROOT "${cpythonstatic_SOURCE_DIR}/python")
            elseif(EXISTS "${cpythonstatic_SOURCE_DIR}/libs/python310.lib")
                set(PYTHON_ACTUAL_ROOT "${cpythonstatic_SOURCE_DIR}")
            else()
                set(PYTHON_ACTUAL_ROOT "${cpythonstatic_SOURCE_DIR}")
            endif()
        else()
            if(EXISTS "${cpythonstatic_SOURCE_DIR}/lib/libpython3.10.so" OR EXISTS "${cpythonstatic_SOURCE_DIR}/lib/libpython3.10.dylib")
                set(PYTHON_ACTUAL_ROOT "${cpythonstatic_SOURCE_DIR}")
            elseif(EXISTS "${cpythonstatic_SOURCE_DIR}/python/lib/libpython3.10.so")
                set(PYTHON_ACTUAL_ROOT "${cpythonstatic_SOURCE_DIR}/python")
            elseif(EXISTS "${cpythonstatic_SOURCE_DIR}/opt/cellframe-node/python")
                set(PYTHON_ACTUAL_ROOT "${cpythonstatic_SOURCE_DIR}/opt/cellframe-node/python")
            else()
                set(PYTHON_ACTUAL_ROOT "${cpythonstatic_SOURCE_DIR}")
            endif()
        endif()

        message("[*] Python extracted to: ${cpythonstatic_SOURCE_DIR}")
        message("[*] Python root dir set to: ${PYTHON_ACTUAL_ROOT}")

        # Set Python paths based on platform
        set(Python_VERSION "3.10")
        set(Python_VERSION_MAJOR "3")
        set(Python_VERSION_MINOR "10")

        if(WIN32)
            set(Python_INCLUDE_DIRS "${PYTHON_ACTUAL_ROOT}/include")
            set(Python_LIBRARY_DIRS "${PYTHON_ACTUAL_ROOT}/libs")
            # For MinGW cross-compilation, link directly with DLL (not MSVC .lib)
            if(MINGW OR CMAKE_CROSSCOMPILING)
                set(Python_LIBRARIES "${PYTHON_ACTUAL_ROOT}/python310.dll")
            else()
                set(Python_LIBRARIES "${Python_LIBRARY_DIRS}/python310.lib")
            endif()
        else()
            # Unix: check for cross-compilation
            message("[*] Host processor: ${CMAKE_HOST_SYSTEM_PROCESSOR}, Target processor: ${CMAKE_SYSTEM_PROCESSOR}")
            set(IS_CROSS_COMPILING FALSE)
            if(CMAKE_CROSSCOMPILING OR NOT CMAKE_HOST_SYSTEM_PROCESSOR STREQUAL CMAKE_SYSTEM_PROCESSOR)
                set(IS_CROSS_COMPILING TRUE)
            endif()

            if(IS_CROSS_COMPILING)
                message("[*] Cross-compilation detected - setting Python paths manually")
                set(Python_INCLUDE_DIRS "${PYTHON_ACTUAL_ROOT}/include/python3.10")
                set(Python_LIBRARY_DIRS "${PYTHON_ACTUAL_ROOT}/lib")
                set(Python_LIBRARIES "${PYTHON_ACTUAL_ROOT}/lib/libpython3.10.so")

                if(NOT EXISTS "${Python_INCLUDE_DIRS}/Python.h")
                    message(FATAL_ERROR "Python.h not found at ${Python_INCLUDE_DIRS}/Python.h")
                endif()
                if(NOT EXISTS "${Python_LIBRARIES}")
                    message(FATAL_ERROR "Python library not found at ${Python_LIBRARIES}")
                endif()
            else()
                message("[*] Native build detected - using find_package(Python)")
                list(APPEND CMAKE_PREFIX_PATH ${PYTHON_ACTUAL_ROOT})
                set(Python_ROOT_DIR ${PYTHON_ACTUAL_ROOT})
                set(Python_FIND_STRATEGY LOCATION)
                find_package(Python EXACT 3.10 COMPONENTS Development REQUIRED)
            endif()

            # Set rpath for Unix
            target_link_options(${NODE_TARGET} PUBLIC "-Wl,-rpath,\$ORIGIN/../python/lib:${CMAKE_INSTALL_PREFIX}/python/lib")
        endif()

        add_definitions("-DDAP_BUILD_WITH_PYTHON_ENV")
    else()
        # Use system Python
        if(${CMAKE_VERSION} VERSION_GREATER_EQUAL "3.15")
            cmake_policy(SET CMP0094 NEW)
        endif()
        if(WIN32)
            find_package(Python 3.10 COMPONENTS Interpreter Development REQUIRED)
        else()
            find_package(Python 3.8 COMPONENTS Interpreter Development REQUIRED)
            if(MACOS OR IOS)
                list(APPEND Python_LIBRARIES ssl crypto z util expat)
            elseif(LINUX OR BSD)
                if(CPACK_DEBIAN_PACKAGE_ARCHITECTURE MATCHES "arm")
                    list(APPEND Python_LIBRARIES crypt nsl z util expat)
                else()
                    list(APPEND Python_LIBRARIES ssl crypto crypt nsl z util expat)
                endif()
            endif()
        endif()
    endif()

    message("[*] Python version: ${Python_VERSION}")
    message("[*] Python includes path: ${Python_INCLUDE_DIRS}")
    message("[*] Python library path: ${Python_LIBRARY_DIRS}")
    message("[*] Python libraries: ${Python_LIBRARIES}")

    include_directories(${Python_INCLUDE_DIRS} include/)
    add_subdirectory(python-cellframe)

    if(DARWIN)
        # Fix Python library path to use proper framework structure
        add_custom_command(TARGET ${NODE_TARGET}
            POST_BUILD COMMAND
            ${CMAKE_INSTALL_NAME_TOOL} -change /install/lib/libpython3.10.dylib @executable_path/../Frameworks/Python.framework/Versions/3.10/Python
            $<TARGET_FILE:${NODE_TARGET}>)
    endif()
endif()

# =============================================================================
# Platform-specific linking
# =============================================================================
if(UNIX AND NOT WIN32)
    message("[*] Unix library set")
    set_property(TARGET ${PROJECT_NAME} APPEND_STRING PROPERTY LINK_FLAGS "-D_GNU_SOURCE")
    set(NODE_LIBRARIES cellframe-sdk)
    set(NODE_CLI_LIBRARIES m cellframe-sdk)
    set(NODE_TOOL_LIBRARIES m cellframe-sdk)

    # Add libatomic for 32-bit ARM (required for 64-bit atomic operations)
    if(CMAKE_SYSTEM_PROCESSOR MATCHES "^arm" AND NOT CMAKE_SYSTEM_PROCESSOR MATCHES "aarch64")
        message("[*] 32-bit ARM detected, adding libatomic")
        list(APPEND NODE_LIBRARIES atomic)
        list(APPEND NODE_CLI_LIBRARIES atomic)
        list(APPEND NODE_TOOL_LIBRARIES atomic)
    endif()

    if(SUPPORT_PYTHON_PLUGINS)
        list(APPEND NODE_LIBRARIES dap_plugins_python ${Python_LIBRARIES})
    endif()

    if(ANDROID)
        set(ALL_LIBRARIES ${NODE_LIBRARIES} ${NODE_CLI_LIBRARIES} ${NODE_TOOL_LIBRARIES} log)
        list(REMOVE_DUPLICATES ALL_LIBRARIES)
        target_link_libraries(${NODE_TARGET} ${ALL_LIBRARIES})
    else()
        target_link_libraries(${NODE_TARGET} ${NODE_LIBRARIES} pthread)
        target_link_libraries(${NODE_CLI_TARGET} ${NODE_CLI_LIBRARIES} pthread)
        target_link_libraries(${NODE_TOOL_TARGET} ${NODE_TOOL_LIBRARIES} pthread)
    endif()
endif()

if(WIN32 AND SUPPORT_PYTHON_PLUGINS)
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
        # =============================================================================
        # Python.framework structure for macOS (Apple-compliant framework bundle)
        # =============================================================================
        # Structure:
        #   Python.framework/
        #   ├── Python              -> Versions/Current/Python
        #   ├── Resources           -> Versions/Current/Resources
        #   └── Versions/
        #       ├── Current         -> 3.10
        #       └── 3.10/
        #           ├── Python      (the dylib)
        #           ├── Resources/
        #           │   └── Info.plist
        #           ├── bin/
        #           ├── include/
        #           └── lib/
        #               └── python3.10/
        # =============================================================================
        
        set(PYTHON_FRAMEWORK_DIR "${RLIBDIR}/Python.framework")
        set(PYTHON_VERSION_DIR "${PYTHON_FRAMEWORK_DIR}/Versions/3.10")
        
        set(PYTHON_PIP "${cpythonstatic_SOURCE_DIR}/bin/pip3")
        set(PYTHON_BIN "${cpythonstatic_SOURCE_DIR}/bin/python3.10")
        set(PYTHON_LIB "${cpythonstatic_SOURCE_DIR}/lib/libpython3.10.dylib")
        set(PYTHON_LIB_DIR "${cpythonstatic_SOURCE_DIR}/lib/python3.10")
        set(PYTHON_INCLUDE_DIR_SRC "${cpythonstatic_SOURCE_DIR}/include/python3.10")
        
        # For universal builds, the universal dylib was already created during configure phase
        # Just copy it and the executables
        if(PYTHON_UNIVERSAL_BUILD)
            # The universal dylib is already at PYTHON_LIB (we replaced it during configure)
            INSTALL(FILES ${PYTHON_LIB} DESTINATION ${PYTHON_VERSION_DIR} RENAME Python)
            
            # For python executable, create universal from both archs
            set(PYTHON_BIN_ARM64 "${cpythonstatic_SOURCE_DIR}/bin/python3.10.arm64")
            set(PYTHON_BIN_X86 "${PYTHON_X86_ROOT}/bin/python3.10")
            
            # Create universal python3.10 executable using lipo
            INSTALL(CODE "
                message(STATUS \"Creating universal Python executable...\")
                set(ARM64_BIN \"${PYTHON_BIN_ARM64}\")
                set(X86_BIN \"${PYTHON_BIN_X86}\")
                set(OUTPUT_BIN \"\$ENV{DESTDIR}${PYTHON_VERSION_DIR}/bin/python3.10\")
                
                file(MAKE_DIRECTORY \"\$ENV{DESTDIR}${PYTHON_VERSION_DIR}/bin\")
                
                execute_process(
                    COMMAND lipo -create \"\${ARM64_BIN}\" \"\${X86_BIN}\" -output \"\${OUTPUT_BIN}\"
                    RESULT_VARIABLE LIPO_RESULT
                )
                
                if(NOT LIPO_RESULT EQUAL 0)
                    message(STATUS \"lipo failed, copying single arch python executable\")
                    file(COPY \"\${ARM64_BIN}\" DESTINATION \"\$ENV{DESTDIR}${PYTHON_VERSION_DIR}/bin/\")
                else()
                    message(STATUS \"Universal Python executable created\")
                endif()
                
                # Set executable permissions
                file(CHMOD \"\${OUTPUT_BIN}\" 
                    PERMISSIONS OWNER_READ OWNER_WRITE OWNER_EXECUTE GROUP_READ GROUP_EXECUTE WORLD_READ WORLD_EXECUTE)
            ")
        else()
            # Single architecture - just copy the dylib
            INSTALL(FILES ${PYTHON_LIB} DESTINATION ${PYTHON_VERSION_DIR} RENAME Python)
            
            # Install Python executables (single arch)
            INSTALL(FILES ${PYTHON_BIN} DESTINATION ${PYTHON_VERSION_DIR}/bin/ 
                    PERMISSIONS OWNER_READ OWNER_WRITE OWNER_EXECUTE GROUP_READ GROUP_EXECUTE WORLD_READ WORLD_EXECUTE)
        endif()
        
        # Install pip (no need to lipo, it's a script)
        INSTALL(FILES ${PYTHON_PIP} DESTINATION ${PYTHON_VERSION_DIR}/bin/ 
                PERMISSIONS OWNER_READ OWNER_WRITE OWNER_EXECUTE GROUP_READ GROUP_EXECUTE WORLD_READ WORLD_EXECUTE)
        
        # Install Python standard library
        INSTALL(DIRECTORY ${PYTHON_LIB_DIR} DESTINATION ${PYTHON_VERSION_DIR}/lib/ USE_SOURCE_PERMISSIONS)
        
        # Install Python headers
        if(EXISTS "${PYTHON_INCLUDE_DIR_SRC}")
            INSTALL(DIRECTORY ${PYTHON_INCLUDE_DIR_SRC} DESTINATION ${PYTHON_VERSION_DIR}/include/ USE_SOURCE_PERMISSIONS)
        endif()
        
        # Install Framework Info.plist
        INSTALL(FILES ${CMAKE_CURRENT_SOURCE_DIR}/os/macos/Python.framework.Info.plist 
                DESTINATION ${PYTHON_VERSION_DIR}/Resources/ RENAME Info.plist)
        
        # Install interfaces
        INSTALL(DIRECTORY python-cellframe/dists/interfaces 
                DESTINATION ${PYTHON_VERSION_DIR}/Resources/ USE_SOURCE_PERMISSIONS)
        
        # Create framework symlinks (required for proper framework structure)
        # These are created during install phase
        INSTALL(CODE "
            message(STATUS \"Creating Python.framework symlinks...\")
            set(FW_DIR \"\$ENV{DESTDIR}${PYTHON_FRAMEWORK_DIR}\")
            set(VER_DIR \"\${FW_DIR}/Versions/3.10\")
            
            # Create Versions/Current -> 3.10
            execute_process(COMMAND \${CMAKE_COMMAND} -E create_symlink 
                \"3.10\" \"\${FW_DIR}/Versions/Current\")
            
            # Create Python -> Versions/Current/Python
            execute_process(COMMAND \${CMAKE_COMMAND} -E create_symlink 
                \"Versions/Current/Python\" \"\${FW_DIR}/Python\")
            
            # Create Resources -> Versions/Current/Resources
            execute_process(COMMAND \${CMAKE_COMMAND} -E create_symlink 
                \"Versions/Current/Resources\" \"\${FW_DIR}/Resources\")
            
            message(STATUS \"Python.framework symlinks created\")
        ")
        
        # Fix install_name in Python dylib (required for proper linking)
        INSTALL(CODE "
            message(STATUS \"Fixing Python dylib install_name...\")
            set(PYTHON_DYLIB \"\$ENV{DESTDIR}${PYTHON_VERSION_DIR}/Python\")
            
            # Change install_name from /install/lib/libpython3.10.dylib to framework path
            execute_process(
                COMMAND install_name_tool -id 
                    \"@rpath/Python.framework/Versions/3.10/Python\"
                    \"\${PYTHON_DYLIB}\"
                RESULT_VARIABLE INSTALL_NAME_RESULT
            )
            
            if(NOT INSTALL_NAME_RESULT EQUAL 0)
                message(WARNING \"Failed to fix Python dylib install_name\")
            else()
                message(STATUS \"Python dylib install_name fixed\")
            endif()
        ")
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
        INSTALL(FILES os/windows/cellframe-node.nsis DESTINATION ${CMAKE_INSTALL_ROOT}/ )
        INSTALL(FILES resources/cellframe.ico DESTINATION ${CMAKE_INSTALL_ROOT}/ )
        INSTALL(FILES resources/cellframe.bmp DESTINATION ${CMAKE_INSTALL_ROOT}/ )
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
            # Platform-specific Python installation
            if(WIN32)
                set(PYTHON_BIN_DIR "${PYTHON_ACTUAL_ROOT}")
                set(PYTHON_STD_LIB "${PYTHON_ACTUAL_ROOT}/Lib")
                set(PYTHON_DLLS "${PYTHON_ACTUAL_ROOT}/DLLs")
                set(PYTHON_LIBS_DIR "${PYTHON_ACTUAL_ROOT}/libs")
                set(PYTHON_INCLUDE_DIR_WIN "${PYTHON_ACTUAL_ROOT}/include")
                set(PYTHON_ZIP "${PYTHON_ACTUAL_ROOT}/python310.zip")
                set(PYTHON_INTERFACES_DIR "${CMAKE_INSTALL_PREFIX}/python/Lib")

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
            else()
                # Unix: Use PYTHON_ACTUAL_ROOT which auto-detects correct path for any Python distribution
                set(PYTHON_PIP "${PYTHON_ACTUAL_ROOT}/bin/pip3")
                set(PYTHON_BIN "${PYTHON_ACTUAL_ROOT}/bin/python3.10")
                set(PYTHON_LIB "${PYTHON_ACTUAL_ROOT}/lib/libpython3.10.so.1.0")
                set(PYTHON_LIB_DIR "${PYTHON_ACTUAL_ROOT}/lib/python3.10")
                set(PYTHON_INTERFACES_DIR "${CMAKE_INSTALL_PREFIX}/python/lib")

                INSTALL(FILES ${PYTHON_PIP} DESTINATION ${CMAKE_INSTALL_PREFIX}/python/bin/)
                INSTALL(FILES ${PYTHON_BIN} DESTINATION ${CMAKE_INSTALL_PREFIX}/python/bin/)
                INSTALL(FILES ${PYTHON_LIB} DESTINATION ${CMAKE_INSTALL_PREFIX}/python/lib/)

                # Create symlinks for libpython (required for runtime library loading)
                INSTALL(CODE "execute_process(COMMAND ${CMAKE_COMMAND} -E create_symlink libpython3.10.so.1.0 \$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/python/lib/libpython3.10.so.1)")
                INSTALL(CODE "execute_process(COMMAND ${CMAKE_COMMAND} -E create_symlink libpython3.10.so.1.0 \$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/python/lib/libpython3.10.so)")

                INSTALL(DIRECTORY ${PYTHON_LIB_DIR} DESTINATION ${CMAKE_INSTALL_PREFIX}/python/lib/ USE_SOURCE_PERMISSIONS)
            endif()

            # Common: Install interfaces (path set per-platform above)
            INSTALL(DIRECTORY python-cellframe/dists/interfaces DESTINATION ${PYTHON_INTERFACES_DIR}/ USE_SOURCE_PERMISSIONS)
        endif()
    endif()


endif()
INCLUDE(CPack)
