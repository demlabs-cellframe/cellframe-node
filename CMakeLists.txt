cmake_minimum_required(VERSION 3.10)
project(python-dap C)

set(CMAKE_C_STANDARD 11)

# Build configuration options - по умолчанию SHARED сборка
option(BUILD_SHARED "Build as shared library (standalone mode)" ON)
option(BUILD_STATIC "Build as static library (for integration)" OFF)
option(BUILD_TESTS "Build tests" OFF)

# Configure DAP SDK modules we need - complete set for full functionality
set(DAPSDK_MODULES "core crypto io global-db network-core network-client network-server network-stream network-link_manager")
message(STATUS "DAPSDK_MODULES: ${DAPSDK_MODULES}")

# Include dap-sdk
add_subdirectory(dap-sdk)

# Find Python
find_package(Python3 COMPONENTS Interpreter Development REQUIRED)

# Core python_dap source files
set(PYTHON_DAP_SOURCES
    src/python_dap.c
    src/python_dap_core.c
    src/python_dap_config.c
    src/python_dap_crypto.c
    src/python_dap_network.c
    src/python_dap_system.c
    src/python_dap_common.c
    src/python_dap_time.c
    src/python_dap_logging.c
    src/python_dap_events.c
    src/python_dap_client.c
    src/python_dap_server.c
    src/python_gdb.c
)

# Common include directories
set(PYTHON_DAP_INCLUDE_DIRS
    ${CMAKE_CURRENT_SOURCE_DIR}/include
    ${Python3_INCLUDE_DIRS}
    ${CMAKE_CURRENT_SOURCE_DIR}/dap-sdk/core/include
    ${CMAKE_CURRENT_SOURCE_DIR}/dap-sdk/crypto/include
    ${CMAKE_CURRENT_SOURCE_DIR}/dap-sdk/io/include
    ${CMAKE_CURRENT_SOURCE_DIR}/dap-sdk/global-db/include
    ${CMAKE_CURRENT_SOURCE_DIR}/dap-sdk/net/client/include
    ${CMAKE_CURRENT_SOURCE_DIR}/dap-sdk/net/server/http_server/include
    ${CMAKE_CURRENT_SOURCE_DIR}/dap-sdk/net/stream/stream/include
    ${CMAKE_CURRENT_SOURCE_DIR}/dap-sdk/net/stream/ch/include
    ${CMAKE_CURRENT_SOURCE_DIR}/dap-sdk/net/stream/session/include
    ${CMAKE_CURRENT_SOURCE_DIR}/dap-sdk/net/link_manager/include
)

# Common libraries to link
set(PYTHON_DAP_LIBRARIES
    dap_core
    dap_crypto
    dap_crypto_kyber512
    dap_io
    dap_global_db
    dap_client
    dap_http_server
    dap_stream
    dap_stream_ch
    dap_session
    dap_link_manager
    ${Python3_LIBRARIES}
)

# Build shared library (standalone mode)
if(BUILD_SHARED)
    add_library(python_dap SHARED ${PYTHON_DAP_SOURCES})
    
    target_include_directories(python_dap PUBLIC ${PYTHON_DAP_INCLUDE_DIRS})
    target_link_libraries(python_dap ${PYTHON_DAP_LIBRARIES})
    
    target_compile_options(python_dap PRIVATE
        -Wall -Wextra 
        -fPIC -O3 -std=gnu11
        -Wno-unused-parameter
        -Wno-unused-variable
        -DPYTHON_DAP_STANDALONE
    )
    
    if(APPLE)
        set_target_properties(python_dap PROPERTIES
            LINK_FLAGS "-undefined dynamic_lookup"
        )
    endif()
    
    # Set output name for standalone mode
    set_target_properties(python_dap PROPERTIES
        OUTPUT_NAME "python_dap"
    )
endif()

# Build static library
if(BUILD_STATIC)
    add_library(python_dap_static STATIC ${PYTHON_DAP_SOURCES})
    
    target_include_directories(python_dap_static PUBLIC ${PYTHON_DAP_INCLUDE_DIRS})
    target_link_libraries(python_dap_static ${PYTHON_DAP_LIBRARIES})
    
    target_compile_options(python_dap_static PRIVATE
        -Wall -Wextra 
        -fPIC -O3 -std=gnu11
        -Wno-unused-parameter
        -Wno-unused-variable
        -DPYTHON_DAP_STATIC
    )
    
    # Set output name for static mode
    set_target_properties(python_dap_static PROPERTIES
        OUTPUT_NAME "python_dap"
    )
endif()

# Tests
if(BUILD_TESTS)
    enable_testing()
    if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/tests/c_tests")
        add_subdirectory(tests/c_tests)
    endif()
endif()

# Python package setup (only for shared build)
if(BUILD_SHARED)
    add_custom_target(python_package
        COMMAND ${Python3_EXECUTABLE} setup.py build
        WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
        DEPENDS python_dap
        COMMENT "Building Python package"
    )

    # Install Python package
    add_custom_target(python_install
        COMMAND ${Python3_EXECUTABLE} setup.py install
        WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
        DEPENDS python_package
        COMMENT "Installing Python package"
    )

    # Development target - builds and sets up for testing
    add_custom_target(dev_setup
        COMMAND ${Python3_EXECUTABLE} setup.py develop
        WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
        DEPENDS python_dap
        COMMENT "Setting up development environment"
    )
endif()

# Print configuration summary
message(STATUS "Python DAP Build Configuration:")
message(STATUS "  Shared library (standalone): ${BUILD_SHARED}")
message(STATUS "  Static library: ${BUILD_STATIC}")
message(STATUS "  Tests: ${BUILD_TESTS}")
message(STATUS "  Python path: ${Python3_EXECUTABLE}")