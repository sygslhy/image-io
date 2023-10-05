cmake_minimum_required(VERSION 3.10)
project(image-io)

# Needed for clang-tidy post process
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

include(FetchContent)

FetchContent_Declare(
    cxx-image
    GIT_REPOSITORY "https://github.com/emmcb/cxx-image.git"
    GIT_TAG "master"
)
FetchContent_MakeAvailable(cxx-image)


include(FetchContent)

FetchContent_Declare(
    pybind11
    GIT_REPOSITORY "https://github.com/pybind/pybind11.git"
    GIT_TAG "v2.11.1"
)
FetchContent_MakeAvailable(pybind11)


add_subdirectory(image_io/binding)
