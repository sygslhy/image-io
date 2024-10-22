from cxx_image import (ExifMetadata, ImageDouble, ImageFloat, ImageInt,
                       ImageMetadata, ImageUint8, ImageUint16,
                       PixelRepresentation, io, parser)

from pathlib import Path

import numpy as np
import sys
import logging

__numpy_array_image_convert_vector = {
    np.dtype('uint16'): ImageUint16,
    np.dtype('uint8'): ImageUint8,
    np.dtype('float'): ImageFloat,
    np.dtype('double'): ImageDouble,
    np.dtype('int'): ImageInt
}


# internal function to print image essentiel infos for debugging
def __print_image_metadata_info(metadata):
    if metadata and metadata.fileInfo:
        print('Image Type:', metadata.fileInfo.pixelType)
        print('Pixel Precision:', metadata.fileInfo.pixelPrecision)
        print('Image Layout:', metadata.fileInfo.imageLayout)
        print('Pixel Representation:', metadata.fileInfo.pixelRepresentation)


# fill the image critical information to metadata that could be used otherwhere.
def __fill_medatata(image, metadata):
    assert metadata is not None
    metadata.fileInfo.pixelType = image.pixelType()
    metadata.fileInfo.pixelPrecision = image.pixelPrecision()
    metadata.fileInfo.imageLayout = image.imageLayout()
    metadata.fileInfo.width = image.width()
    metadata.fileInfo.height = image.height()
    return metadata


def read_image(image_path: Path, metadata_path: Path = None) -> np.array:
    """Read different types of image files and return a numpy array,
       Supported image types: plain raw, packed raw 10 and 12 bits, cfa, jpg, png, tiff, bmp.

    Parameters
    ----------
    image_path : Path
        path to image file
    metadata_path : Path, optional
        path to sidecar file for raw file case, the API will find automatically .json next to raw file, by default None,

    Returns
    -------
    np.array
        returned image in numpy array format

    """
    assert image_path.exists(), "Image file {0} not found".format(
        str(image_path))
    try:
        metadata = parser.readMetadata(str(image_path), metadata_path)
        image_reader = io.makeReader(str(image_path), metadata)
        # Currently don't find a good way to supported completely the std::optional by binding C++ function.
        # So create explicitily an ImageMetadata object when metadata is None.
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
        metadata.fileInfo.pixelRepresentation = image_reader.pixelRepresentation(
        )
        metadata = __fill_medatata(image, metadata)
        return np.array(image, copy=False), metadata
    except Exception as e:
        logging.error(
            'Exception occurred in reading image from file {0}: {1}'.format(
                image_path, e))
        __print_image_metadata_info(metadata)
        sys.exit(-1)


def read_exif(image_path: Path) -> ExifMetadata:
    """Read the exif data from image

    Parameters
    ----------
    image_path : Path
        path to image file

    Returns
    -------
    ExifMetadata
        returned exif data
    """

    assert image_path.exists(), "Image file {0} not found".format(
        str(image_path))
    try:
        # By binding parser.readMetadata C++ code, we need to privode explicitely None as metadata path
        # In the case of tif, jpg or dng, we don't need sidecar.
        metadata = parser.readMetadata(str(image_path), None)
        image_reader = io.makeReader(str(image_path), metadata)
        return image_reader.readExif()
    except Exception as e:
        logging.error(
            'Exception occurred in reading exif from file {0}: {1}'.format(
                image_path, e))
        __print_image_metadata_info(metadata)
        sys.exit(-1)


def write_image(output_path: Path, image_array: np.array,
                write_options: io.ImageWriter.Options):
    """Write a numpy array to different types of image file
       Supported image types: plain raw, packed raw 10 and 12 bits, cfa, jpg, png, tiff, bmp.

    Parameters
    ----------
    output_path : Path
        path to image file
    image_array : np.array
        numpy array image to write
    write_options : io.ImageWriter.Options
        write options for writing parameters like, image buffer info, jpegQualiy, tiff compression type and exif metadata infos. by default None
    """
    try:
        # Currently don't find a good way to supported completely the std::optional by binding C++ function.
        # So create explicitily an ImageWriter.Options object when write_options is None.
        options = io.ImageWriter.Options(
        ) if write_options is None else write_options

        # Before writing the numpy array to image file, it is necessary to convert numpy array to C++ image object.
        # However, only numpy array need to know image types-map from np.dtype to Image<T>,
        # so we need firstly __numpy_array_image_convert_vector here
        # In addition, numpy array can't provide enough information to create C++ image object from itself.
        # We still need to get the information from metadata.fileInfo in write_options.
        image = __numpy_array_image_convert_vector[image_array.dtype](
            image_array, options.metadata.fileInfo.pixelType,
            options.metadata.fileInfo.imageLayout,
            options.metadata.fileInfo.pixelPrecision)

        image_writer = io.makeWriter(str(output_path), options)
        image_writer.write(image)
    except Exception as e:
        logging.error(
            'Exception occurred in writing image to file {0}: {1}'.format(
                output_path, e))
        __print_image_metadata_info(options.metadata)
        sys.exit(-1)


def write_exif(image_path: Path, exif: ExifMetadata = None):
    """Write the exif data from image

    Parameters
    ----------
    image_path : Path
        path to image file
    exif : ExifMetadata
        exif data to write
    """
    try:
        image_writer = io.makeWriter(str(image_path), io.ImageWriter.Options())
        image_writer.writeExif(exif)
    except Exception as e:
        logging.error(
            'Exception occurred in writing exif to file {0}: {1}'.format(
                image_path, e))
        sys.exit(-1)
