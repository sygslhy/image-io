#include "model/ImageMetadata.h"

#include "pybind11/pybind11.h"
#include "pybind11/stl.h"
namespace py = pybind11;

namespace cxximg {

void init_model(py::module &m) {

    py::enum_<FileFormat>(m, "FileFormat")
        .value("PLAIN", FileFormat::PLAIN)
        .value("RAW10", FileFormat::RAW10)
        .value("RAW12", FileFormat::RAW12);

    py::enum_<PixelRepresentation>(m, "PixelRepresentation")
        .value("UINT8", PixelRepresentation::UINT8)
        .value("UINT16", PixelRepresentation::UINT16)
        .value("FLOAT", PixelRepresentation::FLOAT);

    py::class_<ExifMetadata> exifMetadata(m, "ExifMetadata", py::is_final());

    exifMetadata.def(py::init<>())
        .def_readwrite("imageWidth", &ExifMetadata::imageWidth)
        .def_readwrite("imageHeight", &ExifMetadata::imageHeight)
        .def_readwrite("imageDescription", &ExifMetadata::imageDescription)
        .def_readwrite("make", &ExifMetadata::make)
        .def_readwrite("model", &ExifMetadata::model)
        .def_readwrite("orientation", &ExifMetadata::orientation)
        .def_readwrite("software", &ExifMetadata::software)
        .def_readwrite("dateTimeOriginal", &ExifMetadata::dateTimeOriginal)
        .def_readwrite("exposureTime", &ExifMetadata::exposureTime)
        .def_readwrite("fNumber", &ExifMetadata::fNumber)
        .def_readwrite("isoSpeedRatings", &ExifMetadata::isoSpeedRatings)
        .def_readwrite("focalLength", &ExifMetadata::focalLength)
        .def_readwrite("focalLengthIn35mmFilm", &ExifMetadata::focalLengthIn35mmFilm);

    py::class_<ExifMetadata::Rational>(exifMetadata, "Rational", py::is_final())
        .def(py::init([](uint32_t n, uint32_t dn) {
            std::unique_ptr<ExifMetadata::Rational> rational(
                new ExifMetadata::Rational());
            rational->numerator = n;
            rational->denominator = dn;
            return rational;
        }))
        .def_readwrite("numerator", &ExifMetadata::Rational::numerator)
        .def_readwrite("denominator", &ExifMetadata::Rational::denominator)
        .def("asDouble", &ExifMetadata::Rational::asDouble)
        .def("asFloat", &ExifMetadata::Rational::asFloat);

    py::class_<ImageMetadata> imageMetadata(m, "ImageMetadata", py::is_final());
    imageMetadata.def(py::init<>())
        .def_readwrite("fileInfo", &ImageMetadata::fileInfo)
        .def_readwrite("cameraControls", &ImageMetadata::cameraControls)
        .def_readwrite("exifMetadata", &ImageMetadata::exifMetadata)
        .def_readwrite("shootingParams", &ImageMetadata::shootingParams)
        .def_readwrite("calibrationData", &ImageMetadata::calibrationData);

    py::class_<ImageMetadata::ROI>(imageMetadata, "ROI", py::is_final())
        .def(py::init<>())
        .def_readwrite("x", &ImageMetadata::ROI::x)
        .def_readwrite("y", &ImageMetadata::ROI::y)
        .def_readwrite("width", &ImageMetadata::ROI::width)
        .def_readwrite("height", &ImageMetadata::ROI::height);

    py::class_<ImageMetadata::FileInfo>(imageMetadata, "FileInfo",
                                        py::is_final())
        .def(py::init<>())
        .def_readwrite("width", &ImageMetadata::FileInfo::width)
        .def_readwrite("height", &ImageMetadata::FileInfo::height)
        .def_readwrite("pixelPrecision",
                       &ImageMetadata::FileInfo::pixelPrecision)
        .def_readwrite("fileFormat", &ImageMetadata::FileInfo::fileFormat)
        .def_readwrite("imageLayout", &ImageMetadata::FileInfo::imageLayout)
        .def_readwrite("pixelType", &ImageMetadata::FileInfo::pixelType)
        .def_readwrite("pixelRepresentation",
                       &ImageMetadata::FileInfo::pixelRepresentation)
        .def_readwrite("widthAlignment",
                       &ImageMetadata::FileInfo::widthAlignment);

    py::class_<ImageMetadata::ShootingParams>(imageMetadata, "ShootingParams",
                                        py::is_final())
        .def(py::init<>())
        .def_readwrite("aperture", &ImageMetadata::ShootingParams::aperture)
        .def_readwrite("exposureTime", &ImageMetadata::ShootingParams::exposureTime)
        .def_readwrite("totalGain",
                       &ImageMetadata::ShootingParams::totalGain)
        .def_readwrite("sensorGain", &ImageMetadata::ShootingParams::sensorGain)
        .def_readwrite("ispGain", &ImageMetadata::ShootingParams::ispGain);

    py::class_<ImageMetadata::CalibrationData>(imageMetadata, "CalibrationData",
                                        py::is_final())
        .def(py::init<>())
        .def_readwrite("blackLevel", &ImageMetadata::CalibrationData::blackLevel)
        .def_readwrite("whiteLevel", &ImageMetadata::CalibrationData::whiteLevel)
        .def_readwrite("luminanceLensShading",
                       &ImageMetadata::CalibrationData::luminanceLensShading)
        .def_readwrite("colorMatrix", &ImageMetadata::CalibrationData::colorMatrix)
        .def_readwrite("colorMatrixTarget", &ImageMetadata::CalibrationData::colorMatrixTarget);


    py::class_<ImageMetadata::CameraControls> cameraControls(
        imageMetadata, "CameraControls", py::is_final());
    cameraControls.def(py::init<>())
        .def_readwrite("whiteBalance",
                       &ImageMetadata::CameraControls::whiteBalance)
        .def_readwrite("colorLensShading",
                       &ImageMetadata::CameraControls::colorLensShading)
        .def_readwrite("faceDetection",
                       &ImageMetadata::CameraControls::faceDetection);

    py::class_<ImageMetadata::WhiteBalance> whiteBalance(
        imageMetadata, "WhiteBalance", py::is_final());
    whiteBalance.def(py::init<>())
        .def_readwrite("gainR", &ImageMetadata::WhiteBalance::gainR)
        .def_readwrite("gainB", &ImageMetadata::WhiteBalance::gainB);

    py::class_<ImageMetadata::ColorLensShading> colorLensShading(
        imageMetadata, "ColorLensShading", py::is_final());
    colorLensShading.def(py::init<>())
        .def_readwrite("gainR", &ImageMetadata::ColorLensShading::gainR)
        .def_readwrite("gainB", &ImageMetadata::ColorLensShading::gainB);
}

} // namespace cxximg
