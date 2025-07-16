cmake_minimum_required(VERSION 3.10)
project(python-dap C)

set(CMAKE_C_STANDARD 11)

# Build configuration
option(BUILD_PYTHON_CELLFRAME_COMMON "Build python_cellframe_common library" ON)
option(BUILD_TESTS "Build tests" ON)

# Include dap-sdk
add_subdirectory(dap-sdk)

# Find Python
find_package(Python3 COMPONENTS Interpreter Development REQUIRED)

if(BUILD_PYTHON_CELLFRAME_COMMON)
    # Create python_cellframe_common shared library
    add_library(python_cellframe_common SHARED
        # Core DAP functions we need for Python
        src/python_dap_core.c
        src/python_dap_config.c
        src/python_dap_crypto.c
        src/python_dap_network.c
        src/python_dap_system.c
        src/python_dap_common.c
    )

    # Link with DAP SDK components
    target_link_libraries(python_cellframe_common
        dap_core
        dap_crypto
        dap_io
        dap_global_db
        ${Python3_LIBRARIES}
    )

    # Include directories
    target_include_directories(python_cellframe_common PRIVATE
        ${Python3_INCLUDE_DIRS}
        dap-sdk/core/include
        dap-sdk/crypto/include
        dap-sdk/io/include
        dap-sdk/global-db/include
        include
    )

    # Set library properties
    set_target_properties(python_cellframe_common PROPERTIES
        PREFIX ""
        OUTPUT_NAME "python_cellframe_common"
        LIBRARY_OUTPUT_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/lib"
    )

    # Install library
    install(TARGETS python_cellframe_common
        LIBRARY DESTINATION lib
        RUNTIME DESTINATION bin
    )
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