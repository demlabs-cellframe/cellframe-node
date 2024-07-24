cmake_minimum_required(VERSION 3.10)

include(FetchContent)

project(cellframe-node-config)

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
                                ./service/service_linux.cpp
                                ./service/service_macos.cpp)

target_link_libraries(cellframe-node-config
)

if (LINUX OR WIN32)
  target_link_libraries(cellframe-node-config PRIVATE stdc++fs )
endif()

target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_20)


IF (WIN32)
  target_link_libraries(cellframe-node-config PRIVATE ws2_32)
ENDIF()


