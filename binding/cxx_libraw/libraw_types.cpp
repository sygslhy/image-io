#include "libraw/libraw_types.h"
#include "libraw/libraw.h" // NOLINT(misc-include-cleaner)

#include "pybind11/buffer_info.h"
#include "pybind11/numpy.h"
#include "pybind11/pybind11.h" // NOLINT
#include "pybind11/stl.h"

namespace py = pybind11;

void initTypes(py::module &mod) { // NOLINT(misc-use-internal-linkage)

    py::enum_<LibRaw_errors>(mod, "LibRaw_errors", "Libraw return error code")
            .value("LIBRAW_SUCCESS", LibRaw_errors::LIBRAW_SUCCESS, "No error; function terminated successfully.")
            .value("LIBRAW_UNSPECIFIED_ERROR",
                   LibRaw_errors::LIBRAW_UNSPECIFIED_ERROR,
                   "An unknown error has been encountered. This code should never be generated.")
            .value("LIBRAW_FILE_UNSUPPORTED",
                   LibRaw_errors::LIBRAW_FILE_UNSUPPORTED,
                   "Unsupported file format (attempt to open a RAW file with a format unknown to the program).");

    py::class_<libraw_image_sizes_t> rawImageSizes(mod, "RawImageSizes", py::is_final());

    rawImageSizes.def(py::init<>())
            .def_readwrite("raw_height",
                           &libraw_image_sizes_t::raw_height,
                           "uint16: Full size height of RAW image (including the frame) in pixels.")
            .def_readwrite("raw_width",
                           &libraw_image_sizes_t::raw_width,
                           "uint16: Full size width of RAW image (including the frame) in pixels.")
            .def_readwrite("height",
                           &libraw_image_sizes_t::height,
                           "uint16: Size height of visible (\"meaningful\") part of the image (without the frame).")
            .def_readwrite("width",
                           &libraw_image_sizes_t::width,
                           "uint16: Size width of visible (\"meaningful\") part of the image (without the frame).")
            .def_readwrite("top_margin",
                           &libraw_image_sizes_t::top_margin,
                           "uint16: Coordinates of the top corner of the frame (the second corner is calculated from "
                           "the full size of the image and size of its visible part).")
            .def_readwrite("left_margin",
                           &libraw_image_sizes_t::left_margin,
                           "uint16: Coordinates of the left corner of the frame (the second corner is calculated from "
                           "the full size of the image and size of its visible part).")
            .def_readwrite("iheight",
                           &libraw_image_sizes_t::iheight,
                           "uint16: Size height of the output image (may differ from height/width for cameras that "
                           "require image rotation or have non-square pixels).")
            .def_readwrite("iwidth",
                           &libraw_image_sizes_t::iwidth,
                           "uint16: Size width of the output image (may differ from height/width for cameras that "
                           "require image rotation or have non-square pixels).")
            .def_readwrite(
                    "raw_pitch", &libraw_image_sizes_t::raw_pitch, "unsigned: Full size of raw data row in bytes.")
            .def_readwrite("pixel_aspect",
                           &libraw_image_sizes_t::pixel_aspect,
                           "double: Pixel width/height ratio. If it is not unity, scaling of the image along one of "
                           "the axes is required during output.")
            .def_readwrite("flip",
                           &libraw_image_sizes_t::flip,
                           "int: Image orientation (0 if does not require rotation; 3 if requires 180-deg rotation; 5 "
                           "if 90 deg counterclockwise, 6 if 90 deg clockwise).")
            .def_property(
                    "mask",
                    [](libraw_image_sizes_t &sizes) -> pybind11::array {
                        auto dtype = pybind11::dtype(pybind11::format_descriptor<int>::format());
                        return pybind11::array(dtype, {8, 4}, {sizeof(int)}, sizes.mask, nullptr);
                    },
                    [](libraw_image_sizes_t &sizes) {})
            .def_readwrite("raw_aspect", &libraw_image_sizes_t::raw_aspect, "unsigned: Full Raw width/height ratio..")
            .def_property(
                    "raw_inset_crops",
                    [](libraw_image_sizes_t &sizes) -> pybind11::array {
                        auto dtype = pybind11::dtype(pybind11::format_descriptor<libraw_raw_inset_crop_t>::format());
                        return pybind11::array(
                                dtype, {2}, {sizeof(libraw_raw_inset_crop_t)}, sizes.raw_inset_crops, nullptr);
                    },
                    [](libraw_image_sizes_t &sizes) {});

    py::class_<libraw_rawdata_t> rawData(mod, "RawData", py::buffer_protocol());
    rawData.def(py::init<>())
            .def_readwrite("sizes", &libraw_rawdata_t::sizes, "class libraw_image_sizes_t: Image Dimensions")
            .def_buffer([](libraw_rawdata_t &mod) -> py::buffer_info {
                return py::buffer_info(mod.raw_image,                               /* Pointer to buffer */
                                       sizeof(uint16_t),                            /* Size of one scalar */
                                       py::format_descriptor<uint16_t>::format(),   /* Python struct-style
                                                                                       format descriptor */
                                       2,                                           /* Number of dimensions */
                                       {mod.sizes.raw_height, mod.sizes.raw_width}, /* Buffer dimensions */
                                       {sizeof(uint16_t) * mod.sizes.raw_width, /* Strides (in bytes) for each index */
                                        sizeof(uint16_t)});
            });

    py::class_<libraw_data_t> mainData(mod, "libraw_data_t", py::is_final(), "Main Data Structure of LibRaw");
    mainData.def(py::init<>())
            .def_readwrite("rawdata", &libraw_data_t::rawdata, "holds unpacked RAW data")
            .def_readwrite(
                    "sizes", &libraw_data_t::sizes, "The structure describes the geometrical parameters of the image");

    py::class_<LibRaw> libRaw(mod, "LibRaw", py::is_final(), "libraw processor class");
    libRaw.def(py::init<>())
            .def_readwrite("imgdata", &LibRaw::imgdata, "Main Data Structure of LibRaw")
            .def("open_file",
                 py::overload_cast<const char *>(&LibRaw::open_file),
                 "open raw image from file with filename")
            .def("unpack",
                 &LibRaw::unpack,
                 "Unpacks the RAW files of the image, calculates the black level (not for all formats). The results "
                 "are placed in imgdata.image.");
};
