cmake_minimum_required(VERSION 3.10)
project(image-io)

list(APPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_SOURCE_DIR}/cmake/modules")

# Needed for clang-tidy post process
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)


add_compile_options("$<$<COMPILE_LANGUAGE:CXX>:-std=gnu++17>")

# Build everything as static for MinGW to avoid any DLL dependency
link_libraries("-static -static-libgcc -static-libstdc++")
add_compile_options("$<$<COMPILE_LANGUAGE:CXX>:-march=haswell>")

if("${CMAKE_CXX_COMPILER_ID}" STREQUAL "GNU")
    SET(CMAKE_FIND_LIBRARY_SUFFIXES ".a")
endif()


include(FetchContent)

FetchContent_Declare(
    cxx-image
    GIT_REPOSITORY "https://github.com/emmcb/cxx-image.git"
    GIT_TAG "5cb01371073812d6c21f60e6faa9e45542cbc6d1"
)
FetchContent_MakeAvailable(cxx-image)

include(FetchContent)

FetchContent_Declare(
    pybind11
    GIT_REPOSITORY "https://github.com/pybind/pybind11.git"
    GIT_TAG "v2.11.1"
)
FetchContent_MakeAvailable(pybind11)

find_package(Intl)
find_package(Iconv)
find_package(Deflate)
find_package(JBIG)
find_package(LERC)
find_package(ZSTD)
find_package(LZMA)
find_package(WebP)

add_subdirectory(image_io/binding)
