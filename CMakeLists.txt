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

#enable for diagtool 
#set(BUILD_DIAGTOOL OFF)

#possible need be setted during crosscompile
#by default it uses dpkg --print-architecture
#we ok with it on native builds.
#SET( CPACK_PACKAGE_ARCHITECTURE "${CMAKE_SYSTEM_PROCESSOR}")
#SET( CPACK_DEBIAN_PACKAGE_ARCHITECTURE "${CMAKE_SYSTEM_PROCESSOR}")

# init CellFrame SDK
add_definitions("-DDAP_VERSION=\"${CPACK_PACKAGE_VERSION_MAJOR}-${CPACK_PACKAGE_VERSION_MINOR}.${CPACK_PACKAGE_VERSION_PATCH}\"")
set(SUBMODULES_NO_BUILD ON)
include (cellframe-sdk/cmake/OS_Detection.cmake)

if (WIN32)
    set(BUILD_WITH_GDB_DRIVER_MDBX OFF)
else()
    set(BUILD_WITH_GDB_DRIVER_MDBX ON)
endif()
#set(BUILD_WITH_GDB_DRIVER_PGSQL ON)
#set(BUILD_CRYPTO_TESTS ON)

set(BUILD_WITH_ZIP OFF)


if(LINUX)
    #set(BUILD_WITH_PYTHON_ENV ON)
    set(SUPPORT_PYTHON_PLUGINS ON)
    option(CREATE_DEFAULT_CONFIG "Create default configuration files" ON) # Optional config files creation
    if (CREATE_DEFAULT_CONFIG)
        message("[*] Generating default configuration for ${PROJECT_NAME}, skip with -DCREATE_DEFAULT_CONFIG=OFF")
    endif()
endif()


set(CELLFRAME_MODULES "core chains mining network srv cs-dag-poa cs-block-poa cs-dag-pos cs-block-pos cs-block-ton cs-none srv-app srv-app-db srv-datum srv-stake-pos-delegate srv-stake-lock srv-xchange")

if(LINUX)
    set(CELLFRAME_MODULES "${CELLFRAME_MODULES} modules-dynamic srv-vpn")
endif()
if(MACOS)
    set(CELLFRAME_MODULES "${CELLFRAME_MODULES} srv-vpn")
endif()

add_subdirectory(cellframe-sdk)

if (CELLFRAME_MODULES MATCHES "modules-dynamic")
    add_definitions("-DDAP_MODULES_DYNAMIC")
endif()

SET(CMAKE_INSTALL_PREFIX "/opt/${PROJECT_NAME}")
SET(CPACK_INSTALL_PREFIX "/opt/${PROJECT_NAME}")
SET(DESTDIR "/opt/${PROJECT_NAME}")

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

    if(BUILD_WITH_GDB_DRIVER_PGSQL)
	SET( CPACK_PACKAGE_VERSION "${CPACK_PACKAGE_VERSION}-pgsql" )
    endif()
    if(CMAKE_BUILD_TYPE MATCHES Debug)
	SET( CPACK_PACKAGE_VERSION "${CPACK_PACKAGE_VERSION}-dbg" )
    endif()
    if(CMAKE_BUILD_TYPE MATCHES RelWithDebInfo)
	SET( CPACK_PACKAGE_VERSION "${CPACK_PACKAGE_VERSION}-rwd" )
    endif()
    SET( CPACK_DEBIAN_PACKAGE_MAINTAINER "Dmitriy Gerasimov <naeper@demlabs.net>" )
    SET( CPACK_DEBIAN_PACKAGE_DESCRIPTION_SUMMARY "CellFrame Node software https://cellframe.net" )
    SET( CPACK_DEBIAN_PACKAGE_DESCRIPTION   "CellFrame Node" )
    SET( CPACK_DEBIAN_PACKAGE_SECTION "extra")
    SET( CPACK_DEBIAN_PACKAGE_DEPENDS "debconf (>=1.5), dpkg (>=1.17), bash (>=4), debconf-utils, dconf-cli, less, pv, psmisc, logrotate, irqbalance, xz-utils")
    SET( CPACK_DEBIAN_PACKAGE_BREAKS "cellframe-dashboard" )

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
	                kernel32 user32 shell32 winmm gdi32 advapi32 ole32 version imm32
			oleaut32 ws2_32 ntdll psapi shlwapi bcrypt crypt32 secur32 userenv )
    set_property(TARGET ${NODE_CLI_TARGET} APPEND_STRING PROPERTY LINK_FLAGS "-mconsole")
    target_link_libraries(${NODE_TOOL_TARGET} cellframe-sdk )
    set_property(TARGET ${NODE_TOOL_TARGET} APPEND_STRING PROPERTY LINK_FLAGS "-mconsole")

    target_link_libraries(${PROJECT_NAME} cellframe-sdk json-c )
    set_property(TARGET ${PROJECT_NAME} APPEND_STRING PROPERTY LINK_FLAGS "-mwindows")


endif()
if(BSD)
    set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -L /usr/local/lib ")
    set(CMAKE_LINKER_FLAGS "${CMAKE_LINKER_FLAGS} -L /usr/local/lib")
endif()

if(UNIX AND NOT WIN32)
    message ("[*] Unix library set")
    set_property(TARGET ${PROJECT_NAME} APPEND_STRING PROPERTY LINK_FLAGS "-D_GNU_SOURCE")
    set(NODE_LIBRARIES cellframe-sdk )

    set(NODE_CLI_LIBRARIES m cellframe-sdk)

    set(NODE_TOOL_LIBRARIES m cellframe-sdk)
    
    if(BUILD_DIAGTOOL)
        message("[*] Diagtool build on")
        add_subdirectory(diagtool)
    endif()

    if (SUPPORT_PYTHON_PLUGINS)
	message("[+] Build with python plugins support")

	set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -DDAP_SUPPORT_PYTHON_PLUGINS")
	add_definitions("-DDAP_SUPPORT_PYTHON_PLUGINS")

	if (BUILD_WITH_PYTHON_ENV)

	    message("[+] Build with python environment")
	    message("    Downloading static prebuild cpython3.7...")
	    #this python was build by compiling and installing static python distrip to /opt/cellframe-node/ and
	    # installing pip in it, then tared all back.
	    FetchContent_Declare(
		CPython37Static
		URL      https://pub.cellframe.net/3rdparty/python/cpython.tar.xz
		)

            FetchContent_MakeAvailable(CPython37Static)
            
            SET(OPENSSL_ARCHIVE_URL https://pub.cellframe.net/3rdparty/python/openssl-1.1.1o.tar.gz)
            add_subdirectory(cellframe-sdk/3rdparty/openssl-cmake)
            add_dependencies(${NODE_TARGET} ssl_lib crypto_lib)

	    set(CMAKE_PREFIX_PATH ${cpython37static_SOURCE_DIR})

	    set(Python_ADDITIONAL_VERSIONS 3.7)
	    find_package(PythonLibs REQUIRED)

	    add_definitions("-DDAP_BUILD_WITH_PYTHON_ENV")
	    set(PYTHON_LIBRARIES  ${PYTHON_LIBRARIES} ssl_lib crypto_lib -lcrypt -lnsl -lz -lutil -lexpat )

	else()
	    set(Python_ADDITIONAL_VERSION 3.9 3.8 3.7 3.6 3.5 3.4)
	    find_package(PythonLibs REQUIRED)
	endif()

	include_directories(${PYTHON_INCLUDE_DIR} include/)
	add_subdirectory(python-cellframe)

	set(NODE_LIBRARIES ${NODE_LIBRARIES}  dap_plugins_python ${PYTHON_LIBRARIES})
    endif()

    if(ANDROID )
	set(ALL_LIBRARIES ${NODE_LIBRARIES} ${NODE_CLI_LIBRARIES} ${NODE_TOOL_LIBRARIES} log)

	list(REMOVE_DUPLICATES ALL_LIBRARIES)

	target_link_libraries(${NODE_TARGET} ${ALL_LIBRARIES})
    else()
	target_link_libraries(${NODE_TARGET}      ${NODE_LIBRARIES} pthread z util expat )
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
    INSTALL(TARGETS ${PROJECT_NAME} DESTINATION ${BINDIR} )
    INSTALL(TARGETS ${NODE_CLI_TARGET} DESTINATION ${BINDIR} )
    INSTALL(TARGETS ${NODE_TOOL_TARGET} DESTINATION ${BINDIR} )

    INSTALL(FILES ${CMAKE_CURRENT_SOURCE_DIR}/os/macos/com.demlabs.cellframe-node.plist DESTINATION ${SHAREDIR} )
    INSTALL(DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/scripts/ DESTINATION ${SHAREDIR} FILES_MATCHING PATTERN "*"  PATTERN "*" PERMISSIONS OWNER_EXECUTE;OWNER_READ;OWNER_WRITE;WORLD_READ;GROUP_READ )
    INSTALL(DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/scripts.darwin/ DESTINATION ${SHAREDIR} FILES_MATCHING PATTERN "*"  PATTERN "*" PERMISSIONS OWNER_EXECUTE;OWNER_READ;OWNER_WRITE;WORLD_READ;GROUP_READ )
else()

    INSTALL(DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/dist/ DESTINATION ${CMAKE_INSTALL_PREFIX} FILES_MATCHING PATTERN "*"  PATTERN "*")
    if(LINUX)
	    INSTALL(DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/dist.linux/ DESTINATION ${CMAKE_INSTALL_PREFIX} FILES_MATCHING PATTERN "*"  PATTERN "*")
        if (CREATE_DEFAULT_CONFIG)
            INSTALL(CODE "execute_process(COMMAND ${CMAKE_CURRENT_SOURCE_DIR}/scripts/create_default_config.sh ${DESTDIR})")
        endif()
    elseif(BSD)
	    INSTALL(DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/dist.bsd/ DESTINATION ${CMAKE_INSTALL_PREFIX} FILES_MATCHING PATTERN "*"  PATTERN "*")
    endif()

    INSTALL(TARGETS ${PROJECT_NAME} DESTINATION ${CMAKE_INSTALL_PREFIX}/bin )
    INSTALL(TARGETS ${NODE_CLI_TARGET} DESTINATION ${CMAKE_INSTALL_PREFIX}/bin )
    INSTALL(TARGETS ${NODE_TOOL_TARGET} DESTINATION ${CMAKE_INSTALL_PREFIX}/bin )

    if (BUILD_DIAGTOOL)
        INSTALL(TARGETS cellframe-diagtool DESTINATION ${CMAKE_INSTALL_PREFIX}/bin )
    endif()

    if(NOT ANDROID)
	    #install all python-specific files back to its original location
	if (SUPPORT_PYTHON_PLUGINS AND BUILD_WITH_PYTHON_ENV)

	   INSTALL(FILES ${cpython37static_SOURCE_DIR}/bin/pip3 DESTINATION ${CMAKE_INSTALL_PREFIX}/bin/ )
       INSTALL(FILES ${cpython37static_SOURCE_DIR}/bin/python3.7 DESTINATION ${CMAKE_INSTALL_PREFIX}/bin/ )
	   INSTALL(DIRECTORY ${cpython37static_SOURCE_DIR}/lib/python3.7 DESTINATION ${CMAKE_INSTALL_PREFIX}/lib/ USE_SOURCE_PERMISSIONS)
        endif()
    endif()

    INSTALL(DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/scripts/ DESTINATION ${CMAKE_INSTALL_PREFIX}/sbin FILES_MATCHING PATTERN "*"  PATTERN "*" PERMISSIONS OWNER_EXECUTE;OWNER_READ;OWNER_WRITE;WORLD_READ;GROUP_READ )

endif()
INCLUDE(CPack)

