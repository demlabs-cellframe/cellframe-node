cmake_minimum_required(VERSION 3.10)

project(cellframe-diagtool)

find_package(Qt5 5.15 REQUIRED COMPONENTS
    Core
    Network
)

set(CMAKE_AUTOMOC ON)



if(UNIX)
    if(DARWIN)
        add_definitions(CLI_PATH=.\cellframe-node-cli)
        add_executable(${PROJECT_NAME}
            main.cpp
            DiagnosticWorker.cpp
            AbstractDiagnostic.cpp
            MacDiagnostic.cpp
        )
    endif()

    if(LINUX)
        add_definitions(CLI_PATH=/opt/cellframe-node/bin/cellframe-node-cli)
        add_executable(${PROJECT_NAME}
            main.cpp
            DiagnosticWorker.cpp
            AbstractDiagnostic.cpp
            LinuxDiagnostic.cpp
        )
    endif()

endif()

if(WIN32)
    add_definitions(CLI_PATH=cellframe-node-cli.exe)
    add_executable(${PROJECT_NAME}
        main.cpp
        DiagnosticWorker.cpp
        AbstractDiagnostic.cpp
        WinDiagnostic.cpp
    )
endif()


target_link_libraries(${PROJECT_NAME}
    Qt5::Core Qt5::Network
)

