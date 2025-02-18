#include "pybind11/detail/common.h"
#include "pybind11/pybind11.h"
#include "pybind11/stl.h" // NOLINT(misc-include-cleaner)

#include "loguru.hpp"

namespace py = pybind11;

namespace cxximg {

void initExif(py::module &);  // NOLINT(misc-use-internal-linkage)
void initMath(py::module &);  // NOLINT(misc-use-internal-linkage)
void initModel(py::module &); // NOLINT(misc-use-internal-linkage)

namespace parser {
void initParser(py::module &); // NOLINT(misc-use-internal-linkage)
}

namespace io {
void initIO(py::module &); // NOLINT(misc-use-internal-linkage)
}

namespace image {
void initImage(py::module &); // NOLINT(misc-use-internal-linkage)
}

PYBIND11_MODULE(cxx_image, mod) {
    mod.doc() = "image io binding module";

    // Logoru issue: need to set Verbosity_OFF explicitly at binding call,
    // because loguru default value is Verbosity_OFF, it suppprts only configure
    // it by command line. since binding call is thourgh program directly, not
    // through command line, so this setting is necessary.
    loguru::g_stderr_verbosity = loguru::Verbosity_WARNING;

    // initialize all the binding submodules.
    initExif(mod);
    initMath(mod);
    initModel(mod);
    image::initImage(mod);
    parser::initParser(mod);
    io::initIO(mod);
}

} // namespace cxximg
