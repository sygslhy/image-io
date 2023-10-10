include(FindPackageHandleStandardArgs)

find_path(LZMA_INCLUDE_DIR lzma.h)
find_library(LZMA_LIBRARY NAMES lzma)

find_package_handle_standard_args(
    LZMA
    REQUIRED_VARS LZMA_LIBRARY LZMA_INCLUDE_DIR
    HANDLE_COMPONENTS
)

if(LZMA_FOUND AND NOT TARGET LZMA::LZMA)
    add_library(LZMA::LZMA UNKNOWN IMPORTED)
    set_target_properties(LZMA::LZMA PROPERTIES INTERFACE_INCLUDE_DIRECTORIES "${LZMA_INCLUDE_DIR}")
    set_target_properties(
        LZMA::LZMA PROPERTIES IMPORTED_LINK_INTERFACE_LANGUAGES "C" IMPORTED_LOCATION "${LZMA_LIBRARY}"
    )
endif()

mark_as_advanced(LZMA_LIBRARY LZMA_INCLUDE_DIR)