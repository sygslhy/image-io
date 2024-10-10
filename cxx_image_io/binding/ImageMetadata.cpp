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
            .def("serialize",
                 [](const ImageMetadata &meta)
                 {
                     auto fileInfo = py::cast(meta.fileInfo);
                     auto shootingParams = py::cast(meta.shootingParams);
                     auto cameraControls = py::cast(meta.cameraControls);
                     py::dict dict;
                     dict["fileInfo"] = fileInfo.attr("serialize")();
                     dict["shootingParams"] = shootingParams.attr("serialize")();
                     dict["cameraControls"] = cameraControls.attr("serialize")();
                     return dict;
                 })
            .def("__repr__",
                 [](const ImageMetadata &meta)
                 {
                     auto obj = py::cast(meta);
                     auto d = obj.attr("serialize")();
                     return py::str(d);
                 });

        py::class_<ImageMetadata::ROI>(imageMetadata, "ROI", py::is_final())
            .def(py::init<>())
            .def_readwrite("x", &ImageMetadata::ROI::x)
            .def_readwrite("y", &ImageMetadata::ROI::y)
            .def_readwrite("width", &ImageMetadata::ROI::width)
            .def_readwrite("height", &ImageMetadata::ROI::height)
            .def("serialize",
                 [](const ImageMetadata::ROI &roi)
                 {
                     py::list list;
                     list.append(roi.x);
                     list.append(roi.y);
                     list.append(roi.width);
                     list.append(roi.height);
                     return list;
                 })
            .def("__repr__",
                 [](const ImageMetadata::ROI &roi)
                 {
                     auto d = py::cast(roi).attr("serialize")();
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
            .def("serialize",
                 [](const ImageMetadata::FileInfo &fileInfo)
                 {
                     py::dict dict;
                     if (fileInfo.width)
                         dict["width"] = *fileInfo.width;
                     if (fileInfo.height)
                         dict["height"] = *fileInfo.height;
                     if (fileInfo.pixelPrecision)
                         dict["pixelPrecision"] = *fileInfo.pixelPrecision;
                     if (fileInfo.fileFormat)
                         dict["fileFormat"] = py::str(cxximg::toString(*fileInfo.fileFormat));
                     if (fileInfo.imageLayout)
                         dict["imageLayout"] = py::str(cxximg::toString(*fileInfo.imageLayout));
                     if (fileInfo.pixelType)
                         dict["pixelType"] = py::str(cxximg::toString(*fileInfo.pixelType));
                     if (fileInfo.pixelRepresentation)
                         dict["pixelRepresentation"] = py::str(cxximg::toString(*fileInfo.pixelRepresentation));
                     if (fileInfo.widthAlignment)
                         dict["widthAlignment"] = *fileInfo.widthAlignment;
                     if (fileInfo.heightAlignment)
                         dict["heightAlignment"] = *fileInfo.heightAlignment;
                     if (fileInfo.sizeAlignment)
                         dict["sizeAlignment"] = *fileInfo.sizeAlignment;
                     return dict;
                 })
            .def("__repr__",
                 [](const ImageMetadata::FileInfo &fileInfo)
                 {
                     auto d = py::cast(fileInfo).attr("serialize")();
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
            .def("serialize",
                 [](const ImageMetadata::ShootingParams &shootingParams)
                 {
                     py::dict dict;
                     if (shootingParams.aperture)
                         dict["aperture"] = py::float_(*shootingParams.aperture);
                     if (shootingParams.exposureTime)
                         dict["exposureTime"] = py::float_(*shootingParams.exposureTime);
                     if (shootingParams.sensitivity)
                         dict["sensitivity"] = py::float_(*shootingParams.sensitivity);
                     if (shootingParams.totalGain)
                         dict["totalGain"] = py::float_(*shootingParams.totalGain);
                     if (shootingParams.sensorGain)
                         dict["sensorGain"] = py::float_(*shootingParams.sensorGain);
                     if (shootingParams.ispGain)
                         dict["ispGain"] = py::float_(*shootingParams.ispGain);
                     if (shootingParams.zoom)
                         dict["zoom"] = py::cast(shootingParams.zoom).attr("serialize")();
                     return dict;
                 })
            .def("__repr__",
                 [](const ImageMetadata::ShootingParams &shootingParams)
                 {
                     auto d = py::cast(shootingParams).attr("serialize")();
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
                           &ImageMetadata::CameraControls::faceDetection)
            .def("serialize",
                 [](const ImageMetadata::CameraControls &cameraControls)
                 {
                     py::dict dict;
                     dict["whiteBalance"] = py::cast(cameraControls.whiteBalance).attr("serialize")();
                     dict["colorShading"] = py::cast(cameraControls.colorShading).attr("serialize")();

                     if (cameraControls.faceDetection)
                     {
                         py::list faces;
                         for (const auto &v : *cameraControls.faceDetection)
                         {
                             py::list roi = py::cast(v).attr("serialize")();
                             faces.append(roi);
                         }
                         dict["faceDetection"] = faces;
                     }
                     return dict;
                 })
            .def("__repr__",
                 [](const ImageMetadata::ShootingParams &shootingParams)
                 {
                     auto d = py::cast(shootingParams).attr("serialize")();
                     return py::str(d);
                 });

        py::class_<ImageMetadata::WhiteBalance> whiteBalance(
            imageMetadata, "WhiteBalance", py::is_final());
        whiteBalance.def(py::init<>())
            .def_readwrite("gainR", &ImageMetadata::WhiteBalance::gainR)
            .def_readwrite("gainB", &ImageMetadata::WhiteBalance::gainB)
            .def("serialize",
                 [](const ImageMetadata::WhiteBalance &whiteBalance)
                 {
                     py::list list;
                     list.append(whiteBalance.gainR);
                     list.append(whiteBalance.gainB);
                     return list;
                 })
            .def("__repr__",
                 [](const ImageMetadata::WhiteBalance &whiteBalance)
                 {
                     auto d = py::cast(whiteBalance).attr("serialize")();
                     return py::str(d);
                 });

        py::class_<ImageMetadata::ColorShading> colorShading(
            imageMetadata, "ColorShading", py::is_final());
        colorShading.def(py::init<>())
            .def_readwrite("gainR", &ImageMetadata::ColorShading::gainR)
            .def_readwrite("gainB", &ImageMetadata::ColorShading::gainB)
            .def("serialize",
                 [](const ImageMetadata::ColorShading &colorShading)
                 {
                     if (colorShading.gainR.numCols() != colorShading.gainB.numCols() || colorShading.gainR.numRows() != colorShading.gainB.numRows())
                     {
                         throw std::runtime_error("color Shading must have the same cols and rows size");
                     }
                     py::list listR;
                     py::list listB;
                     for (int y = 0; y < colorShading.gainR.numRows(); ++y)
                     {
                         py::list lineR;
                         py::list lineB;
                         for (int x = 0; x < colorShading.gainR.numCols(); ++x)
                         {
                             lineR.append(colorShading.gainR(x, y));
                             lineB.append(colorShading.gainB(x, y));
                         }
                         listR.append(lineR);
                         listB.append(lineB);
                     }
                     py::list listColorShading;
                     listColorShading.append(listR);
                     listColorShading.append(listB);
                     return listColorShading;
                 })
            .def("__repr__",
                 [](const ImageMetadata::ColorShading &colorShading)
                 {
                     auto d = py::cast(colorShading).attr("serialize")();
                     return py::str(d);
                 });
    }

} // namespace cxximg
