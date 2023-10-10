include(FindPackageHandleStandardArgs)

find_path(WebP_INCLUDE_DIR webp/decode.h)
find_library(WebP_LIBRARY NAMES webp)

find_package_handle_standard_args(
    WebP
    REQUIRED_VARS WebP_LIBRARY WebP_INCLUDE_DIR
    HANDLE_COMPONENTS
)

if(WebP_FOUND AND NOT TARGET WebP::WebP)
    add_library(WebP::WebP UNKNOWN IMPORTED)
    set_target_properties(WebP::WebP PROPERTIES INTERFACE_INCLUDE_DIRECTORIES "${WebP_INCLUDE_DIR}")
    set_target_properties(
        WebP::WebP PROPERTIES IMPORTED_LINK_INTERFACE_LANGUAGES "C" IMPORTED_LOCATION "${WebP_LIBRARY}"
    )
endif()

mark_as_advanced(WebP_LIBRARY WebP_INCLUDE_DIR)