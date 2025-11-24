"""
Image-reading strategy implemented using the C++ backend (read_image_cxx).

This reader handles formats supported by your C++ image library, including:
JPEG, PNG, TIFF, BMP, YUV, NV12, CFA, DNG, etc.
"""

from pathlib import Path
import numpy as np

from .base_reader import BaseImageReader
from cxx_image_io.utils.io_cxx_image import read_image_cxx

class CxxImageReader(BaseImageReader):
    """Image-reading strategy using the C++ backend."""

    SUPPORTED_EXT = {
        '.yuv', '.nv12', '.bmp', '.jpg', '.jpeg', '.png', '.cfa', '.dng', '.tif', '.tiff'
    }

    def can_read(self, image_path: Path) -> bool:
        """
        Check if the file extension is supported by the C++ backend.
        """
        return image_path.suffix.lower() in self.SUPPORTED_EXT

    def read(self, image_path: Path, metadata_path: Path = None):
        """
        Delegate image reading to the existing read_image_cxx() function.

        Returns
        -------
        (np.ndarray, metadata)
        """
        return read_image_cxx(image_path, metadata_path)
