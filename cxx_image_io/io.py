import logging
import sys
from pathlib import Path
from abc import ABC, abstractmethod

import numpy as np
from cxx_image import (ExifMetadata, ImageDouble, ImageFloat, ImageInt,  ImageUint8,
                       ImageUint16, ImageMetadata, io, parser)
from .reader.factory import ImageReaderFactory

# Internal Mapping from numpy dtypes to corresponding C++ Image<T> classes
_numpy_array_image_convert_vector = {
    np.dtype('uint16'): ImageUint16,
    np.dtype('uint8'): ImageUint8,
    np.dtype('float'): ImageFloat,
    np.dtype('double'): ImageDouble,
    np.dtype('int'): ImageInt
}



def read_image(image_path: Path, metadata_path: Path = None) -> (np.array, ImageMetadata):
    """Generic API to read different types of image files and return a numpy array,

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
        metadata
    """
    reader = ImageReaderFactory.get_reader(image_path)
    return reader.read(image_path, metadata_path)


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
    assert isinstance(image_path, Path), "Image path must be pathlib.Path type."
    assert image_path.exists(), "Image file {0} not found".format(str(image_path))
    # By binding parser.readMetadata C++ code, we need to privode explicitely None as metadata path
    # In the case of tif, jpg, we don't need sidecar.
    metadata = parser.readMetadata(str(image_path), None)
    image_reader = io.makeReader(str(image_path), metadata)
    return image_reader.readExif()


def write_image(output_path: Path, image_array: np.array, write_options: io.ImageWriter.Options):
    """Write a numpy array to different types of image file
       Supported image types: plain raw, packed raw 10 and 12 bits, cfa, jpg, png, tiff, bmp.

    Parameters
    ----------
    output_path : Path
        path to image file
    image_array : np.array
        numpy array image to write
    write_options : io.ImageWriter.Options
        write options for writing parameters like, image buffer info, jpegQualiy, tiff compression type
        and exif metadata infos. by default None
    """
    assert isinstance(output_path, Path), "Image path must be pathlib.Path type."
    assert isinstance(image_array, np.ndarray), "image must be numpy array."
    try:
        # Currently don't find a good way to supported completely the std::optional by binding C++ function.
        # So create explicitily an ImageWriter.Options object when write_options is None.
        options = io.ImageWriter.Options() if write_options is None else write_options

        # Before writing the numpy array to image file, it is necessary to convert numpy array to C++ image object.
        # However, only numpy array need to know image types-map from np.dtype to Image<T>,
        # so we need firstly _numpy_array_image_convert_vector here
        # In addition, numpy array can't provide enough information to create C++ image object from itself.
        # We still need to get the information from metadata.fileInfo in write_options.
        image = _numpy_array_image_convert_vector[image_array.dtype](image_array, options.metadata.fileInfo.pixelType,
                                                                      options.metadata.fileInfo.imageLayout,
                                                                      options.metadata.fileInfo.pixelPrecision)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        image_writer = io.makeWriter(str(output_path), options)
        image_writer.write(image)
    except Exception as e:
        logging.error('Exception occurred in writing image to file {0}: {1}'.format(output_path, e))
        sys.exit("Exception caught in writing image, check the error log.")


def write_exif(image_path: Path, exif: ExifMetadata = None):
    """Write the exif data from image

    Parameters
    ----------
    image_path : Path
        path to image file
    exif : ExifMetadata
        exif data to write
    """
    assert isinstance(image_path, Path), "Image path must be pathlib.Path type."
    try:
        image_writer = io.makeWriter(str(image_path), io.ImageWriter.Options())
        image_writer.writeExif(exif)
    except Exception as e:
        logging.error('Exception occurred in writing exif to file {0}: {1}'.format(image_path, e))
        sys.exit("Exception caught in writing exif, check the error log.")
