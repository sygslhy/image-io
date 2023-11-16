

add_library(cxx_image_bind STATIC 
	Image.cpp
	ImageIO.cpp
	ImageMetadata.cpp
	Matrix.cpp
	MetadataParser.cpp)
target_link_libraries(cxx_image_bind PRIVATE image io math model parser  pybind11::pybind11 loguru)

# Add the lib io's private headers to target becuase pybind11 need defintion of every detail image readers.
set(IO_PRIVATE_HDR ${CMAKE_BINARY_DIR}/_deps/cxx-image-src/lib/io/src/)
target_include_directories(cxx_image_bind PRIVATE ${IO_PRIVATE_HDR})
target_link_libraries(cxx_image_bind PRIVATE Deflate::Deflate Intl::Intl Iconv::Iconv JBIG::JBIG LERC::LERC LZMA::LZMA WebP::WebP ZSTD::ZSTD)


pybind11_add_module(cxx_image BindingEntryPoint.cpp)
target_link_libraries(cxx_image PRIVATE cxx_image_bind pybind11::pybind11 loguru)


install(TARGETS cxx_image
  COMPONENT python
  LIBRARY DESTINATION "${CMAKE_SOURCE_DIR}/image_io"
  )