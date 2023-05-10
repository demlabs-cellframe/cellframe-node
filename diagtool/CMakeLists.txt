cmake_minimum_required(VERSION 3.10)

project(cellframe-diagtool)

find_package(Qt5 5.15 REQUIRED COMPONENTS
    Core
    Network
)

set(CMAKE_AUTOMOC ON)

add_executable(${PROJECT_NAME}
    main.cpp
    DiagnosticWorker.cpp
    AbstractDiagnostic.cpp
    LinuxDiagnostic.cpp
)

target_link_libraries(${PROJECT_NAME}
    Qt5::Core Qt5::Network
)

