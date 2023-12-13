#include "io/ImageIO.h"
#include "image/Image.h"
#include "model/ImageMetadata.h"

#include "pybind11/numpy.h"
#include "pybind11/pybind11.h"
#include "pybind11/stl.h"
#include <pybind11/operators.h>

#include "BmpIO.h"
#include "CfaIO.h"
#include "DngIO.h"
#include "JpegIO.h"
#include "MipiRawIO.h"
#include "PlainIO.h"
#include "PngIO.h"
#include "TiffIO.h"

namespace py = pybind11;

namespace cxximg {

namespace io {

void init_io(py::module &m) {

    py::module_ m_io = m.def_submodule("io", "io namespace");

    py::class_<ImageReader> imageReader(m_io, "ImageReader");
    imageReader.def("pixelRepresentation", &ImageReader::pixelRepresentation)
        .def("readMetadata",
             [](ImageReader &self, py::object &metadata) {
                 std::optional<ImageMetadata> cls =
                     metadata.cast<ImageMetadata>();
                 self.readMetadata(cls);
                 return py::cast(cls);
             })
        .def("readExif", &ImageReader::readExif);

    py::class_<PlainReader, ImageReader> plainReader(m_io, "PlainReader");
    plainReader.def("read8u", &PlainReader::read8u)
        .def("read16u", &PlainReader::read16u)
        .def("readf", &PlainReader::readf);

    py::class_<BmpReader, ImageReader> bmpReader(m_io, "BmpReader");
    bmpReader.def("read8u", &BmpReader::read8u);

    py::class_<JpegReader, ImageReader> jpegReader(m_io, "JpegReader");
    jpegReader.def("read8u", &JpegReader::read8u)
        .def("readExif", &JpegReader::readExif);

    py::class_<PngReader, ImageReader> pngReader(m_io, "PngReader");
    pngReader.def("read8u", &PngReader::read8u)
        .def("read16u", &PngReader::read16u);

    py::class_<TiffReader, ImageReader> tiffReader(m_io, "TiffReader");
    tiffReader.def("read8u", &TiffReader::read8u)
        .def("read16u", &TiffReader::read16u)
        .def("readf", &TiffReader::readf)
        .def("readExif", &TiffReader::readExif);

    py::class_<CfaReader, ImageReader> cfaReader(m_io, "CfaReader");
    cfaReader.def("read16u", &CfaReader::read16u);

    py::class_<MipiRaw10Reader, ImageReader> mipiRaw10Reader(m_io,
                                                             "MipiRaw10Reader");
    mipiRaw10Reader.def("read16u", &MipiRaw10Reader::read16u);

    py::class_<MipiRaw12Reader, ImageReader> mipiRaw12Reader(m_io,
                                                             "MipiRaw12Reader");
    mipiRaw12Reader.def("read16u", &MipiRaw12Reader::read16u);

    py::class_<DngReader, ImageReader> dngReader(m_io, "DngReader");
    dngReader.def("read16u", &DngReader::read16u)
        .def("read16u", &DngReader::read8u)
        .def("readExif", &DngReader::readExif);

    m_io.def("makeReader", [](const std::string &inputPath,
                              const py::object &metadata) {
        if (metadata != py::none()) {
            ImageMetadata *cls = metadata.cast<ImageMetadata *>();
            std::unique_ptr<ImageReader> imageReader =
                io::makeReader(inputPath, ImageReader::Options(*cls));
            return imageReader;
        }
        std::unique_ptr<ImageReader> imageReader = io::makeReader(inputPath);
        return imageReader;
    });

    py::class_<ImageWriter> imageWriter(m_io, "ImageWriter");
    imageWriter.def("writeExif", &ImageWriter::writeExif);

    py::enum_<ImageWriter::TiffCompression>(imageWriter, "TiffCompression")
        .value("NONE", ImageWriter::TiffCompression::NONE)
        .value("DEFLATE", ImageWriter::TiffCompression::DEFLATE);

    py::class_<ImageWriter::Options> options(imageWriter, "Options");
    options.def(py::init<>())
        .def(py::init([](py::object metadata) {
            ImageMetadata *cls = metadata.cast<ImageMetadata *>();
            return std::make_unique<ImageWriter::Options>(*cls);
        }))
        .def_readwrite("jpegQuality", &ImageWriter::Options::jpegQuality)
        .def_readwrite("tiffCompression",
                       &ImageWriter::Options::tiffCompression)
        .def_readwrite("fileFormat", &ImageWriter::Options::fileFormat)
        .def_readwrite("metadata", &ImageWriter::Options::metadata);

    py::class_<PlainWriter, ImageWriter> plainWriter(m_io, "PlainWriter");
    plainWriter
        .def("write",
             [](PlainWriter &self, const Image8u &image) { self.write(image); })
        .def("write", [](PlainWriter &self,
                         const Image16u &image) { self.write(image); })
        .def("write",
             [](PlainWriter &self, const Imagef &image) { self.write(image); });

    py::class_<BmpWriter, ImageWriter> bmpWriter(m_io, "BmpWriter");
    bmpWriter.def("write", [](BmpWriter &self, const Image8u &image) {
        self.write(image);
    });

    py::class_<JpegWriter, ImageWriter> jpegWriter(m_io, "JpegWriter");
    jpegWriter
        .def("write",
             [](JpegWriter &self, const Image8u &image) { self.write(image); })
        .def("writeExif", &JpegWriter::writeExif);

    py::class_<PngWriter, ImageWriter> pngWriter(m_io, "PngWriter");
    pngWriter
        .def("write",
             [](PngWriter &self, const Image8u &image) { self.write(image); })
        .def("write", [](PlainWriter &self, const Image16u &image) {
            self.write(image);
        });

    py::class_<TiffWriter, ImageWriter> tiffWriter(m_io, "TiffWriter");
    tiffWriter
        .def("write",
             [](TiffWriter &self, const Image8u &image) { self.write(image); })
        .def("write",
             [](TiffWriter &self, const Image16u &image) { self.write(image); })
        .def("write",
             [](TiffWriter &self, const Imagef &image) { self.write(image); })
        .def("writeExif", &TiffWriter::writeExif);

    py::class_<CfaWriter, ImageWriter> cfaWriter(m_io, "CfaWriter");
    cfaWriter.def("write", [](CfaWriter &self, const Image16u &image) {
        self.write(image);
    });

    py::class_<MipiRaw10Writer, ImageWriter> mipiRaw10Writer(m_io,
                                                             "MipiRaw10Writer");
    mipiRaw10Writer.def("write",
                        [](MipiRaw10Writer &self, const Image16u &image) {
                            self.write(image);
                        });

    py::class_<MipiRaw12Writer, ImageWriter> mipiRaw12Writer(m_io,
                                                             "MipiRaw12Writer");
    mipiRaw12Writer.def("write",
                        [](MipiRaw12Writer &self, const Image16u &image) {
                            self.write(image);
                        });

    py::class_<DngWriter, ImageWriter> dngWriter(m_io, "DngWriter");
    dngWriter
        .def("write",
             [](DngWriter &self, const Image16u &image) { self.write(image); })
        .def("write",
             [](DngWriter &self, const Imagef &image) { self.write(image); });

    m_io.def("makeWriter", [](const std::string &outputPath,
                              const py::object &write_options) {
        if (write_options != py::none()) {
            ImageWriter::Options *cls =
                write_options.cast<ImageWriter::Options *>();
            std::unique_ptr<ImageWriter> imageWriter =
                io::makeWriter(outputPath, ImageWriter::Options(*cls));
            return imageWriter;
        }
        std::unique_ptr<ImageWriter> imageWriter = io::makeWriter(outputPath);
        return imageWriter;
    });
}

} // namespace io

} // namespace cxximg
