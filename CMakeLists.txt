cmake_minimum_required(VERSION 3.10)
project(image-io)

# Needed for clang-tidy post process
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)


# Build everything as static for MinGW to avoid any DLL dependency
if(MINGW OR MSYS)
    link_libraries("-static -static-libgcc -static-libstdc++")
    add_compile_options("$<$<COMPILE_LANGUAGE:CXX>:-std=c++17>")
endif()

if("${CMAKE_CXX_COMPILER_ID}" STREQUAL "GNU")
    add_compile_options("$<$<COMPILE_LANGUAGE:CXX>:-march=haswell>")
    add_compile_options("$<$<COMPILE_LANGUAGE:CXX>:-fPIC>" "$<$<COMPILE_LANGUAGE:C>:-fPIC>")
    add_compile_options("$<$<COMPILE_LANGUAGE:CXX>:-std=gnu++17>")
endif()

SET(CMAKE_FIND_LIBRARY_SUFFIXES ".a")

include(FetchContent)

FetchContent_Declare(
    cxx-image
    GIT_REPOSITORY "https://github.com/sygslhy/cxx-image.git"
    GIT_TAG "feature/pov-dng-preview" #  Sep 16, 2024
)
FetchContent_MakeAvailable(cxx-image)

FetchContent_Declare(
    pybind11
    GIT_REPOSITORY "https://github.com/pybind/pybind11.git"
    GIT_TAG "v2.13.6"
)
FetchContent_MakeAvailable(pybind11)

add_subdirectory(cxx_image_io/binding)
