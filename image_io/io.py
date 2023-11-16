
from cxx_image import io, parser, ImageUint16, ImageUint8, ImageFloat, ImageDouble, ImageInt, PixelType, PixelRepresentation, ImageLayout, ImageMetadata, ExifMetadata
import numpy as np

__numpy_array_image_convert_vector = {
        np.dtype('uint16'): ImageUint16,
        np.dtype('uint8'): ImageUint8,
        np.dtype('float'): ImageFloat,
        np.dtype('double'): ImageDouble,
        np.dtype('int'): ImageInt
}

# fill the image critical information to metadata that could be used at otherwhere. 
def __fill_medatata(image, metadata):
    assert metadata is not None
    metadata.fileInfo.pixelType = image.pixelType()
    metadata.fileInfo.pixelPrecision = image.pixelPrecision()
    metadata.fileInfo.imageLayout = image.imageLayout()


def read_image(image_path:str, metadata_path:str = None) -> np.array:
    """Read different types of image files and return a numpy array,
       Supported image types: plain raw, packed raw 10 and 12 bits, cfa, jpg, png, tiff, bmp.

    Parameters
    ----------
    image_path : str
        path to image file
    metadata_path : str, optional
        path to sidecar file for raw file case, by default None

    Returns
    -------
    np.array
        returned image in numpy array format

    """
    metadata = parser.readMetadata(image_path, metadata_path)
    image_reader = io.makeReader(image_path, metadata)
    metadata = ImageMetadata() if metadata is None else metadata
    metadata = image_reader.readMetadata(metadata)
    if image_reader.pixelRepresentation() == PixelRepresentation.UINT8:
        image = image_reader.read8u()
    elif image_reader.pixelRepresentation() == PixelRepresentation.UINT16:
        image = image_reader.read16u()
    elif image_reader.pixelRepresentation() == PixelRepresentation.FLOAT:
        image = image_reader.readf()
    else:
        raise Exception('Unsupported image type!')
    __fill_medatata(image, metadata)
    return np.array(image, copy=False), metadata
    

def read_exif(image_path:str) -> ExifMetadata:
    """Read the exif data from image 

    Parameters
    ----------
    image_path : str
        path to image file

    Returns
    -------
    ExifMetadata
        returned exif data
    """
    metadata = parser.readMetadata(image_path, None)
    image_reader = io.makeReader(image_path, metadata)
    return image_reader.readExif()
    

def write_image(output_path:str, image_array:np.array, write_options:io.ImageWriter.Options):
    """Write a numpy array to different types of image file
       Supported image types: plain raw, packed raw 10 and 12 bits, cfa, jpg, png, tiff, bmp.

    Parameters
    ----------
    output_path : str
        path to image file
    image_array : np.array
        numpy array image to write
    write_options : io.ImageWriter.Options
        write options for writing parameters like, image buffer info, jpegQualiy, tiff compression type and exif metadata infos. by default None
    """
    options = io.ImageWriter.Options() if write_options is None else write_options
    image = __numpy_array_image_convert_vector[image_array.dtype](image_array, options.metadata.fileInfo.pixelType, 
                                    options.metadata.fileInfo.imageLayout, options.metadata.fileInfo.pixelPrecision)
    image_writer = io.makeWriter(output_path, options)
    image_writer.write(image)


def write_exif(image_path:str, exif:ExifMetadata = None):
    """Write the exif data from image 

    Parameters
    ----------
    image_path : str
        path to image file
    exif : ExifMetadata
        exif data to write
    """
    image_writer = io.makeWriter(image_path, io.ImageWriter.Options())
    image_writer.writeExif(exif)