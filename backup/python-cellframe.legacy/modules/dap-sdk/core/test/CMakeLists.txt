project(TPO C)
cmake_minimum_required(VERSION 3.10)

set(CMAKE_VERBOSE_MAKEFILE ON)
set(CMAKE_COLOR_MAKEFILE   ON)
set(CMAKE_C_STANDARD 11)

include_directories(${PYTHON_INCLUDE_DIR} include/)

file(GLOB TPO_INCLUDES include/*.h)
file(GLOB TPO_SRCS src/*.c)

add_library(${PROJECT_NAME} SHARED ${TPO_INCLUDES} ${TPO_SRCS} )

target_link_libraries(${PROJECT_NAME} ${PYTHON_LIBRARIES})

target_link_libraries(${PROJECT_NAME} dap_python_module)
