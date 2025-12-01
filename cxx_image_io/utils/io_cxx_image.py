import logging
import sys
from pathlib import Path

import numpy as np
from cxx_image import ImageMetadata, PixelRepresentation, io, parser


# internal function to fill the image critical information to metadata that could be used otherwhere.
def _fill_medatata(image, metadata):
    assert metadata is not None
    metadata.fileInfo.pixelType = image.pixelType()
    metadata.fileInfo.pixelPrecision = image.pixelPrecision()
    metadata.fileInfo.imageLayout = image.imageLayout()
    metadata.fileInfo.width = image.width()
    metadata.fileInfo.height = image.height()
    return metadata


def read_image_cxx(image_path: Path, metadata_path: Path = None) -> (np.array, ImageMetadata):
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
        metadata

    """
    assert isinstance(image_path, Path), "Image path must be pathlib.Path type."
    assert image_path.exists(), "Image file {0} not found".format(str(image_path))

    if metadata_path:
        assert isinstance(metadata_path, Path), "Metadata path must be pathlib.Path type."
        assert metadata_path.exists(), "Metadata file {0} not found".format(str(metadata_path))
    try:
        metadata = parser.readMetadata(str(image_path), metadata_path)
        image_reader = io.makeReader(str(image_path), metadata)
        # Currently don't find a good way to supported completely the std::optional by binding C++ function.
        # So create explicitily an ImageMetadata object when metadata is None.
        metadata = ImageMetadata() if metadata is None else metadata
        metadata = image_reader.readMetadata(metadata)
        pixel_repr = image_reader.pixelRepresentation()
        if pixel_repr == PixelRepresentation.UINT8:
            image = image_reader.read8u()
        elif pixel_repr == PixelRepresentation.UINT16:
            image = image_reader.read16u()
        else:
            image = image_reader.readf()

        metadata.fileInfo.pixelRepresentation = pixel_repr
        metadata = _fill_medatata(image, metadata)
        return np.array(image, copy=False), metadata
    except Exception as e:
        logging.error('Exception occurred in reading image from file {0}: {1}'.format(image_path, e))
        sys.exit("Exception caught in reading image, check the error log.")
