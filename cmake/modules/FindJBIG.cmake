include(FindPackageHandleStandardArgs)

find_path(JBIG_INCLUDE_DIR jbig.h)
find_library(JBIG_LIBRARY NAMES jbig)

find_package_handle_standard_args(
    JBIG
    REQUIRED_VARS JBIG_LIBRARY JBIG_INCLUDE_DIR
    HANDLE_COMPONENTS
)

if(JBIG_FOUND AND NOT TARGET JBIG::JBIG)
    add_library(JBIG::JBIG UNKNOWN IMPORTED)
    set_target_properties(JBIG::JBIG PROPERTIES INTERFACE_INCLUDE_DIRECTORIES "${JBIG_INCLUDE_DIR}")
    set_target_properties(
        JBIG::JBIG PROPERTIES IMPORTED_LINK_INTERFACE_LANGUAGES "C" IMPORTED_LOCATION "${JBIG_LIBRARY}"
    )
endif()

mark_as_advanced(JBIG_LIBRARY JBIG_INCLUDE_DIR)