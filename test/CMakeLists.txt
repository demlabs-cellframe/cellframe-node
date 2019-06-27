if(TARGET kelvin_node_test)
    return() # The project has already been built.
endif()
project(kelvin_node_test)

add_subdirectory(libdap-test)

file(GLOB SOURCES *.c)
file(GLOB HEADERS *.h)

add_executable(${PROJECT_NAME} ${SOURCES} ${HEADERS})

target_link_libraries(${PROJECT_NAME} dap_core dap_test dap_chain_global_db dap_chain_gdb)

file(COPY locale DESTINATION ${CMAKE_CURRENT_BINARY_DIR})

add_test(
    NAME kelvin_node_test
    COMMAND kelvin_node_test
)
