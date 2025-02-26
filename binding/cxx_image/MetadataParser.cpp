#include "parser/MetadataParser.h"

#include "pybind11/pybind11.h" // NOLINT
#include "pybind11/stl.h"      // NOLINT(misc-include-cleaner)

#include <optional>
#include <string>

namespace py = pybind11;

namespace cxximg {

namespace parser {

void initParser(py::module &mod) {                                        // NOLINT(misc-use-internal-linkage)
    py::module_ mParser = mod.def_submodule("parser", "parse namespace"); // NOLINT(misc-const-correctness)
    mParser.def("readMetadata",
                py::overload_cast<const std::string &, const std::optional<std::string> &>(&readMetadata));
}

} // namespace parser

} // namespace cxximg