cmake_minimum_required(VERSION 3.10)
project(hello-world C)

# Find DAP SDK
find_package(DAP REQUIRED)

# Create executable
add_executable(${PROJECT_NAME}
    main.c
    app.c
)

# Include directories
target_include_directories(${PROJECT_NAME} PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}
    ${DAP_INCLUDE_DIRS}
)

# Link DAP SDK libraries
target_link_libraries(${PROJECT_NAME}
    dap_core
    dap_common
    dap_config
)

# Compile options
target_compile_options(${PROJECT_NAME} PRIVATE
    -Wall
    -Wextra
    -Wpedantic
    -O2
)

# Installation
install(TARGETS ${PROJECT_NAME}
    RUNTIME DESTINATION bin
)



