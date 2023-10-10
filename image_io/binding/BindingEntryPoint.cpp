#include "pybind11/pybind11.h"
#include "pybind11/stl.h"

#include "loguru.hpp"

namespace py = pybind11;

namespace cxximg {

void init_math(py::module &);
void init_model(py::module &);

namespace parser {
    void init_parser(py::module &);
}

namespace io {
    void init_io(py::module &);
}

namespace image {
    void init_image(py::module &);
}



PYBIND11_MODULE(cxx_image_io, m) {
    m.doc() = "image io binding module";
   
    loguru::g_stderr_verbosity = loguru::Verbosity_OFF;

    init_math(m);
    init_model(m);
    image::init_image(m);
    parser::init_parser(m);
    io::init_io(m);

}

}
