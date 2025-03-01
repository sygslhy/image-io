add_library(cxx_libraw_bind STATIC Metadata.cpp RawTypes.cpp)
target_link_libraries(
    cxx_libraw_bind PRIVATE raw_r # Link libraw dynamically
                            pybind11::pybind11
)

pybind11_add_module(cxx_libraw BindingEntryPoint.cpp)
target_link_libraries(cxx_libraw PRIVATE cxx_libraw_bind pybind11::pybind11)

# One hacky workaround to fix the multiple definition of _Unwind_Resume
if(MINGW OR MSYS)
    target_link_libraries(cxx_libraw PRIVATE "-Wl,-allow-multiple-definition")
endif()

install(
    TARGETS cxx_libraw
    COMPONENT cxx-image-io
    LIBRARY DESTINATION cxx_image_io
)
