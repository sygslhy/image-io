#include "libraw/libraw.h"

#include "pybind11/numpy.h"
#include "pybind11/pybind11.h"
#include "pybind11/stl.h"

namespace py = pybind11;

// void init_types(py::module &m) {
//     py::class_<libraw_image_sizes_t> rawImageSizes(m, "RawImageSizes", py::is_final());
//
//     rawImageSizes.def(py::init<>())
//         .def_readwrite("raw_height", &libraw_image_sizes_t::raw_height, "uint16: Full size height of RAW image
//         (including the frame) in pixels.") .def_readwrite("raw_width", &libraw_image_sizes_t::raw_width, "uint16:
//         Full size width of RAW image (including the frame) in pixels.") .def_readwrite("height",
//         &libraw_image_sizes_t::height, "uint16: Size height of visible (\"meaningful\") part of the image (without
//         the frame).") .def_readwrite("width", &libraw_image_sizes_t::width, "uint16: Size width of visible
//         (\"meaningful\") part of the image (without the frame).") .def_readwrite("top_margin",
//         &libraw_image_sizes_t::top_margin, "uint16: Coordinates of the top corner of the frame (the second corner is
//         calculated from the full size of the image and size of its visible part).") .def_readwrite("left_margin",
//         &libraw_image_sizes_t::left_margin, "uint16: Coordinates of the left corner of the frame (the second corner
//         is calculated from the full size of the image and size of its visible part).") .def_readwrite("iheight",
//         &libraw_image_sizes_t::iheight, "uint16: Size height of the output image (may differ from height/width for
//         cameras that require image rotation or have non-square pixels).") .def_readwrite("iwidth",
//         &libraw_image_sizes_t::iwidth, "uint16: Size width of the output image (may differ from height/width for
//         cameras that require image rotation or have non-square pixels).") .def_readwrite("raw_pitch",
//         &libraw_image_sizes_t::raw_pitch, "unsigned: Full size of raw data row in bytes.")
//         .def_readwrite("pixel_aspect", &libraw_image_sizes_t::pixel_aspect, "double: Pixel width/height ratio. If it
//         is not unity, scaling of the image along one of the axes is required during output.") .def_readwrite("flip",
//         &libraw_image_sizes_t::flip, "int: Image orientation (0 if does not require rotation; 3 if requires 180-deg
//         rotation; 5 if 90 deg counterclockwise, 6 if 90 deg clockwise).") .def_property("mask",
//         [](libraw_image_sizes_t &p)->pybind11::array {
//             auto dtype = pybind11::dtype(pybind11::format_descriptor<int>::format());
//             return pybind11::array(dtype, { 8, 4 }, { sizeof(int) }, p.mask, nullptr);
//             }, [](libraw_image_sizes_t& p) {})
//         .def_readwrite("raw_aspect", &libraw_image_sizes_t::raw_aspect, "unsigned: Full Raw width/height ratio..")
//         .def_property("raw_inset_crops", [](libraw_image_sizes_t &p)->pybind11::array {
//             auto dtype = pybind11::dtype(pybind11::format_descriptor<libraw_raw_inset_crop_t>::format());
//             return pybind11::array(dtype, { 2 }, { sizeof(libraw_raw_inset_crop_t) }, p.raw_inset_crops, nullptr);
//         }, [](libraw_image_sizes_t& p) {});
//
//     py::class_<libraw_rawdata_t> rawData(m, "RawData", py::is_final());
//     rawData.def(py::init<>())
//         .def_readwrite("sizes", &libraw_rawdata_t::sizes, "class libraw_image_sizes_t: Image Dimensions")
//         .def_buffer([](libraw_rawdata_t &m) -> py::buffer_info {
//             return py::buffer_info(
//                 m.raw_alloc,                               /* Pointer to buffer */
//                 sizeof(uint16_t),                          /* Size of one scalar */
//                 py::format_descriptor<uint16_t>::format(), /* Python struct-style format descriptor */
//                 2,                                      /* Number of dimensions */
//                 { m.sizes.raw_height, m.sizes.raw_width },                 /* Buffer dimensions */
//                 { sizeof(uint16_t) * m.sizes.raw_width,             /* Strides (in bytes) for each index */
//                     sizeof(uint16_t) }
//             );
//         });
//
// };

int add(int i, int j) {
    return i + j;
}

void init_types(py::module &m) {
    m.def("add", &add, "A function that adds two numbers");
};
