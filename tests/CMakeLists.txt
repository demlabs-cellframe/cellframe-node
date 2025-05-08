# ---------- 3.  GoogleTest ----------
# сначала пытаемся найти «правильные» экспорты (если, к примеру,
# билд идёт под Ubuntu 22.04+, vcpkg, Conan и т.д.)
find_package(GTest CONFIG QUIET)

if (NOT GTest_FOUND)
    # пробуем модульный FindGTest, который идёт в стандартном CMake
    find_package(GTest MODULE QUIET)
endif()

if (NOT GTest_FOUND)
    #  Debian/Ubuntu: есть libgtest.so, но нет никакого CMake-конфига
    find_library(GTEST_LIB NAMES gtest         PATHS /usr/lib /usr/lib64)
    find_library(GTEST_MAIN_LIB NAMES gtest_main PATHS /usr/lib /usr/lib64)

    if (GTEST_LIB AND GTEST_MAIN_LIB)
        add_library(GTest::gtest      SHARED IMPORTED)
        add_library(GTest::gtest_main SHARED IMPORTED)
        set_target_properties(GTest::gtest      PROPERTIES IMPORTED_LOCATION "${GTEST_LIB}")
        set_target_properties(GTest::gtest_main PROPERTIES IMPORTED_LOCATION "${GTEST_MAIN_LIB}")
        set(GTest_FOUND TRUE)
        message(STATUS "System GTest libraries imported manually "
                       "(${GTEST_LIB}, ${GTEST_MAIN_LIB})")
    endif()
endif()

if (NOT GTest_FOUND)
    # последний шанс – собрать vendored копию, если она есть в репозитории
    set(VENDORED "${PROJECT_SOURCE_DIR}/third_party/googletest")
    if (EXISTS "${VENDORED}/CMakeLists.txt")
        add_subdirectory(${VENDORED} EXCLUDE_FROM_ALL)
        add_library(GTest::gtest      ALIAS gtest)
        add_library(GTest::gtest_main ALIAS gtest_main)
        set(GTest_FOUND TRUE)
        message(STATUS "Vendored GoogleTest собран из ${VENDORED}")
    endif()
endif()

if (NOT GTest_FOUND)
    message(FATAL_ERROR "GoogleTest not found: "
                        "нет ни системных libgtest(.so), "
                        "ни подмодуля third_party/googletest")
endif()

set(GTEST_LIBS GTest::gtest GTest::gtest_main)
