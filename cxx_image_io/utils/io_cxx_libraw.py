from pathlib import Path

import numpy as np
from cxx_image import (ExifMetadata, ImageLayout, ImageMetadata, Matrix3,
                       PixelRepresentation, PixelType)
from cxx_libraw import LibRaw, LibRaw_errors


# Get the color type of a pixel at (y,x) in the raw image data.
def _raw_color(libRaw, y, x):
    top_margin = libRaw.imgdata.sizes.top_margin
    left_margin = libRaw.imgdata.sizes.left_margin
    return libRaw.COLOR(y - top_margin, x - left_margin)


# Convert LibRaw flip value to EXIF orientation value.
def _libraw_flip_to_exif_orientation(flip):
    conv_dict = {0: 1, 3: 3, 5: 6, 6: 8}
    return conv_dict[flip]


def _parse_pixelType(libRaw):
    """
    Parse the 2×2 Bayer pattern from libRaw object and return the 2×2 pattern.

    Only 2×2 Bayer CFA patterns are supported.
    """

    filters = libRaw.imgdata.idata.filters

    # Only support 2×2 Bayer filters encoded by libraw (filters >= 1000)
    if filters < 1000:
        raise NotImplementedError(f"Only 2×2 Bayer CFA is supported. libraw filters={filters}")

    # libraw encodes 2×2 pattern by a 4×4 repeating block
    n = 4
    pattern = np.empty((n, n), dtype=np.uint8)

    for y in range(n):
        for x in range(n):
            pattern[y, x] = _raw_color(libRaw, y, x)

    # Reduce 4×4 repeating pattern → 2×2 CFA pattern
    top_left = pattern[:2, :2]

    if not (np.all(top_left == pattern[:2, 2:]) and np.all(top_left == pattern[2:, :2])
            and np.all(top_left == pattern[2:, 2:])):
        raise ValueError("Invalid 4×4 Bayer pattern; sub-blocks are inconsistent.")

    return top_left


# Internal function to convert 2x2 bayer pattern to PixelType
def _bayer_pattern_to_pixel_type(pattern):
    patterns = {
        PixelType.BAYER_RGGB: np.array([[0, 1], [3, 2]]),
        PixelType.BAYER_BGGR: np.array([[2, 3], [1, 0]]),
        PixelType.BAYER_GBRG: np.array([[3, 2], [0, 1]]),
        PixelType.BAYER_GRBG: np.array([[1, 0], [2, 3]]),
    }
    for key, value in patterns.items():
        if np.array_equal(pattern, value):
            return key
    raise ValueError("Invalid Bayer pattern")


# Internal fill metadata fileInfo function
def _fill_file_info(libRaw, metadata):
    assert isinstance(metadata, Metadata), "metadata must be Metadata type."

    metadata.fileInfo.width = libRaw.imgdata.rawdata.sizes.raw_width
    metadata.fileInfo.height = libRaw.imgdata.rawdata.sizes.raw_height

    if libRaw.imgdata.color.raw_bps > 8:
        metadata.fileInfo.pixelRepresentation = PixelRepresentation.UINT16
    else:
        metadata.fileInfo.pixelRepresentation = PixelRepresentation.UINT8

    metadata.fileInfo.pixelPrecision = libRaw.imgdata.color.raw_bps
    metadata.fileInfo.imageLayout = ImageLayout.PLANAR

    raw_pattern = _parse_pixelType(libRaw)
    if raw_pattern.shape == (2, 2) and libRaw.imgdata.idata.cdesc in ('RGBG', 'GRBG', 'BGGR', 'RGGB'):
        metadata.fileInfo.pixelType = _bayer_pattern_to_pixel_type(raw_pattern)
    else:
        metadata.fileInfo.pixelType = PixelType.CUSTOM

    return metadata


# Internal fill calibration data function
def _fill_calibration_data(libRaw, metadata):
    assert isinstance(metadata, Metadata), "metadata must be Metadata type."

    # fill calibrationData
    metadata.calibrationData.blackLevel = libRaw.imgdata.color.black
    metadata.calibrationData.whiteLevel = libRaw.imgdata.color.maximum

    if libRaw.imgdata.color.cam_mul[1] > 0 and libRaw.imgdata.color.cam_mul[0] > 0 and libRaw.imgdata.color.cam_mul[
            2] > 0:
        metadata.cameraControls.whiteBalance = ImageMetadata.WhiteBalance()
        metadata.cameraControls.whiteBalance.gainR = libRaw.imgdata.color.cam_mul[0] / libRaw.imgdata.color.cam_mul[1]
        metadata.cameraControls.whiteBalance.gainB = libRaw.imgdata.color.cam_mul[2] / libRaw.imgdata.color.cam_mul[1]

    if libRaw.imgdata.color.dng_levels.baseline_exposure and libRaw.imgdata.color.dng_levels.baseline_exposure >= 0:
        metadata.shootingParams.ispGain = 2**libRaw.imgdata.color.dng_levels.baseline_exposure

    rgb_cam = np.array(libRaw.imgdata.color.rgb_cam[:, :3])
    metadata.calibrationData.colorMatrix = Matrix3(rgb_cam)

    return metadata


# Internal fill exif data function
def _fill_exif_metadata(libRaw, metadata):
    assert isinstance(metadata, Metadata), "metadata must be Metadata type."

    metadata.exifMetadata.imageWidth = libRaw.imgdata.rawdata.sizes.width
    metadata.exifMetadata.imageHeight = libRaw.imgdata.rawdata.sizes.height

    if libRaw.imgdata.rawdata.sizes.flip is not None:
        metadata.exifMetadata.orientation = _libraw_flip_to_exif_orientation(libRaw.imgdata.rawdata.sizes.flip)
    if libRaw.imgdata.other.iso_speed and libRaw.imgdata.other.iso_speed > 0:
        metadata.exifMetadata.isoSpeedRatings = int(libRaw.imgdata.other.iso_speed)

    if libRaw.imgdata.other.shutter:
        fshutter = round(libRaw.imgdata.other.shutter, 8)
        if fshutter > 0:
            metadata.exifMetadata.exposureTime = ExifMetadata.Rational(1, int(1 / fshutter))
    if libRaw.imgdata.other.aperture:
        metadata.exifMetadata.fNumber = ExifMetadata.Rational(round(libRaw.imgdata.other.aperture * 10), 10)
    if libRaw.imgdata.other.focal_len:
        metadata.exifMetadata.focalLength = ExifMetadata.Rational(int(libRaw.imgdata.other.focal_len * 10), 10)
    if libRaw.imgdata.idata.make:
        metadata.exifMetadata.make = libRaw.imgdata.idata.make
    if libRaw.imgdata.idata.model:
        metadata.exifMetadata.model = libRaw.imgdata.idata.model
    if libRaw.imgdata.other.timestamp:
        metadata.exifMetadata.dateTimeOriginal = libRaw.imgdata.other.timestamp
    if libRaw.imgdata.other.desc:
        metadata.exifMetadata.imageDescription = libRaw.imgdata.other.desc

    return metadata


# Convert LibRawdata to Metadata object.
def _convert_LibRawdata_to_Metadata(libRaw):
    assert isinstance(libRaw, LibRaw), "libRaw must be LibRaw type."
    libRawParameters = LibRawParameters(libRaw.imgdata.rawdata.sizes.raw_width,
                                        libRaw.imgdata.rawdata.sizes.raw_height, libRaw.imgdata.rawdata.sizes.width,
                                        libRaw.imgdata.rawdata.sizes.height, libRaw.imgdata.rawdata.sizes.top_margin,
                                        libRaw.imgdata.rawdata.sizes.left_margin)
    metadata = Metadata(libRawParameters)

    metadata = _fill_file_info(libRaw, metadata)

    metadata = _fill_calibration_data(libRaw, metadata)

    metadata = _fill_exif_metadata(libRaw, metadata)

    return metadata


class Metadata(ImageMetadata):
    def __init__(self, LibRawParameters):
        super().__init__()
        self.libRawParameters = LibRawParameters

    def serialize(self):
        metadata_dict = super().serialize()
        metadata_dict['LibRawParams'] = self.libRawParameters.__dict__
        return metadata_dict

    def __repr__(self):
        all_dict = self.serialize()
        return str(all_dict)


class LibRawParameters:
    """Important parameters related to raw sensor data size and coordinates needed by LibRaw processor.

    """
    def __init__(self, raw_width, raw_height, width, height, top_margin, left_margin):
        assert raw_width > 0, "raw_width must be a positive int"
        assert raw_height > 0, "raw_height must be a positive int"
        assert width > 0, "width must be a positive int"
        assert height > 0, "height must be a positive int"
        assert top_margin >= 0, "top_margin must be a non-negative int"
        assert left_margin >= 0, "left_margin must be a non-negative int"
        assert width <= raw_width, "visible width must not exceed raw width"
        assert height <= raw_height, "visible height must not exceed raw height"
        assert top_margin + height <= raw_height, "top_margin + height exceeds raw height"
        assert left_margin + width <= raw_width, "left_margin + width exceeds raw width"

        self.rawWidth = raw_width
        self.rawHeight = raw_height
        self.rawWidthVisible = width
        self.rawHeightVisible = height
        self.topMargin = top_margin
        self.leftMargin = left_margin

    def __repr__(self):
        return str(self.__dict__)


class UnSupportedFileException(Exception):
    """Custom Exception for the case libraw cannot open unsupported file type.
    """
    def __init__(self, message):
        self.message = message
        super().__init__(message)


def read_image_libraw(image_path: Path) -> (np.array, Metadata):
    """Read different types of raw files and return a numpy array,
       Supported image types: all the support file type by libraw

    Parameters
    ----------
    image_path : Path
        path to image file

    Returns
    -------
    np.array
        returned image in numpy array format

    """
    iProcessor = LibRaw()
    ret_open = iProcessor.open_file(str(image_path))
    iProcessor.unpack()
    if ret_open != LibRaw_errors.LIBRAW_SUCCESS:
        raise UnSupportedFileException('Unsupported libRaw file type.')
    raw_with_margin = np.array(iProcessor.imgdata.rawdata, copy=False)

    metadata = _convert_LibRawdata_to_Metadata(iProcessor)
    return raw_with_margin, metadata
