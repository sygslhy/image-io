import os
import sys

# Try to ensure that the .pyd file directory is appended in sys.path.
cur_file_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(cur_file_dir)
# Then import cxx_image from .pyd file.
from cxx_image import (ExifMetadata, FileFormat, ImageLayout, ImageMetadata,
                       PixelType, PixelRepresentation, RgbColorSpace,
                       SemanticLabel, UnorderdMapSemanticMasks, DynamicMatrix,
                       Matrix3)

from cxx_image.io import ImageReader, ImageWriter

# Exposure the public APIs
from .io import read_exif, read_image, write_exif, write_image
from .utils import split_image_channels, merge_image_channels
