#include "image/Image.h" // NOLINT(misc-header-include-cycle)
#include "image/ImageLayout.h"
#include "image/PixelType.h"

#include "pybind11/buffer_info.h"
#include "pybind11/numpy.h"
#include "pybind11/pybind11.h"
#include "pybind11/stl.h" // NOLINT(misc-include-cleaner)

#include <cstdint>
#include <stdexcept>
#include <vector>

namespace py = pybind11;

namespace cxximg {

namespace image {

namespace {

template <typename T>
std::vector<py::ssize_t> calculBufferDim(Image<T> &mod) {
    if (mod.numPlanes() > 1) {
        return {mod.height(), mod.width(), mod.numPlanes()};
    }
    return {mod.height(), mod.width()};
}

template <typename T>
std::vector<py::ssize_t> calculBufferStrides(Image<T> &mod) {
    ImageDescriptor<T> imageDescrriptor = mod.descriptor();
    const int rowStride = imageDescrriptor.layout.planes[0].rowStride;
    const int pixelStride = imageDescrriptor.layout.planes[0].pixelStride;

    if (mod.numPlanes() > 1) {
        return {static_cast<py::ssize_t>(sizeof(T)) * rowStride,
                static_cast<py::ssize_t>(sizeof(T)) * pixelStride,
                static_cast<py::ssize_t>(sizeof(T))};
    }

    return {static_cast<py::ssize_t>(rowStride * sizeof(T)), static_cast<py::ssize_t>(pixelStride * sizeof(T))};
}

template <typename T>
py::buffer_info defineBufferInfos(Image<T> &mod) {
    if (mod.descriptor().layout.imageLayout == ImageLayout::YUV_420 ||
        mod.descriptor().layout.imageLayout == ImageLayout::NV12) {
        ImageDescriptor<T> imageDescrriptor = mod.descriptor();
        const int rowStride = imageDescrriptor.layout.planes[0].rowStride;
        const int pixelStride = imageDescrriptor.layout.planes[0].pixelStride;
        return py::buffer_info(
                mod.data(),                          /* Pointer to buffer */
                sizeof(T),                           /* Size of one scalar */
                py::format_descriptor<T>::format(),  /* Python struct-style format
                                                        descriptor */
                2,                                   /* Number of dimensions */
                {3 * mod.height() / 2, mod.width()}, /* Buffer dimensions */
                {static_cast<py::ssize_t>(rowStride * sizeof(T)), static_cast<py::ssize_t>(pixelStride * sizeof(T))}
                /* Strides (in bytes) for each index */
        );
    }
    return py::buffer_info(mod.data(),                         /* Pointer to buffer */
                           sizeof(T),                          /* Size of one scalar */
                           py::format_descriptor<T>::format(), /* Python struct-style format
                                                                  descriptor */
                           mod.numPlanes() > 1 ? 3 : 2,        /* Number of dimensions */
                           calculBufferDim(mod),               /* Buffer dimensions */
                           calculBufferStrides(mod)            /* Strides (in bytes) for each index */
    );
}

template <typename T>
Image<T> createImageFromPyarray(const py::array_t<T> &arr,
                                PixelType pixelType,
                                ImageLayout imageLayout,
                                int pixelPrecision = 0) {
    /* Request a buffer descriptor from Python */
    py::buffer_info info = arr.request();
    /* Some basic validation checks ... */
    if (info.format != py::format_descriptor<T>::format()) {
        throw std::runtime_error("Incompatible format: expected a correct format array!");
    }
    if (info.ndim > 3 || info.ndim < 2) {
        throw std::runtime_error("Incompatible buffer dimension!");
    }

    if (imageLayout == ImageLayout::YUV_420 || imageLayout == ImageLayout::NV12) {
        const LayoutDescriptor layout = LayoutDescriptor::Builder(info.shape[1], info.shape[0] * 2 / 3)
                                                .pixelPrecision(pixelPrecision)
                                                .imageLayout(imageLayout)
                                                .pixelType(pixelType)
                                                .build();
        return Image<T>(layout, static_cast<T *>(info.ptr));
    }
    /*Create the Image based on the py::array's buffer */
    const LayoutDescriptor layout = LayoutDescriptor::Builder(info.shape[1], info.shape[0])
                                            .pixelPrecision(pixelPrecision)
                                            .imageLayout(imageLayout)
                                            .pixelType(pixelType)
                                            .build();
    return Image<T>(layout, static_cast<T *>(info.ptr));
}
} // namespace
void initImage(py::module &mod) { // NOLINT(misc-use-internal-linkage)
    py::enum_<PixelType>(mod, "PixelType")
            .value("CUSTOM", PixelType::CUSTOM)
            .value("GRAYSCALE", PixelType::GRAYSCALE)
            .value("GRAY_ALPHA", PixelType::GRAY_ALPHA)
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

    py::enum_<ImageLayout>(mod, "ImageLayout")
            .value("CUSTOM", ImageLayout::CUSTOM)
            .value("PLANAR", ImageLayout::PLANAR)
            .value("INTERLEAVED", ImageLayout::INTERLEAVED)
            .value("YUV_420", ImageLayout::YUV_420)
            .value("NV12", ImageLayout::NV12);

    py::class_<ImageView<int>>(mod, "ImageViewInt")
            .def("pixelType", &ImageView<int>::pixelType)
            .def("pixelPrecision", &ImageView<int>::pixelPrecision)
            .def("imageLayout", &ImageView<int>::imageLayout)
            .def("width", &ImageView<int>::width)
            .def("height", &ImageView<int>::height);

    py::class_<Image<int>, ImageView<int>>(mod, "ImageInt", py::buffer_protocol())
            .def(py::init(
                    [](const py::array_t<int> &arr, PixelType pixelType, ImageLayout imageLayout, int pixelPrecision) {
                        return createImageFromPyarray<int>(arr, pixelType, imageLayout, pixelPrecision);
                    }))
            .def_buffer([](Image<int> &mod) -> py::buffer_info { return defineBufferInfos(mod); });

    py::class_<ImageView<float>>(mod, "ImageViewFloat")
            .def("pixelType", &ImageView<float>::pixelType)
            .def("pixelPrecision", &ImageView<float>::pixelPrecision)
            .def("imageLayout", &ImageView<float>::imageLayout)
            .def("width", &ImageView<float>::width)
            .def("height", &ImageView<float>::height);

    py::class_<Image<float>, ImageView<float>>(mod, "ImageFloat", py::buffer_protocol())
            .def(py::init([](const py::array_t<float> &arr,
                             PixelType pixelType,
                             ImageLayout imageLayout,
                             int pixelPrecision) {
                return createImageFromPyarray<float>(arr, pixelType, imageLayout, pixelPrecision);
            }))
            .def_buffer([](Image<float> &mod) -> py::buffer_info { return defineBufferInfos(mod); });

    py::class_<ImageView<uint8_t>>(mod, "ImageViewUint8")
            .def("pixelType", &ImageView<uint8_t>::pixelType)
            .def("pixelPrecision", &ImageView<uint8_t>::pixelPrecision)
            .def("imageLayout", &ImageView<uint8_t>::imageLayout)
            .def("width", &ImageView<uint8_t>::width)
            .def("height", &ImageView<uint8_t>::height);

    py::class_<Image<uint8_t>, ImageView<uint8_t>>(mod, "ImageUint8", py::buffer_protocol())
            .def(py::init([](const py::array_t<uint8_t> &arr,
                             PixelType pixelType,
                             ImageLayout imageLayout,
                             int pixelPrecision) {
                return createImageFromPyarray<uint8_t>(arr, pixelType, imageLayout, pixelPrecision);
            }))
            .def_buffer([](Image<uint8_t> &mod) -> py::buffer_info { return defineBufferInfos(mod); });

    py::class_<ImageView<uint16_t>>(mod, "ImageViewUint16")
            .def("pixelType", &ImageView<uint16_t>::pixelType)
            .def("pixelPrecision", &ImageView<uint16_t>::pixelPrecision)
            .def("imageLayout", &ImageView<uint16_t>::imageLayout)
            .def("width", &ImageView<uint16_t>::width)
            .def("height", &ImageView<uint16_t>::height);

    py::class_<Image<uint16_t>, ImageView<uint16_t>>(mod, "ImageUint16", py::buffer_protocol())
            .def(py::init([](const py::array_t<uint16_t> &arr,
                             PixelType pixelType,
                             ImageLayout imageLayout,
                             int pixelPrecision) {
                return createImageFromPyarray<uint16_t>(arr, pixelType, imageLayout, pixelPrecision);
            }))
            .def_buffer([](Image<uint16_t> &mod) -> py::buffer_info { return defineBufferInfos(mod); });

    py::class_<ImageView<double>>(mod, "ImageViewDouble")
            .def("pixelType", &ImageView<double>::pixelType)
            .def("pixelPrecision", &ImageView<double>::pixelPrecision)
            .def("imageLayout", &ImageView<double>::imageLayout)
            .def("width", &ImageView<double>::width)
            .def("height", &ImageView<double>::height);

    py::class_<Image<double>, ImageView<double>>(mod, "ImageDouble", py::buffer_protocol())
            .def(py::init([](const py::array_t<double> &arr,
                             PixelType pixelType,
                             ImageLayout imageLayout,
                             int pixelPrecision) {
                return createImageFromPyarray<double>(arr, pixelType, imageLayout, pixelPrecision);
            }))
            .def_buffer([](Image<double> &mod) -> py::buffer_info { return defineBufferInfos(mod); });
}

} // namespace image

} // namespace cxximg