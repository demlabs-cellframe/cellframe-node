cmake_minimum_required(VERSION 3.10)
project(python-dap C)

set(CMAKE_C_STANDARD 11)

# Build configuration
option(BUILD_PYTHON_CELLFRAME_COMMON "Build python_cellframe_common library" ON)
option(BUILD_TESTS "Build tests" ON)

# Configure DAP SDK modules we need - complete set for full functionality
set(DAPSDK_MODULES "core crypto io global-db network-core network-client network-server network-stream network-link_manager")
message(STATUS "DAPSDK_MODULES: ${DAPSDK_MODULES}")

# Include dap-sdk
add_subdirectory(dap-sdk)

# Find Python
find_package(Python3 COMPONENTS Interpreter Development REQUIRED)

if(BUILD_PYTHON_CELLFRAME_COMMON)
    # Create python_cellframe_common shared library
    add_library(python_cellframe_common SHARED
        # Complete DAP functions we need for Python
        src/python_dap_core.c
        src/python_dap_config.c
        src/python_dap_crypto.c
        src/python_dap_network.c
        src/python_dap_system.c
        src/python_gdb.c
    )

    # Set library properties with complete include paths
    target_include_directories(python_cellframe_common PUBLIC
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

    # Link with complete DAP SDK libraries
    target_link_libraries(python_cellframe_common
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

    # Set compile options with proper warnings control
    target_compile_options(python_cellframe_common PRIVATE
        -Wall -Wextra 
        -fPIC -O3 -std=gnu11
        -Wno-unused-parameter
        -Wno-unused-variable
    )

    # Platform specific settings
    if(APPLE)
        set_target_properties(python_cellframe_common PROPERTIES
            LINK_FLAGS "-undefined dynamic_lookup"
        )
    endif()
endif()

# Tests
if(BUILD_TESTS)
    enable_testing()
    add_subdirectory(tests/c_tests)
endif()

# Python package setup
add_custom_target(python_package
    COMMAND ${Python3_EXECUTABLE} setup.py build
    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
    DEPENDS python_cellframe_common
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
    DEPENDS python_cellframe_common
    COMMENT "Setting up development environment"
)