cmake_minimum_required(VERSION 3.10)

include(FetchContent)



project(cellframe-node-config)

FetchContent_Declare(ftxui
  GIT_REPOSITORY https://github.com/ArthurSonzogni/ftxui
  GIT_TAG v4.0.0
)

#FetchContent_GetProperties(ftxui)
if(NOT ftxui_POPULATED)
  FetchContent_Populate(ftxui)
  add_subdirectory(${ftxui_SOURCE_DIR} ${ftxui_BINARY_DIR} EXCLUDE_FROM_ALL)
endif()



set(CMAKE_AUTOMOC ON)


add_executable(${PROJECT_NAME} ./main.cpp 
                                
                                ./ui/question.cpp
                                ./commands/abstractcommand.cpp 
                                ./commands/networkcommand.cpp
                                ./commands/conditioncommand.cpp
                                ./commands/storagecommand.cpp
                                ./commands/configcommand.cpp
                                ./commands/fromtemplatecommand.cpp
                                ./config/cellframeconfigfile.cpp)

target_link_libraries(cellframe-node-config
  PRIVATE ftxui::screen
  PRIVATE ftxui::dom
  PRIVATE ftxui::component # Not needed for this example.
)

IF (WIN32)
  target_link_libraries(cellframe-node-config PRIVATE ws2_32)
ENDIF()


