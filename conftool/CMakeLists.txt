cmake_minimum_required(VERSION 3.10)

include(FetchContent)

project(cellframe-node-config)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_executable(${PROJECT_NAME} ./main.cpp 
                                ./commands/abstractcommand.cpp 
                                ./commands/networkcommand.cpp
                                ./commands/conditioncommand.cpp
                                ./commands/storagecommand.cpp
                                ./commands/configcommand.cpp
                                ./commands/servicecommand.cpp
                                ./commands/fromtemplatecommand.cpp
                                ./config/cellframeconfigfile.cpp
                                ./service/service_win.cpp
                                ./service/service_linux.cpp)

target_link_libraries(cellframe-node-config
)

if (LINUX OR WIN32)
  target_link_libraries(cellframe-node-config PRIVATE stdc++fs )
endif()

if (APPLE)

  target_link_libraries(cellframe-node-config PUBLIC "-framework Security -framework Foundation")

  add_library(conftool_osx_ctrl STATIC ./service/service_macos.cpp ./service/macos_auth.m)
    set_target_properties(conftool_osx_ctrl PROPERTIES
     LIBRARY_OUTPUT_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR})
  target_link_libraries(cellframe-node-config PUBLIC conftool_osx_ctrl)

endif()


target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_20)


IF (WIN32)
  target_link_libraries(cellframe-node-config PRIVATE ws2_32)
ENDIF()


