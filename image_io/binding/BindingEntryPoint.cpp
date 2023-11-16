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

PYBIND11_MODULE(cxx_image, m) {
    m.doc() = "image io binding module";

    // Logoru issue: need to set Verbosity_OFF explicitly at binding call,
    // because loguru default value is Verbosity_OFF, it suppprts only configure
    // it by command line. since binding call is thourgh program directly, not
    // through command line, so this setting is necessary.
    loguru::g_stderr_verbosity = loguru::Verbosity_OFF;

    // initialize all the binding submodules.
    init_math(m);
    init_model(m);
    image::init_image(m);
    parser::init_parser(m);
    io::init_io(m);
}

} // namespace cxximg
