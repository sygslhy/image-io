#include "math/Matrix.h"
#include "math/ColorSpace.h"
#include "math/DynamicMatrix.h"

#include "pybind11/buffer_info.h"
#include "pybind11/cast.h" // NOLINT(misc-include-cleaner)
#include "pybind11/numpy.h"
#include "pybind11/pybind11.h"
#include "pybind11/pytypes.h"
#include "pybind11/stl.h" // NOLINT(misc-include-cleaner)

#include <stdexcept>

namespace py = pybind11;

namespace cxximg {
namespace {
DynamicMatrix createDynamicMatrixFromPyarray(const py::array_t<float> &arr) {
    /* Request a buffer descriptor from Python */
    py::buffer_info info = arr.request();
    /* Some basic validation checks ... */
    if (info.format != py::format_descriptor<float>::format()) {
        throw std::runtime_error("Incompatible format: expected a correct format array!");
    }
    if (info.ndim != 2) {
        throw std::runtime_error("Incompatible buffer dimension!");
    }
    /*Create the Dynamic Matrix based on the py::array's buffer */
    return DynamicMatrix{
            static_cast<int>(info.shape[1]), static_cast<int>(info.shape[0]), static_cast<float *>(info.ptr)};
}

Matrix3 createMatrix3FromPyarray(const py::array_t<float> &arr) {
    /* Request a buffer descriptor from Python */
    py::buffer_info info = arr.request();
    /* Some basic validation checks ... */
    if (info.format != py::format_descriptor<float>::format()) {
        throw std::runtime_error("Incompatible format: expected a correct format array!");
    }
    if (info.ndim != 2) {
        throw std::runtime_error("Incompatible buffer dimension!");
    }
    if (info.shape[1] != 3 || info.shape[0] != 3) {
        throw std::runtime_error("Incompatible buffer shape!");
    }

    /*Create the Matrix 3x3 based on the py::array's buffer */

    return Matrix3(static_cast<float *>(info.ptr));
}

py::buffer_info defineBufferInfos(DynamicMatrix mod) {
    static constexpr int MATRIX_DIM = 2;
    return py::buffer_info(mod.data(),                             /* Pointer to buffer */
                           sizeof(float),                          /* Size of one scalar */
                           py::format_descriptor<float>::format(), /* Python struct-style format
                                                                      descriptor */
                           MATRIX_DIM,                             /* Number of dimensions */
                           {mod.numRows(), mod.numCols()},         /* Buffer dimensions */
                           {sizeof(float) * mod.numCols(),         /* Strides (in bytes) for each index */
                            sizeof(float)});
}

py::buffer_info defineBufferInfos(Matrix3 mod) {
    static constexpr int MATRIX_DIM = 2;
    return py::buffer_info(mod.data(),                             /* Pointer to buffer */
                           sizeof(float),                          /* Size of one scalar */
                           py::format_descriptor<float>::format(), /* Python struct-style format
                                                                      descriptor */
                           MATRIX_DIM,                             /* Number of dimensions */
                           {mod.numRows(), mod.numCols()},         /* Buffer dimensions */
                           {sizeof(float) * mod.numCols(),         /* Strides (in bytes) for each index */
                            sizeof(float)});
}
} // namespace
void initMath(py::module &mod) { // NOLINT(misc-use-internal-linkage)
    py::enum_<RgbColorSpace>(mod, "RgbColorSpace")
            .value("ADOBE_RGB", RgbColorSpace::ADOBE_RGB)
            .value("DISPLAY_P3", RgbColorSpace::DISPLAY_P3)
            .value("REC2020", RgbColorSpace::REC2020)
            .value("SRGB", RgbColorSpace::SRGB)
            .value("XYZ_D50", RgbColorSpace::XYZ_D50)
            .value("XYZ_D65", RgbColorSpace::XYZ_D65);

    py::enum_<RgbTransferFunction>(mod, "RgbTransferFunction")
            .value("GAMMA22", RgbTransferFunction::GAMMA22)
            .value("LINEAR", RgbTransferFunction::LINEAR)
            .value("SRGB", RgbTransferFunction::SRGB);

    py::class_<DynamicMatrix>(mod, "DynamicMatrix", py::buffer_protocol())
            .def(py::init([](const py::array_t<float> &arr) { return createDynamicMatrixFromPyarray(arr); }))
            .def_buffer([](DynamicMatrix &mod) -> py::buffer_info { return defineBufferInfos(mod); })
            .def("serialize",
                 [](const DynamicMatrix &mod) {
                     py::list list2D;
                     for (int y = 0; y < mod.numRows(); ++y) { // NOLINT(readability-identifier-length)
                         py::list line;
                         for (int x = 0; x < mod.numCols(); ++x) { // NOLINT(readability-identifier-length)
                             line.append(mod(y, x));
                         }
                         list2D.append(line);
                     }
                     return list2D;
                 })
            .def("__repr__", [](const DynamicMatrix &mod) {
                auto dict = py::cast(mod).attr("serialize")();
                return py::str(dict);
            });

    py::class_<Matrix3>(mod, "Matrix3", py::buffer_protocol())
            .def(py::init([](const py::array_t<float> &arr) { return createMatrix3FromPyarray(arr); }))
            .def_buffer([](Matrix3 &mod) -> py::buffer_info { return defineBufferInfos(mod); })
            .def("serialize",
                 [](const Matrix3 &mod) {
                     py::list list2D;
                     for (int y = 0; y < mod.numRows(); ++y) { // NOLINT(readability-identifier-length)
                         py::list line;
                         for (int x = 0; x < mod.numCols(); ++x) { // NOLINT(readability-identifier-length)
                             line.append(mod(y, x));
                         }
                         list2D.append(line);
                     }
                     return list2D;
                 })
            .def("__repr__", [](const Matrix3 &mod) {
                auto dict = py::cast(mod).attr("serialize")();
                return py::str(dict);
            });
}

} // namespace cxximg