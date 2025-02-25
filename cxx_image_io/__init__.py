import ctypes
import os
import sys

# Determine the path to the shared libraries
lib_dir = os.path.join(os.path.dirname(__file__))

# Load the shared libraries
if sys.platform == "win32":
    hllDll = ctypes.WinDLL(os.path.join(lib_dir, "libexif.dll"))
    hllDll1 = ctypes.WinDLL(os.path.join(lib_dir, "libraw_r.dll"))
else:
    hllDll = ctypes.CDLL(os.path.join(lib_dir, "libexif.so"))
    hllDll1 = ctypes.CDLL(os.path.join(lib_dir, "libraw_r.so"))

# Try to ensure that the .pyd file directory is appended in sys.path.
cur_file_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(cur_file_dir)
# Then import cxx_image from .pyd file.
from cxx_image import (ExifMetadata, FileFormat, ImageLayout, ImageMetadata, PixelType, PixelRepresentation,
                       RgbColorSpace, SemanticLabel, UnorderdMapSemanticMasks, DynamicMatrix, Matrix3)

from cxx_image.io import ImageReader, ImageWriter

from cxx_libraw import add

# Exposure the public APIs
from .io import read_exif, read_image, write_exif, write_image
from .utils import split_image_channels, merge_image_channels
