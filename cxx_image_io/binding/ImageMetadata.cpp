#include "model/ImageMetadata.h"

#include "pybind11/pybind11.h"
#include "pybind11/stl.h"

namespace py = pybind11;

namespace cxximg
{

    void init_model(py::module &m)
    {

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
            .def_readwrite("brightnessValue", &ExifMetadata::brightnessValue)
            .def_readwrite("exposureBiasValue", &ExifMetadata::exposureBiasValue)
            .def_readwrite("exposureTime", &ExifMetadata::exposureTime)
            .def_readwrite("fNumber", &ExifMetadata::fNumber)
            .def_readwrite("isoSpeedRatings", &ExifMetadata::isoSpeedRatings)
            .def_readwrite("focalLength", &ExifMetadata::focalLength)
            .def_readwrite("focalLengthIn35mmFilm", &ExifMetadata::focalLengthIn35mmFilm)
            .def("__repr__",
                 [](const ExifMetadata &exif)
                 {
                    return py::str("ExifMetadata example");

                 });

        py::class_<ExifMetadata::Rational>(exifMetadata, "Rational", py::is_final())
            .def(py::init([](uint32_t n, uint32_t dn)
                          {
            std::unique_ptr<ExifMetadata::Rational> rational(
                new ExifMetadata::Rational());
            rational->numerator = n;
            rational->denominator = dn;
            return rational; }))
            .def_readwrite("numerator", &ExifMetadata::Rational::numerator)
            .def_readwrite("denominator", &ExifMetadata::Rational::denominator)
            .def("asDouble", &ExifMetadata::Rational::asDouble)
            .def("asFloat", &ExifMetadata::Rational::asFloat);

        py::class_<ExifMetadata::SRational>(exifMetadata, "SRational", py::is_final())
            .def(py::init([](int32_t n, int32_t dn)
                          {
            std::unique_ptr<ExifMetadata::SRational> srational(
                new ExifMetadata::SRational());
            srational->numerator = n;
            srational->denominator = dn;
            return srational; }))
            .def_readwrite("numerator", &ExifMetadata::SRational::numerator)
            .def_readwrite("denominator", &ExifMetadata::SRational::denominator)
            .def("asDouble", &ExifMetadata::SRational::asDouble)
            .def("asFloat", &ExifMetadata::SRational::asFloat);

        py::class_<ImageMetadata> imageMetadata(m, "ImageMetadata", py::is_final());
        imageMetadata.def(py::init<>())
            .def_readwrite("fileInfo", &ImageMetadata::fileInfo)
            .def_readwrite("exifMetadata", &ImageMetadata::exifMetadata)
            .def_readwrite("shootingParams", &ImageMetadata::shootingParams)
            .def_readwrite("calibrationData", &ImageMetadata::calibrationData)
            .def_readwrite("cameraControls", &ImageMetadata::cameraControls);
        imageMetadata.def("synchronize", &ImageMetadata::synchronize)
            .def("toDict",
                [](const ImageMetadata &meta){
                    auto fileInfo = py::cast(meta.fileInfo);
                    py::dict dict;
                    dict["fileInfo"] = fileInfo.attr("toDict")();
                    return dict;
                })
            .def("__repr__",
                 [](const ImageMetadata &meta)
                 {
                    auto obj = py::cast(meta);
                    auto d = obj.attr("toDict")();
                    return py::str(d);
                 });

        py::class_<ImageMetadata::ROI>(imageMetadata, "ROI", py::is_final())
            .def(py::init<>())
            .def_readwrite("x", &ImageMetadata::ROI::x)
            .def_readwrite("y", &ImageMetadata::ROI::y)
            .def_readwrite("width", &ImageMetadata::ROI::width)
            .def_readwrite("height", &ImageMetadata::ROI::height)
            .def("toDict",
                [](const ImageMetadata::ROI &roi){
                    py::dict dict;
                    dict["x"] = roi.x;
                    dict["y"] = roi.y;
                    dict["width"] = roi.width;
                    dict["height"] = roi.height;
                    return dict;
                })
            .def("__repr__",
                 [](const ImageMetadata::ROI &roi)
                 {
                    auto d = py::cast(roi).attr("toDict")();
                    return py::str(d);
                 });

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
                           &ImageMetadata::FileInfo::widthAlignment)
            .def_readwrite("heightAlignment",
                           &ImageMetadata::FileInfo::heightAlignment)
            .def_readwrite("sizeAlignment",
                           &ImageMetadata::FileInfo::sizeAlignment)
            .def("toDict",
                [](const ImageMetadata::FileInfo &fileInfo){
                    py::dict dict;
                    dict["width"] = *fileInfo.width;
                    dict["height"] = *fileInfo.height;
                    dict["pixelPrecision"] = *fileInfo.pixelPrecision;
                    dict["fileFormat"] = py::str(cxximg::toString(*fileInfo.fileFormat));
                    dict["imageLayout"] = py::str(cxximg::toString(*fileInfo.imageLayout));
                    dict["pixelType"] = py::str(cxximg::toString(*fileInfo.pixelType));
                    dict["pixelRepresentation"] = py::str(cxximg::toString(*fileInfo.pixelRepresentation));
                    dict["widthAlignment"] = *fileInfo.widthAlignment;
                    dict["heightAlignment"] = *fileInfo.heightAlignment;
                    dict["sizeAlignment"] = *fileInfo.sizeAlignment;
                    return dict;
                })
            .def("__repr__",
                 [](const ImageMetadata::FileInfo &fileInfo)
                 {
                    auto d = py::cast(fileInfo).attr("toDict")();
                    return py::str(d);
                 });

        py::class_<ImageMetadata::ShootingParams>(imageMetadata, "ShootingParams",
                                                  py::is_final())
            .def(py::init<>())
            .def_readwrite("aperture", &ImageMetadata::ShootingParams::aperture)
            .def_readwrite("exposureTime", &ImageMetadata::ShootingParams::exposureTime)
            .def_readwrite("sensitivity", &ImageMetadata::ShootingParams::sensitivity)
            .def_readwrite("totalGain",
                           &ImageMetadata::ShootingParams::totalGain)
            .def_readwrite("sensorGain", &ImageMetadata::ShootingParams::sensorGain)
            .def_readwrite("ispGain", &ImageMetadata::ShootingParams::ispGain)
            .def_readwrite("zoom", &ImageMetadata::ShootingParams::zoom)
            .def("toDict",
                [](const ImageMetadata::ShootingParams &shootingParams){
                    py::dict dict;
                    dict["aperture"] = *shootingParams.aperture;
                    dict["exposureTime"] = *shootingParams.exposureTime;
                    dict["sensitivity"] = *shootingParams.sensitivity;
                    dict["totalGain"] = *shootingParams.totalGain;
                    dict["sensorGain"] = *shootingParams.sensorGain;
                    dict["ispGain"] = *shootingParams.ispGain;
                    dict["zoom"] = py::cast(shootingParams.zoom).attr("toDict")();
                    return dict;
                })
            .def("__repr__",
                 [](const ImageMetadata::ShootingParams &shootingParams)
                 {
                    auto d = py::cast(shootingParams).attr("toDict")();
                    return py::str(d);
                 });

        py::class_<ImageMetadata::CalibrationData>(imageMetadata, "CalibrationData",
                                                   py::is_final())
            .def(py::init<>())
            .def_readwrite("blackLevel", &ImageMetadata::CalibrationData::blackLevel)
            .def_readwrite("whiteLevel", &ImageMetadata::CalibrationData::whiteLevel)
            .def_readwrite("vignetting",
                           &ImageMetadata::CalibrationData::vignetting)
            .def_readwrite("colorMatrix", &ImageMetadata::CalibrationData::colorMatrix)
            .def_readwrite("colorMatrixTarget", &ImageMetadata::CalibrationData::colorMatrixTarget);

        py::class_<ImageMetadata::CameraControls> cameraControls(
            imageMetadata, "CameraControls", py::is_final());
        cameraControls.def(py::init<>())
            .def_readwrite("whiteBalance",
                           &ImageMetadata::CameraControls::whiteBalance)
            .def_readwrite("colorShading",
                           &ImageMetadata::CameraControls::colorShading)
            .def_readwrite("faceDetection",
                           &ImageMetadata::CameraControls::faceDetection);

        py::class_<ImageMetadata::WhiteBalance> whiteBalance(
            imageMetadata, "WhiteBalance", py::is_final());
        whiteBalance.def(py::init<>())
            .def_readwrite("gainR", &ImageMetadata::WhiteBalance::gainR)
            .def_readwrite("gainB", &ImageMetadata::WhiteBalance::gainB);

        py::class_<ImageMetadata::ColorShading> colorShading(
            imageMetadata, "ColorShading", py::is_final());
        colorShading.def(py::init<>())
            .def_readwrite("gainR", &ImageMetadata::ColorShading::gainR)
            .def_readwrite("gainB", &ImageMetadata::ColorShading::gainB);
    }

} // namespace cxximg
