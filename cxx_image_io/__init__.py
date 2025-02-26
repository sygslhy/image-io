import ctypes
import os
import sys

# Determine the path to the shared libraries
lib_dir = os.path.join(os.path.dirname(__file__))

# Load the shared libraries
if sys.platform == 'win32':
    hllDll = ctypes.WinDLL(os.path.join(lib_dir, "libexif.dll"))
    hllDll1 = ctypes.WinDLL(os.path.join(lib_dir, "libraw_r.dll"))
elif sys.platform == 'linux':
    hllDll = ctypes.CDLL(os.path.join(lib_dir, "libexif.so"))
    hllDll1 = ctypes.CDLL(os.path.join(lib_dir, "libraw_r.so"))
elif sys.platform == 'darwin':
    hllDll = ctypes.CDLL(os.path.join(lib_dir, "libexif.dylib"))
    hllDll1 = ctypes.CDLL(os.path.join(lib_dir, "libraw_r.dylib"))
else:
    print('Warning, unsupport platform')

# Try to ensure that the .pyd file directory is appended in sys.path.
cur_file_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(cur_file_dir)
# Then import cxx_image from .pyd file.
from cxx_image import (DynamicMatrix, ExifMetadata, FileFormat, ImageLayout,
                       ImageMetadata, Matrix3, PixelRepresentation, PixelType,
                       RgbColorSpace, SemanticLabel, UnorderdMapSemanticMasks)
from cxx_image.io import ImageReader, ImageWriter
from cxx_libraw import LibRaw, RawData, RawImageSizes

# Exposure the public APIs
from .io import read_exif, read_image, write_exif, write_image
from .utils import merge_image_channels, split_image_channels
