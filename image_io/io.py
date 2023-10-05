import sys
sys.path.append('build/cmake-release')
from impact_cpp import set_log_level, io, parser, ImageUint16, ImageUint8, ImageFloat, ImageDouble, ImageInt, PixelType, PixelRepresentation, ImageLayout
import numpy as np

__numpy_array_image_convert_vector = {
        np.dtype('uint16'): ImageUint16,
        np.dtype('uint8'): ImageUint8,
        np.dtype('float'): ImageFloat,
        np.dtype('double'): ImageDouble,
        np.dtype('int'): ImageInt
}


class ImageInfo: # change to ImageMetadata when read_image.
    def __init__(self, pixel_type:PixelType, pixel_precision:int = 0, image_layout:ImageLayout = ImageLayout.PLANAR):
        self.pixel_type = pixel_type
        self.pixel_precision = pixel_precision
        self.image_layout = image_layout

# read_exif de pybinding
# cpp_log_level can be a global function , no expose to user.
def read_image(image_path:str, metadata_path:str = None, read_info = False, cpp_log_level = 'off') -> np.array:
    """Read different types of image files and return a numpy array,
       Supported image types: plain raw, packed raw 10 and 12 bits, cfa, jpg, png, tiff, bmp.

    Parameters
    ----------
    image_path : str
        path to image file
    metadata_path : str, optional
        path to sidecar file for raw file case, by default None
    read_info : bool, optional
        flag to read along the image with descriptive format infomations, by default False
    cpp_log_level : str, optional
        flag to set the trace leve in C++ code, [off, fatal, error, warning, info] , by default 'off'

    Returns
    -------
    np.array
        returned image in numpy array format

    """
    set_log_level(cpp_log_level)
    metadata = parser.readSidecar(image_path, metadata_path)
    image_reader = io.makeReader(image_path, metadata)
    reader_descriptor = image_reader.readDescriptor()
    if reader_descriptor.pixelRepresentation == PixelRepresentation.UINT8:
        image = image_reader.read8u()
        return (np.array(image, copy=False), ImageInfo(image.pixelType(), image.pixelPrecision(), image.imageLayout())) if read_info is True else np.array(image, copy=False)
    if reader_descriptor.pixelRepresentation == PixelRepresentation.UINT16:
        image = image_reader.read16u()
        return (np.array(image, copy=False), ImageInfo(image.pixelType(), image.pixelPrecision(), image.imageLayout())) if read_info is True else np.array(image, copy=False)
    if readerDescriptor.pixelRepresentation == PixelRepresentation.FLOAT:
        image = image_reader.readf()
        return (np.array(image, copy=False), ImageInfo(image.pixelType(), image.pixelPrecision(), image.imageLayout())) if read_info is True else np.array(image, copy=False)

    raise Exception('Unsupported image type!')

# no more need for Image medata in parameters because it will be in part of ImageWriter Option.
def write_image(output_path:str, image_array:np.array,  write_options:io.ImageWriter.Options = None, cpp_log_level = 'off'):
    """Write a numpy array to different types of image file
       Supported image types: plain raw, packed raw 10 and 12 bits, cfa, jpg, png, tiff, bmp.

    Parameters
    ----------
    output_path : str
        path to image file
    image_array : np.array
        numpy array image to write
    image_info : ImageInfo
        image format descriptive infomations
    write_options : io.ImageWriter.Options, optional
        optional write options for writing parameters like jpegQualiy, tiff compression type and exif metadata infos. by default None
    cpp_log_level : str, optional
        flag to set the trace leve in C++ code, [off, fatal, error, warning, info] , by default 'off'
    """
    set_log_level(cpp_log_level)
    options = io.ImageWriter.Options() if write_options is None else write_options
    image = __numpy_array_image_convert_vector[image_array.dtype](image_array, image_info.pixel_type, image_info.image_layout, image_info.pixel_precision)
    image_writer = io.makeWriter(output_path, options)
    image_writer.write(image)