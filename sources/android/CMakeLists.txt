cmake_minimum_required(VERSION 3.22.1)

project("android-node")

add_library(android-node SHARED
    ./node_jni.cpp)

target_link_libraries(android-node PRIVATE
    # List libraries link to the target library
    android
    log
    cellframe-node
    dap_app_cli
    cellframe-node-config)
