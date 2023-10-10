#include "model/ImageMetadata.h"

#include <pybind11/numpy.h>
#include "pybind11/pybind11.h"
#include "pybind11/stl.h"

namespace py = pybind11;


namespace cxximg {

DynamicMatrix createDynamicMatrixFromPyarray(py::array_t<float> b){
    /* Request a buffer descriptor from Python */
    py::buffer_info info = b.request();
    /* Some basic validation checks ... */
    if (info.format != py::format_descriptor<float>::format()){
        throw std::runtime_error("Incompatible format: expected a correct format array!");
    }
    if (info.ndim != 2) {
        throw std::runtime_error("Incompatible buffer dimension!");
    }
    /*Create the Dynamic Matrix based on the py::array's buffer */
    return DynamicMatrix(info.shape[1], info.shape[0], static_cast<float*>(info.ptr));
}

py::buffer_info defineBufferInfos(DynamicMatrix m){
    static constexpr int MATRIX_DIM = 2;
    return py::buffer_info(
                m.data(),                               /* Pointer to buffer */
                sizeof(float),                          /* Size of one scalar */
                py::format_descriptor<float>::format(), /* Python struct-style format descriptor */
                MATRIX_DIM,                                      /* Number of dimensions */
                { m.numRows(), m.numCols() },             /* Buffer dimensions */
                { sizeof(float) * m.numCols(),             /* Strides (in bytes) for each index */
                sizeof(float) }
    );
}


void init_math(py::module &m) {

    py::class_<DynamicMatrix>(m, "DynamicMatrix", py::buffer_protocol())
            .def(py::init([](py::array_t<float> b) {
                return createDynamicMatrixFromPyarray(b);
            }))
            .def_buffer([](DynamicMatrix &m) -> py::buffer_info {
                return defineBufferInfos(m);
            });

}

}