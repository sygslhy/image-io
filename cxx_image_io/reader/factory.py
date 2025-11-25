from pathlib import Path

from .base_reader import BaseImageReader
from .cxx_image_reader import CxxImageReader
from .cxx_libraw_reader import LibRawImageReader

"""
Factory class responsible for selecting the appropriate image reader.

Reader selection priority:
    1. CxxImageReader     handles standard image formats
    2. LibRawImageReader  handles RAW formats
"""


class ImageReaderFactory:
    """
    Factory responsible for selecting the appropriate image reader
    based on the predefined multi-stage rules:

    1. If extension is in the deterministic C++ list => use Cxx reader.
    2. Otherwise try LibRaw.
    3. If LibRaw fails => fallback to Cxx reader again (RAW + sidecar).
    """

    CXX_READER = CxxImageReader()
    LIBRAW_READER = LibRawImageReader()

    @classmethod
    def get_reader(cls, image_path: Path) -> BaseImageReader:
        """
        Select an appropriate reader for the given file following three-step logic.
        """

        # Stage 1: Deterministic extension → always prefer C++ backend
        if cls.CXX_READER.can_read(image_path):
            return cls.CXX_READER

        # Stage 2: Try LibRaw
        if cls.LIBRAW_READER.can_read(image_path):
            return cls.LIBRAW_READER

        # Stage 3: Fallback: special RAW files requiring sidecar → C++
        return cls.CXX_READER
