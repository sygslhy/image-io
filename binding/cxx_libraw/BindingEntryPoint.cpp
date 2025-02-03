#include "pybind11/pybind11.h"
#include "pybind11/stl.h"

namespace py = pybind11;

void init_types(py::module &);

PYBIND11_MODULE(cxx_libraw, m) {
    m.doc() = "libraw binding module";

    // initialize all the binding submodules.
    init_types(m);


}
