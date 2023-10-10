include(FindPackageHandleStandardArgs)

find_path(Deflate_INCLUDE_DIR libdeflate.h)
find_library(Deflate_LIBRARY NAMES deflate)

find_package_handle_standard_args(
    Deflate
    REQUIRED_VARS Deflate_LIBRARY Deflate_INCLUDE_DIR
    HANDLE_COMPONENTS
)

if(Deflate_FOUND AND NOT TARGET Deflate::Deflate)
    add_library(Deflate::Deflate UNKNOWN IMPORTED)
    set_target_properties(Deflate::Deflate PROPERTIES INTERFACE_INCLUDE_DIRECTORIES "${Deflate_INCLUDE_DIR}")
    set_target_properties(
        Deflate::Deflate PROPERTIES IMPORTED_LINK_INTERFACE_LANGUAGES "C" IMPORTED_LOCATION "${Deflate_LIBRARY}"
    )
endif()

mark_as_advanced(Deflate_LIBRARY Deflate_INCLUDE_DIR)