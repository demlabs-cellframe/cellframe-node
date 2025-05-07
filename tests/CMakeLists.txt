# Укажи имя исполняемого файла теста
add_executable(test_example test_example.c)

# Линкуем с библиотекой cmocka
find_package(PkgConfig REQUIRED)
pkg_check_modules(CMOCKA REQUIRED cmocka)

target_include_directories(test_example PRIVATE ${CMOCKA_INCLUDE_DIRS})
target_link_libraries(test_example ${CMOCKA_LIBRARIES})

# Добавляем тест в ctest
add_test(NAME test_example COMMAND test_example)
