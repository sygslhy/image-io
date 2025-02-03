add_library(cxx_libraw_bind STATIC
	libraw_types.cpp
)
target_link_libraries(cxx_libraw_bind PRIVATE libraw::libraw  pybind11::pybind11)

pybind11_add_module(cxx_libraw BindingEntryPoint.cpp )
target_link_libraries(cxx_libraw PRIVATE cxx_libraw_bind  pybind11::pybind11)

install(TARGETS cxx_libraw
	COMPONENT cxx-image-io
	LIBRARY DESTINATION cxx_image_io
)