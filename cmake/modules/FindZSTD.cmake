include(FindPackageHandleStandardArgs)

find_path(ZSTD_INCLUDE_DIR zstd.h)
find_library(ZSTD_LIBRARY NAMES zstd)

find_package_handle_standard_args(
    ZSTD
    REQUIRED_VARS ZSTD_LIBRARY ZSTD_INCLUDE_DIR
    HANDLE_COMPONENTS
)

if(ZSTD_FOUND AND NOT TARGET ZSTD::ZSTD)
    add_library(ZSTD::ZSTD UNKNOWN IMPORTED)
    set_target_properties(ZSTD::ZSTD PROPERTIES INTERFACE_INCLUDE_DIRECTORIES "${ZSTD_INCLUDE_DIR}")
    set_target_properties(
        ZSTD::ZSTD PROPERTIES IMPORTED_LINK_INTERFACE_LANGUAGES "C" IMPORTED_LOCATION "${ZSTD_LIBRARY}"
    )
endif()

mark_as_advanced(ZSTD_LIBRARY ZSTD_INCLUDE_DIR)