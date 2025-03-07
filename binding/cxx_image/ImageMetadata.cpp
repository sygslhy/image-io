#include "model/ImageMetadata.h"

#include "pybind11/cast.h"
#include "pybind11/pybind11.h"
#include "pybind11/pytypes.h"
#include "pybind11/stl.h"      // NOLINT(misc-include-cleaner)
#include "pybind11/stl_bind.h" // NOLINT(misc-include-cleaner)

#include <stdexcept>

namespace py = pybind11;

PYBIND11_MAKE_OPAQUE(cxximg::ImageMetadata::SemanticMasks);

namespace cxximg {

void initModel(py::module &mod) { // NOLINT(misc-use-internal-linkage)
    py::enum_<FileFormat>(mod, "FileFormat", "File format types")
            .value("PLAIN", FileFormat::PLAIN, "Plain Raw format")
            .value("RAW10", FileFormat::RAW10, "Packed 10bit RAW format")
            .value("RAW12", FileFormat::RAW12, "Packed 12bit RAW format");

    py::enum_<PixelRepresentation>(mod, "PixelRepresentation")
            .value("UINT8", PixelRepresentation::UINT8)
            .value("UINT16", PixelRepresentation::UINT16)
            .value("FLOAT", PixelRepresentation::FLOAT);

    py::class_<ImageMetadata> imageMetadata(
            mod, "ImageMetadata", "Image Metadata, see class detail with help(ImageMetadata)");
    imageMetadata.def(py::init<>())
            .def_readwrite("fileInfo", &ImageMetadata::fileInfo, "class ImageMetadata.FileInfo: File Information")
            .def_readwrite("exifMetadata", &ImageMetadata::exifMetadata, "class ExifMetadata: Exif metadata")
            .def_readwrite("shootingParams",
                           &ImageMetadata::shootingParams,
                           "class ImageMetadata.ShootingParams: Shooting params")
            .def_readwrite("calibrationData",
                           &ImageMetadata::calibrationData,
                           "class ImageMetadata.Calibration: Calibration data")
            .def_readwrite("cameraControls",
                           &ImageMetadata::cameraControls,
                           "class ImageMetadata.CameraControls: Camera controls")
            .def_readwrite("semanticMasks",
                           &ImageMetadata::semanticMasks,
                           "class ImageMetadata.SemanticMasks: Semantic masks");
    imageMetadata.def("synchronize", &ImageMetadata::synchronize)
            .def("serialize",
                 [](const ImageMetadata &meta) {
                     py::dict dict;
                     dict["fileInfo"] = py::cast(meta.fileInfo).attr("serialize")();
                     dict["exifMetadata"] = py::cast(meta.exifMetadata).attr("serialize")();
                     dict["shootingParams"] = py::cast(meta.shootingParams).attr("serialize")();
                     dict["cameraControls"] = py::cast(meta.cameraControls).attr("serialize")();
                     dict["calibrationData"] = py::cast(meta.calibrationData).attr("serialize")();
                     py::list masks;
                     for (const auto &pair : meta.semanticMasks) {
                         auto maskData = py::cast(pair.second).attr("serialize")();
                         masks.append(maskData);
                     }
                     dict["semanticMasks"] = masks;
                     return dict;
                 })
            .def("__repr__", [](const ImageMetadata &meta) {
                auto dict = py::cast(meta).attr("serialize")();
                return py::str(dict);
            });

    py::class_<ImageMetadata::ROI>(
            imageMetadata, "ROI", py::is_final(), "ROI see class detail with help(ImageMetadata.ROI)")
            .def(py::init<>())
            .def_readwrite("x", &ImageMetadata::ROI::x, "float: x for ROI")
            .def_readwrite("y", &ImageMetadata::ROI::y, "float: y for ROI")
            .def_readwrite("width", &ImageMetadata::ROI::width, "float: width for ROI")
            .def_readwrite("height", &ImageMetadata::ROI::height, "float: height for ROI")
            .def("serialize",
                 [](const ImageMetadata::ROI &roi) {
                     py::list list;
                     list.append(roi.x);
                     list.append(roi.y);
                     list.append(roi.width);
                     list.append(roi.height);
                     return list;
                 })
            .def("__repr__", [](const ImageMetadata::ROI &roi) {
                auto dict = py::cast(roi).attr("serialize")();
                return py::str(dict);
            });

    py::enum_<SemanticLabel>(mod, "SemanticLabel")
            .value("NONE", SemanticLabel::NONE)
            .value("PERSON", SemanticLabel::PERSON)
            .value("SKIN", SemanticLabel::SKIN)
            .value("SKY", SemanticLabel::SKY)
            .value("UNKNOWN", SemanticLabel::UNKNOWN);

    py::bind_map<ImageMetadata::SemanticMasks>(mod, "UnorderdMapSemanticMasks");

    py::class_<ImageMetadata::SemanticMask>(imageMetadata, "SemanticMask", py::is_final())
            .def(py::init<>())
            .def_readwrite("name", &ImageMetadata::SemanticMask::name)
            .def_readwrite("label", &ImageMetadata::SemanticMask::label)
            .def_readwrite("mask", &ImageMetadata::SemanticMask::mask)
            .def("serialize",
                 [](const ImageMetadata::SemanticMask &sematicMask) {
                     py::dict dict;
                     dict["name"] = py::str(sematicMask.name);
                     dict["label"] = py::str(cxximg::toString(sematicMask.label));
                     dict["mask"] = py::cast(sematicMask.mask).attr("serialize")();
                     return dict;
                 })
            .def("__repr__", [](const ImageMetadata::SemanticMask &sematicMask) {
                auto dict = py::cast(sematicMask).attr("serialize")();
                return py::str(dict);
            });

    py::class_<ImageMetadata::FileInfo>(imageMetadata,
                                        "FileInfo",
                                        "File Information, see class detail with help(ImageMetadata.FileInfo)",
                                        py::is_final())
            .def(py::init<>())
            .def_readwrite("width", &ImageMetadata::FileInfo::width, "uint16: Image width")
            .def_readwrite("height", &ImageMetadata::FileInfo::height, "uint16: Image height")
            .def_readwrite("pixelPrecision", &ImageMetadata::FileInfo::pixelPrecision, "uint8: Bit precision of pixel")
            .def_readwrite("fileFormat", &ImageMetadata::FileInfo::fileFormat, "enum FileFormat: File format")
            .def_readwrite("imageLayout", &ImageMetadata::FileInfo::imageLayout, "enum ImageLayout: Image layout")
            .def_readwrite("pixelType", &ImageMetadata::FileInfo::pixelType, "enum PixelType: Pixel type")
            .def_readwrite("pixelRepresentation",
                           &ImageMetadata::FileInfo::pixelRepresentation,
                           "enum PixelRepresentation: Pixel representation")
            .def_readwrite("widthAlignment",
                           &ImageMetadata::FileInfo::widthAlignment,
                           "uint16:  Width alignment (must be a power of 2)")
            .def_readwrite("heightAlignment",
                           &ImageMetadata::FileInfo::heightAlignment,
                           "uint16: Height alignment (must be a power of 2)")
            .def_readwrite("sizeAlignment",
                           &ImageMetadata::FileInfo::sizeAlignment,
                           "uint16:  Buffer size alignment (must be a power of 2)")
            .def("serialize",
                 [](const ImageMetadata::FileInfo &fileInfo) {
                     py::dict dict;
                     if (fileInfo.width) {
                         dict["width"] = *fileInfo.width;
                     }
                     if (fileInfo.height) {
                         dict["height"] = *fileInfo.height;
                     }
                     if (fileInfo.pixelPrecision) {
                         dict["pixelPrecision"] = *fileInfo.pixelPrecision;
                     }
                     if (fileInfo.fileFormat) {
                         dict["fileFormat"] = py::str(cxximg::toString(*fileInfo.fileFormat));
                     }
                     if (fileInfo.imageLayout) {
                         dict["imageLayout"] = py::str(cxximg::toString(*fileInfo.imageLayout));
                     }
                     if (fileInfo.pixelType) {
                         dict["pixelType"] = py::str(cxximg::toString(*fileInfo.pixelType));
                     }
                     if (fileInfo.pixelRepresentation) {
                         dict["pixelRepresentation"] = py::str(cxximg::toString(*fileInfo.pixelRepresentation));
                     }
                     if (fileInfo.widthAlignment) {
                         dict["widthAlignment"] = *fileInfo.widthAlignment;
                     }
                     if (fileInfo.heightAlignment) {
                         dict["heightAlignment"] = *fileInfo.heightAlignment;
                     }
                     if (fileInfo.sizeAlignment) {
                         dict["sizeAlignment"] = *fileInfo.sizeAlignment;
                     }
                     return dict;
                 })
            .def("__repr__", [](const ImageMetadata::FileInfo &fileInfo) {
                auto dict = py::cast(fileInfo).attr("serialize")();
                return py::str(dict);
            });

    py::class_<ImageMetadata::ShootingParams>(
            imageMetadata,
            "ShootingParams",
            "Shooting Params, see class detail with help(ImageMetadata.ShootingParams)",
            py::is_final())
            .def(py::init<>())
            .def_readwrite("aperture", &ImageMetadata::ShootingParams::aperture, "float: Aperture")
            .def_readwrite("exposureTime", &ImageMetadata::ShootingParams::exposureTime, "float: Exposure time")
            .def_readwrite(
                    "sensitivity", &ImageMetadata::ShootingParams::sensitivity, "float: Standard ISO sensitivity")
            .def_readwrite("totalGain",
                           &ImageMetadata::ShootingParams::totalGain,
                           "float: Total applied gain (= sensorGain * ispgain)")
            .def_readwrite("sensorGain", &ImageMetadata::ShootingParams::sensorGain, "float: Sensor gain")
            .def_readwrite("ispGain", &ImageMetadata::ShootingParams::ispGain, "float: ISP gain")
            .def_readwrite("zoom", &ImageMetadata::ShootingParams::zoom, "class ImageMetadata.ROI: Zoom ROI")
            .def("serialize",
                 [](const ImageMetadata::ShootingParams &shootingParams) {
                     py::dict dict;
                     if (shootingParams.aperture) {
                         dict["aperture"] = py::float_(*shootingParams.aperture);
                     }
                     if (shootingParams.exposureTime) {
                         dict["exposureTime"] = py::float_(*shootingParams.exposureTime);
                     }
                     if (shootingParams.sensitivity) {
                         dict["sensitivity"] = py::float_(*shootingParams.sensitivity);
                     }
                     if (shootingParams.totalGain) {
                         dict["totalGain"] = py::float_(*shootingParams.totalGain);
                     }
                     if (shootingParams.sensorGain) {
                         dict["sensorGain"] = py::float_(*shootingParams.sensorGain);
                     }
                     if (shootingParams.ispGain) {
                         dict["ispGain"] = py::float_(*shootingParams.ispGain);
                     }
                     if (shootingParams.zoom) {
                         dict["zoom"] = py::cast(shootingParams.zoom).attr("serialize")();
                     }
                     return dict;
                 })
            .def("__repr__", [](const ImageMetadata::ShootingParams &shootingParams) {
                auto dict = py::cast(shootingParams).attr("serialize")();
                return py::str(dict);
            });

    py::class_<ImageMetadata::CalibrationData>(
            imageMetadata,
            "CalibrationData",
            "Calibration data, see class detail with help(ImageMetadata.CalibrationData)",
            py::is_final())
            .def(py::init<>())
            .def_readwrite("blackLevel", &ImageMetadata::CalibrationData::blackLevel, "int or float: Black level")
            .def_readwrite("whiteLevel", &ImageMetadata::CalibrationData::whiteLevel, "int or float: White level")
            .def_readwrite("vignetting",
                           &ImageMetadata::CalibrationData::vignetting,
                           "DynamicMatrix: Luminance lens shading correction map")
            .def_readwrite("colorMatrix", &ImageMetadata::CalibrationData::colorMatrix, "Matrix3: Color matrix")
            .def_readwrite("colorMatrixTarget",
                           &ImageMetadata::CalibrationData::colorMatrixTarget,
                           "enum RgbColorSpace: Target color space of color matrix")
            .def("serialize",
                 [](const ImageMetadata::CalibrationData &calibData) {
                     py::dict dict;
                     if (calibData.blackLevel) {
                         dict["blackLevel"] = *calibData.blackLevel;
                     }
                     if (calibData.whiteLevel) {
                         dict["whiteLevel"] = *calibData.whiteLevel;
                     }
                     if (calibData.vignetting) {
                         dict["vignetting"] = py::cast(calibData.vignetting).attr("serialize")();
                     }
                     if (calibData.colorMatrix) {
                         dict["colorMatrix"] = py::cast(calibData.colorMatrix).attr("serialize")();
                     }
                     if (calibData.colorMatrixTarget) {
                         dict["colorMatrixTarget"] = py::str(cxximg::toString(*calibData.colorMatrixTarget));
                     }
                     return dict;
                 })
            .def("__repr__", [](const ImageMetadata::CalibrationData &calibData) {
                auto dict = py::cast(calibData).attr("serialize")();
                return py::str(dict);
            });

    py::class_<ImageMetadata::CameraControls> cameraControls(
            imageMetadata,
            "CameraControls",
            "Camera Controls, see class detail with help(ImageMetadata.CameraControls)",
            py::is_final());
    cameraControls.def(py::init<>())
            .def_readwrite("whiteBalance",
                           &ImageMetadata::CameraControls::whiteBalance,
                           "class ImageMetadata.WhiteBalance: White balance scales")
            .def_readwrite("colorShading",
                           &ImageMetadata::CameraControls::colorShading,
                           "class ImageMetadata.ColorShading: Color lens shading correction maps")
            .def_readwrite("faceDetection",
                           &ImageMetadata::CameraControls::faceDetection,
                           "UnorderdMapSemanticMasks: Array of face ROI")
            .def("serialize",
                 [](const ImageMetadata::CameraControls &cameraControls) {
                     py::dict dict;
                     if (cameraControls.whiteBalance) {
                         dict["whiteBalance"] = py::cast(cameraControls.whiteBalance).attr("serialize")();
                     }
                     if (cameraControls.colorShading) {
                         dict["colorShading"] = py::cast(cameraControls.colorShading).attr("serialize")();
                     }
                     if (cameraControls.faceDetection) {
                         py::list faces;
                         for (const auto &elem : *cameraControls.faceDetection) {
                             py::list roi = py::cast(elem).attr("serialize")();
                             faces.append(roi);
                         }
                         dict["faceDetection"] = faces;
                     }
                     return dict;
                 })
            .def("__repr__", [](const ImageMetadata::CameraControls &cameraControls) {
                auto dict = py::cast(cameraControls).attr("serialize")();
                return py::str(dict);
            });

    py::class_<ImageMetadata::WhiteBalance> whiteBalance(
            imageMetadata,
            "WhiteBalance",
            "White balance scales, see class detail with help(ImageMetadata.WhiteBalance)",
            py::is_final());
    whiteBalance.def(py::init<>())
            .def_readwrite("gainR", &ImageMetadata::WhiteBalance::gainR, "float: White balance R/G scale")
            .def_readwrite("gainB", &ImageMetadata::WhiteBalance::gainB, "float: White balance B/G scale")
            .def("serialize",
                 [](const ImageMetadata::WhiteBalance &whiteBalance) {
                     py::list list;
                     list.append(whiteBalance.gainR);
                     list.append(whiteBalance.gainB);
                     return list;
                 })
            .def("__repr__", [](const ImageMetadata::WhiteBalance &whiteBalance) {
                auto dict = py::cast(whiteBalance).attr("serialize")();
                return py::str(dict);
            });

    py::class_<ImageMetadata::ColorShading> colorShading(
            imageMetadata,
            "ColorShading",
            "Color lens shading correction maps, see class detail with help(ImageMetadata.ColorShading)",
            py::is_final());
    colorShading.def(py::init<>())
            .def_readwrite("gainR",
                           &ImageMetadata::ColorShading::gainR,
                           "class DynamicMatrix: Color lens shading R/G correction map")
            .def_readwrite("gainB",
                           &ImageMetadata::ColorShading::gainB,
                           "class DynamicMatrix: Color lens shading B/G correction map")
            .def("serialize",
                 [](const ImageMetadata::ColorShading &colorShading) {
                     if (colorShading.gainR.numCols() != colorShading.gainB.numCols() ||
                         colorShading.gainR.numRows() != colorShading.gainB.numRows()) {
                         throw std::runtime_error("color Shading must have the same cols and rows size");
                     }
                     py::list listR;
                     py::list listB;
                     for (int y = 0; y < colorShading.gainR.numRows(); ++y) { // NOLINT(readability-identifier-length)
                         py::list lineR;
                         py::list lineB;
                         for (int x = 0; x < colorShading.gainR.numCols(); // NOLINT(readability-identifier-length)
                              ++x) {
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
            .def("__repr__", [](const ImageMetadata::ColorShading &colorShading) {
                auto dict = py::cast(colorShading).attr("serialize")();
                return py::str(dict);
            });
}

} // namespace cxximg
