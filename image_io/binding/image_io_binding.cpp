#include "pybind11/pybind11.h"
#include "pybind11/stl.h"

#include "loguru.hpp"
#include <iostream>
namespace py = pybind11;

namespace impact {

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

int parsLogLevel(const std::string& level){
    if (level == "off"){
        return loguru::Verbosity_OFF;
    }
    if (level == "fatal"){
        return loguru::Verbosity_FATAL;
    }
    if (level == "error"){
        return loguru::Verbosity_WARNING;
    }
    if (level == "warning"){
        return loguru::Verbosity_FATAL;
    }
    if (level == "info"){
        return loguru::Verbosity_INFO;
    }
    std::cout << "WARNING: '" << level << "' is not valid log level string, stay default 'off' level" << std::endl;
    return loguru::Verbosity_OFF;
}

PYBIND11_MODULE(impact_cpp, m) {
    m.doc() = "impact binding module";
    m.def("set_log_level", [](const std::string &level){
            loguru::g_stderr_verbosity = parsLogLevel(level);
        }, "set loguru cpp log when call image IO through pybinding");
    init_math(m);
    init_model(m);
    image::init_image(m);
    parser::init_parser(m);
    io::init_io(m);

}

}