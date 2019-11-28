
if(${CMAKE_SYSTEM_NAME} MATCHES "Linux")
    set(LINUX 1)

# check if we're building natively on Android (TERMUX)
    EXECUTE_PROCESS( COMMAND uname -o COMMAND tr -d '\n' OUTPUT_VARIABLE OPERATING_SYSTEM)
      if(${OPERATING_SYSTEM} MATCHES "Android")
        set(ANDROID 1)
        message("ANDROID")
        add_definitions(-DANDROID)
      endif(${OPERATING_SYSTEM} MATCHES "Android")
# Another test, in case we're cross-compiling for Android and CMAKE_SYSTEM_NAME has been set manually (as suggest by cmake)
# https://cmake.org/cmake/help/v3.8/manual/cmake-toolchains.7.html#cross-compiling-for-android

elseif(${CMAKE_SYSTEM_NAME} MATCHES "Android")
    message("ANDROID")
    set(ANDROID 1)
    set(LINUX 1)
    add_definitions(-DANDROID)
endif()
