"""
Factory class responsible for selecting the appropriate image reader.

Reader selection priority:
    1. CxxImageReader     – handles standard image formats
    2. LibRawImageReader  – handles RAW formats
"""

from pathlib import Path

from .cxx_image_reader import CxxImageReader
from .cxx_libraw_reader import LibRawImageReader
from .base_reader import BaseImageReader


class ImageReaderFactory:
    """
    Factory for selecting an appropriate image-reading strategy.

    The factory checks each registered reader in sequence and uses the first
    one that declares support for the given file.
    """

    READERS = [
        CxxImageReader(),
        LibRawImageReader()
    ]

    @classmethod
    def get_reader(cls, image_path: Path) -> BaseImageReader:
        """
        Determine which reader should be used for the provided file.

        Parameters
        ----------
        image_path : Path
            File path whose reader is to be selected.

        Returns
        -------
        BaseImageReader
            A reader capable of loading the file.
        """
        for reader in cls.READERS:
            if reader.can_read(image_path):
                return reader

        # Fallback: give LibRaw a chance even if suffix didn't match
        return LibRawImageReader()
