#include "model/ExifMetadata.h"

#include "pybind11/cast.h" // NOLINT(misc-include-cleaner)
#include "pybind11/pybind11.h"
#include "pybind11/pytypes.h"
#include "pybind11/stl.h" // NOLINT(misc-include-cleaner)

#include <cstdint>
#include <memory>

namespace py = pybind11;

namespace cxximg {

void initExif(py::module &mod) { // NOLINT(misc-use-internal-linkage)
    py::class_<ExifMetadata> exifMetadata(mod, "ExifMetadata", py::is_final());

    exifMetadata.def(py::init<>())
            .def_readwrite("imageWidth", &ExifMetadata::imageWidth, "uint16: Image width reported in EXIF data")
            .def_readwrite("imageHeight", &ExifMetadata::imageHeight, "uint16: Image height reported in EXIF data")
            .def_readwrite("imageDescription", &ExifMetadata::imageDescription, "str: Image description")
            .def_readwrite("make", &ExifMetadata::make, "str: Camera manufacturer's name")
            .def_readwrite("model", &ExifMetadata::model, "str: Camera model")
            .def_readwrite("orientation", &ExifMetadata::orientation, "uint16: Image orientation")
            .def_readwrite("software", &ExifMetadata::software, "str: Software used")
            .def_readwrite(
                    "dateTimeOriginal", &ExifMetadata::dateTimeOriginal, "str: Date when original image was taken")
            .def_readwrite(
                    "brightnessValue", &ExifMetadata::brightnessValue, "class SRational: The value of brightness")
            .def_readwrite("exposureBiasValue", &ExifMetadata::exposureBiasValue, "class SRational: The exposure bias")
            .def_readwrite("exposureTime", &ExifMetadata::exposureTime, "class Rational: Exposure time in seconds")
            .def_readwrite("fNumber", &ExifMetadata::fNumber, "class Rational: F/stop")
            .def_readwrite("isoSpeedRatings", &ExifMetadata::isoSpeedRatings, "uint16: ISO speed")
            .def_readwrite(
                    "focalLength", &ExifMetadata::focalLength, "class Rational: Focal length of lens in millimeters")
            .def_readwrite("focalLengthIn35mmFilm",
                           &ExifMetadata::focalLengthIn35mmFilm,
                           "class Rational: Focal length of lens in millimeters "
                           "(35mm equivalent)")
            .def(
                    "serialize",
                    [](const ExifMetadata &exif) {
                        py::dict dict;
                        if (exif.imageWidth) {
                            dict["imageWidth"] = *exif.imageWidth;
                        }
                        if (exif.imageHeight) {
                            dict["imageHeight"] = *exif.imageHeight;
                        }
                        if (exif.imageDescription) {
                            dict["imageDescription"] = py::str(*exif.imageDescription);
                        }
                        if (exif.make) {
                            dict["make"] = py::str(*exif.make);
                        }
                        if (exif.model) {
                            dict["model"] = py::str(*exif.model);
                        }
                        if (exif.orientation) {
                            dict["orientation"] = *exif.orientation;
                        }
                        if (exif.software) {
                            dict["software"] = py::str(*exif.software);
                        }
                        if (exif.exposureTime) {
                            dict["exposureTime"] = py::cast(exif.exposureTime).attr("serialize")();
                        }
                        if (exif.fNumber) {
                            dict["fNumber"] = py::cast(exif.fNumber).attr("serialize")();
                        }
                        if (exif.isoSpeedRatings) {
                            dict["isoSpeedRatings"] = *exif.isoSpeedRatings;
                        }
                        if (exif.dateTimeOriginal) {
                            dict["dateTimeOriginal"] = py::str(*exif.dateTimeOriginal);
                        }
                        if (exif.brightnessValue) {
                            dict["brightnessValue"] = py::cast(exif.brightnessValue).attr("serialize")();
                        }
                        if (exif.exposureBiasValue) {
                            dict["exposureBiasValue"] = py::cast(exif.exposureBiasValue).attr("serialize")();
                        }
                        if (exif.focalLength) {
                            dict["focalLength"] = py::cast(exif.focalLength).attr("serialize")();
                        }
                        if (exif.focalLengthIn35mmFilm) {
                            dict["focalLengthIn35mmFilm"] = *exif.focalLengthIn35mmFilm;
                        }
                        return dict;
                    },
                    "Serialize the exifMetadata to python dict type")
            .def("__repr__", [](const ExifMetadata &exif) {
                auto dict = py::cast(exif).attr("serialize")();
                return py::str(dict);
            });

    py::class_<ExifMetadata::Rational>(exifMetadata, "Rational", py::is_final())
            .def(py::init([](uint32_t num, uint32_t denum) {
                std::unique_ptr<ExifMetadata::Rational> rational(new ExifMetadata::Rational());
                rational->numerator = num;
                rational->denominator = denum;
                return rational;
            }))
            .def_readwrite("numerator", &ExifMetadata::Rational::numerator)
            .def_readwrite("denominator", &ExifMetadata::Rational::denominator)
            .def("asDouble", &ExifMetadata::Rational::asDouble)
            .def("asFloat", &ExifMetadata::Rational::asFloat)
            .def("serialize",
                 [](const ExifMetadata::Rational &rational) {
                     py::list list;
                     list.append(rational.numerator);
                     list.append(rational.denominator);
                     return list;
                 })
            .def("__repr__", [](const ExifMetadata::Rational &rational) {
                auto dict = py::cast(rational).attr("serialize")();
                return py::str(dict);
            });

    py::class_<ExifMetadata::SRational>(exifMetadata, "SRational", py::is_final())
            .def(py::init([](int32_t num, int32_t denum) {
                std::unique_ptr<ExifMetadata::SRational> srational(new ExifMetadata::SRational());
                srational->numerator = num;
                srational->denominator = denum;
                return srational;
            }))
            .def_readwrite("numerator", &ExifMetadata::SRational::numerator)
            .def_readwrite("denominator", &ExifMetadata::SRational::denominator)
            .def("asDouble", &ExifMetadata::SRational::asDouble)
            .def("asFloat", &ExifMetadata::SRational::asFloat)
            .def("serialize",
                 [](const ExifMetadata::SRational &rational) {
                     py::list list;
                     list.append(rational.numerator);
                     list.append(rational.denominator);
                     return list;
                 })
            .def("__repr__", [](const ExifMetadata::SRational &rational) {
                auto dict = py::cast(rational).attr("serialize")();
                return py::str(dict);
            });
}
} // namespace cxximg