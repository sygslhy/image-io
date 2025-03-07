#include "libraw/libraw.h" // NOLINT(misc-include-cleaner)
#include "libraw/libraw_types.h"

#include "pybind11/buffer_info.h"
#include "pybind11/numpy.h"
#include "pybind11/pybind11.h" // NOLINT
#include "pybind11/stl.h"      // NOLINT(misc-include-cleaner)

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
            .def_readwrite("raw_aspect", &libraw_image_sizes_t::raw_aspect, "unsigned: Full Raw width/height ratio..");

    py::class_<libraw_rawdata_t> rawData(mod, "RawData", py::buffer_protocol());
    rawData.def(py::init<>())
            .def_readwrite("sizes", &libraw_rawdata_t::sizes, "class libraw_image_sizes_t: Image Dimensions")
            .def_buffer([](libraw_rawdata_t &mod) -> py::buffer_info {
                if (mod.color.raw_bps > 8) {
                    return py::buffer_info(
                            mod.raw_image,                               /* Pointer to buffer */
                            sizeof(uint16_t),                            /* Size of one scalar */
                            py::format_descriptor<uint16_t>::format(),   /* Python struct-style
                                                                            format descriptor */
                            2,                                           /* Number of dimensions */
                            {mod.sizes.raw_height, mod.sizes.raw_width}, /* Buffer dimensions */
                            {sizeof(uint16_t) * mod.sizes.raw_width,     /* Strides (in bytes) for each index */
                             sizeof(uint16_t)});
                }
                return py::buffer_info(mod.raw_image,                               /* Pointer to buffer */
                                       sizeof(uint8_t),                             /* Size of one scalar */
                                       py::format_descriptor<uint8_t>::format(),    /* Python struct-style
                                                                                        format descriptor */
                                       2,                                           /* Number of dimensions */
                                       {mod.sizes.raw_height, mod.sizes.raw_width}, /* Buffer dimensions */
                                       {sizeof(uint8_t) * mod.sizes.raw_width, /* Strides (in bytes) for each index */
                                        sizeof(uint8_t)});
            });

    py::class_<libraw_output_params_t> postProcessingParams(mod, "PostprocessingParams", py::is_final());
    postProcessingParams.def(py::init<>())
            .def_readwrite("bright", &libraw_output_params_t::bright, "float: Brightness (default 1.0).")
            .def_readwrite("user_sat", &libraw_output_params_t::user_sat, "int: White level / Saturation adjustment.")
            .def_readwrite("user_black", &libraw_output_params_t::user_black, "int: custom black level.");

    py::class_<libraw_dng_levels_t> dngLevels(mod, "dngLevels", py::is_final());
    dngLevels.def(py::init<>())
            .def_readwrite("baseline_exposure", &libraw_dng_levels_t::baseline_exposure, "float： ISP Gain in log")
            .def_property(
                    "asshotneutral",
                    [](libraw_dng_levels_t &self) -> pybind11::array {
                        auto dtype = pybind11::dtype(pybind11::format_descriptor<float>::format());
                        return pybind11::array(dtype, {4}, {sizeof(float)}, self.asshotneutral, nullptr);
                    },                                // getter
                    [](libraw_dng_levels_t &self) {}) // setter
            ;

    py::class_<libraw_colordata_t> colorData(mod, "ColorData", py::is_final());
    colorData.def(py::init<>())
            .def_readwrite("raw_bps",
                           &libraw_colordata_t::raw_bps,
                           "unsigned: RAW bits per pixel (PhaseOne: Raw format used).")
            .def_readwrite("black", &libraw_colordata_t::black, "unsigned: Black level.")
            .def_readwrite(
                    "data_maximum",
                    &libraw_colordata_t::data_maximum,
                    "unsigned: Maximum pixel value in current file. Calculated at raw2image or dcraw_process() calls.")
            .def_readwrite("maximum",
                           &libraw_colordata_t::maximum,
                           "unsigned: Maximum pixel value. Calculated from the data for most cameras, hardcoded for "
                           "others. This value may be changed on postprocessing stage.")
            .def_readwrite("fmaximum",
                           &libraw_colordata_t::fmaximum,
                           "float: Maximum pixel value in real image for floating data files.")
            .def_readwrite("dng_levels", &libraw_colordata_t::dng_levels, "DNG black/white levels, analog balance, WB")
            .def_property(
                    "cam_mul",
                    [](libraw_colordata_t &color) -> pybind11::array {
                        auto dtype = pybind11::dtype(pybind11::format_descriptor<float>::format());
                        return pybind11::array(dtype, {4}, {sizeof(float)}, color.cam_mul, nullptr);
                    },                                // getter
                    [](libraw_colordata_t &color) {}) // setter
            .def_property(
                    "cmatrix",
                    [](libraw_colordata_t &color) -> pybind11::array {
                        auto dtype = pybind11::dtype(pybind11::format_descriptor<float>::format());
                        return pybind11::array(
                                dtype, {3, 4}, {sizeof(float) * 4, sizeof(float)}, color.cmatrix, nullptr);
                    },                                // getter
                    [](libraw_colordata_t &color) {}) // setter
            .def_property(
                    "ccm",
                    [](libraw_colordata_t &color) -> pybind11::array {
                        auto dtype = pybind11::dtype(pybind11::format_descriptor<float>::format());
                        return pybind11::array(dtype, {3, 4}, {sizeof(float) * 4, sizeof(float)}, color.ccm, nullptr);
                    },                                // getter
                    [](libraw_colordata_t &color) {}) // setter
            .def_property(
                    "rgb_cam",
                    [](libraw_colordata_t &color) -> pybind11::array {
                        auto dtype = pybind11::dtype(pybind11::format_descriptor<float>::format());
                        return pybind11::array(
                                dtype, {3, 4}, {sizeof(float) * 4, sizeof(float)}, color.rgb_cam, nullptr);
                    },                                // getter
                    [](libraw_colordata_t &color) {}) // setter
            ;

    py::class_<libraw_iparams_t> mainParameters(mod, "MainParameters", py::is_final(), "Main Parameters of the Image");

    mainParameters.def(py::init<>())
            .def_property(
                    "make",
                    [](const libraw_iparams_t &self) { return std::string(self.make); }, // getter
                    [](libraw_iparams_t &self, const std::string &new_data) {            // setter
                        std::strncpy(self.make, new_data.c_str(), sizeof(self.make) - 1);
                        self.make[sizeof(self.make) - 1] = '\0';
                    },
                    "char[64]: Camera manufacturer.")
            .def_property(
                    "model",
                    [](const libraw_iparams_t &self) { return std::string(self.model); }, // getter
                    [](libraw_iparams_t &self, const std::string &new_data) {             // setter
                        std::strncpy(self.model, new_data.c_str(), sizeof(self.model) - 1);
                        self.model[sizeof(self.model) - 1] = '\0';
                    },
                    "char[64]: Camera model.")
            .def_property(
                    "normalized_make",
                    [](const libraw_iparams_t &self) { return std::string(self.normalized_make); }, // getter
                    [](libraw_iparams_t &self, const std::string &new_data) {                       // setter
                        std::strncpy(self.normalized_make, new_data.c_str(), sizeof(self.normalized_make) - 1);
                        self.normalized_make[sizeof(self.normalized_make) - 1] = '\0';
                    },
                    "char[64]: Primary vendor name.")
            .def_property(
                    "normalized_model",
                    [](const libraw_iparams_t &self) { return std::string(self.normalized_model); }, // getter
                    [](libraw_iparams_t &self, const std::string &new_data) {                        // setter
                        std::strncpy(self.normalized_model, new_data.c_str(), sizeof(self.normalized_model) - 1);
                        self.normalized_model[sizeof(self.normalized_model) - 1] = '\0';
                    },
                    "char[64]: Primary model name.")
            .def_property(
                    "software",
                    [](const libraw_iparams_t &self) { return std::string(self.software); }, // getter
                    [](libraw_iparams_t &self, const std::string &new_data) {                // setter
                        std::strncpy(self.software, new_data.c_str(), sizeof(self.software) - 1);
                        self.software[sizeof(self.software) - 1] = '\0';
                    },
                    "char[64]: Softwary name/version.")
            .def_property(
                    "cdesc",
                    [](const libraw_iparams_t &self) { return std::string(self.cdesc); }, // getter
                    [](libraw_iparams_t &self, const std::string &new_data) {             // setter
                        std::strncpy(self.cdesc, new_data.c_str(), sizeof(self.cdesc) - 1);
                        self.cdesc[sizeof(self.cdesc) - 1] = '\0';
                    },
                    "char[5]:Description of colors numbered from 0 to 3 (RGBG,RGBE,GMCY, or GBTG).")
            .def_readwrite("filters", &libraw_iparams_t::filters, "Bit mask describing the order of color pixels ");

    py::class_<libraw_data_t> mainData(mod, "libraw_data_t", py::is_final(), "Main Data Structure of LibRaw");
    mainData.def(py::init<>())
            .def_readwrite("rawdata", &libraw_data_t::rawdata, "holds unpacked RAW data")
            .def_readwrite(
                    "sizes", &libraw_data_t::sizes, "The structure describes the geometrical parameters of the image")
            .def_readwrite("color", &libraw_data_t::color, "Color Information")
            .def_readwrite("params", &libraw_data_t::params, "management of dcraw-style postprocessing")
            .def_readwrite("idata", &libraw_data_t::idata, "Main Parameters of the Image")
            .def_readwrite("other", &libraw_data_t::other, "Other Parameters of the Image");

    py::class_<LibRaw> libRaw(mod, "LibRaw", py::is_final(), "libraw processor class");
    libRaw.def(py::init<>())
            .def_readwrite("imgdata", &LibRaw::imgdata, "Main Data Structure of LibRaw")
            .def("open_file",
                 py::overload_cast<const char *>(&LibRaw::open_file),
                 "open raw image from file with filename")
            .def("unpack",
                 &LibRaw::unpack,
                 "Unpacks the RAW files of the image, calculates the black level (not for all formats). The results "
                 "are placed in imgdata.image.")
            .def("COLOR",
                 &LibRaw::COLOR,
                 "This call returns pixel color (color component number) in bayer pattern at row,col. The returned "
                 "value is in 0..3 range for 4-component Bayer (RGBG2, CMYG and so on) and in 0..2 range for 3-color "
                 "data.");
};
