#include "pybind11/pybind11.h"
#include "pybind11/stl.h"

#include "loguru.hpp"

namespace py = pybind11;

PYBIND11_MODULE(cxx_libraw, m) {
    m.doc() = "libraw binding module";

    // Logoru issue: need to set Verbosity_OFF explicitly at binding call,
    // because loguru default value is Verbosity_OFF, it suppprts only configure
    // it by command line. since binding call is thourgh program directly, not
    // through command line, so this setting is necessary.
    loguru::g_stderr_verbosity = loguru::Verbosity_WARNING;

    // initialize all the binding submodules.

}
