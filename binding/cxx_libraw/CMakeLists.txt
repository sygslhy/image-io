pybind11_add_module(cxx_libraw BindingEntryPoint.cpp)
target_link_libraries(cxx_libraw PRIVATE  pybind11::pybind11 loguru::loguru)

install(TARGETS cxx_libraw
	COMPONENT cxx-image-io
	LIBRARY DESTINATION cxx_image_io
)