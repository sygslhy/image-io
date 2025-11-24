"""
Image-reading strategy using the LibRaw backend (read_image_libraw).

This reader handles various RAW camera formats:
CR2, NEF, ARW, RAF, ORF, RW2, DNG, and more.
"""

from pathlib import Path
import numpy as np

from .base_reader import BaseImageReader
from cxx_image_io.utils.io_cxx_libraw import read_image_libraw, LibRaw, LibRaw_errors


class LibRawImageReader(BaseImageReader):
    """Image-reading strategy using LibRaw."""

    SUPPORTED_RAW_EXT = {
        '.cr2', '.nef', '.arw', '.orf', '.rw2', 'kdc', 'raw', 'pef','srw', 'dcr'}

    def can_read(self, image_path: Path) -> bool:
        """
        Check whether the provided file appears to be a RAW image.
        """
        return image_path.suffix.lower() in self.SUPPORTED_RAW_EXT or self._try_open(image_path)


    def _try_open(self, image_path: Path) -> bool:
        """
        Check if LibRaw is capable of opening this file.
        """
        try:
            processor = LibRaw()
            ret = processor.open_file(str(image_path))
            return ret != LibRaw_errors.LIBRAW_FILE_UNSUPPORTED
        except Exception:
            return False


    def read(self, image_path: Path, metadata_path: Path = None):
        """
        Delegate reading to read_image_libraw().

        Returns
        -------
        (np.ndarray, metadata)
        """
        return read_image_libraw(image_path)
