cmake_minimum_required(VERSION 3.10)

project(sqlite3 C)

add_library(${PROJECT_NAME} STATIC sqlite3.c sqlite3.h)

target_include_directories(${PROJECT_NAME} PUBLIC .)
