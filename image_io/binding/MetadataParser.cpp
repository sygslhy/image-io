#include "parser/MetadataParser.h"

#include "pybind11/pybind11.h"
#include "pybind11/stl.h"

namespace py = pybind11;

namespace cxximg {

namespace parser {

void init_parser(py::module &m) {
    py::module_ m_parser = m.def_submodule("parser", "parse namespace");
    m_parser.def(
        "readMetadata",
        py::overload_cast<const std::string &,
                          const std::optional<std::string> &>(&readMetadata));
}

} // namespace parser

} // namespace cxximg