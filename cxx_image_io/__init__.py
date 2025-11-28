import ctypes
import os
import sys

# Determine the path to the shared libraries
lib_dir = os.path.join(os.path.dirname(__file__))

LIB_EXT = {
    "win32": ".dll",
    "linux": ".so",
    "darwin": ".dylib",
}


# preload the all dll libs
def preload_libs(lib_dir, lib_names):
    platform = sys.platform
    ext = None
    for key, value in LIB_EXT.items():
        if platform.startswith(key):
            ext = value
            break

    if ext is None:
        raise RuntimeError(f"Unsupported platform: {platform}")

    for name in lib_names:
        path = os.path.join(lib_dir, name + ext)
        if os.path.exists(path):
            ctypes.CDLL(path)
        else:
            raise FileNotFoundError(f"{path} not found")


# Load the shared libraries, so that binding module can
# find the preloaded dll in memory.
preload_libs(lib_dir, ["libexif", "libraw_r"])

# Try to ensure that the .pyd file directory is appended in sys.path.
cur_file_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(cur_file_dir)

# Then import cxx_image from .pyd file.
from cxx_image import (DynamicMatrix, ExifMetadata, FileFormat, ImageLayout,
                       ImageMetadata, Matrix3, PixelRepresentation, PixelType,
                       RgbColorSpace, SemanticLabel, UnorderdMapSemanticMasks)
from cxx_image.io import ImageReader, ImageWriter
# Then import cxx_libraw from .pyd file and utils interfaces.
from cxx_libraw import LibRaw, RawData, RawImageSizes

from cxx_image_io.reader.base_reader import BaseImageReader
from cxx_image_io.reader.cxx_image_reader import CxxImageReader
from cxx_image_io.reader.cxx_libraw_reader import (LibRawImageReader,
                                                   read_image_libraw)
# Exposure some class for unit tests
from cxx_image_io.utils.io_cxx_libraw import (LibRaw_errors, LibRawParameters,
                                              Metadata,
                                              UnSupportedFileException)

# Exposure the public APIs
from .io import read_exif, read_image, write_exif, write_image
from .utils.channels import merge_image_channels, split_image_channels
