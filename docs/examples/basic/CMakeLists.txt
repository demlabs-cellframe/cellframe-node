cmake_minimum_required(VERSION 3.10)
project(dap_basic_example C)

# Создать исполняемый файл
add_executable(${PROJECT_NAME}
    dap_basic_example.c
)

# Включить директории
target_include_directories(${PROJECT_NAME} PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}
)

# Связать с необходимыми библиотеками
target_link_libraries(${PROJECT_NAME}
    m  # math library
)

# Опции компиляции
target_compile_options(${PROJECT_NAME} PRIVATE
    -Wall
    -Wextra
    -Wpedantic
    -O2
    -g
    -std=c99
)

# Установка
install(TARGETS ${PROJECT_NAME}
    RUNTIME DESTINATION bin
)

# Вывод информации о сборке
message(STATUS "DAP Basic Example configured:")
message(STATUS "  Build type: ${CMAKE_BUILD_TYPE}")
message(STATUS "  Install prefix: ${CMAKE_INSTALL_PREFIX}")
message(STATUS "  Compiler: ${CMAKE_C_COMPILER}")
message(STATUS "  C Standard: ${CMAKE_C_STANDARD}")
message(STATUS "")
message(STATUS "Build commands:")
message(STATUS "  make          - Build the example")
message(STATUS "  make install  - Install to ${CMAKE_INSTALL_PREFIX}/bin")
message(STATUS "  make clean    - Clean build files")



