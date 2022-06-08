cmake_minimum_required(VERSION 3.10)
project(cellframe-node C)
set(CMAKE_ENABLE_EXPORTS ON)
set(CMAKE_VERBOSE_MAKEFILE ON)
set(CMAKE_COLOR_MAKEFILE   ON)
set(CMAKE_C_STANDARD 11)

# Predefine project
SET( CPACK_PACKAGE_NAME  "${PROJECT_NAME}")
SET( CPACK_PACKAGE_VERSION_MAJOR 5)
SET( CPACK_PACKAGE_VERSION_MINOR 2)
SET( CPACK_PACKAGE_VERSION_PATCH 0)

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
#set(BUILD_WITH_GDB_DRIVER_MDBX ON)
#set(BUILD_CRYPTO_TESTS ON)

#set(BUILD_WITH_SYSTEM_PYTHON ON)       #link with system python3. If OFF - will user prebuilds or src.
set(BUILD_PYTHON_FROM_SRC ON)           #build Python from sources; if OFF - will use a prebuilds.
set(BUILD_PYTHON_СUSTOM_LIBFFI ON)      #use libffi from source archive.
set(BUILD_PYTHON_СUSTOM_ZLIB ON)        #use zlib from source arcivie.
set(BUILD_PYTHON_СUSTOM_OPENSSL ON)     #use openssl from source archive.
set(BUILD_PYTHON_SHARED OFF)            #use python with shared lib (or link staticaly).

if(LINUX)
    set(SUPPORT_PYTHON_PLUGINS OFF)
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

add_subdirectory(cellframe-sdk)

if (CELLFRAME_MODULES MATCHES "modules-dynamic")
    add_definitions("-DDAP_MODULES_DYNAMIC")
endif()


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
    
    #have to figure out how to use it properly with custom RPATH for python plugins...
    if (NOT SUPPORT_PYTHON_PLUGINS)
        SET( CPACK_DEBIAN_PACKAGE_SHLIBDEPS ON)
    endif()

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



if(UNIX AND NOT WIN32)
    message ("[*] Unix library set")
    set_property(TARGET ${PROJECT_NAME} APPEND_STRING PROPERTY LINK_FLAGS "-D_GNU_SOURCE")
    set(NODE_LIBRARIES cellframe-sdk )

    set(NODE_CLI_LIBRARIES m cellframe-sdk)

    set(NODE_TOOL_LIBRARIES m cellframe-sdk)

    if (SUPPORT_PYTHON_PLUGINS)
        message("[+] Build with python plugins support")
        
        add_definitions("-DDAP_SUPPORT_PYTHON_PLUGINS")
        set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -DDAP_SUPPORT_PYTHON_PLUGINS")
        
        set(PYTHON_PREFIX ${CMAKE_CURRENT_BINARY_DIR}/python)

        if (BUILD_WITH_SYSTEM_PYTHON)
            message("[!] Using system python")
            set(Python_ADDITIONAL_VERSION 3.9 3.8 3.7 3.6 3.5 3.4)
            find_package(PythonLibs REQUIRED)     

            add_library( PYTHON_LIBRARY SHARED IMPORTED )
            set_target_properties( PYTHON_LIBRARY PROPERTIES IMPORTED_LOCATION ${PYTHON_LIBRARY})

        elseif (BUILD_PYTHON_FROM_SRC)
            message("[!] Building python from source")
            include(ExternalProject)

            set(LIBFFI_URL "https://pub.cellframe.net/3rdparty/python/libffi-3.3.tar.gz")
            set(LIBFFI_HASH "SHA256=72fba7922703ddfa7a028d513ac15a85c8d54c8d67f55fa5a4802885dc652056")

            set(ZLIB_URL  "https://pub.cellframe.net/3rdparty/python/zlib-1.2.12.tar.gz")
            set(ZLIB_HASH "SHA256=91844808532e5ce316b3c010929493c0244f3d37593afd6de04f71821d5136d9")

            set(LIBSSL_URL "https://pub.cellframe.net/3rdparty/python/openssl-1.1.1o.tar.gz")
            set(LIBSSL_HASH "SHA256=9384a2b0570dd80358841464677115df785edb941c71211f75076d72fe6b438f")

            set(PYTHON_URL "https://pub.cellframe.net/3rdparty/python/Python-3.9.12.tgz")
            set(PYTHON_HASH "SHA256=70e08462ebf265012bd2be88a63d2149d880c73e53f1712b7bbbe93750560ae8")

            if(BUILD_PYTHON_СUSTOM_LIBFFI)
                message("[+] Building libffi from source")

                set(LIBFFI_PREFIX ${CMAKE_CURRENT_BINARY_DIR}/libffi)
                set(WRP_CFLAGS "-fPIC")
                set(WRP_CPPFLAGS "-fPIC")

                configure_file(cfg.python.wrapper.in ffi.cfg.wrapper.sh @ONLY)

                ExternalProject_Add(
                    LIBFFI
                    URL                         ${LIBFFI_URL}
                    URL_HASH                    ${LIBFFI_HASH}
                    PREFIX                      ${LIBFFI_PREFIX}
                    INSTALL_DIR                 ${LIBFFI_PREFIX}
                    BUILD_COMMAND               ${MAKE}
                    LOG_CONFIGURE               ON
                    LOG_BUILD                   ON
                    LOG_OUTPUT_ON_FAILURE       ON
                    CONFIGURE_HANDLED_BY_BUILD  ON
                    CONFIGURE_COMMAND           /bin/sh ${CMAKE_CURRENT_BINARY_DIR}/ffi.cfg.wrapper.sh <SOURCE_DIR>/configure --disable-shared --prefix=${LIBFFI_PREFIX}
                )

                set(PYTHON_WRP_CFLAGS "${PYTHON_WRP_CFLAGS} -DHAVE_FFI_PREP_CIF_VAR=1 -DHAVE_FFI_PREP_CLOSURE_LOC=1 -DHAVE_FFI_CLOSURE_ALLOC=1 -I${LIBFFI_PREFIX}/include")
                set(PYTHON_WRP_CPPFLAGS "${PYTHON_WRP_CPPFLAGS} -DHAVE_FFI_PREP_CIF_VAR=1 -DHAVE_FFI_PREP_CLOSURE_LOC=1 -DHAVE_FFI_CLOSURE_ALLOC=1 -I${LIBFFI_PREFIX}/include")
                set(PYTHON_WRP_LDFLAGS "${PYTHON_WRP_LDFLAGS} ${LIBFFI_PREFIX}/lib/libffi.a")

            endif()

            if(BUILD_PYTHON_СUSTOM_ZLIB)
                message("[+] Building zlib from source")

                set(ZLIB_PREFIX ${CMAKE_CURRENT_BINARY_DIR}/zlib)
                set(WRP_CFLAGS "-fPIC")
                set(WRP_CPPFLAGS "-fPIC")

                configure_file(cfg.python.wrapper.in zlib.cfg.wrapper.sh @ONLY)

                ExternalProject_Add(
                    ZLIB
                    URL                         ${ZLIB_URL}
                    URL_HASH                    ${ZLIB_HASH}
                    PREFIX                      ${ZLIB_PREFIX}
                    INSTALL_DIR                 ${ZLIB_PREFIX}
                    BUILD_COMMAND               ${MAKE}
                    LOG_CONFIGURE               ON
                    LOG_BUILD                   ON
                    LOG_OUTPUT_ON_FAILURE       ON
                    CONFIGURE_HANDLED_BY_BUILD  ON
                    CONFIGURE_COMMAND           /bin/sh ${CMAKE_CURRENT_BINARY_DIR}/zlib.cfg.wrapper.sh <SOURCE_DIR>/configure --static --prefix=${ZLIB_PREFIX}
                )

                set(PYTHON_WRP_CFLAGS "${PYTHON_WRP_CFLAGS} -I${ZLIB_PREFIX}/include")
                set(PYTHON_WRP_CPPFLAGS "${PYTHON_WRP_CPPFLAGS} -I${ZLIB_PREFIX}/include")
                set(PYTHON_WRP_LDFLAGS "${PYTHON_WRP_LDFLAGS} -L${ZLIB_PREFIX}/lib/ ${ZLIB_PREFIX}/lib/libz.a")

            endif()

            if(BUILD_PYTHON_СUSTOM_OPENSSL)

                message("[+] Building openssl from source")

                set(LIBSSL_PREFIX ${CMAKE_CURRENT_BINARY_DIR}/libssl)

                ExternalProject_Add(
                    LIBSSL
                    URL                         ${LIBSSL_URL}
                    URL_HASH                    ${LIBSSL_HASH}
                    PREFIX                      ${LIBSSL_PREFIX}
                    INSTALL_DIR                 ${LIBSSL_PREFIX}
                    BUILD_COMMAND               ${MAKE}
                    LOG_CONFIGURE               ON
                    LOG_BUILD                   ON
                    LOG_OUTPUT_ON_FAILURE       ON
                    CONFIGURE_HANDLED_BY_BUILD  ON
                    CONFIGURE_COMMAND           <SOURCE_DIR>/config --prefix=${LIBSSL_PREFIX}
                )

                set(WITH_OPENSSL "--with-openssl=${LIBSSL_PREFIX}")

            endif()

            if(CMAKE_BUILD_TYPE MATCHES Debug)
                if (BUILD_PYTHON_SHARED)
                    message("[*] Building python as shared lib")
                    set(PYTHON_LIBRARY ${CMAKE_BINARY_DIR}/python/lib/libpython3.9d.so)
                else()
                    message("[*] Building python as static lib")
                    set(PYTHON_LIBRARY ${CMAKE_BINARY_DIR}/python/lib/libpython3.9d.a)
                endif()
                set(PYTHON_INCLUDE_DIR ${PYTHON_PREFIX}/include/python3.9d)
            else()
                if (BUILD_PYTHON_SHARED)
                    message("[*] Building python as shared lib")
                    set(PYTHON_LIBRARY ${CMAKE_BINARY_DIR}/python/lib/libpython3.9.so)
                else()
                    message("[*] Building python as static lib")
                    set(PYTHON_LIBRARY ${CMAKE_BINARY_DIR}/python/lib/libpython3.9.a)
                endif()
                set(PYTHON_INCLUDE_DIR ${PYTHON_PREFIX}/include/python3.9)
            endif()

            if(NOT BUILD_PYTHON_SHARED)
                set(PYTHON_SHARED  "--disable-shared")
            else()
                set(PYTHON_SHARED  "--enable-shared")
            endif()

            set(WRP_CFLAGS ${PYTHON_WRP_CFLAGS})
            set(WRP_CPPFLAGS ${PYTHON_WRP_CPPFLAGS})
            set(WRP_LDFLAGS ${PYTHON_WRP_LDFLAGS})

            configure_file(cfg.python.wrapper.in python.cfg.wrapper.sh @ONLY)

            ExternalProject_Add(
                PYTHON
                URL                         ${PYTHON_URL}
                URL_HASH                    ${PYTHON_HASH}
                PREFIX                      ${PYTHON_PREFIX}
                INSTALL_DIR                 ${PYTHON_PREFIX}
                BUILD_COMMAND               ${MAKE}
                BUILD_BYPRODUCTS            ${PYTHON_INCLUDE_DIR} ${PYTHON_LIBRARY}
                LOG_CONFIGURE               ON
                LOG_BUILD                   ON
                LOG_OUTPUT_ON_FAILURE       ON
                CONFIGURE_HANDLED_BY_BUILD  ON
                CONFIGURE_COMMAND           /bin/sh ${CMAKE_CURRENT_BINARY_DIR}/python.cfg.wrapper.sh <SOURCE_DIR>/configure --with-pydebug --with-ensurepip=install ${PYTHON_SHARED} ${WITH_OPENSSL}  --prefix=${PYTHON_PREFIX}
            )

            if(NOT BUILD_PYTHON_SHARED)
                add_library( PYTHON_LIBRARY STATIC IMPORTED )
            else()
                add_library( PYTHON_LIBRARY SHARED IMPORTED )
            endif()

            set_target_properties( PYTHON_LIBRARY PROPERTIES IMPORTED_LOCATION ${PYTHON_LIBRARY})

            if(BUILD_PYTHON_СUSTOM_ZLIB)
                add_dependencies(PYTHON ZLIB)
            endif()

            if(BUILD_PYTHON_СUSTOM_OPENSSL)
                add_dependencies(PYTHON LIBSSL)
            endif()

            if(BUILD_PYTHON_СUSTOM_LIBFFI)
                add_dependencies(PYTHON LIBFFI)
            endif()

            if (BUILD_PYTHON_SHARED)
                set(CMAKE_SKIP_RPATH TRUE)
                set_target_properties(${NODE_TARGET} PROPERTIES LINK_FLAGS "-Wl,-rpath,\$ORIGIN/python/lib/")
            endif()

            add_dependencies(dap_core PYTHON)

        endif()

        get_target_property(PYTHON_LIBRARY_PATH PYTHON_LIBRARY IMPORTED_LOCATION)

        message("[!] Python includes path: " ${PYTHON_INCLUDE_DIR})    
        message("[!] Python library path: " ${PYTHON_LIBRARY_PATH})    
        
        include_directories(${PYTHON_INCLUDE_DIR})
        set(NODE_LIBRARIES ${NODE_LIBRARIES} dap_plugins_python PYTHON_LIBRARY -lutil)
        
        add_subdirectory(python-cellframe)
        
    endif()

    if(ANDROID )
        set(ALL_LIBRARIES ${NODE_LIBRARIES} ${NODE_CLI_LIBRARIES} ${NODE_TOOL_LIBRARIES} log)
        list(REMOVE_DUPLICATES ALL_LIBRARIES)
        target_link_libraries(${NODE_TARGET} ${ALL_LIBRARIES})
    else()
        
        target_link_libraries(${NODE_TARGET}      ${NODE_LIBRARIES}  pthread )
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

        if (SUPPORT_PYTHON_PLUGINS AND NOT BUILD_WITH_SYSTEM_PYTHON) #install python environment if not system python in use
            INSTALL(DIRECTORY build/python/ DESTINATION ${CMAKE_INSTALL_PREFIX}/bin/python USE_SOURCE_PERMISSIONS)
        endif()
    endif()

    INSTALL(DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/scripts/ DESTINATION ${CMAKE_INSTALL_PREFIX}/sbin FILES_MATCHING PATTERN "*"  PATTERN "*" PERMISSIONS OWNER_EXECUTE;OWNER_READ;OWNER_WRITE;WORLD_READ;GROUP_READ )
    
endif()
INCLUDE(CPack)
