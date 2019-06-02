if(TARGET kelvin_node_test)
    return() # The project has already been built.
endif()
project(kelvin_node_test)

add_subdirectory(libdap-test)

file(GLOB SOURCES *.c)
file(GLOB HEADERS *.h)

add_executable(${PROJECT_NAME} ${SOURCES} ${HEADERS})

target_link_libraries(${PROJECT_NAME} dap_core)

add_test(
    NAME kelvin_node_test
    COMMAND kelvin_node_test
)
