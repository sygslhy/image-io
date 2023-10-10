include(FindPackageHandleStandardArgs)

find_path(LERC_INCLUDE_DIR Lerc_c_api.h)
find_library(LERC_LIBRARY NAMES Lerc)

find_package_handle_standard_args(
    LERC
    REQUIRED_VARS LERC_LIBRARY LERC_INCLUDE_DIR
    HANDLE_COMPONENTS
)

if(LERC_FOUND AND NOT TARGET LERC::LERC)
    add_library(LERC::LERC UNKNOWN IMPORTED)
    set_target_properties(LERC::LERC PROPERTIES INTERFACE_INCLUDE_DIRECTORIES "${LERC_INCLUDE_DIR}")
    set_target_properties(
        LERC::LERC PROPERTIES IMPORTED_LINK_INTERFACE_LANGUAGES "C" IMPORTED_LOCATION "${LERC_LIBRARY}"
    )
endif()

mark_as_advanced(LERC_LIBRARY LERC_INCLUDE_DIR)