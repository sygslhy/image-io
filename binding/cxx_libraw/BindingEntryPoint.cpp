#include "pybind11/detail/common.h"
#include "pybind11/pybind11.h"

namespace py = pybind11;

void initTypes(py::module &);    // NOLINT(misc-use-internal-linkage)
void initMetadata(py::module &); // NOLINT(misc-use-internal-linkage)

PYBIND11_MODULE(cxx_libraw, mod) {
    mod.doc() = "libraw binding module";

    // initialize all the binding submodules.
    initTypes(mod);
    initMetadata(mod);
}
