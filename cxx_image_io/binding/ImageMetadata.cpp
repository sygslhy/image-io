#include "model/ImageMetadata.h"

#include "pybind11/pybind11.h"
#include "pybind11/stl.h"
#include "pybind11/stl_bind.h"

namespace py = pybind11;

PYBIND11_MAKE_OPAQUE(cxximg::ImageMetadata::SemanticMasks);

namespace cxximg
{

    void init_model(py::module &m)
    {

        py::enum_<FileFormat>(m, "FileFormat", "File format types")
            .value("PLAIN", FileFormat::PLAIN, "Plain Raw format")
            .value("RAW10", FileFormat::RAW10, "Packed 10bit RAW format")
            .value("RAW12", FileFormat::RAW12, "Packed 12bit RAW format");

        py::enum_<PixelRepresentation>(m, "PixelRepresentation")
            .value("UINT8", PixelRepresentation::UINT8)
            .value("UINT16", PixelRepresentation::UINT16)
            .value("FLOAT", PixelRepresentation::FLOAT);



        py::class_<ImageMetadata> imageMetadata(m, "ImageMetadata", py::is_final());
        imageMetadata.def(py::init<>())
            .def_readwrite("fileInfo", &ImageMetadata::fileInfo, "class ImageMetadata.FileInfo: File Information")
            .def_readwrite("exifMetadata", &ImageMetadata::exifMetadata, "class ExifMetadata: Exif metadata")
            .def_readwrite("shootingParams", &ImageMetadata::shootingParams, "class ImageMetadata.ShootingParams: Shooting params")
            .def_readwrite("calibrationData", &ImageMetadata::calibrationData)
            .def_readwrite("cameraControls", &ImageMetadata::cameraControls)
            .def_readwrite("semanticMasks", &ImageMetadata::semanticMasks);
        imageMetadata.def("synchronize", &ImageMetadata::synchronize)
            .def("serialize",
                 [](const ImageMetadata &meta)
                 {
                     py::dict dict;
                     dict["fileInfo"] = py::cast(meta.fileInfo).attr("serialize")();
                     dict["exifMetadata"] = py::cast(meta.exifMetadata).attr("serialize")();
                     dict["shootingParams"] = py::cast(meta.shootingParams).attr("serialize")();
                     dict["cameraControls"] = py::cast(meta.cameraControls).attr("serialize")();
                     dict["calibrationData"] = py::cast(meta.calibrationData).attr("serialize")();
                     py::list masks;
                     for (const auto &pair : meta.semanticMasks)
                     {
                         auto maskData = py::cast(pair.second).attr("serialize")();
                         masks.append(maskData);
                     }
                     dict["semanticMasks"] = masks;
                     return dict;
                 })
            .def("__repr__",
                 [](const ImageMetadata &meta)
                 {
                     auto d = py::cast(meta).attr("serialize")();
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

        py::enum_<SemanticLabel>(m, "SemanticLabel")
            .value("NONE", SemanticLabel::NONE)
            .value("PERSON", SemanticLabel::PERSON)
            .value("SKIN", SemanticLabel::SKIN)
            .value("SKY", SemanticLabel::SKY)
            .value("UNKNOWN", SemanticLabel::UNKNOWN);

        py::bind_map<ImageMetadata::SemanticMasks>(m, "UnorderdMapSemanticMasks");

        py::class_<ImageMetadata::SemanticMask>(imageMetadata, "SemanticMask",
                                                py::is_final())
            .def(py::init<>())
            .def_readwrite("name", &ImageMetadata::SemanticMask::name)
            .def_readwrite("label", &ImageMetadata::SemanticMask::label)
            .def_readwrite("mask", &ImageMetadata::SemanticMask::mask)
            .def("serialize",
                 [](const ImageMetadata::SemanticMask &sematicMask)
                 {
                     py::dict dict;
                     dict["name"] = py::str(sematicMask.name);
                     dict["label"] = py::str(cxximg::toString(sematicMask.label));
                     dict["mask"] = py::cast(sematicMask.mask).attr("serialize")();
                     return dict;
                 })
            .def("__repr__",
                 [](const ImageMetadata::SemanticMask &sematicMask)
                 {
                     auto d = py::cast(sematicMask).attr("serialize")();
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
            .def_readwrite("colorMatrixTarget", &ImageMetadata::CalibrationData::colorMatrixTarget)
            .def("serialize",
                 [](const ImageMetadata::CalibrationData calibData)
                 {
                     py::dict dict;
                     if (calibData.blackLevel)
                         dict["blackLevel"] = *calibData.blackLevel;
                     if (calibData.whiteLevel)
                         dict["whiteLevel"] = *calibData.whiteLevel;
                     if (calibData.vignetting)
                         dict["vignetting"] = py::cast(calibData.vignetting).attr("serialize")();
                     if (calibData.colorMatrix)
                         dict["colorMatrix"] = py::cast(calibData.colorMatrix).attr("serialize")();
                     if (calibData.colorMatrixTarget)
                         dict["colorMatrixTarget"] = py::str(cxximg::toString(*calibData.colorMatrixTarget));
                     return dict;
                 })
            .def("__repr__",
                 [](const ImageMetadata::CalibrationData &calibData)
                 {
                     auto d = py::cast(calibData).attr("serialize")();
                     return py::str(d);
                 });

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
                     if (cameraControls.whiteBalance)
                        dict["whiteBalance"] = py::cast(cameraControls.whiteBalance).attr("serialize")();
                     if (cameraControls.colorShading)
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
                 [](const ImageMetadata::CameraControls &cameraControls)
                 {
                     auto d = py::cast(cameraControls).attr("serialize")();
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
