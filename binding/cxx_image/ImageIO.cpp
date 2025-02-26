#include "io/ImageIO.h"
#include "image/Image.h"
#include "io/ImageReader.h"
#include "io/ImageWriter.h"
#include "model/ImageMetadata.h"

#include "pybind11/cast.h"
#include "pybind11/numpy.h"
#include "pybind11/pybind11.h"
#include "pybind11/pytypes.h"
#include "pybind11/stl.h" // NOLINT(misc-include-cleaner)

#include "BmpIO.h"
#include "CfaIO.h"
#include "DngIO.h"
#include "JpegIO.h"
#include "MipiRawIO.h"
#include "PlainIO.h"
#include "PngIO.h"
#include "TiffIO.h"

#include <memory>
#include <optional>
#include <string>

namespace py = pybind11;

namespace cxximg {

namespace io {

void initIO(py::module &mod) {                                 // NOLINT(misc-use-internal-linkage)
    py::module_ mIO = mod.def_submodule("io", "io namespace"); // NOLINT(misc-const-correctness)

    py::class_<ImageReader> imageReader(mIO, "ImageReader");
    imageReader.def("pixelRepresentation", &ImageReader::pixelRepresentation)
            .def("readMetadata",
                 [](ImageReader &self, py::object &metadata) {
                     std::optional<ImageMetadata> cls = metadata.cast<ImageMetadata>();
                     self.readMetadata(cls);
                     return py::cast(cls);
                 })
            .def("readExif", &ImageReader::readExif);

    py::class_<PlainReader, ImageReader> plainReader(mIO, "PlainReader");
    plainReader.def("read8u", &PlainReader::read8u)
            .def("read16u", &PlainReader::read16u)
            .def("readf", &PlainReader::readf);

    py::class_<BmpReader, ImageReader> bmpReader(mIO, "BmpReader");
    bmpReader.def("read8u", &BmpReader::read8u);

    py::class_<JpegReader, ImageReader> jpegReader(mIO, "JpegReader");
    jpegReader.def("read8u", &JpegReader::read8u).def("readExif", &JpegReader::readExif);

    py::class_<PngReader, ImageReader> pngReader(mIO, "PngReader");
    pngReader.def("read8u", &PngReader::read8u).def("read16u", &PngReader::read16u);

    py::class_<TiffReader, ImageReader> tiffReader(mIO, "TiffReader");
    tiffReader.def("read8u", &TiffReader::read8u)
            .def("read16u", &TiffReader::read16u)
            .def("readf", &TiffReader::readf)
            .def("readExif", &TiffReader::readExif);

    py::class_<CfaReader, ImageReader> cfaReader(mIO, "CfaReader");
    cfaReader.def("read16u", &CfaReader::read16u);

    py::class_<MipiRaw10Reader, ImageReader> mipiRaw10Reader(mIO, "MipiRaw10Reader");
    mipiRaw10Reader.def("read16u", &MipiRaw10Reader::read16u);

    py::class_<MipiRaw12Reader, ImageReader> mipiRaw12Reader(mIO, "MipiRaw12Reader");
    mipiRaw12Reader.def("read16u", &MipiRaw12Reader::read16u);

    py::class_<DngReader, ImageReader> dngReader(mIO, "DngReader");
    dngReader.def("read16u", &DngReader::read16u).def("readf", &DngReader::readf).def("readExif", &DngReader::readExif);

    mIO.def("makeReader", [](const std::string &inputPath, const py::object &metadata) {
        if (!metadata.is(py::none())) {
            auto *cls = metadata.cast<ImageMetadata *>();
            std::unique_ptr<ImageReader> imageReader = io::makeReader(inputPath, ImageReader::Options(*cls));
            return imageReader;
        }
        std::unique_ptr<ImageReader> imageReader = io::makeReader(inputPath);
        return imageReader;
    });

    py::class_<ImageWriter> imageWriter(mIO, "ImageWriter");
    imageWriter.def("writeExif", &ImageWriter::writeExif);

    py::enum_<ImageWriter::TiffCompression>(imageWriter, "TiffCompression")
            .value("NONE", ImageWriter::TiffCompression::NONE)
            .value("DEFLATE", ImageWriter::TiffCompression::DEFLATE);

    py::class_<ImageWriter::Options> options(imageWriter, "Options");
    options.def(py::init<>())
            .def(py::init([](const py::object &metadata) {
                auto *cls = metadata.cast<ImageMetadata *>();
                return std::make_unique<ImageWriter::Options>(*cls);
            }))
            .def_readwrite("jpegQuality", &ImageWriter::Options::jpegQuality)
            .def_readwrite("tiffCompression", &ImageWriter::Options::tiffCompression)
            .def_readwrite("fileFormat", &ImageWriter::Options::fileFormat)
            .def_readwrite("metadata", &ImageWriter::Options::metadata);

    py::class_<PlainWriter, ImageWriter> plainWriter(mIO, "PlainWriter");
    plainWriter.def("write", [](PlainWriter &self, const Image8u &image) { self.write(image); })
            .def("write", [](PlainWriter &self, const Image16u &image) { self.write(image); })
            .def("write", [](PlainWriter &self, const Imagef &image) { self.write(image); });

    py::class_<BmpWriter, ImageWriter> bmpWriter(mIO, "BmpWriter");
    bmpWriter.def("write", [](BmpWriter &self, const Image8u &image) { self.write(image); });

    py::class_<JpegWriter, ImageWriter> jpegWriter(mIO, "JpegWriter");
    jpegWriter.def("write", [](JpegWriter &self, const Image8u &image) { self.write(image); })
            .def("writeExif", &JpegWriter::writeExif);

    py::class_<PngWriter, ImageWriter> pngWriter(mIO, "PngWriter");
    pngWriter.def("write", [](PngWriter &self, const Image8u &image) { self.write(image); })
            .def("write", [](PngWriter &self, const Image16u &image) { self.write(image); });

    py::class_<TiffWriter, ImageWriter> tiffWriter(mIO, "TiffWriter");
    tiffWriter.def("write", [](TiffWriter &self, const Image8u &image) { self.write(image); })
            .def("write", [](TiffWriter &self, const Image16u &image) { self.write(image); })
            .def("write", [](TiffWriter &self, const Imagef &image) { self.write(image); })
            .def("writeExif", &TiffWriter::writeExif);

    py::class_<CfaWriter, ImageWriter> cfaWriter(mIO, "CfaWriter");
    cfaWriter.def("write", [](CfaWriter &self, const Image16u &image) { self.write(image); });

    py::class_<MipiRaw10Writer, ImageWriter> mipiRaw10Writer(mIO, "MipiRaw10Writer");
    mipiRaw10Writer.def("write", [](MipiRaw10Writer &self, const Image16u &image) { self.write(image); });

    py::class_<MipiRaw12Writer, ImageWriter> mipiRaw12Writer(mIO, "MipiRaw12Writer");
    mipiRaw12Writer.def("write", [](MipiRaw12Writer &self, const Image16u &image) { self.write(image); });

    py::class_<DngWriter, ImageWriter> dngWriter(mIO, "DngWriter");
    dngWriter.def("write", [](DngWriter &self, const Image16u &image) { self.write(image); })
            .def("write", [](DngWriter &self, const Imagef &image) { self.write(image); });

    mIO.def("makeWriter", [](const std::string &outputPath, const py::object &write_options) {
        if (!write_options.is(py::none())) {
            auto *cls = write_options.cast<ImageWriter::Options *>();
            std::unique_ptr<ImageWriter> imageWriter = io::makeWriter(outputPath, ImageWriter::Options(*cls));
            return imageWriter;
        }
        std::unique_ptr<ImageWriter> imageWriter = io::makeWriter(outputPath);
        return imageWriter;
    });
}

} // namespace io

} // namespace cxximg
