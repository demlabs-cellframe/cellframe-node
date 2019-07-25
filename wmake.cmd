@echo off
set CMAKE_PATH=C:/cmake
set MINGW_PATH=C:/mingw-w64/x86_64-8.1.0-posix-seh-rt_v6-rev0

PATH=%CMAKE_PATH%/bin;%MINGW_PATH%/mingw64/bin;%MINGW_PATH%/mingw64/x86_64-w64-mingw32/include;%MINGW_PATH%/mingw64/x86_64-w64-mingw32/lib
mingw32-make.exe

