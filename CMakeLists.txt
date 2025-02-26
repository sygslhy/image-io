cmake_minimum_required(VERSION 3.11)
set(CMAKE_INSTALL_PREFIX
    "${CMAKE_SOURCE_DIR}"
    CACHE PATH "install path"
)
project(image-io)
if(CMAKE_INSTALL_PREFIX_INITIALIZED_TO_DEFAULT)
    set(CMAKE_INSTALL_PREFIX
        "${CMAKE_SOURCE_DIR}"
        CACHE PATH "default install path" FORCE
    )
endif(CMAKE_INSTALL_PREFIX_INITIALIZED_TO_DEFAULT)

# Needed for clang-tidy post process
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Build everything as static for MinGW to avoid any DLL dependency
if(MINGW OR MSYS)
    add_compile_options("$<$<COMPILE_LANGUAGE:CXX>:-std=c++17>")
else()
    # add flag -fPIC for binding compiling library
    add_compile_options("$<$<COMPILE_LANGUAGE:CXX>:-fPIC>" "$<$<COMPILE_LANGUAGE:C>:-fPIC>")
endif()

if("${CMAKE_CXX_COMPILER_ID}" STREQUAL "AppleClang" OR "${CMAKE_CXX_COMPILER_ID}" STREQUAL "Clang")
    add_compile_options("$<$<COMPILE_LANGUAGE:CXX>:-std=c++17>")
    link_libraries("-framework CoreServices")
endif()

if("${CMAKE_CXX_COMPILER_ID}" STREQUAL "GNU")
    add_compile_options("$<$<COMPILE_LANGUAGE:CXX>:-std=gnu++17>")
endif()

include(FetchContent)

# fetch third-party libs from the source code from github which override the find_package and build with -fPIC option.
# make the same alias target name as former find_package searched. third-party libs: jpeg, tiff, png, exif, zlib
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
    GIT_TAG "dynamic"
    OVERRIDE_FIND_PACKAGE
)
FetchContent_MakeAvailable(EXIF)

# Set on purpose for no subdirectory of dll and pyd installations
set(CMAKE_INSTALL_BINDIR "")
set(CMAKE_INSTALL_LIBDIR "")
message(STATUS "CMAKE_INSTALL_PREFIX = ${CMAKE_INSTALL_PREFIX}")

add_library(EXIF::EXIF ALIAS exif)
install(
    TARGETS exif
    COMPONENT cxx-image-io
    LIBRARY DESTINATION cxx_image_io
    RUNTIME DESTINATION cxx_image_io
)

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
    GIT_TAG "test-msys"
)
FetchContent_MakeAvailable(cxx-image)

FetchContent_Declare(
    libraw
    GIT_REPOSITORY "https://github.com/sygslhy/LibRaw.git"
    GIT_TAG "master"
)
FetchContent_MakeAvailable(libraw)

install(
    TARGETS raw_r
    COMPONENT cxx-image-io
    LIBRARY DESTINATION cxx_image_io
    RUNTIME DESTINATION cxx_image_io
)

add_subdirectory(binding)
