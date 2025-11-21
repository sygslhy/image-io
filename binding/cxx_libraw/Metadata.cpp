#include "libraw/libraw.h" // NOLINT(misc-include-cleaner)

#include "pybind11/pybind11.h" // NOLINT

#include <cstring>
#include <ctime>
#include <string>

namespace py = pybind11;

void initMetadata(py::module &mod) { // NOLINT(misc-use-internal-linkage)

    py::class_<libraw_imgother_t> otherParameters(
            mod, "OtherParameters", py::is_final(), "Other Parameters of the Image");

    otherParameters.def(py::init<>())
            .def_readwrite("iso_speed", &libraw_imgother_t::iso_speed, "float: ISO sensitivity.")
            .def_readwrite("shutter", &libraw_imgother_t::shutter, "float: Shutter speed.")
            .def_readwrite("aperture", &libraw_imgother_t::aperture, "float Aperture.")
            .def_readwrite("focal_len", &libraw_imgother_t::focal_len, "float: Focal length.")
            .def_readwrite("shot_order", &libraw_imgother_t::shot_order, "unsigned : Serial number of image.")
            .def_property(
                    "timestamp",
                    [](const libraw_imgother_t &self) {
                        std::time_t timestamp = self.timestamp;
                        const std::tm *ptm = std::localtime(&timestamp);
                        char data[32];
                        std::strftime(data, sizeof(data), "%Y:%m:%d %H:%M:%S", ptm);
                        return std::string(data);
                    }, // getter
                    [](libraw_imgother_t &self) {},
                    "str : Date and time of shooting.") // setter
            .def_property(
                    "desc",
                    [](const libraw_imgother_t &other) { return std::string(other.desc); }, // getter
                    [](libraw_imgother_t &other, const std::string &new_data) {             // setter
                        std::strncpy(other.desc, new_data.c_str(), sizeof(other.desc) - 1);
                        other.desc[sizeof(other.desc) - 1] = '\0';
                    },
                    "char [512]: Image description.")
            .def_property(
                    "artist",
                    [](const libraw_imgother_t &other) { return std::string(other.artist); }, // getter
                    [](libraw_imgother_t &other, const std::string &new_data) {               // setter
                        std::strncpy(other.artist, new_data.c_str(), sizeof(other.artist) - 1);
                        other.artist[sizeof(other.artist) - 1] = '\0';
                    },
                    "char artist[64]: Author of image.");
};