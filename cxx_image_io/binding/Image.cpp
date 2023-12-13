#include "image/Image.h"

#include "pybind11/numpy.h"
#include "pybind11/pybind11.h"
#include "pybind11/stl.h"

namespace py = pybind11;

namespace cxximg {

namespace image {

template <typename T> std::vector<py::ssize_t> calculBufferDim(Image<T> &m) {
    if (m.numPlanes() > 1) {
        return {m.height(), m.width(), m.numPlanes()};
    }
    return {m.height(), m.width()};
}

template <typename T>
std::vector<py::ssize_t> calculBufferStrides(Image<T> &m) {
    ImageDescriptor<T> imageDescrriptor = m.descriptor();
    int rowStride = imageDescrriptor.planes[0].rowStride;
    int pixelStride = imageDescrriptor.planes[0].pixelStride;

    if (m.numPlanes() > 1) {
        return {static_cast<py::ssize_t>(sizeof(T)) * rowStride,
                static_cast<py::ssize_t>(sizeof(T)) * pixelStride,
                static_cast<py::ssize_t>(sizeof(T))};
    }

    return {static_cast<py::ssize_t>(rowStride * sizeof(T)),
            static_cast<py::ssize_t>(pixelStride * sizeof(T))};
}

template <typename T> py::buffer_info defineBufferInfos(Image<T> &m) {

    if (m.descriptor().layout.imageLayout == ImageLayout::YUV_420 ||
        m.descriptor().layout.imageLayout == ImageLayout::NV12) {
        throw std::runtime_error("Cannot support convert the different sizes "
                                 "planes image to numpy array.");
    }
    return py::buffer_info(
        m.data(),                           /* Pointer to buffer */
        sizeof(T),                          /* Size of one scalar */
        py::format_descriptor<T>::format(), /* Python struct-style format
                                               descriptor */
        m.numPlanes() > 1 ? 3 : 2,          /* Number of dimensions */
        calculBufferDim(m),                 /* Buffer dimensions */
        calculBufferStrides(m) /* Strides (in bytes) for each index */
    );
}

template <typename T>
Image<T> createImageFromPyarray(py::array_t<T> b, PixelType pixelType,
                                ImageLayout imageLayout,
                                int pixelPrecision = 0) {
    /* Request a buffer descriptor from Python */
    py::buffer_info info = b.request();
    /* Some basic validation checks ... */
    if (info.format != py::format_descriptor<T>::format()) {
        throw std::runtime_error(
            "Incompatible format: expected a correct format array!");
    }
    if (info.ndim > 3 || info.ndim < 2) {
        throw std::runtime_error("Incompatible buffer dimension!");
    }
    /*Create the Image based on the py::array's buffer */
    ImageDescriptor<T> descriptor(
        LayoutDescriptor::Builder(info.shape[1], info.shape[0])
            .pixelPrecision(pixelPrecision)
            .imageLayout(imageLayout)
            .pixelType(pixelType)
            .build());
    return Image<T>(descriptor, static_cast<T *>(info.ptr));
}

void init_image(py::module &m) {

    py::enum_<PixelType>(m, "PixelType")
        .value("CUSTOM", PixelType::CUSTOM)
        .value("GRAYSCALE", PixelType::GRAYSCALE)
        .value("RAW12", PixelType::GRAY_ALPHA)
        .value("RGB", PixelType::RGB)
        .value("RGBA", PixelType::RGBA)
        .value("YUV", PixelType::YUV)
        .value("BAYER_RGGB", PixelType::BAYER_RGGB)
        .value("BAYER_BGGR", PixelType::BAYER_BGGR)
        .value("BAYER_GRBG", PixelType::BAYER_GRBG)
        .value("BAYER_GBRG", PixelType::BAYER_GBRG)
        .value("QUADBAYER_RGGB", PixelType::QUADBAYER_RGGB)
        .value("QUADBAYER_BGGR", PixelType::QUADBAYER_BGGR)
        .value("QUADBAYER_GRBG", PixelType::QUADBAYER_GRBG)
        .value("QUADBAYER_GBRG", PixelType::QUADBAYER_GBRG);

    py::enum_<ImageLayout>(m, "ImageLayout")
        .value("CUSTOM", ImageLayout::CUSTOM)
        .value("PLANAR", ImageLayout::PLANAR)
        .value("INTERLEAVED", ImageLayout::INTERLEAVED)
        .value("YUV_420", ImageLayout::YUV_420)
        .value("NV12", ImageLayout::NV12);

    py::class_<ImageView<int>>(m, "ImageViewInt")
        .def("pixelType", &ImageView<int>::pixelType)
        .def("pixelPrecision", &ImageView<int>::pixelPrecision)
        .def("imageLayout", &ImageView<int>::imageLayout);

    py::class_<Image<int>, ImageView<int>>(m, "ImageInt", py::buffer_protocol())
        .def(py::init([](py::array_t<int> b, PixelType pixelType,
                         ImageLayout imageLayout, int pixelPrecision) {
            return createImageFromPyarray<int>(b, pixelType, imageLayout,
                                               pixelPrecision);
        }))
        .def_buffer([](Image<int> &m) -> py::buffer_info {
            return defineBufferInfos(m);
        });

    py::class_<ImageView<float>>(m, "ImageViewFloat")
        .def("pixelType", &ImageView<float>::pixelType)
        .def("pixelPrecision", &ImageView<float>::pixelPrecision)
        .def("imageLayout", &ImageView<float>::imageLayout);

    py::class_<Image<float>, ImageView<float>>(m, "ImageFloat",
                                               py::buffer_protocol())
        .def(py::init([](py::array_t<float> b, PixelType pixelType,
                         ImageLayout imageLayout, int pixelPrecision) {
            return createImageFromPyarray<float>(b, pixelType, imageLayout,
                                                 pixelPrecision);
        }))
        .def_buffer([](Image<float> &m) -> py::buffer_info {
            return defineBufferInfos(m);
        });

    py::class_<ImageView<uint8_t>>(m, "ImageViewUint8")
        .def("pixelType", &ImageView<uint8_t>::pixelType)
        .def("pixelPrecision", &ImageView<uint8_t>::pixelPrecision)
        .def("imageLayout", &ImageView<uint8_t>::imageLayout);

    py::class_<Image<uint8_t>, ImageView<uint8_t>>(m, "ImageUint8",
                                                   py::buffer_protocol())
        .def(py::init([](py::array_t<uint8_t> b, PixelType pixelType,
                         ImageLayout imageLayout, int pixelPrecision) {
            return createImageFromPyarray<uint8_t>(b, pixelType, imageLayout,
                                                   pixelPrecision);
        }))
        .def_buffer([](Image<uint8_t> &m) -> py::buffer_info {
            return defineBufferInfos(m);
        });

    py::class_<ImageView<uint16_t>>(m, "ImageViewUint16")
        .def("pixelType", &ImageView<uint16_t>::pixelType)
        .def("pixelPrecision", &ImageView<uint16_t>::pixelPrecision)
        .def("imageLayout", &ImageView<uint16_t>::imageLayout);

    py::class_<Image<uint16_t>, ImageView<uint16_t>>(m, "ImageUint16",
                                                     py::buffer_protocol())
        .def(py::init([](py::array_t<uint16_t> b, PixelType pixelType,
                         ImageLayout imageLayout, int pixelPrecision) {
            return createImageFromPyarray<uint16_t>(b, pixelType, imageLayout,
                                                    pixelPrecision);
        }))
        .def_buffer([](Image<uint16_t> &m) -> py::buffer_info {
            return defineBufferInfos(m);
        });

    py::class_<ImageView<double>>(m, "ImageViewDouble")
        .def("pixelType", &ImageView<double>::pixelType)
        .def("pixelPrecision", &ImageView<double>::pixelPrecision)
        .def("imageLayout", &ImageView<double>::imageLayout);

    py::class_<Image<double>, ImageView<double>>(m, "ImageDouble",
                                                 py::buffer_protocol())
        .def(py::init([](py::array_t<double> b, PixelType pixelType,
                         ImageLayout imageLayout, int pixelPrecision) {
            return createImageFromPyarray<double>(b, pixelType, imageLayout,
                                                  pixelPrecision);
        }))
        .def_buffer([](Image<double> &m) -> py::buffer_info {
            return defineBufferInfos(m);
        });
}

} // namespace image

} // namespace cxximg