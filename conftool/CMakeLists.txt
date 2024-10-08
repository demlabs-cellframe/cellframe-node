cmake_minimum_required(VERSION 3.10)

include(FetchContent)

project(cellframe-node-config)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
SET (CONFTOOL_SRC ./main.cpp
        ./commands/AbstractCommand.cpp
        ./commands/NetworkCommand.cpp
        ./commands/ConditionCommand.cpp
        ./commands/StorageCommand.cpp
        ./commands/ConfigCommand.cpp
        ./commands/ServiceCommand.cpp
        ./commands/FromTemplateCommand.cpp
        ./commands/NetworkListCommand.cpp
        ./config/CellframeConfigFile.cpp
        ./service/service_win.cpp
        ./service/service_linux.cpp)


if (ANDROID)
  add_library(${PROJECT_NAME} SHARED ${CONFTOOL_SRC})
else ()
  add_executable(${PROJECT_NAME} ${CONFTOOL_SRC})
endif ()
  if (LINUX OR WIN32 )
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

#if (ANDROID)
#  add_definitions("-DANDROID_STL=c++_static")
#endif()


IF (WIN32)
  target_link_libraries(cellframe-node-config PRIVATE ws2_32)
ENDIF()


