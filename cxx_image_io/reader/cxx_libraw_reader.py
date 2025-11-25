from pathlib import Path

from cxx_image_io.utils.io_cxx_libraw import (LibRaw, LibRaw_errors,
                                              read_image_libraw)

from .base_reader import BaseImageReader


class LibRawImageReader(BaseImageReader):
    """
    Image-reading strategy using the LibRaw backend (read_image_libraw).

    This reader handles various RAW camera formats:
    CR2, NEF, ARW, RAF, ORF, RW2, DNG, and more.
    """

    SUPPORTED_RAW_EXT = {'.cr2', '.nef', '.arw', '.orf', '.rw2', '.kdc', '.raw', '.pef', '.srw', '.dcr'}

    def can_read(self, image_path: Path) -> bool:
        """
        Check whether the provided file appears to be a RAW image.
        """
        return image_path.suffix.lower() in self.SUPPORTED_RAW_EXT or self._can_open(image_path)

    def _can_open(self, image_path: Path) -> bool:
        """
        Check if LibRaw is capable of opening this file.
        """
        processor = LibRaw()
        ret = processor.open_file(str(image_path))
        return ret == LibRaw_errors.LIBRAW_SUCCESS

    def read(self, image_path: Path, metadata_path: Path = None):
        """
        Delegate reading to read_image_libraw().

        Returns
        -------
        (np.ndarray, metadata)
        """
        return read_image_libraw(image_path)
