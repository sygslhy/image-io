cmake_minimum_required(VERSION 3.11)
project(image-io)

# Needed for clang-tidy post process
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# add flag -fPIC for binding compiling library
add_compile_options("$<$<COMPILE_LANGUAGE:CXX>:-fPIC>" "$<$<COMPILE_LANGUAGE:C>:-fPIC>")

# Build everything as static for MinGW to avoid any DLL dependency
if(MINGW OR MSYS)
    link_libraries("-static -static-libgcc -static-libstdc++")
    add_compile_options("$<$<COMPILE_LANGUAGE:CXX>:-std=c++17>")
endif()

if("${CMAKE_CXX_COMPILER_ID}" STREQUAL "AppleClang" OR "${CMAKE_CXX_COMPILER_ID}" STREQUAL "Clang")
    add_compile_options("$<$<COMPILE_LANGUAGE:CXX>:-std=c++17>")
    link_libraries("-framework CoreServices")
endif()

if("${CMAKE_CXX_COMPILER_ID}" STREQUAL "GNU")
    add_compile_options("$<$<COMPILE_LANGUAGE:CXX>:-std=gnu++17>")
endif()

SET(CMAKE_FIND_LIBRARY_SUFFIXES ".a")

# WR for CI pass the M_PI missing issue
add_definitions(-D_USE_MATH_DEFINES)

include(FetchContent)

# fetch third-party libs from the source code from github
# which override the find_package
# and build with -fPIC option.
# make the same alias target name as former find_package searched.
# third-party libs: jpeg, tiff, png, exif, zlib
FetchContent_Declare(
    JPEG
    GIT_REPOSITORY "https://github.com/sygslhy/libjpeg.git"
    GIT_TAG "master"
    OVERRIDE_FIND_PACKAGE
)
FetchContent_MakeAvailable(JPEG)
add_library(JPEG::JPEG ALIAS jpeg-static)

FetchContent_Declare(
    EXIF
    GIT_REPOSITORY "https://github.com/sygslhy/libexif.git"
    GIT_TAG "master"
    OVERRIDE_FIND_PACKAGE
)
FetchContent_MakeAvailable(EXIF)
add_library(EXIF::EXIF ALIAS exif)

FetchContent_Declare(
    PNG
    GIT_REPOSITORY "https://github.com/sygslhy/libpng.git"
    GIT_TAG "master"
    OVERRIDE_FIND_PACKAGE
)
FetchContent_MakeAvailable(PNG)
add_library(PNG::PNG ALIAS png)

FetchContent_Declare(
    TIFF
    GIT_REPOSITORY "https://github.com/sygslhy/libtiff.git"
    GIT_TAG "master"
    OVERRIDE_FIND_PACKAGE
)
FetchContent_MakeAvailable(TIFF)
add_library(TIFF::TIFF ALIAS tiff)
add_library(TIFF::CXX ALIAS tiffxx)

FetchContent_Declare(
    ZLIB
    GIT_REPOSITORY "https://github.com/sygslhy/libz.git"
    GIT_TAG "master"
    OVERRIDE_FIND_PACKAGE
)
FetchContent_MakeAvailable(ZLIB)
add_library(ZLIB::ZLIB ALIAS z)

FetchContent_Declare(
    pybind11
    GIT_REPOSITORY "https://github.com/pybind/pybind11.git"
    GIT_TAG "v2.13.6"
)
FetchContent_MakeAvailable(pybind11)

FetchContent_Declare(
    cxx-image
    GIT_REPOSITORY "https://github.com/sygslhy/cxx-image.git"
    GIT_TAG "test-msys" #  Sep 16, 2024
)
FetchContent_MakeAvailable(cxx-image)

add_subdirectory(cxx_image_io/binding)
