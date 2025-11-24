"""
Image-reading strategy using the LibRaw backend (read_image_libraw).

This reader handles various RAW camera formats:
CR2, NEF, ARW, RAF, ORF, RW2, DNG, and more.
"""

from pathlib import Path
import numpy as np

from .base_reader import BaseImageReader
from utils.io_cxx_libraw import read_image_libraw


class LibRawImageReader(BaseImageReader):
    """Image-reading strategy using LibRaw."""

    SUPPORTED_RAW_EXT = {
        '.cr2', '.nef', '.arw', '.raf', '.orf', '.rw2'    }

    def can_read(self, image_path: Path) -> bool:
        """
        Check whether the provided file appears to be a RAW image.
        """
        return image_path.suffix.lower() in self.SUPPORTED_RAW_EXT

    def read(self, image_path: Path, metadata_path: Path = None):
        """
        Delegate reading to read_image_libraw().

        Returns
        -------
        (np.ndarray, metadata)
        """
        return read_image_libraw(image_path)
