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
    GIT_REPOSITORY "https://github.com/emmcb/cxx-image.git"
    GIT_TAG "5cff7e0ed4775582433d8482f49b1a114af4527a"
)
FetchContent_MakeAvailable(cxx-image)

include(FetchContent)

FetchContent_Declare(
    pybind11
    GIT_REPOSITORY "https://github.com/pybind/pybind11.git"
    GIT_TAG "v2.11.1"
)
FetchContent_MakeAvailable(pybind11)

add_subdirectory(cxx_image_io/binding)
