#include "libraw/libraw.h" // NOLINT(misc-include-cleaner)

#include "pybind11/pybind11.h" // NOLINT

namespace py = pybind11;

void initMetadata(py::module &mod) { // NOLINT(misc-use-internal-linkage)

    py::class_<libraw_imgother_t> otherParameters(
            mod, "OtherParameters", py::is_final(), "Other Parameters of the Image");

    otherParameters.def(py::init<>())
            .def_readwrite("iso_speed", &libraw_imgother_t::iso_speed, "float: ISO sensitivity.")
            .def_readwrite("shutter", &libraw_imgother_t::shutter, "float: Shutter speed.")
            .def_readwrite("aperture", &libraw_imgother_t::aperture, "float Aperture.")
            .def_readwrite("focal_len", &libraw_imgother_t::focal_len, "float: Focal length.")
            .def_readwrite("timestamp", &libraw_imgother_t::timestamp, "time_t : Date of shooting.")
            .def_readwrite("shot_order", &libraw_imgother_t::shot_order, "unsigned : Serial number of image.")
            .def_property(
                    "desc",
                    [](const libraw_imgother_t &s) { return std::string(s.desc); }, // getter
                    [](libraw_imgother_t &s, const std::string &new_data) {         // setter
                        std::strncpy(s.desc, new_data.c_str(), sizeof(s.desc) - 1);
                        s.desc[sizeof(s.desc) - 1] = '\0';
                    },
                    "char [512]: Image description.")
            .def_property(
                    "artist",
                    [](const libraw_imgother_t &s) { return std::string(s.artist); }, // getter
                    [](libraw_imgother_t &s, const std::string &new_data) {           // setter
                        std::strncpy(s.artist, new_data.c_str(), sizeof(s.artist) - 1);
                        s.artist[sizeof(s.artist) - 1] = '\0';
                    },
                    "char artist[64]: Author of image.");

    py::class_<libraw_iparams_t> mainParameters(mod, "MainParameters", py::is_final(), "Main Parameters of the Image");

    mainParameters.def(py::init<>())
            .def_property(
                    "make",
                    [](const libraw_iparams_t &s) { return std::string(s.make); }, // getter
                    [](libraw_iparams_t &s, const std::string &new_data) {         // setter
                        std::strncpy(s.make, new_data.c_str(), sizeof(s.make) - 1);
                        s.make[sizeof(s.make) - 1] = '\0';
                    },
                    "char[64]: Camera manufacturer.")
            .def_property(
                    "model",
                    [](const libraw_iparams_t &s) { return std::string(s.model); }, // getter
                    [](libraw_iparams_t &s, const std::string &new_data) {          // setter
                        std::strncpy(s.model, new_data.c_str(), sizeof(s.model) - 1);
                        s.model[sizeof(s.model) - 1] = '\0';
                    },
                    "char[64]: Camera model.")
            .def_property(
                    "normalized_make",
                    [](const libraw_iparams_t &s) { return std::string(s.normalized_make); }, // getter
                    [](libraw_iparams_t &s, const std::string &new_data) {                    // setter
                        std::strncpy(s.normalized_make, new_data.c_str(), sizeof(s.normalized_make) - 1);
                        s.normalized_make[sizeof(s.normalized_make) - 1] = '\0';
                    },
                    "char[64]: Primary vendor name.")
            .def_property(
                    "normalized_model",
                    [](const libraw_iparams_t &s) { return std::string(s.normalized_model); }, // getter
                    [](libraw_iparams_t &s, const std::string &new_data) {                     // setter
                        std::strncpy(s.normalized_model, new_data.c_str(), sizeof(s.normalized_model) - 1);
                        s.normalized_model[sizeof(s.normalized_model) - 1] = '\0';
                    },
                    "char[64]: Primary model name.")
            .def_property(
                    "software",
                    [](const libraw_iparams_t &s) { return std::string(s.software); }, // getter
                    [](libraw_iparams_t &s, const std::string &new_data) {             // setter
                        std::strncpy(s.software, new_data.c_str(), sizeof(s.software) - 1);
                        s.software[sizeof(s.software) - 1] = '\0';
                    },
                    "char[64]: Softwary name/version.");

    py::class_<libraw_output_params_t> postprocessingParams(mod, "PostprocessingParams", py::is_final());
    postprocessingParams.def(py::init<>())
            .def_readwrite("bright", &libraw_output_params_t::bright, "float: Brightness (default 1.0).");
};